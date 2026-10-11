"""Campaign fight flow (BattleController / BattleLoadingWindow / StoryWindow; user captures 2026-09-30):
- the loading pictures custom_background 4-13 (battle_loading_1..10) with their text art battle_loading_N_en_en (N = id - 3,
  shown on pictures 2-10) and BATTLE_LOADING_N / _CV_N texts;
- the story→battle sweep, Spine `switch` (xyd.Battle.effect_switch, texiao01).
Output web/assets/battle-loading/ (+ loading.json) and web/assets/spine/switch/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode
SPR = Path.home() / 'Downloads/Decompiled'
DEC = Path.home() / 'Downloads/Decomp files'
OUT = ROOT / 'web/assets/battle-loading'; OUT.mkdir(parents=True, exist_ok=True)
for n in range(1, 11):
    tex = DEC / 'unity/Assets/hotres/textures'
    pic = next(p for p in (tex / f'scenes_web/battle_loading_{n}.png', tex / f'local_tex/battle_loading_{n}.png') if p.exists())
    Image.open(pic).convert('RGB').save(OUT / f'battle_loading_{n}.webp', 'WEBP', quality=84)
    t = SPR / f'Images (other)/battle_loading_text/battle_loading_{n}_en_en.png'
    if t.exists(): shutil.copy2(t, OUT / t.name)
for n in ('battle_loading_bar_bg', 'battle_loading_bar', 'scene_bottom', 'rect_bg'):
    shutil.copy2(SPR / f'Sprites (atlases, cut)/{n}.png', OUT / f'{n}.png')
# BattleLoadingWindow rectColor / labelColor / labelStrokeColor (Color.New2 = 0xRRGGBBAA), index = picture number
hexc = lambda v: '#%08x' % v if v else ''
colors = {'rect': [hexc(v) for v in (0, 3041613298, 1581402802, 2927343346, 3968878834, 2254857458, 2791801778, 1329216946, 1786220466, 3865674482)],
          'label': [hexc(v) for v in (0, 4294177791, 4126403327, 4109303295, 2976200703, 1784043007, 4143185407, 4261077759, 4093443583, 3161028863)],
          'stroke': [hexc(v) for v in (0, 3041810687, 1983655935, 1765965311, 4294967295, 4294967295, 2722194943, 2285185023, 1366273023, 4294967295)]}
db = sqlite3.connect(DEC / 'data/en_en.db')
text = dict(db.execute("select name, translation from translation_en_en where name like 'BATTLE_LOADING%' or name like 'BATTLE_TIPS_DESC%'"))
(OUT / 'loading.json').write_text(json.dumps({'pictures': list(range(1, 11)), 'text': text, 'colors': colors}, ensure_ascii=False, separators=(',', ':')))
src = SPR / 'Animation (Battle, Boss, Buff, Debuff)/~Buffs/switch'
out = ROOT / 'web/assets/spine/switch'; out.mkdir(parents=True, exist_ok=True)
(out / 'model.json').write_text(json.dumps(decode((src / 'switch.skel').read_bytes()), separators=(',', ':')))
atlas = (src / 'switch.atlas').read_text()
for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M): shutil.copy2(src / page, out / page)
(out / 'model.atlas').write_text(atlas)
print(len(list(OUT.glob('*.webp'))), 'pictures,', len(list(OUT.glob('*_en_en.png'))), 'texts; switch anims', [a for a in json.loads((out / 'model.json').read_text()).get('animations', {})])
