"""Recover original campaign entrance sprites and Spine idle loot effect."""
import json,shutil
from pathlib import Path
from spine36 import decode
ROOT=Path(__file__).resolve().parents[1]
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
def main():
 target=ROOT/'web/assets/campaign'
 for name in ['dog_mini_game_enter_btn','campaign_award_icon1','campaign_award_icon2']:
  shutil.copyfile(CUT/(name+'.png'),target/(name+'.png'))
 source=Path.home()/'Downloads/Decomp files/unity/Assets/hotres/spine/campaign_web/guajijiemian'
 dest=target/'loot';dest.mkdir(exist_ok=True)
 data=decode((source/'guajijiemian.skel.bytes').read_bytes())
 (dest/'model.json').write_text(json.dumps(data,separators=(',',':')))
 shutil.copyfile(source/'guajijiemian.atlas.txt',dest/'model.atlas')
 from PIL import Image
 image=Image.open(source/'guajijiemian_RGB.png').convert('RGBA')
 image.putalpha(Image.open(source/'guajijiemian_Alpha.png').convert('RGB').getchannel('R'))
 image.save(dest/'guajijiemian.png')
if __name__=='__main__':main()
