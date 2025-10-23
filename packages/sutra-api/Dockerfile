# Production Sutra API - Optimized Multi-Stage Build (Target: 50-80MB)
# Build from monorepo root: docker build -f packages/sutra-api/Dockerfile -t sutra-api:latest .

# Stage 1: Builder with full toolchain
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy only storage-client package
COPY packages/sutra-storage-client-tcp ./packages/sutra-storage-client-tcp

# Create minimal requirements
RUN cat > api-requirements.txt <<EOF
typing_extensions>=4.12.0
msgpack>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
EOF

# Install packages
RUN pip install --no-cache-dir --prefix=/install -r api-requirements.txt && \
    pip install --no-cache-dir --prefix=/install ./packages/sutra-storage-client-tcp && \
    # Remove ALL unnecessary files
    find /install -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type f -name "*.pyc" -delete && \
    find /install -type f -name "*.pyo" -delete && \
    find /install -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type f -name "*.so" -exec strip {} + 2>/dev/null || true

# Stage 2: Minimal runtime (NO build tools)
FROM python:3.11-slim

# PRODUCTION: Only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Create non-root user
RUN useradd -m -u 1000 sutra

WORKDIR /app

# Copy ONLY installed packages from builder
COPY --from=builder /install /usr/local

# Copy ONLY API code
COPY packages/sutra-api/sutra_api ./sutra_api

# Set ownership
RUN chown -R sutra:sutra /app

# Switch to non-root user
USER sutra

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SUTRA_STORAGE_MODE=server \
    SUTRA_STORAGE_SERVER=storage-server:50051

# Run application
CMD ["python3", "-m", "uvicorn", "sutra_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
