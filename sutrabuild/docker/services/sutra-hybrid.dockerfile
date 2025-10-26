# Sutra Hybrid Service
# Build: docker build -f build/docker/services/sutra-hybrid.dockerfile -t sutra-hybrid:latest .

FROM sutra-python-base:latest AS deps

# Install ML dependencies
USER root
RUN pip install --no-cache-dir \
    numpy>=2.0.0 \
    scipy>=1.14.0 \
    scikit-learn>=1.5.0 \
    pydantic-settings>=2.0.0

# Install internal packages
COPY --chown=sutra:sutra packages/sutra-storage-client-tcp ./packages/sutra-storage-client-tcp
COPY --chown=sutra:sutra packages/sutra-core ./packages/sutra-core  
COPY --chown=sutra:sutra packages/sutra-nlg ./packages/sutra-nlg

RUN pip install --no-cache-dir \
    ./packages/sutra-storage-client-tcp \
    ./packages/sutra-core \
    ./packages/sutra-nlg

USER sutra

# Final stage
FROM sutra-python-base:latest

# Copy dependencies
COPY --from=deps --chown=sutra:sutra /home/sutra/.local /home/sutra/.local

# Copy application code
COPY --chown=sutra:sutra packages/sutra-hybrid/sutra_hybrid ./sutra_hybrid

# Environment  
ENV SUTRA_STORAGE_SERVER=storage-server:50051 \
    SUTRA_USE_SEMANTIC_EMBEDDINGS=true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD health-check http://localhost:8000/ping

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "sutra_hybrid.api.app:app", "--host", "0.0.0.0", "--port", "8000"]