# Sutra Embedding Service
# Build: docker build -f sutrabuild/docker/services/sutra-embedding-service.dockerfile -t sutra-embedding-service:latest .

FROM sutra-python-base:latest AS deps

# Install embedding-specific dependencies
USER root
RUN pip install --no-cache-dir \
    torch>=2.0.0 \
    transformers>=4.35.0 \
    sentence-transformers>=2.2.0 \
    numpy>=1.24.0

USER sutra

# Final stage
FROM sutra-python-base:latest

# Copy installed dependencies
COPY --from=deps --chown=sutra:sutra /home/sutra/.local /home/sutra/.local

# Copy application code
COPY --chown=sutra:sutra packages/sutra-embedding-service/main.py ./main.py
COPY --chown=sutra:sutra packages/sutra-embedding-service/main_simple.py ./main_simple.py
COPY --chown=sutra:sutra packages/sutra-embedding-service/download_model.py ./download_model.py
COPY --chown=sutra:sutra packages/sutra-embedding-service/requirements.txt ./requirements.txt

# Create models directory
RUN mkdir -p /app/models && chown sutra:sutra /app/models

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/models \
    TRANSFORMERS_CACHE=/app/models

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD health-check http://localhost:8889/health

EXPOSE 8889

CMD ["python3", "main_simple.py"]