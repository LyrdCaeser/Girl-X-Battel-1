"""Recover original Slot dealer Spines without changing the archived Unity assets."""
import hashlib,json,re
from pathlib import Path
from PIL import Image
from spine36 import decode
ROOT=Path(__file__).resolve().parents[1]
HOT=Path.home()/'Downloads/Decomp files/unity/Assets/hotres'
WEB=ROOT/'web/assets'

def spine(src,out):
    # Same format recovery as extract_visuals.spine; no imports of asset generators.
    skel=next(src.glob('*.skel.bytes'));name=skel.name[:-len('.skel.bytes')]
    out.mkdir(parents=True,exist_ok=True)
    (out/'model.json').write_text(json.dumps(decode(skel.read_bytes()),separators=(',',':')))
    atlas=(src/(name+'.atlas.txt')).read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$',atlas,re.M):
        stem=Path(page).stem
        image=Image.open(src/(stem+'_RGB.png')).convert('RGBA')
        image.putalpha(Image.open(src/(stem+'_Alpha.png')).convert('RGB').getchannel('R'))
        image.save(out/page)
    (out/'model.atlas').write_text(atlas)

def main():
    result={}
    for name in ('gamble_girl','gamble_up_girl'):
        source=HOT/'spine/gamble_web'/name
        output=WEB/'spine'/name
        spine(source,output)
        model=json.loads((output/'model.json').read_text())
        result[name]={'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.iterdir()) if p.suffix in ('.bytes','.txt','.png')},'animations':list(model['animations']), 'outputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}}
    dest=ROOT/'validation/slots-lucky-2026-09-29/dealers.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({name:row['animations'] for name,row in result.items()})

if __name__=='__main__':main()

# GambleWindow chrome (nav tabs, the grey locked High Stakes tab with awake_lock, probability / help round buttons, the
# ticket icons of the top bar) — WAVE-045
import shutil as _sh
_CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
for _n in ('nav_btn_blue_left', 'nav_btn_blue_right', 'nav_btn_white_left', 'nav_btn_white_right', 'nav_btn_grey_right', 'check_white_btn', 'help_2', 'awake_lock', 'icon_35', 'icon_29', 'icon_6'):
    _sh.copy2(_CUT / f'{_n}.png', ROOT / 'web/assets/slots' / f'{_n}.png')
