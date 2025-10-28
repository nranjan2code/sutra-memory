# What Actually Happens By Text Size

**This document shows EXACTLY what the system does with different text sizes. No suggestions, just facts.**

---

## Understanding Edition Limits First

```
┌──────────────────────────────────────────────────────────────┐
│ YOUR EDITION DETERMINES MAXIMUM TEXT LENGTH                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Simple Edition:      512 characters  = ~100 words           │
│ Community Edition:   1024 characters = ~200 words           │
│ Enterprise Edition:  2048 characters = ~400 words           │
│                                                              │
│ Code location: packages/sutra-embedding-service/main.py     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Key Fact**: If your text exceeds your edition limit, the embedding service returns:
```
HTTPException(status_code=422, detail="Text length exceeds edition limit")
```

---

## Example 1: Short Text - "Humans are mammals" (19 characters)

### Works in ALL Editions ✅

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Simple | 512 chars | 19 chars | ✅ Success |
| Community | 1024 chars | 19 chars | ✅ Success |
| Enterprise | 2048 chars | 19 chars | ✅ Success |

### What Happens:

```
Step 1: Embedding Service
  Input: "Humans are mammals" (19 chars)
  Check: 19 < 512 (Simple limit) ✅ Pass
  Output: [0.023, -0.145, ..., 0.234] (768 numbers)

Step 2: Semantic Analysis
  Type: Definitional
  Domain: Scientific
  Confidence: 85%

Step 3: Extract Connections
  Found: "Humans" (capitalized word)
  Type: Semantic connection
  Confidence: 78%

Step 4: Storage
  ┌─────────────────────────────────┐
  │ Concept ID: a3f2c8d1            │
  │ Content: "Humans are mammals"   │
  │ Embedding: ✅ Stored (768D)     │
  │ Connections: 1                  │
  │   - "Humans" (78%)              │
  └─────────────────────────────────┘

Result: ✅ Fully searchable concept
```

---

## Example 2: Medium Text - Diabetes Sentence (120 characters)

```
"Diabetes requires regular blood glucose monitoring and affects insulin production in the pancreas."
```

### Works in ALL Editions ✅

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Simple | 512 chars | 120 chars | ✅ Success |
| Community | 1024 chars | 120 chars | ✅ Success |
| Enterprise | 2048 chars | 120 chars | ✅ Success |

### What Happens:

```
Step 1: Embedding Service
  Input: 120 characters
  Check: 120 < 512 ✅ Pass
  Output: [0.156, -0.089, ..., -0.145] (768 numbers)

Step 2: Semantic Analysis
  Type: Rule
  Domain: Medical
  Causal: Diabetes → insulin production
  Confidence: 92%

Step 3: Extract Connections
  Found: "Diabetes"
  Type: Semantic
  Confidence: 82%

Step 4: Storage
  ┌─────────────────────────────────┐
  │ Concept ID: b8e4d9f2            │
  │ Content: [full 120 chars]       │
  │ Embedding: ✅ Stored (768D)     │
  │ Causal: Diabetes → insulin      │
  │ Connections: 1                  │
  │   - "Diabetes" (82%)            │
  └─────────────────────────────────┘

Result: ✅ Fully searchable concept
```

---

## Example 3: Long Paragraph (600 characters)

```
"On January 15, 2024, Patient Smith was diagnosed with Type 2 Diabetes after 
presenting with elevated blood glucose levels. The diagnosis led to immediate 
changes in treatment protocol. Dr. Johnson prescribed Metformin and recommended 
lifestyle modifications including diet and exercise. The patient was scheduled 
for follow-up appointments every two weeks to monitor progress and adjust 
medication dosages as needed. Initial HbA1c levels were measured at 8.2%, 
indicating poor glycemic control. A comprehensive treatment plan was developed."
```

### What Happens BY EDITION:

#### Simple Edition (512 char limit):

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Simple | 512 chars | 600 chars | ❌ FAILS |

```
Step 1: Embedding Service
  Input: 600 characters
  Check: 600 > 512 ❌ FAIL
  Error: HTTPException(422, "Text length 600 exceeds edition limit of 512")

Step 2: Storage Server Receives Error
  Code: learning_pipeline.rs line 74-77
  
  match self.embedding_client.generate(content).await {
      Err(e) => {
          warn!("Embedding failed, continuing without: {}", e);
          None  // ← NO EMBEDDING!
      }
  }

Step 3: Semantic Analysis (Still Works!)
  Type: Event
  Domain: Medical
  Time: 2024-01-15
  Confidence: 94%

Step 4: Extract Connections (Still Works!)
  Found: "Patient Smith", "Type 2 Diabetes", "Dr", "Johnson", "Metformin"
  Takes top 10 (default limit)

Step 5: Storage
  ┌─────────────────────────────────┐
  │ Concept ID: c9d3e5f1            │
  │ Content: ✅ All 600 chars saved │
  │ Embedding: ❌ None (too long)   │
  │ Semantic: ✅ Full analysis      │
  │ Connections: 5 entities         │
  └─────────────────────────────────┘

Result: ⚠️ Concept stored but NOT vector-searchable
```

#### Community Edition (1024 char limit):

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Community | 1024 chars | 600 chars | ✅ Success |

```
Step 1: Embedding Service
  Input: 600 characters
  Check: 600 < 1024 ✅ Pass
  Output: [0.234, 0.089, ..., 0.145] (768 numbers)

Step 2-5: [Same as Example 2]

Result: ✅ Fully searchable concept
```

#### Enterprise Edition (2048 char limit):

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Enterprise | 2048 chars | 600 chars | ✅ Success |

```
Step 1: Embedding Service
  Input: 600 characters
  Check: 600 < 2048 ✅ Pass
  Output: [0.234, 0.089, ..., 0.145] (768 numbers)

Result: ✅ Fully searchable concept
```

---

## Example 4: Full Document (25,000 characters = 5000 words)

```
CLINICAL PROTOCOL FOR TYPE 2 DIABETES MANAGEMENT

1. INTRODUCTION
[... 25,000 characters total ...]
```

### What Happens IN ALL EDITIONS:

| Edition | Limit | Your Text | Result |
|---------|-------|-----------|--------|
| Simple | 512 chars | 25,000 chars | ❌ FAILS |
| Community | 1024 chars | 25,000 chars | ❌ FAILS |
| Enterprise | 2048 chars | 25,000 chars | ❌ FAILS |

**All editions fail because 25,000 >> 2048**

```
Step 1: Embedding Service (ALL EDITIONS)
  Input: 25,000 characters
  Check: 25,000 > 2048 ❌ FAIL
  Error: HTTPException(422, "Text length 25000 exceeds edition limit of 2048")

Step 2: Storage Server Receives Error
  warn!("Embedding failed, continuing without");
  embedding = None

Step 3: Semantic Analysis (Still Works!)
  Processes full 25,000 characters
  Type: Rule
  Domain: Medical
  Multiple causal chains
  Confidence: 96%

Step 4: Extract Connections (Partial)
  Finds 100+ entities across document
  Takes only top 10 (default limit)

Step 5: Storage
  ┌─────────────────────────────────────┐
  │ Concept ID: d7e2f4a9                │
  │ Content: ✅ All 25,000 chars saved  │
  │ Embedding: ❌ None (too long)       │
  │ Semantic: ✅ Full analysis          │
  │ Connections: Only 10 of 100+        │
  └─────────────────────────────────────┘

Result: ⚠️ Concept stored but NOT vector-searchable
         ⚠️ Missing most entity connections
```

---

## Summary Table: What Works Where

| Text Size | Characters | Simple | Community | Enterprise | Embedding? | Searchable? |
|-----------|------------|--------|-----------|------------|------------|-------------|
| 1 sentence | ~20 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 1 paragraph | ~200 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2-3 paragraphs | ~500 | ❌ | ✅ | ✅ | ✅/❌ | ✅/❌ |
| 4-5 paragraphs | ~900 | ❌ | ✅ | ✅ | ✅/❌ | ✅/❌ |
| 6-8 paragraphs | ~1500 | ❌ | ❌ | ✅ | ❌/✅ | ❌/✅ |
| Full document | 2000+ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend:**
- ✅ = Works
- ❌ = Fails (no embedding)
- ✅/❌ = Depends on your edition

---

## Key Facts (Not Suggestions)

### Fact 1: Edition Limits Are Hard Limits
```
Code: packages/sutra-embedding-service/main.py (lines 257-260)

if len(text) > max_length:
    raise HTTPException(
        status_code=422,
        detail=f"Text exceeds edition limit of {max_length}"
    )
```

### Fact 2: Storage Server Continues Without Embedding
```
Code: packages/sutra-storage/src/learning_pipeline.rs (lines 74-77)

match self.embedding_client.generate(content).await {
    Ok(vec) => Some(vec),
    Err(e) => {
        warn!("Embedding failed, continuing without: {}", e);
        None  // ← Concept stored with NO embedding
    }
}
```

### Fact 3: No Embedding = No Vector Search
Without embedding vector, these queries DON'T work:
- ❌ `client.vector_search("find similar documents")`
- ❌ `client.semantic_search("meaning-based search")`

These queries STILL work:
- ✅ `client.get_concept(concept_id)` - Direct retrieval
- ✅ `client.query_by_semantic(filter={type="Rule"})` - Metadata filters
- ✅ `client.find_causal_chain(...)` - Graph traversal
- ✅ `client.get_neighbors(concept_id)` - Connection traversal

### Fact 4: Connection Limit is 10 by Default
```
Code: packages/sutra-storage/src/learning_pipeline.rs (line 122)

for assoc in extracted.into_iter().take(options.max_associations_per_concept)
// default: max_associations_per_concept = 10
```

For documents with 100+ entities, only top 10 by confidence are stored.

---

## What This Means For You

### If You Have Simple Edition (512 chars):
- ✅ Good for: Single facts, short statements
- ⚠️ Limited for: Multi-sentence paragraphs
- ❌ Bad for: Long paragraphs, documents

### If You Have Community Edition (1024 chars):
- ✅ Good for: Single facts, paragraphs
- ⚠️ Limited for: Multi-paragraph content
- ❌ Bad for: Full documents

### If You Have Enterprise Edition (2048 chars):
- ✅ Good for: Facts, paragraphs, short sections
- ⚠️ Limited for: Long sections
- ❌ Bad for: Full documents (still need chunking)

### For Long Documents (ALL EDITIONS):
**You MUST chunk into sections < 400 words each**

This is not a suggestion. This is the only way to get:
- ✅ Embeddings for all content
- ✅ Full entity connections
- ✅ Vector search capability

---

## Example: Chunking a Document

Instead of this ❌:
```python
# Sends 25,000 characters
client.learn_concept(full_document)
# Result: No embedding, limited connections
```

Do this ✅:
```python
# Split document into 10 sections of ~2000 chars each
sections = split_by_headers(full_document)

for section in sections:
    client.learn_concept(section)  # Each < 2000 chars
# Result: All sections fully embedded and connected
```

This is not a best practice - **this is the ONLY way it works for long documents**.

---

**Related**: [Natural Language Scenarios](./NATURAL_LANGUAGE_SCENARIOS.md) | [Architecture](./ARCHITECTURE.md)
