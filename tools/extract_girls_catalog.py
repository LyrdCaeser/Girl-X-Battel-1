"""Girls catalogue (web/assets/girls-catalog.json) rebuilt from the partner table: every girl the client lists in the
guide — show_in_guide 1 (launch roster) or a release timestamp (girls added later, including the three Cosmic girls
of group 7, 757001-757003). Fields: id, name (partner_text), group, job, stars (max_star), skins (skin_ids), art
(web/assets/characters/<id>.png exists). Also copies the missing partner_card_<id> cards and refreshes cards.json.
Sources in ~/Downloads are read only."""
import json, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets'
partners = json.loads((ROOT / 'data/partner.json').read_text())
db = sqlite3.connect(DEC / 'data/en_en.db')
# partner_text_en_en columns are shifted in the export: the girl's name sits in the second column
names = {str(r[0]): r[1] for r in db.execute('select * from partner_text_en_en')}
catalog = []
for pid, row in sorted(partners.items(), key=lambda kv: int(kv[0])):
    if str(row.get('show_in_guide') or 0) in ('0', ''):
        continue
    catalog.append({'id': int(pid), 'name': names.get(pid, ''), 'group': int(row['group']), 'job': int(row['job']),
                    'stars': int(row['max_star']), 'skins': [int(x) for x in str(row.get('skin_ids') or '').split('|') if x.strip()],
                    'art': (OUT / 'characters' / f'{pid}.png').exists(),
                    # the 5★ re-issues (54xxxx: `host` = the base girl) have no art of their own; the client draws the host's
                    **({'host': int(row['host'])} if str(row.get('host') or '').strip() else {})})
(OUT / 'girls-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')))
cards = set(json.loads((OUT / 'cards.json').read_text()))
copied = 0
for g in catalog:
    src, dst = CUT / f"partner_card_{g['id']}.png", OUT / 'cards' / f"partner_card_{g['id']}.png"
    if src.exists():
        if not dst.exists():
            shutil.copy2(src, dst); copied += 1
        cards.add(g['id'])
(OUT / 'cards.json').write_text(json.dumps(sorted(cards)))
print(len(catalog), 'girls,', sum(g['group'] == 7 for g in catalog), 'cosmic,', copied, 'cards copied')
