"""
Pure Binary Storage System (PBSS)

A minimal, JSON-free binary storage used to persist knowledge nodes without a
traditional database. Adapted from sutra-swarm's PureBinaryStorage.
"""

import struct
import zlib
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

PBSS_MAGIC = b'PBSS'
PBSS_VERSION = 1


@dataclass
class StorageStats:
    total_nodes: int = 0
    total_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 1.0
    avg_operation_time: float = 0.0
    total_operations: int = 0


class PureBinaryStorage:
    """Minimal pure-binary storage backend for nodes with metadata."""

    def __init__(self, storage_path: str = "pure_binary_knowledge"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.stats = StorageStats()

    def encode_node(self, node: Dict[str, Any]) -> bytes:
        node_id = node.get('id', '')
        level = node.get('level', 'unit')
        content = node.get('content', '')
        timestamp = float(node.get('timestamp', time.time()))

        node_id_bytes = str(node_id).encode('utf-8')
        level_bytes = str(level).encode('utf-8')
        content_bytes = str(content).encode('utf-8')

        header = struct.pack('<4sBHHH', PBSS_MAGIC, PBSS_VERSION,
                             len(node_id_bytes), len(level_bytes), len(content_bytes))
        ts_bytes = struct.pack('<d', timestamp)
        binary = header + ts_bytes + node_id_bytes + level_bytes + content_bytes

        md = node.get('metadata', {}) or {}
        md_bytes = self._encode_metadata(md) if md else b''
        binary += struct.pack('<H', len(md_bytes)) + md_bytes
        return binary

    def _encode_metadata(self, metadata: Dict[str, Any]) -> bytes:
        parts: List[bytes] = []
        parts.append(struct.pack('<H', len(metadata)))
        for k, v in metadata.items():
            kb = str(k).encode('utf-8')
            vb = str(v).encode('utf-8')
            parts.append(struct.pack('<H', len(kb)))
            parts.append(kb)
            parts.append(struct.pack('<H', len(vb)))
            parts.append(vb)
        return b''.join(parts)

    def decode_node(self, data: bytes) -> Dict[str, Any]:
        off = 0
        header_size = struct.calcsize('<4sBHHH')
        magic, _ver, id_len, level_len, content_len = struct.unpack('<4sBHHH', data[off:off+header_size])
        off += header_size
        if magic != PBSS_MAGIC:
            raise ValueError('Invalid PBSS magic')
        timestamp = struct.unpack('<d', data[off:off+8])[0]
        off += 8
        node_id = data[off:off+id_len].decode('utf-8'); off += id_len
        level = data[off:off+level_len].decode('utf-8'); off += level_len
        content = data[off:off+content_len].decode('utf-8'); off += content_len
        md_size = struct.unpack('<H', data[off:off+2])[0]; off += 2
        metadata = {}
        if md_size:
            metadata = self._decode_metadata(data[off:off+md_size])
        return {'id': node_id, 'level': level, 'content': content, 'timestamp': timestamp, 'metadata': metadata}

    def _decode_metadata(self, data: bytes) -> Dict[str, Any]:
        off = 0
        pairs = struct.unpack('<H', data[off:off+2])[0]; off += 2
        md: Dict[str, Any] = {}
        for _ in range(pairs):
            klen = struct.unpack('<H', data[off:off+2])[0]; off += 2
            key = data[off:off+klen].decode('utf-8'); off += klen
            vlen = struct.unpack('<H', data[off:off+2])[0]; off += 2
            val = data[off:off+vlen].decode('utf-8'); off += vlen
            md[key] = val
        return md

    def _filename(self, node_id: str, level: str) -> Path:
        return self.storage_path / f"{level}_{hash(node_id) & 0xFFFFFFFF:08x}.pb"

    def store_node(self, node: Dict[str, Any]) -> bool:
        with self._lock:
            start = time.time()
            try:
                path = self._filename(str(node.get('id', 'unknown')), str(node.get('level', 'unit')))
                raw = self.encode_node(node)
                comp = zlib.compress(raw, level=6)
                # Atomic write: write to temp then replace
                tmp_path = path.with_suffix(path.suffix + ".tmp")
                with open(tmp_path, 'wb') as f:
                    f.write(comp)
                # os.replace is atomic on POSIX
                import os
                os.replace(tmp_path, path)
                self.stats.total_nodes += 1
                self.stats.total_size += len(raw)
                self.stats.compressed_size += len(comp)
                self.stats.compression_ratio = self.stats.total_size / max(self.stats.compressed_size, 1)
                op_us = (time.time() - start) * 1_000_000
                self.stats.total_operations += 1
                self.stats.avg_operation_time = (self.stats.avg_operation_time * (self.stats.total_operations - 1) + op_us) / self.stats.total_operations
                return True
            except Exception:
                return False

    def retrieve_node(self, node_id: str, level: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            try:
                path = self._filename(node_id, level)
                if not path.exists():
                    return None
                comp = path.read_bytes()
                raw = zlib.decompress(comp)
                return self.decode_node(raw)
            except Exception:
                return None

    def list_all_nodes(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for p in self.storage_path.glob("*.pb"):
            try:
                comp = p.read_bytes()
                raw = zlib.decompress(comp)
                nodes.append(self.decode_node(raw))
            except Exception:
                continue
        return nodes