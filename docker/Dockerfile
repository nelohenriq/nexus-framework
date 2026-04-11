# NEXUS Framework - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt 2>/dev/null || pip install --no-cache-dir --user pip
RUN pip install --no-cache-dir --user .

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Create non-root user
RUN useradd --create-home --shell /bin/bash nexus

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/nexus/.local

# Copy application code
COPY --chown=nexus:nexus . /app

# Set environment variables
ENV PATH=/home/nexus/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV NEXUS_LOG_LEVEL=INFO

# Switch to non-root user
USER nexus

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
 CMD python -c "import requests; requests.get("http://localhost:8000/health")" || exit 1

# Default command
CMD ["python", "-m", "nexus.api.rest"]