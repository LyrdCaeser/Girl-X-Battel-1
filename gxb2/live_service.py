from __future__ import annotations
import json
import threading
import time
import uuid
from pathlib import Path

from . import database, topup

ROOT = Path(__file__).resolve().parents[1]
PVP_SEASON_REWARDS = json.loads((ROOT / 'data/pvp_season_rewards.json').read_text())
GUILD_ONLINE_CONFIG = json.loads((ROOT / 'data/guild_online_config.json').read_text())
DB_PATH = ROOT / "state" / "live_service.sqlite3"
_lock = threading.RLock()


def _db():
    return database.connect(DB_PATH, "live")

def _audit(db, action, target, detail, operator="GM"):
    db.execute("INSERT INTO audit(at,operator,action,target,detail) VALUES(?,?,?,?,?)",
               (int(time.time()), operator, action, target, json.dumps(detail, ensure_ascii=False)))


def worlds():
    with _lock:
        db=_db()
        rows=[dict(r) for r in db.execute("SELECT * FROM worlds ORDER BY created_at, server_id")]
        db.close(); return rows


def create_world(server_id, name):
    server_id=str(server_id or '').strip().upper()
    name=str(name or '').strip()
    if not server_id or len(server_id)>16 or not server_id.replace('-','').isalnum():
        raise ValueError("Server ID không hợp lệ")
    if not name or len(name)>60: raise ValueError("Tên server không hợp lệ")
    with _lock:
        db=_db(); now=int(time.time())
        db.execute("INSERT INTO worlds(server_id,name,status,created_at) VALUES(?,?, 'online',?)",(server_id,name,now))
        _audit(db,"world.create",server_id,{"name":name})
        db.commit(); db.close()
    return {"server_id":server_id,"name":name,"status":"online","created_at":now,
            "registration_open":1,"character_creation_open":1,"message":""}


def set_world_status(server_id,status):
    status=str(status or '').lower()
    if status not in ("online","maintenance","closed"): raise ValueError("Trạng thái server không hợp lệ")
    with _lock:
        db=_db(); cur=db.execute("UPDATE worlds SET status=? WHERE server_id=?",(status,server_id))
        if not cur.rowcount: db.close(); raise ValueError("Không tìm thấy server")
        _audit(db,"world.status",server_id,{"status":status}); db.commit(); db.close()
    return {"server_id":server_id,"status":status}


def register_player(uid, server_id, character_name):
    uid=str(uid or '').strip()
    server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip()
    if not uid or len(uid)>64: raise ValueError("UID không hợp lệ")
    if not character_name or len(character_name)>40: raise ValueError("Tên nhân vật không hợp lệ")
    now=int(time.time())
    with _lock:
        db=_db()
        if not db.execute("SELECT 1 FROM worlds WHERE server_id=?",(server_id,)).fetchone():
            db.close(); raise ValueError("Server không tồn tại")
        db.execute("""INSERT INTO players(uid,server_id,character_name,status,ban_reason,created_at,updated_at)
            VALUES(?,?,?,'active','',?,?)
            ON CONFLICT(uid,server_id) DO UPDATE SET character_name=excluded.character_name,updated_at=excluded.updated_at""",
            (uid,server_id,character_name,now,now))
        db.commit(); db.close()
    return player(uid,server_id)


def player(uid,server_id):
    with _lock:
        db=_db(); row=db.execute("SELECT * FROM players WHERE uid=? AND server_id=?",(str(uid),str(server_id).upper())).fetchone()
        db.close(); return dict(row) if row else None


def players(query=""):
    q=str(query or '').strip()
    with _lock:
        db=_db()
        if q:
            like=f"%{q}%"
            rows=db.execute("""SELECT * FROM players WHERE uid LIKE ? OR character_name LIKE ? OR server_id LIKE ?
                               ORDER BY updated_at DESC LIMIT 200""",(like,like,like)).fetchall()
        else:
            rows=db.execute("SELECT * FROM players ORDER BY updated_at DESC LIMIT 200").fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def set_ban(uid,server_id,banned,reason=""):
    with _lock:
        db=_db()
        status="banned" if banned else "active"
        cur=db.execute("UPDATE players SET status=?,ban_reason=?,updated_at=? WHERE uid=? AND server_id=?",
                       (status,str(reason or '')[:300] if banned else '',int(time.time()),str(uid),str(server_id).upper()))
        if not cur.rowcount: db.close(); raise ValueError("Không tìm thấy người chơi")
        _audit(db,"player.ban" if banned else "player.unban",f"{server_id}:{uid}",{"reason":reason})
        db.commit(); db.close()
    return player(uid,server_id)


def send_mail(uid,server_id,character_name,title,body,attachments,operator="GM"):
    if not isinstance(attachments,dict): raise ValueError("attachments phải là object {item_id: amount}")
    clean={}
    for k,v in attachments.items():
        item=str(int(k)); amount=int(v)
        if amount<0 or amount>2_000_000_000: raise ValueError("Số lượng vật phẩm không hợp lệ")
        if amount: clean[item]=amount
    if not clean: raise ValueError("Thư phải có ít nhất một vật phẩm")
    target=player(uid,server_id)
    if not target: raise ValueError("Không tìm thấy UID/Server")
    if character_name and target["character_name"].casefold()!=str(character_name).strip().casefold():
        raise ValueError("Tên Nhân Vật không khớp UID + Server")
    mid="MAIL-"+uuid.uuid4().hex[:16].upper(); now=int(time.time())
    with _lock:
        db=_db()
        db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                      VALUES(?,?,?,?,?,?,?,'pending',?,?)""",
                   (mid,str(uid),str(server_id).upper(),target["character_name"],str(title or "Quà từ GM")[:100],
                    str(body or '')[:1000],json.dumps(clean),now,operator))
        _audit(db,"mail.send",f"{server_id}:{uid}",{"mail_id":mid,"attachments":clean},operator)
        db.commit(); db.close()
    return {"id":mid,"uid":str(uid),"server_id":str(server_id).upper(),"character_name":target["character_name"],
            "title":str(title or "Quà từ GM"),"body":str(body or ''),"attachments":clean,"status":"pending","created_at":now}


def mailbox(uid,server_id):
    with _lock:
        db=_db()
        rows=db.execute("SELECT * FROM mail WHERE uid=? AND server_id=? ORDER BY created_at DESC",
                        (str(uid),str(server_id).upper())).fetchall()
        out=[]
        for r in rows:
            d=dict(r); d["attachments"]=json.loads(d["attachments"]); out.append(d)
        db.close(); return out


def claim_mail(mail_id,uid,server_id):
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM mail WHERE id=? AND uid=? AND server_id=?",(mail_id,str(uid),str(server_id).upper())).fetchone()
        if not row: db.rollback();db.close();raise ValueError("Không tìm thấy thư")
        if row["status"]!="pending": db.rollback();db.close();raise ValueError("Thư đã được nhận")
        attachments=json.loads(row["attachments"])
        now=int(time.time())
        db.execute("UPDATE mail SET status='claimed',claimed_at=? WHERE id=?",(now,mail_id))
        _audit(db,"mail.claim",f"{server_id}:{uid}",{"mail_id":mail_id})
        db.commit(); db.close()
        return attachments


def create_order(uid,server_id,character_name,package,note=""):
    target=player(uid,server_id)
    if not target: raise ValueError("Không tìm thấy UID/Server")
    if target["status"]=="banned": raise ValueError("Tài khoản đang bị khóa")
    if target["character_name"].casefold()!=str(character_name or '').strip().casefold():
        raise ValueError("Tên Nhân Vật không khớp UID + Server")
    requested=str(package or '').strip()
    pkg=topup.package(requested)
    note=str(note or '')[:500]
    if not pkg:
        custom=topup.package("CUSTOM")
        if not custom or not custom.get("manual_reward"):
            raise ValueError("Gói nạp không tồn tại hoặc đang tạm khóa")
        pkg=custom
        if requested and requested.upper()!="CUSTOM":
            note=(f"Yêu cầu gói: {requested}\n"+note)[:500]
    oid="ORD-"+uuid.uuid4().hex[:14].upper(); now=int(time.time())
    expected={str(k):int(v) for k,v in (pkg.get("reward") or {}).items() if int(v)>0}
    with _lock:
        db=_db()
        db.execute("""INSERT INTO orders(
                      id,uid,server_id,character_name,package,package_name,price_label,manual_reward,
                      note,status,reward,created_at)
                      VALUES(?,?,?,?,?,?,?,?,?,'pending',?,?)""",
                   (oid,str(uid),str(server_id).upper(),target["character_name"],pkg["id"],pkg["name"],
                    pkg.get("price_label",""),1 if pkg.get("manual_reward") else 0,note,
                    json.dumps(expected,ensure_ascii=False),now))
        _audit(db,"order.create",f"{server_id}:{uid}",
               {"order_id":oid,"package":pkg["id"],"package_name":pkg["name"],"manual_reward":bool(pkg.get("manual_reward"))},"PLAYER")
        db.commit(); db.close()
    return order(oid)


def order(order_id):
    with _lock:
        db=_db(); row=db.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone(); db.close()
        if not row:return None
        d=dict(row); d["reward"]=json.loads(d["reward"]); return d


def orders(status=""):
    with _lock:
        db=_db()
        if status: rows=db.execute("SELECT * FROM orders WHERE status=? ORDER BY created_at DESC",(status,)).fetchall()
        else: rows=db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 300").fetchall()
        out=[]
        for r in rows:
            d=dict(r); d["reward"]=json.loads(d["reward"]); out.append(d)
        db.close(); return out


def review_order(order_id,approve,reward=None,reviewer="GM"):
    reward=reward or {}
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone()
        if not row: db.rollback();db.close();raise ValueError("Không tìm thấy đơn")
        if row["status"]!="pending": db.rollback();db.close();raise ValueError("Đơn đã được xử lý")
        clean={}
        if approve:
            manual=bool(int(row["manual_reward"] or 0))
            source=reward if manual else json.loads(row["reward"] or "{}")
            if not isinstance(source,dict): source={}
            for k,v in source.items():
                item=str(int(k)); amount=int(v)
                if amount<0 or amount>2_000_000_000:
                    db.rollback();db.close();raise ValueError("Số lượng vật phẩm không hợp lệ")
                if amount: clean[item]=amount
            if not clean:
                db.rollback();db.close()
                raise ValueError("Đơn duyệt phải có reward")
        status="approved" if approve else "rejected"; now=int(time.time())
        db.execute("UPDATE orders SET status=?,reward=?,reviewed_at=?,reviewer=? WHERE id=?",
                   (status,json.dumps(clean),now,reviewer,order_id))
        _audit(db,"order."+status,f"{row['server_id']}:{row['uid']}",
               {"order_id":order_id,"package":row["package"],"reward":clean},reviewer)
        db.commit(); db.close()
    if approve:
        send_mail(row["uid"],row["server_id"],row["character_name"],"Nạp thành công",
                  f"Đơn {order_id} · {row['package_name'] or row['package']} đã được QTV duyệt.",clean,reviewer)
    return order(order_id)


def audit(limit=200):
    with _lock:
        db=_db(); rows=[dict(r) for r in db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",(int(limit),))]
        for r in rows:
            try:r["detail"]=json.loads(r["detail"])
            except Exception:pass
        db.close(); return rows


def set_world_policy(server_id, registration_open=None, character_creation_open=None, message=None):
    server_id=str(server_id or '').strip().upper()
    fields=[]; values=[]
    if registration_open is not None:
        fields.append("registration_open=?"); values.append(1 if bool(registration_open) else 0)
    if character_creation_open is not None:
        fields.append("character_creation_open=?"); values.append(1 if bool(character_creation_open) else 0)
    if message is not None:
        fields.append("message=?"); values.append(str(message)[:300])
    if not fields: raise ValueError("Không có policy nào để cập nhật")
    with _lock:
        db=_db()
        values.append(server_id)
        cur=db.execute(f"UPDATE worlds SET {', '.join(fields)} WHERE server_id=?", values)
        if not cur.rowcount:
            db.close(); raise ValueError("Không tìm thấy server")
        _audit(db,"world.policy",server_id,{
            "registration_open": registration_open,
            "character_creation_open": character_creation_open,
            "message": message,
        })
        db.commit()
        row=db.execute("SELECT * FROM worlds WHERE server_id=?",(server_id,)).fetchone()
        out=dict(row); db.close(); return out


def touch_presence(uid, server_id, character_name, level=1, power=0):
    uid=str(uid or '').strip()
    server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip()
    now=int(time.time())
    with _lock:
        db=_db()
        db.execute("""INSERT INTO presence(uid,server_id,character_name,last_seen)
                      VALUES(?,?,?,?)
                      ON CONFLICT(uid,server_id) DO UPDATE SET
                        character_name=excluded.character_name,
                        last_seen=excluded.last_seen""",
                   (uid,server_id,character_name,now))
        db.execute("""INSERT INTO leaderboard(uid,server_id,character_name,level,power,updated_at)
                      VALUES(?,?,?,?,?,?)
                      ON CONFLICT(uid,server_id) DO UPDATE SET
                        character_name=excluded.character_name,
                        level=excluded.level,
                        power=excluded.power,
                        updated_at=excluded.updated_at""",
                   (uid,server_id,character_name,max(1,int(level)),max(0,int(power)),now))
        db.commit(); db.close()
    return {"uid":uid,"server_id":server_id,"last_seen":now}


def online_players(server_id="", max_age=120):
    cutoff=int(time.time())-max(15,int(max_age))
    with _lock:
        db=_db()
        if server_id:
            rows=db.execute("""SELECT p.uid,p.server_id,p.character_name,p.last_seen,l.level,l.power
                               FROM presence p
                               LEFT JOIN leaderboard l ON l.uid=p.uid AND l.server_id=p.server_id
                               WHERE p.server_id=? AND p.last_seen>=?
                               ORDER BY p.last_seen DESC LIMIT 500""",
                            (str(server_id).upper(),cutoff)).fetchall()
        else:
            rows=db.execute("""SELECT p.uid,p.server_id,p.character_name,p.last_seen,l.level,l.power
                               FROM presence p
                               LEFT JOIN leaderboard l ON l.uid=p.uid AND l.server_id=p.server_id
                               WHERE p.last_seen>=?
                               ORDER BY p.last_seen DESC LIMIT 500""",
                            (cutoff,)).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def leaderboard(server_id, limit=100):
    limit=max(1,min(500,int(limit)))
    with _lock:
        db=_db()
        rows=db.execute("""SELECT uid,server_id,character_name,level,power,updated_at
                           FROM leaderboard WHERE server_id=?
                           ORDER BY power DESC, level DESC, updated_at ASC LIMIT ?""",
                        (str(server_id).upper(),limit)).fetchall()
        out=[]
        for idx,r in enumerate(rows,1):
            d=dict(r); d["rank"]=idx; out.append(d)
        db.close(); return out


def _guild_row(db, guild_id):
    row=db.execute("SELECT * FROM world_guilds WHERE id=?",(int(guild_id),)).fetchone()
    return dict(row) if row else None


def guild_for_player(uid, server_id):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    with _lock:
        db=_db()
        row=db.execute("""SELECT g.*,m.role,m.power AS member_power,m.joined_at
                          FROM world_guild_members m
                          JOIN world_guilds g ON g.id=m.guild_id
                          WHERE m.uid=? AND m.server_id=?""",(uid,server_id)).fetchone()
        if not row:
            db.close(); return None
        out=dict(row)
        members=db.execute("""SELECT uid,server_id,character_name,role,power,contribution,joined_at,last_seen
                              FROM world_guild_members WHERE guild_id=?
                              ORDER BY CASE role WHEN 'leader' THEN 0 WHEN 'deputy' THEN 1 ELSE 2 END,
                                       contribution DESC,power DESC,joined_at""",(int(out["id"]),)).fetchall()
        out["members"]=[dict(r) for r in members]
        out["member_count"]=len(out["members"])
        db.close(); return out


def world_guilds(server_id, limit=100):
    server_id=str(server_id or '').strip().upper()
    limit=max(1,min(200,int(limit)))
    with _lock:
        db=_db()
        rows=db.execute("""SELECT g.*,
                            (SELECT COUNT(*) FROM world_guild_members m WHERE m.guild_id=g.id) AS member_count
                           FROM world_guilds g WHERE g.server_id=?
                           ORDER BY g.level DESC,g.exp DESC,g.created_at ASC LIMIT ?""",
                        (server_id,limit)).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def create_world_guild(uid, server_id, character_name, name, notice="", power=0):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip(); name=str(name or '').strip()
    notice=str(notice or '').strip()[:180]
    if not 3 <= len(name) <= 24: raise ValueError("Tên Guild phải dài 3–24 ký tự")
    if not character_name: raise ValueError("Tên Nhân Vật không hợp lệ")
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM world_guild_members WHERE uid=? AND server_id=?",(uid,server_id)).fetchone():
            db.rollback(); db.close(); raise ValueError("Bạn đã ở trong một Guild")
        try:
            if db.backend=="postgres":
                cur=db.execute("""INSERT INTO world_guilds(server_id,name,notice,owner_uid,level,exp,created_at)
                                  VALUES(?,?,?, ?,1,0,?) RETURNING id""",(server_id,name,notice,uid,now))
                guild_id=int(cur.fetchone()["id"])
            else:
                cur=db.execute("""INSERT INTO world_guilds(server_id,name,notice,owner_uid,level,exp,created_at)
                                  VALUES(?,?,?, ?,1,0,?)""",(server_id,name,notice,uid,now))
                guild_id=int(cur.lastrowid)
        except database.IntegrityError:
            db.rollback(); db.close(); raise ValueError("Tên Guild đã tồn tại trong server này")
        db.execute("""INSERT INTO world_guild_members(guild_id,uid,server_id,character_name,role,power,joined_at,last_seen)
                      VALUES(?,?,?,?, 'leader',?,?,?)""",
                   (guild_id,uid,server_id,character_name,max(0,int(power)),now,now))
        _audit(db,"guild.create",f"{server_id}:{guild_id}",{"uid":uid,"name":name},"PLAYER")
        db.commit(); db.close()
    return guild_for_player(uid,server_id)


def join_world_guild(uid, server_id, character_name, guild_id, power=0):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip(); guild_id=int(guild_id)
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM world_guild_members WHERE uid=? AND server_id=?",(uid,server_id)).fetchone():
            db.rollback(); db.close(); raise ValueError("Bạn đã ở trong một Guild")
        guild=db.execute("SELECT * FROM world_guilds WHERE id=? AND server_id=?",(guild_id,server_id)).fetchone()
        if not guild:
            db.rollback(); db.close(); raise ValueError("Guild không tồn tại trong server này")
        count=int(db.execute("SELECT COUNT(*) AS c FROM world_guild_members WHERE guild_id=?",(guild_id,)).fetchone()["c"])
        capacity=20+max(0,int(guild["level"])-1)*2
        if count>=capacity:
            db.rollback(); db.close(); raise ValueError("Guild đã đầy")
        db.execute("""INSERT INTO world_guild_members(guild_id,uid,server_id,character_name,role,power,joined_at,last_seen)
                      VALUES(?,?,?,?, 'member',?,?,?)""",
                   (guild_id,uid,server_id,character_name,max(0,int(power)),now,now))
        _audit(db,"guild.join",f"{server_id}:{guild_id}",{"uid":uid},"PLAYER")
        db.commit(); db.close()
    return guild_for_player(uid,server_id)


def leave_world_guild(uid, server_id):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        member=db.execute("""SELECT m.*,g.owner_uid FROM world_guild_members m
                             JOIN world_guilds g ON g.id=m.guild_id
                             WHERE m.uid=? AND m.server_id=?""",(uid,server_id)).fetchone()
        if not member:
            db.rollback(); db.close(); raise ValueError("Bạn chưa ở trong Guild")
        if member["role"]=="leader" or member["owner_uid"]==uid:
            count=int(db.execute("SELECT COUNT(*) AS c FROM world_guild_members WHERE guild_id=?",(int(member["guild_id"]),)).fetchone()["c"])
            if count>1:
                db.rollback(); db.close(); raise ValueError("Leader phải chuyển quyền hoặc chỉ còn một mình mới có thể giải tán")
            db.execute("DELETE FROM world_guilds WHERE id=?",(int(member["guild_id"]),))
            action="guild.disband"
        else:
            db.execute("DELETE FROM world_guild_members WHERE uid=? AND server_id=?",(uid,server_id))
            action="guild.leave"
        _audit(db,action,f"{server_id}:{member['guild_id']}",{"uid":uid},"PLAYER")
        db.commit(); db.close()
    return {"ok":True}


def update_world_guild_member(uid, server_id, character_name, power=0):
    now=int(time.time())
    with _lock:
        db=_db()
        db.execute("""UPDATE world_guild_members SET character_name=?,power=?,last_seen=?
                      WHERE uid=? AND server_id=?""",
                   (str(character_name or '')[:40],max(0,int(power)),now,str(uid),str(server_id).upper()))
        db.commit(); db.close()


def _public_pvp_match(row, include_result=False):
    """Serialize a PvP match without exposing internal RNG/snapshots before finish."""
    data=dict(row)
    out={key:data.get(key) for key in (
        "id","mode","server_id","server_a","server_b",
        "player_a","player_b","name_a","name_b","power_a","power_b",
        "status","winner_uid","created_at","resolved_at",
        "rating_delta_a","rating_delta_b",
    )}
    if include_result and str(data.get("status"))=="finished":
        for key in ("snapshot_a","snapshot_b","battle_report"):
            try:
                out[key]=json.loads(data.get(key) or "{}")
            except Exception:
                out[key]={}
    return out


def pvp_match_internal(match_id, uid):
    """Server-only raw match lookup. Never return this object directly to clients."""
    match_id=str(match_id or "").strip(); uid=str(uid or "").strip()
    with _lock:
        db=_db()
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        if not row:
            db.close(); raise ValueError("Không tìm thấy trận PvP")
        if uid not in (row["player_a"],row["player_b"]):
            db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        out=dict(row); db.close(); return out


def enqueue_pvp(uid, server_id, character_name, mode, power=0):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip()
    mode=str(mode or 'arena').strip().lower()
    if mode not in ("arena","team","cross"): raise ValueError("Chế độ PvP không hợp lệ")
    power=max(0,int(power)); now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        existing=db.execute("""SELECT * FROM pvp_matches
                               WHERE status IN ('ready','active') AND (player_a=? OR player_b=?)
                               ORDER BY created_at DESC LIMIT 1""",(uid,uid)).fetchone()
        if existing:
            out=_public_pvp_match(existing); db.commit(); db.close(); return {"status":"matched","match":out}
        db.execute("""INSERT INTO pvp_queue(uid,server_id,character_name,mode,power,joined_at,status)
                      VALUES(?,?,?,?,?,?,'waiting')
                      ON CONFLICT(uid,server_id,mode) DO UPDATE SET
                        character_name=excluded.character_name,power=excluded.power,
                        joined_at=excluded.joined_at,status='waiting'""",
                   (uid,server_id,character_name,mode,power,now))
        if mode=="cross":
            opponent=db.execute("""SELECT * FROM pvp_queue
                                   WHERE mode=? AND status='waiting' AND uid<>?
                                   ORDER BY ABS(power-?),joined_at LIMIT 1""",
                                (mode,uid,power)).fetchone()
        else:
            opponent=db.execute("""SELECT * FROM pvp_queue
                                   WHERE mode=? AND status='waiting' AND server_id=? AND uid<>?
                                   ORDER BY ABS(power-?),joined_at LIMIT 1""",
                                (mode,server_id,uid,power)).fetchone()
        if opponent:
            match_id="PVP-"+uuid.uuid4().hex[:16].upper()
            seed=normalize_online_seed(uuid.uuid4().int)
            match_server="CROSS" if mode=="cross" else server_id
            db.execute("""INSERT INTO pvp_matches(
                          id,mode,server_id,server_a,server_b,player_a,player_b,name_a,name_b,power_a,power_b,
                          status,winner_uid,created_at,resolved_at,seed,snapshot_a,snapshot_b,battle_report,rating_delta_a,rating_delta_b)
                          VALUES(?,?,?,?,?,?,?,?,?,?,?,'ready','',?,0,?,'{}','{}','{}',0,0)""",
                       (match_id,mode,match_server,str(opponent["server_id"]).upper(),server_id,
                        str(opponent["uid"]),uid,str(opponent["character_name"]),character_name,
                        int(opponent["power"]),power,now,seed))
            db.execute("DELETE FROM pvp_queue WHERE (uid=? AND server_id=? AND mode=?) OR (uid=? AND server_id=? AND mode=?)",
                       (uid,server_id,mode,str(opponent["uid"]),str(opponent["server_id"]),mode))
            _audit(db,"pvp.match",match_id,{"mode":mode,"a":opponent["uid"],"b":uid},"SYSTEM")
            row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
            out={"status":"matched","match":_public_pvp_match(row)}
        else:
            out={"status":"waiting","joined_at":now}
        db.commit(); db.close(); return out


def cancel_pvp(uid, server_id, mode):
    with _lock:
        db=_db()
        db.execute("DELETE FROM pvp_queue WHERE uid=? AND server_id=? AND mode=?",
                   (str(uid),str(server_id).upper(),str(mode).lower()))
        db.commit(); db.close()
    return {"ok":True}


def pvp_status(uid, server_id, mode=""):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper(); mode=str(mode or '').lower()
    with _lock:
        db=_db()
        match=db.execute("""SELECT * FROM pvp_matches
                            WHERE (player_a=? OR player_b=?) AND status IN ('ready','active')
                            ORDER BY created_at DESC LIMIT 1""",(uid,uid)).fetchone()
        if match:
            out={"status":"matched","match":_public_pvp_match(match)}
        else:
            if mode:
                q=db.execute("SELECT * FROM pvp_queue WHERE uid=? AND server_id=? AND mode=?",(uid,server_id,mode)).fetchone()
            else:
                q=db.execute("SELECT * FROM pvp_queue WHERE uid=? AND server_id=? ORDER BY joined_at DESC LIMIT 1",(uid,server_id)).fetchone()
            out={"status":"waiting","queue":dict(q)} if q else {"status":"idle"}
        db.close(); return out


def activate_pvp_match(match_id, uid):
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        if not row:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy trận PvP")
        if uid not in (row["player_a"],row["player_b"]):
            db.rollback(); db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        if row["status"]=="ready":
            db.execute("UPDATE pvp_matches SET status='active' WHERE id=?",(str(match_id),))
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        db.commit(); out=_public_pvp_match(row); db.close(); return out


def resolve_pvp_match(match_id, uid, winner_uid):
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        if not row:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy trận PvP")
        if uid not in (row["player_a"],row["player_b"]):
            db.rollback(); db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        if winner_uid not in (row["player_a"],row["player_b"]):
            db.rollback(); db.close(); raise ValueError("Winner không hợp lệ")
        if row["status"]=="finished":
            out=_public_pvp_match(row, include_result=True); db.commit(); db.close(); return out
        now=int(time.time())
        db.execute("UPDATE pvp_matches SET status='finished',winner_uid=?,resolved_at=? WHERE id=?",
                   (str(winner_uid),now,str(match_id)))
        _audit(db,"pvp.finish",str(match_id),{"winner":winner_uid},"SYSTEM")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        db.commit(); out=_public_pvp_match(row, include_result=True); db.close(); return out


def pvp_history(uid, limit=50):
    limit=max(1,min(200,int(limit)))
    with _lock:
        db=_db()
        rows=db.execute("""SELECT id,mode,server_id,server_a,server_b,player_a,player_b,name_a,name_b,
                                  power_a,power_b,status,winner_uid,created_at,resolved_at,
                                  rating_delta_a,rating_delta_b
                           FROM pvp_matches
                           WHERE player_a=? OR player_b=?
                           ORDER BY created_at DESC LIMIT ?""",(str(uid),str(uid),limit)).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def heartbeat_pvp_match(match_id, uid, ready=True):
    match_id=str(match_id or '').strip(); uid=str(uid or '').strip(); now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        if not row:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy trận PvP")
        if uid not in (row["player_a"],row["player_b"]):
            db.rollback(); db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        db.execute("""INSERT INTO pvp_match_peers(match_id,uid,ready,last_seen)
                      VALUES(?,?,?,?)
                      ON CONFLICT(match_id,uid) DO UPDATE SET
                        ready=excluded.ready,last_seen=excluded.last_seen""",
                   (match_id,uid,1 if ready else 0,now))
        peers=db.execute("SELECT uid,ready,last_seen FROM pvp_match_peers WHERE match_id=?",(match_id,)).fetchall()
        online_cutoff=now-15
        all_ready=len(peers)>=2 and all(int(p["ready"]) and int(p["last_seen"])>=online_cutoff for p in peers)
        if all_ready and row["status"]=="ready":
            db.execute("UPDATE pvp_matches SET status='active' WHERE id=?",(match_id,))
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        db.commit()
        out={"match":_public_pvp_match(row),"peers":[dict(p) for p in peers],"all_ready":all_ready}
        db.close(); return out


def pvp_match_session(match_id, uid):
    match_id=str(match_id or '').strip(); uid=str(uid or '').strip(); now=int(time.time())
    with _lock:
        db=_db()
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        if not row:
            db.close(); raise ValueError("Không tìm thấy trận PvP")
        if uid not in (row["player_a"],row["player_b"]):
            db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        peers=db.execute("SELECT uid,ready,last_seen FROM pvp_match_peers WHERE match_id=?",(match_id,)).fetchall()
        out={"match":_public_pvp_match(row),"peers":[dict(p) for p in peers],"server_time":now}
        db.close(); return out


def current_pvp_season(now=None):
    t=time.gmtime(int(now or time.time()))
    return f"{t.tm_year:04d}-{t.tm_mon:02d}"


def pvp_rating(uid, server_id, mode, season_id=None):
    season_id=season_id or current_pvp_season()
    with _lock:
        db=_db()
        row=db.execute("""SELECT * FROM pvp_ratings
                          WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                       (str(uid),str(server_id).upper(),str(mode).lower(),season_id)).fetchone()
        if not row:
            out={"uid":str(uid),"server_id":str(server_id).upper(),"mode":str(mode).lower(),
                 "season_id":season_id,"rating":1000,"wins":0,"losses":0,"matches":0}
        else:
            out=dict(row)
        db.close(); return out


def pvp_rating_board(mode, season_id=None, limit=100):
    mode=str(mode or "arena").lower()
    season_id=season_id or current_pvp_season()
    limit=max(1,min(500,int(limit)))
    with _lock:
        db=_db()
        rows=db.execute("""SELECT r.*,p.character_name
                           FROM pvp_ratings r
                           LEFT JOIN players p ON p.uid=r.uid AND p.server_id=r.server_id
                           WHERE r.mode=? AND r.season_id=?
                           ORDER BY r.rating DESC,r.wins DESC,r.matches ASC,r.updated_at ASC LIMIT ?""",
                        (mode,season_id,limit)).fetchall()
        out=[]
        for idx,row in enumerate(rows,1):
            d=dict(row); d["rank"]=idx; out.append(d)
        db.close(); return out


def _ensure_rating(db, uid, server_id, mode, season_id, now):
    db.execute("""INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at)
                  VALUES(?,?,?,?,1000,0,0,0,?)
                  ON CONFLICT(uid,server_id,mode,season_id) DO NOTHING""",
               (uid,server_id,mode,season_id,now))


def _elo_delta(rating_a, rating_b, a_won, k=32):
    expected=1.0/(1.0+10**((float(rating_b)-float(rating_a))/400.0))
    score=1.0 if a_won else 0.0
    return int(round(k*(score-expected)))


def finish_authoritative_pvp(match_id, requester_uid, snapshot_a, snapshot_b, report):
    match_id=str(match_id or "").strip()
    requester_uid=str(requester_uid or "").strip()
    if not isinstance(snapshot_a,dict) or not isinstance(snapshot_b,dict) or not isinstance(report,dict):
        raise ValueError("PvP result payload không hợp lệ")
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        if not row:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy trận PvP")
        if requester_uid not in (row["player_a"],row["player_b"]):
            db.rollback(); db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        if row["status"]=="finished":
            out=_public_pvp_match(row, include_result=True)
            db.commit(); db.close(); return out
        if row["status"] not in ("ready","active"):
            db.rollback(); db.close(); raise ValueError("Trận PvP không ở trạng thái có thể xử lý")
        if report.get("isWin") not in (0,1):
            db.rollback(); db.close(); raise ValueError("Battle report không hợp lệ")
        winner_uid=row["player_a"] if int(report["isWin"])==1 else row["player_b"]
        season_id=current_pvp_season()
        server_a=(row["server_a"] or row["server_id"] or snapshot_a.get("server_id") or "").upper()
        server_b=(row["server_b"] or row["server_id"] or snapshot_b.get("server_id") or "").upper()
        mode=str(row["mode"])
        now=int(time.time())
        _ensure_rating(db,row["player_a"],server_a,mode,season_id,now)
        _ensure_rating(db,row["player_b"],server_b,mode,season_id,now)
        ra=db.execute("""SELECT * FROM pvp_ratings WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                      (row["player_a"],server_a,mode,season_id)).fetchone()
        rb=db.execute("""SELECT * FROM pvp_ratings WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                      (row["player_b"],server_b,mode,season_id)).fetchone()
        a_won=winner_uid==row["player_a"]
        delta_a=_elo_delta(int(ra["rating"]),int(rb["rating"]),a_won)
        delta_b=-delta_a
        db.execute("""UPDATE pvp_ratings
                      SET rating=rating+?,wins=wins+?,losses=losses+?,matches=matches+1,updated_at=?
                      WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                   (delta_a,1 if a_won else 0,0 if a_won else 1,now,row["player_a"],server_a,mode,season_id))
        db.execute("""UPDATE pvp_ratings
                      SET rating=rating+?,wins=wins+?,losses=losses+?,matches=matches+1,updated_at=?
                      WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                   (delta_b,0 if a_won else 1,1 if a_won else 0,now,row["player_b"],server_b,mode,season_id))
        db.execute("""UPDATE pvp_matches SET
                      status='finished',winner_uid=?,resolved_at=?,
                      snapshot_a=?,snapshot_b=?,battle_report=?,
                      rating_delta_a=?,rating_delta_b=?
                      WHERE id=?""",
                   (winner_uid,now,json.dumps(snapshot_a,ensure_ascii=False),json.dumps(snapshot_b,ensure_ascii=False),
                    json.dumps(report,ensure_ascii=False),delta_a,delta_b,match_id))
        _audit(db,"pvp.authoritative_finish",match_id,{
            "winner":winner_uid,"mode":mode,"season":season_id,
            "rating_delta_a":delta_a,"rating_delta_b":delta_b,
        },"SYSTEM")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
        db.commit()
        out=_public_pvp_match(row, include_result=True)
        db.close(); return out


def pvp_match_result(match_id, uid):
    with _lock:
        db=_db()
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        if not row:
            db.close(); raise ValueError("Không tìm thấy trận PvP")
        if str(uid) not in (row["player_a"],row["player_b"]):
            db.close(); raise ValueError("Bạn không thuộc trận PvP này")
        out=_public_pvp_match(row, include_result=True)
        db.close(); return out


def _guild_member(db, uid, server_id):
    row=db.execute("""SELECT m.*,g.owner_uid,g.name AS guild_name,g.server_id AS guild_server
                      FROM world_guild_members m
                      JOIN world_guilds g ON g.id=m.guild_id
                      WHERE m.uid=? AND m.server_id=?""",
                   (str(uid),str(server_id).upper())).fetchone()
    return dict(row) if row else None


def _require_guild_role(db, uid, server_id, allowed):
    member=_guild_member(db,uid,server_id)
    if not member: raise ValueError("Bạn chưa ở trong Guild")
    if member["role"] not in tuple(allowed):
        raise ValueError("Bạn không có quyền thực hiện thao tác này")
    return member


def apply_world_guild(uid, server_id, character_name, guild_id, power=0):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip(); guild_id=int(guild_id); now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM world_guild_members WHERE uid=? AND server_id=?",(uid,server_id)).fetchone():
            db.rollback(); db.close(); raise ValueError("Bạn đã ở trong một Guild")
        if not db.execute("SELECT 1 FROM world_guilds WHERE id=? AND server_id=?",(guild_id,server_id)).fetchone():
            db.rollback(); db.close(); raise ValueError("Guild không tồn tại")
        db.execute("""INSERT INTO world_guild_applications(guild_id,uid,server_id,character_name,power,created_at,status)
                      VALUES(?,?,?,?,?,?,'pending')
                      ON CONFLICT(guild_id,uid) DO UPDATE SET
                        character_name=excluded.character_name,power=excluded.power,
                        created_at=excluded.created_at,status='pending'""",
                   (guild_id,uid,server_id,character_name,max(0,int(power)),now))
        _audit(db,"guild.apply",f"{server_id}:{guild_id}",{"uid":uid},"PLAYER")
        db.commit(); db.close()
    return {"ok":True}


def guild_applications(uid, server_id):
    with _lock:
        db=_db()
        member=_require_guild_role(db,uid,server_id,("leader","deputy"))
        rows=db.execute("""SELECT guild_id,uid,server_id,character_name,power,created_at,status
                           FROM world_guild_applications
                           WHERE guild_id=? AND status='pending'
                           ORDER BY power DESC,created_at ASC""",(int(member["guild_id"]),)).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def review_guild_application(operator_uid, server_id, applicant_uid, approve):
    server_id=str(server_id or '').upper(); applicant_uid=str(applicant_uid or '')
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        member=_require_guild_role(db,operator_uid,server_id,("leader","deputy"))
        app=db.execute("""SELECT * FROM world_guild_applications
                          WHERE guild_id=? AND uid=? AND status='pending'""",
                       (int(member["guild_id"]),applicant_uid)).fetchone()
        if not app:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy đơn xin vào Guild")
        status="approved" if approve else "rejected"
        if approve:
            if db.execute("SELECT 1 FROM world_guild_members WHERE uid=? AND server_id=?",(applicant_uid,server_id)).fetchone():
                db.execute("UPDATE world_guild_applications SET status='rejected' WHERE guild_id=? AND uid=?",
                           (int(member["guild_id"]),applicant_uid))
                db.commit(); db.close(); raise ValueError("Người chơi đã ở Guild khác")
            guild=db.execute("SELECT * FROM world_guilds WHERE id=?",(int(member["guild_id"]),)).fetchone()
            count=int(db.execute("SELECT COUNT(*) AS c FROM world_guild_members WHERE guild_id=?",(int(member["guild_id"]),)).fetchone()["c"])
            capacity=20+max(0,int(guild["level"])-1)*2
            if count>=capacity:
                db.rollback(); db.close(); raise ValueError("Guild đã đầy")
            now=int(time.time())
            db.execute("""INSERT INTO world_guild_members(guild_id,uid,server_id,character_name,role,power,joined_at,last_seen)
                          VALUES(?,?,?,?, 'member',?,?,?)""",
                       (int(member["guild_id"]),applicant_uid,server_id,app["character_name"],int(app["power"]),now,now))
            db.execute("""UPDATE world_guild_applications SET status='approved'
                          WHERE guild_id=? AND uid=?""",(int(member["guild_id"]),applicant_uid))
            db.execute("""UPDATE world_guild_applications SET status='rejected'
                          WHERE uid=? AND server_id=? AND status='pending' AND guild_id<>?""",
                       (applicant_uid,server_id,int(member["guild_id"])))
        else:
            db.execute("""UPDATE world_guild_applications SET status='rejected'
                          WHERE guild_id=? AND uid=?""",(int(member["guild_id"]),applicant_uid))
        _audit(db,"guild.application."+status,f"{server_id}:{member['guild_id']}",
               {"operator":operator_uid,"applicant":applicant_uid},"PLAYER")
        db.commit(); db.close()
    return {"ok":True,"status":status}


def set_guild_role(operator_uid, server_id, target_uid, role):
    role=str(role or '').lower()
    if role not in ("member","deputy"): raise ValueError("Role Guild không hợp lệ")
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        operator=_require_guild_role(db,operator_uid,server_id,("leader",))
        target=db.execute("""SELECT * FROM world_guild_members WHERE guild_id=? AND uid=?""",
                          (int(operator["guild_id"]),str(target_uid))).fetchone()
        if not target:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy thành viên")
        if target["role"]=="leader":
            db.rollback(); db.close(); raise ValueError("Không thể đổi role Leader bằng thao tác này")
        db.execute("UPDATE world_guild_members SET role=? WHERE guild_id=? AND uid=?",
                   (role,int(operator["guild_id"]),str(target_uid)))
        _audit(db,"guild.role",f"{server_id}:{operator['guild_id']}",
               {"operator":operator_uid,"target":target_uid,"role":role},"PLAYER")
        db.commit(); db.close()
    return {"ok":True,"role":role}


def kick_guild_member(operator_uid, server_id, target_uid):
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        operator=_require_guild_role(db,operator_uid,server_id,("leader","deputy"))
        target=db.execute("""SELECT * FROM world_guild_members WHERE guild_id=? AND uid=?""",
                          (int(operator["guild_id"]),str(target_uid))).fetchone()
        if not target:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy thành viên")
        if target["role"]=="leader":
            db.rollback(); db.close(); raise ValueError("Không thể kick Leader")
        if operator["role"]=="deputy" and target["role"]=="deputy":
            db.rollback(); db.close(); raise ValueError("Deputy không thể kick Deputy khác")
        db.execute("DELETE FROM world_guild_members WHERE guild_id=? AND uid=?",
                   (int(operator["guild_id"]),str(target_uid)))
        _audit(db,"guild.kick",f"{server_id}:{operator['guild_id']}",
               {"operator":operator_uid,"target":target_uid},"PLAYER")
        db.commit(); db.close()
    return {"ok":True}


def transfer_guild_leader(operator_uid, server_id, target_uid):
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        operator=_require_guild_role(db,operator_uid,server_id,("leader",))
        target=db.execute("""SELECT * FROM world_guild_members WHERE guild_id=? AND uid=?""",
                          (int(operator["guild_id"]),str(target_uid))).fetchone()
        if not target:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy thành viên")
        if str(target_uid)==str(operator_uid):
            db.rollback(); db.close(); raise ValueError("Bạn đã là Leader")
        gid=int(operator["guild_id"])
        db.execute("UPDATE world_guild_members SET role='member' WHERE guild_id=? AND uid=?",(gid,str(operator_uid)))
        db.execute("UPDATE world_guild_members SET role='leader' WHERE guild_id=? AND uid=?",(gid,str(target_uid)))
        db.execute("UPDATE world_guilds SET owner_uid=? WHERE id=?",(str(target_uid),gid))
        _audit(db,"guild.transfer_leader",f"{server_id}:{gid}",
               {"from":operator_uid,"to":target_uid},"PLAYER")
        db.commit(); db.close()
    return {"ok":True}


def update_world_guild(uid, server_id, notice=None):
    with _lock:
        db=_db()
        member=_require_guild_role(db,uid,server_id,("leader","deputy"))
        if notice is None:
            db.close(); raise ValueError("Không có dữ liệu cần cập nhật")
        value=str(notice or '')[:180]
        db.execute("UPDATE world_guilds SET notice=? WHERE id=?",(value,int(member["guild_id"])))
        _audit(db,"guild.notice",f"{server_id}:{member['guild_id']}",{"uid":uid},"PLAYER")
        db.commit(); db.close()
    return guild_for_player(uid,server_id)


def send_guild_chat(uid, server_id, character_name, message):
    message=" ".join(str(message or '').strip().split())
    if not 1<=len(message)<=280: raise ValueError("Tin nhắn phải dài 1–280 ký tự")
    now=int(time.time())
    with _lock:
        db=_db()
        member=_require_guild_role(db,uid,server_id,("leader","deputy","member"))
        if db.backend=="postgres":
            cur=db.execute("""INSERT INTO world_guild_chat(guild_id,uid,character_name,message,created_at)
                              VALUES(?,?,?,?,?) RETURNING id""",
                           (int(member["guild_id"]),str(uid),str(character_name)[:40],message,now))
            mid=int(cur.fetchone()["id"])
        else:
            cur=db.execute("""INSERT INTO world_guild_chat(guild_id,uid,character_name,message,created_at)
                              VALUES(?,?,?,?,?)""",
                           (int(member["guild_id"]),str(uid),str(character_name)[:40],message,now))
            mid=int(cur.lastrowid)
        db.commit(); db.close()
    return {"id":mid,"uid":str(uid),"character_name":str(character_name),"message":message,"created_at":now}


def guild_chat(uid, server_id, limit=100):
    with _lock:
        db=_db()
        member=_require_guild_role(db,uid,server_id,("leader","deputy","member"))
        rows=db.execute("""SELECT id,uid,character_name,message,created_at
                           FROM world_guild_chat WHERE guild_id=?
                           ORDER BY id DESC LIMIT ?""",(int(member["guild_id"]),max(1,min(200,int(limit))))).fetchall()
        out=[dict(r) for r in rows]; out.reverse(); db.close(); return out


def send_guild_mail(uid, server_id, title, body):
    title=str(title or '').strip()[:100]; body=str(body or '').strip()[:1500]
    if not title or not body: raise ValueError("Tiêu đề và nội dung Guild Mail không được trống")
    now=int(time.time()); mail_id="GMAIL-"+uuid.uuid4().hex[:14].upper()
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        member=_require_guild_role(db,uid,server_id,("leader","deputy"))
        gid=int(member["guild_id"])
        db.execute("""INSERT INTO world_guild_mail(id,guild_id,sender_uid,title,body,created_at)
                      VALUES(?,?,?,?,?,?)""",(mail_id,gid,str(uid),title,body,now))
        members=db.execute("SELECT uid,server_id,character_name FROM world_guild_members WHERE guild_id=?",(gid,)).fetchall()
        for m in members:
            personal_id="MAIL-"+uuid.uuid4().hex[:16].upper()
            db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                          VALUES(?,?,?,?,?,?,?,'pending',?,'GUILD')""",
                       (personal_id,m["uid"],m["server_id"],m["character_name"],title,body,"{}",now))
        _audit(db,"guild.mail",f"{server_id}:{gid}",{"sender":uid,"mail_id":mail_id,"members":len(members)},"PLAYER")
        db.commit(); db.close()
    return {"id":mail_id,"sent":len(members)}


def guild_ranking(server_id, limit=100):
    with _lock:
        db=_db()
        rows=db.execute("""SELECT g.id,g.server_id,g.name,g.level,g.exp,g.owner_uid,
                                  COUNT(m.uid) AS member_count,
                                  COALESCE(SUM(m.power),0) AS total_power
                           FROM world_guilds g
                           LEFT JOIN world_guild_members m ON m.guild_id=g.id
                           WHERE g.server_id=?
                           GROUP BY g.id,g.server_id,g.name,g.level,g.exp,g.owner_uid
                           ORDER BY total_power DESC,g.level DESC,g.exp DESC,g.created_at ASC LIMIT ?""",
                        (str(server_id).upper(),max(1,min(200,int(limit))))).fetchall()
        out=[]
        for i,r in enumerate(rows,1):
            d=dict(r); d["rank"]=i; out.append(d)
        db.close(); return out


def guild_wars(server_id, limit=50):
    refresh_guild_wars(server_id)
    with _lock:
        db=_db()
        rows=db.execute("""SELECT w.*,ga.name AS guild_a_name,gb.name AS guild_b_name
                           FROM guild_wars w
                           JOIN world_guilds ga ON ga.id=w.guild_a
                           JOIN world_guilds gb ON gb.id=w.guild_b
                           WHERE w.server_id=?
                           ORDER BY w.created_at DESC LIMIT ?""",
                        (str(server_id).upper(),max(1,min(100,int(limit))))).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out


def schedule_guild_war(operator_uid, server_id, opponent_guild_id, duration=86400):
    now=int(time.time())
    war_cfg=GUILD_ONLINE_CONFIG.get("guild_war") or {}
    duration=max(3600,min(172800,int(duration or war_cfg.get("default_duration_seconds",86400))))
    delay=max(0,min(3600,int(war_cfg.get("start_delay_seconds",60))))
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        member=_require_guild_role(db,operator_uid,server_id,("leader","deputy"))
        own=int(member["guild_id"]); other=int(opponent_guild_id)
        if own==other:
            db.rollback(); db.close(); raise ValueError("Không thể thách đấu chính Guild của mình")
        if not db.execute("SELECT 1 FROM world_guilds WHERE id=? AND server_id=?",(other,str(server_id).upper())).fetchone():
            db.rollback(); db.close(); raise ValueError("Guild đối thủ không tồn tại")
        wid="GW-"+uuid.uuid4().hex[:14].upper()
        db.execute("""INSERT INTO guild_wars(id,server_id,guild_a,guild_b,score_a,score_b,status,starts_at,ends_at,winner_guild,created_at)
                      VALUES(?,?,?, ?,0,0,'scheduled',?,?,0,?)""",
                   (wid,str(server_id).upper(),own,other,now+delay,now+delay+duration,now))
        _audit(db,"guild.war.schedule",wid,{"guild_a":own,"guild_b":other,"operator":operator_uid},"PLAYER")
        db.commit(); db.close()
    return {"id":wid,"starts_at":now+delay,"ends_at":now+delay+duration}


def previous_pvp_season(now=None):
    t=time.gmtime(int(now or time.time()))
    year=t.tm_year; month=t.tm_mon-1
    if month==0:
        year-=1; month=12
    return f"{year:04d}-{month:02d}"


def pvp_season_reward(mode, rating):
    tiers=(PVP_SEASON_REWARDS.get("modes") or {}).get(str(mode).lower()) or []
    rating=int(rating)
    for tier in sorted(tiers,key=lambda x:int(x.get("min_rating",0)),reverse=True):
        if rating>=int(tier.get("min_rating",0)):
            return {str(k):int(v) for k,v in (tier.get("items") or {}).items() if int(v)>0}
    return {}


def pvp_season_claim_status(uid, server_id, mode):
    season_id=previous_pvp_season()
    with _lock:
        db=_db()
        row=db.execute("""SELECT * FROM pvp_ratings
                          WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                       (str(uid),str(server_id).upper(),str(mode).lower(),season_id)).fetchone()
        claim=db.execute("""SELECT * FROM pvp_season_claims
                            WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                         (str(uid),str(server_id).upper(),str(mode).lower(),season_id)).fetchone()
        db.close()
    if not row or int(row["matches"])<=0:
        return {"season_id":season_id,"eligible":False,"claimed":False,"reward":{},"rating":0}
    reward=pvp_season_reward(mode,int(row["rating"]))
    return {"season_id":season_id,"eligible":bool(reward),"claimed":bool(claim),
            "reward":reward,"rating":int(row["rating"]),"wins":int(row["wins"]),"losses":int(row["losses"])}


def claim_pvp_season_reward(uid, server_id, character_name, mode):
    uid=str(uid); server_id=str(server_id).upper(); mode=str(mode).lower()
    status=pvp_season_claim_status(uid,server_id,mode)
    if not status["eligible"]: raise ValueError("Không có phần thưởng mùa trước")
    if status["claimed"]: raise ValueError("Phần thưởng mùa này đã nhận")
    reward=status["reward"]; now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if db.execute("""SELECT 1 FROM pvp_season_claims
                         WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                      (uid,server_id,mode,status["season_id"])).fetchone():
            db.rollback(); db.close(); raise ValueError("Phần thưởng mùa này đã nhận")
        db.execute("""INSERT INTO pvp_season_claims(uid,server_id,mode,season_id,rating,reward,claimed_at)
                      VALUES(?,?,?,?,?,?,?)""",
                   (uid,server_id,mode,status["season_id"],int(status["rating"]),
                    json.dumps(reward,ensure_ascii=False),now))
        mail_id="MAIL-"+uuid.uuid4().hex[:16].upper()
        db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                      VALUES(?,?,?,?,?,?,?,'pending',?,'PVP_SEASON')""",
                   (mail_id,uid,server_id,str(character_name),
                    f"Phần thưởng PvP mùa {status['season_id']}",
                    f"Xếp hạng mùa đã kết thúc với Rating {status['rating']}.",
                    json.dumps(reward),now))
        _audit(db,"pvp.season_claim",f"{server_id}:{uid}",
               {"mode":mode,"season":status["season_id"],"rating":status["rating"],"reward":reward},"SYSTEM")
        db.commit(); db.close()
    return {"ok":True,"mail_id":mail_id,**status}


def _guild_level_from_exp(exp):
    cfg=GUILD_ONLINE_CONFIG.get("guild") or {}
    step=max(1,int(cfg.get("exp_per_level",5000)))
    cap=max(1,int(cfg.get("max_level",20)))
    return min(cap,1+max(0,int(exp))//step)


def add_guild_progress(guild_id, member_uid, exp_gain=0, contribution_gain=0):
    exp_gain=max(0,int(exp_gain)); contribution_gain=max(0,int(contribution_gain))
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        guild=db.execute("SELECT * FROM world_guilds WHERE id=?",(int(guild_id),)).fetchone()
        if not guild:
            db.rollback(); db.close(); raise ValueError("Guild không tồn tại")
        new_exp=int(guild["exp"])+exp_gain
        new_level=_guild_level_from_exp(new_exp)
        db.execute("UPDATE world_guilds SET exp=?,level=? WHERE id=?",(new_exp,new_level,int(guild_id)))
        if member_uid:
            db.execute("""UPDATE world_guild_members
                          SET contribution=contribution+?
                          WHERE guild_id=? AND uid=?""",
                       (contribution_gain,int(guild_id),str(member_uid)))
        db.commit(); db.close()
    return {"guild_id":int(guild_id),"exp":new_exp,"level":new_level,
            "exp_gain":exp_gain,"contribution_gain":contribution_gain}


def _refresh_single_guild_war(db, row, now):
    war=dict(row)
    status=war["status"]
    if status=="scheduled" and now>=int(war["starts_at"]):
        status="active"
        db.execute("UPDATE guild_wars SET status='active' WHERE id=?",(war["id"],))
        war["status"]="active"
    if status in ("scheduled","active") and now>=int(war["ends_at"]):
        score_a=int(war["score_a"]); score_b=int(war["score_b"])
        winner=int(war["guild_a"]) if score_a>score_b else int(war["guild_b"]) if score_b>score_a else 0
        db.execute("UPDATE guild_wars SET status='finished',winner_guild=? WHERE id=?",(winner,war["id"]))
        war["status"]="finished"; war["winner_guild"]=winner
    return war


def settle_guild_war(war_id, force=False):
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT * FROM guild_wars WHERE id=?",(str(war_id),)).fetchone()
        if not row:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy Guild War")
        war=dict(row)
        if force and war["status"]!="finished":
            score_a=int(war["score_a"]); score_b=int(war["score_b"])
            winner=int(war["guild_a"]) if score_a>score_b else int(war["guild_b"]) if score_b>score_a else 0
            db.execute("UPDATE guild_wars SET status='finished',winner_guild=?,ends_at=? WHERE id=?",
                       (winner,now,str(war_id)))
            war["status"]="finished"; war["winner_guild"]=winner; war["ends_at"]=now
        else:
            war=_refresh_single_guild_war(db,row,now)
        if war["status"]!="finished":
            db.commit(); db.close(); return war
        if db.execute("SELECT 1 FROM guild_war_claims WHERE war_id=? LIMIT 1",(str(war_id),)).fetchone():
            db.commit(); db.close(); return war
        reward_cfg=GUILD_ONLINE_CONFIG.get("guild_war") or {}
        winner=int(war["winner_guild"] or 0)
        for gid in (int(war["guild_a"]),int(war["guild_b"])):
            members=db.execute("""SELECT uid,server_id,character_name
                                  FROM world_guild_members WHERE guild_id=?""",(gid,)).fetchall()
            if winner==0:
                reward=reward_cfg.get("draw_reward") or {}
            elif gid==winner:
                reward=reward_cfg.get("winner_reward") or {}
            else:
                reward=reward_cfg.get("loser_reward") or {}
            clean={str(k):int(v) for k,v in reward.items() if int(v)>0}
            for m in members:
                if db.execute("SELECT 1 FROM guild_war_claims WHERE war_id=? AND uid=?",
                              (str(war_id),m["uid"])).fetchone():
                    continue
                db.execute("""INSERT INTO guild_war_claims(war_id,uid,guild_id,reward,claimed_at)
                              VALUES(?,?,?,?,?)""",
                           (str(war_id),m["uid"],gid,json.dumps(clean),now))
                mail_id="MAIL-"+uuid.uuid4().hex[:16].upper()
                outcome="Hòa" if winner==0 else "Chiến thắng" if gid==winner else "Thất bại"
                db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                              VALUES(?,?,?,?,?,?,?,'pending',?,'GUILD_WAR')""",
                           (mail_id,m["uid"],m["server_id"],m["character_name"],
                            f"Guild War · {outcome}",
                            f"Guild War {war_id} đã kết thúc. Kết quả: {outcome}.",
                            json.dumps(clean),now))
        _audit(db,"guild.war.settle",str(war_id),
               {"winner_guild":winner,"score_a":war["score_a"],"score_b":war["score_b"]},"SYSTEM")
        db.commit(); db.close(); return war


def refresh_guild_wars(server_id=None):
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if server_id:
            rows=db.execute("SELECT * FROM guild_wars WHERE server_id=? ORDER BY created_at DESC",
                            (str(server_id).upper(),)).fetchall()
        else:
            rows=db.execute("SELECT * FROM guild_wars ORDER BY created_at DESC").fetchall()
        ids=[]
        for row in rows:
            war=_refresh_single_guild_war(db,row,now)
            if war["status"]=="finished":
                ids.append(war["id"])
        db.commit(); db.close()
    for wid in ids:
        try: settle_guild_war(wid)
        except Exception: pass


def guild_war_detail(uid, server_id, war_id):
    refresh_guild_wars(server_id)
    with _lock:
        db=_db()
        member=_guild_member(db,uid,server_id)
        if not member:
            db.close(); raise ValueError("Bạn chưa ở trong Guild")
        row=db.execute("""SELECT w.*,ga.name AS guild_a_name,gb.name AS guild_b_name
                          FROM guild_wars w
                          JOIN world_guilds ga ON ga.id=w.guild_a
                          JOIN world_guilds gb ON gb.id=w.guild_b
                          WHERE w.id=? AND w.server_id=?""",
                       (str(war_id),str(server_id).upper())).fetchone()
        if not row:
            db.close(); raise ValueError("Không tìm thấy Guild War")
        war=dict(row)
        if int(member["guild_id"]) not in (int(war["guild_a"]),int(war["guild_b"])):
            db.close(); raise ValueError("Guild của bạn không thuộc trận chiến này")
        own_gid=int(member["guild_id"])
        enemy_gid=int(war["guild_b"]) if own_gid==int(war["guild_a"]) else int(war["guild_a"])
        enemies=db.execute("""SELECT uid,character_name,role,power,contribution
                              FROM world_guild_members WHERE guild_id=?
                              ORDER BY power DESC,joined_at ASC""",(enemy_gid,)).fetchall()
        battles=db.execute("""SELECT id,attacker_uid,attacker_guild,defender_uid,defender_guild,winner_uid,score,created_at
                              FROM guild_war_battles WHERE war_id=?
                              ORDER BY created_at DESC LIMIT 100""",(str(war_id),)).fetchall()
        out={"war":war,"own_guild_id":own_gid,"enemy_guild_id":enemy_gid,
             "enemies":[dict(r) for r in enemies],"battles":[dict(r) for r in battles]}
        db.close(); return out


def prepare_guild_war_attack(uid, server_id, war_id, defender_uid):
    refresh_guild_wars(server_id)
    with _lock:
        db=_db()
        attacker=_guild_member(db,uid,server_id)
        if not attacker:
            db.close(); raise ValueError("Bạn chưa ở trong Guild")
        war=db.execute("SELECT * FROM guild_wars WHERE id=? AND server_id=?",
                       (str(war_id),str(server_id).upper())).fetchone()
        if not war:
            db.close(); raise ValueError("Không tìm thấy Guild War")
        if war["status"]!="active":
            db.close(); raise ValueError("Guild War chưa ở trạng thái chiến đấu")
        gid=int(attacker["guild_id"])
        if gid not in (int(war["guild_a"]),int(war["guild_b"])):
            db.close(); raise ValueError("Guild của bạn không thuộc trận này")
        enemy_gid=int(war["guild_b"]) if gid==int(war["guild_a"]) else int(war["guild_a"])
        defender=db.execute("""SELECT * FROM world_guild_members
                               WHERE guild_id=? AND uid=?""",(enemy_gid,str(defender_uid))).fetchone()
        if not defender:
            db.close(); raise ValueError("Đối thủ không thuộc Guild đối phương")
        if db.execute("""SELECT 1 FROM guild_war_battles
                         WHERE war_id=? AND attacker_uid=? AND defender_uid=?""",
                      (str(war_id),str(uid),str(defender_uid))).fetchone():
            db.close(); raise ValueError("Bạn đã đánh đối thủ này trong Guild War")
        out={"war":dict(war),"attacker":dict(attacker),"defender":dict(defender)}
        db.close(); return out


def record_guild_war_battle(war_id, attacker_uid, defender_uid, attacker_snapshot, defender_snapshot, report):
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        war=db.execute("SELECT * FROM guild_wars WHERE id=?",(str(war_id),)).fetchone()
        if not war:
            db.rollback(); db.close(); raise ValueError("Không tìm thấy Guild War")
        if war["status"]!="active" or now < int(war["starts_at"]) or now >= int(war["ends_at"]):
            db.rollback(); db.close(); raise ValueError("Guild War không còn trong thời gian chiến đấu")
        attacker=db.execute("""SELECT * FROM world_guild_members WHERE uid=? AND server_id=?""",
                            (str(attacker_uid),war["server_id"])).fetchone()
        defender=db.execute("""SELECT * FROM world_guild_members WHERE uid=? AND server_id=?""",
                            (str(defender_uid),war["server_id"])).fetchone()
        if not attacker or not defender or int(attacker["guild_id"])==int(defender["guild_id"]):
            db.rollback(); db.close(); raise ValueError("Cặp Guild War không hợp lệ")
        if int(attacker["guild_id"]) not in (int(war["guild_a"]),int(war["guild_b"])):
            db.rollback(); db.close(); raise ValueError("Guild tấn công không thuộc Guild War")
        is_win=int(report.get("isWin",0))==1
        winner_uid=str(attacker_uid) if is_win else str(defender_uid)
        cfg=GUILD_ONLINE_CONFIG.get("guild_war") or {}
        score_cfg=cfg.get("score") or {}
        rounds=max(1,int(report.get("total_round") or 1))
        if is_win:
            base=int(score_cfg.get("win_base",100))
            cap=max(0,int(score_cfg.get("round_bonus_cap",50)))
            score=max(1,base+max(0,cap-min(cap,rounds)))
        else:
            score=max(0,int(score_cfg.get("loss_base",25)))
        target_gid=int(attacker["guild_id"]) if is_win else int(defender["guild_id"])
        col="score_a" if target_gid==int(war["guild_a"]) else "score_b"
        battle_id="GWB-"+uuid.uuid4().hex[:14].upper()
        db.execute("""INSERT INTO guild_war_battles(
                      id,war_id,attacker_uid,attacker_guild,defender_uid,defender_guild,winner_uid,score,report,created_at)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (battle_id,str(war_id),str(attacker_uid),int(attacker["guild_id"]),
                    str(defender_uid),int(defender["guild_id"]),winner_uid,score,
                    json.dumps({"attacker":attacker_snapshot,"defender":defender_snapshot,"battle":report},
                               ensure_ascii=False),now))
        db.execute(f"UPDATE guild_wars SET {col}={col}+? WHERE id=?",(score,str(war_id)))
        contrib_cfg=(GUILD_ONLINE_CONFIG.get("guild") or {}).get("contribution") or {}
        exp_gain=max(0,int(contrib_cfg.get("guild_exp_per_battle",200)))
        att_contrib=int(contrib_cfg.get("war_win" if is_win else "war_loss",300 if is_win else 120))
        def_contrib=int(contrib_cfg.get("war_loss" if is_win else "war_win",120 if is_win else 300))
        for member,contrib in ((attacker,att_contrib),(defender,def_contrib)):
            guild=db.execute("SELECT exp FROM world_guilds WHERE id=?",(int(member["guild_id"]),)).fetchone()
            new_exp=int(guild["exp"])+exp_gain
            db.execute("UPDATE world_guilds SET exp=?,level=? WHERE id=?",
                       (new_exp,_guild_level_from_exp(new_exp),int(member["guild_id"])))
            db.execute("""UPDATE world_guild_members SET contribution=contribution+?
                          WHERE guild_id=? AND uid=?""",
                       (contrib,int(member["guild_id"]),member["uid"]))
        _audit(db,"guild.war.battle",str(war_id),
               {"battle_id":battle_id,"attacker":attacker_uid,"defender":defender_uid,
                "winner":winner_uid,"score":score},"SYSTEM")
        updated=db.execute("SELECT * FROM guild_wars WHERE id=?",(str(war_id),)).fetchone()
        db.commit(); out={"battle_id":battle_id,"winner_uid":winner_uid,"score":score,"war":dict(updated)}
        db.close(); return out


def maintenance_tick(now=None):
    now=int(now or time.time())
    refresh_guild_wars()
    settle_previous_pvp_season(now)
    with _lock:
        db=_db()
        db.execute("DELETE FROM pvp_queue WHERE joined_at<?",(now-600,))
        db.execute("DELETE FROM pvp_match_peers WHERE last_seen<?",(now-3600,))
        db.execute("""UPDATE pvp_matches SET status='expired',resolved_at=?
                      WHERE status IN ('ready','active') AND created_at<?""",(now,now-1800))
        db.commit(); db.close()
    return {"ok":True,"at":now}


def admin_set_pvp_rating(uid, server_id, mode, rating, season_id=None, operator="SUPER_GM"):
    uid=str(uid or '').strip(); server_id=str(server_id or '').strip().upper()
    mode=str(mode or 'arena').strip().lower()
    if mode not in ("arena","team","cross"): raise ValueError("Mode PvP không hợp lệ")
    rating=max(0,min(100000,int(rating)))
    season_id=str(season_id or current_pvp_season())
    now=int(time.time())
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM players WHERE uid=? AND server_id=?",(uid,server_id)).fetchone():
            db.rollback(); db.close(); raise ValueError("Không tìm thấy UID/Server")
        _ensure_rating(db,uid,server_id,mode,season_id,now)
        db.execute("""UPDATE pvp_ratings SET rating=?,updated_at=?
                      WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                   (rating,now,uid,server_id,mode,season_id))
        _audit(db,"admin.pvp.rating",f"{server_id}:{uid}",
               {"mode":mode,"season":season_id,"rating":rating},operator)
        db.commit(); db.close()
    return pvp_rating(uid,server_id,mode,season_id)


def admin_add_guild_progress(uid, server_id, exp_gain=0, contribution_gain=0, operator="SUPER_GM"):
    with _lock:
        db=_db()
        member=_guild_member(db,uid,server_id)
        db.close()
    if not member: raise ValueError("Người chơi chưa ở trong Guild")
    result=add_guild_progress(member["guild_id"],uid,exp_gain,contribution_gain)
    with _lock:
        db=_db(); _audit(db,"admin.guild.progress",f"{server_id}:{uid}",
                         {"exp_gain":int(exp_gain),"contribution_gain":int(contribution_gain),
                          "guild_id":member["guild_id"]},operator)
        db.commit(); db.close()
    return result


def admin_force_settle_guild_war(war_id, operator="SUPER_GM"):
    result=settle_guild_war(war_id,force=True)
    with _lock:
        db=_db(); _audit(db,"admin.guild.war.force_settle",str(war_id),
                         {"winner_guild":result.get("winner_guild",0)},operator)
        db.commit(); db.close()
    return result


def settle_previous_pvp_season(now=None):
    now=int(now or time.time())
    season_id=previous_pvp_season(now)
    issued=0
    with _lock:
        db=_db(); db.execute("BEGIN IMMEDIATE")
        rows=db.execute("""SELECT r.*,p.character_name
                           FROM pvp_ratings r
                           LEFT JOIN players p ON p.uid=r.uid AND p.server_id=r.server_id
                           WHERE r.season_id=? AND r.matches>0""",(season_id,)).fetchall()
        for row in rows:
            if db.execute("""SELECT 1 FROM pvp_season_claims
                             WHERE uid=? AND server_id=? AND mode=? AND season_id=?""",
                          (row["uid"],row["server_id"],row["mode"],season_id)).fetchone():
                continue
            reward=pvp_season_reward(row["mode"],int(row["rating"]))
            if not reward:
                continue
            db.execute("""INSERT INTO pvp_season_claims(uid,server_id,mode,season_id,rating,reward,claimed_at)
                          VALUES(?,?,?,?,?,?,?)""",
                       (row["uid"],row["server_id"],row["mode"],season_id,int(row["rating"]),
                        json.dumps(reward,ensure_ascii=False),now))
            mail_id="MAIL-"+uuid.uuid4().hex[:16].upper()
            db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                          VALUES(?,?,?,?,?,?,?,'pending',?,'PVP_SEASON')""",
                       (mail_id,row["uid"],row["server_id"],row["character_name"] or row["uid"],
                        f"Phần thưởng PvP mùa {season_id}",
                        f"Phần thưởng {row['mode']} · Rating {row['rating']} đã được tự động phát.",
                        json.dumps(reward),now))
            issued+=1
        if issued:
            _audit(db,"pvp.season.auto_settle",season_id,{"issued":issued},"SYSTEM")
        db.commit(); db.close()
    return {"season_id":season_id,"issued":issued}
