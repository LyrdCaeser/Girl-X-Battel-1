"""House / Senpai dress original data and assets; archives remain read-only."""
from pathlib import Path
import json,re,hashlib,shutil
from PIL import Image
from extract_acquisition import ROOT,SOURCE,CUT,read_table
from spine36 import decode

def spine(src,out):
 skel=next(src.glob("*.skel.bytes"));name=skel.name[:-len(".skel.bytes")]
 out.mkdir(parents=True,exist_ok=True)
 if (out/"model.atlas").exists():return name
 (out/"model.json").write_text(json.dumps(decode(skel.read_bytes()),separators=(",",":")))
 atlas=(src/(name+".atlas.txt")).read_text()
 for page in re.findall(r"^([^\r\n]+\.png)\r?$",atlas,re.M):
  stem=Path(page).stem;im=Image.open(src/(stem+"_RGB.png")).convert("RGBA");im.putalpha(Image.open(src/(stem+"_Alpha.png")).convert("RGB").getchannel("R"));im.save(out/page)
 (out/"model.atlas").write_text(atlas)
 return name

def main():
 out=ROOT/'web/assets/original-ui/house-dress';out.mkdir(parents=True,exist_ok=True)
 tables=['house_furniture','house_furniture_group','house_furniture_unit','house_floor','shop_house_furniture','house_award','senpai_dress','senpai_dress_style','senpai_dress_item','senpai_dress_group','senpai_dress_slot','summon_dress','en_en/item_text_en_en','en_en/house_furniture_group_text_en_en','en_en/senpai_dress_group_text_en_en']
 d={n:read_table(n) for n in tables};sources={};missing=[]
 def track(p):sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 for n in tables:track(SOURCE/f'lua/data/tables/{n}.lua')
 raw=(SOURCE/'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig');track(SOURCE/'lua/data/tables/misc.lua')
 d['misc']={name:json.loads(value) for name,value in re.findall(r'\n\t(\w+) = \{\s*"\w+",\s*("[^\n]+")',raw) if name.startswith(('house_','dorm_','dress_gacha'))}
 for n in ['models/House','models/Dress','models/Summon','windows/HouseWindow','windows/HouseMap','windows/HouseGrid','windows/HouseItem','windows/DressMainWindow','windows/DressSummonWindow','components/SenpaiModel']:
  track(SOURCE/f'lua/app/{n}.lua')
 track(SOURCE/'unity/Assets/hotres/prefabs/windows/house_window.prefab')
 names=set()
 for r in d['house_furniture'].values():
  r['label']=d['en_en/item_text_en_en'].get(str(r['id']),{}).get('name',str(r['id']))
  for key in ['img','flip_img','collection_img','interact_img']:
   for n in str(r[key]).split('|'):
    if n and n!='-1':names.add(n);names.update([n+'_1',n+'_2',n+'_3'])
 for r in d['senpai_dress_style'].values():
  names.update([str(r['image']),'icon_'+str(r['image'])])
  if r['pos'] in [4,5]:names.add(str(r['resource']))
 for r in d['senpai_dress_item'].values():
  names.update(str(r['icon']).split('|'));r['label']=d['en_en/item_text_en_en'].get(str(r['id']),{}).get('name',str(r['id']))
 names.update(p.stem for p in CUT.glob('house_*.png'));names.update(p.stem for p in CUT.glob('dress_*.png') if 'logo' not in p.stem or 'en_en' in p.stem)
 names.update(['icon_1','icon_2','icon_69','icon_258','blue_btn_54_54','yellow_btn_54_54','win_back_btn','close_btn_2','help_2','dress_summon_logo_en_en','dress_main_tab_1_en_en','dress_main_tab_2_en_en'])
 sizes={}
 for n in sorted(names):
  p=CUT/(n+'.png')
  if p.exists():shutil.copy2(p,out/p.name);track(p);sizes[n]=list(Image.open(p).size)
 for r in d['senpai_dress_style'].values():
  if r['pos'] not in [4,5]:continue
  n=str(r['resource']);p=SOURCE/'unity/Assets/hotres/textures/senpai_slot_web'/(n+'.png')
  if p.exists():shutil.copy2(p,out/p.name);track(p);sizes[n]=list(Image.open(p).size)
 for n in names:
  if n in sizes:continue
  p=SOURCE/'unity/Assets/hotres/textures/scenes_web'/(n+'.png')
  if p.exists():shutil.copy2(p,out/p.name);track(p);sizes[n]=list(Image.open(p).size)
 d['sizes']=sizes
 for n,p in [('dress_main_bg',SOURCE/'unity/Assets/hotres/textures/scenes_big_web/dress_main_bg.png'),('dress_summon_normal_bg',SOURCE/'unity/Assets/hotres/textures/activity_web/dress_summon/dress_summon_normal_bg.png')]:
  if p.exists():shutil.copy2(p,out/(n+'.png'));track(p)
 resources={};separators={};spines=SOURCE/'unity/Assets/hotres/spine/senpai_dress_web'
 found={p.name:p for p in spines.rglob('*.skel.bytes')}
 for r in d['senpai_dress_style'].values():
  n=str(r['resource'])
  if r['pos'] not in [1,2,3] or not n or n in resources:continue
  p=found.get(n+'.skel.bytes')
  if not p:missing.append(n);continue
  try:
   spine(p.parent,out/'models'/n);resources[n]=n
   prefab=next(p.parent.glob('*.prefab'),None)
   if prefab:
    raw=prefab.read_text();match=re.search(r'separatorSlotNames:\s*\n((?:  - [^\n]+\n)+)',raw)
    separators[n]=re.findall(r'  - ([^\r\n]+)',match.group(1)) if match else []
   for s in p.parent.iterdir():
    if s.is_file() and not s.name.endswith('.meta'):track(s)
  except (ValueError,StopIteration,OSError) as e:missing.append(n+': '+str(e))
 d['separators']=separators;d['models']=resources;d['missing_models']=missing;d['sources']=sources
 d['dropbox']={k:r for k,r in json.loads((ROOT/'data/dropbox.json').read_text()).items() if int(r['dropbox_id']) in [50001,50002,50003,50004,50005]}
 (ROOT/'data/house_dress.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 (out/'catalog.json').write_text(json.dumps({k:v for k,v in d.items() if k not in ['sources','en_en/item_text_en_en']},ensure_ascii=False)+'\n')
 print('Furniture',len(d['house_furniture']),'dress styles',len(d['senpai_dress_style']),'assets',len(sizes),'models',len(resources),'missing models',len(missing))
if __name__=='__main__':main()
