"""Recover original NewbieCamp objectives and boards from audited table exports."""
import json,hashlib,shutil
from pathlib import Path
from extract_growth_diary import rows
ROOT=Path(__file__).resolve().parents[1]
def main():
 tasks=rows('beginner_quest');boards=rows('beginner_quest_board')
 source=ROOT/'data/recovered/texts/en_en/beginner_quest_text_en_en.json'
 text={str(r[0]):r[1] for r in json.loads(source.read_text())['rows']}
 for i,r in tasks.items():r['text']=text[i]
 for i,b in boards.items():
  b['missions']=sorted([int(k) for k,r in tasks.items() if str(r['phase_id'])==i and not r['is_hide']],key=lambda k:tasks[str(k)]['rank'])
  hidden=[int(k) for k,r in tasks.items() if str(r['phase_id'])==i and r['is_hide']]
  assert len(hidden)==1;b['bonus_id']=hidden[0]
  assert tasks[str(hidden[0])]['award']==b['award'] and tasks[str(hidden[0])]['complete_value']==len(b['missions'])
 assert len(tasks)==33 and [len(b['missions']) for b in boards.values()]==[10,11,9]
 target=ROOT/'web/assets/newbie-camp';target.mkdir(parents=True,exist_ok=True)
 cut=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
 for name in ('newbie_camp_icon','newbie_camp_icon1_0','newbie_camp_icon2_0','newbie_camp_icon3_0'):
  p=cut/(name+'.png')
  if p.exists():shutil.copyfile(p,target/p.name)
 sources=[source,ROOT/'data/recovered/tables/beginner_quest.json',ROOT/'data/recovered/tables/beginner_quest_board.json']
 (ROOT/'data/newbie_camp.json').write_text(json.dumps({'tasks':tasks,'boards':boards,'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},ensure_ascii=False,indent=1)+'\n')
 print('33 tasks; 3 phases; original rewards verified')
if __name__=='__main__':main()
