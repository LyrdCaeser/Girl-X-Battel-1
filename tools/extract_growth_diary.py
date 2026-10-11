"""Normalize recovered Growth Diary tables, English text and original assets."""
import json, hashlib, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'data/recovered'
def rows(name):
    d=json.loads((REC/'tables'/f'{name}.json').read_text())
    return {rid:{k:r[i-1] for k,i in d['keys'].items() if i<=len(r)} for rid,r in d['rows'].items()}
def main():
    missions=rows('growth_diary_mission'); ways=rows('getway')
    texts=json.loads((REC/'texts/en_en/growth_diary_mission_text_en_en.json').read_text())
    descriptions={str(r[0]):r[1] for r in texts['rows']}
    translation=json.loads((REC/'texts/en_en/translation_en_en.json').read_text())
    text={r[0]:r[1] for r in translation['rows'] if str(r[0]).startswith('GROWTH_DIARY_')}
    chapters={}
    for rid,r in missions.items():
        r['text']=descriptions[rid];r['window']=ways[str(r['getway'])]['go_window']
        chapter=chapters.setdefault(str(r['chapter_id']),{'missions':[],'award':r['chapter_awards']})
        assert chapter['award']==r['chapter_awards']
        chapter['missions'].append(int(rid))
    assert len(missions)==160 and len(chapters)==40 and all(len(c['missions'])==4 for c in chapters.values())
    for c in chapters.values():c['missions'].sort()
    target=ROOT/'web/assets/growth-diary';target.mkdir(parents=True,exist_ok=True)
    cut=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
    names=['growth_diary_icon_h5','growth_diary_icon','growth_dairy_star','growth_dairy_line2','growth_dairy_bg2','growth_dairy_progress','growth_dairy_line','mission_awarded_en_en']
    hashes={}
    for n in names:
        p=cut/f'{n}.png'
        if p.exists():shutil.copyfile(p,target/p.name);hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    bg=Path.home()/'Downloads/Decomp files/unity/Assets/hotres/textures/scenes_web/growth_dairy_bg.png'
    if bg.exists():shutil.copyfile(bg,target/bg.name);hashes[str(bg)]=hashlib.sha256(bg.read_bytes()).hexdigest()
    for p in [REC/'tables/growth_diary_mission.json',REC/'tables/getway.json',REC/'texts/en_en/growth_diary_mission_text_en_en.json']:
        hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    (ROOT/'data/growth_diary.json').write_text(json.dumps({'missions':missions,'chapters':chapters,'text':text,'sources':hashes},ensure_ascii=False,indent=1)+'\n')
    print(len(missions),'missions,',len(chapters),'chapters,',len(list(target.glob('*.png'))),'assets')
if __name__=='__main__':main()
