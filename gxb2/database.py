from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path

DATABASE_URL = (os.environ.get("GXB3_DATABASE_URL") or os.environ.get("DATABASE_URL") or "").strip()
POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")
IntegrityError = sqlite3.IntegrityError

_pool = None
_pool_lock = threading.RLock()
_schema_ready = set()


class CursorProxy:
    def __init__(self, cursor, backend):
        self._cursor = cursor
        self.backend = backend

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return getattr(self._cursor, "lastrowid", None)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)


class DBConnection:
    def __init__(self, conn, backend, pool=None, identity=""):
        self._conn = conn
        self.backend = backend
        self._pool = pool
        self.identity = identity or backend
        self._closed = False

    def execute(self, sql, params=()):
        if self.backend == "postgres":
            if sql.strip().upper() == "BEGIN IMMEDIATE":
                sql = "BEGIN"
            sql = sql.replace("?", "%s")
        cur = self._conn.execute(sql, tuple(params or ()))
        return CursorProxy(cur, self.backend)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._pool is not None:
            self._pool.putconn(self._conn)
        else:
            self._conn.close()


def is_postgres():
    return POSTGRES


def backend_name():
    return "postgres" if POSTGRES else "sqlite"


def _pg_pool():
    global _pool, IntegrityError
    with _pool_lock:
        if _pool is None:
            try:
                import psycopg
                from psycopg.rows import dict_row
                from psycopg_pool import ConnectionPool
            except ImportError as exc:
                raise RuntimeError("PostgreSQL cần cài psycopg[binary,pool].") from exc
            IntegrityError = (sqlite3.IntegrityError, psycopg.IntegrityError)
            _pool = ConnectionPool(
                conninfo=DATABASE_URL,
                min_size=int(os.environ.get("GXB3_DB_POOL_MIN", "1")),
                max_size=int(os.environ.get("GXB3_DB_POOL_MAX", "12")),
                kwargs={"autocommit": False, "row_factory": dict_row},
                open=True,
            )
        return _pool


def connect(sqlite_path: Path, schema: str):
    if POSTGRES:
        pool = _pg_pool()
        conn = pool.getconn()
        db = DBConnection(conn, "postgres", pool, DATABASE_URL)
    else:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(sqlite_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        db = DBConnection(conn, "sqlite", identity=str(sqlite_path.resolve()))
    ensure_schema(db, schema)
    return db


def ensure_schema(db: DBConnection, schema: str):
    key = (db.backend, db.identity, schema)
    if key in _schema_ready:
        return
    with _pool_lock:
        if key in _schema_ready:
            return
        if schema == "auth":
            _ensure_auth(db)
        elif schema == "live":
            _ensure_live(db)
        else:
            raise ValueError(f"Unknown schema: {schema}")
        db.commit()
        _schema_ready.add(key)


def _ensure_auth(db):
    if db.backend == "postgres":
        db.execute("""CREATE TABLE IF NOT EXISTS accounts(
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
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_username_ci ON accounts((lower(username)))")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email_ci ON accounts((lower(email))) WHERE email <> ''")
        db.execute("""CREATE TABLE IF NOT EXISTS sessions(
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
        db.execute("""CREATE TABLE IF NOT EXISTS recovery_codes(
            account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
            code_hash TEXT NOT NULL,
            created_at BIGINT NOT NULL,
            used_at BIGINT NOT NULL DEFAULT 0
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS login_attempts(
            bucket TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            first_at BIGINT NOT NULL,
            blocked_until BIGINT NOT NULL DEFAULT 0
        )""")
        return

    db.execute("""CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        email TEXT NOT NULL DEFAULT '',
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at INTEGER NOT NULL,
        last_login INTEGER NOT NULL DEFAULT 0
    )""")
    db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email
                  ON accounts(email COLLATE NOCASE) WHERE email <> ''""")
    cols = {row[1] for row in db.execute("PRAGMA table_info(accounts)")}
    if "ban_reason" not in cols:
        db.execute("ALTER TABLE accounts ADD COLUMN ban_reason TEXT NOT NULL DEFAULT ''")
    db.execute("""CREATE TABLE IF NOT EXISTS sessions(
        token_hash TEXT PRIMARY KEY,
        account_id INTEGER NOT NULL,
        server_id TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        last_seen INTEGER NOT NULL,
        FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
    )""")
    session_cols = {row[1] for row in db.execute("PRAGMA table_info(sessions)")}
    if "session_id" not in session_cols:
        db.execute("ALTER TABLE sessions ADD COLUMN session_id TEXT NOT NULL DEFAULT ''")
    if "user_agent" not in session_cols:
        db.execute("ALTER TABLE sessions ADD COLUMN user_agent TEXT NOT NULL DEFAULT ''")
    if "remote_addr" not in session_cols:
        db.execute("ALTER TABLE sessions ADD COLUMN remote_addr TEXT NOT NULL DEFAULT ''")
    import secrets
    for old in db.execute("SELECT rowid FROM sessions WHERE session_id='' OR session_id IS NULL").fetchall():
        db.execute("UPDATE sessions SET session_id=? WHERE rowid=?", ("SES-" + secrets.token_hex(8).upper(), old[0]))
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id)")
    db.execute("""CREATE TABLE IF NOT EXISTS recovery_codes(
        account_id INTEGER PRIMARY KEY,
        code_hash TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        used_at INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS login_attempts(
        bucket TEXT PRIMARY KEY,
        count INTEGER NOT NULL,
        first_at INTEGER NOT NULL,
        blocked_until INTEGER NOT NULL DEFAULT 0
    )""")


def _ensure_live(db):
    if db.backend == "postgres":
        db.execute("""CREATE TABLE IF NOT EXISTS worlds(
            server_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'online',
            created_at BIGINT NOT NULL,
            registration_open INTEGER NOT NULL DEFAULT 1,
            character_creation_open INTEGER NOT NULL DEFAULT 1,
            message TEXT NOT NULL DEFAULT ''
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS players(
            uid TEXT NOT NULL,
            server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            ban_reason TEXT NOT NULL DEFAULT '',
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            PRIMARY KEY(uid, server_id)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS mail(
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
        db.execute("""CREATE TABLE IF NOT EXISTS orders(
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
        db.execute("""CREATE TABLE IF NOT EXISTS audit(
            id BIGSERIAL PRIMARY KEY,
            at BIGINT NOT NULL,
            operator TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            detail TEXT NOT NULL
        )""")
        db.execute("""INSERT INTO worlds(server_id,name,status,created_at,registration_open,character_creation_open,message)
                      VALUES('S1','Server 1','online',?,1,1,'')
                      ON CONFLICT(server_id) DO NOTHING""", (int(__import__("time").time()),))
        return

    db.execute("""CREATE TABLE IF NOT EXISTS worlds(
        server_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'online',
        created_at INTEGER NOT NULL
    )""")
    world_cols = {row[1] for row in db.execute("PRAGMA table_info(worlds)")}
    if "registration_open" not in world_cols:
        db.execute("ALTER TABLE worlds ADD COLUMN registration_open INTEGER NOT NULL DEFAULT 1")
    if "character_creation_open" not in world_cols:
        db.execute("ALTER TABLE worlds ADD COLUMN character_creation_open INTEGER NOT NULL DEFAULT 1")
    if "message" not in world_cols:
        db.execute("ALTER TABLE worlds ADD COLUMN message TEXT NOT NULL DEFAULT ''")
    db.execute("""CREATE TABLE IF NOT EXISTS players(
        uid TEXT NOT NULL,
        server_id TEXT NOT NULL,
        character_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        ban_reason TEXT NOT NULL DEFAULT '',
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        PRIMARY KEY(uid, server_id)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS mail(
        id TEXT PRIMARY KEY,
        uid TEXT NOT NULL,
        server_id TEXT NOT NULL,
        character_name TEXT NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        attachments TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at INTEGER NOT NULL,
        claimed_at INTEGER NOT NULL DEFAULT 0,
        operator TEXT NOT NULL DEFAULT 'GM'
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS orders(
        id TEXT PRIMARY KEY,
        uid TEXT NOT NULL,
        server_id TEXT NOT NULL,
        character_name TEXT NOT NULL,
        package TEXT NOT NULL,
        note TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        reward TEXT NOT NULL DEFAULT '{}',
        created_at INTEGER NOT NULL,
        reviewed_at INTEGER NOT NULL DEFAULT 0,
        reviewer TEXT NOT NULL DEFAULT ''
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS audit(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        at INTEGER NOT NULL,
        operator TEXT NOT NULL,
        action TEXT NOT NULL,
        target TEXT NOT NULL,
        detail TEXT NOT NULL
    )""")
    db.execute("INSERT OR IGNORE INTO worlds(server_id,name,status,created_at) VALUES('S1','Server 1','online',?)",
               (int(__import__("time").time()),))


def close_pool():
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None
