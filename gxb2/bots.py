"""Bots: simulated players for everything that needed other people (rankings, comments, chat).

LOCAL (LOCAL-085): there is no server and no other player. The 50 persistent rivals of Junior Varsity (gxb2/arena.ladder: the
15 original robots + NPC rivals) are reused as a stable cast. Everything here is deterministic (hash of bot, topic and day),
so the same save shows the same world on any machine and nothing is stored: bots never change the player's save.
- rank(kind, mine): a leaderboard for `kind` where each bot's score grows a little every day up to its own ceiling (a share of
  the kind's maximum), with the player inserted at their real value.
- comments(topic): a few canned lines with like counts for the Student Files "Review" tab.
- chat(channel, now): a rolling window of canned messages, one every few minutes.
Bots are labelled as such in DESIGN_DECISIONS; the UI shows them like players of server S1.
"""
from __future__ import annotations
import hashlib, time
from . import arena

EPOCH = 1_790_000_000   # bots "started playing" here; their progress is measured in days since then


def h(*parts):
    return int(hashlib.sha256('|'.join(str(p) for p in parts).encode()).hexdigest()[:12], 16)


def cast():
    out = []
    for r in arena.ladder():
        skill = (r['id'] * 37 % 50 + 1) / 50
        out.append({'id': r['id'], 'name': r['name'], 'lv': max(int(r['lv']), int(60 + 330 * skill)), 'avatar': r['avatar'], 'skill': skill})
    return out


# kind → (maximum score, days for the strongest bot to reach its ceiling, label)
KINDS = {'soul_land': (150, 40, 'Stages'), 'shrine': (2_000_000, 30, 'Points'), 'cafeteria': (60, 7, 'Orders'),
         'guild_boss': (5_000_000_000, 20, 'Damage'), 'tower': (1500, 120, 'Floor')}


def rank(kind, mine, name='You', lv=1, now=None, top=50):
    now = int(time.time()) if now is None else now
    cap, days, label = KINDS[kind]
    day = max(0, (now - EPOCH) // 86400)
    rows = []
    for b in cast():
        ceiling = cap * (0.25 + 0.7 * b['skill'])
        speed = 0.5 + (h(kind, b['id']) % 100) / 100                     # 0.5 – 1.5× the base pace
        wobble = (h(kind, b['id'], day) % 7) / 100                        # small daily movement
        prog = min(1.0, day * speed / days) if kind != 'cafeteria' else ((day % 7 + 1) / 7) * speed / 1.5
        rows.append({'name': b['name'], 'lv': b['lv'], 'avatar': b['avatar'], 'score': int(ceiling * min(1.0, prog + wobble)), 'bot': True})
    rows.append({'name': name, 'lv': lv, 'score': int(mine), 'me': True})
    rows.sort(key=lambda r: (-r['score'], not r.get('me')))
    for i, r in enumerate(rows): r['rank'] = i + 1
    me = next(r for r in rows if r.get('me'))
    return {'label': label, 'rows': rows[:top], 'me': me}


LINES = ['She carried my whole team in Tests.', 'Best girl, no discussion.', 'Needs her Anima Gear to shine, but then she is a monster.',
         'I pair her with a healer and never lose.', 'Got her to 10★ last week, totally worth the Lunch Boxes.', 'Her skin is so cute!!',
         'Underrated in Junior Varsity, try her in the back row.', 'Speed is everything with her, stack it.', 'My first 5★ ♥',
         'Great in Guild Boss, weak in Patrol.', 'Her voice lines are the best in the game.', 'Still waiting for her wedding skin…',
         'Put her in front and watch her block everything.', 'Anyone has a good lineup for her?', 'Graduated her today, finally!']


def comments(topic, now=None, n=5):
    now = int(time.time()) if now is None else now
    people = cast(); out = []
    k = 3 + h('n', topic) % (n - 2)
    for i in range(k):
        b = people[h('who', topic, i) % len(people)]
        out.append({'name': b['name'], 'lv': b['lv'], 'avatar': b['avatar'], 'text': LINES[h('line', topic, i) % len(LINES)],
                    'likes': 5 + h('like', topic, i) % 400, 'time': now - 86400 * (1 + h('age', topic, i) % 30), 'bot': True})
    out.sort(key=lambda c: -c['likes'])
    return {'hot': out, 'likes': 200 + h('likes', topic) % 9000}


CHAT = {'world': ['Anyone for Security Squad?', 'gm senpais', 'Finally cleared Tests 500!', 'Which girl should I graduate first?', 'Pulled a 5★ from a Regular Capsule lol',
                  'Is the Fantasy Book worth buying levels?', 'Dorm comfort tips?', 'That new skin though ♥', 'How do you beat Land of Souls stage 30?', 'gn everyone',
                  'Tsuruga this season is brutal', 'Free hearts, add me', 'lf active guild', 'Daily Quiz done ✔', 'Who else is saving gems?'],
        'english': ['Hello from S1!', 'Any tips for a new player?', 'What is the best Faction Aura right now?', 'Thanks for the hearts!', 'How do Exchange Portfolios work?',
                    'Use your Seals on Fairy, trust me.', 'Is Sapphire good?', 'Level your Servant first.'],
        'servers': ['S1 best server', 'Cross-server arena when?', 'gg to everyone in Varsity', 'S26 says hi'],
        'recruit': ['[Firefly] recruiting, Lv.200+, daily sign in', '[Waifu] casual guild, everyone welcome', '[Hazzards] top 10 Gym, need active members',
                    '[Squatopia] cafeteria Lv.5, join us', '[MoonCats] new guild, growing fast']}


def chat(channel, now=None, n=14, every=420):
    now = int(time.time()) if now is None else now
    lines = CHAT.get(channel)
    if not lines: return []
    people = cast(); slot = now // every; out = []
    for i in range(n):
        s = slot - (n - 1 - i)
        b = people[h('chat', channel, s) % len(people)]
        out.append({'name': b['name'], 'lv': b['lv'], 'avatar': b['avatar'], 'text': lines[h('msg', channel, s) % len(lines)], 'time': s * every, 'bot': True})
    return out


def snapshot(state, level, now=None):
    """Leaderboards and chat for the engine snapshot (read only)."""
    now = int(time.time()) if now is None else now
    name = state.get('name') or 'You'
    land = sum(int(f.get('cleared') and f['cleared'] - f['first'] + 1 or 0) for f in ((state.get('soul_land_info') or {}).get('forts') or []))
    shrine = sum(int(r.get('best') or 0) for r in ((state.get('shrine_info') or {}).get('routes') or []))
    orders = int(((state.get('missions') or {}).get('totals') or {}).get('guild_orders', 0))
    tower = int((state.get('tower') or {}).get('max_stage', 0) or 0)
    return {'ranks': {'soul_land': rank('soul_land', land, name, level, now), 'shrine': rank('shrine', shrine, name, level, now),
                      'cafeteria': rank('cafeteria', orders, name, level, now, top=20), 'tower': rank('tower', tower, name, level, now)},
            'chat': {c: chat(c, now) for c in CHAT}}
