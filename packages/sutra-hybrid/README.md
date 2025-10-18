# Sutra Hybrid (with Grounded NLG)

Production-ready hybrid API that combines semantic retrieval over the Sutra Storage gRPC server with optional grounded, template-driven NLG (no LLMs).

## Build (Docker)

```bash
# From repo root
docker build -f packages/sutra-hybrid/Dockerfile -t sutra-hybrid:nlg .
```

## Run

```bash
docker run --rm -p 8001:8000 \
  -e SUTRA_STORAGE_SERVER=storage-server:50051 \
  -e SUTRA_NLG_ENABLED=true \
  -e SUTRA_NLG_TONE=friendly \
  --name sutra-hybrid sutra-hybrid:nlg
```

## Environment variables

- SUTRA_STORAGE_SERVER: gRPC address of storage-server (host:port)
- SUTRA_NLG_ENABLED: true|false (enable grounded NLG post-processing; default: true)
- SUTRA_NLG_TONE: friendly|formal|concise|regulatory (default: friendly)

## API (selected)

- POST /sutra/learn
- POST /sutra/query
  - Body fields:
    - query: string
    - semantic_boost: boolean
    - max_depth: int
    - max_paths: int
    - tone: optional string (friendly|formal|concise|regulatory)
    - moves: optional array of strings (e.g., ["define","evidence"])

## Example

```bash
curl -s http://localhost:8001/sutra/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is Python?","tone":"friendly","moves":["define","evidence"]}' | jq .
```

## Guarantees

- Grounded responses only: every clause derives from stored concepts or marked hedge tokens.
- On any NLG failure or low evidence, system falls back to raw, retrieved answer.
- Full audit trail remains intact.

## Notes

- The NLG layer lives in packages/sutra-nlg and is installed into this image.
- No LLMs are used; generation is template-driven and deterministic.
