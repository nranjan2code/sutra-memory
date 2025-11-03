# Quick Start: Add Self-Monitoring to Your Application

**5-Minute Guide to Event-Driven Observability with Sutra**

---

## Overview

Replace your Prometheus + Grafana + Elasticsearch stack with Sutra's event-driven observability:
- ✅ Emit structured events from your app
- ✅ Store in Sutra knowledge graph
- ✅ Query with natural language
- ✅ Get causal reasoning automatically

**Cost:** $0 (use your existing Sutra Storage)  
**Time to implement:** 5 minutes  
**External dependencies:** 0

---

## Step 1: Add Event Library (30 seconds)

### Rust Application

```toml
# Cargo.toml
[dependencies]
sutra-grid-events = { path = "../packages/sutra-grid-events" }
chrono = "0.4"
tokio = { version = "1", features = ["full"] }
```

### Python Application (Coming Soon)

```bash
pip install sutra-events
```

---

## Step 2: Define Your Events (2 minutes)

### Example: API Monitoring

```rust
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "event_type", rename_all = "snake_case")]
pub enum ApiEvent {
    RequestReceived {
        request_id: String,
        endpoint: String,
        method: String,
        user_id: Option<String>,
        timestamp: DateTime<Utc>,
    },
    
    RequestCompleted {
        request_id: String,
        status_code: u16,
        latency_ms: u64,
        timestamp: DateTime<Utc>,
    },
    
    RequestFailed {
        request_id: String,
        error: String,
        status_code: u16,
        timestamp: DateTime<Utc>,
    },
    
    DatabaseQuerySlow {
        request_id: String,
        query_type: String,
        latency_ms: u64,
        timestamp: DateTime<Utc>,
    },
}
```

### Example: Business Events

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BusinessEvent {
    OrderPlaced {
        order_id: String,
        user_id: String,
        amount: f64,
        items_count: u32,
        timestamp: DateTime<Utc>,
    },
    
    PaymentProcessed {
        order_id: String,
        payment_method: String,
        amount: f64,
        timestamp: DateTime<Utc>,
    },
    
    PaymentFailed {
        order_id: String,
        payment_method: String,
        error: String,
        timestamp: DateTime<Utc>,
    },
    
    OrderShipped {
        order_id: String,
        carrier: String,
        tracking_number: String,
        timestamp: DateTime<Utc>,
    },
}
```

---

## Step 3: Emit Events (1 minute)

### Initialize Event Emitter

```rust
use sutra_grid_events::EventEmitter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Connect to Sutra Storage (TCP)
    let events = EventEmitter::new("localhost:50051".to_string()).await?;
    
    // Start your application
    run_app(events).await?;
    
    Ok(())
}
```

### Emit Events in Request Handler

```rust
use axum::{Router, routing::get, extract::State};
use std::sync::Arc;

async fn handle_request(
    State(events): State<Arc<EventEmitter>>,
) -> String {
    let request_id = uuid::Uuid::new_v4().to_string();
    let start = std::time::Instant::now();
    
    // Emit: Request received
    events.emit(ApiEvent::RequestReceived {
        request_id: request_id.clone(),
        endpoint: "/api/users".to_string(),
        method: "GET".to_string(),
        user_id: Some("user-123".to_string()),
        timestamp: Utc::now(),
    });
    
    // Process request...
    let result = process_request().await;
    
    let latency = start.elapsed().as_millis() as u64;
    
    match result {
        Ok(data) => {
            // Emit: Success
            events.emit(ApiEvent::RequestCompleted {
                request_id: request_id.clone(),
                status_code: 200,
                latency_ms: latency,
                timestamp: Utc::now(),
            });
            
            data
        }
        Err(e) => {
            // Emit: Failure
            events.emit(ApiEvent::RequestFailed {
                request_id: request_id.clone(),
                error: e.to_string(),
                status_code: 500,
                timestamp: Utc::now(),
            });
            
            format!("Error: {}", e)
        }
    }
}
```

### Emit Business Events

```rust
async fn place_order(
    events: Arc<EventEmitter>,
    user_id: String,
    items: Vec<Item>,
) -> Result<String, Error> {
    let order_id = generate_order_id();
    
    // Emit: Order placed
    events.emit(BusinessEvent::OrderPlaced {
        order_id: order_id.clone(),
        user_id: user_id.clone(),
        amount: calculate_total(&items),
        items_count: items.len() as u32,
        timestamp: Utc::now(),
    });
    
    // Process payment
    match process_payment(&order_id).await {
        Ok(_) => {
            events.emit(BusinessEvent::PaymentProcessed {
                order_id: order_id.clone(),
                payment_method: "credit_card".to_string(),
                amount: calculate_total(&items),
                timestamp: Utc::now(),
            });
        }
        Err(e) => {
            events.emit(BusinessEvent::PaymentFailed {
                order_id: order_id.clone(),
                payment_method: "credit_card".to_string(),
                error: e.to_string(),
                timestamp: Utc::now(),
            });
            return Err(e);
        }
    }
    
    Ok(order_id)
}
```

---

## Step 4: Query Events (30 seconds)

### Via Sutra Control (Chat Interface)

```bash
# Start Sutra Control
docker-compose up sutra-control

# Open browser: http://localhost:3000
# Type natural language queries:
```

**Example Queries:**

```
"Show all request failures today"
"What caused request-abc123 to fail?"
"Which endpoints are slowest?"
"Show payment failures this week"
"How has API latency changed since yesterday?"
"Which users had the most errors?"
```

### Via API (Programmatic)

```python
from sutra_client import SutraClient

client = SutraClient("http://localhost:8000")

# Query failures
failures = client.query("Show all payment failures today")
for event in failures.results:
    print(f"{event.order_id}: {event.error}")

# Root cause analysis
analysis = client.query("What caused order-xyz789 to fail?")
print(analysis.causal_chain)
print(f"Confidence: {analysis.confidence}")
```

---

## Example Scenarios

### Scenario 1: API Monitoring

**Goal:** Track request latency and failures

**Events to Emit:**
- RequestReceived (every request)
- RequestCompleted (successful responses)
- RequestFailed (errors)
- DatabaseQuerySlow (slow DB queries)

**Queries:**
```
"Show all 500 errors today"
"What's the average API latency?"
"Which endpoints have the most failures?"
"Show slow database queries in the last hour"
```

**Cost Savings:**
- Datadog APM: $18K/year
- Sutra: $0/year
- **Savings: $18K**

---

### Scenario 2: E-Commerce Monitoring

**Goal:** Track order lifecycle and payment failures

**Events to Emit:**
- OrderPlaced
- PaymentProcessed
- PaymentFailed
- OrderShipped

**Queries:**
```
"Show all payment failures today"
"What caused order-abc123 to fail?"
"Which payment methods have the highest failure rate?"
"Show order processing time trends"
```

**Benefits:**
- Complete order lifecycle tracking
- Automatic root cause analysis (payment → order failure)
- Temporal reasoning ("What happened before payment failed?")

---

### Scenario 3: Microservices Monitoring

**Goal:** Track service interactions and cascading failures

**Events to Emit:**
- ServiceCallStarted
- ServiceCallCompleted
- ServiceCallFailed
- CircuitBreakerOpen

**Queries:**
```
"Show all service failures today"
"What caused the user-service outage?"
"Which services are calling inventory-service?"
"Show cascading failure chains"
```

**Benefits:**
- Distributed tracing without Jaeger
- Causal chain discovery (service A → service B → failure)
- Natural language queries (no complex trace IDs)

---

## Integration Examples

### Axum (Rust Web Framework)

```rust
use axum::{Router, middleware, extract::State};
use std::sync::Arc;

#[tokio::main]
async fn main() {
    let events = EventEmitter::new("localhost:50051".to_string())
        .await
        .expect("Failed to connect to Sutra Storage");
    
    let events = Arc::new(events);
    
    let app = Router::new()
        .route("/api/users", get(list_users))
        .route("/api/orders", post(create_order))
        .layer(middleware::from_fn(event_middleware))
        .with_state(events);
    
    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn event_middleware(
    State(events): State<Arc<EventEmitter>>,
    req: axum::http::Request<axum::body::Body>,
    next: middleware::Next<axum::body::Body>,
) -> impl axum::response::IntoResponse {
    let request_id = uuid::Uuid::new_v4().to_string();
    let start = std::time::Instant::now();
    
    events.emit(ApiEvent::RequestReceived {
        request_id: request_id.clone(),
        endpoint: req.uri().path().to_string(),
        method: req.method().to_string(),
        user_id: None, // Extract from headers
        timestamp: Utc::now(),
    });
    
    let response = next.run(req).await;
    let latency = start.elapsed().as_millis() as u64;
    
    events.emit(ApiEvent::RequestCompleted {
        request_id,
        status_code: response.status().as_u16(),
        latency_ms: latency,
        timestamp: Utc::now(),
    });
    
    response
}
```

### FastAPI (Python)

```python
from fastapi import FastAPI, Request
from sutra_events import EventEmitter
import time
import uuid
from datetime import datetime

app = FastAPI()
events = EventEmitter("localhost:50051")

@app.middleware("http")
async def event_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    
    # Emit: Request received
    events.emit({
        "event_type": "request_received",
        "request_id": request_id,
        "endpoint": request.url.path,
        "method": request.method,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    response = await call_next(request)
    latency = int((time.time() - start) * 1000)
    
    # Emit: Request completed
    events.emit({
        "event_type": "request_completed",
        "request_id": request_id,
        "status_code": response.status_code,
        "latency_ms": latency,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    return response
```

---

## Performance Considerations

### Event Emission Overhead

**Benchmark:** Emitting events adds <1ms latency per request
- Event creation: <0.1ms (in-memory)
- TCP send: <0.5ms (local network)
- Non-blocking: Queue event, return immediately

**Recommendation:** Emit events freely (no performance impact)

### Storage Overhead

**Event Volume:** Typical API:
- 100 req/sec × 2 events/req (received + completed) = 200 events/sec
- Event size: ~500 bytes
- Daily storage: 200 × 500 × 86400 = 8.6 GB/day

**Recommendation:** For high-volume APIs (1000+ req/sec):
- Sample events (emit 10% of requests)
- Aggregate metrics (emit summary every 10 seconds)

### Query Performance

**Typical queries:** 10-50ms response time
- "Show failures today": ~15ms
- "What caused X?": ~30ms (causal chain traversal)
- "Show latency trend": ~20ms (temporal aggregation)

**Recommendation:** Use for operational queries (not real-time dashboards)

---

## Best Practices

### Event Design

**DO:**
- ✅ Include timestamp in every event
- ✅ Use consistent ID fields (request_id, order_id, user_id)
- ✅ Emit events for both success and failure
- ✅ Include error details in failure events
- ✅ Use snake_case for field names

**DON'T:**
- ❌ Emit sensitive data (passwords, tokens)
- ❌ Emit duplicate events (idempotency)
- ❌ Use inconsistent timestamps (use UTC)

### Event Naming

**Pattern:** `<Entity><Action>`

**Good:**
- RequestReceived
- OrderPlaced
- PaymentFailed
- UserRegistered

**Bad:**
- ReceivedRequest (inconsistent order)
- Order (no action)
- Failed (no entity)

### Event Granularity

**Emit events for:**
- State transitions (created → processing → completed)
- External API calls (started → succeeded/failed)
- Business actions (order placed, payment processed)
- Performance thresholds (latency > 1s, memory > 80%)

**Don't emit events for:**
- Every function call (too granular)
- Internal calculations (not observable)
- Hot loops (performance impact)

---

## Troubleshooting

### Problem: Events not appearing in queries

**Check:**
1. Is Sutra Storage running? `docker ps | grep sutra-storage`
2. Is EventEmitter connected? Check logs for connection errors
3. Are events being emitted? Add debug logging

**Fix:**
```rust
// Add logging to verify emission
events.emit(my_event);
log::info!("Emitted event: {:?}", my_event);
```

### Problem: Slow event emission

**Check:**
1. Network latency to storage server
2. Event batch size (are you batching?)
3. Storage server load

**Fix:**
```rust
// Batch events for efficiency
let events_batch = vec![event1, event2, event3];
events.emit_batch(events_batch);
```

### Problem: Storage reconnection failures

**Check:**
1. Storage server availability
2. Network connectivity
3. Port 50051 open (firewall)

**Fix:** EventEmitter auto-reconnects, but check logs:
```
Failed to write event to storage: connection refused - attempting reconnect
✅ Event worker reconnected to storage
```

---

## Next Steps

1. ✅ **Start emitting events** (5 minutes)
2. ✅ **Query in Sutra Control** (natural language)
3. ✅ **Iterate on event schema** (add fields as needed)
4. 🔄 **Build custom dashboards** (optional, via API)
5. 🔄 **Set up alerts** (query events programmatically)

---

## Additional Resources

- **Full Case Study:** [docs/case-studies/DEVOPS_SELF_MONITORING.md](./DEVOPS_SELF_MONITORING.md)
- **Event Schema Reference:** `packages/sutra-grid-events/src/events.rs`
- **API Documentation:** [docs/api/](../api/)
- **Example Code:** `packages/sutra-grid-master/src/main.rs` (production usage)

---

## Support

**Questions?** Open an issue: https://github.com/nranjan2code/sutra-memory/issues

**Enterprise support:** sales@sutra.ai

**Community:** https://discord.gg/sutra-ai
