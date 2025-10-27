# Key Design Decisions

**Rationale behind major architectural and implementation choices**

---

## 🏗️ Storage Architecture

### Decision: Dual Storage (User + Domain)

**Choice Made:** Separate storage servers for user data vs domain knowledge

**Alternatives Considered:**
- Single unified storage
- Traditional SQL database + vector store
- Microservices with separate databases per service

**Rationale:**
```
✅ Separation of concerns (user management vs AI knowledge)
✅ Independent scaling (user storage scales differently than domain knowledge)
✅ Multi-tenancy support (easy organization isolation)  
✅ Backup strategy (different retention policies)
✅ Development isolation (changes to user features don't affect AI)
```

**Trade-offs:**
- More complex deployment (2 storage servers vs 1)
- Cross-storage queries require coordination
- Slightly higher resource usage

**Validation:** Proved storage engine can replace PostgreSQL + Redis + Elasticsearch

---

## 💬 UI Architecture

### Decision: Conversation-First Design

**Choice Made:** Everything organized around conversations, not traditional admin panels

**Alternatives Considered:**
- Traditional dashboard with separate chat module
- Document-based interface (like Notion)
- Command-line interface with optional web UI

**Rationale:**
```
✅ Natural for AI interaction (conversations are the primary interface)
✅ Familiar UX (ChatGPT-like experience users expect)
✅ Search and organization map naturally to conversations
✅ Audit trail built into conversation history
✅ Knowledge accumulates through conversation patterns
```

**Implementation:**
- Spaces organize conversations by project/domain
- Search spans all conversation history
- Graph visualization shows reasoning within conversations
- Meta-reasoning: AI can reason about its own conversation history

---

## 🔐 Authentication Strategy  

### Decision: JWT with Dual Tokens

**Choice Made:** Access tokens (24h) + Refresh tokens (7d) with server-side session tracking

**Alternatives Considered:**
- Session cookies only
- Single long-lived JWT
- OAuth2 delegation to external providers
- Magic links / passwordless

**Rationale:**
```
✅ Stateless API requests (JWT bearer tokens)
✅ Automatic token refresh (seamless UX)
✅ Server-side revocation (session concepts in storage)
✅ Mobile app friendly (no cookie dependency)  
✅ Audit trail (all sessions tracked as concepts)
```

**Security Features:**
- Argon2id password hashing (memory-hard, side-channel resistant)
- Session revocation stored in user-storage.dat
- JWT secrets configurable via environment variables
- Production mode adds TLS 1.3 + HMAC signatures

---

## ⚡ Performance Choices

### Decision: Server-Sent Events for Streaming

**Choice Made:** SSE over WebSockets for real-time message streaming

**Alternatives Considered:**
- WebSockets for bidirectional communication
- Long polling with chunked responses
- Pure REST with polling

**Rationale:**
```
✅ Simpler than WebSockets (HTTP-based, no connection management)
✅ Automatic reconnection (browser built-in)
✅ Works through proxies and firewalls
✅ JWT token authentication via headers (POST request to establish)
✅ Server-side event streaming natural for AI response generation
```

**Implementation:**
- POST to `/message/stream` establishes SSE connection
- Progressive refinement: user_message → progress → chunks → complete
- Confidence scores update in real-time
- Automatic fallback to non-streaming if SSE fails

---

## 🔍 Search Architecture

### Decision: Semantic Search with Relevance Scoring

**Choice Made:** Vector similarity + recency + starred boost + exact match bonus

**Alternatives Considered:**
- Pure keyword search (Elasticsearch-style)
- Pure semantic search (vector similarity only)
- Hybrid search with separate keyword and semantic indexes
- AI-powered query rewriting

**Rationale:**
```
✅ Better than keywords (understands meaning, not just text matching)
✅ Recency bias (recent conversations more relevant)
✅ User signals (starred items boosted)
✅ Exact matches (handles proper nouns, codes, IDs)
✅ Single index (simpler than hybrid approach)
```

**Scoring Algorithm:**
```python
final_score = (
    semantic_similarity * 0.7 +
    recency_score * 0.2 +        # Exponential decay over 30 days
    starred_boost * 0.1 +        # +0.2 if user starred
    exact_match_bonus            # +0.3 if exact phrase match
)
```

---

## 🎨 UI Framework Selection

### Decision: Material Design 3 with React

**Choice Made:** MUI v5 with Material Design 3 theming

**Alternatives Considered:**
- Custom CSS framework
- Tailwind CSS with headless components
- Ant Design
- Chakra UI
- Plain HTML/CSS

**Rationale:**
```
✅ Professional appearance out of the box
✅ Accessibility built-in (WCAG 2.1 AA compliance)
✅ Mobile responsive by default
✅ Consistent design system (reduces decision fatigue)
✅ Large component library (reduces custom development)
✅ Dark mode support included
```

**Theme Customization:**
- Primary: #6750A4 (professional purple)
- Secondary: #625B71 (muted purple-gray)
- Glassmorphism for command palette
- Custom loading skeletons

---

## 📊 Graph Visualization

### Decision: ReactFlow for Knowledge Graphs

**Choice Made:** ReactFlow with custom node components and force-directed layout

**Alternatives Considered:**
- D3.js custom implementation
- Cytoscape.js
- vis.js
- Three.js for 3D visualization
- ASCII art graphs in terminal

**Rationale:**
```
✅ React integration (consistent with rest of UI)
✅ Interactive by default (pan, zoom, node selection)
✅ Custom node components (Material Design 3 styling)
✅ Performance optimizations built-in
✅ Minimap and controls included
✅ Typescript support
```

**Custom Features:**
- Color-coded nodes by confidence (green/orange/red)
- Animated edges for reasoning flow
- Expandable/collapsible (doesn't clutter chat)
- Lazy loading (only fetch when expanded)

---

## 🚀 Deployment Strategy

### Decision: Single-Path Docker Compose

**Choice Made:** Leverage existing `./sutra-deploy.sh` with no new deployment scripts

**Alternatives Considered:**
- Kubernetes manifests
- Separate deployment system for UI
- Cloud-native services (managed databases)
- Serverless functions (AWS Lambda, Vercel)

**Rationale:**
```
✅ Zero additional complexity for users
✅ Single command deployment (./sutra-deploy.sh install)
✅ Consistent with existing Sutra deployment
✅ Works across all editions (simple/community/enterprise)
✅ No cloud vendor lock-in
```

**Integration Strategy:**
- Add services to existing docker-compose-grid.yml
- Reuse existing health check infrastructure  
- Leverage existing nginx reverse proxy
- Maintain existing log aggregation

---

## 📱 Mobile Strategy

### Decision: Responsive Web App (No Native Apps)

**Choice Made:** Mobile-responsive React app, no native iOS/Android apps

**Alternatives Considered:**
- React Native mobile app
- Progressive Web App (PWA) with offline support
- Native iOS and Android apps
- Mobile-only simplified interface

**Rationale:**
```
✅ Single codebase (web covers desktop + mobile)
✅ No app store approval process
✅ Instant updates (no app store delays)
✅ B2B context (professionals use browsers)
✅ Touch-friendly UI (44x44px buttons, swipe gestures)
```

**Mobile Features:**
- Sidebar becomes drawer on mobile
- Touch-friendly button sizes
- Keyboard shortcuts adapted for mobile
- Responsive typography and spacing

---

## 🧪 Testing Philosophy

### Decision: Test Framework Examples (Not Full Coverage)

**Choice Made:** Provide test patterns and examples, not comprehensive test suite

**Alternatives Considered:**
- Full test coverage (85%+ target)
- No testing documentation
- Only integration tests
- Only unit tests

**Rationale:**
```
✅ Demonstrates testing patterns for developers
✅ Shows best practices for each layer (backend/frontend)
✅ Enables teams to build their own test suites
✅ Faster implementation (examples vs full coverage)
✅ Educational value (teaches testing approaches)
```

**Test Categories Covered:**
- Backend: UserService, API routes, authentication, search
- Frontend: Components, hooks, user interactions, error states

---

## 🔄 State Management

### Decision: React Query + Context (No Redux)

**Choice Made:** TanStack Query for server state, React Context for client state

**Alternatives Considered:**
- Redux Toolkit
- Zustand
- Recoil  
- Pure React useState/useEffect

**Rationale:**
```
✅ Server state ≠ client state (different optimization needs)
✅ React Query handles caching, retries, synchronization automatically
✅ Context sufficient for simple client state (auth, theme, UI)
✅ Less boilerplate than Redux
✅ Built-in loading and error states
```

**State Categories:**
- **Server State** (React Query): conversations, messages, users, search results
- **Client State** (Context): authentication, theme, UI preferences
- **URL State** (React Router): current conversation, page navigation

---

## 📈 Scalability Decisions

### Decision: Optimize for 10K Users, Design for More

**Choice Made:** Current architecture targets 10K concurrent users, with clear scaling path

**Alternatives Considered:**
- Microservices from day one
- Serverless-first architecture
- Traditional three-tier architecture
- Event-sourced architecture

**Rationale:**
```
✅ Start simple, scale as needed (YAGNI principle)
✅ Storage engine already handles 10M+ concepts
✅ Horizontal scaling path clear (more storage shards)
✅ Performance monitoring built-in (web vitals tracking)
✅ Premature optimization avoided
```

**Scaling Strategy:**
1. **Phase 1** (current): Single API server, dual storage
2. **Phase 2**: Multiple API servers, load balancer
3. **Phase 3**: Storage sharding, read replicas
4. **Phase 4**: Microservices if complexity demands

---

## 🎯 Quality vs Speed Tradeoffs

### Decision: Quality Over Feature Velocity

**Choice Made:** Professional polish and documentation over rapid feature addition

**Alternatives Considered:**
- MVP with basic features only
- Feature-rich but rough around edges
- Perfect feature set but no documentation

**Rationale:**
```
✅ Enterprise customers expect professional quality
✅ Documentation reduces support burden
✅ Polish increases user adoption and satisfaction
✅ Compliance requirements demand audit trails and reliability
✅ Easier to maintain high-quality codebase
```

**Quality Investments:**
- 24,000+ words of documentation
- Comprehensive error handling and loading states
- Accessibility compliance (WCAG 2.1 AA)
- Performance optimizations (React.memo, code splitting)
- Professional visual design (Material Design 3)

---

## 🔗 Integration Strategy  

### Decision: API-First, UI-Optional

**Choice Made:** Complete REST API that works independently of UI

**Alternatives Considered:**
- UI-first with minimal API
- GraphQL instead of REST
- RPC-style API (gRPC)
- Tightly coupled UI+API

**Rationale:**
```
✅ API enables custom integrations (Python SDK, mobile apps)
✅ UI can be replaced without changing backend
✅ Third-party tool integration possible
✅ Automation and scripting supported
✅ Clear separation of concerns
```

**API Design:**
- RESTful endpoints with consistent patterns
- OpenAPI documentation auto-generated
- JWT authentication for all endpoints  
- Comprehensive error responses
- Rate limiting and abuse protection

---

## 📊 Metrics and Observability

### Decision: Web Vitals + Custom Metrics

**Choice Made:** Core Web Vitals tracking with custom performance measurements

**Alternatives Considered:**
- No metrics (rely on user feedback)
- Full APM solution (DataDog, New Relic)
- Custom logging only
- Server-side metrics only

**Rationale:**
```
✅ Core Web Vitals correlate with user experience
✅ Custom metrics for AI-specific performance (reasoning time)
✅ Client-side metrics show real user experience
✅ No external service dependency
✅ Privacy-friendly (no user tracking)
```

**Metrics Tracked:**
- **Core Web Vitals**: CLS, INP, FCP, LCP, TTFB
- **Custom**: API response times, search latency, streaming duration
- **Business**: conversations created, messages sent, search queries

---

## 💡 Key Lessons Learned

### 1. Storage Engine Versatility
The same storage engine that handles AI knowledge works excellently for user management, sessions, and permissions. No need for separate databases.

### 2. Conversation-First UX
Organizing everything around conversations feels natural and enables powerful meta-reasoning (AI can reason about its own conversation history).

### 3. Real-Time Streaming Value  
Progressive refinement during AI response generation significantly improves perceived performance and user engagement.

### 4. Documentation ROI
Comprehensive documentation (24,000+ words) took significant effort but enables user adoption and reduces support burden.

### 5. Single-Path Deployment
Leveraging existing deployment infrastructure instead of creating new systems reduced complexity and user friction.

---

**This document captures the reasoning behind major technical decisions. For implementation details, see [Architecture Guide](./architecture.md).**

---

**Last Updated:** October 27, 2025  
**Decision Log Version:** 1.0