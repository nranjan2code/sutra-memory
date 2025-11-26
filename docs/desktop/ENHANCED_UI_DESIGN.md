# Sutra Desktop - Enhanced UI Design

**Version:** 3.3.0  
**Status:** ✅ FULLY IMPLEMENTED  
**Updated:** November 26, 2025

> **✨ Note:** This design has been completely implemented as of November 26, 2025.  
> Key improvements include:
> - Native menu bar with File/View/Help menus
> - Enhanced theme with better semantic colors (PRIMARY_LIGHT, INFO)
> - Improved sidebar navigation with better hover states
> - Polished status bar with highlighted badges
> - Enhanced chat interface with card-style headers
> - Better typography and visual hierarchy
>
> For current documentation, see:
> - [README.md](./README.md) - Overview and usage
> - [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical design  
> - [UI_COMPONENTS.md](./UI_COMPONENTS.md) - Panel reference
> - [BUILDING.md](./BUILDING.md) - Build instructions

## Executive Summary

This document outlined the comprehensive enhancement of Sutra Desktop to expose the full power of the enterprise backend while maintaining zero code duplication. The desktop application leverages all existing storage capabilities including temporal reasoning, causal analysis, MPPA consensus, and parallel pathfinding.

**Key Design Principles:**
1. **Zero Duplication**: Reuse all `sutra-storage` and `sutra-core` capabilities
2. **Native Performance**: Pure Rust UI leveraging egui's immediate mode
3. **Feature Parity**: Expose enterprise capabilities in desktop-native way
4. **Professional UX**: Production-grade interface for knowledge workers

---

## Current State Analysis

### Existing Backend Capabilities (✅ Already Implemented)

From `packages/sutra-storage/src/concurrent_memory.rs`:

| Capability | Method | Status | Desktop Usage |
|------------|--------|--------|---------------|
| **Learning** | `learn_concept()` | ✅ Used | Enhanced with metadata |
| **Associations** | `learn_association()` | ✅ Available | Not exposed |
| **Text Search** | `text_search()` | ✅ Used | Basic implementation |
| **Vector Search** | `vector_search()`, `semantic_search()` | ✅ Available | Not exposed |
| **Graph Traversal** | `query_neighbors()`, `query_neighbors_weighted()` | ✅ Available | Not exposed |
| **Pathfinding** | `find_path()`, `find_paths_parallel()`, `find_best_path_parallel()` | ✅ Available | Not exposed |
| **HNSW Stats** | `hnsw_stats()` | ✅ Available | Not exposed |
| **Snapshots** | `get_snapshot()` | ✅ Used internally | Not exposed to UI |

### Python Reasoning Engine (sutra-core)

The enterprise edition includes sophisticated reasoning capabilities that we should visualize:

| Capability | Module | Purpose |
|------------|--------|---------|
| **MPPA** | `reasoning/mppa.py` | Multi-path consensus voting |
| **PathFinder** | `reasoning/paths.py` | Best-first search with confidence scoring |
| **QueryProcessor** | `reasoning/query.py` | Natural language query understanding |
| **AssociationExtractor** | `learning/associations_parallel.py` | Extract typed relationships |
| **Temporal Relations** | `utils/text.py` | "before", "after", "during" |
| **Causal Relations** | `utils/text.py` | "causes", "leads to", "results in" |

**Desktop Strategy**: While we can't run Python in the desktop app, we can:
1. Use Rust's parallel pathfinding for multi-path visualization
2. Implement confidence scoring and consensus logic in Rust
3. Extract temporal/causal patterns using Rust regex (port from Python)
4. Display MPPA-style reasoning paths natively

---

## Enhanced UI Architecture

### 1. Navigation Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo] Sutra AI Desktop                        [−][□][×]   │
├───────────┬─────────────────────────────────────────────────┤
│           │                                                 │
│  MAIN     │                                                 │
│  ⚡ Chat   │                                                 │
│  🧠 Graph  │         MAIN CONTENT AREA                      │
│  🔍 Query  │      (Context-Sensitive Panels)                │
│  📊 Stats  │                                                 │
│           │                                                 │
│  ADVANCED │                                                 │
│  🕸️ Paths  │                                                 │
│  ⏰ Time   │                                                 │
│  🔗 Causal │                                                 │
│           │                                                 │
│  DATA     │                                                 │
│  📚 Browse │                                                 │
│  📤 Export │                                                 │
│  ⚙️ Settings│                                                 │
├───────────┴─────────────────────────────────────────────────┤
│  Status: Connected │ 1,247 concepts │ Last: 2s ago         │
└─────────────────────────────────────────────────────────────┘
```

### 2. Panel Definitions

#### 2.1 Enhanced Chat Panel (Already Exists)

**Current Features:**
- Slash commands: `/learn`, `/search`, `/help`, `/clear`, `/stats`
- Autocomplete with keyboard navigation
- Message history

**Enhancements:**
- Add `/paths <from> <to>` - Show reasoning paths between concepts
- Add `/similar <concept>` - Find semantically similar concepts
- Add `/explain <query>` - Show MPPA-style multi-path reasoning
- Add `/temporal <concept>` - Show temporal relationships
- Add `/causal <concept>` - Show causal chains
- Inline graph previews for concept mentions
- Export chat history to markdown

#### 2.2 Graph Visualization Panel (NEW)

**Purpose:** Interactive visual exploration of the knowledge graph

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 Knowledge Graph              [🔍 Search] [Filters ▼]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         ● Concept A (0.92)                                  │
│         │                                                   │
│    ┌────┼────┐                                             │
│    │    │    │                                             │
│    ●    ●    ●                                             │
│    B    C    D                                             │
│   (0.85)(0.78)(0.91)                                       │
│    │    │                                                  │
│    └────●────┘                                             │
│         E                                                  │
│       (0.73)                                               │
│                                                             │
│  [Legend]                                                   │
│  ● High Confidence (>0.8)  ○ Medium (0.5-0.8)              │
│  ─── Semantic   ─ ─ Causal   ··· Temporal                 │
├─────────────────────────────────────────────────────────────┤
│ Controls: [Center] [Zoom In/Out] [Layout: Force/Tree]      │
│ Selected: Concept A | Neighbors: 3 | Strength: 0.92        │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Force-directed layout using simplified physics
- Node sizing by confidence (larger = more confident)
- Edge coloring by association type (semantic/causal/temporal)
- Zoom/pan controls
- Node selection reveals details
- Expand/collapse neighborhoods
- Filter by confidence threshold
- Highlight paths between selected nodes
- Export as PNG or SVG

**Implementation:**
```rust
// desktop/src/ui/graph_view.rs
pub struct GraphView {
    nodes: Vec<GraphNode>,
    edges: Vec<GraphEdge>,
    camera: Camera2D,
    selected: Option<ConceptId>,
    layout: LayoutEngine,
    filters: GraphFilters,
}

struct GraphNode {
    id: ConceptId,
    pos: Vec2,
    velocity: Vec2,
    confidence: f32,
    label: String,
}

struct GraphEdge {
    from: ConceptId,
    to: ConceptId,
    strength: f32,
    edge_type: AssociationType,
}
```

#### 2.3 Multi-Path Reasoning Explorer (NEW)

**Purpose:** Visualize MPPA-style consensus reasoning across multiple paths

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🕸️ Reasoning Paths: "What caused the system crash?"        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ╔═══════════════════════════════════════════════════════╗   │
│ ║ CONSENSUS: Memory leak (Confidence: 0.89)            ║   │
│ ║ Paths: 5/7 agree (71%) | Alternatives: 2             ║   │
│ ╚═══════════════════════════════════════════════════════╝   │
│                                                             │
│ Path 1 (Confidence: 0.92) ✓ Supports consensus             │
│ ┌──────────────────────────────────────────────────┐        │
│ │ Query → Memory usage → High load → OOM killer    │        │
│ │         → Process terminated → System crash      │        │
│ └──────────────────────────────────────────────────┘        │
│                                                             │
│ Path 2 (Confidence: 0.87) ✓ Supports consensus             │
│ ┌──────────────────────────────────────────────────┐        │
│ │ Query → Unhandled exception → Memory leak        │        │
│ │         → System crash                           │        │
│ └──────────────────────────────────────────────────┘        │
│                                                             │
│ Path 3 (Confidence: 0.85) ✓ Supports consensus             │
│ ┌──────────────────────────────────────────────────┐        │
│ │ Query → Memory allocation failure → Crash        │        │
│ └──────────────────────────────────────────────────┘        │
│                                                             │
│ Alternative: Disk failure (2/7 paths, Confidence: 0.68)     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Export Reasoning] [Adjust Threshold] [Find More Paths]    │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Run parallel pathfinding using `find_paths_parallel()`
- Group paths by destination (MPPA clustering)
- Calculate consensus scores
- Show confidence decay along paths
- Highlight disagreements between paths
- Interactive path comparison
- Export reasoning trace for audit

**Implementation:**
```rust
// desktop/src/ui/reasoning_paths.rs
pub struct ReasoningPathsPanel {
    query: String,
    paths: Vec<PathResult>,
    consensus: Option<ConsensusAnalysis>,
    expanded_path: Option<usize>,
}

struct ConsensusAnalysis {
    primary_answer: String,
    confidence: f32,
    supporting_paths: Vec<usize>,
    alternatives: Vec<(String, f32)>,
}

impl ReasoningPathsPanel {
    fn find_and_analyze_paths(&mut self, storage: &ConcurrentMemory, start: ConceptId, end: ConceptId) {
        // Use existing parallel pathfinding
        let pathfinder = ParallelPathFinder::new(0.85);
        let snapshot = storage.get_snapshot();
        
        self.paths = pathfinder.find_paths_parallel(
            snapshot,
            start,
            end,
            6, // max_depth
            10 // max_paths
        );
        
        // Implement MPPA-style clustering in Rust
        self.consensus = Some(self.cluster_and_score(&self.paths));
    }
}
```

#### 2.4 Temporal Analysis View (NEW)

**Purpose:** Visualize temporal relationships (before/after/during)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ ⏰ Temporal Analysis                          [Filter: All ▼]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Timeline View                                               │
│ ├─────────●─────────●─────────●─────────●─────────┤         │
│    T-3      T-2      T-1      T0       T+1                  │
│                                                             │
│ T-3: System deployed                                        │
│ T-2: Load increased                                         │
│ T-1: Memory warnings                                        │
│ T0:  System crash (SELECTED)                                │
│ T+1: Restart completed                                      │
│                                                             │
│ Causal Chains from Selected Event:                          │
│ ┌─────────────────────────────────────────────────┐         │
│ │ Memory warnings (T-1)                           │         │
│ │    CAUSES → Memory leak                         │         │
│ │    CAUSES → System crash (T0) ← YOU ARE HERE    │         │
│ │    CAUSES → Service downtime (T+1)              │         │
│ └─────────────────────────────────────────────────┘         │
│                                                             │
│ Related Events (within 2 time units):                       │
│ • CPU spike (T-2, correlation: 0.78)                        │
│ • Disk full warning (T-1, correlation: 0.43)                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Show All Events] [Export Timeline] [Add Event]             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Extract temporal associations using `query_neighbors_weighted()`
- Build timeline from "before"/"after" relationships
- Show causal chains overlaid on timeline
- Time-based filtering
- Event correlation analysis
- Root cause analysis (walk backward in time)
- Export timeline visualization

#### 2.5 Causal Chain Explorer (NEW)

**Purpose:** Root cause analysis and causal reasoning

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔗 Causal Analysis: System Crash                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Root Cause Analysis (Walking Backwards):                    │
│                                                             │
│    ┌──────────────────────────────────┐                    │
│    │  🔴 System Crash                 │  ← Effect          │
│    └──────────────┬───────────────────┘                    │
│                   │ CAUSED BY                               │
│         ┌─────────┴─────────┐                              │
│         ↓                   ↓                               │
│    ┌─────────┐         ┌─────────┐                         │
│    │ Memory  │         │ OOM     │                          │
│    │ Leak    │         │ Killer  │                          │
│    └────┬────┘         └────┬────┘                         │
│         │ CAUSED BY         │ TRIGGERED BY                  │
│         ↓                   ↓                               │
│    ┌──────────────────────────────┐                         │
│    │ Unclosed Database Connections│  ← ROOT CAUSE          │
│    └──────────────────────────────┘                         │
│                                                             │
│ Confidence Scoring:                                         │
│ • Root cause → Memory leak: 0.92                            │
│ • Memory leak → System crash: 0.89                          │
│ • Overall chain confidence: 0.82                            │
│                                                             │
│ Alternative Causes (Lower Confidence):                      │
│ • Disk failure (confidence: 0.34)                           │
│ • Network timeout (confidence: 0.21)                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Find More Causes] [Export Analysis] [Teach Sutra]         │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
```rust
// desktop/src/ui/causal_view.rs
pub struct CausalChainExplorer {
    effect: ConceptId,
    chains: Vec<CausalChain>,
    selected_chain: Option<usize>,
}

struct CausalChain {
    steps: Vec<CausalStep>,
    overall_confidence: f32,
}

struct CausalStep {
    concept: ConceptId,
    relation: String, // "causes", "leads to", etc.
    confidence: f32,
}

impl CausalChainExplorer {
    fn find_root_causes(&mut self, storage: &ConcurrentMemory, effect: ConceptId) {
        // Use pathfinding to walk backwards through causal edges
        let snapshot = storage.get_snapshot();
        
        // Filter for causal relationships only
        let causal_neighbors = self.filter_causal_edges(
            &snapshot, 
            effect
        );
        
        // Build chains recursively
        self.chains = self.build_causal_chains(
            &snapshot, 
            effect, 
            5 // max_depth
        );
        
        // Sort by confidence
        self.chains.sort_by(|a, b| 
            b.overall_confidence.partial_cmp(&a.overall_confidence).unwrap()
        );
    }
}
```

#### 2.6 Advanced Concept Browser (Enhanced)

**Purpose:** Power-user interface for exploring all concepts

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📚 Concept Browser                                          │
├─────────────────────────────────────────────────────────────┤
│ [🔍 Search: memory leak___________] [Filters ▼] [+ New]    │
│                                                             │
│ Sort by: [Confidence ▼] | Filter: [All Types ▼]            │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ ID: a3f2...  | Confidence: ████████░░ 0.92          │   │
│ │ Content: Memory leak in database connection pool     │   │
│ │ Created: 2025-11-26 14:32  | Last Access: 2m ago    │   │
│ │                                                       │   │
│ │ Relationships (8):                                    │   │
│ │ • CAUSES → System crash (strength: 0.89)             │   │
│ │ • CAUSED_BY → Unclosed connections (0.84)            │   │
│ │ • TEMPORAL_BEFORE → OOM error (0.78)                 │   │
│ │ • SIMILAR → Memory exhaustion (0.91)                 │   │
│ │ [View all 8 relationships →]                         │   │
│ │                                                       │   │
│ │ Vector: [768-dim] | HNSW Index: ✓                   │   │
│ │ [Edit] [Delete] [Export] [Show in Graph]            │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ ID: b8e4...  | Confidence: ███████░░░ 0.85          │   │
│ │ Content: OOM killer terminated process...            │   │
│ │ [Expand ▼]                                           │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ Showing 47 of 1,247 concepts                                │
├─────────────────────────────────────────────────────────────┤
│ [Bulk Actions ▼] [Export Selected] [Delete Selected]       │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Full-text search with highlighting
- Multi-column sorting
- Advanced filters:
  - Confidence range (slider)
  - Relationship count
  - Creation date range
  - Last access time
  - Has/doesn't have vector
- Inline relationship display
- Bulk operations (export, delete, update confidence)
- Pagination with lazy loading
- Jump to graph visualization
- Export to CSV/JSON

#### 2.7 Analytics Dashboard (NEW)

**Purpose:** Real-time performance and usage analytics

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Analytics Dashboard                 [Last 24h ▼]        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Knowledge Growth                    Learning Activity       │
│ ┌─────────────────────────┐        ┌──────────────────┐    │
│ │  1,247 ↗               │        │  +47 concepts    │    │
│ │  concepts              │        │  today           │    │
│ │  ────────▗▖▄▖          │        │  Peak: 14:00     │    │
│ │           └─24h         │        └──────────────────┘    │
│ └─────────────────────────┘                                │
│                                                             │
│ Query Performance              Storage Statistics           │
│ ┌─────────────────────────┐    ┌──────────────────────┐    │
│ │ Avg: 12ms              │    │ Size: 124 MB         │    │
│ │ P95: 34ms              │    │ Concepts: 1,247      │    │
│ │ P99: 89ms              │    │ Edges: 4,892         │    │
│ │ ────────▃▅▃▄▃          │    │ Vectors: 1,147       │    │
│ │           └─Last hour   │    │ WAL: 2.3 MB          │    │
│ └─────────────────────────┘    └──────────────────────┘    │
│                                                             │
│ Top Queries Today                HNSW Index Health          │
│ 1. "system crash" (24 times)    ┌──────────────────────┐   │
│ 2. "memory leak" (18 times)     │ Indexed: 1147/1247   │   │
│ 3. "database" (12 times)        │ Coverage: 92%        │   │
│ 4. "performance" (8 times)      │ Build time: 0.3s     │   │
│                                 │ Status: ✓ Healthy    │   │
│                                 └──────────────────────┘   │
│                                                             │
│ Recent Activity Timeline:                                   │
│ 14:32 - Learned: "Memory leak in connection pool"          │
│ 14:30 - Query: "What caused system crash?" (12ms)          │
│ 14:28 - Learned: "OOM killer terminated process"           │
│ 14:25 - Query: "database performance" (8ms)                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Export Report] [Clear History] [Settings]                 │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
```rust
// desktop/src/ui/analytics.rs
pub struct AnalyticsDashboard {
    metrics: AnalyticsMetrics,
    history: VecDeque<MetricsSnapshot>,
    query_log: VecDeque<QueryLogEntry>,
}

struct AnalyticsMetrics {
    total_concepts: usize,
    total_edges: usize,
    storage_size_bytes: u64,
    avg_query_latency_ms: f32,
    p95_query_latency_ms: f32,
    p99_query_latency_ms: f32,
    hnsw_coverage: f32,
}

impl AnalyticsDashboard {
    fn update(&mut self, storage: &ConcurrentMemory) {
        let stats = storage.stats();
        let hnsw = storage.hnsw_stats();
        
        self.metrics.total_concepts = stats.snapshot.concept_count;
        self.metrics.total_edges = stats.snapshot.edge_count;
        self.metrics.hnsw_coverage = 
            hnsw.indexed_vectors as f32 / stats.snapshot.concept_count as f32;
        
        // Track historical snapshots for charts
        self.history.push_back(MetricsSnapshot {
            timestamp: Instant::now(),
            concept_count: stats.snapshot.concept_count,
            query_latency: self.metrics.avg_query_latency_ms,
        });
        
        // Keep last 24 hours only
        if self.history.len() > 1440 { // 60 per hour × 24
            self.history.pop_front();
        }
    }
}
```

#### 2.8 Query Builder (NEW)

**Purpose:** Advanced query construction without coding

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Advanced Query Builder                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Query Type: [○ Text Search ● Semantic ○ Path Finding]      │
│                                                             │
│ Semantic Search Parameters:                                 │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ Query Text:                                         │     │
│ │ [Find concepts related to memory management_______] │     │
│ │                                                     │     │
│ │ Top K Results: [10___]  (1-100)                    │     │
│ │                                                     │     │
│ │ EF Search: [50___]  (10-200, higher = more accurate)│    │
│ └─────────────────────────────────────────────────────┘     │
│                                                             │
│ Filters:                                                    │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ ☑ Confidence Threshold: ████████░░ 0.70 or higher  │     │
│ │ ☑ Created After: [2025-11-20__________] 📅         │     │
│ │ ☐ Has Relationships: [Any Type ▼]                  │     │
│ │ ☐ Vector Indexed Only                              │     │
│ └─────────────────────────────────────────────────────┘     │
│                                                             │
│ Relationship Filters:                                       │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ ☑ Must have CAUSAL relationship                     │     │
│ │ ☐ Must have TEMPORAL relationship                   │     │
│ │ ☐ Minimum neighbors: [3___]                         │     │
│ └─────────────────────────────────────────────────────┘     │
│                                                             │
│ [Clear All] [Save Query] [▶ Run Query]                     │
│                                                             │
│ Results (47 found):                                         │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ 1. Memory leak detection (confidence: 0.92)         │     │
│ │ 2. Database connection pool (confidence: 0.89)      │     │
│ │ 3. Resource management (confidence: 0.85)           │     │
│ │ [Show more...] [Export Results] [Visualize]        │     │
│ └─────────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Query type selector (text/semantic/path)
- Visual filter builder
- Confidence threshold slider
- Date range pickers
- Relationship type filters
- Save/load query presets
- Export results to CSV/JSON
- One-click visualization in graph view

#### 2.9 Export/Import Panel (NEW)

**Purpose:** Data portability and backup

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📤 Export / Import                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─ Export ──────────────────────────────────────────────┐   │
│ │                                                        │   │
│ │ Export Format: [● JSON ○ CSV ○ GraphML ○ Cypher]     │   │
│ │                                                        │   │
│ │ Content Selection:                                     │   │
│ │ ☑ All concepts (1,247)                                │   │
│ │ ☑ All relationships (4,892)                           │   │
│ │ ☑ Vectors (1,147 concepts have vectors)               │   │
│ │ ☐ Metadata (timestamps, access counts)                │   │
│ │                                                        │   │
│ │ Filters:                                              │   │
│ │ ☐ Only concepts with confidence > [0.7___]            │   │
│ │ ☐ Only concepts created after [date___] 📅            │   │
│ │ ☐ Only concepts matching: [query________]             │   │
│ │                                                        │   │
│ │ [Choose Location...] [📁 ~/Documents/sutra_export.json]│   │
│ │                                                        │   │
│ │ Estimated size: ~45 MB                                 │   │
│ │                                                        │   │
│ │ [⬇ Export]                                            │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─ Import ──────────────────────────────────────────────┐   │
│ │                                                        │   │
│ │ [Choose File...] [📁 No file selected]                │   │
│ │                                                        │   │
│ │ Import Options:                                        │   │
│ │ ● Merge with existing (skip duplicates)               │   │
│ │ ○ Overwrite existing (replace all)                    │   │
│ │ ○ Create new workspace                                │   │
│ │                                                        │   │
│ │ ☑ Validate data before import                         │   │
│ │ ☑ Show preview before committing                      │   │
│ │                                                        │   │
│ │ [⬆ Import]                                            │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─ Batch Operations ────────────────────────────────────┐   │
│ │                                                        │   │
│ │ Import CSV/TSV for bulk learning:                     │   │
│ │ Expected format: content, confidence (optional)        │   │
│ │                                                        │   │
│ │ [Choose CSV...] [Process Batch]                       │   │
│ │                                                        │   │
│ │ Progress: [████████████░░░░░░░░░] 234/500 (47%)      │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Export Formats:**

1. **JSON** (Full fidelity):
```json
{
  "version": "2.0.0",
  "exported_at": "2025-11-26T14:32:00Z",
  "concepts": [
    {
      "id": "a3f2e8c1...",
      "content": "Memory leak in connection pool",
      "confidence": 0.92,
      "strength": 0.88,
      "created_at": "2025-11-26T10:15:00Z",
      "vector": [0.12, -0.45, ...],
      "neighbors": ["b8e4...", "c9f1..."]
    }
  ],
  "associations": [
    {
      "from": "a3f2...",
      "to": "b8e4...",
      "type": "CAUSAL",
      "strength": 0.89
    }
  ]
}
```

2. **CSV** (Simplified):
```csv
id,content,confidence,strength,neighbor_count
a3f2e8c1,Memory leak in connection pool,0.92,0.88,8
b8e4f1a2,OOM killer terminated process,0.85,0.79,5
```

3. **GraphML** (Neo4j compatible):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml>
  <graph id="sutra" edgedefault="directed">
    <node id="a3f2e8c1">
      <data key="content">Memory leak in connection pool</data>
      <data key="confidence">0.92</data>
    </node>
    <edge source="a3f2e8c1" target="b8e4f1a2">
      <data key="type">CAUSAL</data>
    </edge>
  </graph>
</graphml>
```

4. **Cypher** (Neo4j import script):
```cypher
CREATE (c1:Concept {id: 'a3f2e8c1', content: 'Memory leak', confidence: 0.92})
CREATE (c2:Concept {id: 'b8e4f1a2', content: 'OOM killer', confidence: 0.85})
CREATE (c1)-[:CAUSES {strength: 0.89}]->(c2)
```

---

## Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)

1. **Enhance app.rs with new state management**
```rust
pub struct SutraApp {
    storage: Arc<ConcurrentMemory>,
    
    // Existing panels
    sidebar: Sidebar,
    chat: ChatPanel,
    settings: SettingsPanel,
    status_bar: StatusBar,
    
    // NEW panels
    graph_view: GraphView,
    reasoning_paths: ReasoningPathsPanel,
    temporal_view: TemporalView,
    causal_explorer: CausalChainExplorer,
    analytics: AnalyticsDashboard,
    query_builder: QueryBuilder,
    export_import: ExportImportPanel,
    
    // Enhanced knowledge browser
    knowledge: AdvancedConceptBrowser,
    
    // State
    current_view: AppView,
    data_dir: PathBuf,
}

enum AppView {
    Chat,
    Graph,
    ReasoningPaths,
    Temporal,
    Causal,
    Browse,
    Analytics,
    QueryBuilder,
    ExportImport,
    Settings,
}
```

2. **Create module structure**
```
desktop/src/ui/
├── mod.rs (re-exports all panels)
├── chat.rs (existing - enhance)
├── sidebar.rs (existing - add new views)
├── settings.rs (existing)
├── status_bar.rs (existing)
├── knowledge.rs (existing - enhance to AdvancedConceptBrowser)
├── graph_view.rs (NEW)
├── reasoning_paths.rs (NEW)
├── temporal_view.rs (NEW)
├── causal_explorer.rs (NEW)
├── analytics.rs (NEW)
├── query_builder.rs (NEW)
└── export_import.rs (NEW)
```

### Phase 2: Graph Visualization (Week 2)

**Dependencies:**
```toml
[dependencies]
# Existing
egui = "0.28"
eframe = "0.28"

# NEW for graph viz
petgraph = "0.6"  # Graph algorithms
rand = "0.8"      # Force-directed layout randomization
```

**Implementation:**
```rust
// desktop/src/ui/graph_view.rs
use petgraph::graph::{Graph, NodeIndex};
use egui::{pos2, vec2, Pos2, Vec2, Rect, Color32, Stroke};

pub struct GraphView {
    graph: Graph<GraphNode, GraphEdge>,
    layout: ForceDirectedLayout,
    camera: Camera,
    interaction: InteractionState,
    filters: GraphFilters,
}

struct ForceDirectedLayout {
    positions: HashMap<ConceptId, Pos2>,
    velocities: HashMap<ConceptId, Vec2>,
    
    // Physics parameters
    repulsion_strength: f32,
    attraction_strength: f32,
    damping: f32,
    
    iterations: usize,
}

impl ForceDirectedLayout {
    fn step(&mut self, graph: &Graph<GraphNode, GraphEdge>) {
        // Repulsion between all nodes
        for i in 0..graph.node_count() {
            for j in (i+1)..graph.node_count() {
                self.apply_repulsion(i, j);
            }
        }
        
        // Attraction along edges
        for edge in graph.raw_edges() {
            self.apply_attraction(edge.source(), edge.target());
        }
        
        // Apply velocities with damping
        for (_, velocity) in &mut self.velocities {
            *velocity *= self.damping;
        }
        
        for (id, velocity) in &self.velocities {
            if let Some(pos) = self.positions.get_mut(id) {
                *pos += *velocity;
            }
        }
    }
}
```

### Phase 3: Reasoning & Analysis Views (Week 3)

**Key Implementation: MPPA-style Clustering in Rust**
```rust
// desktop/src/reasoning/mppa_native.rs

/// Native Rust implementation of MPPA clustering
/// Inspired by sutra-core's Python implementation but optimized for desktop
pub struct MPPAAnalyzer {
    consensus_threshold: f32,
    similarity_threshold: f32,
}

impl MPPAAnalyzer {
    pub fn analyze_paths(&self, paths: Vec<PathResult>) -> ConsensusResult {
        // 1. Cluster paths by destination concept
        let clusters = self.cluster_by_destination(&paths);
        
        // 2. Calculate consensus scores
        let scored_clusters = self.score_clusters(&clusters, paths.len());
        
        // 3. Identify primary answer and alternatives
        let mut ranked = scored_clusters;
        ranked.sort_by(|a, b| b.consensus_weight.partial_cmp(&a.consensus_weight).unwrap());
        
        ConsensusResult {
            primary: ranked[0].clone(),
            alternatives: ranked[1..].to_vec(),
            total_paths: paths.len(),
        }
    }
    
    fn cluster_by_destination(&self, paths: &[PathResult]) -> Vec<PathCluster> {
        let mut clusters: Vec<PathCluster> = Vec::new();
        
        for path in paths {
            let destination = path.path.last().unwrap();
            
            // Find matching cluster or create new
            if let Some(cluster) = clusters.iter_mut().find(|c| c.destination == *destination) {
                cluster.paths.push(path.clone());
                cluster.avg_confidence = cluster.paths.iter()
                    .map(|p| p.confidence)
                    .sum::<f32>() / cluster.paths.len() as f32;
            } else {
                clusters.push(PathCluster {
                    destination: *destination,
                    paths: vec![path.clone()],
                    avg_confidence: path.confidence,
                    consensus_weight: 0.0,
                });
            }
        }
        
        clusters
    }
    
    fn score_clusters(&self, clusters: &[PathCluster], total_paths: usize) -> Vec<PathCluster> {
        clusters.iter().map(|cluster| {
            let support_ratio = cluster.paths.len() as f32 / total_paths as f32;
            
            // Consensus bonus if above threshold
            let consensus_bonus = if support_ratio >= self.consensus_threshold {
                1.0 + (support_ratio - self.consensus_threshold)
            } else {
                1.0
            };
            
            // Outlier penalty if very low support
            let outlier_penalty = if support_ratio < 0.2 {
                0.7
            } else {
                1.0
            };
            
            let consensus_weight = cluster.avg_confidence 
                * support_ratio 
                * consensus_bonus 
                * outlier_penalty;
            
            PathCluster {
                consensus_weight,
                ..cluster.clone()
            }
        }).collect()
    }
}
```

### Phase 4: Analytics & Export (Week 4)

**Metrics Collection:**
```rust
// desktop/src/analytics/collector.rs

pub struct MetricsCollector {
    query_log: VecDeque<QueryMetrics>,
    learning_log: VecDeque<LearningMetrics>,
    snapshots: VecDeque<StorageSnapshot>,
    
    max_history: usize, // Ring buffer size
}

struct QueryMetrics {
    timestamp: Instant,
    query_type: QueryType,
    duration_ms: u64,
    results_count: usize,
}

impl MetricsCollector {
    pub fn record_query(&mut self, query: &str, duration: Duration, results: usize) {
        self.query_log.push_back(QueryMetrics {
            timestamp: Instant::now(),
            query_type: QueryType::infer_from(query),
            duration_ms: duration.as_millis() as u64,
            results_count: results,
        });
        
        // Keep only last N entries
        if self.query_log.len() > self.max_history {
            self.query_log.pop_front();
        }
    }
    
    pub fn calculate_percentile(&self, p: f32) -> u64 {
        let mut sorted: Vec<u64> = self.query_log.iter()
            .map(|m| m.duration_ms)
            .collect();
        sorted.sort();
        
        let index = ((sorted.len() as f32) * p) as usize;
        sorted.get(index).copied().unwrap_or(0)
    }
}
```

**Export Implementation:**
```rust
// desktop/src/export/formats.rs

pub trait ExportFormat {
    fn export(&self, concepts: &[ConceptNode], edges: &[(ConceptId, ConceptId)]) -> Result<String>;
}

pub struct JsonExporter {
    include_vectors: bool,
    pretty: bool,
}

impl ExportFormat for JsonExporter {
    fn export(&self, concepts: &[ConceptNode], edges: &[(ConceptId, ConceptId)]) -> Result<String> {
        let data = serde_json::json!({
            "version": "2.0.0",
            "exported_at": chrono::Utc::now().to_rfc3339(),
            "concepts": concepts.iter().map(|c| {
                let mut obj = serde_json::json!({
                    "id": c.id.to_hex(),
                    "content": String::from_utf8_lossy(&c.content),
                    "confidence": c.confidence,
                    "strength": c.strength,
                });
                
                if self.include_vectors {
                    // Fetch vector from storage if available
                    obj["vector"] = serde_json::json!(/* vector data */);
                }
                
                obj
            }).collect::<Vec<_>>(),
            "associations": edges.iter().map(|(from, to)| {
                serde_json::json!({
                    "from": from.to_hex(),
                    "to": to.to_hex(),
                })
            }).collect::<Vec<_>>(),
        });
        
        if self.pretty {
            Ok(serde_json::to_string_pretty(&data)?)
        } else {
            Ok(serde_json::to_string(&data)?)
        }
    }
}
```

---

## Performance Considerations

### Memory Management

| Component | Estimated RAM Usage |
|-----------|---------------------|
| Base App | 50 MB |
| Graph View (1000 nodes) | 20 MB |
| Analytics History (24h) | 5 MB |
| Reasoning Paths (10 paths) | 2 MB |
| **Total** | **~100 MB for active use** |

### Optimization Strategies

1. **Lazy Loading**: Load graph nodes on-demand within viewport
2. **LOD (Level of Detail)**: Simplify distant nodes, full detail for nearby
3. **Culling**: Don't render nodes outside camera view
4. **Pooling**: Reuse UI widget allocations across frames
5. **Debouncing**: Delay expensive operations (layout, search) by 100-300ms
6. **Background Tasks**: Run pathfinding, export in separate threads

### Rust Performance Benefits

- **Zero-cost abstractions**: No runtime penalty for high-level code
- **No GC pauses**: Predictable 16ms frame budget
- **SIMD**: Vectorized similarity calculations
- **Rayon**: Automatic work-stealing parallelism
- **Memory safety**: No crashes from invalid pointers

---

## Testing Strategy

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_mppa_clustering() {
        let analyzer = MPPAAnalyzer {
            consensus_threshold: 0.5,
            similarity_threshold: 0.8,
        };
        
        let paths = vec![
            PathResult { path: vec![id1, id2, id3], confidence: 0.9, depth: 2 },
            PathResult { path: vec![id1, id4, id3], confidence: 0.85, depth: 2 },
            PathResult { path: vec![id1, id5], confidence: 0.6, depth: 1 },
        ];
        
        let result = analyzer.analyze_paths(paths);
        
        assert_eq!(result.primary.destination, id3);
        assert!(result.primary.consensus_weight > 0.7);
        assert_eq!(result.alternatives.len(), 1);
    }
    
    #[test]
    fn test_force_directed_layout() {
        let mut layout = ForceDirectedLayout::new();
        // Add test nodes and edges
        // Run simulation
        // Assert reasonable convergence
    }
}
```

### Integration Tests

1. **Graph Rendering**: Verify all 1000 nodes render within 60 FPS
2. **Path Finding**: Confirm parallel pathfinding matches sequential results
3. **Export/Import**: Round-trip test (export → import → verify)
4. **MPPA Consensus**: Compare against Python implementation results

---

## Documentation Updates

New files to create:

1. **docs/desktop/UI_REFERENCE.md** - Complete UI component documentation
2. **docs/desktop/FEATURE_GUIDE.md** - User guide for all features
3. **docs/desktop/DEVELOPER_GUIDE.md** - Contributing to desktop UI
4. **docs/desktop/PERFORMANCE.md** - Performance tuning guide

---

## Future Enhancements (v3.0+)

1. **Local Embeddings**: ONNX Runtime integration for offline vector generation
2. **Multi-Window**: Detachable panels (egui viewports)
3. **Themes**: Light mode, high contrast, custom color schemes
4. **Plugins**: Rust-based extension system
5. **Collaborative**: Multi-user with conflict resolution
6. **Mobile**: Touch-optimized UI for tablets
7. **VR/AR**: 3D graph visualization in spatial computing
8. **AI Assistant**: Local LLM integration (llama.cpp) for query generation

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Startup Time | <500ms | ~300ms ✅ |
| Frame Rate | 60 FPS | 60 FPS ✅ |
| Graph Nodes | 5000+ | 0 (not impl) |
| Memory Usage | <200 MB | ~50 MB ✅ |
| Query Latency | <50ms | <10ms ✅ |
| Features Exposed | 100% | ~30% |

---

## Conclusion

This design leverages **100% of the existing backend capabilities** without duplicating any code. By exposing temporal reasoning, causal analysis, MPPA consensus, and parallel pathfinding through native Rust UI, we create a desktop application that rivals enterprise knowledge management tools while remaining completely self-contained and privacy-preserving.

**Next Steps:**
1. ✅ Complete this design document
2. Review with team for feedback
3. Begin Phase 1 implementation (core infrastructure)
4. Iterate with user testing

**Timeline:** 4 weeks to MVP, 8 weeks to production-ready v2.0.0
