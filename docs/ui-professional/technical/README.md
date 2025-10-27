# Technical Architecture & Design Decisions

**Core technical documentation for Sutra AI's conversation-first UI system**

---

## 📋 Contents

### Architecture Documents
- **[Conversation-First Architecture →](./architecture.md)** - Complete system design
- **[Design Decisions →](./design-decisions.md)** - Key architectural choices

### Key Technical Concepts

#### Dual Storage Architecture
```
User Storage (port 50053)     Domain Storage (port 50051)
├── Users & Authentication    ├── Medical Protocols
├── Conversations & Messages  ├── Legal Cases  
├── Spaces & Permissions      ├── Technical Documentation
└── Session Management        └── Your Knowledge Domain
```

#### Why Two Storage Systems?
- **Separation of Concerns** - User management vs domain knowledge
- **Independent Scaling** - Scale user storage separately from domain data
- **Multi-Tenancy** - Easy organization-based data isolation
- **Backup Strategy** - Different retention policies for user data vs knowledge

#### Graph-Native Design
Everything is stored as concepts and associations:
```
User --[has_session]--> Session --[expires_at]--> Timestamp
User --[owns_conversation]--> Conversation --[in_space]--> Space
Conversation --[has_message]--> Message --[references]--> Concept
```

#### Real-Time Learning
- No model retraining required
- New knowledge immediately queryable
- Concept relationships automatically discovered
- Quality gates prevent hallucination

---

## 🏗️ System Components

### Frontend (React + TypeScript)
- **Material Design 3** - Professional UI components
- **React Query** - Server state management
- **React Router** - Navigation and deep linking
- **Code Splitting** - Performance optimization

### Backend (FastAPI + Python)
- **FastAPI** - High-performance API framework
- **Pydantic** - Request/response validation
- **JWT Authentication** - Secure session management
- **Server-Sent Events** - Real-time message streaming

### Storage (Rust)
- **Custom TCP Protocol** - High-performance binary protocol
- **HNSW Vector Index** - Semantic search capabilities
- **Write-Ahead Log** - Crash recovery and durability
- **Cross-Shard 2PC** - Distributed transactions

---

## 🔐 Security Architecture

### Development Mode (Default)
- No authentication (localhost only)
- No encryption
- Fast development iteration

### Production Mode (`SUTRA_SECURE_MODE=true`)
- TLS 1.3 encryption
- HMAC-SHA256 signatures
- Role-based access control
- Audit logging

### Authentication Flow
```
1. User registers → Argon2id password hash stored
2. User logs in → JWT access + refresh tokens issued
3. API requests → Bearer token validated
4. Token expires → Automatic refresh via refresh token
5. Logout → Session invalidated in storage
```

---

## ⚡ Performance Design

### Target Metrics
- **API Response Time** - <100ms p99
- **Message Streaming** - <3s total response
- **Search Latency** - <60ms semantic search
- **Graph Traversal** - <50ms subgraph queries

### Optimization Strategies
- **React.memo** - Prevent unnecessary re-renders
- **Code Splitting** - Lazy load heavy components
- **Infinite Scroll** - Efficient large dataset handling
- **Request Cancellation** - Abort stale API calls

### Caching Strategy
- **React Query** - Client-side API response cache
- **Storage Engine** - Memory-mapped persistent index
- **Browser Cache** - Static asset caching
- **Service Worker** - Offline capability (future)

---

## 📊 Data Flow

### Message Flow
```
1. User types message → MessageInput component
2. Frontend sends → POST /api/conversations/{id}/message/stream
3. Backend validates → Check user permissions
4. Context loaded → Last 10 messages from user-storage
5. Domain query → Send context to domain-storage  
6. AI reasoning → Generate response with confidence
7. Stream response → Server-Sent Events to frontend
8. Store result → Message saved to user-storage
9. UI updates → New message appears in chat
```

### Search Flow
```
1. User presses Cmd+K → CommandPalette opens
2. User types query → Debounced search (300ms)
3. Semantic search → Vector similarity in storage engine
4. Relevance scoring → Similarity + recency + starred
5. Result grouping → By type (conversations, messages, spaces)
6. Results display → Grouped with navigation
```

---

## 🧪 Testing Philosophy

### Test Categories
- **Unit Tests** - Individual component logic
- **Integration Tests** - API endpoint behavior  
- **E2E Tests** - Complete user workflows
- **Performance Tests** - Load and latency validation

### Quality Gates
- **Code Coverage** - Target 85%+ for critical paths
- **API Tests** - All endpoints with error cases
- **UI Tests** - Core user journeys
- **Security Tests** - Authentication and authorization

### Test Infrastructure
- **Backend** - pytest with fixtures and mocks
- **Frontend** - Vitest with React Testing Library
- **E2E** - Playwright for browser automation
- **Load Testing** - Custom scripts for storage performance

---

## 🔄 Development Workflow

### Branch Strategy
- **main** - Production-ready code
- **develop** - Integration branch
- **feature/** - Individual features
- **hotfix/** - Emergency production fixes

### Code Quality
- **TypeScript** - Type safety throughout frontend
- **Python Type Hints** - Backend type annotations
- **ESLint + Prettier** - Code formatting
- **Pre-commit Hooks** - Automated quality checks

### Deployment Pipeline
- **Local Development** - `./sutra-deploy.sh install`
- **Testing** - Automated test suite
- **Build** - Docker container creation
- **Deploy** - Single-command deployment

---

## 📈 Scalability Considerations

### Current Limits
- **Users** - 10K+ concurrent users supported
- **Conversations** - 1M+ conversations per organization
- **Messages** - 100M+ messages with efficient pagination
- **Knowledge** - 10M+ concepts per domain storage

### Scaling Strategies
- **Horizontal Scaling** - Multiple storage shards
- **Read Replicas** - Separate read/write storage instances
- **CDN** - Static asset distribution
- **Load Balancing** - Multiple API server instances

### Future Enhancements
- **Microservices** - Split monolithic API
- **Event Sourcing** - Audit trail improvements
- **Real-time Sync** - Multi-device conversation sync
- **Edge Deployment** - Regional data residency

---

## 🎯 Design Principles

### 1. Explainability First
Every AI response shows complete reasoning path

### 2. Quality Over Speed  
"I don't know" responses when uncertain

### 3. Graph-Native Storage
No SQL databases - everything in concept graphs

### 4. Audit-Ready Design
Complete trails for compliance requirements

### 5. User Experience Parity
Professional quality matching ChatGPT

### 6. Performance by Design
Sub-100ms response times throughout

---

## 📚 Related Documentation

- **[User Guides](../user-guides/)** - End-user documentation
- **[API Reference](../api/)** - Complete API documentation  
- **[Deployment](../deployment/)** - Production deployment
- **[Development](../development/)** - Implementation guides

---

**Last Updated:** October 27, 2025  
**Architecture Version:** 2.0  
**Status:** Production Ready