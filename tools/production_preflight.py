#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from gxb2 import database, live_service
from gxb2.battle import simulate
from gxb2.engine import Engine
from gxb2.security import validate_production_config

ROOT=Path(__file__).resolve().parents[1]


def check_battle_runtime():
    with tempfile.TemporaryDirectory(prefix="gxb3-preflight-") as tmp:
        engine=Engine(Path(tmp)/"player.sqlite3")
        try:
            snap=engine.pvp_team_snapshot()
            report=simulate(
                snap["team"],snap["team"],battle_id=987654,seed=987654,
                pet_a=snap.get("pet"),pet_b=snap.get("pet"),
                guild_skills_a=snap.get("guild_skills") or [],
                guild_skills_b=snap.get("guild_skills") or [],
                chime_bonus_a=snap.get("chime_bonus") or [],
                chime_bonus_b=snap.get("chime_bonus") or [],
                battle_type=1,
            )
            if report.get("isWin") not in (0,1):
                raise RuntimeError("Battle runtime trả kết quả không hợp lệ")
            return {"frames":len(report.get("frames") or []),"rounds":report.get("total_round")}
        finally:
            engine.close()


def main():
    parser=argparse.ArgumentParser(description="GXB 3 production release preflight")
    parser.add_argument("--skip-battle",action="store_true",help="Chỉ kiểm tra infra; không dùng để duyệt release cuối")
    args=parser.parse_args()

    host=os.environ.get("GXB3_HOST","127.0.0.1")
    origin=os.environ.get("GXB3_PUBLIC_ORIGIN","")
    admin=os.environ.get("GXB3_ADMIN_KEY","")
    db_url=os.environ.get("GXB3_DATABASE_URL") or os.environ.get("DATABASE_URL") or ""

    print("== GXB 3 Production Preflight ==")
    warnings=validate_production_config(http_host=host,public_origin=origin,admin_key=admin,database_url=db_url)
    for warning in warnings:
        print("WARNING:",warning)

    if not database.is_postgres():
        raise SystemExit("FAIL: production preflight phải chạy với PostgreSQL active.")
    worlds=live_service.worlds()
    print(f"OK database: PostgreSQL · worlds={len(worlds)}")
    print("OK public origin:",origin)
    print("OK admin secret: configured (value hidden)")

    if args.skip_battle:
        print("SKIP battle runtime: đây KHÔNG phải release approval cuối.")
    else:
        result=check_battle_runtime()
        print(f"OK battle runtime: frames={result['frames']} rounds={result['rounds']}")

    print("PASS: production preflight hoàn tất.")


if __name__=="__main__":
    main()
