"""Standalone asset/manifest QA checks, no game runtime imports."""
from pathlib import Path
import base64,json
root=Path(__file__).resolve().parent
m=json.loads((root/'fx.json').read_text())
assert m['quality_profiles']['desktop']['steps']==list(range(7))
assert m['quality_profiles']['mobile']['steps']==list(range(7))
assert m['quality_profiles']['desktop']['atlas_resources']==m['quality_profiles']['mobile']['atlas_resources']
assert len(m['sequence'])==7
assert sum(x['res']=='lianhua_hurt02' for x in m['sequence'])==2
assert m['skill_hit_event_ms']==1120
d=json.loads((root/'model.json').read_text())
assert d['skeleton']['spine']=='3.6.37'
assert len(d['slots'])==8
assert len(d['bones'])>=10
assert all(n in {x['name'] for x in d['bones']} for n in ('torso','right_arm','staff','hair_back','skirt_left','staff_tip'))
assert d['animations']['skill']['events'][0]['time']==1.12
assert 'hit' in d['events']
a=json.loads((root/'images.b64.json').read_text())
assert len(a)==8
for n,data in a.items():
 assert n.endswith('.webp'),n
 assert len(base64.b64decode(data))>500
print('PASS QA contract: 7/7 PC/Mobile FX, 8 split parts, hit 1.12s, Spine 3.6.37')
