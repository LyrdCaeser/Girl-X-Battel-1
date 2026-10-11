"""Client inventory: every game model of the decompiled client (lua/app/models) with the windows that use it, the
data tables it reads and the network messages it sends, compared with what this local project reads/implements.

Reads ~/Downloads/Decomp files (read-only) and writes INVENTARIO_CLIENTE.md + validation/client-inventory.json.
Re-run after each wave:  python3 tools/build_client_inventory.py
"""
import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files/lua'
MODELS, WINDOWS = DEC / 'app/models', DEC / 'app/windows'
TABLE_CLASSES, DATA = DEC / 'app/common/tables', DEC / 'data/tables'

# Model → (local module/view, status). Status follows the master checklist syntax; [P] = partial, [T] = implemented
# and tested locally, [ ] = nothing playable. Keep in sync with ESTADO_PROYECTO.md.
LOCAL = {
    'PetTraining': ('pet_training.py / remaining-systems.js', '[T][P][M]'),
    'PetSlot': ('home_systems.py / pet_training.py Ulticore', '[T][P][M]'),
    'NewbieCamp': ('newbie_camp.py / newbie-camp.js', '[T][P][M]'),
    'GrowthDiary': ('growth_diary.py / growth-diary.js', '[T][P][M]'),
    'Backpack': ('engine.py / bag', '[T]'), 'Partner': ('engine.py / girls', '[T][P]'), 'HeroAttr': ('battle.py attrs', '[T]'),
    'Slot': ('engine.py (roster/slot)', '[T][P]'), 'Map': ('campaign.py', '[T][P]'), 'Summon': ('acquisition.py / capsule', '[T][P]'),
    'Prophet': ('acquisition.py Exchange', '[T][P][M]'), 'Gamble': ('acquisition.py Slots', '[T][P][M]'),
    'Shop': ('shops.py', '[T][P][M]'), 'Mission': ('missions.py', '[T][P][M]'), 'Achievement': ('missions.py Trophies', '[T][P]'),
    'DailyQuiz': ('engine.py daily quiz', '[T][P]'), 'TowerMap': ('engine.py Tests', '[T][P]'), 'Pet': ('home_systems.py Servants', '[T][P]'),
    'ExploreModel': ('explore.py', '[T][M]'), 'Arena': ('arena.py Junior Varsity', '[T][M]'), 'Mail': ('home_systems.py', '[T][M]'),
    'Friend': ('home_systems.py contactos / friend_boss.py actual', '[T][P][M]'), 'Activity': ('events.py / point_events.py', '[P][M]'),
    'ActivityData': ('events.py', '[P]'), 'ActivityDatas': ('events.py', '[P]'), 'SelfPlayer': ('engine.py perfil', '[T][P]'),
    'Player': ('engine.py perfil', '[P]'), 'Collection': ('galería', '[P]'), 'Dress': ('dress.py Outfits', '[T][P][M]'), 'Skin': ('skins.py girl skins', '[T][P][M]'),
    'ShenXue': ('engine.py Graduate', '[T][P]'), 'TeamFormation': ('engine.py formación', '[T]'), 'Dungeon': ('patrol.py Patrol', '[T][M]'), 'AcademyAssessment': ('house_exam.py House Exam', '[T][M]'), 'HeroChallenge': ('hero_challenge.py Normal+Puzzle', '[T][P][M]'), 'Trial': ('sanctuary.py Sanctuary', '[T][P][M]'), 'Tavern': ('internship.py Internship', '[T][M]'), 'Midas': ('midas.py Alchemy', '[T][M]'), 'OldSchool': ('old_campus.py Old Campus', '[T][P][M]'), 'TimeCloisterModel': ('echoes.py Echoes of Time', '[T][P][M]'), 'ShrineHurdleModel': ('shrine.py Realm of Trials', '[T][P][M]'), 'Shrine': ('shrine.py Message Board / Pond', '[T][M]'), 'GalaxyTrip': ('galaxy.py Galaxy Voyage', '[T][P][M]'), 'StoryListModel': ('story.py Main story + Memories', '[T][P]'),
    'SoulEquip1': ('souls.py Anima Artifact', '[T][P][M]'), 'SoulEquip2': ('souls.py Anima Stones', '[T][P][M]'), 'SoulLand': ('soul_land.py Land of Souls', '[T][P][M]'),
    'Guild': ('guild_lab.py / guild-lab.js (solo laboratorio)', '[P][M]'),
    'SettingUp': ('localStorage mute', '[P]'), 'Hero': ('battle.py / engine.py', '[T]'), 'Monster': ('battle.py', '[T]'), 'RedMark': ('web (parcial)', '[P]'),
}
SKIP = {'BaseModel', 'ModelManager', 'datas', 'ErrorModel', 'GMcommand', 'TextInput', 'FloatMessage', 'FloatMessage2', 'ItemFloatModel',
        'DeviceNotify', 'AdvertiseComplete', 'SelfShader', 'ImgGuide',
        'ACDFA', 'FunctionOpen', 'ItemInfo', 'SummonMemeoryWindow', 'ReportPetAttr'}


def snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def main():
    # accessor (xyd.tables.fooTable) → data file(s) the class loads
    class_file = {}
    tm = (TABLE_CLASSES / 'TableManager.lua').read_text(encoding='utf-8-sig', errors='ignore')
    for acc, cls in re.findall(r'metatable\.(\w+) = "app\.common\.tables\.(\w+)"', tm):
        class_file[acc] = cls
    loads = {}
    for f in TABLE_CLASSES.glob('*.lua'):
        loads[f.stem] = sorted(set(re.findall(r'ctor\(self, "([a-z0-9_]+?)_?"', f.read_text(encoding='utf-8-sig', errors='ignore'))))
    data_tables = sorted(p.stem for p in DATA.glob('*.lua'))

    local_text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for pat in ('gxb2/*.py', 'tools/*.py', 'web/*.js', 'server.py')
                           for p in ROOT.glob(pat) if p.name != Path(__file__).name)
    local_words = set(re.findall(r'[a-z][a-z0-9_]+', local_text))
    engine_text = (ROOT / 'gxb2/engine.py').read_text() + (ROOT / 'gxb2/protocol.py').read_text()

    windows = {f.stem: f.read_text(encoding='utf-8-sig', errors='ignore') for f in WINDOWS.glob('*.lua')}
    rows = []
    for f in sorted(MODELS.glob('*.lua')):
        name = f.stem
        if name in SKIP:
            continue
        text = f.read_text(encoding='utf-8-sig', errors='ignore')
        inst = name[0].lower() + name[1:]
        wins = sorted(w for w, t in windows.items() if f'xyd.models.{inst}' in t or f'xyd.models.{inst}:' in t)
        # Tables: the model plus its own windows (name prefix), so shared windows (formation, battle) don't add noise.
        stem = name[:-5] if name.endswith('Model') else name
        own = [w for w in windows if w.startswith(stem)]
        corpus = text + ''.join(windows[w] for w in own)
        wins = sorted(set(wins) | set(own))
        mids = sorted(set(re.findall(r'xyd\.mid\.([A-Z0-9_]+)', text)))
        accs = sorted(set(re.findall(r'xyd\.tables\.(\w+Table\w*)', corpus)))
        tables = sorted({d for a in accs for d in loads.get(class_file.get(a, ''), [])} & set(data_tables))
        used = [t for t in tables if t in local_words]
        mids_local = [m for m in mids if f"'{m}'" in engine_text or f'"{m}"' in engine_text]
        module, status = LOCAL.get(name, ('—', '[ ]'))
        rows.append({'model': name, 'windows': wins, 'tables': tables, 'tables_used': used, 'mids': mids, 'mids_local': mids_local,
                     'local': module, 'status': status})

    used_all = sorted(t for t in data_tables if t in local_words)
    groups = defaultdict(lambda: [0, 0])
    for t in data_tables:
        g = t.split('_')[0]
        groups[g][1] += 1
        groups[g][0] += t in local_words
    (ROOT / 'validation').mkdir(exist_ok=True)
    (ROOT / 'validation/client-inventory.json').write_text(json.dumps({'models': rows, 'tables_used': used_all, 'tables_total': len(data_tables)},
                                                                      ensure_ascii=False, indent=1))

    done = [r for r in rows if r['status'] != '[ ]']
    no_event = [t for t in data_tables if not t.startswith('activity')]
    out = ['# Inventario del cliente descompilado',
           '',
           '> Generado por `tools/build_client_inventory.py` desde `~/Downloads/Decomp files` (solo lectura). No editar a mano: '
           'actualizar el mapa `LOCAL` del script y volver a ejecutarlo. JSON completo en `validation/client-inventory.json`.',
           '',
           '## Resumen',
           '',
           'El mapa de estados LOCAL se mantiene manualmente y puede conservar estados históricos; una casilla vacía no prueba ausencia de implementación. Las referencias de tabla son léxicas y no certifican que se lean en ejecución.', '',
           f'- Modelos de juego del cliente: **{len(rows)}**; con implementación local (total o parcial): **{len(done)}** '
           f'({round(100 * len(done) / len(rows))}%).',
           f'- Tablas de datos originales: **{len(used_all)}/{len(data_tables)}** leídas por el proyecto '
           f'({round(100 * len(used_all) / len(data_tables))}%); sin eventos `activity_*`: '
           f'**{sum(t in local_words for t in no_event)}/{len(no_event)}** ({round(100 * sum(t in local_words for t in no_event) / len(no_event))}%).',
           f'- Mensajes de red referenciados por modelos: {sum(len(r["mids"]) for r in rows)}; el proyecto usa su propia API HTTP, '
           'así que la columna de mensajes solo cuenta los que `engine.py`/`protocol.py` nombran.',
           '',
           '## Modelos (sistemas) del cliente',
           '',
           '| Modelo | Estado local | Módulo local | Tablas usadas | Mensajes | Ventanas principales |',
           '|---|---|---|---|---|---|']
    order = sorted(rows, key=lambda r: (r['status'] != '[ ]', -len(r['tables']) - len(r['mids'])))
    for r in order:
        w = ', '.join(r['windows'][:4]) + (f' (+{len(r["windows"]) - 4})' if len(r['windows']) > 4 else '')
        out.append(f"| {r['model']} | {r['status']} | {r['local']} | {len(r['tables_used'])}/{len(r['tables'])} | "
                   f"{len(r['mids_local'])}/{len(r['mids'])} | {w or '—'} |")
    out += ['', '## Cobertura de tablas por prefijo', '', '| Prefijo | Usadas / total |', '|---|---|']
    for g, (u, n) in sorted(groups.items(), key=lambda x: -x[1][1]):
        if n >= 3:
            out.append(f'| `{g}_*` | {u}/{n} |')
    out += ['', '## Tablas sin usar por modelo pendiente', '']
    for r in order:
        if r['status'] == '[ ]' and r['tables']:
            out.append(f"- **{r['model']}**: " + ', '.join(f'`{t}`' for t in r['tables'][:14]) + (' …' if len(r['tables']) > 14 else ''))
    (ROOT / 'INVENTARIO_CLIENTE.md').write_text('\n'.join(out) + '\n')
    print(f'{len(rows)} modelos, {len(done)} con implementación; tablas {len(used_all)}/{len(data_tables)}')


if __name__ == '__main__':
    main()
