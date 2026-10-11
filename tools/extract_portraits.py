"""Preserve exact partner.avatar icons from archived cut sprites; no generator imports."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'

def main():
    partner=json.loads((ROOT/'data/partner.json').read_text())
    catalog=json.loads((ROOT/'web/assets/girls-catalog.json').read_text())
    manifest_path=ROOT/'web/assets/avatars.json'
    # Preserve legacy atlas coordinates for compatibility with earlier bundles.
    legacy=json.loads(manifest_path.read_text())
    manifest={k:{field:value for field,value in row.items() if field!='src'} for k,row in legacy.items() if 'x' in row}
    out=ROOT/'web/assets/original-ui/portraits';out.mkdir(parents=True,exist_ok=True)
    sources={};missing=[]
    for tid,row in partner.items():
        manifest.setdefault(tid,{}).update(stars=int(row.get('max_star') or 1),group=int(row.get('group') or 0))
        name=row.get('avatar') or '';source=CUT/(name+'.png')
        if not name or not source.is_file():
            missing.append({'id':int(tid),'avatar':name});continue
        shutil.copyfile(source,out/source.name)
        manifest.setdefault(tid,{})['src']='/assets/original-ui/portraits/'+source.name
        sources[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()
    visible_missing=[row['id'] for row in catalog if not manifest.get(str(row['id']),{}).get('src')]
    if visible_missing:raise ValueError('Missing visible original icons: '+str(visible_missing))
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    report={'table_source_sha256':hashlib.sha256((ROOT/'data/partner.json').read_bytes()).hexdigest(),'original_sources':sources,'mapped_partner_ids':sum('src' in r for r in manifest.values()),'visible_catalog':len(catalog),'visible_missing':visible_missing,'nonvisible_missing':missing,'legacy_ids':sum('x' in r for r in manifest.values()),'outputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.png'))}}
    log=ROOT/'validation/portraits-2026-09-29';log.mkdir(parents=True,exist_ok=True)
    (log/'assets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print({k:report[k] for k in ('mapped_partner_ids','visible_catalog','visible_missing','legacy_ids')},'original images',len(sources))
if __name__=='__main__':main()
