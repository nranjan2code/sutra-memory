# Sutra Desktop Architecture

**Version:** 3.3.0  
**Updated:** November 26, 2025

This document describes the internal architecture of Sutra Desktop, including module structure, data flow, and design decisions.

---

## Design Principles

### 1. Zero Code Duplication

The desktop application is a **thin UI wrapper** around `sutra-storage`. All storage logic, including:
- Concept learning and retrieval
- Graph traversal and pathfinding
- HNSW vector indexing
- WAL-based persistence

...comes directly from the shared crate. This ensures:
- Feature parity with server deployments
- Single source of truth for storage logic
- Automatic updates when storage crate improves

### 2. Immediate Mode GUI

Using **egui** (immediate mode GUI), the UI is:
- Rebuilt every frame (~60 FPS)
- Stateless rendering (state lives in data structures)
- Highly responsive with no layout thrashing
- Memory efficient with minimal allocations

### 3. Single-Threaded UI with Background Storage

- **UI Thread**: All egui rendering and user interaction
- **Storage Operations**: Most operations are synchronous but fast (<10ms)
- **Future**: Long operations (bulk import, export) will use tokio for async

---

## Module Structure

```
desktop/
├── Cargo.toml              # Dependencies and features
├── scripts/
│   └── build-macos.sh      # macOS app bundle script
└── src/
    ├── main.rs             # Entry point, window setup
    ├── app.rs              # Main application controller
    ├── theme.rs            # Color palette and styling
    ├── types.rs            # Shared data types
    └── ui/
        ├── mod.rs          # Module exports
        ├── sidebar.rs      # Navigation sidebar
        ├── chat.rs         # Chat interface
        ├── knowledge.rs    # Concept browser
        ├── settings.rs     # Settings panel
        ├── status_bar.rs   # Bottom status bar
        ├── graph_view.rs   # Interactive graph visualization
        ├── reasoning_paths.rs   # MPPA path explorer
        ├── temporal_view.rs     # Timeline analysis
        ├── causal_view.rs       # Root cause analysis
        ├── analytics.rs         # Performance dashboard
        ├── query_builder.rs     # Advanced search
        └── export_import.rs     # Data portability
```

---

## Core Components

### main.rs - Application Entry Point

```rust
fn main() -> Result<()> {
    // 1. Initialize logging
    // 2. Configure native window options
    // 3. Apply custom theme
    // 4. Create and run SutraApp
}
```

Responsibilities:
- Tracing/logging setup
- Window configuration (size, icon, title)
- Theme application to egui context
- eframe application lifecycle

### app.rs - Application Controller

```rust
pub struct SutraApp {
    // Storage engine (from sutra-storage crate)
    storage: Arc<ConcurrentMemory>,
    data_dir: PathBuf,
    
    // Core UI panels
    sidebar: Sidebar,
    chat: ChatPanel,
    knowledge: KnowledgePanel,
    settings: SettingsPanel,
    status_bar: StatusBar,
    
    // Enhanced UI panels
    graph_view: GraphView,
    reasoning_paths: ReasoningPathsPanel,
    temporal_view: TemporalView,
    causal_view: CausalView,
    analytics: AnalyticsDashboard,
    query_builder: QueryBuilder,
    export_import: ExportImportPanel,
    
    // State
    initialized: bool,
}
```

Key methods:
- `new()` - Initialize storage and all panels
- `update()` - egui frame update (called 60x/sec)
- `handle_*_action()` - Action handlers for each panel
- `on_exit()` - Flush storage on shutdown

### theme.rs - Visual Design System

Color palette following modern dark theme principles:

```rust
// Primary colors
pub const PRIMARY: Color32 = Color32::from_rgb(167, 139, 250);     // Vibrant Purple
pub const SECONDARY: Color32 = Color32::from_rgb(96, 165, 250);    // Sky Blue
pub const ACCENT: Color32 = Color32::from_rgb(251, 191, 36);       // Amber
pub const SUCCESS: Color32 = Color32::from_rgb(52, 211, 153);      // Emerald
pub const WARNING: Color32 = Color32::from_rgb(251, 146, 60);      // Orange
pub const ERROR: Color32 = Color32::from_rgb(248, 113, 113);       // Red

// Backgrounds
pub const BG_DARK: Color32 = Color32::from_rgb(15, 15, 25);        // Darkest
pub const BG_PANEL: Color32 = Color32::from_rgb(22, 22, 35);       // Panels
pub const BG_WIDGET: Color32 = Color32::from_rgb(35, 35, 55);      // Inputs/cards
```

Helper functions:
- `setup_custom_theme()` - Apply theme to egui context
- `card_frame()` - Styled card component
- `elevated_card()` - More prominent card variant
- `button_frame()` - Styled button container

### types.rs - Shared Data Structures

Types used across multiple panels:

```rust
// Graph visualization
pub struct GraphNode { id, label, content, confidence, x, y, vx, vy }
pub struct GraphEdge { from, to, strength, edge_type }
pub enum EdgeType { Semantic, Causal, Temporal, Hierarchical, Similar }

// Reasoning paths (MPPA)
pub struct ReasoningPath { path: Vec<PathStep>, confidence, depth }
pub struct ConsensusResult { primary_cluster, alternatives, total_paths }

// Temporal analysis
pub struct TimelineEvent { concept_id, label, timestamp, relative_time }
pub enum TemporalRelation { Before, After, During, Concurrent }

// Causal analysis
pub struct CausalChain { nodes: Vec<CausalNode>, confidence, depth }
pub enum CausalRelationType { DirectCause, IndirectCause, Contributing, Correlation }

// Analytics
pub struct AnalyticsMetrics { total_concepts, total_edges, query_latency_ms, ... }

// Query builder
pub struct QueryFilters { min_confidence, max_results, has_causal, has_temporal, ... }

// Export/import
pub enum ExportFormat { Json, Csv, GraphML, Cypher }
```

---

## Data Flow

### Action-Handler Pattern

Each UI panel communicates through a typed action enum:

```rust
// Panel returns optional action
pub fn ui(&mut self, ui: &mut egui::Ui) -> Option<ChatAction> {
    // ... render UI ...
    if button_clicked {
        return Some(ChatAction::Learn(content));
    }
    None
}

// App controller handles actions
fn handle_chat_action(&mut self, action: ChatAction) {
    match action {
        ChatAction::Learn(content) => {
            self.storage.learn_concept(...);
            self.refresh_stats();
        }
        // ...
    }
}
```

Benefits:
- Clear separation of UI and logic
- Type-safe communication
- Easy to test handlers independently
- Consistent pattern across all panels

### Storage Integration

The app uses `sutra-storage::ConcurrentMemory` directly:

```rust
// Initialization
let config = ConcurrentConfig {
    storage_path: data_dir.clone(),
    memory_threshold: 10_000,
    vector_dimension: 256,
    // ...
};
let storage = ConcurrentMemory::new(config);

// Learning
let concept_id = ConceptId::from_bytes(md5_hash);
storage.learn_concept(concept_id, content.as_bytes().to_vec(), None, 1.0, 1.0)?;

// Searching
let results = storage.text_search(&query, limit);

// Graph operations
let neighbors = storage.query_neighbors(&concept_id);
let weighted = storage.query_neighbors_weighted(&concept_id);

// Pathfinding
let pathfinder = ParallelPathFinder::new(confidence_decay);
let paths = pathfinder.find_paths_parallel(snapshot, from, to, max_depth, max_paths);

// Persistence
storage.flush()?;
```

---

## View Architecture

### Sidebar Navigation

```rust
pub enum SidebarView {
    // MAIN section
    Chat, Knowledge, Search,
    // ANALYSIS section (collapsible)
    Graph, Paths, Timeline, Causal,
    // TOOLS section (collapsible)
    Analytics, Query, Export,
    // Always visible
    Settings,
}
```

The sidebar renders differently based on current selection and provides visual feedback.

### Panel Update Cycle

```rust
impl eframe::App for SutraApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // 1. Initial data load (once)
        if !self.initialized {
            self.handle_knowledge_action(KnowledgeAction::Refresh);
            self.graph_view.load_from_storage(&self.storage);
            self.initialized = true;
        }
        
        // 2. Request repaint for animations
        ctx.request_repaint_after(Duration::from_millis(100));
        
        // 3. Render sidebar
        egui::SidePanel::left("sidebar").show(ctx, |ui| {
            self.sidebar.ui(ui);
        });
        
        // 4. Render status bar
        egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
            self.status_bar.ui(ui);
        });
        
        // 5. Render main content based on current view
        egui::CentralPanel::default().show(ctx, |ui| {
            match self.sidebar.current_view {
                SidebarView::Chat => {
                    if let Some(action) = self.chat.ui(ui) {
                        self.handle_chat_action(action);
                    }
                }
                // ... other views
            }
        });
    }
}
```

---

## Graph Visualization

### Force-Directed Layout

The graph view implements a simple force-directed algorithm:

```rust
impl GraphView {
    fn simulate_step(&mut self) {
        // 1. Repulsion: all nodes push each other away
        for i in 0..nodes.len() {
            for j in (i+1)..nodes.len() {
                let force = self.repulsion / distance_squared;
                // Apply to velocities
            }
        }
        
        // 2. Attraction: connected nodes pull together
        for edge in &self.edges {
            let force = distance * self.attraction * edge.strength;
            // Apply to velocities
        }
        
        // 3. Apply velocities with damping
        for node in &mut self.nodes {
            node.vx *= self.damping;
            node.vy *= self.damping;
            node.x += node.vx;
            node.y += node.vy;
        }
        
        // 4. Stop when movement is minimal
        if total_movement < 0.5 {
            self.simulation_running = false;
        }
    }
}
```

### Camera System

```rust
pub struct Camera {
    pub offset: Vec2,  // Pan offset
    pub zoom: f32,     // Zoom level (0.1 - 5.0)
}

impl Camera {
    pub fn world_to_screen(&self, world: Pos2, rect: Rect) -> Pos2 {
        let center = rect.center();
        Pos2::new(
            center.x + (world.x + self.offset.x) * self.zoom,
            center.y + (world.y + self.offset.y) * self.zoom,
        )
    }
}
```

---

## MPPA Consensus Analysis

The reasoning paths panel implements MPPA-style clustering:

```rust
fn analyze_consensus(&self) -> ConsensusResult {
    // 1. Cluster paths by destination concept
    let mut clusters: HashMap<ConceptId, Vec<ReasoningPath>> = HashMap::new();
    for path in &self.paths {
        let destination = path.path.last().unwrap().concept_id;
        clusters.entry(destination).or_default().push(path.clone());
    }
    
    // 2. Score each cluster
    for cluster in &mut clusters {
        let support_ratio = cluster.paths.len() as f32 / total_paths as f32;
        let avg_confidence = cluster.paths.iter().map(|p| p.confidence).sum() / cluster.len();
        
        // MPPA scoring formula
        let consensus_bonus = if support_ratio >= 0.5 { 1.0 + (support_ratio - 0.5) } else { 1.0 };
        let outlier_penalty = if support_ratio < 0.2 { 0.7 } else { 1.0 };
        cluster.consensus_weight = avg_confidence * support_ratio * consensus_bonus * outlier_penalty;
    }
    
    // 3. Rank by consensus weight
    clusters.sort_by_consensus_weight();
    
    ConsensusResult {
        primary_cluster: clusters[0],
        alternatives: clusters[1..],
        total_paths,
    }
}
```

---

## Export Formats

### JSON (Full Fidelity)

```json
{
  "version": "2.0.0",
  "exported_at": "2025-11-26T14:32:00Z",
  "format": "sutra-desktop",
  "concepts": [
    {
      "id": "a3f2e8c1...",
      "content": "Memory leak in connection pool",
      "confidence": 0.92,
      "strength": 0.88,
      "neighbors": ["b8e4...", "c9f1..."]
    }
  ],
  "edges": [
    {"from": "a3f2...", "to": "b8e4..."}
  ]
}
```

### CSV (Simplified)

```csv
id,content,confidence,strength,neighbor_count
a3f2e8c1,Memory leak in connection pool,0.92,0.88,8
```

### GraphML (Neo4j Compatible)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="content" for="node" attr.name="content" attr.type="string"/>
  <graph id="sutra" edgedefault="directed">
    <node id="a3f2e8c1">
      <data key="content">Memory leak</data>
    </node>
  </graph>
</graphml>
```

### Cypher (Neo4j Import Script)

```cypher
CREATE (c1:Concept {id: 'a3f2e8c1', content: 'Memory leak', confidence: 0.92});
MATCH (a:Concept {id: 'a3f2e8c1'}), (b:Concept {id: 'b8e4f1a2'})
CREATE (a)-[:RELATES_TO]->(b);
```

---

## Performance Optimizations

### Frame Budget

At 60 FPS, each frame has ~16ms budget:
- UI layout: ~2ms
- Storage queries: ~1-5ms (cached)
- Graph rendering: ~3ms (up to 1000 nodes)
- Reserve: ~6ms for spikes

### Memory Management

- **Lazy loading**: Graph nodes loaded on-demand
- **Ring buffers**: Analytics history capped at 1440 entries
- **LOD rendering**: Distant graph nodes simplified
- **Culling**: Only visible elements rendered

### Storage Efficiency

- **WAL batching**: Multiple writes combined
- **HNSW caching**: Vector index memory-mapped
- **Snapshot sharing**: Read-only snapshots avoid locks

---

## Testing

### Unit Tests

```bash
cd desktop
cargo test
```

### Integration Tests

```bash
# Full build and run cycle
cargo build -p sutra-desktop --release
./target/release/sutra-desktop --test-mode
```

### UI Testing

Manual testing checklist:
- [ ] All slash commands work
- [ ] Autocomplete navigation (keyboard and mouse)
- [ ] Graph zoom/pan/select
- [ ] Path finding between concepts
- [ ] Export/import round-trip
- [ ] Graceful shutdown (data persisted)

---

## Future Enhancements

### Planned (v3.4+)

1. **Local Embeddings**: ONNX Runtime for offline vector generation
2. **Multi-Window**: Detachable panels using egui viewports
3. **Themes**: Light mode and custom color schemes
4. **Undo/Redo**: Transaction-based history

### Considered (v4.0+)

1. **Plugin System**: Rust-based extensions
2. **Collaborative**: Multi-user sync with conflict resolution
3. **Mobile**: Touch-optimized UI for tablets
4. **AI Assistant**: Local LLM integration (llama.cpp)

---

## Related Documentation

- [README.md](./README.md) - Overview and quick start
- [BUILDING.md](./BUILDING.md) - Build configuration
- [UI_COMPONENTS.md](./UI_COMPONENTS.md) - Panel reference
- [sutra-storage docs](../storage/) - Storage engine internals
