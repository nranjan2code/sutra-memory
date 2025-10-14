# Sutra AI - Production Deployment Guide

Complete guide for deploying Sutra AI as an AI replacement in production environments.

## 🚀 Quick Production Setup

### Prerequisites

- **Python**: 3.8+ 
- **Memory**: 2GB RAM minimum, 4GB+ recommended
- **Storage**: 1GB for knowledge bases
- **CPU**: Any modern CPU (no GPU required)

### Installation

```bash
# Clone and setup
git clone https://github.com/sutra-ai/sutra-models.git
cd sutra-models

# Production setup
make setup
source venv/bin/activate

# Install production dependencies  
pip install -e packages/sutra-core/
pip install gunicorn uvicorn fastapi  # For API deployment
```

### Basic Production Instance

```python
# production_ai.py
from sutra_core import ReasoningEngine
import logging

# Configure production logging
logging.basicConfig(level=logging.INFO)

# Initialize AI with production settings
ai = ReasoningEngine(
    enable_caching=True,
    max_cache_size=10000  # Increased cache for production
)

# Load your domain knowledge
def load_knowledge_base():
    """Load production knowledge base."""
    
    # Load from files, databases, APIs, etc.
    knowledge_sources = [
        "data/company_knowledge.txt",
        "data/product_documentation.txt", 
        "data/faq_database.txt"
    ]
    
    for source_file in knowledge_sources:
        with open(source_file, 'r') as f:
            for line in f:
                if line.strip():
                    ai.learn(line.strip(), source=source_file)
    
    print(f"Loaded knowledge base with {len(ai.concepts)} concepts")

# Health check endpoint
def health_check():
    """Basic health check for monitoring."""
    stats = ai.get_system_stats()
    return {
        "status": "healthy",
        "concepts": stats["system_info"]["total_concepts"],
        "cache_hit_rate": stats["system_info"]["cache_hit_rate"]
    }

if __name__ == "__main__":
    load_knowledge_base()
    
    # Example production queries
    result = ai.ask("What is our company's main product?")
    print(f"Answer: {result.primary_answer}")
    print(f"Confidence: {result.confidence:.2f}")
```

## 🏗️ Architecture Patterns

### 1. Knowledge Management System

```python
# knowledge_system.py
from sutra_core import ReasoningEngine
from typing import List, Dict
import json

class ProductionKnowledgeSystem:
    def __init__(self, config: Dict):
        self.ai = ReasoningEngine(
            enable_caching=config.get("enable_caching", True),
            max_cache_size=config.get("cache_size", 10000)
        )
        self.knowledge_sources = config.get("knowledge_sources", [])
        
    def load_from_documents(self, documents: List[str]):
        """Load knowledge from document collection."""
        for doc_path in documents:
            with open(doc_path, 'r') as f:
                content = f.read()
                # Split into chunks for better learning
                chunks = self._chunk_document(content)
                for chunk in chunks:
                    self.ai.learn(chunk, source=doc_path)
    
    def load_from_database(self, db_config: Dict):
        """Load knowledge from database."""
        # Connect to your database
        # Extract knowledge entries
        # Learn each entry
        pass
    
    def query_with_confidence(self, question: str, min_confidence: float = 0.5):
        """Query with confidence threshold."""
        result = self.ai.ask(question)
        
        if result.confidence < min_confidence:
            return {
                "answer": "I don't have enough confidence to answer this question.",
                "confidence": result.confidence,
                "suggested_queries": self.ai.query_processor.get_query_suggestions(question)
            }
        
        return {
            "answer": result.primary_answer,
            "confidence": result.confidence,
            "explanation": result.reasoning_explanation,
            "alternatives": result.alternative_answers
        }
    
    def _chunk_document(self, content: str, chunk_size: int = 500) -> List[str]:
        """Split document into learnable chunks."""
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
```

### 2. REST API Service

```python
# api_service.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sutra_core import ReasoningEngine
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI
ai = ReasoningEngine(enable_caching=True, max_cache_size=5000)

# API Models
class QueryRequest(BaseModel):
    question: str
    num_paths: int = 5
    detailed: bool = False

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    consensus_strength: float
    explanation: str
    alternatives: list = []
    processing_time_ms: float

class LearnRequest(BaseModel):
    content: str
    source: str = None
    category: str = None

# FastAPI app
app = FastAPI(
    title="Sutra AI API",
    description="Advanced AI reasoning system with explainable answers",
    version="1.0.0"
)

# CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    stats = ai.get_system_stats()
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "system_info": stats["system_info"]
    }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process AI query with reasoning."""
    try:
        start_time = time.time()
        
        # Process query
        result = ai.ask(request.question, num_reasoning_paths=request.num_paths)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = QueryResponse(
            answer=result.primary_answer,
            confidence=result.confidence,
            consensus_strength=result.consensus_strength,
            explanation=result.reasoning_explanation,
            alternatives=[{"answer": ans, "confidence": conf} for ans, conf in result.alternative_answers],
            processing_time_ms=processing_time
        )
        
        logger.info(f"Query processed: {request.question[:50]}... -> {response.confidence:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn")
async def learn(request: LearnRequest):
    """Learn new knowledge."""
    try:
        concept_id = ai.learn(request.content, source=request.source, category=request.category)
        
        logger.info(f"Learned new concept: {request.content[:50]}...")
        return {
            "concept_id": concept_id,
            "status": "learned",
            "content_length": len(request.content)
        }
        
    except Exception as e:
        logger.error(f"Learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/explain/{question}")
async def explain_reasoning(question: str, detailed: bool = False):
    """Get detailed reasoning explanation."""
    try:
        explanation = ai.explain_reasoning(question, detailed=detailed)
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    return ai.get_system_stats()

@app.post("/optimize")
async def optimize_performance():
    """Run performance optimization."""
    optimizations = ai.optimize_performance()
    return {
        "optimizations": optimizations,
        "status": "completed"
    }

@app.post("/save")
async def save_knowledge_base(filepath: str = "knowledge_backup.json"):
    """Save knowledge base to file."""
    success = ai.save_knowledge_base(filepath)
    return {
        "saved": success,
        "filepath": filepath
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Educational AI Tutor

```python
# ai_tutor.py
from sutra_core import ReasoningEngine
from typing import Dict, List
import json

class AITutor:
    def __init__(self, subject_domain: str):
        self.ai = ReasoningEngine(enable_caching=True)
        self.subject_domain = subject_domain
        self.student_progress = {}
        
    def load_curriculum(self, curriculum_file: str):
        """Load educational content."""
        with open(curriculum_file, 'r') as f:
            curriculum = json.load(f)
            
        for topic in curriculum["topics"]:
            for concept in topic["concepts"]:
                self.ai.learn(
                    concept["content"], 
                    source=topic["name"],
                    category=self.subject_domain
                )
    
    def ask_question(self, student_id: str, question: str) -> Dict:
        """Process student question with educational context."""
        result = self.ai.ask(question)
        
        # Track student interaction
        if student_id not in self.student_progress:
            self.student_progress[student_id] = []
        
        interaction = {
            "question": question,
            "answer": result.primary_answer,
            "confidence": result.confidence,
            "timestamp": time.time()
        }
        self.student_progress[student_id].append(interaction)
        
        # Generate educational response
        educational_response = {
            "answer": result.primary_answer,
            "confidence": result.confidence,
            "explanation": result.reasoning_explanation,
            "related_topics": self._get_related_topics(question),
            "difficulty_level": self._assess_difficulty(result.confidence),
            "follow_up_questions": self._generate_follow_ups(question)
        }
        
        return educational_response
    
    def _get_related_topics(self, question: str) -> List[str]:
        """Find related educational topics."""
        concepts = self.ai.search_concepts(question, limit=5)
        return [concept["content"][:50] + "..." for concept in concepts]
    
    def _assess_difficulty(self, confidence: float) -> str:
        """Assess question difficulty based on AI confidence."""
        if confidence > 0.8:
            return "easy"
        elif confidence > 0.5:
            return "medium"
        else:
            return "difficult"
    
    def _generate_follow_ups(self, question: str) -> List[str]:
        """Generate educational follow-up questions."""
        suggestions = self.ai.query_processor.get_query_suggestions(question)
        return suggestions[:3]
```

## 📊 Performance Configuration

### Production Settings

```python
# config/production.py
PRODUCTION_CONFIG = {
    # AI Engine Settings
    "enable_caching": True,
    "cache_size": 50000,  # Large cache for production
    
    # Path Finding Settings
    "max_reasoning_depth": 8,  # Deeper reasoning for complex queries
    "min_confidence_threshold": 0.05,  # Lower threshold for broader search
    "confidence_decay_factor": 0.9,  # Less aggressive decay
    
    # Consensus Settings
    "consensus_threshold": 0.4,  # Lower threshold for consensus
    "min_paths_for_consensus": 3,  # More paths for robustness
    "outlier_penalty": 0.2,  # Less aggressive outlier penalty
    
    # Performance Settings
    "auto_optimization_interval": 3600,  # Optimize every hour
    "knowledge_backup_interval": 86400,  # Backup daily
    
    # Logging
    "log_level": "INFO",
    "log_queries": True,
    "log_performance_metrics": True
}
```

### Memory Management

```python
# memory_manager.py
import psutil
import time
from sutra_core import ReasoningEngine

class ProductionMemoryManager:
    def __init__(self, ai_engine: ReasoningEngine):
        self.ai = ai_engine
        self.memory_threshold = 0.85  # 85% memory usage threshold
        
    def monitor_memory(self):
        """Monitor and manage memory usage."""
        while True:
            memory_percent = psutil.virtual_memory().percent / 100.0
            
            if memory_percent > self.memory_threshold:
                print(f"Memory usage high: {memory_percent:.1%}")
                self._optimize_memory()
            
            time.sleep(300)  # Check every 5 minutes
    
    def _optimize_memory(self):
        """Optimize memory usage when threshold exceeded."""
        # Run system optimization
        optimizations = self.ai.optimize_performance()
        
        # Clear old cache entries
        if len(self.ai.query_cache) > 1000:
            # Keep only recent cache entries
            cache_items = list(self.ai.query_cache.items())
            self.ai.query_cache = dict(cache_items[-1000:])
        
        # Remove weak concepts if memory is critically low
        memory_percent = psutil.virtual_memory().percent / 100.0
        if memory_percent > 0.95:
            weak_concepts = [
                cid for cid, concept in self.ai.concepts.items()
                if concept.strength < 2.0 and concept.access_count < 5
            ]
            for cid in weak_concepts[:100]:  # Remove up to 100 weak concepts
                if cid in self.ai.concepts:
                    del self.ai.concepts[cid]
        
        print(f"Memory optimization complete. Freed memory.")
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY packages/sutra-core/ ./packages/sutra-core/
COPY api_service.py .
COPY config/ ./config/

# Install sutra-core package
RUN pip install -e packages/sutra-core/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  sutra-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data  # Mount knowledge data
      - ./logs:/app/logs  # Mount log directory
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - sutra-ai
    restart: unless-stopped
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream sutra_backend {
        server sutra-ai:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://sutra_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts for AI processing
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://sutra_backend/health;
            access_log off;
        }
    }
}
```

## 📈 Monitoring & Observability

### Monitoring Setup

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from sutra_core import ReasoningEngine
import time
import logging

# Prometheus metrics
query_counter = Counter('sutra_queries_total', 'Total queries processed')
query_duration = Histogram('sutra_query_duration_seconds', 'Query processing time')
confidence_gauge = Gauge('sutra_average_confidence', 'Average answer confidence')
concepts_gauge = Gauge('sutra_concepts_total', 'Total number of concepts')
cache_hit_rate = Gauge('sutra_cache_hit_rate', 'Cache hit rate')

class MonitoredReasoningEngine(ReasoningEngine):
    """Reasoning engine with monitoring capabilities."""
    
    def ask(self, question: str, **kwargs):
        """Monitored query processing."""
        query_counter.inc()
        
        with query_duration.time():
            result = super().ask(question, **kwargs)
        
        # Update metrics
        confidence_gauge.set(result.confidence)
        
        # Log query
        logging.info(f"Query processed: confidence={result.confidence:.2f}, "
                    f"consensus={result.consensus_strength:.2f}")
        
        return result
    
    def learn(self, content: str, **kwargs):
        """Monitored learning."""
        concept_id = super().learn(content, **kwargs)
        
        # Update concept count
        concepts_gauge.set(len(self.concepts))
        
        return concept_id
    
    def update_metrics(self):
        """Update all monitoring metrics."""
        stats = self.get_system_stats()
        
        concepts_gauge.set(stats['system_info']['total_concepts'])
        cache_hit_rate.set(stats['system_info']['cache_hit_rate'])

# Start Prometheus metrics server
def start_monitoring(port=8001):
    """Start monitoring server."""
    start_http_server(port)
    logging.info(f"Monitoring server started on port {port}")
```

### Logging Configuration

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/sutra_ai.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'sutra_core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO'
    }
}

def configure_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
```

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] Load and validate knowledge base
- [ ] Configure caching parameters for expected load
- [ ] Set up monitoring and logging
- [ ] Configure memory limits and optimization
- [ ] Test query performance under load
- [ ] Set up backup procedures for knowledge base
- [ ] Configure SSL/TLS certificates
- [ ] Set up health check endpoints

### Production Deployment

- [ ] Deploy with Docker/Kubernetes
- [ ] Configure load balancer (if multiple instances)
- [ ] Set up monitoring dashboards
- [ ] Configure alerting for errors/performance
- [ ] Test failover procedures
- [ ] Document operational procedures
- [ ] Set up automated backups
- [ ] Configure log rotation and retention

### Post-Deployment

- [ ] Monitor performance metrics
- [ ] Validate query accuracy and confidence
- [ ] Monitor memory usage and optimization
- [ ] Set up regular knowledge base updates
- [ ] Monitor cache hit rates
- [ ] Review and tune configuration parameters

## 💡 Production Tips

1. **Knowledge Base Management**: Regularly backup and version your knowledge bases
2. **Caching Strategy**: Size cache based on query patterns and available memory
3. **Performance Monitoring**: Track query latency, confidence, and cache hit rates
4. **Memory Management**: Monitor memory usage and run optimizations periodically
5. **Error Handling**: Implement graceful degradation for low-confidence answers
6. **Load Testing**: Test with realistic query volumes and knowledge base sizes
7. **Security**: Implement proper authentication and rate limiting
8. **Updates**: Plan for knowledge base updates without service interruption

Sutra AI is designed for production use with these patterns and practices ensuring reliable, scalable AI deployment.