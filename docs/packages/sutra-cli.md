# sutra-cli (Planned)

Command-line interface for interacting with Sutra Models.

Status: Not implemented yet. This document specifies the intended design.

## Goals

- Scriptable access to learning, reasoning, and system management
- Human-friendly output with optional JSON
- Works offline (local storage)

## Proposed Commands

```
sutra
├── learn
│   ├── text "..."
│   ├── file path.txt
│   └── batch path.jsonl
├── search
│   ├── semantic --query "..." --top-k 5 --threshold 0.3
│   └── concept --id <CID>
├── reason
│   └── query "..." --max-steps 3 --num-paths 3 --threshold 0.3
├── system
│   ├── stats
│   ├── save
│   ├── load
│   └── reset --yes
└── demo
    └── hybrid
```

## Examples

```bash
# Learn a single text
sutra learn text "Python is a programming language" --source docs

# Learn a batch (JSONL: one JSON object per line with {"content": "..."})
sutra learn batch data.jsonl

# Semantic search
sutra search semantic --query "programming languages" --top-k 5 --threshold 0.4

# Reasoning query
sutra reason query "How do plants make energy?" --max-steps 3 --num-paths 3

# System management
sutra system stats
sutra system save
sutra system reset --yes
```

## Output Formats

- Default: pretty text
- `--json`: machine-readable JSON output for scripting

## Configuration

- Uses same storage as API by default (`./api_knowledge`)
- Flags to override: `--storage-path`, `--use-semantic/--no-semantic`

## Testing Strategy

- Use `click.testing.CliRunner`
- Test command parsing and exit codes
- Mock HybridAI for deterministic behavior

## Roadmap

- v0: Basic commands (learn/search/reason/system)
- v1: Interactive TUI mode
- v2: Remote API mode (targets sutra-api instead of local HybridAI)
