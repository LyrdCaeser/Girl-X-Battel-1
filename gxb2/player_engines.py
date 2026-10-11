from __future__ import annotations

import threading
from pathlib import Path

from .engine import Engine

ROOT = Path(__file__).resolve().parents[1]


class PlayerEnginePool:
    def __init__(self):
        self._lock = threading.RLock()
        self._engines = {}

    @staticmethod
    def _safe(value):
        return ''.join(ch for ch in str(value) if ch.isalnum() or ch in ('-', '_'))[:80]

    def get(self, uid, server_id, character_name):
        uid = self._safe(uid)
        server_id = self._safe(server_id).upper()
        key = (uid, server_id)
        with self._lock:
            engine = self._engines.get(key)
            if engine is None:
                path = ROOT / "state" / "players" / uid / f"{server_id}.sqlite3"
                path.parent.mkdir(parents=True, exist_ok=True)
                engine = Engine(path, identity=(uid, server_id))
                engine.bind_identity(uid, server_id, character_name)
                self._engines[key] = engine
            else:
                engine.bind_identity(uid, server_id, character_name)
            return engine

    def close(self):
        with self._lock:
            engines = list(self._engines.values())
            self._engines.clear()
        for engine in engines:
            try: engine.close()
            except Exception: pass
