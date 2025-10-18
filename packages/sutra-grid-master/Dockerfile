# Multi-stage build for Sutra Grid Master
# Stage 1: Builder
FROM rustlang/rust:nightly-alpine AS builder

# Install build dependencies
RUN apk add --no-cache musl-dev protobuf-dev

WORKDIR /build

# Create workspace structure to match dependency paths
RUN mkdir -p sutra-grid-master sutra-grid-events sutra-storage

# Copy storage proto dependency (needed by grid-events)
COPY packages/sutra-storage/proto ./sutra-storage/proto

# Copy grid-events dependency
COPY packages/sutra-grid-events/ ./sutra-grid-events/

# Copy master files to subdirectory to maintain relative paths
COPY packages/sutra-grid-master/Cargo.toml packages/sutra-grid-master/Cargo.lock packages/sutra-grid-master/build.rs ./sutra-grid-master/
COPY packages/sutra-grid-master/proto ./sutra-grid-master/proto
COPY packages/sutra-grid-master/src ./sutra-grid-master/src

# Change to master directory for build
WORKDIR /build/sutra-grid-master

# Build for release with static linking
RUN cargo build --release --bin sutra-grid-master
RUN cargo build --release --bin sutra-grid-cli

# Stage 2: Runtime
FROM alpine:3.19

# Install runtime dependencies and gRPC health probe
RUN apk add --no-cache ca-certificates libgcc curl && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/latest/download/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Create non-root user
RUN addgroup -g 1000 sutra && \
    adduser -D -u 1000 -G sutra sutra

# Create data and config directories
RUN mkdir -p /data /config && chown -R sutra:sutra /data /config

WORKDIR /app

# Copy binaries from builder
COPY --from=builder /build/sutra-grid-master/target/release/sutra-grid-master /app/grid-master
COPY --from=builder /build/sutra-grid-master/target/release/sutra-grid-cli /app/grid-cli

# Create default master configuration
RUN mkdir -p /config && cat > /config/master-config.toml << 'EOF'
[master]
port = 7000
host = "0.0.0.0"

[events]
storage_url = "http://grid-event-storage:50051"
EOF

# Set ownership
RUN chown -R sutra:sutra /app

# Switch to non-root user
USER sutra

# Expose gRPC port
EXPOSE 7000

# Health check using gRPC health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD grpc_health_probe -addr=:7000 || exit 1

# Environment variables
ENV RUST_LOG=info \
    GRID_MASTER_HOST=0.0.0.0 \
    GRID_MASTER_PORT=7000 \
    CONFIG_PATH=/config

# Run Grid Master
ENTRYPOINT ["/app/grid-master"]