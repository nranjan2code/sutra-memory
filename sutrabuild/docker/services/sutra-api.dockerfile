# Sutra API Service
# Build: docker build -f build/docker/services/sutra-api.dockerfile -t sutra-api:latest .

FROM sutra-python-base:latest AS deps

# Install API-specific dependencies
USER root
RUN pip install --no-cache-dir \
    argon2-cffi>=23.1.0 \
    pyjwt[crypto]>=2.8.0 \
    python-jose>=3.3.0 \
    python-multipart>=0.0.6 \
    pydantic-settings>=2.0.0

# Install storage client
COPY --chown=sutra:sutra packages/sutra-storage-client-tcp ./packages/sutra-storage-client-tcp
RUN pip install --no-cache-dir ./packages/sutra-storage-client-tcp

USER sutra

# Final stage
FROM sutra-python-base:latest

# Copy installed dependencies
COPY --from=deps --chown=sutra:sutra /home/sutra/.local /home/sutra/.local

# Copy application code
COPY --chown=sutra:sutra packages/sutra-api/sutra_api ./sutra_api

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SUTRA_STORAGE_MODE=server \
    SUTRA_STORAGE_SERVER=storage-server:50051 \
    SUTRA_USER_STORAGE_SERVER=user-storage-server:50051

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD health-check http://localhost:8000/health

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "sutra_api.main:app", "--host", "0.0.0.0", "--port", "8000"]