# Natural Language Learning Scenarios

**How sutra-storage learns from real-world text inputs**

---

## Overview

This document demonstrates **exactly what happens** when the system ingests natural language text of varying complexity. Unlike controlled data ingestion, natural language is unpredictable—sentences can be simple facts, complex narratives, or entire documents. The system must extract knowledge from any input.

**Key Principle**: The system learns what it can extract. It doesn't fail on "bad" input; it extracts maximum value from whatever is provided.

---

## Scenario 1: Simple Factual Statement

### Input
```python
client.learn_concept("Humans are mammals.")
```

### Processing Steps

#### Step 1: Embedding Generation
```
Input: "Humans are mammals."
Model: nomic-embed-text-v1.5
Output: [0.023, -0.145, 0.089, ..., 0.234]  # 768 dimensions
Latency: ~30ms
```

#### Step 2: Semantic Analysis
```rust
// File: packages/sutra-storage/src/semantic/analyzer.rs

SemanticMetadata {
    semantic_type: Definitional,  // ← "are" indicates definition
    
    temporal_bounds: None,  // ← No temporal markers
    
    causal_relations: None,  // ← No causal markers
    
    domain_context: Some(Scientific),  // ← "mammals" is scientific term
    
    negation_scope: None,  // ← No negation
    
    classification_confidence: 0.85,  // ← High confidence
}
```

**Pattern Matching**:
- `definitional_is_a` pattern: "are" → Definitional type
- `domain_scientific` pattern: "mammals" → Scientific domain

#### Step 3: Association Extraction
```rust
// Sentence: "Humans are mammals."

// 1. Split into sentences
sentences = ["Humans are mammals"]

// 2. Embed sentence
sentence_embedding = [0.145, 0.234, ...]

// 3. Classify relation type (cosine similarity)
relation_type = Semantic  // ← "is a" relationship
confidence = 0.78

// 4. Extract entities (capitalization heuristics)
entities = ["Humans"]  // ← "mammals" not capitalized enough

// Result: 1 association
SemanticAssociation {
    target: "Humans",
    assoc_type: Semantic,
    confidence: 0.78,
}
```

**Why only 1 association?**
- "Humans" is capitalized → Extracted
- "mammals" is lowercase → Not extracted as entity
- Only first entity becomes target

#### Step 4: Concept ID Generation
```rust
use std::hash::{Hash, Hasher};

let mut hasher = DefaultHasher::new();
"Humans are mammals.".hash(&mut hasher);
let hash = hasher.finish();

concept_id = format!("{:016x}", hash)
// Result: "a3f2c8d1e4b6f9a2"
```

**Deterministic**: Same text always generates same ID.

#### Step 5: Storage
```rust
// WAL entry
Operation::WriteConcept {
    concept_id: ConceptId::from_string("a3f2c8d1e4b6f9a2"),
    content_len: 19,  // "Humans are mammals."
    vector_len: 768,
    created: 1730073600000000,  // microseconds
    modified: 1730073600000000,
}

// Stored in concurrent memory
ConceptNode {
    id: a3f2c8d1e4b6f9a2,
    content: b"Humans are mammals.",
    strength: 1.0,
    confidence: 1.0,
    semantic: Some(SemanticMetadata {
        semantic_type: Definitional,
        domain_context: Some(Scientific),
        classification_confidence: 0.85,
    }),
}

// HNSW index
vector[a3f2c8d1e4b6f9a2] = [0.023, -0.145, ..., 0.234]
```

### What System Learned

```json
{
  "concept_id": "a3f2c8d1e4b6f9a2",
  "content": "Humans are mammals.",
  "semantic_type": "Definitional",
  "domain": "Scientific",
  "associations": [
    {
      "target": "Humans",
      "type": "Semantic",
      "confidence": 0.78
    }
  ],
  "embedding": [768 dimensions],
  "queryable_via": [
    "Vector search: 'what are humans'",
    "Semantic filter: type=Definitional, domain=Scientific",
    "Graph traversal: from 'Humans' concept"
  ]
}
```

### Expected Behavior

**What you can query**:
```python
# 1. Semantic search
results = client.vector_search("what are mammals")
# Returns: This concept (high similarity)

# 2. Domain-specific search
results = client.query_by_semantic(
    filter={"domain_context": "Scientific"}
)
# Returns: This concept (and other scientific facts)

# 3. Type-based search
results = client.query_by_semantic(
    filter={"semantic_type": "Definitional"}
)
# Returns: This concept (and other definitions)

# 4. Graph traversal
neighbors = client.get_neighbors("a3f2c8d1e4b6f9a2")
# Returns: ["Humans" concept ID] if it exists
```

**What you cannot query**:
- Specific to "mammals" (not extracted as separate entity)
- Temporal queries (no time component)
- Causal queries (no causality)

---

## Scenario 2: Multi-Fact Sentence

### Input
```python
client.learn_concept(
    "Diabetes requires regular blood glucose monitoring and "
    "affects insulin production in the pancreas."
)
```

### Processing Steps

#### Step 1: Embedding Generation
```
Input: "Diabetes requires regular blood glucose monitoring..."
Output: [0.156, -0.089, 0.234, ..., -0.145]  # 768 dimensions
Latency: ~30ms
```

#### Step 2: Semantic Analysis
```rust
SemanticMetadata {
    semantic_type: Rule,  // ← "requires" is modal verb
    
    temporal_bounds: None,
    
    causal_relations: Some(vec![
        CausalRelation {
            cause: "Diabetes",
            effect: "affects insulin production",
            causal_type: Direct,
            confidence: 0.82,
        }
    ]),
    
    domain_context: Some(Medical),  // ← "Diabetes", "insulin", "pancreas"
    
    negation_scope: None,
    
    classification_confidence: 0.92,  // ← Very high confidence
}
```

**Pattern Matching**:
- `rule_modal`: "requires" → Rule type
- `causal_direct`: "affects" → Causal relation
- `domain_medical`: "Diabetes", "glucose", "insulin", "pancreas" → Medical

#### Step 3: Association Extraction

```rust
// Split into sentences
sentences = [
    "Diabetes requires regular blood glucose monitoring and affects insulin production in the pancreas"
]

// Embed sentence
embedding = [0.156, -0.089, ...]

// Classify relation
// "requires" + "affects" → Mixed semantic and causal
// Take highest scoring: Semantic (0.82)

// Extract entities (capitalized words)
entities = ["Diabetes"]

// Result: 1 association
SemanticAssociation {
    target: "Diabetes",
    assoc_type: Semantic,
    confidence: 0.82,
}
```

**Why only 1 association?**
- "Diabetes" is capitalized → Extracted
- "glucose", "insulin", "pancreas" are lowercase → Not extracted
- Medical terms often lowercase → Limitation of capitalization heuristic

**Workaround**: Multi-word medical terms like "Diabetes Mellitus" would be extracted.

#### Step 4: Storage

```rust
ConceptNode {
    id: b8e4d9f2a1c7b5e3,
    content: b"Diabetes requires regular blood glucose monitoring...",
    strength: 1.0,
    confidence: 1.0,
    semantic: Some(SemanticMetadata {
        semantic_type: Rule,
        domain_context: Some(Medical),
        causal_relations: Some([...]),
        classification_confidence: 0.92,
    }),
}
```

### What System Learned

```json
{
  "concept_id": "b8e4d9f2a1c7b5e3",
  "content": "Diabetes requires regular blood glucose monitoring and affects insulin production in the pancreas.",
  "semantic_type": "Rule",
  "domain": "Medical",
  "causal_relations": [
    {
      "cause": "Diabetes",
      "effect": "affects insulin production",
      "type": "Direct",
      "confidence": 0.82
    }
  ],
  "associations": [
    {
      "target": "Diabetes",
      "type": "Semantic",
      "confidence": 0.82
    }
  ],
  "embedding": [768 dimensions],
  "queryable_via": [
    "Vector search: 'diabetes management'",
    "Domain filter: Medical",
    "Type filter: Rule",
    "Causal chain: from 'Diabetes' concept"
  ]
}
```

### Expected Behavior

**What you can query**:
```python
# 1. Medical protocol search
results = client.query_by_semantic(
    filter={
        "semantic_type": "Rule",
        "domain_context": "Medical"
    }
)
# Returns: This concept (medical rule)

# 2. Causal chain analysis
chain = client.find_causal_chain(
    start_id="b8e4d9f2a1c7b5e3",
    causal_type="Direct",
    max_depth=3
)
# Returns: Causal relationships involving diabetes

# 3. Semantic search for diabetes
results = client.vector_search("how to manage diabetes")
# Returns: This concept (high similarity to "blood glucose monitoring")

# 4. Rule-based reasoning
rules = client.query_by_semantic(
    filter={"semantic_type": "Rule", "domain_context": "Medical"}
)
# Returns: All medical rules including this one
```

**Limitations**:
- "insulin" and "pancreas" not extracted as separate entities
- Could benefit from medical NER (Named Entity Recognition)

---

## Scenario 3: Complex Narrative

### Input
```python
client.learn_concept(
    "On January 15, 2024, Patient Smith was diagnosed with Type 2 Diabetes "
    "after presenting with elevated blood glucose levels. The diagnosis led to "
    "immediate changes in treatment protocol. Dr. Johnson prescribed Metformin "
    "and recommended lifestyle modifications including diet and exercise."
)
```

### Processing Steps

#### Step 1: Embedding Generation
```
Input: "On January 15, 2024, Patient Smith was diagnosed..."
Output: [0.234, 0.089, -0.156, ..., 0.145]  # 768 dimensions
Latency: ~35ms (longer text)
```

#### Step 2: Semantic Analysis

```rust
SemanticMetadata {
    semantic_type: Event,  // ← "diagnosed", "presenting" are event markers
    
    temporal_bounds: Some(TemporalBounds {
        start_time: Some(1705276800),  // Jan 15, 2024 (Unix timestamp)
        end_time: None,
        temporal_type: TemporalType::At,
        confidence: 0.95,
    }),
    
    causal_relations: Some(vec![
        CausalRelation {
            cause: "elevated blood glucose levels",
            effect: "diagnosed with Type 2 Diabetes",
            causal_type: Direct,
            confidence: 0.88,
        },
        CausalRelation {
            cause: "diagnosis",
            effect: "changes in treatment protocol",
            causal_type: Enabling,
            confidence: 0.76,
        }
    ]),
    
    domain_context: Some(Medical),
    
    negation_scope: None,
    
    classification_confidence: 0.94,
}
```

**Pattern Matching**:
- `event_past`: "was diagnosed", "presented", "prescribed" → Event
- `temporal_at`: "January 15, 2024" → Temporal extraction
- `causal_direct`: "led to" → Causal chain
- `domain_medical`: Multiple medical terms → Medical domain

#### Step 3: Association Extraction

```rust
// Split into sentences
sentences = [
    "On January 15, 2024, Patient Smith was diagnosed with Type 2 Diabetes after presenting with elevated blood glucose levels",
    "The diagnosis led to immediate changes in treatment protocol",
    "Dr. Johnson prescribed Metformin and recommended lifestyle modifications including diet and exercise"
]

// Embed each sentence
embeddings = [
    [0.234, 0.089, ...],
    [0.156, -0.089, ...],
    [0.089, 0.234, ...]
]

// Classify relations
// Sentence 1: Causal ("after") → 0.88
// Sentence 2: Causal ("led to") → 0.85
// Sentence 3: Semantic ("prescribed") → 0.72

// Extract entities per sentence
// Sentence 1: ["Patient Smith", "Type 2 Diabetes"]
// Sentence 2: [] (no capitalized entities)
// Sentence 3: ["Dr", "Johnson", "Metformin"]

// Results: 5 associations
associations = [
    SemanticAssociation { target: "Patient Smith", assoc_type: Causal, confidence: 0.88 },
    SemanticAssociation { target: "Type 2 Diabetes", assoc_type: Causal, confidence: 0.88 },
    SemanticAssociation { target: "Dr", assoc_type: Semantic, confidence: 0.72 },
    SemanticAssociation { target: "Johnson", assoc_type: Semantic, confidence: 0.72 },
    SemanticAssociation { target: "Metformin", assoc_type: Semantic, confidence: 0.72 },
]

// Apply confidence threshold (0.5) and max associations (10)
// All pass → 5 associations stored
```

#### Step 4: Storage

```rust
ConceptNode {
    id: c9d3e5f1a8b2c4d6,
    content: b"On January 15, 2024, Patient Smith was diagnosed...",
    strength: 1.0,
    confidence: 1.0,
    semantic: Some(SemanticMetadata {
        semantic_type: Event,
        domain_context: Some(Medical),
        temporal_bounds: Some(TemporalBounds { ... }),
        causal_relations: Some([...]),
        classification_confidence: 0.94,
    }),
}

// 5 associations created
learn_association(c9d3e5f1, target_id("Patient Smith"), Causal, 0.88)
learn_association(c9d3e5f1, target_id("Type 2 Diabetes"), Causal, 0.88)
learn_association(c9d3e5f1, target_id("Dr"), Semantic, 0.72)
learn_association(c9d3e5f1, target_id("Johnson"), Semantic, 0.72)
learn_association(c9d3e5f1, target_id("Metformin"), Semantic, 0.72)
```

### What System Learned

```json
{
  "concept_id": "c9d3e5f1a8b2c4d6",
  "content": "On January 15, 2024, Patient Smith was diagnosed...",
  "semantic_type": "Event",
  "domain": "Medical",
  "temporal": {
    "date": "2024-01-15T00:00:00Z",
    "type": "At",
    "confidence": 0.95
  },
  "causal_chain": [
    {
      "cause": "elevated blood glucose levels",
      "effect": "diagnosed with Type 2 Diabetes",
      "confidence": 0.88
    },
    {
      "cause": "diagnosis",
      "effect": "changes in treatment protocol",
      "confidence": 0.76
    }
  ],
  "associations": [
    {"target": "Patient Smith", "type": "Causal", "confidence": 0.88},
    {"target": "Type 2 Diabetes", "type": "Causal", "confidence": 0.88},
    {"target": "Dr", "type": "Semantic", "confidence": 0.72},
    {"target": "Johnson", "type": "Semantic", "confidence": 0.72},
    {"target": "Metformin", "type": "Semantic", "confidence": 0.72}
  ],
  "embedding": [768 dimensions],
  "queryable_via": [
    "Vector search: 'diabetes diagnosis'",
    "Temporal search: events on 2024-01-15",
    "Causal chain: glucose → diabetes → treatment",
    "Domain filter: Medical events",
    "Graph traversal: from Patient Smith or Metformin"
  ]
}
```

### Expected Behavior

**What you can query**:
```python
# 1. Temporal search
events = client.find_temporal_chain(
    domain="Medical",
    start_time=1705276800,  # Jan 15, 2024
    end_time=1705363200     # Jan 16, 2024
)
# Returns: This event (and other events on that date)

# 2. Causal chain analysis
chain = client.find_causal_chain(
    start_id="c9d3e5f1a8b2c4d6",
    causal_type="Direct",
    max_depth=5
)
# Returns: glucose → diabetes → treatment chain

# 3. Patient-centric search
results = client.get_neighbors(target_id("Patient Smith"))
# Returns: This event (and other events involving Patient Smith)

# 4. Drug-based search
results = client.get_neighbors(target_id("Metformin"))
# Returns: This event (and other events involving Metformin)

# 5. Medical event timeline
events = client.query_by_semantic(
    filter={
        "semantic_type": "Event",
        "domain_context": "Medical"
    }
)
# Returns: All medical events including this one
```

**Advanced Queries**:
```python
# Find all diabetes diagnoses in January 2024
events = client.query_by_semantic(
    filter={
        "semantic_type": "Event",
        "domain_context": "Medical",
        "temporal_after": 1704067200,   # Jan 1, 2024
        "temporal_before": 1706745600,  # Feb 1, 2024
        "required_terms": ["diagnosed", "Diabetes"]
    }
)
```

---

## Scenario 4: Long Document (Multi-Page)

### Input
```python
# Medical protocol document (5000 words)
document = """
CLINICAL PROTOCOL FOR TYPE 2 DIABETES MANAGEMENT

1. INTRODUCTION
Type 2 Diabetes Mellitus is a metabolic disorder characterized by insulin resistance...

2. DIAGNOSIS CRITERIA
Patients must meet one of the following criteria:
- Fasting plasma glucose ≥ 126 mg/dL
- 2-hour plasma glucose ≥ 200 mg/dL during OGTT
- HbA1c ≥ 6.5%

3. TREATMENT PROTOCOL
3.1 First-Line Therapy
Metformin is the preferred initial medication unless contraindicated...

3.2 Lifestyle Modifications
All patients must receive counseling on:
- Diet: Mediterranean or DASH diet
- Exercise: 150 minutes moderate activity per week
- Weight loss: 5-10% reduction if overweight

[... 4500 more words ...]
"""

client.learn_concept(document)
```

### Processing Strategy

The system treats long documents as **single atomic concepts** with extensive metadata extraction.

#### Step 1: Embedding Generation (Truncation)

```python
# Most embedding models have token limits
# nomic-embed-text-v1.5: 512 tokens (~2048 characters)

# System behavior:
# 1. Truncate to first 2048 characters
# 2. Generate embedding from truncated text
# 3. Store full content (no truncation in storage)

truncated = document[:2048]
embedding = embedding_client.generate(truncated)

# Warning logged:
# "Content length 25000 exceeds embedding context, truncating to 2048"
```

**Impact**:
- Embedding captures only introduction/beginning
- Later sections not represented in vector space
- Semantic search biased toward beginning

**Workaround** (Recommended):
```python
# Option 1: Chunk document into logical sections
sections = [
    "CLINICAL PROTOCOL FOR TYPE 2 DIABETES MANAGEMENT\n1. INTRODUCTION\n...",
    "2. DIAGNOSIS CRITERIA\nPatients must meet...",
    "3. TREATMENT PROTOCOL\n3.1 First-Line Therapy...",
    # ... etc
]

concept_ids = client.learn_batch_v2(sections)

# Then create document structure
doc_id = client.learn_concept(
    "Document: Type 2 Diabetes Protocol",
    generate_embedding=False
)

for section_id in concept_ids:
    client.learn_association(
        source_id=doc_id,
        target_id=section_id,
        association_type=AssociationType.Compositional,
        confidence=1.0
    )
```

#### Step 2: Semantic Analysis (Full Document)

```rust
// Semantic analysis processes ENTIRE document (no truncation)
SemanticMetadata {
    semantic_type: Rule,  // ← "must", "required" throughout
    
    temporal_bounds: None,  // ← Protocol is timeless
    
    causal_relations: Some(vec![
        // Extracted from multiple sections
        CausalRelation { cause: "insulin resistance", effect: "Type 2 Diabetes", ... },
        CausalRelation { cause: "Metformin", effect: "glucose reduction", ... },
        // ... potentially many more
    ]),
    
    domain_context: Some(Medical),
    
    negation_scope: Some(vec![
        // "unless contraindicated"
        NegationScope { scope: "Metformin", condition: "contraindicated", ... }
    ]),
    
    classification_confidence: 0.96,  // ← Very high (many medical terms)
}
```

#### Step 3: Association Extraction (Batch Processing)

```rust
// Split document into sentences
sentences = split_sentences(document);
// Result: ~250 sentences (20 words/sentence average)

// Batch embed sentences (single API call)
sentence_embeddings = embedding_client.generate_batch(sentences);
// Latency: ~3ms per sentence × 250 = 750ms total

// Process each sentence
let mut associations = Vec::new();
for (sentence, embedding) in sentences.zip(sentence_embeddings) {
    let (assoc_type, confidence) = classify_relation(&embedding);
    
    if confidence >= 0.5 {
        let entities = extract_entities(sentence);
        for target in entities[1..] {
            associations.push(SemanticAssociation {
                target,
                assoc_type,
                confidence,
            });
        }
    }
}

// Apply limits
// max_associations_per_concept = 10 (default)
associations.truncate(10);  // ← Only top 10 stored
```

**Important**: Only first 10 associations stored by default. For documents, consider increasing:
```python
client.learn_concept(
    content=document,
    max_associations_per_concept=50,  # ← More associations
    min_association_confidence=0.7,   # ← Higher quality threshold
)
```

#### Step 4: Storage

```rust
ConceptNode {
    id: d7e2f4a9b1c8d5e7,
    content: b"CLINICAL PROTOCOL FOR TYPE 2 DIABETES MANAGEMENT...",  // Full 25,000 bytes
    strength: 1.0,
    confidence: 1.0,
    semantic: Some(SemanticMetadata {
        semantic_type: Rule,
        domain_context: Some(Medical),
        causal_relations: Some([...]),  // Multiple causal chains
        negation_scope: Some([...]),
        classification_confidence: 0.96,
    }),
}

// Top 10 associations stored
// (or 50 if configured)
```

### What System Learned

```json
{
  "concept_id": "d7e2f4a9b1c8d5e7",
  "content": "[Full 5000-word document stored]",
  "content_length": 25000,
  "semantic_type": "Rule",
  "domain": "Medical",
  "causal_relations": [
    "Multiple causal chains extracted from document"
  ],
  "negation_scopes": [
    "Contraindications and exceptions"
  ],
  "associations": [
    "Top 10 most relevant entities/concepts",
    "Truncated due to max_associations_per_concept=10"
  ],
  "embedding": [
    "Based on first 2048 characters only",
    "Biased toward introduction"
  ],
  "queryable_via": [
    "Vector search: 'diabetes protocol' (introduction only)",
    "Domain filter: Medical",
    "Type filter: Rule",
    "Full-text search: entire document",
    "Graph traversal: top 10 associations"
  ]
}
```

### Expected Behavior

**What works well**:
```python
# 1. Full-text retrieval
concept = client.get_concept("d7e2f4a9b1c8d5e7")
# Returns: Full document content

# 2. Semantic classification
rules = client.query_by_semantic(
    filter={"semantic_type": "Rule", "domain_context": "Medical"}
)
# Returns: This document (classified as medical rule)

# 3. Causal analysis
chains = client.find_causal_chain(start_id="d7e2f4a9b1c8d5e7")
# Returns: Causal relationships extracted from document
```

**What has limitations**:
```python
# 1. Vector search (only first 2048 chars embedded)
results = client.vector_search("DASH diet recommendations")
# May NOT return this document if "DASH" is in section 3.2
# (beyond embedding context window)

# 2. Association coverage (only top 10 by default)
neighbors = client.get_neighbors("d7e2f4a9b1c8d5e7")
# Returns: Only 10 associations (not all entities in document)
```

### Recommended Approach for Long Documents

```python
# 1. Chunk into logical sections
sections = chunk_document_by_headers(document)

# 2. Learn each section
section_ids = []
for i, section in enumerate(sections):
    concept_id = client.learn_concept(
        content=section,
        max_associations_per_concept=20,  # More per section
    )
    section_ids.append(concept_id)

# 3. Create document hierarchy
doc_id = client.learn_concept(
    content=f"Document: {title}",
    generate_embedding=False,
    extract_associations=False,
)

# 4. Link sections to document
for i, section_id in enumerate(section_ids):
    client.learn_association(
        source_id=doc_id,
        target_id=section_id,
        association_type=AssociationType.Compositional,
        confidence=1.0,
    )
    
    # Link sections sequentially
    if i > 0:
        client.learn_association(
            source_id=section_ids[i-1],
            target_id=section_id,
            association_type=AssociationType.Temporal,
            confidence=1.0,
        )

# Result:
# - Each section fully embedded
# - All associations captured
# - Document structure preserved
# - Temporal ordering maintained
```

---

## Scenario 5: Ambiguous or Low-Quality Text

### Input
```python
client.learn_concept("thing stuff happens sometimes maybe")
```

### Processing Steps

#### Step 1: Embedding Generation
```
Input: "thing stuff happens sometimes maybe"
Output: [0.012, -0.034, 0.056, ..., -0.023]  # 768 dimensions
Latency: ~28ms
```

**Quality**: Low (generic words, no specificity)

#### Step 2: Semantic Analysis

```rust
SemanticMetadata {
    semantic_type: Unknown,  // ← No clear patterns matched
    
    temporal_bounds: Some(TemporalBounds {
        temporal_type: TemporalType::Imprecise,  // ← "sometimes"
        confidence: 0.35,  // ← Low confidence
    }),
    
    causal_relations: None,
    
    domain_context: None,  // ← No domain keywords
    
    negation_scope: None,
    
    classification_confidence: 0.12,  // ← Very low
}
```

**Pattern Matching Results**:
- No rule patterns matched
- No domain patterns matched
- "happens" suggests event but too vague
- "maybe" suggests uncertainty but no clear context

#### Step 3: Association Extraction

```rust
// Sentence: "thing stuff happens sometimes maybe"

// Extract entities
entities = []  // ← Nothing capitalized, no entities extracted

// Result: 0 associations
associations = []
```

#### Step 4: Storage

```rust
ConceptNode {
    id: e8f3a5b2c9d6e4f1,
    content: b"thing stuff happens sometimes maybe",
    strength: 1.0,
    confidence: 1.0,  // ← Still stored!
    semantic: Some(SemanticMetadata {
        semantic_type: Unknown,
        domain_context: None,
        classification_confidence: 0.12,
    }),
}

// No associations created
```

### What System Learned

```json
{
  "concept_id": "e8f3a5b2c9d6e4f1",
  "content": "thing stuff happens sometimes maybe",
  "semantic_type": "Unknown",
  "domain": null,
  "associations": [],
  "embedding": [768 dimensions with low information density],
  "queryable_via": [
    "Direct retrieval by concept_id",
    "Vector search (but low quality match)",
    "Filter: semantic_type=Unknown"
  ],
  "limitations": [
    "No graph connectivity (no associations)",
    "No semantic classification",
    "Low-quality embedding",
    "Poor semantic search results"
  ]
}
```

### System Behavior

**Key Point**: System never fails or rejects input. It extracts maximum value from whatever is provided.

```python
# Even bad input succeeds
concept_id = client.learn_concept("asdf qwer zxcv")
# Returns: valid concept_id

# But has minimal utility
neighbors = client.get_neighbors(concept_id)
# Returns: [] (no associations)

semantic_type = client.get_concept(concept_id).semantic_type
# Returns: "Unknown"
```

---

## Scenario 6: Contradictory Statements

### Input
```python
# First statement
id1 = client.learn_concept("Aspirin prevents blood clots.")

# Contradictory statement
id2 = client.learn_concept("Aspirin causes bleeding in some patients.")
```

### Processing

Both concepts learned independently:

```json
// Concept 1
{
  "concept_id": "f4e7b3a8c2d9f6e5",
  "content": "Aspirin prevents blood clots.",
  "semantic_type": "Causal",
  "causal_relations": [
    {"cause": "Aspirin", "effect": "prevents blood clots"}
  ]
}

// Concept 2
{
  "concept_id": "a9c5d2e8f1b6c7d4",
  "content": "Aspirin causes bleeding in some patients.",
  "semantic_type": "Causal",
  "causal_relations": [
    {"cause": "Aspirin", "effect": "bleeding"}
  ]
}
```

### Contradiction Detection

```python
# System can find contradictions
contradictions = client.find_contradictions(domain="Medical")

# Returns:
[
    {
        "concept_1": "f4e7b3a8c2d9f6e5",
        "concept_2": "a9c5d2e8f1b6c7d4",
        "conflict_type": "Causal",
        "explanation": "Aspirin has opposing effects (prevents vs causes)",
        "confidence": 0.78
    }
]
```

**How it works**:
1. Both concepts link to "Aspirin" entity
2. Causal analysis finds opposite effects
3. Flagged as potential contradiction
4. Human review recommended

---

## Summary Table

| Scenario | Embedding Quality | Associations | Semantic Type | Queryability | Best Practice |
|----------|------------------|--------------|---------------|-------------|---------------|
| **Simple fact** | High | 1 | Definitional | Good | Use as-is |
| **Multi-fact** | High | 1 | Rule | Very good | Consider splitting |
| **Complex narrative** | High | 5 | Event | Excellent | Use as-is |
| **Long document** | Low (truncated) | 10 (limited) | Rule | Partial | Chunk into sections |
| **Low-quality text** | Low | 0 | Unknown | Poor | Clean before ingesting |
| **Contradictions** | High (both) | Varies | Varies | Good (detected) | Use contradiction detection |

---

## Configuration for Different Content Types

### Short Facts (Scenario 1-2)
```python
# Default settings work well
client.learn_concept(content, options={
    "generate_embedding": True,
    "extract_associations": True,
    "min_association_confidence": 0.5,
    "max_associations_per_concept": 10,
})
```

### Complex Narratives (Scenario 3)
```python
# Increase association limits
client.learn_concept(content, options={
    "generate_embedding": True,
    "extract_associations": True,
    "min_association_confidence": 0.6,  # Higher quality
    "max_associations_per_concept": 20,  # More associations
})
```

### Long Documents (Scenario 4)
```python
# Chunk and process
sections = chunk_by_headers(document)
for section in sections:
    client.learn_concept(section, options={
        "max_associations_per_concept": 30,  # Capture more per section
    })
```

### Low-Quality Text (Scenario 5)
```python
# Pre-process before learning
cleaned = clean_text(raw_text)
if is_meaningful(cleaned):
    client.learn_concept(cleaned)
else:
    logger.warning("Text too low-quality, skipping")
```

---

## Monitoring Content Quality

```python
# After learning, check quality
concept = client.get_concept(concept_id)

# Quality indicators
quality_score = 0

if concept.semantic_type != "Unknown":
    quality_score += 30

if concept.domain_context is not None:
    quality_score += 20

if len(concept.associations) > 0:
    quality_score += 25

if concept.classification_confidence > 0.7:
    quality_score += 25

# quality_score: 0-100
# < 30: Very low quality
# 30-60: Moderate quality
# 60-80: Good quality
# > 80: Excellent quality

if quality_score < 30:
    logger.warning(f"Low quality concept: {concept_id}")
```

---

## Best Practices

1. **Chunk long documents** into logical sections (headers, paragraphs)
2. **Increase association limits** for complex content (20-50 instead of 10)
3. **Pre-filter low-quality** text before ingesting
4. **Use batch operations** for multiple related facts
5. **Monitor quality scores** after ingestion
6. **Structure hierarchically** (document → sections → facts)
7. **Leverage contradiction detection** for quality assurance
8. **Test with representative samples** before bulk ingestion

---

**Next**: [README.md](./README.md) | [Architecture](./ARCHITECTURE.md) | [Scenarios](./SCENARIOS.md)
