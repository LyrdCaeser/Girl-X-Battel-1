from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


AUTH_TABLES = ["accounts", "sessions", "recovery_codes", "login_attempts"]
LIVE_TABLES = ["worlds", "players", "mail", "orders", "audit", "presence", "leaderboard", "world_guilds", "world_guild_members", "world_guild_applications", "world_guild_chat", "world_guild_mail", "guild_wars", "guild_war_battles", "guild_war_claims", "pvp_queue", "pvp_matches", "pvp_match_peers", "pvp_ratings", "pvp_season_claims"]


def rows(path, table):
    if not path.exists():
        return []
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in db.execute(f"SELECT * FROM {table}")]
    except sqlite3.OperationalError:
        return []
    finally:
        db.close()


def insert_many(pg, table, records, conflict_cols=None):
    if not records:
        return 0
    cols = list(records[0])
    placeholders = ",".join(["%s"] * len(cols))
    names = ",".join(cols)
    values = [tuple(r.get(c) for c in cols) for r in records]
    if conflict_cols:
        target = ",".join(conflict_cols)
        update_cols = [c for c in cols if c not in conflict_cols]
        update = ",".join(f"{c}=EXCLUDED.{c}" for c in update_cols)
        sql = f"INSERT INTO {table}({names}) VALUES({placeholders}) ON CONFLICT({target}) DO UPDATE SET {update}"
    else:
        sql = f"INSERT INTO {table}({names}) VALUES({placeholders}) ON CONFLICT DO NOTHING"
    with pg.cursor() as cur:
        cur.executemany(sql, values)
    return len(records)


def ensure_schema(pg):
    with pg.cursor() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS accounts(
            id BIGSERIAL PRIMARY KEY,
            uid TEXT UNIQUE,
            username TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at BIGINT NOT NULL,
            last_login BIGINT NOT NULL DEFAULT 0,
            ban_reason TEXT NOT NULL DEFAULT ''
        )""")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_username_ci ON accounts((lower(username)))")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email_ci ON accounts((lower(email))) WHERE email <> ''")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(
            token_hash TEXT PRIMARY KEY,
            account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            server_id TEXT NOT NULL,
            created_at BIGINT NOT NULL,
            expires_at BIGINT NOT NULL,
            last_seen BIGINT NOT NULL,
            session_id TEXT NOT NULL UNIQUE,
            user_agent TEXT NOT NULL DEFAULT '',
            remote_addr TEXT NOT NULL DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS recovery_codes(
            account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
            code_hash TEXT NOT NULL,
            created_at BIGINT NOT NULL,
            used_at BIGINT NOT NULL DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS login_attempts(
            bucket TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            first_at BIGINT NOT NULL,
            blocked_until BIGINT NOT NULL DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS worlds(
            server_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'online',
            created_at BIGINT NOT NULL,
            registration_open INTEGER NOT NULL DEFAULT 1,
            character_creation_open INTEGER NOT NULL DEFAULT 1,
            message TEXT NOT NULL DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS players(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            ban_reason TEXT NOT NULL DEFAULT '',
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            PRIMARY KEY(uid, server_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS mail(
            id TEXT PRIMARY KEY,
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            attachments TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at BIGINT NOT NULL,
            claimed_at BIGINT NOT NULL DEFAULT 0,
            operator TEXT NOT NULL DEFAULT 'GM'
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders(
            id TEXT PRIMARY KEY,
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            package TEXT NOT NULL,
            note TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            reward TEXT NOT NULL DEFAULT '{}',
            created_at BIGINT NOT NULL,
            reviewed_at BIGINT NOT NULL DEFAULT 0,
            reviewer TEXT NOT NULL DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS audit(
            id BIGSERIAL PRIMARY KEY,
            at BIGINT NOT NULL,
            operator TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            detail TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS presence(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            last_seen BIGINT NOT NULL,
            PRIMARY KEY(uid, server_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS leaderboard(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            power BIGINT NOT NULL DEFAULT 0,
            updated_at BIGINT NOT NULL,
            PRIMARY KEY(uid, server_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS world_guilds(
            id BIGSERIAL PRIMARY KEY,
            server_id TEXT NOT NULL,
            name TEXT NOT NULL,
            notice TEXT NOT NULL DEFAULT '',
            owner_uid TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            exp BIGINT NOT NULL DEFAULT 0,
            created_at BIGINT NOT NULL,
            UNIQUE(server_id,name)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS world_guild_members(
            guild_id BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            power BIGINT NOT NULL DEFAULT 0,
            joined_at BIGINT NOT NULL,
            last_seen BIGINT NOT NULL,
            contribution BIGINT NOT NULL DEFAULT 0,
            PRIMARY KEY(uid,server_id),
            UNIQUE(guild_id,uid)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS world_guild_applications(
            guild_id BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            power BIGINT NOT NULL DEFAULT 0,
            created_at BIGINT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            PRIMARY KEY(guild_id,uid)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS world_guild_chat(
            id BIGSERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            uid TEXT NOT NULL,
            character_name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS world_guild_mail(
            id TEXT PRIMARY KEY,
            guild_id BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            sender_uid TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS guild_wars(
            id TEXT PRIMARY KEY,
            server_id TEXT NOT NULL,
            guild_a BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            guild_b BIGINT NOT NULL REFERENCES world_guilds(id) ON DELETE CASCADE,
            score_a BIGINT NOT NULL DEFAULT 0,
            score_b BIGINT NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'scheduled',
            starts_at BIGINT NOT NULL,
            ends_at BIGINT NOT NULL,
            winner_guild BIGINT NOT NULL DEFAULT 0,
            created_at BIGINT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS guild_war_battles(
            id TEXT PRIMARY KEY,
            war_id TEXT NOT NULL REFERENCES guild_wars(id) ON DELETE CASCADE,
            attacker_uid TEXT NOT NULL,
            attacker_guild BIGINT NOT NULL,
            defender_uid TEXT NOT NULL,
            defender_guild BIGINT NOT NULL,
            winner_uid TEXT NOT NULL DEFAULT '',
            score BIGINT NOT NULL DEFAULT 0,
            report TEXT NOT NULL DEFAULT '{}',
            created_at BIGINT NOT NULL,
            UNIQUE(war_id,attacker_uid,defender_uid)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS guild_war_claims(
            war_id TEXT NOT NULL REFERENCES guild_wars(id) ON DELETE CASCADE,
            uid TEXT NOT NULL,
            guild_id BIGINT NOT NULL,
            reward TEXT NOT NULL,
            claimed_at BIGINT NOT NULL,
            PRIMARY KEY(war_id,uid)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pvp_queue(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            mode TEXT NOT NULL,
            power BIGINT NOT NULL DEFAULT 0,
            joined_at BIGINT NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',
            PRIMARY KEY(uid,server_id,mode)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pvp_matches(
            id TEXT PRIMARY KEY,
            mode TEXT NOT NULL,
            server_id TEXT NOT NULL,
            server_a TEXT NOT NULL DEFAULT '',
            server_b TEXT NOT NULL DEFAULT '',
            player_a TEXT NOT NULL,
            player_b TEXT NOT NULL,
            name_a TEXT NOT NULL,
            name_b TEXT NOT NULL,
            power_a BIGINT NOT NULL DEFAULT 0,
            power_b BIGINT NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ready',
            winner_uid TEXT NOT NULL DEFAULT '',
            created_at BIGINT NOT NULL,
            resolved_at BIGINT NOT NULL DEFAULT 0,
            seed BIGINT NOT NULL DEFAULT 0,
            snapshot_a TEXT NOT NULL DEFAULT '{}',
            snapshot_b TEXT NOT NULL DEFAULT '{}',
            battle_report TEXT NOT NULL DEFAULT '{}',
            rating_delta_a INTEGER NOT NULL DEFAULT 0,
            rating_delta_b INTEGER NOT NULL DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pvp_ratings(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            season_id TEXT NOT NULL,
            rating INTEGER NOT NULL DEFAULT 1000,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            matches INTEGER NOT NULL DEFAULT 0,
            updated_at BIGINT NOT NULL,
            PRIMARY KEY(uid,server_id,mode,season_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pvp_season_claims(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            season_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            reward TEXT NOT NULL,
            claimed_at BIGINT NOT NULL,
            PRIMARY KEY(uid,server_id,mode,season_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pvp_match_peers(
            match_id TEXT NOT NULL REFERENCES pvp_matches(id) ON DELETE CASCADE,
            uid TEXT NOT NULL,
            ready INTEGER NOT NULL DEFAULT 0,
            last_seen BIGINT NOT NULL,
            PRIMARY KEY(match_id,uid)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS player_profiles(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            data TEXT NOT NULL,
            clock_floor BIGINT NOT NULL DEFAULT 0,
            updated_at BIGINT NOT NULL,
            PRIMARY KEY(uid, server_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS player_battles(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            id BIGINT NOT NULL,
            stage BIGINT,
            report TEXT NOT NULL,
            PRIMARY KEY(uid, server_id, id)
        )""")



def player_save_records(state_dir):
    profiles = []
    battles = []
    root = state_dir / "players"
    if not root.exists():
        return profiles, battles
    for uid_dir in root.iterdir():
        if not uid_dir.is_dir():
            continue
        uid = uid_dir.name
        for db_path in uid_dir.glob("*.sqlite3"):
            server_id = db_path.stem.upper()
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            try:
                profile = db.execute("SELECT data FROM profile WHERE id=1").fetchone()
                if not profile:
                    continue
                clock = db.execute("SELECT floor FROM clock WHERE id=1").fetchone()
                profiles.append({
                    "uid": uid,
                    "server_id": server_id,
                    "data": profile["data"],
                    "clock_floor": int(clock["floor"]) if clock else 0,
                    "updated_at": int(db_path.stat().st_mtime),
                })
                try:
                    for row in db.execute("SELECT id,stage,report FROM battles"):
                        battles.append({
                            "uid": uid,
                            "server_id": server_id,
                            "id": int(row["id"]),
                            "stage": int(row["stage"]) if row["stage"] is not None else None,
                            "report": row["report"],
                        })
                except sqlite3.OperationalError:
                    pass
            finally:
                db.close()
    return profiles, battles

def main():
    ap = argparse.ArgumentParser(description="Migrate GXB3 auth/live-service SQLite data to PostgreSQL")
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--state-dir", type=Path, default=Path("state"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    auth_path = args.state_dir / "auth.sqlite3"
    live_path = args.state_dir / "live_service.sqlite3"

    player_profiles, player_battles = player_save_records(args.state_dir)
    source = {
        "accounts": rows(auth_path, "accounts"),
        "sessions": rows(auth_path, "sessions"),
        "recovery_codes": rows(auth_path, "recovery_codes"),
        "login_attempts": rows(auth_path, "login_attempts"),
        "worlds": rows(live_path, "worlds"),
        "players": rows(live_path, "players"),
        "mail": rows(live_path, "mail"),
        "orders": rows(live_path, "orders"),
        "audit": rows(live_path, "audit"),
        "presence": rows(live_path, "presence"),
        "leaderboard": rows(live_path, "leaderboard"),
        "world_guilds": rows(live_path, "world_guilds"),
        "world_guild_members": rows(live_path, "world_guild_members"),
        "world_guild_applications": rows(live_path, "world_guild_applications"),
        "world_guild_chat": rows(live_path, "world_guild_chat"),
        "world_guild_mail": rows(live_path, "world_guild_mail"),
        "guild_wars": rows(live_path, "guild_wars"),
        "guild_war_battles": rows(live_path, "guild_war_battles"),
        "guild_war_claims": rows(live_path, "guild_war_claims"),
        "pvp_queue": rows(live_path, "pvp_queue"),
        "pvp_matches": rows(live_path, "pvp_matches"),
        "pvp_match_peers": rows(live_path, "pvp_match_peers"),
        "pvp_ratings": rows(live_path, "pvp_ratings"),
        "pvp_season_claims": rows(live_path, "pvp_season_claims"),
        "player_profiles": player_profiles,
        "player_battles": player_battles,
    }

    if args.dry_run:
        for table, data in source.items():
            print(f"{table}: {len(data)} rows")
        return

    with psycopg.connect(args.database_url, row_factory=dict_row) as pg:
        ensure_schema(pg)
        inserted = {}
        inserted["accounts"] = insert_many(pg, "accounts", source["accounts"], ["id"])
        inserted["sessions"] = insert_many(pg, "sessions", source["sessions"], ["token_hash"])
        inserted["recovery_codes"] = insert_many(pg, "recovery_codes", source["recovery_codes"], ["account_id"])
        inserted["login_attempts"] = insert_many(pg, "login_attempts", source["login_attempts"], ["bucket"])
        inserted["worlds"] = insert_many(pg, "worlds", source["worlds"], ["server_id"])
        inserted["players"] = insert_many(pg, "players", source["players"], ["uid", "server_id"])
        inserted["mail"] = insert_many(pg, "mail", source["mail"], ["id"])
        inserted["orders"] = insert_many(pg, "orders", source["orders"], ["id"])
        inserted["audit"] = insert_many(pg, "audit", source["audit"], ["id"])
        inserted["presence"] = insert_many(pg, "presence", source["presence"], ["uid", "server_id"])
        inserted["leaderboard"] = insert_many(pg, "leaderboard", source["leaderboard"], ["uid", "server_id"])
        inserted["world_guilds"] = insert_many(pg, "world_guilds", source["world_guilds"], ["id"])
        inserted["world_guild_members"] = insert_many(pg, "world_guild_members", source["world_guild_members"], ["uid", "server_id"])
        inserted["world_guild_applications"] = insert_many(pg, "world_guild_applications", source["world_guild_applications"], ["guild_id", "uid"])
        inserted["world_guild_chat"] = insert_many(pg, "world_guild_chat", source["world_guild_chat"], ["id"])
        inserted["world_guild_mail"] = insert_many(pg, "world_guild_mail", source["world_guild_mail"], ["id"])
        inserted["guild_wars"] = insert_many(pg, "guild_wars", source["guild_wars"], ["id"])
        inserted["guild_war_battles"] = insert_many(pg, "guild_war_battles", source["guild_war_battles"], ["id"])
        inserted["guild_war_claims"] = insert_many(pg, "guild_war_claims", source["guild_war_claims"], ["war_id", "uid"])
        inserted["pvp_queue"] = insert_many(pg, "pvp_queue", source["pvp_queue"], ["uid", "server_id", "mode"])
        inserted["pvp_matches"] = insert_many(pg, "pvp_matches", source["pvp_matches"], ["id"])
        inserted["pvp_match_peers"] = insert_many(pg, "pvp_match_peers", source["pvp_match_peers"], ["match_id", "uid"])
        inserted["pvp_ratings"] = insert_many(pg, "pvp_ratings", source["pvp_ratings"], ["uid", "server_id", "mode", "season_id"])
        inserted["pvp_season_claims"] = insert_many(pg, "pvp_season_claims", source["pvp_season_claims"], ["uid", "server_id", "mode", "season_id"])
        inserted["player_profiles"] = insert_many(pg, "player_profiles", source["player_profiles"], ["uid", "server_id"])
        inserted["player_battles"] = insert_many(pg, "player_battles", source["player_battles"], ["uid", "server_id", "id"])

        with pg.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(id),0)+1 AS n FROM accounts")
            next_account = cur.fetchone()["n"]
            cur.execute("SELECT setval(pg_get_serial_sequence('accounts','id'), %s, false)", (next_account,))
            cur.execute("SELECT COALESCE(MAX(id),0)+1 AS n FROM audit")
            next_audit = cur.fetchone()["n"]
            cur.execute("SELECT setval(pg_get_serial_sequence('audit','id'), %s, false)", (next_audit,))
            cur.execute("SELECT COALESCE(MAX(id),0)+1 AS n FROM world_guilds")
            next_guild = cur.fetchone()["n"]
            cur.execute("SELECT setval(pg_get_serial_sequence('world_guilds','id'), %s, false)", (next_guild,))
            cur.execute("SELECT COALESCE(MAX(id),0)+1 AS n FROM world_guild_chat")
            next_chat = cur.fetchone()["n"]
            cur.execute("SELECT setval(pg_get_serial_sequence('world_guild_chat','id'), %s, false)", (next_chat,))
        pg.commit()

    for table, count in inserted.items():
        print(f"{table}: migrated {count} rows")


if __name__ == "__main__":
    main()
