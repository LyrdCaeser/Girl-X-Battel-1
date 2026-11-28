"""Render the original authoritative LuaJIT PvP report for its actual participant.

This module never simulates a battle, changes a winner, computes rewards, or
writes to the player database. It maps the exact server-computed combat timeline
to the viewer's side of the 720x1280 original BattleWindow.
"""
from __future__ import annotations

import copy


def _side_pos(value, viewer_is_a):
    try:
        pos = int(value)
    except (ValueError, TypeError):
        return value
    if not viewer_is_a:
        if 1 <= pos <= 12:
            return pos + 6 if pos <= 6 else pos - 6
        if pos in (13, 14):  # original Servant (pet) energy slots
            return 27 - pos
    return pos


def _unit(unit, side, viewer_is_a, names=None):
    pos = int(unit["pos"])
    if pos < 1 or pos > 6:
        raise ValueError("PvP combat unit outside original formation")
    pos = pos + (6 if side == "B" else 0)
    return {
        "pos": _side_pos(pos, viewer_is_a),
        "table_id": int(unit["table_id"]),
        "name": str(unit.get("name") or (names or {}).get(str(unit["table_id"])) or unit["table_id"]),
        "level": int(unit.get("level") or unit.get("lv") or 1),
        "skin_id": int(unit.get("skin_id") or 0),
    }


def for_viewer(report, viewer_uid, player_a_uid, player_b_uid, *, pet_a=None, pet_b=None, names=None):
    """Build a playback-only payload from a confirmed server report.

    The original authoritative report/winner are never mutated.
    Viewer B gets a 180-degree side swap so their own team stays on the left.
    """
    if not all(str(v or "").strip() for v in (viewer_uid, player_a_uid, player_b_uid)):
        raise ValueError("Missing PvP participant identity")
    if str(player_a_uid) == str(player_b_uid):
        raise ValueError("A PvP match requires two distinct participants")
    if str(viewer_uid) not in (str(player_a_uid), str(player_b_uid)):
        raise PermissionError("Only authenticated match participants may view this battle")
    if not isinstance(report, dict):
        raise ValueError("Battle report is missing")
    if not isinstance(report.get("frames"), list) or report.get("isWin") not in (0, 1):
        raise ValueError("Battle report is incomplete")
    viewer_is_a = str(viewer_uid) == str(player_a_uid)
    result = {
        "frames": copy.deepcopy(report["frames"]),
        "hp": copy.deepcopy(report.get("hp") or []),
        "hurts": copy.deepcopy(report.get("hurts") or []),
        "display_units": [
            _unit(u, side, viewer_is_a, names)
            for side, team in (("A", report.get("teamA") or []), ("B", report.get("teamB") or []))
            for u in team
        ],
        "isWin": int(report["isWin"]) if viewer_is_a else 1 - int(report["isWin"]),
        "total_round": int(report.get("total_round") or 0),
        "total_harm": int(report.get("total_harm") or 0),
        "map_asset": "battle_map_26_1",  # original battle map, no sample opponent
        "petA": copy.deepcopy(pet_a if viewer_is_a else pet_b),
    }
    if not viewer_is_a:
        for frame in result["frames"]:
            frame["pos"] = _side_pos(frame.get("pos"), False)
            for field in ("buffs", "eps"):
                values = frame.get(field)
                if isinstance(values, list):
                    for value in values:
                        if isinstance(value, dict):
                            for name in ("pos", "f_pos"):
                                if name in value:
                                    value[name] = _side_pos(value[name], False)
            for field in ("targets", "targets_2"):
                values = frame.get(field)
                if isinstance(values, list):
                    frame[field] = [_side_pos(pos, False) for pos in values]
        for field in ("hp", "hurts"):
            for row in result[field]:
                if "pos" in row:
                    row["pos"] = _side_pos(row["pos"], False)
    return result
