from __future__ import annotations

import time

from . import database


class BufferedCursor:
    def __init__(self, rows=None, rowcount=0):
        self._rows = list(rows or [])
        self._index = 0
        self.rowcount = rowcount

    def fetchone(self):
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    def fetchall(self):
        if self._index >= len(self._rows):
            return []
        rows = self._rows[self._index:]
        self._index = len(self._rows)
        return rows

    def __iter__(self):
        return iter(self.fetchall())


class ScopedPostgresPlayerDB:
    """Small SQL compatibility layer for Engine's profile/clock/battle persistence.

    The game engine only uses three local SQLite tables. This adapter maps those
    exact operations into shared PostgreSQL tables keyed by UID + server_id.
    """

    def __init__(self, uid: str, server_id: str):
        if not database.is_postgres():
            raise RuntimeError("ScopedPostgresPlayerDB requires PostgreSQL")
        database.ensure_player_schema()
        self.uid = str(uid)
        self.server_id = str(server_id).upper()
        self._tx = None

    def _conn(self):
        if self._tx is None:
            self._tx = database.acquire_postgres()
        return self._tx

    def _short_query(self, sql, params=()):
        conn = database.acquire_postgres()
        try:
            cur = conn.execute(sql, tuple(params or ()))
            rows = cur.fetchall()
            return BufferedCursor(rows, cur.rowcount)
        finally:
            database.release_postgres(conn)

    def execute(self, sql, params=()):
        raw = sql.strip()
        low = " ".join(raw.lower().split())
        params = tuple(params or ())

        if low.startswith("pragma journal_mode"):
            return BufferedCursor()
        if low.startswith("create table if not exists profile"):
            return BufferedCursor()
        if low.startswith("create table if not exists clock"):
            return BufferedCursor()
        if low.startswith("create table if not exists battles"):
            return BufferedCursor()

        if low == "begin immediate":
            conn = self._conn()
            conn.execute("BEGIN")
            return BufferedCursor()

        if low.startswith("select floor from clock where id=1"):
            return self._short_query(
                "SELECT clock_floor FROM player_profiles WHERE uid=%s AND server_id=%s",
                (self.uid, self.server_id),
            )

        if low.startswith("select 1 from profile where id=1"):
            return self._short_query(
                "SELECT 1 FROM player_profiles WHERE uid=%s AND server_id=%s",
                (self.uid, self.server_id),
            )

        if low.startswith("insert into profile values"):
            data = params[0]
            conn = self._conn()
            cur = conn.execute(
                """INSERT INTO player_profiles(uid,server_id,data,clock_floor,updated_at)
                   VALUES(%s,%s,%s,0,%s)
                   ON CONFLICT(uid,server_id) DO UPDATE SET
                     data=excluded.data,
                     updated_at=excluded.updated_at""",
                (self.uid, self.server_id, data, int(time.time())),
            )
            return BufferedCursor(rowcount=cur.rowcount)

        if low.startswith("insert into clock"):
            floor = int(params[0])
            conn = self._conn()
            cur = conn.execute(
                """UPDATE player_profiles
                   SET clock_floor=%s,updated_at=%s
                   WHERE uid=%s AND server_id=%s""",
                (floor, int(time.time()), self.uid, self.server_id),
            )
            return BufferedCursor(rowcount=cur.rowcount)

        if low.startswith("select data from profile where id=1"):
            if self._tx is not None:
                cur = self._tx.execute(
                    "SELECT data FROM player_profiles WHERE uid=%s AND server_id=%s FOR UPDATE",
                    (self.uid, self.server_id),
                )
                rows = cur.fetchall()
                return BufferedCursor(rows, cur.rowcount)
            return self._short_query(
                "SELECT data FROM player_profiles WHERE uid=%s AND server_id=%s",
                (self.uid, self.server_id),
            )

        if low.startswith("update profile set data="):
            data = params[0]
            conn = self._conn()
            cur = conn.execute(
                """UPDATE player_profiles
                   SET data=%s,updated_at=%s
                   WHERE uid=%s AND server_id=%s""",
                (data, int(time.time()), self.uid, self.server_id),
            )
            return BufferedCursor(rowcount=cur.rowcount)

        if low.startswith("insert into battles values"):
            battle_id, stage, report = params
            conn = self._conn()
            cur = conn.execute(
                """INSERT INTO player_battles(uid,server_id,id,stage,report)
                   VALUES(%s,%s,%s,%s,%s)
                   ON CONFLICT(uid,server_id,id) DO UPDATE SET
                     stage=excluded.stage,
                     report=excluded.report""",
                (self.uid, self.server_id, int(battle_id), int(stage), report),
            )
            return BufferedCursor(rowcount=cur.rowcount)

        if low.startswith("select report,stage from battles where id="):
            battle_id = int(params[0])
            return self._short_query(
                """SELECT report,stage FROM player_battles
                   WHERE uid=%s AND server_id=%s AND id=%s""",
                (self.uid, self.server_id, battle_id),
            )

        raise RuntimeError(f"Unsupported player persistence SQL: {raw}")

    def commit(self):
        if self._tx is None:
            return
        conn = self._tx
        self._tx = None
        try:
            conn.commit()
        finally:
            database.release_postgres(conn)

    def rollback(self):
        if self._tx is None:
            return
        conn = self._tx
        self._tx = None
        try:
            conn.rollback()
        finally:
            database.release_postgres(conn)

    def close(self):
        if self._tx is not None:
            self.rollback()
