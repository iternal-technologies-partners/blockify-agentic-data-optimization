"""Configuration management using pydantic-settings.

All configuration is loaded from environment variables with sensible defaults.
"""

import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8315, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Blockify API (LLM for merging)
    blockify_api_key: str = Field(default="", description="Blockify API key for distillation")
    blockify_base_url: str = Field(
        default="https://api.blockify.ai/v1",
        description="Blockify API base URL"
    )

    # OpenAI Embeddings
    openai_api_key: str = Field(default="", description="OpenAI API key for embeddings")
    openai_embedding_url: str = Field(
        default="https://api.openai.com/v1/embeddings",
        description="OpenAI embeddings endpoint"
    )
    embedding_model_name: str = Field(
        default="text-embedding-3-small",
        description="Embedding model to use"
    )
    openai_embedding_batch_size: int = Field(
        default=1000,
        description="Max texts per embedding API call"
    )

    # Database
    database_backend: Literal["sqlite", "postgresql", "redis", "filesystem"] = Field(
        default="sqlite",
        description="Job persistence backend"
    )
    database_url: str = Field(
        default="sqlite:///./data/jobs.db",
        description="Database connection URL"
    )
    data_dir: str = Field(
        default="./data",
        description="Data directory for filesystem storage"
    )

    # Job retention
    job_retention_enabled: bool = Field(
        default=False,
        description="Enable automatic job cleanup"
    )
    job_retention_days: int = Field(
        default=30,
        description="Days to retain completed jobs"
    )

    # Job execution
    job_timeout_seconds: int = Field(
        default=600000,
        description="Maximum job execution time in seconds"
    )
    max_workers: int = Field(
        default=10,
        description="Thread pool size for concurrent jobs"
    )

    # Algorithm
    max_blocks_per_cluster: int = Field(default=20, description="Max blocks per LLM merge call")
    max_cluster_size_for_llm: int = Field(default=20, description="Max cluster size before hierarchical split")
    max_recursion_depth: int = Field(default=10, description="Max hierarchical recursion depth")
    llm_parallel_threads: int = Field(default=10, description="Parallel threads for LLM calls")
    embedding_parallel_threads: int = Field(default=10, description="Parallel threads for embedding batch generation")
    similarity_parallel_threads: int = Field(default=10, description="Parallel threads for similarity computation")
    llm_max_retries: int = Field(default=3, description="LLM call retry count")
    llm_retry_delay: float = Field(default=2.0, description="Base retry delay in seconds")
    llm_max_completion_tokens: int = Field(default=8192, description="Max tokens for LLM response")
    llm_request_timeout: int = Field(default=180, description="LLM request timeout in seconds")

    # Similarity
    use_lsh: bool = Field(default=True, description="Use LSH for large datasets")
    max_similarity_neighbors: int = Field(default=50, description="K for k-NN search")
    sparse_similarity_threshold: int = Field(default=100, description="Min items for sparse search")
    similarity_increase_per_iteration: float = Field(default=0.01, description="Threshold increase per iteration")
    similarity_increase_iteration_start: int = Field(default=2, description="Start increasing after iteration N")
    max_similarity_threshold: float = Field(default=0.98, description="Maximum similarity threshold")
    louvain_node_threshold: int = Field(default=1000, description="Use Louvain for graphs > N nodes")

    # Intermediate results
    save_intermediate_results: bool = Field(
        default=True,
        description="Save intermediate results for crash recovery"
    )

    # Debugging
    llm_debug: bool = Field(default=False, description="Enable verbose LLM debugging")

    # Observability
    prometheus_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    otlp_endpoint: Optional[str] = Field(default=None, description="OpenTelemetry collector endpoint")
    otlp_enabled: bool = Field(default=False, description="Enable OpenTelemetry tracing")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
