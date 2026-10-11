"""Original HeadView buff icons and English labels, recovered sources read only."""
import json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
t=json.loads((root/'data/recovered/tables/buff.json').read_text())
texts=json.loads((root/'data/recovered/texts/en_en/buff_text_en_en.json').read_text())
names={r[0]:r[1] for r in texts['rows']}
cut=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
out=root/'web/assets/spine/status-icons';out.mkdir(parents=True,exist_ok=True)
rows={}
for name,values in t['rows'].items():
 row={k:values[i-1] for k,i in t['keys'].items() if i<=len(values)}
 icons=[]
 for k in ('icon1','icon2'):
  icon=str(row.get(k) or '');src=cut/(icon+'.png')
  if icon and src.is_file():shutil.copy2(src,out/src.name);icons.append(icon)
  else:icons.append('')
 if any(icons):rows[name]={'label':names.get(name) or name,'positive':icons[0],'negative':icons[1] or icons[0]}
(root/'web/assets/spine/battle-status.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
print(len(rows),'states;',len(list(out.glob('*.png'))),'original icons')
