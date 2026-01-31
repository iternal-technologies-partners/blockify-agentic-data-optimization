# Blockify Distillation Service
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Production
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash blockify && \
    mkdir -p /app/data && \
    chown -R blockify:blockify /app

# Copy application code
COPY --chown=blockify:blockify app/ ./app/
COPY --chown=blockify:blockify requirements.txt .

# Switch to non-root user
USER blockify

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8315 \
    DATABASE_BACKEND=sqlite \
    DATABASE_URL=sqlite:///./data/jobs.db \
    DATA_DIR=/app/data

# Create data directory for SQLite
VOLUME ["/app/data"]

# Expose port
EXPOSE 8315

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8315/health || exit 1

# Run the application
CMD ["python", "-m", "app.api"]
