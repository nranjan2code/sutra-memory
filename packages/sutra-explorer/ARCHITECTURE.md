# Sutra Explorer - Next-Generation Architecture

**Version:** 2.0 (Complete Rewrite)  
**Date:** October 29, 2025  
**Status:** Clean Slate - Zero Backward Compatibility  
**Framework:** Strictly uses `@sutra/ui-framework`

---

## 🎯 Mission

Build the **world's best knowledge graph explorer** for Sutra AI with:
- **Holographic HUD aesthetic** (cyan monochrome, sci-fi)
- **Adaptive rendering** (mobile to 8K displays)
- **Colorblind-safe** (WCAG AAA, brightness encoding)
- **Touch-first, keyboard-enhanced** (natural gestures + power shortcuts)
- **60fps everywhere** (mobile), 120fps (desktop)
- **Read-only safe** (standalone exploration tool)

---

## 🏗️ Architecture Principles

### 1. **UI Framework Constraint (STRICT)**
```typescript
// ✅ CORRECT - Always use sutra-ui-framework
import { Button, Card, Badge, Text, holographicTheme } from '@sutra/ui-framework';

// ❌ FORBIDDEN - No direct Material-UI or custom components
import { Button } from '@mui/material';  // NEVER
import MyCustomButton from './MyButton';  // NEVER (unless wrapper)
```

**Why:** Unified design system, consistent theme application, reusable across all Sutra apps.

### 2. **Adaptive Rendering Strategy**
```typescript
interface RenderStrategy {
  mode: 'list' | 'cluster' | 'force2d' | 'tree' | '2.5d' | '3d' | 'vr';
  reason: string;
  technology: 'react-window' | 'd3' | 'three.js' | 'webxr';
  fpsTarget: 60 | 120;
}

const selectRenderMode = (
  deviceType: 'mobile' | 'tablet' | 'desktop' | '4k',
  nodeCount: number,
  screenSize: { width: number; height: number }
): RenderStrategy => {
  // Mobile optimization
  if (deviceType === 'mobile') {
    if (nodeCount < 20) return { mode: 'list', ... };
    if (nodeCount < 100) return { mode: 'cluster', ... };
    return { mode: 'force2d', ... };  // Simplified 2D
  }
  
  // Desktop command center
  if (deviceType === 'desktop') {
    if (nodeCount < 50) return { mode: 'force2d', ... };
    if (nodeCount < 500) return { mode: 'tree', ... };
    return { mode: '2.5d', ... };
  }
  
  // 4K/8K immersive
  if (deviceType === '4k') {
    return { mode: '3d', fpsTarget: 120, ... };
  }
};
```

### 3. **Holographic Theme Integration**
```typescript
// All components wrapped in ThemeProvider
import { ThemeProvider, holographicTheme } from '@sutra/ui-framework';

<ThemeProvider theme={holographicTheme}>
  <ExplorerApp />
</ThemeProvider>
```

**Visual Rules:**
- **Single color:** Cyan (#00ffff) + grayscale
- **Brightness encoding:** High = important, Low = inactive
- **No color for information:** Size, glow, opacity, animation instead
- **WCAG AAA:** 14.6:1 contrast ratio minimum

### 4. **Performance Targets**
```typescript
const PERFORMANCE_TARGETS = {
  mobile: {
    initialLoad: 2000,    // ms
    fps: 60,
    memoryBudget: 200,    // MB
    touchResponse: 100,   // ms
  },
  desktop: {
    initialLoad: 500,     // ms
    fps: 60,
    memoryBudget: 1000,   // MB
    mouseResponse: 16,    // ms (1 frame)
  },
  highEnd: {
    initialLoad: 200,     // ms
    fps: 120,
    memoryBudget: 2000,   // MB
    mouseResponse: 8,     // ms (1 frame @ 120fps)
  },
};
```

---

## 📦 Package Structure

```
packages/sutra-explorer-new/
├── ARCHITECTURE.md                 # This file
├── README.md                       # User documentation
├── package.json                    # TypeScript dependencies
├── Cargo.toml                      # Rust parser dependencies
├── tsconfig.json                   # TypeScript config
├── vite.config.ts                  # Vite bundler config
├── Dockerfile                      # Multi-stage build
├── docker-compose.yml              # Standalone deployment
│
├── src/                            # Rust parser (read-only)
│   ├── lib.rs                      # Storage.dat v2 parser
│   ├── parser.rs                   # Binary format parser
│   └── graph.rs                    # Graph query operations
│
├── backend/                        # FastAPI REST API
│   ├── main.py                     # API endpoints
│   ├── models.py                   # Pydantic models
│   └── requirements.txt            # Python deps
│
└── frontend/                       # React + TypeScript UI
    ├── public/
    │   └── index.html
    │
    ├── src/
    │   ├── App.tsx                 # Main entry point
    │   ├── main.tsx                # React DOM render
    │   │
    │   ├── components/             # UI components (using sutra-ui-framework)
    │   │   ├── layout/
    │   │   │   ├── Header.tsx      # Top nav bar
    │   │   │   ├── Sidebar.tsx     # Tree nav + bookmarks
    │   │   │   ├── Inspector.tsx   # Right panel details
    │   │   │   └── BottomSheet.tsx # Mobile drawer
    │   │   │
    │   │   ├── graph/
    │   │   │   ├── GraphRenderer.tsx       # Render coordinator
    │   │   │   ├── ListView.tsx            # List mode (react-window)
    │   │   │   ├── ClusterView.tsx         # Cluster mode (canvas)
    │   │   │   ├── Force2DView.tsx         # 2D force (D3.js)
    │   │   │   ├── TreeView.tsx            # Hierarchical (Dagre)
    │   │   │   ├── Force25DView.tsx        # 2.5D layered (Three.js)
    │   │   │   ├── Immersive3DView.tsx     # 3D immersive (Three.js)
    │   │   │   └── VRView.tsx              # VR mode (WebXR)
    │   │   │
    │   │   ├── nodes/
    │   │   │   ├── HolographicNode.tsx     # Node component (Card)
    │   │   │   ├── NodeInspector.tsx       # Detail view
    │   │   │   └── NodeTooltip.tsx         # Hover preview
    │   │   │
    │   │   ├── edges/
    │   │   │   ├── HolographicEdge.tsx     # Edge rendering
    │   │   │   └── EdgeLabel.tsx           # Edge tooltip
    │   │   │
    │   │   ├── controls/
    │   │   │   ├── SearchBar.tsx           # Full-text search
    │   │   │   ├── FilterPanel.tsx         # Filter controls
    │   │   │   ├── ViewModeSelector.tsx    # List/2D/3D switcher
    │   │   │   ├── ZoomControls.tsx        # +/- buttons
    │   │   │   └── Minimap.tsx             # Overview map
    │   │   │
    │   │   └── interactions/
    │   │       ├── TouchGestures.tsx       # Touch handlers
    │   │       ├── KeyboardShortcuts.tsx   # Keyboard nav
    │   │       ├── LassoSelect.tsx         # Multi-select
    │   │       └── ContextMenu.tsx         # Right-click menu
    │   │
    │   ├── hooks/
    │   │   ├── useDeviceDetection.ts       # Mobile/desktop/4K
    │   │   ├── useRenderStrategy.ts        # Auto mode selection
    │   │   ├── useKeyboardNav.ts           # Keyboard shortcuts
    │   │   ├── useTouchGestures.ts         # Touch handlers
    │   │   ├── useGraphData.ts             # API data fetching
    │   │   └── usePerformanceMonitor.ts    # FPS tracking
    │   │
    │   ├── services/
    │   │   ├── api.ts                      # REST API client
    │   │   └── storage.ts                  # Local state management
    │   │
    │   ├── utils/
    │   │   ├── graph-algorithms.ts         # BFS, DFS, pathfinding
    │   │   ├── layout-engines.ts           # Force/tree/hierarchical
    │   │   ├── performance.ts              # FPS, memory tracking
    │   │   └── accessibility.ts            # ARIA helpers
    │   │
    │   └── types/
    │       ├── graph.ts                    # Node, Edge, Graph types
    │       ├── render.ts                   # RenderStrategy types
    │       └── api.ts                      # API response types
    │
    └── package.json
```

---

## 🔌 API Design (Backend)

### REST Endpoints (FastAPI)

```python
# Storage Management
GET    /health                              # Health check + storage status
POST   /load                                # Load storage.dat file
GET    /stats                               # Storage statistics

# Concept Operations
GET    /concepts?limit=100&offset=0         # List concepts (paginated)
GET    /concepts/{id}                       # Get concept details
POST   /search                              # Full-text search

# Graph Operations
GET    /associations/{id}                   # Get concept neighbors
POST   /path                                # Find path between nodes
POST   /neighborhood                        # Get N-hop neighborhood

# Vector Operations
POST   /similarity                          # Cosine similarity between nodes

# Metadata
GET    /metadata                            # Graph metadata (types, domains)
```

### Response Models (Pydantic)

```python
class ConceptResponse(BaseModel):
    id: str
    content: str
    confidence: float
    strength: float
    access_count: int
    created_at: str
    metadata: Optional[Dict[str, Any]]
    neighbors: List[str]
    
class EdgeResponse(BaseModel):
    source_id: str
    target_id: str
    confidence: float
    edge_type: str
    
class GraphResponse(BaseModel):
    nodes: List[ConceptResponse]
    edges: List[EdgeResponse]
    stats: Dict[str, int]
```

---

## 🎨 Component Design (Frontend)

### Component Hierarchy

```
App (ThemeProvider)
├─ Header (using sutra-ui-framework Button, Text)
├─ Layout
│  ├─ Sidebar (using sutra-ui-framework Card)
│  │  ├─ SearchBar (using sutra-ui-framework Input)
│  │  ├─ TreeNav (using sutra-ui-framework Text, Badge)
│  │  └─ Bookmarks (using sutra-ui-framework Card, Button)
│  │
│  ├─ GraphCanvas
│  │  └─ GraphRenderer (adaptive)
│  │     ├─ ListView (react-window)
│  │     ├─ ClusterView (canvas)
│  │     ├─ Force2DView (D3.js)
│  │     ├─ TreeView (Dagre)
│  │     ├─ Force25DView (Three.js)
│  │     ├─ Immersive3DView (Three.js)
│  │     └─ VRView (WebXR)
│  │
│  └─ Inspector (using sutra-ui-framework Card, Text, Badge)
│     ├─ NodeDetails
│     ├─ NeighborList
│     └─ Actions (using sutra-ui-framework Button)
│
└─ BottomSheet (mobile only)
   ├─ QuickStats (using sutra-ui-framework Text, Badge)
   └─ QuickActions (using sutra-ui-framework Button)
```

### Example: HolographicNode Component

```typescript
import { Card, Text, Badge } from '@sutra/ui-framework';
import type { Node } from '../types/graph';

interface HolographicNodeProps {
  node: Node;
  state: 'idle' | 'hover' | 'selected' | 'dimmed';
  onSelect: (id: string) => void;
}

export const HolographicNode: React.FC<HolographicNodeProps> = ({
  node,
  state,
  onSelect,
}) => {
  return (
    <Card
      variant={state === 'selected' ? 'elevated' : 'default'}
      padding="md"
      interactive
      onClick={() => onSelect(node.id)}
      style={{
        // Holographic styling
        opacity: state === 'dimmed' ? 0.2 : 1,
        borderWidth: state === 'selected' ? 3 : 1,
        borderColor: 'rgba(0, 255, 255, 0.5)',
        
        // Glow by confidence
        boxShadow: `
          0 0 ${node.confidence * 10}px rgba(0, 255, 255, ${node.confidence * 0.3}),
          0 0 ${node.confidence * 20}px rgba(0, 255, 255, ${node.confidence * 0.2})
        `,
        
        // Animation
        animation: state === 'selected' ? 'pulse 2s ease-in-out infinite' : 'none',
      }}
    >
      <Card.Header>
        <Text variant="h6" color="primary">
          {node.id.substring(0, 8)}
        </Text>
        <Badge
          colorScheme={node.confidence > 0.8 ? 'success' : 'warning'}
          size="sm"
        >
          {Math.round(node.confidence * 100)}%
        </Badge>
      </Card.Header>
      
      <Card.Content>
        <Text variant="body2" color="secondary">
          {node.content.substring(0, 60)}...
        </Text>
      </Card.Content>
      
      <Card.Actions>
        <Badge colorScheme="info" size="sm">
          {node.edgeCount} edges
        </Badge>
      </Card.Actions>
    </Card>
  );
};
```

---

## 🚀 Performance Strategy

### 1. **Virtualization (Mobile/Desktop Lists)**
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={windowHeight}
  itemCount={nodes.length}
  itemSize={80}  // px per row
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <HolographicNode node={nodes[index]} />
    </div>
  )}
</FixedSizeList>
```

### 2. **Progressive Loading**
```typescript
const useProgressiveLoad = (nodes: Node[]) => {
  const [visibleNodes, setVisibleNodes] = useState<Node[]>([]);
  
  useEffect(() => {
    // Load 50 nodes at a time
    let offset = 0;
    const interval = setInterval(() => {
      if (offset < nodes.length) {
        setVisibleNodes(prev => [...prev, ...nodes.slice(offset, offset + 50)]);
        offset += 50;
      } else {
        clearInterval(interval);
      }
    }, 100);  // 100ms chunks
    
    return () => clearInterval(interval);
  }, [nodes]);
  
  return visibleNodes;
};
```

### 3. **GPU Instancing (3D Mode)**
```typescript
import { InstancedMesh } from 'three';

// Render 10K nodes with single draw call
const nodeGeometry = new SphereGeometry(1, 16, 16);
const nodeMaterial = new MeshBasicMaterial({ color: 0x00ffff });
const instancedMesh = new InstancedMesh(nodeGeometry, nodeMaterial, 10000);

nodes.forEach((node, i) => {
  const matrix = new Matrix4();
  matrix.setPosition(node.x, node.y, node.z);
  instancedMesh.setMatrixAt(i, matrix);
});
```

### 4. **Level of Detail (LOD)**
```typescript
const getNodeDetail = (zoomLevel: number, node: Node) => {
  if (zoomLevel < 0.5) {
    return 'minimal';  // Just a dot
  } else if (zoomLevel < 2.0) {
    return 'medium';   // Dot + label
  } else {
    return 'full';     // Full card with content
  }
};
```

---

## ♿ Accessibility Features

### 1. **Colorblind Safety**
```typescript
// All information encoded redundantly
const encodeImportance = (value: number) => ({
  size: 20 + value * 40,           // 20px to 60px
  opacity: 0.4 + value * 0.6,      // 0.4 to 1.0
  glowRadius: value * 20,          // 0 to 20px
  brightness: 0.3 + value * 0.7,   // 30% to 100% brightness
});
```

### 2. **Keyboard Navigation**
```typescript
const KeyboardShortcuts = () => {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Tab':
          focusNextNode();
          e.preventDefault();
          break;
        case 'Enter':
        case ' ':
          selectFocusedNode();
          e.preventDefault();
          break;
        case 'Escape':
          deselectAll();
          break;
        case 'f':
          fitToScreen();
          break;
        // ... 30+ shortcuts
      }
    };
    
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);
};
```

### 3. **Screen Reader Support**
```typescript
<div
  role="button"
  aria-label={`Concept ${node.content}. Confidence ${node.confidence * 100}%. ${node.edgeCount} connections.`}
  aria-pressed={node.selected}
  tabIndex={0}
  onKeyPress={(e) => e.key === 'Enter' && selectNode(node)}
>
  <HolographicNode node={node} />
</div>
```

---

## 🔧 Build & Deployment

### Docker Multi-Stage Build

```dockerfile
# Stage 1: Rust parser
FROM rust:1.75 as rust-builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src/
RUN cargo build --release

# Stage 2: Python backend
FROM python:3.11-slim as python-builder
WORKDIR /build
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/

# Stage 3: Frontend
FROM node:20 as frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 4: Final image
FROM python:3.11-slim
WORKDIR /app

# Copy binaries
COPY --from=rust-builder /build/target/release/libsutra_explorer.so ./
COPY --from=python-builder /build/backend/ ./backend/
COPY --from=frontend-builder /build/dist/ ./frontend/dist/

# Install runtime deps
RUN pip install --no-cache-dir uvicorn fastapi

EXPOSE 8100 3000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8100"]
```

---

## 📊 Success Metrics

### Performance KPIs
- ✅ 60fps on iPhone 13 (500 nodes)
- ✅ 120fps on RTX 4090 (10K nodes)
- ✅ <2s initial load (mobile)
- ✅ <500ms initial load (desktop)
- ✅ <200MB memory (mobile)
- ✅ <1GB memory (desktop)

### Accessibility KPIs
- ✅ WCAG AAA compliance (14.6:1 contrast)
- ✅ 100% keyboard navigable
- ✅ Screen reader friendly
- ✅ Works for all colorblindness types
- ✅ Reduced motion mode

### UX KPIs
- ✅ Time to first interaction: <3s
- ✅ Task completion rate: >90%
- ✅ User satisfaction (NPS): >50

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Current)
- [x] Architecture design
- [ ] Package structure
- [ ] Core components (using sutra-ui-framework)
- [ ] Rust parser
- [ ] FastAPI backend

### Phase 2: Rendering
- [ ] Adaptive rendering coordinator
- [ ] ListView (react-window)
- [ ] ClusterView (canvas)
- [ ] Force2DView (D3.js)

### Phase 3: Interactions
- [ ] Touch gestures
- [ ] Keyboard shortcuts
- [ ] Multi-select lasso
- [ ] Context menus

### Phase 4: Advanced
- [ ] 3D rendering (Three.js)
- [ ] VR mode (WebXR)
- [ ] Performance optimizations
- [ ] Accessibility audit

### Phase 5: Polish
- [ ] Documentation
- [ ] Docker deployment
- [ ] Integration tests
- [ ] User testing

---

**Next Steps:**
1. Delete old `packages/sutra-explorer`
2. Scaffold new package structure
3. Implement core components using sutra-ui-framework
4. Build adaptive rendering coordinator
5. Test on mobile devices

**Zero backward compatibility. Clean slate. Best practices only.** 🚀
