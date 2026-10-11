"""HeroIcon:initEffect original frames and rank 10+ Spine effects; sources read only."""
import sys,shutil,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from extract_slots_dealers import spine
ROOT=Path(__file__).resolve().parents[1]
HOT=Path.home()/'Downloads/Decomp files/unity/Assets/hotres'
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
for sub,name in [('partner_web','shiziui_touxiang'),('group_tianyi','shiziui_touxiang_tianyi')]:
    spine(HOT/'spine'/sub/name,ROOT/'web/assets/spine'/name)
    m=json.loads((ROOT/'web/assets/spine'/name/'model.json').read_text());print(name,list(m['animations']))
for name in ['hero_frame2','hero_frame3']:
    shutil.copy2(CUT/(name+'.png'),ROOT/'web/assets/summon-result'/(name+'.png'))
from extract_growth_diary import rows
frames={k:v['avatar_frame_effect'] for k,v in rows('item').items() if v.get('avatar_frame_effect')}
(ROOT/'web/assets/spine/frame-effects.json').write_text(json.dumps(frames,separators=(',',':')))
index={p.parent.name:p.parent for p in (HOT/'spine').rglob('*.skel.bytes')}
for name in sorted(set(frames.values())):
    if name in index:
        out=ROOT/'web/assets/spine'/name
        try: spine(index[name],out)
        except FileNotFoundError:
            atlas=(index[name]/(name+'.atlas.txt')).read_text()
            for page in re.findall(r'^([^\r\n]+\.png)\r?$',atlas,re.M):
                shutil.copy2(index[name]/page,out/page)
            (out/'model.atlas').write_text(atlas)
        print('profile',name)
