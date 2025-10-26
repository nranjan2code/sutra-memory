# Sutra Storage Service  
# Build: docker build -f build/docker/services/sutra-storage.dockerfile -t sutra-storage:latest .

FROM rust:1.82-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/* && \
    rustup install nightly && \
    rustup default nightly

WORKDIR /build

# Copy storage package
COPY packages/sutra-storage/Cargo.toml packages/sutra-storage/Cargo.lock ./
COPY packages/sutra-storage/proto ./proto
COPY packages/sutra-storage/src ./src

# Build with cache optimization
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/build/target \
    cargo build --release --bin storage-server && \
    cp /build/target/release/storage-server /tmp/storage-server && \
    strip /tmp/storage-server

# Runtime stage
FROM sutra-rust-base:latest

# Copy binary
COPY --from=builder --chown=sutra:sutra /tmp/storage-server /app/storage_server
RUN chmod +x /app/storage_server

# Environment
ENV RUST_LOG=info \
    STORAGE_PATH=/data \
    STORAGE_HOST=0.0.0.0 \
    STORAGE_PORT=50051 \
    VECTOR_DIMENSION=768

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD nc -z localhost 50051 || exit 1

EXPOSE 50051

ENTRYPOINT ["/app/storage_server"]