"""Summon reveal (SummonEffectResWindow + components/PartnerSummonEffect.lua): Spines fx_ui_gacha_revision (5★ intro,
animation "222"), fx_ui_newgirl_gaino (≥5★ reveal), fx_ui_newgirl_gainp (<5★ reveal), fx_ui_newgirl_gain_star, and the
summon_scene background. Sources read only; output web/assets/spine/<name>/ and web/assets/summon/."""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_slots_dealers import spine
ROOT = Path(__file__).resolve().parents[1]
HOT = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres'
for sub, name in (('summon', 'fx_ui_gacha_revision'), ('partner_gain', 'fx_ui_newgirl_gaino'), ('partner_gain', 'fx_ui_newgirl_gainp'), ('partner_gain', 'fx_ui_newgirl_gain_star')):
    spine(HOT / 'spine' / sub / name, ROOT / 'web/assets/spine' / name)
    m = json.loads((ROOT / 'web/assets/spine' / name / 'model.json').read_text())
    print(name, list(m['animations']), [s['name'] for s in m['slots']][:40])
OUT = ROOT / 'web/assets/summon'; OUT.mkdir(parents=True, exist_ok=True)
shutil.copy2(HOT / 'textures/local_tex/summon_scene.png', OUT / 'summon_scene.png')
# Sounds of the sequence (sound1.lua): 2147 vd_egg (swipe), 3010 gacha_obtain, 2148 vd_egg_5star (5★ intro),
# 2133 ui_gain_hero_5star_bg, 2115 ui_gain_hero_5star, 2111/2112 ui_gain_hero_left/right.
import subprocess
SND = ROOT / 'web/assets/sounds'
for name in ('vd_egg', 'gacha_obtain', 'vd_egg_5star', 'ui_gain_hero_5star_bg', 'ui_gain_hero_5star', 'ui_gain_hero_left', 'ui_gain_hero_right'):
    src, dst = HOT / f'sounds/ui_sound/{name}.ogg', SND / f'{name}.mp3'
    if src.exists() and not dst.exists():
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(src), '-b:a', '128k', str(dst)], check=True)
print(sorted(p.name for p in SND.glob('*gain*')) + sorted(p.name for p in SND.glob('vd_egg*')))
