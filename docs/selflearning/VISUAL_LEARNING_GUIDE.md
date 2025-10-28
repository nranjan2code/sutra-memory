# Visual Learning Guide: How Text Gets Structured

**This document shows EXACTLY what happens when you feed different text sizes into sutra-storage**

> **Important**: This is NOT a guide of what you should do. This is a description of what ACTUALLY HAPPENS in the system based on the code.

---

## System Configuration: Edition Limits

**Before we start - understand these HARD LIMITS in the code:**

```python
# From: packages/sutra-embedding-service/main.py (lines 58-76)

EDITION_LIMITS = {
    "simple": {
        "max_text_length": 512,        # 512 characters = ~100 words
    },
    "community": {
        "max_text_length": 1024,       # 1024 characters = ~200 words
    },
    "enterprise": {
        "max_text_length": 2048,       # 2048 characters = ~400 words
    }
}

# If text exceeds limit:
if len(text) > max_length:
    raise HTTPException(status_code=422, detail="Text exceeds edition limit")
```

**What this means:**
- If you have **Simple edition** and send 600 characters → **REJECTED**
- If you have **Community edition** and send 1500 characters → **REJECTED**
- If you have **Enterprise edition** and send 3000 characters → **REJECTED**

**The system does NOT truncate. It REJECTS.**

---

### Input
```
"Humans are mammals."
```

### What Happens

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: "Humans are mammals."                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Generate Embedding (768 numbers)                    │
│ [0.023, -0.145, 0.089, ..., 0.234]                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Analyze Meaning                                     │
│ • Type: Definitional ("are" = definition)                   │
│ • Domain: Scientific ("mammals" = science term)             │
│ • Confidence: 85%                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Extract Connections                                 │
│ • Found entity: "Humans" (capitalized)                      │
│ • Connection type: Semantic                                 │
│ • Confidence: 78%                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STORED AS SINGLE CONCEPT                                    │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │ Concept ID: a3f2c8d1                        │           │
│  │ Content: "Humans are mammals."              │           │
│  │ Type: Definitional                          │           │
│  │ Domain: Scientific                          │           │
│  │ Embedding: [768 dimensions]                 │           │
│  │                                             │           │
│  │ Connections:                                │           │
│  │   → "Humans" (78% confidence)               │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Queryable By
- 🔍 Search: "what are humans"
- 🏷️ Filter: Type = Definitional
- 🏷️ Filter: Domain = Scientific
- 🔗 Graph: From "Humans" concept

**Storage**: 1 concept, 1 connection

---

## 2. Multiple Sentences → Single Concept with Multiple Connections

### Input
```
"Diabetes requires regular blood glucose monitoring and affects 
insulin production in the pancreas."
```

### What Happens

```
┌──────────────────────────────────────────────────────────────┐
│ INPUT: Long sentence with multiple facts                     │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Generate Embedding                                   │
│ [0.156, -0.089, 0.234, ..., -0.145]                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Analyze Meaning                                      │
│ • Type: Rule ("requires" = requirement)                      │
│ • Domain: Medical (multiple medical terms)                   │
│ • Causal: Diabetes → affects insulin                         │
│ • Confidence: 92%                                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Extract Connections                                  │
│ • Found: "Diabetes" (capitalized)                            │
│ • Connection: Semantic (82%)                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STORED AS SINGLE CONCEPT                                     │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │ Concept ID: b8e4d9f2                           │         │
│  │ Content: "Diabetes requires regular blood..."  │         │
│  │ Type: Rule                                     │         │
│  │ Domain: Medical                                │         │
│  │ Embedding: [768 dimensions]                    │         │
│  │                                                │         │
│  │ Causal Chain:                                  │         │
│  │   Diabetes → insulin production                │         │
│  │                                                │         │
│  │ Connections:                                   │         │
│  │   → "Diabetes" (82% confidence)                │         │
│  └────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

### Queryable By
- 🔍 Search: "diabetes management"
- 🏷️ Filter: Type = Rule, Domain = Medical
- 🔗 Causal: Diabetes → effects
- 🔗 Graph: From "Diabetes" concept

**Storage**: 1 concept, 1 connection, 1 causal chain

---

## 3. Paragraph → Single Concept with Rich Metadata

### Input
```
"On January 15, 2024, Patient Smith was diagnosed with Type 2 
Diabetes after presenting with elevated blood glucose levels. 
The diagnosis led to immediate changes in treatment protocol. 
Dr. Johnson prescribed Metformin and recommended lifestyle 
modifications including diet and exercise."
```

### What Happens

```
┌──────────────────────────────────────────────────────────────────┐
│ INPUT: Paragraph with timeline, people, drugs, actions          │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Generate Embedding                                       │
│ [0.234, 0.089, -0.156, ..., 0.145]                              │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Analyze Meaning                                          │
│ • Type: Event ("diagnosed", "prescribed" = events)               │
│ • Domain: Medical                                                │
│ • Time: January 15, 2024 (extracted from text)                   │
│ • Causal Chain: glucose → diagnosis → treatment                  │
│ • Confidence: 94%                                                │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Extract Connections (from 3 sentences)                   │
│                                                                  │
│ Sentence 1: "On January 15, 2024, Patient Smith was..."         │
│   → "Patient Smith" (Causal, 88%)                                │
│   → "Type 2 Diabetes" (Causal, 88%)                              │
│                                                                  │
│ Sentence 2: "The diagnosis led to immediate changes..."          │
│   → (no capitalized entities)                                    │
│                                                                  │
│ Sentence 3: "Dr. Johnson prescribed Metformin..."                │
│   → "Dr" (Semantic, 72%)                                         │
│   → "Johnson" (Semantic, 72%)                                    │
│   → "Metformin" (Semantic, 72%)                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ STORED AS SINGLE CONCEPT                                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Concept ID: c9d3e5f1                                   │     │
│  │ Content: "On January 15, 2024, Patient Smith was..." │     │
│  │ Type: Event                                            │     │
│  │ Domain: Medical                                        │     │
│  │ Time: 2024-01-15                                       │     │
│  │ Embedding: [768 dimensions]                            │     │
│  │                                                        │     │
│  │ Causal Chain:                                          │     │
│  │   glucose → diagnosis → treatment                      │     │
│  │                                                        │     │
│  │ Connections: (5 total)                                 │     │
│  │   → "Patient Smith" (88%)                              │     │
│  │   → "Type 2 Diabetes" (88%)                            │     │
│  │   → "Dr" (72%)                                         │     │
│  │   → "Johnson" (72%)                                    │     │
│  │   → "Metformin" (72%)                                  │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

### Queryable By
- 🔍 Search: "diabetes diagnosis"
- 📅 Time: Events on 2024-01-15
- 🔗 Causal: glucose → diabetes → treatment chain
- 🏷️ Filter: Type = Event, Domain = Medical
- 🔗 Graph: From "Patient Smith", "Metformin", etc.

**Storage**: 1 concept, 5 connections, 2 causal relations, 1 temporal marker

---

## 4. Multiple Paragraphs → Trade-offs with Single Concept

### Input (5000 words, multiple pages)
```
CLINICAL PROTOCOL FOR TYPE 2 DIABETES MANAGEMENT

1. INTRODUCTION
Type 2 Diabetes Mellitus is a metabolic disorder...

2. DIAGNOSIS CRITERIA
Patients must meet one of the following criteria:
- Fasting plasma glucose ≥ 126 mg/dL
- 2-hour plasma glucose ≥ 200 mg/dL during OGTT
...

3. TREATMENT PROTOCOL
3.1 First-Line Therapy
Metformin is the preferred initial medication...

[... 4500 more words ...]
```

### ⚠️ Trade-offs: Single Concept Approach

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: 5000-word document (25,000 characters)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Generate Embedding                                  │
│                                                             │
│ Edition Limits (from embedding service):                    │
│ • Simple:     512 chars max                                 │
│ • Community:  1024 chars max                                │
│ • Enterprise: 2048 chars max                                │
│                                                             │
│ ⚠️  Your Edition: Enterprise (2048 char limit)              │
│ ⚠️  Document length: 25,000 chars                           │
│ ⚠️  REJECTED: Text exceeds edition limit!                   │
│                                                             │
│ Result: HTTPException 422 (Unprocessable Entity)            │
│ "Text length 25000 exceeds edition limit of 2048"          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM BEHAVIOR: Embedding generation fails                 │
│                                                             │
│ In learning_pipeline.rs (line 74-77):                       │
│   match self.embedding_client.generate(content).await {     │
│       Ok(vec) => Some(vec),                                 │
│       Err(e) => {                                           │
│           warn!("Embedding failed, continuing without");    │
│           None   // ← Continues WITHOUT embedding           │
│       }                                                     │
│   }                                                         │
│                                                             │
│ Concept is stored WITHOUT embedding vector!                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Analyze Meaning                                     │
│ ✓  Processes FULL document (no length limit)                │
│ • Type: Rule                                                │
│ • Domain: Medical                                           │
│ • Multiple causal chains found                              │
│ • Confidence: 94%                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Extract Connections                                 │
│ ✓  Finds many entities across full document                 │
│ ⚠️  But only stores TOP 10 by default!                      │
│                                                             │
│ In learning_pipeline.rs (line 122):                         │
│   for assoc in extracted                                    │
│       .into_iter()                                          │
│       .take(options.max_associations_per_concept)  // ← 10  │
│                                                             │
│ • 50+ entities found                                        │
│ • Only 10 stored (configurable via options)                 │
│                                                             │
│ Environment variable:                                       │
│   SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=10 (default)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STORED AS SINGLE CONCEPT (With Limitations)                 │
│                                                             │
│  ┌────────────────────────────────────────────────┐        │
│  │ Concept ID: d7e2f4a9                           │        │
│  │ Content: [Full 25,000 bytes stored ✓]         │        │
│  │ Type: Rule                                     │        │
│  │ Domain: Medical                                │        │
│  │ Embedding: None ✗ (failed due to length)      │        │
│  │                                                │        │
│  │ Semantic Metadata: ✓ (full document)           │        │
│  │ Causal Chains: ✓ (extracted from full doc)    │        │
│  │                                                │        │
│  │ Connections: [Only 10 of 50+ ✗]               │        │
│  │   → Top 10 by confidence                       │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│ WHAT WORKS:                                                 │
│ ✓ Full content stored and retrievable by ID                │
│ ✓ Semantic classification (type, domain)                   │
│ ✓ Causal chain analysis                                    │
│ ✓ Full-text search (if implemented)                        │
│                                                             │
│ WHAT DOESN'T WORK:                                          │
│ ✗ Vector similarity search (no embedding!)                 │
│ ✗ Graph traversal (limited to 10 connections)              │
│ ✗ Finding similar documents by meaning                     │
│ ✗ Connecting to entities beyond top 10                     │
└─────────────────────────────────────────────────────────────┘
```

### Real System Behavior

**Edition limits are ENFORCED by embedding service:**
- Simple: 512 characters max
- Community: 1024 characters max  
- Enterprise: 2048 characters max

**What happens with 5000-word document:**
1. Embedding service **rejects** the text (422 error)
2. Storage server **continues** without embedding (warning logged)
3. Concept stored with semantic metadata but NO vector
4. Only top 10 associations stored (default limit)

**Result**: Concept exists but has limited queryability

---

## 5. Multiple Paragraphs → ✅ Solution: Chunk into Sections

### Why Chunking is Necessary

**Hard Limits in the System:**
1. **Embedding service rejects long text** (512-2048 chars based on edition)
2. **Association limit** (default 10 per concept)
3. **Vector search requires embeddings** (no embedding = not searchable)

### Better Approach: Break Document into Logical Sections

```
┌──────────────────────────────────────────────────────────────┐
│ INPUT: 5000-word document                                    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ PREPROCESSING: Split by headers                              │
│                                                              │
│ Section 1: "INTRODUCTION..."                 (500 words)    │
│ Section 2: "DIAGNOSIS CRITERIA..."           (800 words)    │
│ Section 3: "TREATMENT PROTOCOL..."           (1200 words)   │
│ Section 4: "LIFESTYLE MODIFICATIONS..."      (600 words)    │
│ Section 5: "MONITORING AND FOLLOW-UP..."     (900 words)    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ LEARN EACH SECTION SEPARATELY                                │
└──────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┬───────────────────┬───────────────────┐
        ↓                   ↓                   ↓                   ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Concept 1    │    │ Concept 2    │    │ Concept 3    │    │ Concept 4    │
│ Introduction │    │ Diagnosis    │    │ Treatment    │    │ Lifestyle    │
│              │    │              │    │              │    │              │
│ Embedding ✓  │    │ Embedding ✓  │    │ Embedding ✓  │    │ Embedding ✓  │
│ 15 entities  │    │ 22 entities  │    │ 28 entities  │    │ 18 entities  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ CREATE DOCUMENT HIERARCHY                                    │
│                                                              │
│        ┌─────────────────────────────────────┐              │
│        │  Document Root                      │              │
│        │  "Type 2 Diabetes Protocol"         │              │
│        │  (No embedding, just structure)     │              │
│        └─────────────────────────────────────┘              │
│                       │                                      │
│          ┌────────────┼────────────┬─────────────┐          │
│          ↓            ↓            ↓             ↓          │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│    │Section 1│  │Section 2│  │Section 3│  │Section 4│     │
│    │  (500w) │  │  (800w) │  │ (1200w) │  │  (600w) │     │
│    └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
│                                                              │
│ Connection Type: Compositional                               │
│ (Document "contains" sections)                               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ LINK SECTIONS SEQUENTIALLY                                   │
│                                                              │
│  Section 1 ──[next]──> Section 2 ──[next]──> Section 3      │
│                                                              │
│ Connection Type: Temporal                                    │
│ (Reading order preserved)                                    │
└──────────────────────────────────────────────────────────────┘
```

### Final Structure in Storage

```
Document Graph:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                   ┌──────────────┐                          │
│                   │   Document   │                          │
│                   │     Root     │                          │
│                   └──────┬───────┘                          │
│                          │                                  │
│            ┌─────────────┼─────────────┬─────────────┐     │
│            │             │             │             │     │
│     ┌──────▼────┐ ┌──────▼────┐ ┌──────▼────┐ ┌────▼─────┐│
│     │Section 1  │ │Section 2  │ │Section 3  │ │Section 4 ││
│     │Intro      │ │Diagnosis  │ │Treatment  │ │Lifestyle ││
│     └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └────┬─────┘│
│           │             │             │             │      │
│    ┌──────┴─────┐ ┌─────┴─────┐ ┌────┴──────┐ ┌────┴─────┐│
│    │Entities:   │ │Entities:  │ │Entities:  │ │Entities: ││
│    │• Diabetes  │ │• Glucose  │ │• Metformin│ │• Diet    ││
│    │• Insulin   │ │• OGTT     │ │• Insulin  │ │• Exercise││
│    │• Pancreas  │ │• HbA1c    │ │• Dosage   │ │• Weight  ││
│    │  (15 more) │ │  (20 more)│ │  (26 more)│ │ (16 more)││
│    └────────────┘ └───────────┘ └───────────┘ └──────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘

Benefits:
✅ All content fully embedded (no truncation)
✅ All entities captured (no 10-connection limit per concept)
✅ Document structure preserved
✅ Sequential reading order maintained
✅ Better search results (specific sections)
✅ Better graph connectivity (more connections)
```

### Queryable By

```python
# 1. Find entire document
doc = client.vector_search("diabetes treatment protocol")
# Returns: Document root or relevant sections

# 2. Find specific section
section = client.vector_search("DASH diet recommendations")
# Returns: Section 4 (Lifestyle) - not truncated!

# 3. Navigate structure
sections = client.get_neighbors(document_id, filter="Compositional")
# Returns: All 4 sections

# 4. Follow reading order
next_section = client.get_neighbors(section1_id, filter="Temporal")
# Returns: Section 2 (next in sequence)

# 5. Find all mentions of entity
mentions = client.get_neighbors(entity_id("Metformin"))
# Returns: Section 3, possibly Section 4
```

**Storage**: 
- 1 document concept
- 4 section concepts (fully embedded)
- 83+ entity connections total
- 4 compositional connections (document → sections)
- 3 temporal connections (section order)

---

## 6. Full Document → Complete Code Example

### Input Processing

```python
def learn_document_properly(client, document: str, title: str):
    """
    Learn a long document by chunking into sections
    """
    
    # 1. Split document by headers
    sections = split_by_headers(document)
    # Returns: [
    #   ("INTRODUCTION", "Type 2 Diabetes Mellitus is..."),
    #   ("DIAGNOSIS CRITERIA", "Patients must meet..."),
    #   ("TREATMENT PROTOCOL", "Metformin is the preferred..."),
    #   ...
    # ]
    
    # 2. Learn each section (parallel for speed)
    section_ids = []
    for header, content in sections:
        full_text = f"{header}\n\n{content}"
        
        concept_id = client.learn_concept(
            content=full_text,
            options={
                "max_associations_per_concept": 30,  # More per section
                "min_association_confidence": 0.6,   # Higher quality
            }
        )
        section_ids.append((header, concept_id))
    
    # 3. Create document root (no embedding needed)
    doc_id = client.learn_concept(
        content=f"Document: {title}",
        options={
            "generate_embedding": False,
            "extract_associations": False,
        }
    )
    
    # 4. Link sections to document (structure)
    for header, section_id in section_ids:
        client.learn_association(
            source_id=doc_id,
            target_id=section_id,
            association_type="Compositional",
            confidence=1.0,
            metadata={"role": "section", "title": header}
        )
    
    # 5. Link sections sequentially (reading order)
    for i in range(len(section_ids) - 1):
        client.learn_association(
            source_id=section_ids[i][1],
            target_id=section_ids[i+1][1],
            association_type="Temporal",
            confidence=1.0,
            metadata={"role": "next_section"}
        )
    
    return doc_id, section_ids
```

### Querying the Document

```python
# Find document
doc_id = client.vector_search("diabetes protocol")[0].concept_id

# Get all sections
sections = client.get_neighbors(
    doc_id, 
    filter={"association_type": "Compositional"}
)

# Get first section
first_section = sections[0]

# Follow reading order
current = first_section
while True:
    next_sections = client.get_neighbors(
        current,
        filter={"association_type": "Temporal", "role": "next_section"}
    )
    if not next_sections:
        break
    current = next_sections[0]
    print(f"Section: {current.content[:50]}")
```

---

## Comparison Summary

| Text Size | Approach | Concepts | Embedding | Connections | Issues | Queryability |
|-----------|----------|----------|-----------|-------------|--------|-------------|
| **1 Sentence** | Single concept | 1 | ✅ Works | 1 | None | ✅ Good |
| **1 Paragraph** | Single concept | 1 | ✅ Works | 5 | None | ✅ Excellent |
| **Multi-Paragraph** | Single concept | 1 | ⚠️ May fail | 10 (limited) | Length limits | ⚠️ Poor |
| **Long Document** | Single concept | 1 | ❌ Fails (too long) | 10 (limited) | No embedding! | ❌ Very Poor |
| **Long Document** | **Chunked** | 5+ | ✅ All sections | 30+ per section | None | ✅ Excellent |

### Why Long Documents Fail

**Edition Limits (Character Limits):**
```
Simple:     512 characters  (~100 words)
Community:  1024 characters (~200 words)  
Enterprise: 2048 characters (~400 words)
```

**A 5000-word document = ~25,000 characters**
- 48× larger than Simple limit
- 24× larger than Community limit
- 12× larger than Enterprise limit

**What Happens:**
1. Embedding service **rejects** text with 422 error
2. Storage server **continues** without embedding (warning logged)
3. Concept stored but **NOT vector-searchable**
4. Only 10 connections stored (missing most entities)

**The Solution:**
Chunk documents into sections < 400 words each:
- ✅ Each section gets its own embedding
- ✅ Each section gets 30+ connections
- ✅ Document structure preserved
- ✅ Full graph connectivity

---

## Decision Tree: How to Learn Your Content

```
What's your text length?

< 100 words (Enterprise) or < 50 words (Community)?
├─ YES: ✅ Use single concept
│   └─> client.learn_concept(text)
│
└─ NO: It's too long for embedding service

    Chunk into smaller sections:
    1. Split by headers/paragraphs
    2. Keep each section < 400 words
    3. Learn each section separately
    4. Create document hierarchy
    5. Link sections together
```

### Practical Limits by Edition

| Edition | Char Limit | Word Limit | What Fits |
|---------|-----------|------------|-----------|
| Simple | 512 | ~100 words | 1-2 paragraphs |
| Community | 1024 | ~200 words | 3-4 paragraphs |
| Enterprise | 2048 | ~400 words | 6-8 paragraphs |
| **Any Long Doc** | — | — | **Must chunk!** |
    └─ NO: It's a long document
        └─> Chunk by sections
            1. Split by headers/paragraphs
            2. Learn each section
            3. Create document hierarchy
            4. Link sections together
```

---

## Visual: Storage Structure Comparison

### ❌ Wrong: Single Concept for Long Document

```
┌────────────────────────────────────────┐
│ One Massive Concept                    │
│                                        │
│ • 25,000 chars content ✓ (stored)     │
│ • Embedding: None ✗ (too long!)       │
│ • 10 connections ✗ (missing 40+)      │
│ • No structure ✗                       │
│ • NOT searchable by meaning ✗         │
│                                        │
│ Result: Dead-end concept              │
└────────────────────────────────────────┘
```

### ✅ Right: Chunked with Hierarchy

```
                  ┌──────────┐
                  │ Document │
                  │   Root   │
                  └────┬─────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌───▼─────┐
    │Section 1│   │Section 2│   │Section 3│
    │  (800B) │   │  (900B) │   │ (1100B) │
    │         │   │         │   │         │
    │ Embed ✓ │   │ Embed ✓ │   │ Embed ✓ │
    │ 15 conn │   │ 22 conn │   │ 28 conn │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
    ┌────▼──────┐ ┌───▼──────┐ ┌────▼──────┐
    │ Entities  │ │ Entities │ │ Entities  │
    │ Graph     │ │ Graph    │ │ Graph     │
    └───────────┘ └──────────┘ └───────────┘

Result: Excellent search, rich graph, preserved structure
```

---

## Key Takeaways

### ⚠️ Critical Understanding

**The system ENFORCES text length limits at the embedding service level:**

```
┌─────────────────────────────────────────────────────┐
│ EDITION LIMITS (Hard Limits, Not Suggestions)      │
├─────────────────────────────────────────────────────┤
│ Simple:      512 characters  = ~100 words           │
│ Community:   1024 characters = ~200 words           │
│ Enterprise:  2048 characters = ~400 words           │
│                                                     │
│ Exceeding limit = HTTPException 422                 │
│ "Text length exceeds edition limit"                │
└─────────────────────────────────────────────────────┘
```

**What this means:**
- ❌ You **cannot** embed a 5000-word document as one concept
- ⚠️ System continues without embedding (logs warning)
- ✅ Concept stored but NOT searchable by meaning
- ✅ Solution: Chunk into sections < 400 words each

### Quick Rules

| Text Length | Action | Why |
|-------------|--------|-----|
| < 100 words | ✅ Single concept | Fits in all editions |
| 100-200 words | ✅ Single (Community+) | Fits in Community/Enterprise |
| 200-400 words | ✅ Single (Enterprise) | Fits only in Enterprise |
| > 400 words | ⚠️ **Must chunk** | Exceeds ALL edition limits |

### Design Principles

1. **Short text**: Single concept works perfectly
2. **Medium text**: Check your edition limit first
3. **Long documents**: ALWAYS chunk into sections
4. **Embedding = Searchability**: No embedding = no vector search
5. **Connections matter**: Default 10 per concept (increase for sections)
6. **Structure preserves meaning**: Document → Sections → Entities
7. **Test with your edition**: Know your character limits

### Common Mistakes to Avoid

❌ **Trying to learn 5000-word document as single concept**
   - Embedding fails silently (warning logged)
   - Stored without vector = not searchable

❌ **Ignoring edition limits**
   - Simple: 512 chars is VERY small
   - Community: 1024 chars is still limited
   - Enterprise: 2048 chars = only ~2-3 paragraphs

❌ **Not chunking long documents**
   - Results in disconnected concepts
   - Poor graph connectivity
   - Limited queryability

✅ **Always chunk documents > 400 words**
   - Each section fully embedded
   - Rich graph connectivity
   - Excellent searchability

---

**Related**: [Natural Language Scenarios](./NATURAL_LANGUAGE_SCENARIOS.md) | [Architecture](./ARCHITECTURE.md) | [Quick Reference](./QUICK_REFERENCE.md)
