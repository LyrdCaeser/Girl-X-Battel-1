"""Server-owned configurable Skin Shop with exclusive marriage costumes.

All IDs and artwork are the original publisher records. A wedding costume is
identified by partner_pictures.json 'wed' flag, *not* by administrator input.
Never mutate original data/skins.json or the player's money outside Engine lock.
"""
from __future__ import annotations

import re
import threading
import time
from pathlib import Path
import json

from . import live_service, skins, local_config

ROOT = Path(__file__).resolve().parents[1]
PICS = json.loads((ROOT / "data/partner_pictures.json").read_text(encoding="utf-8"))
GIRLS = {int(row["id"]): row for row in json.loads(
    (ROOT / "web/assets/girls-catalog.json").read_text(encoding="utf-8")
)}
_WEDDING_NAMES = re.compile(r"\b(?:bride|bridal|wedding|marriage|bridegroom|groom)\b", re.I)
WEDDING_IDS = frozenset(
    sid for sid, row in skins.SKINS.items()
    if int((PICS.get(str(sid)) or {}).get("wed") or 0) == 1
    or _WEDDING_NAMES.search(str(row.get("name") or ""))
)
_LOCK = threading.RLock()
_READY = set()
MAX_PRICE = 2_000_000_000


def is_wedding(skin_id):
    """Non-overridable source rule; anything tagged as wedding cannot be sold."""
    try:
        return int(skin_id) in WEDDING_IDS
    except (ValueError, TypeError):
        return False


def _db():
    db = live_service._db()
    key = (db.backend, db.identity)
    try:
        if key not in _READY:
            with _LOCK:
                if key not in _READY:
                    db.execute("""CREATE TABLE IF NOT EXISTS skin_shop_settings (
                        skin_id INTEGER PRIMARY KEY,
                        enabled INTEGER NOT NULL,
                        allow_gold INTEGER NOT NULL,
                        allow_crystal INTEGER NOT NULL,
                        allow_ticket INTEGER NOT NULL,
                        price_gold BIGINT NOT NULL,
                        price_crystal BIGINT NOT NULL,
                        updated_at BIGINT NOT NULL,
                        updated_by TEXT NOT NULL
                    )""")
                    db.commit()
                    _READY.add(key)
        return db
    except Exception:
        db.rollback()
        db.close()
        raise


def _settings():
    db = _db()
    try:
        return {int(row["skin_id"]): dict(row)
                for row in db.execute("SELECT * FROM skin_shop_settings").fetchall()}
    finally:
        db.close()


def offer(skin_id, *, settings=None, include_locked=False):
    try:
        sid = int(skin_id)
    except (ValueError, TypeError):
        return None
    row = skins.SKINS.get(sid)
    if not row:
        return None
    wedding = is_wedding(sid)
    if wedding and not include_locked:
        return None
    preset = (settings if settings is not None else _settings()).get(sid) or {}
    raw_ticket = row.get("shop") or ""
    ticket_price = 0
    if raw_ticket:
        try:
            currency, price = str(raw_ticket).split("#")[:2]
            if currency == "74":
                ticket_price = local_config.shop_cost(int(price))
        except (ValueError, TypeError):
            ticket_price = 0
    result = {
        "skin_id": sid, "girl_ids": list(row["partners"]),
        "name": row["name"], "rarity": row.get("rarity", 0),
        "girl_name": next((GIRLS[x]["name"] for x in row["partners"] if x in GIRLS), ""),
        "group": next((int(GIRLS[x].get("group") or 0) for x in row["partners"] if x in GIRLS), 0),
        "is_wedding": wedding,
        "enabled": not wedding and bool(preset.get("enabled", bool(ticket_price))),
        "allow_gold": not wedding and bool(preset.get("allow_gold", 0)),
        "allow_crystal": not wedding and bool(preset.get("allow_crystal", 0)),
        "allow_ticket": not wedding and bool(preset.get("allow_ticket", bool(ticket_price))) and ticket_price > 0,
        "price_gold": int(preset.get("price_gold", 0)),
        "price_crystal": int(preset.get("price_crystal", 0)),
        "price_ticket": ticket_price,
        "updated_at": int(preset.get("updated_at", 0)),
    }
    # An enabled listing must have at least one valid server-side price.
    if result["allow_gold"] and result["price_gold"] < 1:
        result["allow_gold"] = False
    if result["allow_crystal"] and result["price_crystal"] < 1:
        result["allow_crystal"] = False
    return result


def catalogue(*, admin=False):
    settings = _settings()
    offers = [offer(sid, settings=settings, include_locked=admin) for sid in skins.SKINS]
    if not admin:
        offers = [o for o in offers if o and o["enabled"]
                  and (o["allow_gold"] or o["allow_crystal"] or o["allow_ticket"])]
    return {"offers": offers, "total": len(offers), "wedding_count": len(WEDDING_IDS) if admin else 0}


def update_configs(changes, operator):
    """Single audited transaction, no client-controlled wedding flag or item IDs."""
    if not isinstance(changes, list) or not 1 <= len(changes) <= 100:
        raise ValueError("Cần chọn từ 1 đến 100 trang phục để cập nhật")
    validated = []
    seen = set()
    for req in changes:
        if not isinstance(req, dict):
            raise ValueError("Cấu hình trang phục không hợp lệ")
        try:
            sid = int(req.get("skin_id", 0))
        except (ValueError, TypeError):
            raise ValueError("ID trang phục không hợp lệ") from None
        if sid not in skins.SKINS or sid in seen:
            raise ValueError("Trang phục không tồn tại hoặc bị lặp")
        if is_wedding(sid):
            raise ValueError("Trang phục cưới độc quyền đám cưới, tuyệt đối không thể bán")
        seen.add(sid)
        source = skins.SKINS[sid]
        available_ticket = str(source.get("shop") or "").startswith("74#")
        fields = ("enabled", "allow_gold", "allow_crystal", "allow_ticket")
        if any(type(req.get(k)) is not bool for k in fields):
            raise ValueError("Trạng thái bán phải là true hoặc false")
        try:
            gold, crystal = int(req.get("price_gold", 0)), int(req.get("price_crystal", 0))
        except (ValueError, TypeError):
            raise ValueError("Giá tiền phải là số nguyên") from None
        if not 0 <= gold <= MAX_PRICE or not 0 <= crystal <= MAX_PRICE:
            raise ValueError("Giá phải từ 0 đến 2 tỷ")
        if req["allow_ticket"] and not available_ticket:
            raise ValueError("Skin này không có giá Vé Trang Phục gốc")
        if req["enabled"] and not (
            (req["allow_gold"] and gold > 0)
            or (req["allow_crystal"] and crystal > 0)
            or (req["allow_ticket"] and available_ticket)
        ):
            raise ValueError("Để bật bán, cần chọn phương thức thanh toán và giá hợp lệ")
        if req["allow_gold"] and gold < 1 or req["allow_crystal"] and crystal < 1:
            raise ValueError("Giá phương thức đang bật phải lớn hơn 0")
        validated.append((sid, *(int(req[k]) for k in fields), gold, crystal))
    with _LOCK:
        db = _db()
        now = int(time.time())
        try:
            for sid, enabled, gold_on, crystal_on, ticket_on, gp, cp in validated:
                db.execute("""INSERT INTO skin_shop_settings (
                    skin_id,enabled,allow_gold,allow_crystal,allow_ticket,price_gold,price_crystal,updated_at,updated_by
                ) VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(skin_id) DO UPDATE SET
                    enabled=excluded.enabled, allow_gold=excluded.allow_gold,
                    allow_crystal=excluded.allow_crystal, allow_ticket=excluded.allow_ticket,
                    price_gold=excluded.price_gold, price_crystal=excluded.price_crystal,
                    updated_at=excluded.updated_at,updated_by=excluded.updated_by
                """,(sid,enabled,gold_on,crystal_on,ticket_on,gp,cp,now,str(operator)[:100]))
                live_service._audit(db, "skin_shop.update", str(sid),
                    {"enabled":bool(enabled),"allow_gold":bool(gold_on),"allow_crystal":bool(crystal_on),
                     "allow_ticket":bool(ticket_on),"price_gold":gp,"price_crystal":cp}, str(operator))
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    return {"updated": len(validated), "offers": [offer(v[0]) for v in validated]}


def purchase(state, skin_id, payment):
    """Invoked exclusively within Engine.skins_action's per-player transaction."""
    try:
        sid = int(skin_id)
    except (ValueError, TypeError):
        raise ValueError("Trang phục không hợp lệ") from None
    if is_wedding(sid):
        raise ValueError("Trang phục cưới độc quyền đám cưới, không được phép bán")
    current = offer(sid)
    if not current or not current["enabled"]:
        raise ValueError("Trang phục chưa được mở bán")
    currencies = {"gold": ("1", "allow_gold", "price_gold"),
                  "crystal": ("2", "allow_crystal", "price_crystal"),
                  "ticket": ("74", "allow_ticket", "price_ticket")}
    if payment not in currencies:
        raise ValueError("Phương thức thanh toán không hợp lệ")
    currency, allowed, price_key = currencies[payment]
    price = int(current[price_key])
    if not current[allowed] or price <= 0:
        raise ValueError("Phương thức thanh toán chưa được mở bán")
    items = state.setdefault("items", {})
    have = int(items.get(currency, 0))
    if have < price:
        raise ValueError("Không đủ " + {"gold":"Vàng","crystal":"Crystal","ticket":"Vé Trang Phục"}[payment])
    items[currency] = have - price
    items[str(sid)] = int(items.get(str(sid), 0)) + 1
    skins.collected(state)
    receipt = {"skin_id":sid,"currency":payment,"price":price,"at":int(time.time())}
    purchases = state.setdefault("skin_shop_purchases", [])
    purchases.append(receipt)
    # Bound growth of the player's save while preserving recent real receipts.
    if len(purchases) > 500:
        del purchases[:-500]
    return {"got":{str(sid):1},"purchase":receipt}
