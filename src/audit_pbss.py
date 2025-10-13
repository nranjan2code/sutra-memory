"""
Append-only audit logging over PBSS (no traditional database).
Each audit entry is a binary node with level="audit" and simple metadata.
"""
from __future__ import annotations

import os
import time
from typing import Optional, Dict, Any

from .pure_binary_storage import PureBinaryStorage


class AuditLogger:
    def __init__(self, base_path: str = "knowledge_store", workspace_id: str = "core"):
        self.base_path = base_path
        self.workspace_id = workspace_id
        self.nodes_path = os.path.join(base_path, "nodes")
        os.makedirs(self.nodes_path, exist_ok=True)
        self.storage = PureBinaryStorage(self.nodes_path)

    def log(self, action: str, *, resource_type: str, resource_id: str, extra: Optional[Dict[str, Any]] = None) -> None:
        node = {
            "id": f"audit-{int(time.time()*1000)}",
            "level": "audit",
            "content": action,
            "timestamp": time.time(),
            "metadata": {
                "format": "v1",
                "workspace_id": self.workspace_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                # Store a compact kv string; audit is for humans/tools, not core logic
                "extra": str(extra or {}),
            },
        }
        try:
            self.storage.store_node(node)
        except Exception:
            pass

    # Convenience wrappers
    def log_training_cycle(self, cycle: int, stats: Dict[str, Any]) -> None:
        self.log(
            action="training_cycle",
            resource_type="trainer",
            resource_id=str(cycle),
            extra={
                "total_concepts": stats.get("total_concepts"),
                "total_associations": stats.get("total_associations"),
            },
        )

    def log_consolidation(self, concept_id: str, old_type: str, new_type: str) -> None:
        self.log(
            action="consolidation",
            resource_type="concept",
            resource_id=concept_id,
            extra={"from": old_type, "to": new_type},
        )

    def log_assoc_reinforcement(self, source_id: str, target_id: str, assoc_type: str, reinforcement_count: int, strength: float) -> None:
        self.log(
            action="assoc_reinforcement",
            resource_type="association",
            resource_id=f"{source_id}->{target_id}:{assoc_type}",
            extra={"reinforcement": reinforcement_count, "strength": strength},
        )