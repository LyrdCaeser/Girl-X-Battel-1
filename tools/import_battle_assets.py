"""Import base chibis from the archived Unity export, without changing sources."""
from pathlib import Path
import csv,json,re
from PIL import Image
from spine36 import decode
ROOT=Path(__file__).resolve().parents[1]
SRC=Path.home()/'Downloads/Decomp files/unity/Assets/hotres/spine/hero_web'
MODELS=Path.home()/'Downloads/Decomp files/lua/data/tables/model.lua'
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
text=MODELS.read_text(encoding='utf-8-sig');models={k:name for k,name in re.findall(r'\["(\d+)"\]\s*=\s*\{\s*\d+,\s*[^,]+,\s*[^,]+,\s*"([^"]+)"',text)}
partners=json.loads((ROOT/'data/partner.json').read_text());skeletons={x.stem.replace('.skel',''):x for x in SRC.with_name('hero').rglob('*.skel.bytes')}
skeletons.update({x.stem.replace('.skel',''):x for x in SRC.rglob('*.skel.bytes')})
out=ROOT/'web/assets/chibis';out.mkdir(exist_ok=True);catalog={};fail=[];done={x.name for x in out.iterdir() if x.is_dir() and (x/'model.atlas').exists()}
for tid,row in partners.items():
 name=models.get(str(row['partner_model']));src=skeletons.get(name)
 if not src:fail.append((tid,name,'skeleton missing'));continue
 try:
  folder=out/name
  if name not in done:
   j=decode(src.read_bytes());folder.mkdir(exist_ok=True)
   (folder/'model.json').write_text(json.dumps(j,separators=(',',':')))
   atlas=src.with_name(name+'.atlas.txt').read_text()
   for page in re.findall(r'^([^\r\n]+\.png)\r?$',atlas,re.M):
    rgb=src.parent/(Path(page).stem+'_RGB.png');alpha=src.parent/(Path(page).stem+'_Alpha.png')
    image=Image.open(rgb).convert('RGBA');image.putalpha(Image.open(alpha).convert('RGB').getchannel('R'));image.save(folder/page)
   (folder/'model.atlas').write_text(atlas)
   done.add(name)
  catalog[tid]={'model':name,'animations':list(json.loads((folder/'model.json').read_text())['animations']),'group':int(row['group'])}
 except Exception as e:fail.append((tid,name,str(e)))
(out/'catalog.json').write_text(json.dumps(catalog,separators=(',',':')))
(ROOT/'data/chibi-import.json').write_text(json.dumps({'mapped':len(catalog),'models':len(done),'missing':fail},indent=2))
ui=ROOT/'web/assets/original-ui';ui.mkdir(exist_ok=True)
for name in ['new_battle_speed1','new_battle_speed2','new_battle_speed4','battle_img_skip2','battle_speed1','battle_speed2','battle_speed4','battle_img_skip','battle_hp_bar1','battle_hp_bar2','battle_hp_bar_bg','battle_hp_bar_group','battle_hp_bar_bg_new']:
 if (CUT/(name+'.png')).exists(): (ui/(name+'.png')).write_bytes((CUT/(name+'.png')).read_bytes())
print('Mapped',len(catalog),'models',len(done),'missing',len(fail));print(fail[:8])
