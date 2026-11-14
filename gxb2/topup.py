from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "topup_packages.json"
OVERRIDE_PATH = ROOT / "state" / "topup_packages.json"


def _read(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _clean_reward(value):
    if not isinstance(value, dict):
        raise ValueError("reward phải là object")
    out = {}
    for key, amount in value.items():
        item_id = str(int(key))
        qty = int(amount)
        if qty < 0 or qty > 2_000_000_000:
            raise ValueError("Số lượng vật phẩm không hợp lệ")
        if qty:
            out[item_id] = qty
    return out


def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError("Top-up catalog phải là object")
    packages = raw.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ValueError("Phải có ít nhất một gói nạp")
    out = []
    seen = set()
    for row in packages:
        if not isinstance(row, dict):
            raise ValueError("Gói nạp không hợp lệ")
        pid = str(row.get("id") or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9_-]{1,32}", pid):
            raise ValueError("Package ID không hợp lệ")
        if pid in seen:
            raise ValueError("Package ID bị trùng")
        seen.add(pid)
        name = str(row.get("name") or "").strip()[:80]
        price_label = str(row.get("price_label") or "").strip()[:80]
        if not name:
            raise ValueError("Tên gói nạp không được trống")
        manual = bool(row.get("manual_reward", False))
        reward = _clean_reward(row.get("reward") or {})
        if not manual and not reward:
            raise ValueError(f"Gói {pid} phải có reward hoặc bật manual_reward")
        out.append({
            "id": pid,
            "name": name,
            "price_label": price_label,
            "reward": reward,
            "manual_reward": manual,
            "enabled": bool(row.get("enabled", True)),
        })
    return {"packages": out}


def get():
    base = _read(DEFAULT_PATH)
    override = _read(OVERRIDE_PATH)
    if not override.get("packages"):
        return validate(base)
    # Preserve every VPS-admin-configured package/reward/price without overwriting
    # it, but also expose restored original card/gift identifiers introduced
    # after the previous state override was saved.
    custom = validate(override)
    existing = {p["id"] for p in custom["packages"]}
    restored = [p for p in validate(base)["packages"] if p["id"] not in existing]
    return {"packages": custom["packages"] + restored}


def save(raw):
    cfg = validate(copy.deepcopy(raw))
    OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = OVERRIDE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OVERRIDE_PATH)
    return cfg


def reset():
    if OVERRIDE_PATH.exists():
        OVERRIDE_PATH.unlink()
    return get()


def public_catalog():
    rows = []
    for row in get()["packages"]:
        if not row["enabled"]:
            continue
        rows.append({
            "id": row["id"],
            "name": row["name"],
            "price_label": row["price_label"],
            "manual_reward": row["manual_reward"],
            "vip_exp": int((row.get("reward") or {}).get("999999991", 0)),
            "instant_gems": int((row.get("reward") or {}).get("2", 0)),
        })
    return {"packages": rows}


def package(package_id, include_disabled=False):
    key = str(package_id or "").strip().upper()
    for row in get()["packages"]:
        if row["id"] == key and (include_disabled or row["enabled"]):
            return copy.deepcopy(row)
    return None
