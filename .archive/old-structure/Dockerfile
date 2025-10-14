# Revolutionary AI System - Lightweight Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies (minimal!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY sutra_ai.py .
COPY hybrid_llm_replacement.py .
COPY api_service.py .
COPY test_sutra.py .
COPY test_2025_enhancements.py .
COPY demo_enhancements.py .
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
# Run demo: docker run sutra-ai python3 sutra_ai.py --demo
# Run hybrid demo: docker run sutra-ai python3 hybrid_llm_replacement.py
# Run tests: docker run sutra-ai python3 test_sutra.py
# Run enhancement tests: docker run sutra-ai python3 test_2025_enhancements.py