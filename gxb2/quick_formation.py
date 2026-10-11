"""Lineup presets (models/QuickFormation.lua, QuickFormationWindow; capture 2026-09-29-fb/44).

After campaign stage 8-5 (QUICK_FORMATION_TEXT18) the player owns 3 preset lineups. Each keeps up to 6 girls with their
position, gear (weapon / clothes / accessory / shoes / antique) and Limit-Break potentials, without touching the current
team. "Set" applies a preset: the battle formation becomes it, each girl gets its saved potentials, and the saved gear is
moved onto her (from the bag or from the girl wearing it; a piece that is gone is skipped and reported). Names are
editable (6 characters at most). Local rule (LOCAL-048): only the 3 free presets (the gem price of more is not in the
client), and girls in a preset are not protected from being consumed."""
from __future__ import annotations
from . import equipment

OPEN_STAGE = 77  # campaign 8-5
SLOTS = 3
GEAR = equipment.GEAR_SLOTS


class QuickError(ValueError):
    pass


def data(state):
    q = state.setdefault('quick_formations', [])
    while len(q) < SLOTS: q.append({'name': f'Lineup {len(q) + 1}', 'team': []})
    return q


def snapshot(state, developer=False):
    return {'open': developer or int(state.get('max_stage', 0)) >= OPEN_STAGE, 'lineups': data(state)}


def action(state, request, developer=False):
    if not snapshot(state, developer)['open']: raise QuickError('Available after passing Stage 8-5 in Campaign')
    q = data(state); idx = int(request.get('index') or 0)
    if not 0 <= idx < SLOTS: raise QuickError('Alineación inválida')
    owned = {p['partner_id']: p for p in state['partners']}
    act = request.get('action')
    if act == 'save':
        team = request.get('team')
        if team is None: team = state.get('formation') or []
        if not isinstance(team, list) or len(team) > 6: raise QuickError('Formación inválida')
        out, seen = [], set()
        for slot in team:
            pid, pos = int(slot.get('partner_id') or 0), int(slot.get('pos') or 0)
            if pid not in owned or pid in seen or not 1 <= pos <= 6: raise QuickError('Chica o posición inválida')
            seen.add(pid); p = owned[pid]
            out.append({'partner_id': pid, 'pos': pos, 'equips': list(equipment.equips_of(p)), 'potentials': list(p.get('potentials') or [])})
        q[idx]['team'] = sorted(out, key=lambda x: x['pos'])
        return {'lineup': q[idx]}
    if act == 'rename':
        name = str(request.get('name') or '').strip()
        if not name or len(name) > 6: raise QuickError('6 characters at most')
        q[idx]['name'] = name
        return {}
    if act == 'clear':
        q[idx]['team'] = []
        return {}
    if act == 'set':
        team = [t for t in q[idx]['team'] if t['partner_id'] in owned]
        if not team: raise QuickError('You need to preset this lineup first')
        missing = []
        for t in team:
            p = owned[t['partner_id']]; slots = equipment.equips_of(p)
            if t.get('potentials'): p['potentials'] = list(t['potentials'])
            for s in GEAR:
                want = int((t.get('equips') or [0] * 7)[s - 1] or 0)
                if slots[s - 1] == want: continue
                if not want:
                    equipment.add(state, slots[s - 1], 1); slots[s - 1] = 0; continue
                if not equipment.have(state, want):
                    donor = next((o for o in state['partners'] if o is not p and equipment.equips_of(o)[s - 1] == want), None)
                    if donor:
                        donor['equips'][s - 1] = 0; equipment.add(state, want, 1)
                if not equipment.have(state, want):
                    missing.append(want); continue
                equipment.add(state, want, -1)
                if slots[s - 1]: equipment.add(state, slots[s - 1], 1)
                slots[s - 1] = want
        state['formation'] = [{'partner_id': t['partner_id'], 'pos': t['pos']} for t in team]
        return {'missing': missing}
    raise QuickError('Acción de alineación desconocida')
