"""Use/open only items documented by the recovered original game tables.

Original sources: item.json -> type (27=choice, 14=gift), show_in_bag,
giftbox_optional.json -> selectable reward pairs, gift.json -> guaranteed rewards
or dropbox_ids, dropbox.json -> original weighted pools. No inferred rewards.
"""
from __future__ import annotations

import json
import secrets
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/recovered/tables'
MAX_OPEN = 50


def _table(name):
    return json.loads((SOURCE / (name + '.json')).read_text(encoding='utf-8'))


def _cells(table, key):
    row = table['rows'].get(str(key))
    return {name: row[pos - 1] for name, pos in table['keys'].items()} if row else None


def _pair(text):
    parts = str(text).split('#')
    if len(parts) != 2 or not all(part.isdecimal() for part in parts):
        raise ValueError('Bảng thưởng gốc không hợp lệ')
    key, amount = map(int, parts)
    if key <= 0 or amount <= 0:
        raise ValueError('Bảng thưởng gốc không hợp lệ')
    return key, amount


def _reward_pairs(text):
    if not text: return {}
    out = {}
    for pair in str(text).split('|'):
        item, count = _pair(pair)
        out[item] = out.get(item, 0) + count
    return out


@lru_cache(maxsize=1)
def recipes():
    """Compile recovered authoritative item/reward data, skip incomplete rows."""
    items, optional, gifts, dropboxes = [_table(name) for name in
        ('item', 'giftbox_optional', 'gift', 'dropbox')]
    pools = {}
    dkeys = dropboxes['keys']
    for row in dropboxes['rows'].values():
        group, weight = str(row[dkeys['dropbox_id'] - 1]), int(row[dkeys['weight'] - 1])
        if weight <= 0: continue
        spec = str(row[dkeys['item'] - 1]).split('#')
        if len(spec) not in (2, 3) or not all(x.isdecimal() for x in spec):
            continue
        item_id = int(spec[0])
        low = int(spec[1]); high = int(spec[2]) if len(spec) == 3 else low
        if item_id <= 0 or low <= 0 or high < low or str(item_id) not in items['rows']:
            continue
        pools.setdefault(group, []).append((item_id, low, high, weight))

    compiled = {}
    for item_id, row in items['rows'].items():
        record = _cells(items, item_id)
        if record is None or int(record['show_in_bag'] or 0) != 1:
            continue
        kind = int(record['type'] or 0)
        if kind == 27:
            opt = _cells(optional, item_id)
            if not opt or not opt['item']: continue
            choices = {}
            try:
                for spec in str(opt['item']).split('|'):
                    reward_id, amount = _pair(spec)
                    if str(reward_id) not in items['rows']:
                        raise ValueError('Không có vật phẩm gốc')
                    choices[str(reward_id)] = amount
            except ValueError:
                continue
            if choices: compiled[item_id] = {'kind': 'choice', 'choices': choices}
        elif kind == 14:
            gift = _cells(gifts, record['gift_id'])
            if not gift: continue
            try:
                fixed = _reward_pairs(gift['awards'])
                if any(str(reward_id) not in items['rows'] for reward_id in fixed):
                    continue
                pool_ids = [s for s in str(gift['dropbox_ids'] or '').split('|') if s]
                if any(not pools.get(s) for s in pool_ids):
                    continue
                if not fixed and not pool_ids: continue
                compiled[item_id] = {'kind': 'gift', 'fixed': fixed,
                                     'pools': [pools[s] for s in pool_ids]}
            except (ValueError, TypeError):
                continue
    return compiled


def describe(item_id):
    """UI is given only source-derived choices, never a free-form reward ID."""
    item_id = str(item_id)
    recipe = recipes().get(item_id)
    if not recipe:
        return {'usable': False, 'item_id': item_id, 'reason':
                'Vật phẩm này không có công thức Dùng/Mở được xác thực từ dữ liệu gốc.'}
    if recipe['kind'] == 'choice':
        catalog = _catalog()
        return {'usable': True, 'item_id': item_id, 'kind': 'choice',
                'choices': [{'id': int(rid), 'amount': amount,
                             'name': catalog.get(rid, {}).get('name') or 'Vật phẩm #' + rid}
                            for rid, amount in recipe['choices'].items()],
                'max_per_use': MAX_OPEN}
    return {'usable': True, 'item_id': item_id, 'kind': 'gift',
            'random': bool(recipe['pools']), 'max_per_use': MAX_OPEN}


@lru_cache(maxsize=1)
def _catalog():
    return json.loads((ROOT / 'web/assets/items-catalog.json').read_text(encoding='utf-8'))


def open_in_state(state, item_id, count, reward_id=None):
    """Mutate only an already transaction-locked state; caller commits atomically."""
    if any(isinstance(v, (bool, float, list, dict)) for v in (item_id, count)):
        raise ValueError('ID hoặc số lượng vật phẩm không hợp lệ')
    if not str(item_id).isdecimal() or not str(count).isdecimal():
        raise ValueError('ID hoặc số lượng vật phẩm không hợp lệ')
    item_id, count = str(int(item_id)), int(count)
    recipe = recipes().get(item_id)
    if not recipe:
        raise ValueError('Không có chức năng Dùng/Mở từ nguồn gốc cho vật phẩm này')
    if count < 1 or count > MAX_OPEN:
        raise ValueError('Số lượng sử dụng không hợp lệ')
    old = int(state.get('items', {}).get(item_id, 0))
    if old < count:
        raise ValueError('Không đủ vật phẩm trong Túi Đồ')
    rewards = {}
    if recipe['kind'] == 'choice':
        if isinstance(reward_id, (bool, float)) or not str(reward_id).isdecimal():
            raise ValueError('Cần chọn đúng phần thưởng gốc')
        chosen = str(int(reward_id))
        if chosen not in recipe['choices']:
            raise ValueError('Phần thưởng không nằm trong danh sách gốc')
        rewards[int(chosen)] = recipe['choices'][chosen] * count
    else:
        if reward_id not in (None, '', 0):
            raise ValueError('Rương này không cho phép tự chọn phần thưởng')
        for rid, amount in recipe['fixed'].items():
            rewards[rid] = rewards.get(rid, 0) + amount * count
        for pool in recipe['pools']:
            total = sum(row[3] for row in pool)
            for _ in range(count):
                roll = secrets.randbelow(total)
                for rid, low, high, weight in pool:
                    if roll < weight:
                        amount = low + secrets.randbelow(high - low + 1)
                        rewards[rid] = rewards.get(rid, 0) + amount
                        break
                    roll -= weight
    state['items'][item_id] = old - count
    for rid, amount in rewards.items():
        key = str(rid)
        state['items'][key] = int(state['items'].get(key, 0)) + amount
    return {str(rid): amount for rid, amount in rewards.items()}
