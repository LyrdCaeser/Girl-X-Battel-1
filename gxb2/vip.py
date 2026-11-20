"""Paid VIP progression; the original VIP tiers/perks remain unchanged.

VIP EXP is earned only when a verified GM mail or approved paid order is
*claimed* by the exact UID/server owner. Campaign, login, tasks and trophies
must never influence VIP level.
"""
import json
from pathlib import Path

LEVELS = json.loads((Path(__file__).resolve().parents[1] / "data/vip.json").read_text())["levels"]
MAX_LEVEL = len(LEVELS) - 1
# Server-side only virtual reward code: not a consumable inventory item.
VIP_EXP_REWARD_ID = "999999991"
MAX_VIP_EXP_REWARD = 2_000_000


def exp(state):
    return max(0, int(state.get("vip_paid_exp", 0)))


def breakdown(state):
    return {"paid": exp(state)}


def level_for(total):
    total = max(0, int(total))
    return max(int(row["level"]) for row in LEVELS if int(row["need_exp"]) <= total)


def info(state, developer=False):
    total = exp(state)
    lv = MAX_LEVEL if developer else level_for(total)
    next_tier = LEVELS[lv + 1] if lv < MAX_LEVEL else None
    return {
        "level": lv, "exp": total, "base": LEVELS[lv]["need_exp"],
        "next": next_tier["need_exp"] if next_tier else None,
        "sources": breakdown(state), "weights": {}, "perks": LEVELS[lv],
        "next_perks": next_tier,
    }


def apply(state, developer=False):
    lv = info(state, developer)["level"]
    state["vip"] = state["vip_level"] = lv
    return lv


def claim_reward(state, attachments):
    """Apply a mail-only VIP EXP award exactly once within the mail claim transaction.

    The mail claim transaction enforces single-use and UID/server isolation.
    This function never accepts arbitrary player requests.
    """
    gain = int(attachments.pop(VIP_EXP_REWARD_ID, 0))
    if gain < 0 or gain > MAX_VIP_EXP_REWARD:
        raise ValueError("VIP EXP không hợp lệ")
    if gain:
        state["vip_paid_exp"] = exp(state) + gain
        apply(state)
    return gain
