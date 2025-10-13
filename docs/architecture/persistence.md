# Persistence and Audit (PBSS)

Storage backend:
- Pure Binary Storage System (PBSS) encodes nodes to binary with compression and magic headers
- Nodes are stored under <base_path>/nodes/*.pb using atomic writes (temp + replace)

Saved node types:
- concept (id=concept_id): content + metadata: format=v1, workspace_id, memory_type, strength, last_access, access_frequency, emotional_weight
- association (id="assoc:<src>-><tgt>:<type>"): metadata: format=v1, workspace_id, source_id, target_id, type, strength, reinforcement_count
- audit (id=audit-<timestamp>): content=action, metadata: format=v1, workspace_id, resource_type, resource_id, extra

Workspaces:
- Each saved node includes workspace_id
- Loading filters nodes by requested workspace_id; nodes without a workspace tag are included for backward compatibility

Audit logging:
- Enabled via config (AUDIT_ENABLED)
- Logged events: training_cycle, consolidation, assoc_reinforcement milestones

Considerations:
- Snapshot-based persistence (no transactional semantics)
- PBSS files are append/overwrite by node id; no external DB used
- Index rebuild occurs after load (token index)
