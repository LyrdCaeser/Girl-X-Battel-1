"""Enroll → Exchange effects (ProphetReplace.LoadResource): fx_guanghuan (orb while choosing), fx_daiji (ring under the
model), fx_guangzhu (light pillar when a model appears), fx_saomiao (the scan that reveals the card) and fx_wenhao (the
"?" of the unknown result). Spine 3.6 binaries → web/assets/spine/<name>/model.json + atlas. Sources are read only."""
import json, re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode
SRC = Path.home() / 'Downloads/Decompiled/Animation (Misc)/Misc/prophet/replace'
for n in ('fx_guanghuan', 'fx_daiji', 'fx_guangzhu', 'fx_saomiao', 'fx_wenhao'):
    out = ROOT / 'web/assets/spine' / n; out.mkdir(parents=True, exist_ok=True)
    data = decode((SRC / n / f'{n}.skel').read_bytes())
    (out / 'model.json').write_text(json.dumps(data, separators=(',', ':')))
    atlas = (SRC / n / f'{n}.atlas').read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M): shutil.copy2(SRC / n / page, out / page)
    (out / 'model.atlas').write_text(atlas)
    print(n, list((data.get('animations') or {}).keys()), data.get('skeleton', {}).get('width'), data.get('skeleton', {}).get('height'))
