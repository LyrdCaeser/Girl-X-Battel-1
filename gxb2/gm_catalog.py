"""Authenticated GM gift catalog built only from original game records and icons.

Gift recipients are handled by live_service: this module has no database writes.
Character gifts mean *existing shard item IDs*, never developer-generated partners.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = json.loads((ROOT / "web/assets/items-catalog.json").read_text(encoding="utf-8"))
GIRLS = json.loads((ROOT / "web/assets/girls-catalog.json").read_text(encoding="utf-8"))
DEBRIS = json.loads((ROOT / "data/debris.json").read_text(encoding="utf-8"))
GIRL_INDEX = {int(g["id"]): g for g in GIRLS}
ITEM_IMAGES = ROOT / "web/assets/item-icons"
CARD_IMAGES = ROOT / "web/assets/cards"
CHARACTER_IMAGES = ROOT / "web/assets/characters"

def _girl_image(girl_id: int) -> str:
    current = int(girl_id)
    for _ in range(6):
        for folder, prefix in ((CARD_IMAGES, "/assets/cards/partner_card_"),
                               (CHARACTER_IMAGES, "/assets/characters/")):
            if (folder / f"{'partner_card_' if folder == CARD_IMAGES else ''}{current}.png").is_file():
                return f"{prefix}{current}.png"
        host = GIRL_INDEX.get(current, {}).get("host")
        if not host:
            break
        current = int(host)
    return ""

def catalog() -> dict:
    items = []
    for record in ITEMS.values():
        key = str(record.get("icon") or "")
        picture = ITEM_IMAGES / (key + ".png")
        if not key or not picture.is_file():
            continue
        items.append({
            "id": int(record["id"]), "name": str(record["name"]),
            "category": int(record.get("category") or 0),
            "quality": int(record.get("quality") or 0),
            "image": "/assets/item-icons/" + key + ".png",
        })
    shards = []
    for record in DEBRIS.values():
        cost = str(record.get("partner_cost") or "")
        if int(record.get("type") or 0) != 3 or "#" not in cost:
            continue
        try:
            girl_id, required = [int(v) for v in cost.split("#", 1)]
        except (ValueError, TypeError):
            continue
        girl = GIRL_INDEX.get(girl_id)
        if not girl:
            continue
        image = _girl_image(girl_id)
        if not image:
            continue
        shards.append({
            "id": int(record["id"]), "girl_id": girl_id,
            "name": str(girl["name"]), "stars": int(girl.get("stars") or record.get("qlt") or 1),
            "quality": int(record.get("qlt") or 1),
            "required": required, "image": image,
        })
    return {"items": items, "shards": shards}

def allowed_gift_ids() -> set[str]:
    from .vip import VIP_EXP_REWARD_ID
    gift = catalog()
    return {VIP_EXP_REWARD_ID, *(str(v["id"]) for v in (gift["items"] + gift["shards"]))}

def validate_gift(attachments: dict) -> dict:
    if not isinstance(attachments, dict) or not attachments:
        raise ValueError("Chọn ít nhất một phần quà từ danh mục gốc")
    allowed = allowed_gift_ids()
    clean = {}
    for key, amount in attachments.items():
        try:
            item_id = str(int(key))
            qty = int(amount)
        except (TypeError, ValueError):
            raise ValueError("ID hoặc số lượng quà không hợp lệ") from None
        if item_id not in allowed:
            raise ValueError("Vật phẩm không thuộc danh mục quà có ảnh gốc")
        if qty <= 0 or qty > 2_000_000:
            raise ValueError("Số lượng phải từ 1 đến 2.000.000")
        clean[item_id] = clean.get(item_id, 0) + qty
    return clean
