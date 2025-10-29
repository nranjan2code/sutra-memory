# 🚀 Sutra Explorer v2.0

**Next-generation knowledge graph explorer with holographic HUD aesthetic**

> **COMPLETE REWRITE** - Zero backward compatibility. Clean slate. Best practices only.

---

## ✨ Features

### 🎨 Holographic HUD Design
- **Single cyan color** (#00ffff) + grayscale
- **Brightness encoding** - Information via luminosity, not color
- **Colorblind-safe** - WCAG AAA compliant (14.6:1 contrast)
- **Sci-fi aesthetic** - Think JARVIS command center, not rainbow dashboard

### 📱 Adaptive Rendering
Automatically selects optimal visualization:
- **Mobile** (<20 nodes): List view with virtualization
- **Mobile** (20-100): Cluster map with semantic grouping
- **Desktop** (<50): Force-directed 2D graph (D3.js)
- **Desktop** (50-500): Hierarchical tree layout
- **4K/8K**: 3D immersive experience (Three.js)
- **VR Ready**: Spatial computing with hand tracking

### ⚡ Performance First
- **60fps on iPhone 13** with 500 nodes
- **120fps on desktop** with 10K nodes
- **<2s load time** on mobile
- **<500ms load time** on desktop
- Progressive loading, GPU acceleration, level-of-detail rendering

### ♿ Accessibility
- **WCAG AAA** compliance
- **100% keyboard navigable** - 30+ shortcuts
- **Screen reader friendly** - Semantic HTML + ARIA
- **Reduced motion mode** - Respects user preferences
- **Colorblind-safe** - All 8 types supported

### 🎯 Touch-First, Keyboard-Enhanced
- Natural gestures: pinch, rotate, long-press, swipe
- Power-user shortcuts: Vim-style navigation
- Bottom sheet UI for mobile
- Command center layout for desktop

---

## 🚀 Quick Start

### Prerequisites
```bash
# Node.js 20+
node --version  # v20.x.x

# Python 3.11+
python --version  # 3.11.x

# Docker & Docker Compose
docker --version  # 20.x.x+
docker compose version  # 2.x.x+

# Sutra Platform (must be running)
cd .sutra/compose && docker compose -f production.yml ps
# Verify storage-server and user-storage-server are running
```

### Option 1: Docker (Recommended for Production)

```bash
# 1. Navigate to explorer
cd packages/sutra-explorer

# 2. Ensure Sutra platform is running
# The explorer connects to existing storage servers via TCP
docker ps | grep -E 'storage-server|user-storage'

# 3. Start explorer services
docker compose up -d

# 4. Check health
curl http://localhost:8100/health  # Backend
curl http://localhost:3000/health  # Frontend

# 5. Open browser
open http://localhost:3000
```

**What this does:**
- Backend connects to `storage-server:50051` (domain knowledge)
- Backend connects to `user-storage-server:50051` (user data)
- Frontend served on `:3000` (Nginx)
- Backend API on `:8100` (FastAPI)
- All communication via TCP binary protocol (NO direct storage access)

### Option 2: Local Development

```bash
# 1. Install Python dependencies
cd packages/sutra-explorer/backend
pip install -r requirements.txt

# 2. Install storage client (workspace package)
pip install -e ../../sutra-storage-client-tcp

# 3. Start backend (terminal 1)
export SUTRA_USER_STORAGE=localhost:50053
export SUTRA_DOMAIN_STORAGE=localhost:50051
export CORS_ORIGINS=http://localhost:5173
uvicorn main:app --reload --host 0.0.0.0 --port 8100

# 4. Install frontend dependencies (terminal 2)
cd ../frontend
npm install

# 5. Start frontend dev server
VITE_API_URL=http://localhost:8100 npm run dev

# 6. Open browser
open http://localhost:5173  # Vite dev server
```

**Port Configuration:**
- `50051` - Main storage server (domain)
- `50053` - User storage server
- `8100` - Explorer backend API
- `5173` - Frontend dev server (Vite)
- `3000` - Frontend production (Nginx)

---

## 📖 Usage

### Keyboard Shortcuts

**Navigation:**
- `Space + Drag` - Pan canvas
- `Ctrl/Cmd + F` - Focus search
- `Tab` / `Shift+Tab` - Cycle nodes
- `↑ ↓ ← →` - Navigate graph
- `Home` / `End` - Jump to root/last

**View Control:**
- `F` - Fit all to screen
- `1-5` - Switch view modes (List/2D/Tree/2.5D/3D)
- `+` / `-` - Zoom in/out
- `0` - Reset zoom
- `Shift + G` - Toggle grid
- `Shift + M` - Toggle minimap

**Actions:**
- `Ctrl/Cmd + N` - New annotation
- `Ctrl/Cmd + S` - Screenshot
- `Ctrl/Cmd + B` - Bookmark node
- `Delete` - Hide selected nodes
- `Shift + H` - Show all hidden

**Selection:**
- `Ctrl/Cmd + A` - Select all
- `Shift + Click` - Add to selection
- `Alt + Click` - Quick peek

### Touch Gestures

- **Single tap** - Select node
- **Double tap** - Expand to full screen
- **Long press** - Context menu (radial)
- **Pinch** - Zoom in/out
- **Two-finger rotate** - 3D rotation
- **Swipe left/right** - Navigate history
- **Pull down** - Refresh/return to overview

### API Integration

```typescript
// Use REST API directly
const response = await fetch('http://localhost:8100/concepts/abc123');
const concept = await response.json();

// Or use the provided client
import { ExplorerAPI } from '@sutra/explorer';

const api = new ExplorerAPI('http://localhost:8100');
const concepts = await api.getConcepts({ limit: 100 });
const path = await api.findPath('id1', 'id2', { maxDepth: 6 });
```

---

## 🏗️ Architecture

### Stack
- **Frontend:** React 18 + TypeScript + Vite
- **UI Framework:** `@sutra/ui-framework` (holographic theme)
- **Rendering:** D3.js (2D), Three.js (3D), react-window (lists)
- **Backend:** Python 3.11 + FastAPI
- **Parser:** Rust (storage.dat v2 format)
- **State:** Zustand (lightweight)

### Design Principles
1. **UI Framework Constraint** - STRICTLY use `@sutra/ui-framework` components
2. **Adaptive Rendering** - Auto-select optimal visualization
3. **Performance First** - 60fps minimum, progressive loading
4. **Accessibility** - WCAG AAA, keyboard navigable, colorblind-safe
5. **Read-Only** - Safe exploration, no modification

---

## 📊 API Documentation

### Base URL
```
http://localhost:8100
```

### Endpoints

**Storage Management:**
```bash
GET  /health                        # Health check
POST /load                          # Load storage file
GET  /stats                         # Storage statistics
```

**Concepts:**
```bash
GET  /concepts?limit=100&offset=0   # List concepts
GET  /concepts/{id}                 # Get concept details
POST /search                        # Full-text search
```

**Graph Operations:**
```bash
GET  /associations/{id}             # Get neighbors
POST /path                          # Find path between nodes
POST /neighborhood                  # Get N-hop neighborhood
```

**Vectors:**
```bash
POST /similarity                    # Cosine similarity
```

**Interactive Docs:**
- Swagger UI: http://localhost:8100/docs
- ReDoc: http://localhost:8100/redoc

---

## 🎨 Theming

Uses `holographicTheme` from `@sutra/ui-framework`:

```typescript
import { ThemeProvider, holographicTheme } from '@sutra/ui-framework';

<ThemeProvider theme={holographicTheme}>
  <App />
</ThemeProvider>
```

**Theme Features:**
- Single cyan accent color
- Grayscale text hierarchy
- Frosted glass panels
- Subtle glow effects
- Scanline textures
- Monospace typography

---

## 🔧 Configuration

### Environment Variables

```bash
# Backend
STORAGE_PATH=/path/to/storage.dat   # Path to storage file
API_HOST=0.0.0.0                    # API host
API_PORT=8100                       # API port
CORS_ORIGINS=http://localhost:5173  # CORS allowed origins

# Frontend
VITE_API_URL=http://localhost:8100  # Backend API URL
VITE_ENABLE_3D=true                 # Enable 3D rendering
VITE_ENABLE_VR=false                # Enable VR mode (experimental)
```

---

## 🧪 Testing

```bash
# Frontend unit tests
cd frontend
npm test

# Frontend E2E tests
npm run test:e2e

# Backend tests
cd backend
pytest tests/

# Rust parser tests
cargo test
```

---

## 📦 Build

```bash
# Development build
npm run build:dev

# Production build (optimized)
npm run build

# Docker build
docker build -t sutra-explorer:latest .
```

---

## 🤝 Contributing

This is a **clean slate rewrite**. Key principles:

1. **STRICT UI framework usage** - ALL components via `@sutra/ui-framework`
2. **No backward compatibility** - Fresh start, modern patterns
3. **Performance obsessed** - 60fps minimum everywhere
4. **Accessibility first** - WCAG AAA, keyboard nav, colorblind-safe
5. **Documentation** - Every component documented with examples

---

## 📄 License

Part of the Sutra AI project. See main repository for license.

---

## 🔗 Related

- **Vision:** `docs/sutra-explorer/NEXT_GENERATION_VISION.md`
- **UI Spec:** `docs/sutra-explorer/HOLOGRAPHIC_UI_SPEC.md`
- **Architecture:** `packages/sutra-explorer/ARCHITECTURE.md`
- **UI Framework:** `packages/sutra-ui-framework/`

---

**Built for the future of knowledge graph exploration** 🚀
