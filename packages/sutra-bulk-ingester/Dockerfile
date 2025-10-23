# Multi-stage Docker build for Rust + Python bulk ingester
FROM rust:1.82-slim AS rust-builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Rust project files
COPY packages/sutra-bulk-ingester/Cargo.toml ./
COPY packages/sutra-bulk-ingester/src ./src/
COPY packages/sutra-protocol ../sutra-protocol/

# Build the Rust binary
RUN cargo build --release

# Python runtime stage
FROM python:3.11-slim

# Runtime dependencies already in base image

# Create app user
RUN useradd -m -s /bin/bash app

# Set working directory
WORKDIR /app

# Copy the built Rust binary
COPY --from=rust-builder /app/target/release/sutra-bulk-ingester /usr/local/bin/

# Copy Python plugins
COPY packages/sutra-bulk-ingester/plugins ./plugins/

# Install Python dependencies for plugins
RUN pip install --no-cache-dir \
    asyncio \
    aiofiles \
    requests \
    psutil

# Create directories
RUN mkdir -p /datasets /jobs && chown -R app:app /app /datasets /jobs

# Switch to app user
USER app

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Default command
CMD ["/usr/local/bin/sutra-bulk-ingester", "--port", "8005", "--plugin-dir", "./plugins"]