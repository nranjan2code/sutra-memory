# Architectural Policy: No Traditional Query Languages

**Status:** Core Architectural Decision  
**Created:** 2025-01-16  
**Last Updated:** 2025-01-16

## Policy Statement

**Sutra will NEVER support SQL, Cypher, or GraphQL.**

This is not a limitation - it's an intentional architectural decision that enables our unique value proposition.

## Why No SQL/Cypher/GraphQL?

### 1. Different Problem Space
Traditional query languages were designed for **known schema** and **structured queries**:
- SQL: Relational tables with fixed schemas
- Cypher: Graph pattern matching with predefined relationships  
- GraphQL: API queries over known type systems

Sutra solves a **different problem**: reasoning over dynamic, self-learning knowledge graphs where:
- Schema evolves continuously
- Relationships emerge from data
- Queries are exploratory, not predetermined

### 2. Natural Language is Superior for Our Use Case

**Traditional approach:**
```cypher
// Neo4j Cypher
MATCH (p:Person)-[:WORKS_AT]->(c:Company)
WHERE c.industry = 'Healthcare'
RETURN p.name, c.name
```

**Sutra approach:**
```
"Who works at healthcare companies?"
```

Benefits:
- **Domain experts** don't need query language training
- **Compliance officers** can audit in plain English
- **Reasoning chains** are human-readable for explainability
- **Query evolution** doesn't break when schema changes

### 3. TCP Binary Protocol Advantages

Instead of SQL/Cypher/GraphQL, we use:

**Protocol:** MessagePack-based binary TCP (port 7000)  
**Client:** `sutra-storage-client-tcp` Rust library  
**Operations:** 
- `LearnConcept` - Add knowledge atomically
- `QueryGraph` - Natural language reasoning
- `GetConcept` - Retrieve by ID
- `UpdateConcept` - Modify existing knowledge

**Performance:**
- 10-50x lower latency than HTTP+JSON
- Zero parsing overhead (binary protocol)
- Connection pooling for high throughput
- Async I/O throughout stack

### 4. Self-Learning Requirements

SQL/Cypher require **schema migrations**:
```sql
ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10);
```

Sutra **learns dynamically**:
```rust
storage.learn_concept("User Alice prefers Spanish").await?;
// Schema evolves automatically, no migrations
```

This is incompatible with rigid query languages that expect stable schemas.

## What About Database Adapters?

**Question:** Why do we have SQL adapters in `sutra-core/adapters/`?

**Answer:** These are **ingestion adapters** for reading FROM external source systems:

```python
# This is VALID - reading FROM PostgreSQL
from sutra_core.adapters import PostgreSQLAdapter
adapter = PostgreSQLAdapter("postgresql://legacy-db")
concepts = adapter.ingest_table("customers")
storage.learn_many(concepts)
```

```python
# This will NEVER exist - querying Sutra WITH SQL
storage.execute_sql("SELECT * FROM concepts")  # ❌ No!
```

**Rule:** SQL/MongoDB/etc. are **inputs**, never **query languages** for Sutra.

## Enforcement Guidelines

### Documentation
✅ **Correct:** "Sutra uses TCP binary protocol for all queries"  
✅ **Correct:** "Ingest data from PostgreSQL/MongoDB using adapters"  
❌ **Wrong:** "Future: Add SQL interface for compatibility"  
❌ **Wrong:** "Query Sutra using Cypher-like syntax"

### Code Comments
```python
# ✅ Good
# Read customer data FROM PostgreSQL for ingestion
adapter = PostgreSQLAdapter(...)

# ❌ Bad  
# Support SQL queries TO Sutra storage
def execute_sql(query: str):
    ...
```

### Roadmaps
- Never include "SQL API support" or "GraphQL endpoint" as future features
- If comparing to traditional databases, clarify: "Unlike SQL databases..."
- Always position TCP protocol as the interface, not a limitation

## Competitive Positioning

**We are NOT:**
- A relational database (PostgreSQL, MySQL)
- A graph database (Neo4j, Neptune)  
- A document store (MongoDB, Couchbase)
- An API layer (GraphQL, PostgREST)

**We ARE:**
- A self-learning knowledge graph
- Natural language reasoning engine
- Domain-specific AI platform
- Audit-first compliance system

## References

**TCP Protocol:** `packages/sutra-protocol/src/messages.rs`  
**Client Library:** `packages/sutra-storage-client-tcp/`  
**Binary Format:** MessagePack (not JSON/XML/SQL)  
**Query Examples:** `docs/using-storage/README.md`

## Exceptions

**None.** This policy has no exceptions. If you think you need SQL/Cypher/GraphQL:

1. Re-evaluate the use case
2. Use natural language queries instead
3. If truly needed, build a separate translation layer outside Sutra core
4. Document why the translation layer exists (hint: legacy integration)

---

**Last Review:** 2025-01-16  
**Next Review:** On any architecture change proposal  
**Policy Owner:** Sutra Core Team
