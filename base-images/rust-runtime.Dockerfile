# Production Rust Runtime - Binary Only (~8-15MB)
# This is for RUNNING Rust binaries, not building them
FROM scratch AS rootfs
ADD alpine-minirootfs-3.18.4-x86_64.tar.gz /

FROM scratch
COPY --from=rootfs / /

# PRODUCTION: Only runtime libraries needed by Rust binaries
RUN apk add --no-cache \
    ca-certificates \
    libgcc \
    libssl3 \
    curl \
    && rm -rf /var/cache/apk/* /tmp/*

ENV RUST_LOG=info

CMD ["/bin/sh"]
