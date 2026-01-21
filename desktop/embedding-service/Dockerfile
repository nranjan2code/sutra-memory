# Simple Python-based embedding service for Sutra Desktop Edition
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    sentence-transformers==2.7.0 \
    requests==2.31.0 && \
    pip install --no-cache-dir \
    torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu

# Create service script
COPY app.py /app/

# Non-root user
RUN useradd -m -s /bin/bash sutra && chown -R sutra:sutra /app
USER sutra

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8888/health')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8888"]
