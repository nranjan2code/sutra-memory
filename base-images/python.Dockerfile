# Production Python 3.11 base - Runtime Only (~50-80MB)
FROM scratch AS rootfs
ADD alpine-minirootfs-3.18.4-x86_64.tar.gz /

FROM scratch
COPY --from=rootfs / /

# PRODUCTION: Only runtime dependencies, NO build tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    ca-certificates \
    libc6-compat \
    libffi \
    openssl \
    && ln -sf python3 /usr/bin/python \
    && python -m ensurepip \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel \
    && rm -rf /root/.cache /tmp/* /var/cache/apk/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

CMD ["python3"]
