"""Original GuildTerritoryWindow scenery sprites; references are read-only."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/'Downloads/Decomp files'
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
def main():
    out=ROOT/'web/assets/original-ui/guild-territory';out.mkdir(parents=True,exist_ok=True);sources={}
    for i in [1,3,4,5,6]:
        p=CUT/f'guild_territory_icon0{i}_mask.png';shutil.copy2(p,out/p.name);sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    for rel in ['lua/app/windows/GuildTerritoryWindow.lua','unity/Assets/hotres/prefabs/windows/guild_territory_window.prefab']:
        p=SOURCE/rel;sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    for p in [CUT/'guild_territory_icon02.png',ROOT/'web/assets/chibis/yuanshu/model.json']:
        sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    target=ROOT/'validation/guild-ui-2026-09-29';target.mkdir(parents=True,exist_ok=True)
    (target/'sources.json').write_text(json.dumps(sources,indent=2))
    print('5 original buildings; fountain/merchant reused; sources hashed')
if __name__=='__main__':main()
