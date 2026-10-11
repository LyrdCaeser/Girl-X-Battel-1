"""Read archived Lua tables (SQLite columns can be displaced), copy selected original assets.
Never execute source Lua or write to Downloads. Output data/acquisition.json, web/assets/slots.
"""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/'Downloads/Decomp files'
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'

def read_table(name):
    text=(SOURCE/f'lua/data/tables/{name}.lua').read_text(encoding='utf-8-sig')
    head,body=text.split('table.rows =',1)
    keys={k:int(i) for k,i in re.findall(r'\b(\w+) = (\d+)',head)}
    result={}
    for rid,block in re.findall(r'\["(\d+)"\] = \{(.*?)\n\t\}',body,re.S):
        values=[json.loads(v.strip()) for v in block.strip().split(',\n')]
        assert len(values)==len(keys),(name,rid,len(values),len(keys))
        result[rid]={k:values[i-1] for k,i in keys.items()}
    assert result,name
    return result

def main():
    names=['partner_replace','gamble_config','gamble','gamble_up','shop_luck','shop_config']
    result={n:read_table(n) for n in names}
    result['shop_config']={'3':result['shop_config']['3']}
    boxes={int(r['dropbox_id']) for r in result['partner_replace'].values()}
    for table in ('gamble','gamble_up'):
        for r in result[table].values():
            boxes.update(int(v) for k,v in r.items() if k.startswith('dropbox_id') and v)
    result['dropbox']={k:r for k,r in json.loads((ROOT/'data/dropbox.json').read_text()).items() if int(r['dropbox_id']) in boxes}
    paths=[SOURCE/f'lua/data/tables/{n}.lua' for n in names]
    paths += [SOURCE/f'lua/app/{s}' for s in ['windows/ProphetWindow.lua','windows/ProphetChoosePartnerWindow.lua','models/Slot.lua','windows/GambleWindow.lua','models/Gamble.lua','models/Shop.lua','windows/ShopWindow.lua','common/tables/ShopConfigTable.lua']]
    out=ROOT/'web/assets/slots';out.mkdir(parents=True,exist_ok=True)
    for p in CUT.glob('gb_*.png'):shutil.copyfile(p,out/p.name)
    shutil.copyfile(CUT/'shop.png',out/'shop.png')
    for n in ('gb_normal_bg','gb_senior_bg'):
        p=SOURCE/f'unity/Assets/hotres/textures/scenes_web/{n}.png'
        if p.exists():shutil.copyfile(p,out/p.name)
    # Additional prize icons missing from the shared item-icon manifest (treasures/artifacts).
    catalog=json.loads((ROOT/'web/assets/items-catalog.json').read_text())
    shared=set(json.loads((ROOT/'web/assets/item-icons.json').read_text()))
    result['item_icons']={}
    for row in [*result['dropbox'].values(),*result['shop_luck'].values()]:
        iid=str(row['item']).split('#')[0];icon=catalog.get(iid,{}).get('icon')
        if not icon or icon in shared:continue
        p=CUT/(icon+'.png')
        if p.exists():
            shutil.copyfile(p,out/p.name);result['item_icons'][iid]=icon
    for p in sorted(out.glob('*.png')):
        source=CUT/p.name
        if p.stem in ('gb_normal_bg','gb_senior_bg'):source=SOURCE/f'unity/Assets/hotres/textures/scenes_web/{p.name}'
        if source.exists():paths.append(source)
    paths.append(ROOT/'data/dropbox.json')
    result['sources']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (ROOT/'data/acquisition.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({n:len(result[n]) for n in names},'dropbox rows',len(result['dropbox']),'prize icons',len(result['item_icons']))

if __name__=='__main__':main()
