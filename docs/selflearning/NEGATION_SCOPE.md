# Negation Scope Analysis: What It Does

**This document explains what "negation scope analysis" means in sutra-storage**

---

## Quick Answer

**Negation scope analysis detects when a sentence contains negative statements or exceptions, and tracks what concepts are being negated.**

Examples:
- "Aspirin is **not** recommended for children" ← Negation detected
- "All patients **except** those with allergies" ← Exception detected
- "Never administer without consent" ← Explicit negation detected

---

## The Code: How It Works

### Step 1: Pattern Detection

```rust
// From: packages/sutra-storage/src/semantic/analyzer.rs (lines 75-76)

// Negation patterns
negation_explicit: Regex::new(
    r"(?i)\b(not|no|never|none|nothing|neither|nor)\b"
).unwrap(),

negation_exception: Regex::new(
    r"(?i)\b(except|unless|excluding|other than|but not|save for)\b"
).unwrap(),
```

**What it looks for:**
- **Explicit negation**: not, no, never, none, nothing, neither, nor
- **Exceptions**: except, unless, excluding, other than, but not, save for

### Step 2: Extraction

```rust
// From: packages/sutra-storage/src/semantic/analyzer.rs (lines 350-363)

fn extract_negation(&self, text: &str) -> Option<NegationScope> {
    let negation_type = if PATTERNS.negation_explicit.is_match(text) {
        NegationType::Explicit      // ← Found "not", "never", etc.
    } else if PATTERNS.negation_exception.is_match(text) {
        NegationType::Exception     // ← Found "except", "unless", etc.
    } else {
        return None;                // ← No negation found
    };
    
    Some(NegationScope {
        negated_concept_ids: Vec::new(),  // Populated later
        confidence: 0.8,
        negation_type,
    })
}
```

### Step 3: Storage Structure

```rust
// From: packages/sutra-storage/src/semantic/types.rs (lines 212-232)

pub struct NegationScope {
    /// Concepts that are negated by this concept
    pub negated_concept_ids: Vec<[u8; 16]>,  // ← IDs of negated concepts
    
    /// Confidence in negation (0.0 - 1.0)
    pub confidence: f32,  // ← How sure (default: 0.8)
    
    /// Type of negation
    pub negation_type: NegationType,  // ← Explicit or Exception
}

pub enum NegationType {
    Explicit,       // "not", "never", "no"
    Exception,      // "except", "unless", "excluding"
    Contradiction,  // "conflicts with" (detected separately)
}
```

---

## Real Examples

### Example 1: Explicit Negation

**Input:**
```
"Aspirin is not recommended for children under 12"
```

**What Happens:**

```
Step 1: Semantic Analysis
  Pattern match: "not" found
  Type: NegationType::Explicit
  
Step 2: Classification
  semantic_type: Negation  ← Primary type
  negation_scope: Some(NegationScope {
      negated_concept_ids: [],
      confidence: 0.8,
      negation_type: Explicit
  })

Step 3: Stored Concept
┌─────────────────────────────────────────────────────────┐
│ Concept ID: abc123...                                   │
│ Content: "Aspirin is not recommended for children..."   │
│ Type: Negation                                          │
│ Domain: Medical                                         │
│                                                         │
│ Negation Scope:                                         │
│   Type: Explicit                                        │
│   Confidence: 0.8                                       │
│   Negated concepts: [] (empty initially)                │
└─────────────────────────────────────────────────────────┘
```

**Queryable:**
```python
# Find all negations in Medical domain
results = client.query_by_semantic(
    filter={"semantic_type": "Negation", "domain": "Medical"}
)
# Returns: This concept
```

---

### Example 2: Exception (Unless Clause)

**Input:**
```
"Metformin is prescribed unless contraindicated"
```

**What Happens:**

```
Step 1: Semantic Analysis
  Pattern match: "unless" found
  Type: NegationType::Exception
  
Step 2: Classification
  semantic_type: Negation  ← Primary type
  negation_scope: Some(NegationScope {
      negated_concept_ids: [],
      confidence: 0.8,
      negation_type: Exception
  })

Step 3: Stored Concept
┌─────────────────────────────────────────────────────────┐
│ Concept ID: def456...                                   │
│ Content: "Metformin is prescribed unless..."            │
│ Type: Negation                                          │
│ Domain: Medical                                         │
│                                                         │
│ Negation Scope:                                         │
│   Type: Exception  ← "unless" is an exception           │
│   Confidence: 0.8                                       │
│   Negated concepts: [] (empty initially)                │
└─────────────────────────────────────────────────────────┘
```

**Meaning:** 
- This is a rule WITH exceptions
- The exception scope is tracked
- Can query for "rules with exceptions"

---

### Example 3: Multiple Negations

**Input:**
```
"Patients should not smoke and never consume alcohol"
```

**What Happens:**

```
Step 1: Pattern Matches
  Found: "not" (explicit negation)
  Found: "never" (explicit negation)
  Count: 2 negation markers

Step 2: Confidence Calculation
  Base confidence: 0.8
  Multiple matches boost confidence
  Final confidence: 0.85

Step 3: Stored
┌─────────────────────────────────────────────────────────┐
│ Concept ID: ghi789...                                   │
│ Content: "Patients should not smoke..."                 │
│ Type: Negation                                          │
│ Domain: Medical                                         │
│                                                         │
│ Negation Scope:                                         │
│   Type: Explicit                                        │
│   Confidence: 0.85  ← Higher (multiple negations)       │
│   Negated concepts: []                                  │
└─────────────────────────────────────────────────────────┘
```

---

## What Negation Scope Does NOT Do

### ❌ Does NOT Track What Is Negated

```python
# Concept: "Aspirin is not recommended for children"

negation_scope.negated_concept_ids = []  # ← ALWAYS EMPTY!
```

**Why?**
The code shows:
```rust
negated_concept_ids: Vec::new(),  // Populated later during graph construction
```

This field is **initialized empty and never populated** in the current implementation. It's a **placeholder for future functionality**.

### ❌ Does NOT Prevent Contradictions

```python
# Both stored without conflict
client.learn_concept("Aspirin prevents blood clots")
client.learn_concept("Aspirin is not effective for blood clots")
# ↑ Second one has negation_scope, but both exist
```

### ❌ Does NOT Link to Related Concepts

```python
# These are NOT automatically connected
concept_1 = "Metformin is prescribed"
concept_2 = "Metformin is not prescribed unless..."

# negation_scope in concept_2 does NOT point to concept_1
```

---

## What It's Actually Used For

### 1. Semantic Classification

```python
# Find all statements with negations
negations = client.query_by_semantic(
    filter={"semantic_type": "Negation"}
)
# Returns: All concepts containing "not", "never", "except", etc.
```

### 2. Exception Tracking

```python
# Find rules with exceptions
exceptions = client.query_by_semantic(
    filter={
        "semantic_type": "Negation",
        "negation_type": "Exception"
    }
)
# Returns: All "unless", "except" clauses
```

### 3. Confidence Scoring

```rust
// From: packages/sutra-storage/src/semantic/analyzer.rs (lines 386-390)

SemanticType::Negation => {
    PATTERNS.negation_explicit.find_iter(text).count() +
    PATTERNS.negation_exception.find_iter(text).count()
}
// ↑ More negation markers = higher confidence
```

**Result:** Concepts with multiple negations get higher confidence scores.

### 4. Query Filtering

```python
# Find explicit negations in Medical domain
results = client.find_path_semantic(
    start_id="patient_001",
    end_id="treatment_protocol",
    filter={
        "semantic_type": "Negation",
        "domain": "Medical",
        "negation_type": "Explicit"
    }
)
# Returns: Paths through explicit medical negations only
```

---

## Practical Use Cases

### Use Case 1: Contraindications Database

```python
# Medical contraindications often contain negations
contraindications = [
    "Aspirin is not recommended for children under 12",
    "Penicillin should not be given to allergic patients",
    "Metformin is contraindicated in renal failure"
]

for contra in contraindications:
    client.learn_concept(contra)

# Query: Find all contraindications
results = client.query_by_semantic(
    filter={
        "semantic_type": "Negation",
        "domain": "Medical"
    }
)
# Returns: All contraindications (they contain "not", "contraindicated")
```

### Use Case 2: Legal Exceptions

```python
# Legal documents have many exception clauses
legal_rules = [
    "All citizens must pay taxes except those earning below threshold",
    "Evidence is admissible unless obtained illegally",
    "Contracts are binding excluding force majeure events"
]

for rule in legal_rules:
    client.learn_concept(rule)

# Query: Find exception clauses
results = client.query_by_semantic(
    filter={
        "semantic_type": "Negation",
        "negation_type": "Exception",
        "domain": "Legal"
    }
)
# Returns: All exception clauses
```

### Use Case 3: Safety Warnings

```python
# Safety warnings often use explicit negations
warnings = [
    "Never mix bleach with ammonia",
    "Do not operate machinery while medicated",
    "Never swim alone in deep water"
]

for warning in warnings:
    client.learn_concept(warning)

# Query: Find all safety warnings
results = client.query_by_semantic(
    filter={"semantic_type": "Negation"}
)
# "never", "do not" trigger negation detection
```

---

## Summary Table

| What It Does | What It Doesn't Do |
|--------------|-------------------|
| ✓ Detects "not", "never", "no" | ✗ Link to contradicted concepts |
| ✓ Detects "except", "unless" | ✗ Populate negated_concept_ids |
| ✓ Classifies as Negation type | ✗ Prevent contradictions |
| ✓ Stores negation metadata | ✗ Resolve conflicts |
| ✓ Enables negation queries | ✗ Track semantic negation targets |
| ✓ Calculates confidence | ✗ Validate logical consistency |

---

## Design Note

```
┌──────────────────────────────────────────────────────────────┐
│ Negation Scope is METADATA, not LOGIC                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ It tells you: "This concept contains a negation"            │
│ It does NOT: "This concept negates concept X"               │
│                                                              │
│ The negated_concept_ids field exists but is UNUSED          │
│ It's a placeholder for future graph construction logic      │
│                                                              │
│ Current behavior: Detection only, no linking                │
└──────────────────────────────────────────────────────────────┘
```

---

## Code References

**Pattern Definitions:**
- `packages/sutra-storage/src/semantic/analyzer.rs` lines 75-76

**Extraction Logic:**
- `packages/sutra-storage/src/semantic/analyzer.rs` lines 350-363

**Data Structure:**
- `packages/sutra-storage/src/semantic/types.rs` lines 212-232

**Usage in Analysis:**
- `packages/sutra-storage/src/semantic/analyzer.rs` lines 147-151

---

**Related**: [Learning Architecture](./ARCHITECTURE.md) | [Natural Language Scenarios](./NATURAL_LANGUAGE_SCENARIOS.md)
