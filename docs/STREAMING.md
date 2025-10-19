# Streaming Responses with Progressive Answer Refinement

**Real-time AI responses that get smarter as they stream.**

## Overview

Sutra AI streaming provides progressive answer refinement:
1. **⚡ Initial**: Fast first response from single path (< 100ms)
2. **🔄 Refining**: Answer improves as more paths are found
3. **🎯 Consensus**: Multi-path aggregation builds confidence
4. **✅ Complete**: Final answer with full reasoning

## Why Streaming?

### User Experience
- **Perceived performance**: Users see results immediately
- **Confidence building**: Watch answer refine in real-time
- **Transparency**: See reasoning process unfold

### Technical Benefits
- **Non-blocking**: UI remains responsive
- **Progressive**: Better UX than "loading..." spinner
- **Event-driven**: Integrates with existing event system

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Client (Browser / Python / Mobile)                  │
│         ↓ HTTP POST /sutra/stream/query                     │
└─────────────────────────────────────────────────────────────┘
                          │ SSE Stream
                          ▼
┌─────────────────────────────────────────────────────────────┐
│             FastAPI Streaming Endpoint                      │
│  StreamingResponse (Server-Sent Events)                     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          AsyncReasoningEngine (sutra_core)                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  StreamingQueryProcessor                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │ Find        │  │ Path Finding│  │  MPPA        │  │  │
│  │  │ Concepts    │→ │ (Progressive)│→ │  Consensus   │  │  │
│  │  │ (Vector)    │  │ Yield Batches│  │  Refinement  │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  │         ↓               ↓                  ↓           │  │
│  │    Chunk 1        Chunks 2-4         Final Chunk      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Python Client

```python
import asyncio
from examples.streaming_client import stream_query_simple

# Simple streaming
async def main():
    await stream_query_simple("What is machine learning?")

asyncio.run(main())
```

**Output:**
```
🤔 Query: What is machine learning?
============================================================

⚡ Initial answer (1 path):
   A subset of AI focused on learning from data
   Confidence: 0.65

🔄 Refining... (3 paths):
   Machine learning is a subset of AI that enables computers to learn from data without explicit programming
   Confidence: 0.78

✅ Final answer (5 paths):
   Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed
   Confidence: 0.85

============================================================
```

### JavaScript/Browser

```javascript
// Import from examples/streaming_client.js
await streamQuery('What is AI?', {
    onChunk: (chunk) => {
        console.log(`[${chunk.stage}] ${chunk.answer}`);
        console.log(`Confidence: ${chunk.confidence}`);
    },
    onComplete: () => {
        console.log('Done!');
    }
});
```

### React Hook

```jsx
import { useStreamingQuery } from './examples/streaming_client';

function ChatBot() {
    const { answer, confidence, stage, isLoading, stream } = useStreamingQuery();
    
    return (
        <div>
            <input 
                type="text" 
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        stream(e.target.value);
                    }
                }}
            />
            {isLoading && (
                <div className="loading">
                    <span className="stage">{stage}</span>
                    <span className="confidence">{(confidence * 100).toFixed(0)}%</span>
                </div>
            )}
            <div className="answer">{answer}</div>
        </div>
    );
}
```

### Vue 3 Composition API

```vue
<script setup>
import { useStreamingQueryVue } from './examples/streaming_client';

const { answer, confidence, stage, isLoading, stream } = useStreamingQueryVue();

const handleAsk = async (query) => {
    await stream(query);
};
</script>

<template>
    <div>
        <input @keyup.enter="handleAsk($event.target.value)" />
        <div v-if="isLoading">
            {{ stage }}: {{ (confidence * 100).toFixed(0) }}%
        </div>
        <div>{{ answer }}</div>
    </div>
</template>
```

## API Reference

### Endpoint: `POST /sutra/stream/query`

**Request:**
```json
{
    "query": "What is artificial intelligence?",
    "max_concepts": 10,
    "enable_quality_gates": true,
    "min_confidence": 0.3
}
```

**Response:** Server-Sent Events (SSE)

```
event: chunk
data: {"stage": "initial", "answer": "AI is...", "confidence": 0.6, "paths_found": 1, "is_final": false}

event: chunk
data: {"stage": "refining", "answer": "AI is a field...", "confidence": 0.75, "paths_found": 3, "is_final": false}

event: chunk
data: {"stage": "complete", "answer": "Artificial intelligence...", "confidence": 0.85, "paths_found": 5, "is_final": true}

event: done
data: {"status": "complete"}
```

### Streaming Stages

| Stage | Description | Typical Latency |
|-------|-------------|-----------------|
| `initial` | First path found | 50-100ms |
| `refining` | 2-4 paths accumulated | 100-300ms |
| `consensus` | 5+ paths, building consensus | 300-500ms |
| `complete` | Final answer with full confidence | 500-1000ms |

### StreamingChunk Fields

```typescript
interface StreamingChunk {
    stage: 'initial' | 'refining' | 'consensus' | 'complete';
    answer: string;
    confidence: number;  // 0.0 - 1.0
    paths_found: number;
    total_paths_searched: number;
    reasoning_explanation: string;
    timestamp: string;  // ISO 8601
    is_final: boolean;
}
```

## Integration Examples

### FastAPI Backend

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sutra_core.streaming import create_async_engine, format_sse_chunk
from sutra_core import ReasoningEngine

app = FastAPI()
engine = ReasoningEngine()
async_engine = create_async_engine(engine)

@app.post("/stream")
async def stream_answer(query: str):
    async def generator():
        async for chunk in async_engine.ask_stream(query):
            yield format_sse_chunk(chunk)
    
    return StreamingResponse(
        generator(),
        media_type="text/event-stream"
    )
```

### Express.js Backend

```javascript
const express = require('express');
const fetch = require('node-fetch');

app.get('/stream', async (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    
    const response = await fetch('http://localhost:8001/sutra/stream/query', {
        method: 'POST',
        body: JSON.stringify({ query: req.query.q }),
        headers: { 'Content-Type': 'application/json' }
    });
    
    response.body.pipe(res);
});
```

### Next.js API Route

```typescript
// pages/api/stream.ts
export default async function handler(req, res) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    
    const response = await fetch('http://localhost:8001/sutra/stream/query', {
        method: 'POST',
        body: JSON.stringify({ query: req.query.q })
    });
    
    for await (const chunk of response.body) {
        res.write(chunk);
    }
    
    res.end();
}
```

## Progressive Refinement Strategy

### How It Works

1. **Vector Search** (0-50ms)
   - Find top 10 relevant concepts
   - Expand to 15 concepts with neighbors

2. **Parallel Path Finding** (50-100ms)
   - Start path finding immediately
   - Yield first path as "initial" response

3. **Batch Yielding** (100-500ms)
   - Continue finding paths in background
   - Yield batches of 1-2 paths
   - Re-run MPPA consensus after each batch

4. **Final Consensus** (500-1000ms)
   - All paths found (up to target: 5)
   - Final MPPA aggregation
   - Quality gate validation

### Confidence Evolution

Typical confidence progression:
```
Initial (1 path):   0.60-0.70
Refining (3 paths): 0.70-0.80
Consensus (5 paths): 0.80-0.90
```

The answer gets more confident AND more accurate as more reasoning paths agree.

## Quality Gates Integration

Streaming automatically applies quality gates on final chunk:

```python
# In streaming endpoint
if chunk.is_final and enable_quality_gates:
    assessment = validator.validate(
        raw_confidence=chunk.confidence,
        consensus_strength=0.5,
        num_paths=chunk.paths_found,
        has_evidence=chunk.paths_found > 0
    )
    
    if not assessment.passed:
        # Replace with "I don't know"
        chunk.answer = "I don't have enough information..."
```

**User sees:**
1. Progressive refinement (stages 1-3)
2. Final quality check (stage 4)
3. Either confident answer OR honest "I don't know"

## Performance Characteristics

### Latency Breakdown

| Operation | Latency | Cumulative |
|-----------|---------|------------|
| Vector search | 5-10ms | 10ms |
| First path | 30-50ms | 60ms |
| MPPA (1 path) | 1-2ms | 62ms |
| **First chunk emitted** | **~60ms** | **60ms** |
| Paths 2-3 | 50-100ms | 160ms |
| MPPA (3 paths) | 2-3ms | 163ms |
| **Second chunk emitted** | **~160ms** | **160ms** |
| Paths 4-5 | 100-200ms | 360ms |
| MPPA (5 paths) | 3-5ms | 365ms |
| **Final chunk emitted** | **~360ms** | **360ms** |

### Comparison: Streaming vs Non-Streaming

| Metric | Non-Streaming | Streaming |
|--------|---------------|-----------|
| Time to first byte | 500-1000ms | **60-100ms** |
| Perceived latency | 1000ms | **60ms** |
| User sees progress | ❌ | ✅ |
| Answer quality | Same | Same (final) |
| Confidence building | ❌ | ✅ |

**Streaming provides 10x better perceived performance.**

## Event Emission

Streaming queries emit standard events:

```python
# Emitted automatically
EventType.QUERY_RECEIVED  # When stream starts
EventType.QUERY_COMPLETED # When final chunk sent
EventType.QUERY_HIGH_LATENCY  # If > 1000ms total
EventType.QUERY_LOW_CONFIDENCE  # If final confidence < 0.3
```

Query observability:
```python
obs.query("Show me streaming queries with high latency")
obs.query("What's the average streaming time?")
```

## Best Practices

### 1. UI Design

**Do:**
- Show stage indicators (⚡🔄🎯✅)
- Display confidence progression
- Animate text updates smoothly
- Keep previous answer visible during refinement

**Don't:**
- Flash/blink on every update (jarring)
- Replace entire UI (preserve context)
- Show raw JSON to users

### 2. Error Handling

```javascript
streamQuery(query, {
    onChunk: (chunk) => {
        // Handle normal chunks
        updateUI(chunk);
    },
    onError: (error) => {
        // Show error gracefully
        showError("Could not complete query");
        
        // Log for debugging
        console.error(error);
        
        // Fallback to non-streaming
        fallbackToRegularQuery();
    }
});
```

### 3. Timeout Handling

```javascript
const TIMEOUT_MS = 10000;  // 10 seconds

const timeout = setTimeout(() => {
    // Show timeout error
    showError("Query took too long");
}, TIMEOUT_MS);

streamQuery(query, {
    onComplete: () => {
        clearTimeout(timeout);
    }
});
```

### 4. Mobile Considerations

- **Battery**: Streaming uses less battery than polling
- **Bandwidth**: SSE is more efficient than WebSockets
- **Offline**: Detect connection loss and retry

```javascript
window.addEventListener('online', () => {
    // Retry last query
    retryLastQuery();
});
```

## Troubleshooting

### Streaming Not Working

**Check 1: CORS Headers**
```python
# In FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check 2: Nginx Buffering**
```nginx
# Disable buffering for SSE
location /sutra/stream {
    proxy_pass http://backend;
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
}
```

**Check 3: Client Timeout**
```javascript
// Increase timeout
const response = await fetch(url, {
    ...
    signal: AbortSignal.timeout(30000)  // 30 seconds
});
```

### Chunks Arriving Slowly

**Diagnosis:**
```python
# Check path finding latency
obs.query("Show me path finding operations > 500ms")
```

**Solutions:**
1. Reduce `target_paths` (default: 5)
2. Reduce `max_depth` (default: 5)
3. Optimize concept graph density

### Quality Gates Rejecting Too Often

```python
# Use lenient gate for streaming
from sutra_core.quality_gates import LENIENT_QUALITY_GATE

validator = create_quality_validator(storage, LENIENT_QUALITY_GATE)
```

## Production Deployment

### Docker Compose

```yaml
services:
  sutra-hybrid:
    image: sutra-hybrid:latest
    ports:
      - "8001:8000"
    environment:
      - SUTRA_STORAGE_SERVER=storage-server:50051
      - UVICORN_WORKERS=4  # Multiple workers for streaming
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sutra-streaming
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: sutra-hybrid
        image: sutra-hybrid:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### Load Balancing

**Important**: Use sticky sessions for streaming:

```nginx
upstream sutra_backend {
    ip_hash;  # Sticky sessions
    server backend1:8001;
    server backend2:8001;
}
```

## Examples

See complete examples:
- **Python**: `examples/streaming_client.py`
- **JavaScript**: `examples/streaming_client.js`
- **React Hook**: `useStreamingQuery()` in streaming_client.js
- **Vue 3**: `useStreamingQueryVue()` in streaming_client.js

Run Python example:
```bash
python examples/streaming_client.py
```

Run JavaScript example:
```bash
node examples/streaming_client.js
```

## Summary

**Streaming provides:**
- ⚡ 10x faster perceived performance
- 🔄 Real-time answer refinement
- 🎯 Progressive confidence building
- ✅ Same final quality as non-streaming
- 📊 Full observability integration
- 🛡️ Quality gate protection

**Perfect for:**
- Chatbots and assistants
- Interactive Q&A systems
- Real-time search
- Mobile applications
- Progressive web apps

**Your users will love the instant feedback!** 🚀
