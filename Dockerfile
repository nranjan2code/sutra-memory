# Revolutionary AI System - Lightweight Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies (minimal!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY revolutionary_ai.py .
COPY api_service.py .
COPY test_revolutionary.py .
COPY README.md .

# Create directory for knowledge storage
RUN mkdir -p /app/knowledge

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Default command - run API server
CMD ["python3", "api_service.py"]

# Alternative commands:
# Run demo: docker run revolutionary-ai python3 revolutionary_ai.py --demo
# Run tests: docker run revolutionary-ai python3 test_revolutionary.py