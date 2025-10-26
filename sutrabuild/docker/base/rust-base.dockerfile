# Sutra AI - Rust Services Base Image  
# Build: docker build -f build/docker/base/rust-base.dockerfile -t sutra-rust-base:latest .

FROM rust:1.82-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install nightly Rust
RUN rustup install nightly && \
    rustup default nightly

# Runtime base
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Create sutra user
RUN groupadd -g 1000 sutra && \
    useradd -m -u 1000 -g sutra sutra

# Create directories
RUN mkdir -p /app /data && \
    chown sutra:sutra /app /data

WORKDIR /app
USER sutra

# Health check utilities
COPY --chown=sutra:sutra sutrabuild/scripts/health-check.sh /usr/local/bin/health-check
RUN chmod +x /usr/local/bin/health-check

# Environment
ENV RUST_LOG=info

EXPOSE 50051