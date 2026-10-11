"""Copy selected original cut sprites and archive menu rules; source remains read-only."""
import csv, json, re, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/'Downloads/Decompiled'
OUT=ROOT/'web/assets/home-systems'; OUT.mkdir(parents=True,exist_ok=True)
tables={}
for name in ('pet','exp_pet','pet_skill','pet_exskill','battlepass_mission','battlepass_award','shop_battlepass','travel_building1','travel_building2','travel_building3','travel_train','travel_explore','travel_box','travel_event','travel_facility_add','starry_altar','activity_lafuli_award','activity_lafuli_shop','activity_lafuli_drift','giftbag'):
    with (SOURCE/f'Text and Data Tables/tables/{name}.csv').open(encoding='utf-8-sig',newline='') as f: tables[name]=list(csv.DictReader(f))
for name in ('battlepass_mission','giftbag'):
    with (SOURCE/f'Text and Data Tables/tables/en_en/{name}_text_en_en.csv').open(encoding='utf-8-sig',newline='') as f: tables[name+'_text']=list(csv.DictReader(f))
with (SOURCE/'Text and Data Tables/tables/misc.csv').open(encoding='utf-8-sig',newline='') as f:
    tables['misc']={r['key']:r['value'] for r in csv.DictReader(f) if r['key'].startswith('travel_') or r['key'] in ('love_coin_daily_max','friend_search_level')}
with (SOURCE/'Text and Data Tables/combined_tables/dropbox.csv').open(encoding='utf-8-sig',newline='') as f:
    tables['dropbox']=[r for r in csv.DictReader(f) if r['dropbox_id']=='80001']
assets=[]
for p in sorted((SOURCE/'Sprites (atlases, cut)').glob('*.png')):
    name=p.stem
    if not name.startswith(('pet_avatar_','pet_frame_','pet_skill_','pet_bg','pet_kind','pet_icon','mail_','friend_icon_','friend_btn_','friend_rank_','battle_pass_','travel_','explore_','starry_','lafuli_','activity_lafuli_','activity_drift_')): continue
    if re.search(r'_(zh_cn|zh_tw|fr_fr|de_de|ja_jp|ko_kr)',name) or ' (' in name: continue
    shutil.copyfile(p,OUT/p.name);assets.append(name)
for name in ('pet_scene1','starry_altar_bg','activity_lafuli_castle_bg','activity_lafuli_drift_bg'):
    p=SOURCE/f'Images (backgrounds)/scenes/{name}.png'
    if p.exists(): shutil.copyfile(p,OUT/p.name);assets.append(name)
item_ids={1,2,26,27,117,203,204,205,216,221,222,232,358}
for rows in tables.values():
    if not isinstance(rows,list): continue
    for r in rows:
        for text in r.values():
            for match in re.finditer(r'(\d+)#\d+',text or ''): item_ids.add(int(match[1]))
with (SOURCE/'Text and Data Tables/combined_tables/item.csv').open(encoding='utf-8-sig',newline='') as f:
    items={r['id']:{'icon':r['icon']} for r in csv.DictReader(f) if int(r['id']) in item_ids}
for r in items.values():
    p=SOURCE/f"Sprites (atlases, cut)/{r['icon']}.png"
    if r['icon'] and p.exists() and r['icon'] not in assets:
        shutil.copyfile(p,OUT/p.name);assets.append(p.stem)
(ROOT/'data/home_systems.json').write_text(json.dumps(tables,ensure_ascii=False))
# Keep large per-level cost tables on the backend only.
public={k:v for k,v in tables.items() if k not in ('exp_pet','pet_skill','pet_exskill','giftbag_text','giftbag')}
public['gift_previews']=[{'id':r['id'],'title':r['desc_1'],'price':r['price'],'currency':r['currency'],'daily_diamond':r['daily_diamond']} for r in tables['giftbag'] if r['desc_1'] and r['desc_1']!='-1'][:8]
public.update(assets=sorted(set(assets)),items=items)
(OUT/'catalog.json').write_text(json.dumps(public,ensure_ascii=False))
print(f'{len(set(assets))} sprites/backgrounds, {len(tables)} rule tables')
