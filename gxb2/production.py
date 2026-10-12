from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from . import auth, database, live_service
from .battle import simulate, ONLINE_BATTLE_ID, normalize_online_seed
from .engine import Engine


def run_startup_preflight() -> dict:
    """Fail-fast production gate executed inside the deployed container.

    Verifies all PostgreSQL schemas and the exact battle runtime shipped in the
    image. A successful result is persisted to the audit table so operators can
    verify the gate without shell access.
    """
    if not database.is_postgres():
        raise RuntimeError("Production startup preflight requires PostgreSQL")

    # Materialize every production schema eagerly instead of waiting for the
    # first player request.
    adb = auth._db()
    adb.close()
    ldb = live_service._db()
    ldb.close()
    database.ensure_player_schema()

    with tempfile.TemporaryDirectory(prefix="gxb3-startup-preflight-") as tmp:
        engine = Engine(Path(tmp) / "player.sqlite3")
        try:
            snap = engine.pvp_team_snapshot()
            report = simulate(
                snap["team"], snap["team"],
                battle_id=ONLINE_BATTLE_ID, seed=normalize_online_seed(123456),
                pet_a=snap.get("pet"), pet_b=snap.get("pet"),
                guild_skills_a=snap.get("guild_skills") or [],
                guild_skills_b=snap.get("guild_skills") or [],
                chime_bonus_a=snap.get("chime_bonus") or [],
                chime_bonus_b=snap.get("chime_bonus") or [],
                battle_type=1,
            )
        finally:
            engine.close()

    if report.get("isWin") not in (0, 1) or not isinstance(report.get("frames"), list):
        raise RuntimeError("Production battle runtime smoke returned an invalid report")

    result = {
        "ok": True,
        "database": database.backend_name(),
        "battle_frames": len(report.get("frames") or []),
        "battle_rounds": int(report.get("total_round") or 0),
        "checked_at": int(time.time()),
    }
    db = live_service._db()
    try:
        live_service._audit(db, "production.startup_preflight", "SYSTEM", result, "SYSTEM")
        db.commit()
    finally:
        db.close()
    return result
