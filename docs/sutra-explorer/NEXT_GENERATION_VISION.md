# 🚀 Sutra Explorer: Next-Generation Vision

**Date:** October 28, 2025  
**Status:** Clean Slate - Zero Backward Compatibility  
**Target:** Best-in-class knowledge graph explorer for mobile to 8K displays

---

## 🎯 Executive Summary

Build the **world's most intuitive knowledge graph explorer** with a **holographic HUD aesthetic** that works seamlessly across:
- 📱 **Mobile** (375px - touch-first, minimal UI)
- 💻 **Desktop** (1920x1080 - command center experience)
- 🖥️ **4K/8K** (3840x2160+ - immersive 3D holographic space)

**Core Innovation:** Adaptive rendering engine that chooses optimal visualization strategy based on device capabilities, screen real estate, and graph complexity.

**Design Philosophy:** 
- **Colorblind-safe** - Single cyan hue + brightness encoding
- **Accessibility-first** - WCAG AAA contrast, keyboard navigable
- **Minimal color dependency** - Information encoded in brightness, size, glow, animation
- **Sci-fi aesthetic** - Think JARVIS, not Rainbow Dashboard

---

## 🧠 Philosophical Foundation

### Beyond Classical Graph Visualization

Traditional graph tools (Neo4j Browser, Gephi, Cytoscape) fail because:
1. **Single rendering mode** - Force-directed layout doesn't scale
2. **Desktop-only** - Mobile experiences are afterthoughts
3. **Overwhelming** - No progressive disclosure for complex graphs
4. **Static** - Can't adapt to user intent or graph structure

### Our Principles

```
1. PROGRESSIVE DISCLOSURE
   Show minimal essential → reveal complexity on demand

2. CONTEXT-AWARE RENDERING
   Automatic mode selection: List / 2D / 2.5D / 3D / VR

3. TOUCH-FIRST, KEYBOARD-ENHANCED
   Natural gestures, then power-user shortcuts

4. SEMANTIC UNDERSTANDING
   Not just nodes/edges - understand medical protocols, legal chains, causal flows

5. PERFORMANCE AS FEATURE
   60fps on mobile, 120fps on desktop, GPU-accelerated where possible
```

---

## 🎨 Adaptive Rendering Engine

### Automatic Mode Selection Matrix

| Condition | Rendering Mode | Technology | FPS Target |
|-----------|---------------|------------|------------|
| **Mobile, <20 nodes** | List View | React virtualized list | 60 |
| **Mobile, 20-100 nodes** | Cluster Map | 2D Canvas + clustering | 60 |
| **Mobile, >100 nodes** | Heatmap View | WebGL shaders | 60 |
| **Desktop, <50 nodes** | Force-Directed 2D | D3.js force simulation | 60 |
| **Desktop, 50-500 nodes** | Hierarchical Tree | Dagre layout | 60 |
| **Desktop, >500 nodes** | 2.5D Graph | Three.js with instancing | 60 |
| **4K, any size** | 3D Immersive | Three.js + GPU particles | 120 |
| **VR/AR ready** | Spatial Graph | WebXR + hand tracking | 90 |

### User Override

Always allow manual mode switching:
```
Toolbar: [Auto] [List] [2D] [Tree] [2.5D] [3D] [VR]
```

---

## 📱 Mobile-First Design (375px - 428px)

### Holographic HUD Layout

```
┌───────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← Status bar (cyan glow)
│ ╔═══════════════════════════════════╗ │
│ ║ SUTRA [◇] [▽] [○] [MENU]         ║ │ ← Header (56px, frosted glass)
│ ╚═══════════════════════════════════╝ │
│                                       │
│ ┌─────────────────────────────────┐   │
│ │  ╭─────────────────────────────╮ │   │
│ │  │  ▓                          │ │   │ ← Canvas (full height)
│ │  │    ▓▓    ◉─────◉           │ │   │   Graph visualization
│ │  │  ▓   ▓    │     │           │ │   │   area
│ │  │    ▓      ◉     ◉           │ │   │
│ │  │                              │ │   │
│ │  │    NODE:0xA3F8               │ │   │ ← Mini-inspector
│ │  │    [████░░] 0.87              │ │   │   (overlay)
│ │  ╰─────────────────────────────╯ │   │
│ └─────────────────────────────────┘   │
│                                       │
│ ┌─────────────────────────────────┐   │ ← Bottom HUD panel
│ │ ═══════════════════════════════ │   │   (draggable)
│ │ SELECTED: Central Concept       │   │
│ │ CONF: 0.94 | EDGES: 12         │   │   Collapsed state
│ │ [▼ EXPAND FOR DETAILS]         │   │   (80px)
│ └─────────────────────────────────┘   │
│                                       │
│               ◉                       │ ← FAB (floating action)
└───────────────────────────────────────┘

Bottom panel states:
1. Collapsed (80px) - Summary only
2. Half (50% screen) - Key details + actions
3. Full (90% screen) - Complete node data
```

### Core Interactions (Touch Gestures)

**Holographic Touch Feedback:**
```typescript
// Visual feedback on touch
onTouchStart: {
  effect: 'ripple',         // Cyan ripple from touch point
  glow: 'pulse',            // Glow intensity increases
  haptic: 'light',          // Subtle vibration
  sound: 'soft-beep',       // Optional audio (sci-fi)
}

// Gesture library
gestures: {
  singleTap: {
    action: 'Select node',
    feedback: 'Cyan pulse around node',
    duration: '300ms',
  },
  
  doubleTap: {
    action: 'Expand to full screen',
    feedback: 'Zoom animation with trail effect',
    duration: '500ms',
  },
  
  longPress: {
    action: 'Context menu (radial)',
    feedback: 'Expanding cyan ring',
    threshold: '500ms',
    menu: [
      { icon: '◇', label: 'BOOKMARK', angle: 0° },
      { icon: '⊕', label: 'EXPAND', angle: 90° },
      { icon: '⊗', label: 'HIDE', angle: 180° },
      { icon: '⊙', label: 'INFO', angle: 270° },
    ],
  },
  
  pinch: {
    action: 'Zoom',
    feedback: 'Grid scales, nodes resize smoothly',
    minZoom: 0.1,
    maxZoom: 10,
  },
  
  twoFingerRotate: {
    action: '3D rotation (if in 3D mode)',
    feedback: 'Perspective grid rotates',
    enabled: '3D mode only',
  },
  
  swipeLeftRight: {
    action: 'Navigate history',
    feedback: 'Slide transition with blur',
    threshold: '50px',
  },
  
  pullDown: {
    action: 'Refresh / Return to overview',
    feedback: 'Expanding circular glow',
    threshold: '100px',
  },
}
```

### Mobile-Optimized Views

#### 1. **List View** (< 20 nodes)
```tsx
<VirtualizedList>
  <ConceptCard>
    <Thumbnail /> {/* 48x48 icon */}
    <Content>
      <Title>Diabetes Type 2</Title>
      <Metadata>
        <Chip>Medical</Chip>
        <Badge>92% confidence</Badge>
      </Metadata>
      <Preview>Chronic condition affecting...</Preview>
    </Content>
    <Actions>
      <IconButton>chevron_right</IconButton>
    </Actions>
  </ConceptCard>
</VirtualizedList>
```

#### 2. **Cluster Map** (20-100 nodes)
```
Visual: Bubble chart with semantic clustering
- Bubble size = node importance (PageRank)
- Brightness = confidence (bright = high, dim = low)
- Glow intensity = activity/relevance
- Touch bubble → zoom into cluster
- Pinch out → zoom back to overview
```

#### 3. **Heatmap View** (>100 nodes)
```
Visual: Grid-based heatmap (like GitHub contributions)
- Cell brightness = confidence score (bright = high, dim = low)
- Cell size = edge count
- Cyan glow intensity = importance
- Touch cell → show mini-preview
- Long press → expand full node
```

### Mobile Performance Targets

```
Initial load: < 2s (lazy load off-screen)
60fps scrolling (virtualized lists)
Touch response: < 100ms (no jank)
Zoom smoothness: Hardware-accelerated
Memory budget: < 200MB (iOS Safari limit)
```

---

## 💻 Desktop Experience (1920x1080)

### Command Center Layout (Holographic HUD)

```
┌───────────────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← Top glow
│ ╔═══════════════════════════════════════════════════════════════╗ │
│ ║ [◇] SUTRA.EXPLORER  [⊡ 2D] [⊞ 3D] [⊠ LIST]  [◉◉◉] 03:47:21 ║ │ ← 64px header
│ ╚═══════════════════════════════════════════════════════════════╝ │
├────────┬────────────────────────────────────────────┬─────────────┤
│        │                                            │             │
│ ╔════╗ │  ┌──────────────────────────────────────┐ │ ╔═════════╗ │
│ ║NAV ║ │  │                                      │ │ ║ INSPECT ║ │
│ ╠════╣ │  │        ▓     ◉─────◉                 │ │ ╠═════════╣ │
│ ║    ║ │  │      ▓▓▓▓     │     │                │ │ ║ NODE:   ║ │
│ ║ ◉  ║ │  │    ▓     ▓    ◉     ◉                │ │ ║ 0xA3F8  ║ │
│ ║ ◉  ║ │  │      ▓▓▓      │  ╱                   │ │ ║         ║ │
│ ║ ◉  ║ │  │                ◉                     │ │ ║ TYPE:   ║ │
│ ║    ║ │  │                                      │ │ ║ MEDICAL ║ │
│ ║ ◉  ║ │  │  MAIN CANVAS (HOLOGRAPHIC VIEW)      │ │ ║         ║ │
│ ║ ◉  ║ │  │                                      │ │ ║ CONF:   ║ │
│ ║    ║ │  │  ┌────────────────────────────────┐  │ │ ║ 94%     ║ │
│ ║    ║ │  │  │ MINIMAP                        │  │ │ ║         ║ │
│ ║    ║ │  │  │  ▓▓  ▓                         │  │ │ ║ EDGES:  ║ │
│ ║    ║ │  │  │    ▓                           │  │ │ ║ 12      ║ │
│ ║    ║ │  │  └────────────────────────────────┘  │ │ ║         ║ │
│ ╚════╝ │  └──────────────────────────────────────┘ │ ║ [═════] ║ │
│        │                                            │ ║ ACTION  ║ │
│ 240px  │   PRIMARY INTERACTION AREA                 │ ╚═════════╝ │
│        │                                            │   340px     │
└────────┴────────────────────────────────────────────┴─────────────┘
    ↑                      ↑                               ↑
  Tree nav          Force-directed graph          Inspector panel
  Bookmarks         Holographic rendering          Live details
  History           Touch-free zone                Metadata
```

### Advanced Interactions (Command Center)

**Mouse Control (Precision):**
```typescript
mouse: {
  click: {
    action: 'Select node',
    feedback: 'Cyan pulse + inspector update',
    modifier: {
      shift: 'Add to selection',
      ctrl: 'Toggle selection',
      alt: 'Quick peek (no selection)',
    },
  },
  
  doubleClick: {
    action: 'Focus mode (isolate node + neighbors)',
    feedback: 'Dim unrelated nodes to 10% opacity',
    duration: '400ms',
  },
  
  rightClick: {
    action: 'Context menu (list style)',
    feedback: 'Frosted glass panel appears at cursor',
    items: [
      '▸ EXPAND NODE',
      '▸ HIDE NODE',
      '▸ BOOKMARK',
      '▸ EXPORT SUBGRAPH',
      '▸ CREATE NOTE',
      '▸ COPY ID',
    ],
  },
  
  hover: {
    action: 'Show tooltip',
    feedback: 'Subtle glow increase',
    delay: '300ms',
    tooltip: {
      style: 'Minimal frosted glass',
      content: 'ID | Confidence | Edge count',
    },
  },
  
  drag: {
    action: 'Reposition node',
    feedback: 'Trailing glow effect',
    behavior: 'Physics engine pauses for dragged node',
  },
  
  scroll: {
    action: 'Zoom at cursor position',
    feedback: 'Smooth zoom with grid scale',
    sensitivity: 'Configurable (default: 0.1 per tick)',
  },
  
  middleButton: {
    action: 'Pan canvas',
    feedback: 'Cursor changes to move icon',
    behavior: 'Drag to pan',
  },
}
```

**Keyboard Shortcuts (Power Users):**
```
NAVIGATION:
  Space + Drag     → Pan canvas (hand tool)
  Ctrl/Cmd + F     → Focus search bar
  Esc              → Deselect all / Exit mode
  Tab              → Cycle selected node's neighbors
  Shift + Tab      → Reverse cycle
  ↑ ↓ ← →          → Navigate graph (arrow keys)
  Home             → Jump to root/center
  End              → Jump to last selected

VIEW CONTROL:
  F                → Fit all nodes to screen
  1                → List view
  2                → 2D force-directed
  3                → Hierarchical tree
  4                → 2.5D layered
  5                → 3D immersive
  + or =           → Zoom in
  - or _           → Zoom out
  0                → Reset zoom to 100%
  [ ]              → Adjust node size
  { }              → Adjust edge thickness
  Shift + G        → Toggle grid
  Shift + M        → Toggle minimap

ACTIONS:
  Ctrl/Cmd + N     → Create annotation
  Ctrl/Cmd + E     → Export current view
  Ctrl/Cmd + S     → Screenshot (downloads PNG)
  Ctrl/Cmd + P     → Print reasoning path
  Ctrl/Cmd + B     → Bookmark selected node
  Ctrl/Cmd + Z     → Undo layout change
  Ctrl/Cmd + Y     → Redo layout change
  Delete/Backspace → Hide selected nodes
  Shift + H        → Show all hidden nodes

SELECTION:
  Ctrl/Cmd + A     → Select all visible nodes
  Ctrl/Cmd + I     → Invert selection
  Shift + Click    → Add to selection
  Ctrl + Click     → Toggle selection
  Alt + Click      → Quick peek (no selection change)

FILTERS:
  Ctrl/Cmd + 1-9   → Apply saved filter preset
  Shift + C        → Clear all filters
  /                → Quick filter (type to filter)

DEBUG (Dev mode):
  Ctrl + Shift + D → Show debug overlay (FPS, memory)
  Ctrl + Shift + I → Inspector panel
  Ctrl + Shift + L → Console logs
```

### Desktop-Specific Features

#### 1. **Multi-Select with Lasso (Holographic Style)**
```
Hold Shift + Drag → Draw cyan lasso around nodes
│                                                  │
│    ╭─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─╮                   │
│   ╱          ◉         ◉      ╲                 │
│  │      ◉                 ◉    │                │
│  │                              │                │
│   ╲                            ╱                 │
│    ╰─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─╯                   │
│                                                  │
Selected nodes pulse with cyan glow
Mini-toolbar appears: [◇ BOOKMARK] [⊗ HIDE] [⊕ EXPAND] [⊙ EXPORT]
```

#### 2. **Holographic Minimap**
```
┌────────────────┐
│ ╔════════════╗ │
│ ║ ▓▓░░░░     ║ │ ← Current viewport (cyan outline)
│ ║ ░░▓▓░░     ║ │ ← All nodes (dimmed)
│ ║ ░░░░▓▓     ║ │ ← Click to jump
│ ╚════════════╝ │
│ NODES: 847     │
│ VISIBLE: 142   │
└────────────────┘

Style: Frosted glass background
       Monochrome (brightness = importance)
       Cyan box for viewport
```

#### 3. **Timeline Scrubber** (Temporal Graphs)
```
┌──────────────────────────────────────────────────────────┐
│ ╔════════════════════════════════════════════════════╗   │
│ ║ [◀] ──────────────●──────────────── [▶] [⏸]      ║   │
│ ║ 2020 ───────── 2022 ─────────── 2024 ───── 2025  ║   │
│ ╚════════════════════════════════════════════════════╝   │
│ EVENTS: 347 | SHOWING: 2023-06-15 | SPEED: 1x          │
└──────────────────────────────────────────────────────────┘

- Drag scrubber to see graph at specific time
- Play button animates evolution
- Speed control: 0.5x, 1x, 2x, 5x, 10x
- Events appear/disappear with fade effect
```

---

## 🖥️ 4K/8K Experience (3840x2160+)

### Holographic Immersive Mode

**Philosophy:** At high resolutions, leverage extra space for depth, not clutter.

```
┌──────────────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                                  │
│      ╭─────╮                                      ╭─────╮       │
│      │ HUD │                                      │ HUD │       │
│      ╰─────╯                                      ╰─────╯       │
│                                                                  │
│                                                                  │
│                        ▓▓▓                                       │
│                      ▓▓   ▓▓                                     │
│                    ▓▓  ◉   ▓▓                                    │
│         ◉─────────────╱ ╲─────────────◉                         │
│          ╲           ╱   ╲           ╱                          │
│           ╲         ╱     ╲         ╱                           │
│            ◉───────◉       ◉───────◉                            │
│             │       │       │       │                           │
│             ◉       ◉       ◉       ◉                           │
│                                                                  │
│         3D HOLOGRAPHIC SPACE (FULL IMMERSION)                   │
│         Nodes float at different Z depths                       │
│         Perspective grid provides spatial reference             │
│                                                                  │
│      ╭─────╮                                      ╭─────╮       │
│      │ HUD │                                      │ HUD │       │
│      ╰─────╯                                      ╰─────╯       │
│                                                                  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└──────────────────────────────────────────────────────────────────┘

Layout: Minimal UI chrome, maximum graph space
        Corner HUDs (non-intrusive)
        Transparent overlays only
        Full-screen 3D rendering
```

### 3D Navigation (Holographic Space)

**Camera Controls (Sci-Fi Flight Sim Style):**
```typescript
camera: {
  // WASD flight controls
  forward: 'W',        // Fly towards center
  backward: 'S',       // Fly away
  left: 'A',           // Strafe left
  right: 'D',          // Strafe right
  up: 'Q',             // Ascend
  down: 'E',           // Descend
  
  // Mouse controls
  middleDrag: 'Orbit around center',
  rightDrag: 'Pan in 3D space',
  scroll: 'Zoom (field of view)',
  
  // Advanced
  shift: 'Sprint (5x speed)',
  ctrl: 'Slow mode (0.2x speed)',
  
  // Preset views
  '7': 'Top view (orthographic)',
  '1': 'Front view',
  '3': 'Side view',
  '0': 'Free camera',
}
```

### 3D Layout Algorithms (Holographic)

#### 1. **Force-Directed 3D** (Most Natural)
```typescript
// Three.js d3-force-3d
const simulation = d3Force3d()
  .nodes(graphNodes)
  .links(graphEdges)
  .force('charge', d3.forceManyBody()
    .strength(-100)           // Repulsion
    .distanceMax(500))        // Falloff distance
  .force('link', d3.forceLink()
    .distance(link => {
      // Distance by confidence
      return 100 / link.confidence;
    }))
  .force('center', d3.forceCenter(0, 0, 0))
  .force('collision', d3.forceCollide()
    .radius(node => node.size * 1.5));

// Z-axis encodes semantic meaning
node.z = {
  medical: 100,      // Medical concepts float high
  legal: 0,          // Legal at center plane
  financial: -100,   // Financial sink low
}[node.domain];
```

#### 2. **Hierarchical 3D Tree** (Clearest Structure)
```typescript
// Root at center, descendants in expanding spheres
const layout = {
  root: { x: 0, y: 0, z: 0 },
  
  // Level 1: 8 nodes evenly distributed on sphere
  level1: arrangeOnSphere(8, radius: 200),
  
  // Level 2: 24 nodes on larger sphere
  level2: arrangeOnSphere(24, radius: 400),
  
  // Level 3: 72 nodes
  level3: arrangeOnSphere(72, radius: 600),
};

// Golden ratio spiral for even distribution
function arrangeOnSphere(count, radius) {
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  return Array.from({ length: count }, (_, i) => {
    const y = 1 - (i / (count - 1)) * 2; // -1 to 1
    const radiusAtY = Math.sqrt(1 - y * y);
    const theta = goldenAngle * i;
    
    return {
      x: Math.cos(theta) * radiusAtY * radius,
      y: y * radius,
      z: Math.sin(theta) * radiusAtY * radius,
    };
  });
}
```

#### 3. **GPU Particle System** (>10K Nodes)
```glsl
// Vertex shader (runs on GPU for each node)
attribute vec3 position;      // Node position
attribute float confidence;   // Node confidence
attribute float importance;   // Node importance (PageRank)

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform float time;           // For animation

varying float vConfidence;
varying float vImportance;

void main() {
  // Pulse effect based on confidence
  float pulse = sin(time * 2.0 + position.x) * 0.1;
  vec3 animatedPos = position + vec3(0, pulse * confidence, 0);
  
  // Size by importance
  gl_PointSize = 5.0 + importance * 20.0;
  
  // Position in 3D space
  gl_Position = projectionMatrix * viewMatrix * vec4(animatedPos, 1.0);
  
  // Pass to fragment shader
  vConfidence = confidence;
  vImportance = importance;
}
```

```glsl
// Fragment shader (colors each pixel)
varying float vConfidence;
varying float vImportance;

void main() {
  // Circular point shape
  vec2 center = gl_PointCoord - vec2(0.5);
  float dist = length(center);
  
  if (dist > 0.5) discard;  // Circular clipping
  
  // Holographic cyan glow
  float glow = 1.0 - dist * 2.0;  // Bright center, fade edges
  vec3 color = vec3(0.0, 1.0, 1.0) * glow * vConfidence;
  
  // Opacity by importance
  float alpha = vImportance * 0.8;
  
  gl_FragColor = vec4(color, alpha);
}
```

### Visual Enhancements for High-Res

**4K/8K Exclusive Effects:**
```typescript
// Post-processing stack (Three.js)
const composer = new EffectComposer(renderer);

// 1. Bloom pass (cyan glow)
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(width, height),
  strength: 0.4,        // Subtle glow
  radius: 0.6,          // Glow spread
  threshold: 0.5        // Only bright pixels glow
);

// 2. SMAA anti-aliasing (crystal clear edges)
const smaaPass = new SMAAPass(width, height);

// 3. Depth of field (focus on selected cluster)
const dofPass = new BokehPass(scene, camera, {
  focus: selectedNode.z,  // Focus distance
  aperture: 0.00002,      // Blur strength
  maxblur: 0.01           // Max blur amount
});

// 4. Ambient occlusion (realistic depth cues)
const aoPass = new SSAOPass(scene, camera, width, height);
aoPass.kernelRadius = 16;
aoPass.minDistance = 0.001;
aoPass.maxDistance = 0.1;

// 5. Film grain (subtle texture)
const filmPass = new FilmPass(
  noiseIntensity: 0.05,   // Very subtle
  scanlinesIntensity: 0.02,
  scanlinesCount: 2048,
  grayscale: false
);

// Apply in order
composer.addPass(bloomPass);
composer.addPass(smaaPass);
composer.addPass(dofPass);      // Optional, when node selected
composer.addPass(aoPass);
composer.addPass(filmPass);
```

### Density Modes

```
Sparse Mode:  Show only high-confidence edges (>0.8)
Normal Mode:  Show all edges with alpha by confidence
Dense Mode:   Show all connections (debugging)
```

---

## 🎮 Rendering Technology Stack

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  React UI Layer (Controls, HUD, Modals)        │
├─────────────────────────────────────────────────┤
│  Rendering Coordinator                          │
│  - Detects device capability                    │
│  - Chooses optimal renderer                     │
│  - Manages mode transitions                     │
├──────────┬──────────┬──────────┬────────────────┤
│ SVG      │ Canvas   │ WebGL    │ WebXR          │
│ Renderer │ Renderer │ Renderer │ Renderer       │
│          │          │          │                │
│ D3.js    │ D3+      │ Three.js │ Three.js +     │
│          │ Canvas   │          │ XR API         │
│          │          │          │                │
│ <100     │ 100-1K   │ 1K-100K  │ 100K+ nodes    │
│ nodes    │ nodes    │ nodes    │ (spatial)      │
└──────────┴──────────┴──────────┴────────────────┘
```

### Technology Choices

#### 1. **SVG Renderer** (Simple graphs)
```tsx
Library: react-flow or D3.js
Use case: <100 nodes, PDF export, accessibility
Pros:
  ✓ Crisp at any zoom
  ✓ CSS styling (can apply holographic effects)
  ✓ Screen reader friendly
  ✓ Easy debugging (inspect DOM)
Cons:
  ✗ Slow with many nodes
  ✗ Limited post-processing effects

Visual style:
  - Monochrome with cyan accent
  - CSS filters for glow effects
  - SVG gradients for depth cues
```

#### 2. **Canvas 2D Renderer** (Medium graphs)
```tsx
Library: D3.js + raw Canvas API
Use case: 100-1000 nodes, mobile devices
Pros:
  ✓ Fast rendering (bitmap)
  ✓ Low memory usage
  ✓ Good mobile support
  ✓ Can apply glow effects via shadow API
Cons:
  ✗ Pixelated at high zoom
  ✗ No CSS styling
  ✗ Manual hit testing

Visual style:
  - Grayscale base with cyan highlights
  - Canvas shadowBlur for glow effects
  - Custom rendering for holographic borders
```

#### 3. **WebGL Renderer** (Large graphs, 3D)
```tsx
Library: Three.js + react-three-fiber
Use case: 1K-100K nodes, desktop/4K
Pros:
  ✓ GPU-accelerated
  ✓ 3D capabilities
  ✓ Shader effects (bloom, glow, DOF)
  ✓ Instanced rendering
Cons:
  ✗ Complex code
  ✗ GPU compatibility issues
  ✗ Higher power usage

Visual style:
  - Full post-processing stack
  - UnrealBloomPass for cyan glow
  - Custom shaders for holographic effects
  - Depth of field for focus
```

#### 4. **WebXR Renderer** (VR/AR future)
```tsx
Library: Three.js + WebXR API
Use case: 100K+ nodes, spatial computing
Pros:
  ✓ Immersive exploration
  ✓ Natural 3D navigation
  ✓ Hand gestures
  ✓ Holographic aesthetic perfect for VR
Cons:
  ✗ Requires VR headset
  ✗ Limited adoption (2025)
  ✗ Motion sickness concerns

Visual style:
  - Ultra-minimal UI (spatial HUD)
  - Cyan holographic wireframes
  - Floating information panels
  - Hand-tracking for interaction
```

---

## ⚡ Performance Optimization Strategies

### 1. **Progressive Loading**

```typescript
// Load in stages for large graphs
Stage 1: Load core concepts (central nodes)         → 100ms
Stage 2: Load 1-hop neighbors                       → 200ms  
Stage 3: Load 2-hop neighbors (background)          → 500ms
Stage 4: Load full graph (on demand)                → 2000ms

User sees partial graph in 100ms, full in 2s
```

### 2. **Level of Detail (LOD)**

```typescript
// Adjust rendering quality by zoom level
Zoom < 0.5:  Show clusters only (aggregate nodes)
Zoom 0.5-2:  Show nodes as circles with labels
Zoom 2-5:    Show full node cards
Zoom > 5:    Show node details, thumbnails, metadata

// Edge rendering LOD
Far:   Don't render (invisible)
Mid:   Render as thin lines (no labels)
Close: Render with labels and confidence scores
```

### 3. **GPU Instancing** (WebGL only)

```typescript
// Render 10,000 nodes in single draw call
const geometry = new THREE.InstancedBufferGeometry();
const material = new THREE.ShaderMaterial({
  vertexShader: `...`,   // Position + color per instance
  fragmentShader: `...`, // Same shader for all nodes
});

// Update positions without recreating geometry
instancedMesh.instanceMatrix.needsUpdate = true;
```

### 4. **Spatial Indexing**

```typescript
// Octree for 3D, Quadtree for 2D
class SpatialIndex {
  query(viewport: BoundingBox): Node[] {
    // Only return nodes in current view
    // Enables culling of off-screen nodes
  }
}

// Render only visible nodes
const visibleNodes = spatialIndex.query(camera.viewport);
renderer.render(visibleNodes);
```

### 5. **Web Workers for Layout**

```typescript
// Offload physics simulation to worker thread
const layoutWorker = new Worker('force-layout.worker.ts');

layoutWorker.postMessage({
  nodes: graphNodes,
  edges: graphEdges,
  iterations: 300
});

layoutWorker.onmessage = (e) => {
  updateNodePositions(e.data.positions);
};
```

### Performance Budgets

```
Mobile (iPhone 13):
  - 60fps mandatory
  - < 200MB memory
  - < 500ms initial render
  - < 5% battery/minute

Desktop (M2 MacBook):
  - 60fps default, 120fps for <1K nodes
  - < 1GB memory
  - < 300ms initial render

4K Workstation (RTX 4090):
  - 120fps mandatory
  - < 4GB GPU memory
  - < 200ms initial render
  - Support for 100K+ nodes
```

---

## 🎨 Visual Design Language

### Holographic HUD Aesthetic

**Philosophy:** Minimal, functional, accessible. Like a sci-fi command center - not a colorful toy.

**Core Principles:**
- **Monochromatic base** - Dark void with glowing elements
- **Cyan/Teal primary** - High contrast, colorblind-safe
- **Subtle depth cues** - Glow, blur, transparency layers
- **Information density** - Every pixel serves a purpose
- **Accessibility-first** - WCAG AAA contrast ratios

### Color Palette (Holographic Mode)

```typescript
// Minimal color scheme - colorblind accessible
const holoColors = {
  // Base
  void: '#000000',           // Pure black background
  surface: '#0a0e14',        // Subtle surface lift
  border: '#1a2332',         // Container outlines
  
  // Primary (Cyan/Teal family - colorblind safe)
  glow: '#00ffff',           // Bright cyan glow (primary accent)
  primary: '#00d4d4',        // Teal for interactive elements
  primaryDim: '#00a8a8',     // Dimmed state
  
  // Monochrome hierarchy (gray scale)
  text: {
    primary: '#e0e6ed',      // High contrast white
    secondary: '#8892a0',    // Dimmed text
    tertiary: '#4a5568',     // Subtle labels
    disabled: '#2d3748',     // Inactive elements
  },
  
  // Confidence (single hue, varying intensity)
  confidence: {
    high: '#00ffff',         // Bright cyan (>90%)
    medium: '#00d4d4',       // Mid cyan (70-90%)
    low: '#008b8b',          // Dark cyan (<70%)
    critical: '#ff4444',     // Red for warnings only
  },
  
  // Functional colors (minimal, high contrast)
  status: {
    success: '#00ff88',      // Bright green (colorblind safe)
    warning: '#ffbb00',      // Amber (accessible)
    error: '#ff4444',        // Bright red
    info: '#00ddff',         // Cyan-blue
  },
  
  // Transparency layers (for depth)
  alpha: {
    glass: 'rgba(10, 14, 20, 0.7)',     // Frosted glass panels
    overlay: 'rgba(0, 0, 0, 0.85)',     // Modal overlays
    hover: 'rgba(0, 212, 212, 0.1)',    // Hover state
    selected: 'rgba(0, 255, 255, 0.15)', // Selection highlight
  },
};
```

### Visual Hierarchy (No Color Overload)

```
┌──────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← Glow line (cyan)
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  NODE: Central Concept             │ │ ← Bright cyan border
│  │  ╔══════════════════════════════╗  │ │
│  │  ║ Content preview text here... ║  │ │ ← Gray text on dark
│  │  ╚══════════════════════════════╝  │ │
│  │  [●●●●●●●○○○] 94%                │ │ ← Confidence bar
│  └────────────────────────────────────┘ │
│                                          │
│  ┌──────────────────┐                   │
│  │  Secondary Node  │                   │ ← Dimmed cyan
│  │  Preview text    │                   │
│  │  [●●●●○○○○○○] 78% │                   │
│  └──────────────────┘                   │
│                                          │
└──────────────────────────────────────────┘

Brightness hierarchy:
1. Bright cyan (#00ffff) - Primary focus, active elements
2. Mid cyan (#00d4d4) - Interactive elements, hover states
3. Dark cyan (#008b8b) - Low confidence, subtle elements
4. Gray scale (#e0e6ed → #2d3748) - All text content
5. Pure black (#000000) - Background void
```

### Holographic Effects

```css
/* Glow effect (key to holographic aesthetic) */
.holo-glow {
  box-shadow: 
    0 0 5px rgba(0, 255, 255, 0.3),    /* Inner glow */
    0 0 10px rgba(0, 255, 255, 0.2),   /* Mid glow */
    0 0 20px rgba(0, 255, 255, 0.1);   /* Outer glow */
  
  border: 1px solid rgba(0, 255, 255, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

/* Frosted glass panels (depth) */
.holo-panel {
  background: rgba(10, 14, 20, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(26, 35, 50, 0.8);
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 2px 10px rgba(0, 0, 0, 0.5);
}

/* Scanline effect (subtle texture) */
.holo-scanlines::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 255, 255, 0.03) 2px,
    rgba(0, 255, 255, 0.03) 4px
  );
  pointer-events: none;
}

/* Holographic text (subtle glow) */
.holo-text {
  color: #e0e6ed;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-weight: 300;
  letter-spacing: 0.05em;
}

/* Edge highlight (subtle 3D feel) */
.holo-edge {
  border-top: 1px solid rgba(0, 255, 255, 0.3);
  border-left: 1px solid rgba(0, 255, 255, 0.2);
  border-bottom: 1px solid rgba(0, 255, 255, 0.05);
  border-right: 1px solid rgba(0, 255, 255, 0.05);
}
```

### Typography (Monospace for HUD Aesthetic)

```css
/* Holographic interface typography */
:root {
  /* Font families */
  --font-mono: 'Roboto Mono', 'SF Mono', 'Courier New', monospace;
  --font-display: 'Inter', 'SF Pro Display', system-ui, sans-serif;
  
  /* Responsive type scale (tighter for HUD) */
  --text-xs:    clamp(9px, 1.2vw, 11px);    /* Micro labels */
  --text-sm:    clamp(11px, 1.5vw, 13px);   /* Secondary text */
  --text-base:  clamp(13px, 2vw, 15px);     /* Body text */
  --text-lg:    clamp(15px, 2.5vw, 17px);   /* Emphasis */
  --text-xl:    clamp(17px, 3vw, 20px);     /* Headings */
  --text-2xl:   clamp(20px, 3.5vw, 28px);   /* Section titles */
  --text-3xl:   clamp(28px, 4vw, 42px);     /* Hero text (rare) */
  
  /* Font weights (minimal variation) */
  --weight-light: 300;
  --weight-normal: 400;
  --weight-bold: 500;  /* Never go heavier - keeps it crisp */
  
  /* Letter spacing (wider for monospace readability) */
  --tracking-tight: -0.01em;
  --tracking-normal: 0.02em;
  --tracking-wide: 0.05em;
  --tracking-wider: 0.1em;
}

/* Typography classes */
.hud-text-primary {
  font-family: var(--font-mono);
  color: #e0e6ed;
  font-weight: var(--weight-normal);
  letter-spacing: var(--tracking-normal);
  text-shadow: 0 0 8px rgba(0, 255, 255, 0.2);
}

.hud-text-label {
  font-family: var(--font-mono);
  color: #8892a0;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  font-weight: var(--weight-bold);
}

.hud-text-code {
  font-family: var(--font-mono);
  color: #00ffff;
  font-size: var(--text-sm);
  letter-spacing: var(--tracking-normal);
  background: rgba(0, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 2px;
}
```

### Node Visual Hierarchy (Holographic Style)

```
┌────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← Bright glow
│  ╔════════════════════════════════════════╗  │
│  ║ NODE:0xA3F8 [CENTRAL_CONCEPT]         ║  │
│  ║                                        ║  │
│  ║ Content: Diabetes requires regular... ║  │
│  ║                                        ║  │
│  ║ [████████░] 0.94 CONFIDENCE            ║  │
│  ║ EDGES: 12 | DEPTH: 0 | TYPE: MEDICAL  ║  │
│  ╚════════════════════════════════════════╝  │
└────────────────────────────────────────────────┘
                     ↑
              Brightest, largest
              Pure cyan border
              Monospace text

┌──────────────────────────────────┐
│ ─────────────────────────────── │ ← Dimmed glow
│  ╔═══════════════════════════╗  │
│  ║ NODE:0xB2E9 [PRIMARY]     ║  │
│  ║ Content: Regular exercise ║  │
│  ║ [██████░░░] 0.78          ║  │
│  ╚═══════════════════════════╝  │
└──────────────────────────────────┘
             ↑
       Medium size
       Dimmed cyan
       Less detail

┌────────────────────┐
│ ─────────────────  │ ← Faint glow
│  ╔══════════════╗  │
│  ║ 0xC1D4       ║  │
│  ║ [████░░░░░░] ║  │
│  ╚══════════════╝  │
└────────────────────┘
        ↑
   Small, minimal
   Very dim cyan
   ID + confidence only

Visual encoding (no color dependency):
- Brightness = Importance
- Border thickness = Confidence
- Glow intensity = Activity/Focus
- Size = Hierarchy level
```

### Edge Styling (Holographic Connections)

```typescript
// Minimal edge styling - brightness encodes confidence
const holoEdgeStyle = (confidence: number) => ({
  // Width by confidence (subtle variation)
  width: confidence > 0.9 ? 2 : confidence > 0.7 ? 1.5 : 1,
  
  // Opacity encodes confidence (primary visual cue)
  opacity: 0.2 + (confidence * 0.6),  // 0.2 (low) to 0.8 (high)
  
  // Dash pattern for uncertainty
  dashArray: confidence < 0.6 ? '4,4' : null,
  
  // Glow strength by confidence
  glowIntensity: confidence * 0.4,
  
  // Always cyan (no color variation)
  color: '#00ffff',
  
  // Animation for high-confidence paths
  animated: confidence > 0.85,
  animationSpeed: confidence, // Faster = higher confidence
  
  // Blur for depth (distant edges more blurred)
  blur: confidence < 0.5 ? 2 : 0,
});

// Edge flow animation (data packet traveling)
const edgeFlowEffect = {
  gradient: [
    { offset: 0, color: 'rgba(0, 255, 255, 0)' },
    { offset: 0.5, color: 'rgba(0, 255, 255, 0.8)' },
    { offset: 1, color: 'rgba(0, 255, 255, 0)' },
  ],
  duration: '2s',
  direction: 'source-to-target',
};
```

### Holographic Grid (Background Layer)

```css
/* Subtle perspective grid (sci-fi floor) */
.holo-grid {
  background-image: 
    /* Horizontal lines */
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 49px,
      rgba(0, 255, 255, 0.03) 49px,
      rgba(0, 255, 255, 0.03) 50px
    ),
    /* Vertical lines */
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 49px,
      rgba(0, 255, 255, 0.03) 49px,
      rgba(0, 255, 255, 0.03) 50px
    );
  
  /* Perspective effect (vanishing point at center) */
  transform-origin: center center;
  perspective: 1000px;
}

/* Radial fade (darker at edges) */
.holo-vignette::after {
  content: '';
  position: fixed;
  inset: 0;
  background: radial-gradient(
    circle at center,
    transparent 0%,
    transparent 50%,
    rgba(0, 0, 0, 0.5) 100%
  );
  pointer-events: none;
}
```

---

## 🔍 Advanced Features

### 1. **Semantic Zoom (Holographic LOD)**

Different information at different zoom levels - no color changes, only detail level:

```
Zoom 0.1x - 1x:  Cluster aggregates (glowing regions)
                 - Show only high-level groupings
                 - Brightness indicates cluster density
                 
Zoom 1x - 3x:    Node IDs + confidence bars
                 - Minimal node cards
                 - Monospace labels
                 - Glow intensity by importance
                 
Zoom 3x - 10x:   Full holographic cards
                 - Content previews
                 - Metadata bars
                 - Edge labels visible
                 
Zoom 10x+:       Maximum detail
                 - Full text content
                 - All metadata fields
                 - Timestamps, sources, tags
                 - Frosted glass panels
```

### 2. **Time Travel Mode (Holographic History)**

Visualize how knowledge graph evolved - brightness encodes recency:

```tsx
<HolographicTimeline>
  <Scrubber value={currentDate} onChange={setDate} />
  <PlayButton onClick={animateHistory} />
  <SpeedControl options={['0.5x', '1x', '2x', '5x']} />
</HolographicTimeline>

// Visual changes over time:
- New concepts: Fade in with bright cyan glow
- Confidence updates: Glow intensity changes
- Deleted concepts: Fade to 10% opacity (ghosted)
- Active concepts: Pulsing glow animation
- Historical concepts: Dimmed but visible

// No color timeline - just timestamps + brightness
```

### 3. **Path Highlighting (Holographic Traces)**

Trace reasoning chains with dramatic glow effects:

```tsx
<HolographicPathControls>
  <Select>Shortest Path</Select>
  <Select>All Paths</Select>
  <Select>High Confidence Only</Select>
</HolographicPathControls>

// Visual effects (no color changes):
- Non-path nodes: Dim to 10% opacity
- Path nodes: Bright cyan glow (100% opacity)
- Path edges: Animated flow effect
  - Brightness pulses travel along edge
  - Speed = confidence level
  - Width increases for path edges
- Start node: Double-ring glow
- End node: Triple-ring glow
- Intermediate nodes: Single-ring glow

// Confidence visualization:
[████████░░] 94%  ← High confidence (bright, thick)
[██████░░░░] 78%  ← Medium (dimmer, thinner)
[███░░░░░░░] 42%  ← Low (very dim, dashed)
```

### 4. **Concept Bookmarking (Holographic Pins)**

Pin important nodes with visual markers:

```tsx
<HolographicBookmarkPanel>
  <BookmarkedConcept
    id="0xA3F8"
    title="Diabetes Type 2"
    tags={['CRITICAL', 'FREQUENT']}
    onClick={() => focusNode(conceptId)}
  />
</HolographicBookmarkPanel>

// Bookmarked nodes visual treatment:
- Always visible (never culled by LOD)
- Permanent pulsing glow
- ◇ diamond icon overlay (cyan)
- Frosted glass bookmark panel
- Monospace uppercase labels
- Quick-jump from sidebar
- Brightness boost (+20%)
```

### 5. **Collaborative Annotations (Holographic Notes)**

Multi-user notes with minimal visual footprint:

```tsx
<HolographicAnnotation
  author="DR.CHEN"
  timestamp="2025-10-28T10:30:00Z"
  content="Protocol updated Q3 2025"
  position={[x, y, z]}  // 3D space coordinate
/>

// Visual style:
- Frosted glass speech bubble
- Monospace text (all caps)
- Cyan accent line to concept
- Author initials in corner
- Timestamp in military time
- Hover to expand full content
- Click to edit (authorized users)

// Features:
- @mention other users
- Attach files (show file count)
- Version history (timeline view)
- Markdown support (rendered minimally)
```

### 6. **Export Capabilities (Holographic Capture)**

```
Image Export:
  - PNG (current view, transparent background option)
  - SVG (vector, preserves glow effects as filters)
  - High-DPI (2x, 3x for retina displays)

Report Export:
  - PDF (monochrome print-friendly + cyan highlights)
  - Markdown (with ASCII art node diagrams)
  - HTML (standalone, includes CSS holographic effects)

Data Export:
  - JSON (raw graph data, includes visual metadata)
  - GraphML (import to other tools)
  - CSV (node list + confidence + metadata)
  - DOT (Graphviz format)

Video Export:
  - MP4 (animated tour of reasoning path)
  - GIF (looping animation, optimized)
  - WebM (high quality, smaller file size)
  - Configurable: FPS, resolution, camera path

// All exports maintain holographic aesthetic
// Monochrome + cyan theme preserved
```

---

## 🧩 Component Architecture

### Core Components

```
src/
├── core/
│   ├── RenderingCoordinator.tsx      # Chooses optimal renderer
│   ├── GraphDataManager.ts           # State management (Zustand)
│   ├── PerformanceMonitor.ts         # FPS, memory tracking
│   └── LayoutEngine.ts               # Force-directed, hierarchical, etc.
│
├── renderers/
│   ├── SVGRenderer.tsx               # D3.js-based 2D
│   ├── CanvasRenderer.tsx            # Raw Canvas API
│   ├── WebGLRenderer.tsx             # Three.js 3D
│   └── WebXRRenderer.tsx             # VR/AR (future)
│
├── layouts/
│   ├── MobileLayout.tsx              # Bottom sheet + canvas
│   ├── DesktopLayout.tsx             # Triple pane
│   └── ImmersiveLayout.tsx           # Full-screen 3D
│
├── interactions/
│   ├── TouchController.ts            # Gesture recognition
│   ├── MouseController.ts            # Desktop interactions
│   └── KeyboardController.ts         # Shortcuts
│
├── visualization/
│   ├── Node.tsx                      # SVG/Canvas/WebGL node
│   ├── Edge.tsx                      # Connection rendering
│   ├── Cluster.tsx                   # Aggregated node group
│   └── MiniMap.tsx                   # Overview widget
│
└── ui/
    ├── Inspector.tsx                 # Right panel (desktop)
    ├── BottomSheet.tsx               # Mobile details
    ├── Toolbar.tsx                   # Mode selector, actions
    └── SearchBar.tsx                 # Semantic search
```

### State Management (Zustand)

```typescript
interface GraphStore {
  // Data
  nodes: ConceptNode[];
  edges: Association[];
  
  // View state
  selectedNode: string | null;
  hoveredNode: string | null;
  viewport: { x: number; y: number; zoom: number };
  renderMode: 'svg' | 'canvas' | 'webgl' | 'webxr';
  
  // Layout state
  layoutAlgorithm: 'force' | 'hierarchical' | 'circular';
  layoutRunning: boolean;
  
  // Performance
  fps: number;
  nodeCount: number;
  visibleNodes: number;
  
  // Actions
  selectNode: (id: string) => void;
  focusNode: (id: string) => void;
  setRenderMode: (mode: RenderMode) => void;
  resetLayout: () => void;
}
```

---

## 🧪 Testing Strategy

### Performance Testing

```typescript
describe('Performance Benchmarks', () => {
  test('Render 10,000 nodes at 60fps', () => {
    const graph = generateGraph(10000);
    const renderer = new WebGLRenderer(graph);
    
    const fps = measureFPS(renderer, duration: 10000);
    expect(fps).toBeGreaterThan(58); // Allow 2fps variance
  });
  
  test('Initial load under 2s on mobile', () => {
    const startTime = performance.now();
    loadGraph(smallMedicalGraph);
    const loadTime = performance.now() - startTime;
    
    expect(loadTime).toBeLessThan(2000);
  });
});
```

### Visual Regression Testing

```typescript
// Playwright with Percy integration
test('Node rendering consistency', async ({ page }) => {
  await page.goto('/explorer?graph=test-medical');
  await page.waitForSelector('.graph-canvas');
  
  // Take screenshot
  await percySnapshot(page, 'Medical Graph - Default View');
  
  // Zoom in
  await page.mouse.wheel(0, -100);
  await percySnapshot(page, 'Medical Graph - Zoomed');
});
```

### Accessibility Testing

```typescript
// Ensure keyboard navigation works
test('Keyboard navigation', async ({ page }) => {
  await page.keyboard.press('Tab'); // Focus first node
  await expect(page.locator('[data-selected="true"]')).toBeVisible();
  
  await page.keyboard.press('ArrowRight'); // Select neighbor
  await expect(page.locator('[data-selected="true"]')).toHaveCount(1);
});
```

---

## 📊 Success Metrics

### Performance KPIs

```
Mobile:
  ✓ 60fps maintained for graphs up to 500 nodes
  ✓ Initial render < 2s
  ✓ Touch response < 100ms
  ✓ Memory usage < 200MB

Desktop:
  ✓ 60fps maintained for graphs up to 5,000 nodes
  ✓ Initial render < 1s
  ✓ Smooth zooming (no stutter)
  ✓ Memory usage < 1GB

4K/8K:
  ✓ 120fps maintained for graphs up to 10,000 nodes
  ✓ Initial render < 500ms
  ✓ Support for 100K+ nodes (with LOD)
  ✓ GPU memory < 4GB
```

### User Experience KPIs

```
✓ Time to first interaction: < 3s
✓ Task completion rate: > 90% (find specific concept)
✓ User satisfaction (NPS): > 50
✓ Daily active users retention: > 70% (week 2)
```

---

## 🗺️ Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

```
✓ Rendering coordinator (auto-select mode)
✓ SVG renderer (D3.js force-directed)
✓ Canvas renderer (fallback for performance)
✓ Mobile layout (bottom sheet)
✓ Desktop layout (triple pane)
✓ Basic interactions (click, hover, zoom)
✓ Performance monitoring
```

### Phase 2: Advanced Rendering (Weeks 3-4)

```
✓ WebGL renderer (Three.js)
✓ 3D force-directed layout
✓ GPU instancing for large graphs
✓ Level of detail system
✓ Spatial indexing (Octree)
✓ Progressive loading
```

### Phase 3: Rich Interactions (Weeks 5-6)

```
✓ Touch gestures (pinch, rotate, swipe)
✓ Keyboard shortcuts
✓ Multi-select with lasso
✓ Path highlighting
✓ Semantic zoom
✓ Time travel mode
```

### Phase 4: Polish & Scale (Weeks 7-8)

```
✓ Responsive design (mobile → 8K)
✓ Dark/light mode
✓ Accessibility (WCAG 2.1 AA)
✓ Export capabilities
✓ Performance optimization
✓ Documentation
```

### Phase 5: Future Innovations (Backlog)

```
✓ WebXR renderer (VR/AR)
✓ AI-powered layout suggestions
✓ Natural language search
✓ Collaborative annotations
✓ Real-time multi-user
```

---

## 🚀 Quick Start (Developer)

### Installation

```bash
cd packages/sutra-explorer
npm install
```

### Development

```bash
# Start with hot reload
npm run dev

# Test on mobile (scan QR code)
npm run dev -- --host

# Build for production
npm run build

# Analyze bundle size
npm run analyze
```

### Device Testing

```bash
# Test on different screen sizes
npm run test:mobile    # 375x667 (iPhone SE)
npm run test:tablet    # 768x1024 (iPad)
npm run test:desktop   # 1920x1080
npm run test:4k        # 3840x2160
```

---

## 📚 Technical References

### Libraries

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Zustand** - State management (lighter than Redux)
- **Three.js** - WebGL 3D rendering
- **react-three-fiber** - React bindings for Three.js
- **D3.js** - 2D layouts and force simulation
- **react-spring** - Physics-based animations
- **use-gesture** - Touch gesture recognition
- **framer-motion** - UI animations
- **react-virtuoso** - Virtualized lists
- **react-window** - Efficient scrolling

### Performance Tools

- **Lighthouse** - Performance audits
- **WebPageTest** - Real-world performance
- **Chrome DevTools Performance** - Profiling
- **React Profiler** - Component render tracking
- **GPU Shark** - GPU usage monitoring

---

## 🎯 Competitive Analysis

### What We Offer That Others Don't

| Feature | Neo4j Browser | Gephi | Cytoscape | **Sutra Explorer** |
|---------|--------------|-------|-----------|-------------------|
| Mobile-first | ❌ | ❌ | ❌ | ✅ |
| Adaptive rendering | ❌ | ❌ | ❌ | ✅ |
| Touch gestures | ❌ | ❌ | ❌ | ✅ |
| 3D visualization | ❌ | ❌ | ⚠️ (plugin) | ✅ |
| Semantic zoom | ❌ | ❌ | ❌ | ✅ |
| Time travel | ❌ | ❌ | ❌ | ✅ |
| VR/AR ready | ❌ | ❌ | ❌ | ✅ |
| 60fps on mobile | ❌ | ❌ | ❌ | ✅ |
| Domain-aware | ❌ | ❌ | ❌ | ✅ |
| Colorblind-safe | ❌ | ❌ | ❌ | ✅ |
| WCAG AAA | ❌ | ❌ | ❌ | ✅ |
| Keyboard-only | ⚠️ (partial) | ⚠️ (partial) | ⚠️ (partial) | ✅ (complete) |

---

## 💡 Innovation Highlights

### 1. **Context-Aware Mode Selection**

First graph explorer to automatically choose the best rendering strategy based on:
- Device capabilities (GPU, memory, screen size)
- Graph complexity (node/edge count, density)
- User intent (exploring vs. presenting)

### 2. **Holographic HUD Aesthetic**

Not another colorful dashboard - a functional sci-fi command center:
- Single cyan hue (#00ffff) + grayscale
- Information encoded in brightness, not color
- Accessible to all types of colorblindness
- WCAG AAA contrast (14.6:1 ratios)
- Frosted glass panels, glow effects, scanlines

### 3. **Semantic-First Design**

Not just generic nodes/edges:
- Medical protocols render as flowcharts
- Legal precedents show hierarchical chains
- Financial data displays as timeline events
- Causal relationships animate as flows
- Domain-specific layouts automatically applied

### 4. **Progressive Disclosure**

Never overwhelm the user:
- Start with minimal essential information
- Reveal complexity on demand
- Adapt to user's exploration pattern
- Learn preferred visualization modes
- Semantic zoom (not just geometric zoom)

### 5. **Touch-First, Keyboard-Enhanced**

Mobile is primary, desktop adds power:
- Natural gestures (everyone knows pinch-to-zoom)
- Then layer on keyboard shortcuts for pros
- Opposite of desktop-first apps (better UX)
- Haptic feedback on supported devices

### 6. **Performance as Feature**

60fps isn't a target, it's the product:
- Smooth interactions build trust
- Fast responses feel intelligent
- 120fps on high-end displays feels magical
- GPU-accelerated where possible
- Progressive loading (never block)

---

## 🎬 Conclusion

We're not building another graph visualization tool. We're creating the **definitive holographic knowledge exploration experience** that:

1. **Works everywhere** - From iPhone to 8K displays, consistent aesthetic
2. **Adapts intelligently** - Automatic optimization per device
3. **Feels natural** - Touch-first, keyboard-enhanced
4. **Scales massively** - 100K+ nodes on high-end hardware
5. **Looks stunning** - Sci-fi command center aesthetic
6. **Accessible to all** - Colorblind-safe, WCAG AAA compliant

**Design Pillars:**
- 🎨 **Holographic HUD** - Minimal cyan on black, not rainbow chaos
- ♿ **Accessibility-first** - Information encoded redundantly (brightness, size, glow, animation)
- ⚡ **Performance-obsessed** - 60fps minimum, 120fps on capable hardware
- 🧠 **Semantic-aware** - Medical protocols ≠ legal chains ≠ financial data
- 📐 **Mathematically precise** - Golden ratio layouts, physics-based interactions

**Zero backward compatibility means we can build the future without constraints.**

This isn't just a tool - it's the interface future data scientists will expect from all knowledge graph systems.

Let's create something extraordinary. 🚀

---

**Implementation Priority:**
1. **Week 1-2**: Holographic component library + rendering coordinator
2. **Week 3-4**: Mobile experience + touch gestures
3. **Week 5-6**: Desktop command center + 3D renderer
4. **Week 7-8**: Polish, accessibility audit, performance optimization

**Success Metrics:**
- ✅ 60fps on iPhone 13 with 500 nodes
- ✅ WCAG AAA contrast ratios (14.6:1)
- ✅ Keyboard navigable (zero mouse required)
- ✅ Works for all colorblindness types
- ✅ 120fps on RTX 4090 with 10K nodes

**Questions? Ideas?** See `/docs/sutra-explorer/HOLOGRAPHIC_UI_SPEC.md` for detailed implementation guide.
