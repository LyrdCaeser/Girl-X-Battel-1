"""LOCAL-072: elective low-star Graduate progression, preserving identity/skills."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=json.loads((ROOT/'web/assets/girls-catalog.json').read_text())
BASE={int(r['id']):int(r['stars']) for r in CATALOG if int(r['stars'])<=3}
GROUP={int(r['id']):int(r['group']) for r in CATALOG if int(r['id']) in BASE}
CAPS={1:40,2:60,3:80,4:100,5:140,6:180,7:200,8:220,9:240,10:250}

def recipes():
    out={}
    for tid,base in BASE.items():
        for star in range(base+1,11):
            # One untouched namesake copy plus same-star faction food.
            # Exact namesake checked separately to prevent feeding an upgraded copy.
            food=0 if star<=3 else 1 if star<=5 else 2
            out[f'{tid}:{star}']={'kind':'awake','local':True,'source':tid,'target':tid,'star':star,
              'group':GROUP[tid],'material':[tid]+[(star-1)*10000+GROUP[tid]*1000+999]*food,
              'cost':{'1':10000*(star-1)**2},'base_star':base}
    return out
RECIPES=recipes()

def recipe(partner):
    tid=int(partner['table_id']);star=BASE.get(tid,0)+int(partner.get('awake',0))
    return RECIPES.get(f'{tid}:{star+1}') if tid in BASE else None

def combat_partner(partner):
    if partner.get('isMonster') or int(partner['table_id']) not in BASE:return partner
    advance=int(partner.get('awake',0))
    if not advance:return partner
    # Native HeroAttr has no awake tables for these girls. Keep native skills and
    # calculate a documented local attribute multiplier in the runtime adapter.
    return {**partner,'awake':0,'local_growth':advance}
