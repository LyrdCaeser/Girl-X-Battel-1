"""Normalize original Friend Boss (current variant), Training, Ulticore and Practical Work."""
import json,hashlib,shutil
from pathlib import Path
from extract_growth_diary import rows
ROOT=Path(__file__).resolve().parents[1]
def main():
 names=['friend_boss_new','friend_boss_help_award','pet_training','pet_training_boss','pet_training_lesson','pet_training_new_awards','pet_exskill','pet','activity_boss']
 data={n:rows(n) for n in names};misc=rows('misc')
 data['misc']={r['key']:r['value'] for r in misc.values() if any(str(r['key']).startswith(x) for x in ['friend_','pet_training_','pet_exlevel_','pet_exskill_','activity_boss_'])}
 data['text']={r[0]:r[1] for r in json.loads((ROOT/'data/recovered/texts/en_en/translation_en_en.json').read_text())['rows'] if str(r[0]) in ['FRIEND_ASSISTANT_HELP','PET_TRAINING_HELP','ACTIVITY_WORLD_BOSS_HELP']}
 data['sources']={n:hashlib.sha256((ROOT/f'data/recovered/tables/{n}.json').read_bytes()).hexdigest() for n in names+['misc']}
 (ROOT/'data/remaining_systems.json').write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n')
 target=ROOT/'web/assets/remaining-systems';target.mkdir(parents=True,exist_ok=True)
 cut=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
 for name in ['friend_team_boss_head1','friend_team_boss_head2','pet_training_boss_1','pet_training_icon','icon_216','icon_245','activity_world_boss_bg01','activity_world_boss_bg02','activity_world_boss_bg03']:
  p=cut/(name+'.png')
  if p.exists():shutil.copyfile(p,target/p.name)
 print({n:len(data[n]) for n in names})
if __name__=='__main__':main()
