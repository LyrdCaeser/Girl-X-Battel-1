"""Main story (StoryWindow / xyd.StoryType.MAIN, StoryListModel, StoryMemoryWindow) offline.

Recovered from the client:
- main_plot_list ties a campaign stage to its plots "#pre#post": `pre` plays when the stage's battle starts
  (BattleWindow, plotIds[2]) and `post` after winning it (BattleController, plotIds[3]).
- A plot is a chain of main_plot lines (next_id) with background, character picture, name ('*' = the player), dialog,
  voice / music / ambience (sound table), shake and CG.
- Memories: episode → chapter (main_plot_fort) → section (main_plot_list). A section is open when its stage is cleared,
  or it can be unlocked with 2 Key of Memory (208) once the previous section is open (StoryListUnlockWindow).

LOCAL (DESIGN_DECISIONS.md LOCAL-039): the campaign plays each scene the first time only (they can be replayed in
Memories); "male|female" dialog variants use the first one.
"""
from __future__ import annotations
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/story.json').read_text())
LINES = DATA['lines']
LIST = {r['id']: r for r in DATA['list']}
BY_STAGE = {r['stage']: r for r in DATA['list'] if r['stage']}
KEY = '208'


def scene(start):
    out, seen, cur = [], set(), int(start)
    while cur and str(cur) in LINES and cur not in seen and len(out) < 400:
        seen.add(cur)
        out.append(LINES[str(cur)])
        cur = int(LINES[str(cur)].get('x') or 0)
    return out


def saved(state):
    s = state.setdefault('story', {})
    s.setdefault('seen', []); s.setdefault('unlocked', [])
    return s


def section_open(state, s, sid):
    r = LIST[sid]
    return (r['stage'] and int(state.get('max_stage', 0)) >= r['stage']) or sid in s['unlocked']


def stage_plots(state, stage_id):
    """(pre, post) plots of a campaign stage that haven't been watched yet."""
    r = BY_STAGE.get(int(stage_id))
    if not r:
        return 0, 0
    seen = set(saved(state)['seen'])
    return (r['pre'] if r['pre'] and r['pre'] not in seen else 0), (r['post'] if r['post'] and r['post'] not in seen else 0)


def action(state, request):
    s = saved(state)
    kind = request.get('action')
    if kind == 'seen':
        pid = int(request.get('plot', 0))
        if str(pid) in LINES and pid not in s['seen']:
            s['seen'].append(pid)
        return {}
    if kind == 'unlock':
        sid = int(request.get('id', 0))
        if sid not in LIST:
            raise ValueError('Historia no válida')
        if section_open(state, s, sid):
            return {}
        former = LIST[sid]['former']
        if former and not section_open(state, s, former):
            raise ValueError('Unlock by completing previous story section')
        k, n = (LIST[sid]['unlock'] or f'{KEY}#2').split('#')
        items = state.setdefault('items', {})
        if int(items.get(k, 0)) < int(n):
            raise ValueError('No tienes suficientes Key of Memory')
        items[k] = int(items[k]) - int(n)
        s['unlocked'].append(sid)
        return {}
    raise ValueError('Acción de historia no disponible')


def snapshot(state):
    import copy
    s = saved(copy.deepcopy(state))
    return {'open': sorted(sid for sid in LIST if section_open(state, s, sid)), 'seen': s['seen'],
            'keys': int(state.get('items', {}).get(KEY, 0))}


def catalog():
    return {'episodes': DATA['episodes'], 'forts': DATA['forts'], 'text': DATA['text'],
            'sections': [{k: r[k] for k in ('id', 'stage', 'fort', 'label', 'pre', 'post', 'memory', 'unlock', 'former', 'icon', 'name')} for r in DATA['list']]}
