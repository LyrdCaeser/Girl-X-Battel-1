"""Read-only recovery of Firework Project 196 (ActivityBomb, not Firework 274)."""
import hashlib, json, re, shutil
from tools.extract_acquisition import ROOT, SOURCE, CUT, read_table

def main():
    names=['activity_bomb_make','activity_bomb_award']
    result={n:read_table(n) for n in names}
    misc=(SOURCE/'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig')
    result['cost']=re.search(r'activity_bomb_make_cost = \{\s*"activity_bomb_make_cost",\s*"([^"]+)"',misc).group(1)
    result['level_step']=int(re.search(r'activity_bomb_make_lv = \{\s*"activity_bomb_make_lv",\s*"([^"]+)"',misc).group(1))
    paths=[SOURCE/f'lua/data/tables/{n}.lua' for n in names]+[SOURCE/'lua/data/tables/misc.lua',SOURCE/'lua/app/windows/ActivityBombGachaWindow.lua',SOURCE/'lua/app/windows/activity/ActivityBomb.lua']
    out=ROOT/'web/assets/firework-project';out.mkdir(parents=True,exist_ok=True)
    for p in CUT.glob('activity_bomb*.png'):
        shutil.copyfile(p,out/p.name);paths.append(p)
    for p in (SOURCE/'unity/Assets/hotres/textures/scenes_web').glob('activity_bomb*.png'):
        shutil.copyfile(p,out/p.name);paths.append(p)
    result['sources']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (ROOT/'data/firework_project.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(len(result[names[0]]),'outcomes;',len(result[names[1]]),'shop rewards')
if __name__=='__main__':main()
