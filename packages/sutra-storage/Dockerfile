# Production Sutra Storage Server - Optimized Multi-Stage Build (Target: 10-15MB)
# Build from monorepo root: docker build -f packages/sutra-storage/Dockerfile -t sutra-storage-server:latest .

# Stage 1: Builder with full Rust toolchain
FROM rust:1.82-slim AS builder

# Install build dependencies and nightly
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/* && \
    rustup install nightly && \
    rustup default nightly

WORKDIR /build

# Copy manifests
COPY packages/sutra-storage/Cargo.toml packages/sutra-storage/Cargo.lock ./
COPY packages/sutra-storage/proto ./proto
COPY packages/sutra-storage/src ./src

# Build for release with static linking and optimization
# Use BuildKit cache mounts for faster incremental builds
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/build/target \
    cargo build --release --bin storage-server && \
    cp /build/target/release/storage-server /tmp/storage-server && \
    strip /tmp/storage-server

# Stage 2: Minimal runtime (NO build tools, NO Rust toolchain)
FROM debian:bookworm-slim

# PRODUCTION: Only essential runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Create non-root user
RUN groupadd -g 1000 sutra && \
    useradd -m -u 1000 -g sutra sutra

# Create data directory
RUN mkdir -p /data && chown sutra:sutra /data

WORKDIR /app

# Copy ONLY the stripped binary from builder
COPY --from=builder /tmp/storage-server /app/storage_server

# Set ownership
RUN chown sutra:sutra /app/storage_server && \
    chmod +x /app/storage_server

# Switch to non-root user
USER sutra

# Expose TCP port
EXPOSE 50051

# Health check (using nc since we removed curl)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD nc -z localhost 50051 || exit 1

# Environment variables
ENV RUST_LOG=info \
    STORAGE_PATH=/data \
    STORAGE_HOST=0.0.0.0 \
    STORAGE_PORT=50051

# Run server
ENTRYPOINT ["/app/storage_server"]
