from __future__ import annotations

import copy
import json
import math
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "local_config.json"
OVERRIDE_PATH = ROOT / "state" / "local_config.json"
_CACHE_LOCK = threading.RLock()
_CACHE_SIGNATURE = None
_CACHE_VALUE = None

_FALLBACK = {
    "starting_resources": {"1": 10000, "2": 0, "3": 0, "9": 5000, "11": 100, "12": 1000, "33": 10, "36": 10},
    "starter_girls": [41001, 42001, 43001],
    "summon_rate": {"star_multiplier": {"1": 1.0, "2": 1.0, "3": 1.0, "4": 1.0, "5": 1.0, "6": 1.0}},
    "shop": {"price_multiplier": 1.0},
    "rewards": {"multiplier": 1.0},
    "progression": {"cost_multiplier": 1.0},
}


def _merge(base, override):
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _number(value, name, low=0.0, high=100.0):
    if isinstance(value, bool):
        raise ValueError(f"{name}: giá trị không hợp lệ")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: phải là số")
    if not low <= value <= high:
        raise ValueError(f"{name}: phải nằm trong khoảng {low}–{high}")
    return value


def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError("Cấu hình Local phải là object")
    merged = _merge(_FALLBACK, raw)

    resources = merged.get("starting_resources")
    if not isinstance(resources, dict):
        raise ValueError("starting_resources phải là object")
    clean_resources = {}
    for item_id, amount in resources.items():
        try:
            iid, qty = str(int(item_id)), int(amount)
        except (TypeError, ValueError):
            raise ValueError("Tài nguyên khởi đầu phải dùng item ID và số lượng nguyên")
        if qty < 0 or qty > 2_000_000_000:
            raise ValueError(f"Tài nguyên {iid}: số lượng ngoài giới hạn")
        clean_resources[iid] = qty
    merged["starting_resources"] = clean_resources

    starters = merged.get("starter_girls")
    if not isinstance(starters, list) or not 1 <= len(starters) <= 6:
        raise ValueError("starter_girls phải có từ 1 đến 6 ID")
    merged["starter_girls"] = [int(x) for x in starters]

    stars = merged.setdefault("summon_rate", {}).setdefault("star_multiplier", {})
    clean_stars = {}
    for star in range(1, 7):
        clean_stars[str(star)] = _number(stars.get(str(star), 1), f"Tỷ lệ {star}★", 0.0, 100.0)
    merged["summon_rate"]["star_multiplier"] = clean_stars

    merged.setdefault("shop", {})["price_multiplier"] = _number(
        merged.get("shop", {}).get("price_multiplier", 1), "Hệ số giá Shop", 0.0, 100.0
    )
    merged.setdefault("rewards", {})["multiplier"] = _number(
        merged.get("rewards", {}).get("multiplier", 1), "Hệ số phần thưởng", 0.0, 100.0
    )
    merged.setdefault("progression", {})["cost_multiplier"] = _number(
        merged.get("progression", {}).get("cost_multiplier", 1), "Hệ số chi phí tiến triển", 0.0, 100.0
    )
    return merged


def _read(path):
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _signature(path):
    try:
        stat = path.stat()
        return (str(path), stat.st_ino, stat.st_mtime_ns, stat.st_size)
    except OSError:
        return (str(path), None, None)


def _effective():
    """Cached validated configuration; file signatures invalidate it after QTV save/reset."""
    global _CACHE_SIGNATURE, _CACHE_VALUE
    signature = (_signature(DEFAULT_PATH), _signature(OVERRIDE_PATH))
    with _CACHE_LOCK:
        if signature != _CACHE_SIGNATURE or _CACHE_VALUE is None:
            defaults = _merge(_FALLBACK, _read(DEFAULT_PATH))
            _CACHE_VALUE = validate(_merge(defaults, _read(OVERRIDE_PATH)))
            _CACHE_SIGNATURE = signature
        return _CACHE_VALUE


def get():
    # Public callers receive a detached copy and cannot mutate the shared cache.
    return copy.deepcopy(_effective())


def save(raw):
    cfg = validate(raw)
    OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = OVERRIDE_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(OVERRIDE_PATH)
    return cfg


def reset():
    if OVERRIDE_PATH.exists():
        OVERRIDE_PATH.unlink()
    return get()


def starting_resources():
    return dict(_effective()["starting_resources"])


def starter_girls():
    return list(_effective()["starter_girls"])


def scale_cost(value):
    value = int(value)
    if value <= 0:
        return 0
    mult = _effective()["progression"]["cost_multiplier"]
    return max(0, int(math.ceil(value * mult)))


def scale_reward(value):
    value = int(value)
    if value <= 0:
        return 0
    mult = _effective()["rewards"]["multiplier"]
    return max(0, int(math.floor(value * mult)))


def shop_cost(value):
    value = int(value)
    if value <= 0:
        return 0
    mult = _effective()["shop"]["price_multiplier"]
    return max(0, int(math.ceil(value * mult)))


def summon_weight(row, partner_table):
    base = int(row.get("weight") or 0)
    if base <= 0:
        return 0
    table_id = str(row.get("item", "")).split("#")[0]
    girl = partner_table.get(table_id)
    if not girl:
        return base
    star = max(1, min(6, int(girl.get("max_star") or 1)))
    mult = _effective()["summon_rate"]["star_multiplier"].get(str(star), 1.0)
    return max(0, int(round(base * mult)))


def public_config():
    return get()
