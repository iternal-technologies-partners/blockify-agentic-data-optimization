"""FastAPI application for the Blockify Distillation Service.

This module provides the REST API for submitting distillation jobs,
polling for results, and monitoring service health.
"""

import os
import sys
import time
import psutil
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app import __version__
from app.config import settings
from app.models import (
    AutoDistillRequest,
    AutoDistillResponse,
    JobSubmissionResponse,
    HealthResponse,
    ProcessingStats,
)
from app.service import DedupeService
from app.jobs import get_job_manager, shutdown_job_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Track startup time for uptime calculation
_startup_time: float = 0.0

# Prometheus metrics (if enabled)
_metrics_registry = None
_job_counter = None
_job_duration_histogram = None
_active_jobs_gauge = None

if settings.prometheus_enabled:
    try:
        from prometheus_client import (
            CollectorRegistry,
            Counter,
            Histogram,
            Gauge,
            generate_latest,
            CONTENT_TYPE_LATEST,
        )

        _metrics_registry = CollectorRegistry()

        _job_counter = Counter(
            "blockify_distill_jobs_total",
            "Total number of distillation jobs",
            ["status"],
            registry=_metrics_registry,
        )

        _job_duration_histogram = Histogram(
            "blockify_distill_job_duration_seconds",
            "Job duration in seconds",
            buckets=[10, 30, 60, 120, 300, 600, 1800, 3600],
            registry=_metrics_registry,
        )

        _active_jobs_gauge = Gauge(
            "blockify_distill_active_jobs",
            "Number of currently active jobs",
            registry=_metrics_registry,
        )

        logger.info("Prometheus metrics enabled")

    except ImportError:
        logger.warning("prometheus_client not installed, metrics disabled")
        settings.prometheus_enabled = False


# OpenTelemetry tracing (if enabled)
if settings.otlp_enabled and settings.otlp_endpoint:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME

        resource = Resource(attributes={SERVICE_NAME: "blockify-distillation-service"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otlp_endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        logger.info("OpenTelemetry tracing enabled", endpoint=settings.otlp_endpoint)

    except ImportError:
        logger.warning("opentelemetry packages not installed, tracing disabled")


# Global dedupe service instance
_dedupe_service: Optional[DedupeService] = None


def get_dedupe_service() -> DedupeService:
    """Get or create the dedupe service instance."""
    global _dedupe_service
    if _dedupe_service is None:
        _dedupe_service = DedupeService()
    return _dedupe_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    global _startup_time

    # Startup
    _startup_time = time.time()
    logger.info(
        "Starting Blockify Distillation Service",
        version=__version__,
        host=settings.host,
        port=settings.port,
    )

    # Initialize services lazily on first request
    yield

    # Shutdown
    logger.info("Shutting down Blockify Distillation Service")
    shutdown_job_manager()


# Create FastAPI app
app = FastAPI(
    title="Blockify Distillation Service",
    description="Deduplication and merging service for IdeaBlocks using embeddings, clustering, and LLM synthesis",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/autoDistill", response_model=JobSubmissionResponse)
async def submit_distillation_job(
    request: AutoDistillRequest,
    webhook_url: Optional[str] = None,
) -> JobSubmissionResponse:
    """Submit a distillation job for async processing.

    The job will be processed in the background. Use the returned job ID
    to poll for results via GET /api/jobs/{job_id}.

    Args:
        request: The distillation request with IdeaBlocks
        webhook_url: Optional URL to POST results when job completes

    Returns:
        Job submission response with job ID
    """
    logger.info(
        "Received distillation request",
        task_uuid=request.blockifyTaskUUID,
        block_count=len(request.results),
        similarity=request.similarity,
        iterations=request.iterations,
    )

    try:
        job_manager = get_job_manager()
        dedupe_service = get_dedupe_service()

        # Submit job to thread pool
        def progress_callback(phase: str, progress: float, details: dict):
            job_manager.update_job_progress(job_id, phase, progress, details)

        def save_intermediate(result: dict):
            job_manager.job_store.save_intermediate_result(job_id, result)

        job_id = job_manager.submit_job(
            dedupe_service.process_dedupe_request,
            webhook_url=webhook_url,
            request=request,
            progress_callback=progress_callback,
            save_intermediate_callback=save_intermediate,
        )

        if _active_jobs_gauge:
            _active_jobs_gauge.set(job_manager.get_active_job_count())

        logger.info("Job submitted", job_id=job_id, task_uuid=request.blockifyTaskUUID)

        return JobSubmissionResponse(schemaVersion=1, jobId=job_id)

    except Exception as e:
        logger.error("Failed to submit job", error=str(e))
        if _job_counter:
            _job_counter.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")


@app.get("/api/jobs/{job_id}", response_model=AutoDistillResponse)
async def get_job_status(job_id: str) -> AutoDistillResponse:
    """Get the status and results of a distillation job.

    Args:
        job_id: The job ID returned from POST /api/autoDistill

    Returns:
        Job status and results (if complete)
    """
    job_manager = get_job_manager()
    job_data = job_manager.get_job_status(job_id)

    if job_data is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Update metrics on job completion
    if job_data.get("status") in ["success", "failure", "timeout"]:
        if _job_counter:
            _job_counter.labels(status=job_data["status"]).inc()
        if _active_jobs_gauge:
            _active_jobs_gauge.set(job_manager.get_active_job_count())

    return AutoDistillResponse(**job_data)


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str) -> dict:
    """Delete a job (admin endpoint).

    Args:
        job_id: The job ID to delete

    Returns:
        Success status
    """
    job_manager = get_job_manager()
    deleted = job_manager.delete_job(job_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    logger.info("Job deleted", job_id=job_id)
    return {"status": "deleted", "job_id": job_id}


@app.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Detailed health check endpoint.

    Returns system metrics, service status, and configuration info.
    """
    job_manager = get_job_manager()
    dedupe_service = get_dedupe_service()

    # Get system metrics
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)

    # Get service health from dedupe service
    service_health = dedupe_service.get_health_status()

    return HealthResponse(
        status="ok",
        version=__version__,
        model=service_health.get("model", "blockify-distill"),
        embedding_model=service_health.get("embedding_model", settings.embedding_model_name),
        max_cluster_size=str(settings.max_cluster_size_for_llm),
        database_backend=settings.database_backend,
        jobs_active=job_manager.get_active_job_count(),
        jobs_completed_24h=job_manager.get_completed_job_count_24h(),
        uptime_seconds=time.time() - _startup_time,
        memory_usage_mb=round(memory_mb, 2),
        cpu_percent=round(cpu_percent, 2),
    )


@app.get("/health")
async def simple_health() -> dict:
    """Simple health check for load balancers and k8s probes."""
    return {"status": "ok"}


@app.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe for k8s.

    Checks that required services are configured and accessible.
    """
    issues = []

    # Check API keys are configured
    if not settings.blockify_api_key:
        issues.append("BLOCKIFY_API_KEY not configured")
    if not settings.openai_api_key:
        issues.append("OPENAI_API_KEY not configured")

    if issues:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "issues": issues})

    return {"status": "ready"}


@app.get("/metrics")
async def prometheus_metrics() -> Response:
    """Prometheus metrics endpoint."""
    if not settings.prometheus_enabled or _metrics_registry is None:
        raise HTTPException(status_code=404, detail="Metrics not enabled")

    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    # Update active jobs gauge
    if _active_jobs_gauge:
        job_manager = get_job_manager()
        _active_jobs_gauge.set(job_manager.get_active_job_count())

    return Response(
        content=generate_latest(_metrics_registry),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "Blockify Distillation Service",
        "version": __version__,
        "documentation": "/docs",
        "health": "/healthz",
        "metrics": "/metrics" if settings.prometheus_enabled else None,
    }


# Main entry point for running with uvicorn
def main():
    """Run the server with uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.api:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
