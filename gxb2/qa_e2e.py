from __future__ import annotations

import hashlib
import secrets
import time

from . import auth, database, live_service
from .battle import simulate, ONLINE_BATTLE_ID, normalize_online_seed
from .player_engines import PlayerEnginePool

QA_USERS=("qa_release_a","qa_release_b")
QA_NAMES=("QA-A","QA-B")
QA_GUILDS=("QA-Guild-A","QA-Guild-B")


def _existing_pass():
    db=live_service._db()
    try:
        row=db.execute("""SELECT detail FROM audit
                          WHERE action='production.qa_e2e.pass'
                          ORDER BY id DESC LIMIT 1""").fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def _qa_accounts():
    db=auth._db()
    try:
        rows=db.execute("SELECT id,uid,username FROM accounts WHERE username IN (?,?)",QA_USERS).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def cleanup_qa():
    accounts=_qa_accounts()
    uids=[str(r["uid"]) for r in accounts if r.get("uid")]

    db=live_service._db()
    try:
        db.execute("BEGIN IMMEDIATE")
        guilds=db.execute(
            "SELECT id FROM world_guilds WHERE name IN (?,?)" +
            (" OR owner_uid IN ("+",".join("?" for _ in uids)+")" if uids else ""),
            tuple(QA_GUILDS)+tuple(uids),
        ).fetchall()
        gids=[int(r["id"]) for r in guilds]
        if gids:
            marks=",".join("?" for _ in gids)
            wars=db.execute(f"SELECT id FROM guild_wars WHERE guild_a IN ({marks}) OR guild_b IN ({marks})",
                            tuple(gids)+tuple(gids)).fetchall()
            wids=[str(r["id"]) for r in wars]
            if wids:
                wm=",".join("?" for _ in wids)
                db.execute(f"DELETE FROM guild_war_claims WHERE war_id IN ({wm})",tuple(wids))
                db.execute(f"DELETE FROM guild_war_battles WHERE war_id IN ({wm})",tuple(wids))
                db.execute(f"DELETE FROM guild_wars WHERE id IN ({wm})",tuple(wids))
            db.execute(f"DELETE FROM world_guild_applications WHERE guild_id IN ({marks})",tuple(gids))
            db.execute(f"DELETE FROM world_guild_chat WHERE guild_id IN ({marks})",tuple(gids))
            db.execute(f"DELETE FROM world_guild_mail WHERE guild_id IN ({marks})",tuple(gids))
            db.execute(f"DELETE FROM world_guild_members WHERE guild_id IN ({marks})",tuple(gids))
            db.execute(f"DELETE FROM world_guilds WHERE id IN ({marks})",tuple(gids))

        if uids:
            marks=",".join("?" for _ in uids)
            matches=db.execute(f"SELECT id FROM pvp_matches WHERE player_a IN ({marks}) OR player_b IN ({marks})",
                               tuple(uids)+tuple(uids)).fetchall()
            mids=[str(r["id"]) for r in matches]
            if mids:
                mm=",".join("?" for _ in mids)
                db.execute(f"DELETE FROM pvp_match_peers WHERE match_id IN ({mm})",tuple(mids))
                db.execute(f"DELETE FROM pvp_matches WHERE id IN ({mm})",tuple(mids))
            for table in ("pvp_queue","pvp_ratings","pvp_season_claims","presence","leaderboard","mail","orders","players"):
                db.execute(f"DELETE FROM {table} WHERE uid IN ({marks})",tuple(uids))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    if uids and database.is_postgres():
        conn=database.acquire_postgres()
        try:
            marks=",".join("%s" for _ in uids)
            conn.execute(f"DELETE FROM player_battles WHERE uid IN ({marks})",tuple(uids))
            conn.execute(f"DELETE FROM player_profiles WHERE uid IN ({marks})",tuple(uids))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            database.release_postgres(conn)

    adb=auth._db()
    try:
        adb.execute("BEGIN IMMEDIATE")
        rows=adb.execute("SELECT id FROM accounts WHERE username IN (?,?)",QA_USERS).fetchall()
        ids=[int(r["id"]) for r in rows]
        if ids:
            marks=",".join("?" for _ in ids)
            adb.execute(f"DELETE FROM sessions WHERE account_id IN ({marks})",tuple(ids))
            adb.execute(f"DELETE FROM recovery_codes WHERE account_id IN ({marks})",tuple(ids))
            adb.execute(f"DELETE FROM accounts WHERE id IN ({marks})",tuple(ids))
        adb.commit()
    except Exception:
        adb.rollback()
        raise
    finally:
        adb.close()


def _clean_counts():
    db=live_service._db()
    try:
        row=db.execute("""SELECT
            (SELECT COUNT(*) FROM players) AS players,
            (SELECT COUNT(*) FROM world_guilds) AS guilds,
            (SELECT COUNT(*) FROM guild_wars) AS guild_wars,
            (SELECT COUNT(*) FROM pvp_matches) AS pvp_matches,
            (SELECT COUNT(*) FROM pvp_queue) AS pvp_queue""").fetchone()
        out={k:int(row[k]) for k in row.keys()}
    finally:
        db.close()
    adb=auth._db()
    try:
        out["accounts"]=int(adb.execute("SELECT COUNT(*) AS c FROM accounts").fetchone()["c"])
    finally:
        adb.close()
    return out


def run_release_qa_once():
    if _existing_pass():
        return {"skipped":True,"reason":"already_passed"}

    cleanup_qa()
    pool=PlayerEnginePool()
    created=[]
    try:
        password="Qa9!"+secrets.token_urlsafe(18)
        a=auth.register(QA_USERS[0],password,QA_NAMES[0],"S1","","GXB3-QA","127.0.0.1")
        b=auth.register(QA_USERS[1],password,QA_NAMES[1],"S1","","GXB3-QA","127.0.0.1")
        created=[a["account"]["uid"],b["account"]["uid"]]
        uid_a,uid_b=created

        # Login + session lifecycle.
        la=auth.login(QA_USERS[0],password,"S1","127.0.0.1","GXB3-QA")
        lb=auth.login(QA_USERS[1],password,"S1","127.0.0.1","GXB3-QA")
        if not auth.session(la["token"]) or not auth.session(lb["token"]):
            raise RuntimeError("QA login/session failed")

        ea=pool.get(uid_a,"S1",QA_NAMES[0])
        eb=pool.get(uid_b,"S1",QA_NAMES[1])
        sa=ea.pvp_team_snapshot(); sb=eb.pvp_team_snapshot()

        # Server-authoritative PvP: queue -> ready -> active -> real Lua battle -> rating result.
        live_service.enqueue_pvp(uid_a,"S1",QA_NAMES[0],"arena",int(ea.snapshot().get("power",0)))
        matched=live_service.enqueue_pvp(uid_b,"S1",QA_NAMES[1],"arena",int(eb.snapshot().get("power",0)))
        match=matched.get("match") or {}
        mid=str(match.get("id") or "")
        if not mid:
            raise RuntimeError("QA PvP matchmaking failed")
        live_service.heartbeat_pvp_match(mid,uid_a,True)
        ready=live_service.heartbeat_pvp_match(mid,uid_b,True)
        if ready["match"].get("status")!="active":
            raise RuntimeError("QA PvP readiness failed")
        seed=normalize_online_seed(int(match.get("seed") or 1))
        report=simulate(
            sa["team"],sb["team"],battle_id=ONLINE_BATTLE_ID,seed=seed,
            pet_a=sa.get("pet"),pet_b=sb.get("pet"),
            guild_skills_a=sa.get("guild_skills") or [],
            guild_skills_b=sb.get("guild_skills") or [],
            chime_bonus_a=sa.get("chime_bonus") or [],
            chime_bonus_b=sb.get("chime_bonus") or [],
            battle_type=1,
        )
        pvp=live_service.finish_authoritative_pvp(mid,uid_a,sa,sb,report)
        if pvp.get("status")!="finished" or not pvp.get("winner_uid"):
            raise RuntimeError("QA authoritative PvP result failed")

        # Two independent Guilds and a real authoritative Guild War battle.
        ga=live_service.create_world_guild(uid_a,"S1",QA_NAMES[0],QA_GUILDS[0],"Release QA",0)
        gb=live_service.create_world_guild(uid_b,"S1",QA_NAMES[1],QA_GUILDS[1],"Release QA",0)
        gid_a=int(ga["id"]); gid_b=int(gb["id"])
        war=live_service.schedule_guild_war(uid_a,"S1",gid_b,3600)
        wid=str(war["id"])
        db=live_service._db()
        try:
            now=int(time.time())
            db.execute("UPDATE guild_wars SET status='active',starts_at=?,ends_at=? WHERE id=?",(now-1,now+3600,wid))
            db.commit()
        finally:
            db.close()
        prep=live_service.prepare_guild_war_attack(uid_a,"S1",wid,uid_b)
        gseed=normalize_online_seed(int.from_bytes(hashlib.sha256(f"{wid}:{uid_a}:{uid_b}".encode()).digest()[:4],"big"))
        greport=simulate(
            sa["team"],sb["team"],battle_id=ONLINE_BATTLE_ID,seed=gseed,
            pet_a=sa.get("pet"),pet_b=sb.get("pet"),
            guild_skills_a=sa.get("guild_skills") or [],
            guild_skills_b=sb.get("guild_skills") or [],
            chime_bonus_a=sa.get("chime_bonus") or [],
            chime_bonus_b=sb.get("chime_bonus") or [],
            battle_type=1,
        )
        gw=live_service.record_guild_war_battle(wid,uid_a,uid_b,sa,sb,greport)
        if not gw.get("battle_id") or not gw.get("winner_uid"):
            raise RuntimeError("QA Guild War battle failed")

        # Persistence check: close every Engine and DB pool, then reconstruct from PostgreSQL.
        pool.close()
        database.close_pool()
        pool=PlayerEnginePool()
        ea2=pool.get(uid_a,"S1",QA_NAMES[0]); eb2=pool.get(uid_b,"S1",QA_NAMES[1])
        if ea2.snapshot().get("uid")!=uid_a or eb2.snapshot().get("uid")!=uid_b:
            raise RuntimeError("QA persistence reload failed")
        if live_service.pvp_match_result(mid,uid_a).get("status")!="finished":
            raise RuntimeError("QA PvP persistence failed")
        detail=live_service.guild_war_detail(uid_a,"S1",wid)
        if not detail.get("battles"):
            raise RuntimeError("QA Guild War persistence failed")

        proof={
            "ok":True,
            "pvp_match":mid,
            "pvp_winner":pvp["winner_uid"],
            "pvp_frames":len(report.get("frames") or []),
            "guild_war":wid,
            "guild_war_battle":gw["battle_id"],
            "guild_war_winner":gw["winner_uid"],
            "guild_war_frames":len(greport.get("frames") or []),
            "persistence":"reloaded_after_pool_restart",
            "checked_at":int(time.time()),
        }
    finally:
        try: pool.close()
        except Exception: pass
        cleanup_qa()

    counts=_clean_counts()
    if any(counts[k] for k in ("accounts","players","guilds","guild_wars","pvp_matches","pvp_queue")):
        raise RuntimeError(f"QA cleanup did not restore clean state: {counts}")
    if database.is_postgres():
        # Restore user-facing serial IDs as well: the first real account/Guild
        # after release should still start from the pristine sequence.
        conn=database.acquire_postgres()
        try:
            for seq in ("accounts_id_seq","world_guilds_id_seq","world_guild_chat_id_seq"):
                conn.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            database.release_postgres(conn)
    proof["post_cleanup_counts"]=counts
    db=live_service._db()
    try:
        live_service._audit(db,"production.qa_e2e.pass","SYSTEM",proof,"SYSTEM")
        db.commit()
    finally:
        db.close()
    return proof
