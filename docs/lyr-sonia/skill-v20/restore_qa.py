"""Restore a standalone visual QA preview. Does not register heroes or edit production."""
from pathlib import Path
import base64,json,shutil,sys
root=Path(__file__).resolve().parent
target=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/tmp/lyr_sonia_skill_v20_rebuilt_qa')
if target.exists():raise SystemExit('Destination exists: '+str(target))
(target/'assets'/'sonia').mkdir(parents=True)
for name in ('index.html','skill-qa.js','fx.json'):shutil.copy2(root/name,target/name)
shutil.copy2(root/'model.json',target/'assets'/'sonia'/'model.json')
(target/'assets'/'sonia'/'model.atlas').write_text((root/'model.atlas.txt').read_text())
for name,encoded in json.loads((root/'images.b64.json').read_text()).items():
 if name.startswith('sonia_') and name.endswith('.webp'):
  (target/'assets'/'sonia'/name).write_bytes(base64.b64decode(encoded))
vendor=Path('/opt/gxb3/web/vendor');fx=Path('/opt/gxb3/web/assets/battle-fx');chibi=Path('/opt/gxb3/web/assets/chibis')
for link,source in ((target/'vendor',vendor),(target/'assets'/'battle-fx',fx),(target/'assets'/'chibis',chibi)):
 if not source.exists():raise SystemExit('Missing game asset '+str(source))
 link.symlink_to(source,target_is_directory=True)
mobile=Path('/tmp/lyr_sonia_fullskill_qa_v03/mobile-battle-fx')
(target/'mobile-battle-fx').symlink_to(mobile if mobile.exists() else fx,target_is_directory=True)
print('Restored QA files to',target)
print('Launch with: python3 -m http.server 18889 --bind 127.0.0.1 --directory '+str(target))
