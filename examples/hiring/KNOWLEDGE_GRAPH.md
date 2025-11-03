# Hiring Knowledge Graph: Structure & Relationships

**Last Updated:** November 3, 2025

This document explains how hiring data maps to Sutra's knowledge graph structure, showing entities, relationships, and semantic types.

---

## Graph Structure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIRING KNOWLEDGE GRAPH                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │  CANDIDATES  │◄───────►│     JOBS     │                     │
│  │  (Entities)  │  match  │  (Entities)  │                     │
│  └──────┬───────┘         └──────┬───────┘                     │
│         │                         │                              │
│         │ has                     │ requires                     │
│         ▼                         ▼                              │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │    SKILLS    │         │ REQUIREMENTS │                     │
│  │  (Entities)  │         │   (Rules)    │                     │
│  └──────┬───────┘         └──────────────┘                     │
│         │                                                        │
│         │ acquired                                               │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │  TIMELINE    │                                               │
│  │  (Temporal)  │                                               │
│  └──────┬───────┘                                               │
│         │                                                        │
│         │ during                                                 │
│         ▼                                                        │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │  EXPERIENCE  │────────►│  OUTCOMES    │                     │
│  │   (Events)   │ caused  │  (Causal)    │                     │
│  └──────────────┘         └──────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entity Types

### 1. Candidate (Entity)
**Example Concepts:**
```
"Sarah Chen is a Senior Backend Engineer"
"Sarah Chen has 6 years Go programming experience"
"Sarah Chen prefers hybrid work arrangement"
```

**Semantic Classification:**
- Type: Entity
- Domain: Business
- Attributes: Name, title, preferences

**Graph Connections:**
- → Skills (has)
- → Experience (accumulated)
- → Jobs (applied_to, hired_for)
- → Timeline (temporal_bounds)

---

### 2. Skills (Entity + Definitional)
**Example Concepts:**
```
"Go is a programming language" (Definitional)
"Kubernetes is a container orchestration platform" (Definitional)
"Sarah Chen has 6 years Go experience" (Entity + Quantitative)
```

**Semantic Classification:**
- Type: Entity + Definitional
- Domain: Technical
- Relationships: is_a, used_for, requires

**Graph Connections:**
- ← Candidates (has_skill)
- → Technologies (is_a, part_of)
- → Projects (used_in)

---

### 3. Experience (Event + Temporal)
**Example Concepts:**
```
"Sarah Chen was Backend Engineer at TechCorp from Jan 2020 to Mar 2023"
"Sarah Chen led microservices migration in Q2 2022"
```

**Semantic Classification:**
- Type: Event
- Temporal: start_date, end_date
- Domain: Business

**Graph Connections:**
- → Candidates (experienced_by)
- → Companies (at_company)
- → Timeline (during)
- → Skills (developed_skill)

---

### 4. Jobs/Roles (Entity + Rule)
**Example Concepts:**
```
"Senior Backend Engineer role requires 5+ years experience" (Rule)
"Senior Backend Engineer must have distributed systems knowledge" (Rule)
"Senior Backend Engineer offers 170K-220K salary" (Quantitative)
```

**Semantic Classification:**
- Type: Entity + Rule
- Domain: Business
- Constraints: must, should, requires

**Graph Connections:**
- → Requirements (has_requirement)
- → Skills (requires_skill)
- → Candidates (matched_by)

---

### 5. Hiring Outcomes (Event + Causal)
**Example Concepts:**
```
"Sarah Chen hired on Nov 15 2024" (Event)
"Alex Kumar promoted within 6 months" (Event + Temporal)
"Bob Smith left after 4 months due to skills mismatch" (Causal)
```

**Semantic Classification:**
- Type: Event + Causal
- Temporal: hire_date, outcome_date
- Causation: success_factors, failure_factors

**Graph Connections:**
- → Candidates (outcome_for)
- → Success Factors (caused_by)
- → Timeline (occurred_at)

---

## Relationship Types

### 1. HAS (Candidate → Skill)
```
Edge: Sarah Chen ──has──> Go programming
Strength: 0.95 (6 years experience)
Temporal: acquired 2018, current as of 2024
```

### 2. REQUIRES (Job → Skill)
```
Edge: Senior Backend Engineer ──requires──> Distributed systems
Strength: 1.0 (mandatory)
Type: Rule (must have)
```

### 3. MATCHES (Candidate → Job)
```
Edge: Sarah Chen ──matches──> Senior Backend Engineer
Strength: 0.89 (MPPA confidence)
Reasoning: 7 paths (Go, microservices, leadership, ...)
```

### 4. CAUSES (Factor → Outcome)
```
Edge: Kubernetes experience ──causes──> Fast onboarding
Strength: 0.83
Evidence: 5 past hires with K8s → avg 2 weeks onboarding
```

### 5. TEMPORAL (Event → Timeline)
```
Edge: Sarah hired ──during──> November 2024
Bounds: start=2024-11-15, end=None
Relation: After (2024-11-15)
```

---

## Semantic Type Distribution

### Entity (40%)
- Candidates, companies, skills, technologies
- Named entities in hiring domain

### Event (25%)
- Hiring decisions, interviews, promotions
- Time-bound occurrences

### Temporal (15%)
- Career timelines, tenure periods
- Before/after/during relationships

### Causal (10%)
- Success/failure factors
- What leads to outcomes

### Rule (5%)
- Job requirements (must, should)
- Policies and constraints

### Quantitative (3%)
- Salary ranges, years of experience
- Performance metrics

### Condition (1%)
- Preferences, constraints
- If/when requirements

### Negation (1%)
- Exceptions, exclusions
- NOT clauses in requirements

---

## Example Query → Graph Traversal

### Query: "Who should we interview for Senior Backend Engineer?"

**Graph Traversal:**
```
1. Start: "Senior Backend Engineer" role node
   ↓
2. Follow: ──requires──> edges to get requirements
   → Distributed systems (Rule)
   → 5+ years experience (Quantitative)
   → Go or Rust (Rule + Condition)
   ↓
3. Reverse traverse: ←──has── edges from candidates
   → Sarah Chen has Go (6 years)
   → Jennifer Wu has backend (7 years, but Java/Python)
   → Michael Torres has DevOps (5 years, limited backend)
   ↓
4. Weight paths based on strength:
   → Sarah: 0.89 (Go + microservices + leadership)
   → Jennifer: 0.71 (strong backend, weak Go)
   → Michael: 0.64 (infrastructure, not backend)
   ↓
5. Return ranked candidates with reasoning paths
```

---

## Temporal Reasoning Example

### Query: "Who became senior engineer within 3 years?"

**Temporal Graph Walk:**
```
1. Find all promotion events:
   → "Alex Kumar promoted to Senior" (Sep 2024)
   → "Sarah Chen promoted to Senior" (Apr 2023)
   ↓
2. Find start of career for each:
   → Alex: Started as Engineer (Jan 2021)
   → Sarah: Started as Junior (Jan 2018)
   ↓
3. Calculate duration:
   → Alex: 2021 → 2024 = 3 years ✓
   → Sarah: 2018 → 2023 = 5 years ✗
   ↓
4. Filter by temporal constraint (≤ 3 years):
   → Return: Alex Kumar
```

---

## Causal Reasoning Example

### Query: "What causes successful backend hires?"

**Causal Graph Analysis:**
```
1. Find all successful backend hires:
   → Alex Kumar: Promoted, high performance
   → Sarah Chen: (future hire, assume success)
   ↓
2. Extract common factors:
   → Alex: Kubernetes experience
   → Alex: Microservices background
   → Alex: 3+ years tenure at previous company
   ↓
3. Find correlations with success:
   → K8s experience: 5/6 successful (0.83 correlation)
   → Microservices: 4/5 successful (0.80 correlation)
   → 3+ year tenure: 7/9 successful (0.78 correlation)
   ↓
4. Return causal factors ranked by strength:
   1. Kubernetes experience (0.83)
   2. Microservices background (0.80)
   3. Stable tenure (0.78)
```

---

## Knowledge Graph Growth

### Initial State (0 hires)
```
Nodes: 50 (job requirements, company values)
Edges: 100 (requirement relationships)
Knowledge: Job definitions only
```

### After 10 Hires
```
Nodes: 500
  - 10 candidates
  - 50 skills
  - 30 companies
  - 100 events (interviews, hires)
Edges: 2,000
  - has_skill: 200
  - worked_at: 30
  - requires: 100
  - matches: 50
Knowledge: Basic patterns emerging
```

### After 100 Hires
```
Nodes: 5,000
  - 100 candidates
  - 200 skills
  - 80 companies
  - 500 events
  - 50 interviewers
Edges: 25,000
  - Causal: 500 (success/failure factors)
  - Temporal: 1,000 (career progressions)
  - Semantic: 3,000 (skill relationships)
Knowledge: Strong predictive patterns
```

### After 1,000 Hires (Enterprise Scale)
```
Nodes: 50,000
Edges: 500,000
Concepts: 100,000+
Knowledge: Highly accurate predictions (0.85+ confidence calibration)
Patterns: Deep causal chains (multi-hop reasoning)
```

---

## Graph Query Patterns

### Pattern 1: Direct Match
```
QUERY: "Who has Go experience?"
PATTERN: Candidate ──has──> Go
COMPLEXITY: O(1) - simple edge lookup
```

### Pattern 2: Temporal Filter
```
QUERY: "Who has Kubernetes experience after 2022?"
PATTERN: Candidate ──has──> K8s WHERE temporal_bounds.start > 2022
COMPLEXITY: O(n) - filter by temporal constraint
```

### Pattern 3: Multi-Hop Causal
```
QUERY: "What causes successful hires?"
PATTERN: 
  Success ←──caused_by── Factor
  Factor ──possessed_by──> Candidate
  Candidate ──hired_for──> Role
COMPLEXITY: O(n²) - multi-hop traversal with aggregation
```

### Pattern 4: MPPA (Multi-Path)
```
QUERY: "Who matches Senior Backend Engineer?"
PATTERN: Find ALL paths from Candidate to Role requirements
  Path 1: Sarah ──has──> Go ──required_by──> Role
  Path 2: Sarah ──led──> Microservices ──relevant_to──> Role
  Path 3: Sarah ──mentored──> Engineers ──valued_by──> Role
  ... (aggregate 7+ paths)
COMPLEXITY: O(n³) - exhaustive path search + aggregation
```

---

## Storage Optimization

### Concept Deduplication
```
"Sarah Chen has Go experience"
"Sarah Chen has 6 years Go experience"
→ Merged into single concept with metadata:
  - skill: Go
  - years: 6
  - confidence: 0.95
```

### Association Compression
```
Instead of storing:
  Sarah ──has──> Python
  Sarah ──has──> Java
  Sarah ──has──> Go
  Sarah ──has──> Rust

Store:
  Sarah ──has_skills──> [Python, Java, Go, Rust]
  (Multi-edge with type annotations)
```

### Temporal Indexing
```
Events indexed by timestamp:
  2024-11-15: Sarah hired
  2024-11-08: Sarah interviewed
  2024-11-05: Sarah phone screen

Enables fast temporal range queries:
  "Show all hires in November 2024"
  → O(log n) index lookup instead of O(n) scan
```

---

## Conclusion

The hiring knowledge graph leverages Sutra's core capabilities:

1. **Semantic Understanding** - 9 types classify hiring concepts
2. **Temporal Reasoning** - Career progression, skill recency
3. **Causal Analysis** - Success/failure factors
4. **Explainable Paths** - MPPA multi-path aggregation

This structure enables natural language queries that traditional databases cannot handle, while maintaining complete audit trails for compliance.

**No SQL. No Cypher. No GraphQL. Just natural language over a semantically-aware graph.**
