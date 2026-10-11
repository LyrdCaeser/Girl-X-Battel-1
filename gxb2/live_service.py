from __future__ import annotations
import json
import threading
import time
import uuid
from pathlib import Path

from . import database

ROOT = Path(__file__).resolve().parents[1]
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
    oid="ORD-"+uuid.uuid4().hex[:14].upper(); now=int(time.time())
    with _lock:
        db=_db()
        db.execute("""INSERT INTO orders(id,uid,server_id,character_name,package,note,status,reward,created_at)
                      VALUES(?,?,?,?,?,?,'pending','{}',?)""",
                   (oid,str(uid),str(server_id).upper(),target["character_name"],str(package or '')[:120],str(note or '')[:500],now))
        _audit(db,"order.create",f"{server_id}:{uid}",{"order_id":oid,"package":package},"PLAYER")
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
            if not isinstance(reward,dict): raise ValueError("reward phải là object")
            for k,v in reward.items():
                item=str(int(k)); amount=int(v)
                if amount<0 or amount>2_000_000_000: raise ValueError("Số lượng vật phẩm không hợp lệ")
                if amount: clean[item]=amount
            if not clean: db.rollback();db.close();raise ValueError("Đơn duyệt phải có reward")
        status="approved" if approve else "rejected"; now=int(time.time())
        db.execute("UPDATE orders SET status=?,reward=?,reviewed_at=?,reviewer=? WHERE id=?",
                   (status,json.dumps(clean),now,reviewer,order_id))
        _audit(db,"order."+status,f"{row['server_id']}:{row['uid']}",{"order_id":order_id,"reward":clean},reviewer)
        db.commit(); db.close()
    if approve:
        send_mail(row["uid"],row["server_id"],row["character_name"],"Nạp thành công",
                  f"Đơn {order_id} đã được QTV duyệt.",clean,reviewer)
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
        members=db.execute("""SELECT uid,server_id,character_name,role,power,joined_at,last_seen
                              FROM world_guild_members WHERE guild_id=?
                              ORDER BY CASE role WHEN 'leader' THEN 0 WHEN 'deputy' THEN 1 ELSE 2 END,
                                       power DESC,joined_at""",(int(out["id"]),)).fetchall()
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
            out=dict(existing); db.commit(); db.close(); return {"status":"matched","match":out}
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
            seed=uuid.uuid4().int % 2147483647
            match_server="CROSS" if mode=="cross" else server_id
            db.execute("""INSERT INTO pvp_matches(id,mode,server_id,player_a,player_b,name_a,name_b,power_a,power_b,status,winner_uid,created_at,resolved_at,seed)
                          VALUES(?,?,?,?,?,?,?,?,?,'ready','',?,0,?)""",
                       (match_id,mode,match_server,str(opponent["uid"]),uid,str(opponent["character_name"]),character_name,
                        int(opponent["power"]),power,now,seed))
            db.execute("DELETE FROM pvp_queue WHERE (uid=? AND server_id=? AND mode=?) OR (uid=? AND server_id=? AND mode=?)",
                       (uid,server_id,mode,str(opponent["uid"]),str(opponent["server_id"]),mode))
            _audit(db,"pvp.match",match_id,{"mode":mode,"a":opponent["uid"],"b":uid},"SYSTEM")
            row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(match_id,)).fetchone()
            out={"status":"matched","match":dict(row)}
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
            out={"status":"matched","match":dict(match)}
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
        db.commit(); out=dict(row); db.close(); return out


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
            out=dict(row); db.commit(); db.close(); return out
        now=int(time.time())
        db.execute("UPDATE pvp_matches SET status='finished',winner_uid=?,resolved_at=? WHERE id=?",
                   (str(winner_uid),now,str(match_id)))
        _audit(db,"pvp.finish",str(match_id),{"winner":winner_uid},"SYSTEM")
        row=db.execute("SELECT * FROM pvp_matches WHERE id=?",(str(match_id),)).fetchone()
        db.commit(); out=dict(row); db.close(); return out


def pvp_history(uid, limit=50):
    limit=max(1,min(200,int(limit)))
    with _lock:
        db=_db()
        rows=db.execute("""SELECT * FROM pvp_matches
                           WHERE player_a=? OR player_b=?
                           ORDER BY created_at DESC LIMIT ?""",(str(uid),str(uid),limit)).fetchall()
        out=[dict(r) for r in rows]; db.close(); return out
