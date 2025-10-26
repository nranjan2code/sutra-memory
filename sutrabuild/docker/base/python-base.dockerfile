# Sutra AI - Shared Python Base Image
# Build: docker build -f build/docker/base/python-base.dockerfile -t sutra-python-base:latest .

FROM python:3.11-slim

# Security updates and common dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime essentials
    curl \
    ca-certificates \
    # Build essentials (removed in final stage)
    gcc \
    g++ \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Create non-root user (shared across all services)
RUN groupadd -g 1000 sutra && \
    useradd -m -u 1000 -g sutra sutra

# Python optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory structure
RUN mkdir -p /app /data && \
    chown -R sutra:sutra /app /data

WORKDIR /app
USER sutra

# Install common Python packages (shared layer)
RUN pip install --user --no-cache-dir \
    typing_extensions>=4.12.0 \
    msgpack>=1.0.0 \
    pydantic>=2.0.0 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    requests>=2.31.0

# Health check utilities
COPY --chown=sutra:sutra sutrabuild/scripts/health-check.sh /usr/local/bin/health-check
RUN chmod +x /usr/local/bin/health-check

EXPOSE 8000