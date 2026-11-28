"""Stable summon tier budgets.

Publisher dropbox rows carry relative weights for individual girls. Appending
new rows must redistribute a tier's fixed budget instead of increasing the
whole tier and silently inflating rare-girl rates.
"""
from __future__ import annotations

from collections import defaultdict

WEIGHT_TOTAL = 1_000_000

# Exact probability budgets by native star. Wish uses the Advanced Capsule
# base distribution; its selected Wish Girl boost and 500-draw guarantee are
# applied separately by wish.py.
TIER_BUDGETS = {
    10001: {1: 560_000, 2: 340_000, 3: 85_000, 4: 14_500, 5: 500},
    10002: {3: 795_000, 4: 190_000, 5: 15_000},
    10005: {2: 320_000, 3: 540_000, 4: 132_000, 5: 8_000},
    10008: {3: 795_000, 4: 190_000, 5: 15_000},
}


def native_star(row, partner_table):
    table_id = str(row.get("item", "")).split("#")[0]
    girl = partner_table.get(table_id)
    return int(girl.get("max_star") or 0) if girl else 0


def _allocate(rows, budget):
    """Largest-remainder allocation preserving relative within-tier odds."""
    raw = [max(0, int(row.get("weight") or 0)) for row in rows]
    total = sum(raw)
    if budget <= 0 or total <= 0:
        return [0] * len(rows)
    exact = [budget * weight / total for weight in raw]
    out = [int(value) for value in exact]
    remaining = budget - sum(out)
    order = sorted(
        range(len(rows)),
        key=lambda i: (exact[i] - out[i], str(rows[i].get("id", ""))),
        reverse=True,
    )
    for index in order[:remaining]:
        out[index] += 1
    return out


def balanced_pool(rows, partner_table, dropbox_id, effective_weight):
    """Return cloned rows with fixed tier budgets and live multipliers.

    effective_weight is the existing global + per-world multiplier hook. Its
    ratio to a row's raw weight is applied after normalization, so admin rate
    controls work without allowing character-count inflation.
    """
    budget = TIER_BUDGETS.get(int(dropbox_id))
    if not budget:
        out = []
        for source in rows:
            weight = int(effective_weight(source))
            if weight > 0:
                row = dict(source)
                row["_local_weight"] = weight
                out.append(row)
        return out

    groups = defaultdict(list)
    for source in rows:
        star = native_star(source, partner_table)
        if star in budget and int(source.get("weight") or 0) > 0:
            groups[star].append(source)

    out = []
    for star, tier_budget in budget.items():
        tier = groups.get(star, [])
        for source, normalized in zip(tier, _allocate(tier, tier_budget)):
            raw = int(source.get("weight") or 0)
            effective = int(effective_weight(source))
            weight = int(round(normalized * effective / raw)) if raw > 0 else 0
            if weight > 0:
                row = dict(source)
                row["_local_weight"] = weight
                out.append(row)
    return out
