"""JSON file cache for every API response (data/cache/<source>/<hash>.json)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


def _stable(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str, ensure_ascii=False)


class JsonCache:
    def __init__(self, root: Path, ttl_hours: float = 168) -> None:
        self.root = Path(root)
        self.ttl_seconds = ttl_hours * 3600

    def path(self, source: str, endpoint: str, params: dict | None) -> Path:
        digest = hashlib.sha1(_stable({"e": endpoint, "p": params or {}}).encode()).hexdigest()
        safe_endpoint = "".join(c if c.isalnum() else "_" for c in endpoint)[:40]
        return self.root / source / f"{safe_endpoint}_{digest[:16]}.json"

    def get(self, source: str, endpoint: str, params: dict | None) -> Any | None:
        p = self.path(source, endpoint, params)
        if not p.is_file():
            return None
        try:
            blob = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if self.ttl_seconds and time.time() - blob.get("fetched_at", 0) > self.ttl_seconds:
            return None
        return blob.get("response")

    def set(self, source: str, endpoint: str, params: dict | None, response: Any) -> Path:
        p = self.path(source, endpoint, params)
        p.parent.mkdir(parents=True, exist_ok=True)
        blob = {
            "source": source,
            "endpoint": endpoint,
            "params": params or {},  # never contains secrets (see BaseClient)
            "fetched_at": time.time(),
            "response": response,
        }
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(blob, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        tmp.replace(p)
        return p
