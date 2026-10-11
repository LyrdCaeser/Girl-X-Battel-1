"""Export original guild tables/assets; all archived sources read-only."""
from pathlib import Path
import json,re,shutil,hashlib
from extract_acquisition import read_table,SOURCE,CUT,ROOT

def main():
    skills=read_table('guild_skill');texts=read_table('en_en/guild_skill_text_en_en')
    restore=read_table('guild_skill_restore')
    misc=(SOURCE/'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig')
    cost=json.loads(re.search(r'guild_reset_skill_cost = \{\s*"guild_reset_skill_cost",\s*("[^"]+")',misc).group(1))
    out=ROOT/'web/assets/original-ui/guild-lab';out.mkdir(parents=True,exist_ok=True)
    sources={};missing=[]
    coin=CUT/'icon_4.png';shutil.copy2(coin,out/'coin.png');sources[str(coin)]=hashlib.sha256(coin.read_bytes()).hexdigest()
    names={str(r['icon']).removesuffix('_png') for r in skills.values()}
    names.update(p.stem for p in CUT.glob('guild_skill*.png'))
    names.update(['guild_bg_flower','guild_btn_reset','help_2','close_btn_2','partner_detail_arrow','page_icon_0','page_icon_1']+['pub_job_icon'+str(j) for j in range(1,6)])
    from PIL import Image
    atlas_root=SOURCE/'unity/Assets/hotres/atlases'
    for folder,stem in [('guild_skill2_web','guild_skill_web'),('guild_skill2_web','guild_skill2_web')]:
        prefab=atlas_root/folder/(stem+'.prefab');rgb=Image.open(prefab.with_name(stem+'_RGB.png')).convert('RGB');alpha=Image.open(prefab.with_name(stem+'_Alpha.png')).convert('RGB')
        for name,x,y,w,h in re.findall(r'- name: ([^\r\n]+)\s+x: (\d+)\s+y: (\d+)\s+width: (\d+)\s+height: (\d+)',prefab.read_text()):
            if name not in names:continue
            x,y,w,h=map(int,(x,y,w,h));box=(x,y,x+w,y+h);im=rgb.crop(box);im.putalpha(alpha.crop(box).getchannel('R'));im.save(out/(name+'.png'))
        for source in [prefab,prefab.with_name(stem+'_RGB.png'),prefab.with_name(stem+'_Alpha.png')]:sources[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()
    for name in sorted(names):
        p=CUT/(name+'.png')
        if p.exists():shutil.copy2(p,out/p.name);sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        elif not (out/(name+'.png')).exists():missing.append(name)
    for name in ['guild_skill','guild_skill_restore','en_en/guild_skill_text_en_en','misc','buff']:
        p=SOURCE/f'lua/data/tables/{name}.lua';sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    for rel in ['lua/app/windows/GuildLabWindow.lua','lua/app/models/Guild.lua','lua/app/common/tables/GuildSkillTable.lua','unity/Assets/hotres/prefabs/windows/guild_lab_window.prefab']:
        p=SOURCE/rel;sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    bufftext=(SOURCE/'lua/data/tables/buff.lua').read_text(encoding='utf-8-sig');head,body=bufftext.split('table.rows =',1);keys={k:int(i) for k,i in re.findall(r'\b(\w+) = (\d+)',head)}
    buffs={}
    for name,block in re.findall(r'\n\t(\w+) = \{(.*?)\n\t\}',body,re.S):
        values=[json.loads(v.strip()) for v in block.strip().split(',\n')];buffs[name]={k:values[i-1] for k,i in keys.items() if k in ['factor','show_percent']}
    result={'buffs':buffs,'skills':skills,'text':texts,'restore':restore,'reset_cost':cost,'sources':sources,'missing_assets':missing}
    (ROOT/'data/guild_lab.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (out/'catalog.json').write_text(json.dumps({'buffs':buffs,'skills':skills,'text':texts,'reset_cost':cost,'assets':[p.stem for p in out.glob('*.png')]},ensure_ascii=False))
    print(len(skills),'skills;',len(restore),'refund rows;',len(sources),'sources; missing',missing)
if __name__=='__main__':main()
