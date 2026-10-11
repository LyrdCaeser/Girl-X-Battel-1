from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

from . import local_config

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "world_live_defaults.json"
STATE_ROOT = ROOT / "state" / "worlds"

_FALLBACK = {
    "shop": {"price_multiplier": 1.0, "disabled_shop_ids": []},
    "event_shop": {"price_multiplier": 1.0},
    "event_rewards": {"multiplier": 1.0, "checkin_enabled": True, "sevenday_enabled": True},
    "summon_rate": {"star_multiplier": {str(i): 1.0 for i in range(1, 7)}},
}


def _server_id(value):
    sid = str(value or "S1").strip().upper()
    if not re.fullmatch(r"[A-Z0-9_-]{1,16}", sid):
        raise ValueError("Server ID không hợp lệ")
    return sid


def _merge(base, override):
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _read(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _mult(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label}: giá trị không hợp lệ")
    try:
        n = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label}: phải là số")
    if not 0 <= n <= 100:
        raise ValueError(f"{label}: phải nằm trong khoảng 0–100")
    return n


def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError("World Live Config phải là object")
    cfg = _merge(_FALLBACK, raw)

    shop = cfg.setdefault("shop", {})
    shop["price_multiplier"] = _mult(shop.get("price_multiplier", 1), "Shop multiplier")
    disabled = shop.get("disabled_shop_ids", [])
    if not isinstance(disabled, list):
        raise ValueError("disabled_shop_ids phải là danh sách")
    shop["disabled_shop_ids"] = sorted({int(x) for x in disabled if int(x) > 0})

    event_shop = cfg.setdefault("event_shop", {})
    event_shop["price_multiplier"] = _mult(event_shop.get("price_multiplier", 1), "Event Shop multiplier")

    event_rewards = cfg.setdefault("event_rewards", {})
    event_rewards["multiplier"] = _mult(event_rewards.get("multiplier", 1), "Event reward multiplier")
    event_rewards["checkin_enabled"] = bool(event_rewards.get("checkin_enabled", True))
    event_rewards["sevenday_enabled"] = bool(event_rewards.get("sevenday_enabled", True))

    stars = cfg.setdefault("summon_rate", {}).setdefault("star_multiplier", {})
    cfg["summon_rate"]["star_multiplier"] = {
        str(star): _mult(stars.get(str(star), 1), f"Summon {star}★ multiplier")
        for star in range(1, 7)
    }
    return cfg


def path_for(server_id):
    return STATE_ROOT / _server_id(server_id) / "live_config.json"


def get(server_id):
    defaults = _merge(_FALLBACK, _read(DEFAULT_PATH))
    return validate(_merge(defaults, _read(path_for(server_id))))


def save(server_id, raw):
    sid = _server_id(server_id)
    cfg = validate(raw)
    path = path_for(sid)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return cfg


def reset(server_id):
    path = path_for(server_id)
    if path.exists():
        path.unlink()
    return get(server_id)


def shop_enabled(server_id, shop_id):
    return int(shop_id) not in set(get(server_id)["shop"]["disabled_shop_ids"])


def shop_cost(value, server_id):
    base = local_config.shop_cost(value)
    mult = get(server_id)["shop"]["price_multiplier"]
    return max(0, int(math.ceil(base * mult)))


def event_shop_cost(value, server_id):
    base = local_config.shop_cost(value)
    mult = get(server_id)["event_shop"]["price_multiplier"]
    return max(0, int(math.ceil(base * mult)))


def event_reward(value, server_id):
    base = local_config.scale_reward(value)
    mult = get(server_id)["event_rewards"]["multiplier"]
    return max(0, int(math.floor(base * mult)))


def event_enabled(server_id, kind):
    cfg = get(server_id)["event_rewards"]
    if kind == "checkin":
        return bool(cfg["checkin_enabled"])
    if kind == "sevenday":
        return bool(cfg["sevenday_enabled"])
    return True


def summon_weight(row, partner_table, server_id):
    base = local_config.summon_weight(row, partner_table)
    if base <= 0:
        return 0
    table_id = str(row.get("item", "")).split("#")[0]
    girl = partner_table.get(table_id)
    if not girl:
        return base
    star = max(1, min(6, int(girl.get("max_star") or 1)))
    mult = get(server_id)["summon_rate"]["star_multiplier"].get(str(star), 1.0)
    return max(0, int(round(base * mult)))


def public_config(server_id):
    return get(server_id)
