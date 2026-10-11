"""Recover original ImgGuideWindow compositions, localization and cut atlas sprites."""
import json,re,shutil,hashlib
from pathlib import Path
from extract_growth_diary import rows,ROOT
SRC=Path.home()/'Downloads/Decomp files/unity/Assets/hotres/prefabs/components'
CUT=Path.home()/'Downloads/Decompiled/Sprites (atlases, cut)'
def extract():
    target=ROOT/'web/assets/img-guides';target.mkdir(parents=True,exist_ok=True)
    texts={r[0]:r[1] for r in json.loads((ROOT/'data/recovered/texts/en_en/translation_en_en.json').read_text())['rows']}
    guides={};sources={};missing=[]
    def sprite(name):
        name=name.removesuffix('_png');p=CUT/(name+'.png')
        if not p.exists():missing.append(name);return None
        shutil.copyfile(p,target/p.name);sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return '/assets/img-guides/'+p.name
    bg=sprite('img_guide_bg')
    for key,g in rows('img_guide').items():
        pages=[];li=ii=0
        for page,(lc,ic) in enumerate(zip(map(int,str(g['label_number']).split('|')),map(int,str(g['icon_number']).split('|'))),1):
            path=SRC/f"img_guide_{g['skin_name'].lower()}{page}_en_en.prefab"
            if not path.exists():
                nodes=[]
                for n in range(1,ic+1):
                    src=sprite(f"img_guide_{g['prename']}_icon{ii+n}_en_en")
                    if src:nodes.append({'src':src,'flow':True})
                for n in range(1,lc+1):nodes.append({'text':texts.get('IMG_GUIDE_'+g['label_name']+str(li+n),''),'flow':True})
                pages.append({'width':656,'height':962,'background':bg,'nodes':nodes,'layout':'recovered-content'});li+=lc;ii+=ic;continue
            raw=path.read_text();sources[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
            parts=re.split(r'\n--- !u!(\d+) &(\d+)',raw);objs={parts[i+1]:(parts[i],parts[i+2]) for i in range(1,len(parts),3)}
            names={fid:re.search(r'm_Name: (.*)',b)[1] for fid,(c,b) in objs.items() if c=='1'};tr={};bygo={};widgets={}
            def val(b,k,default=0):
                m=re.search(r'^  '+k+r': (.*)$',b,re.M);return m[1] if m else default
            for fid,(c,b) in objs.items():
                go=re.search(r'm_GameObject: \{fileID: (\d+)',b)
                if not go:continue
                go=go[1]
                if c in ('4','224'):
                    pos=re.search(r'm_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+)',b);sc=re.search(r'm_LocalScale: \{x: ([-\d.e]+), y: ([-\d.e]+)',b);pa=re.search(r'm_Father: \{fileID: (\d+)',b)
                    if pos and sc and pa:tr[fid]=(float(pos[1]),float(pos[2]),float(sc[1]),float(sc[2]),pa[1]);bygo[go]=fid
                elif c=='114' and 'mWidth:' in b:widgets[go]=b
            def world(fid):
                if fid not in tr:return 0,0,1,1
                x,y,sx,sy,pa=tr[fid];px,py,psx,psy=world(pa);return px+x*psx,py+y*psy,sx*psx,sy*psy
            # Some prefabs embed a stale copy of another guide (img_guide_prophet2 carries an img_guide_arena2_zh_tw branch):
            # skip every widget under a nested GameObject named img_guide_* that is not the prefab's own root.
            fidname={f:names.get(g_,'') for g_,f in bygo.items()}
            def foreign(fid,seen=0):
                while fid in tr and seen<64:
                    nm=fidname.get(fid,'')
                    if nm.startswith('img_guide_') and nm!=path.stem:return True
                    fid=tr[fid][4];seen+=1
                return False
            nodes=[]
            for go,b in widgets.items():
                if foreign(bygo.get(go,'')):continue
                name=names.get(go,'');sn=val(b,'mSpriteName','');text=val(b,'mText','');font=float(val(b,'mFontSize',20));x,y,sx,sy=world(bygo.get(go,''));w=float(val(b,'mWidth',0))*sx;h=float(val(b,'mHeight',0))*sy
                if re.fullmatch(r'label\d+',name):text=texts.get('IMG_GUIDE_'+g['label_name']+str(li+int(name[5:])),'')
                if re.fullmatch(r'icon\d+',name):sn=f"img_guide_{g['prename']}_icon{ii+int(name[4:])}_en_en"
                if not sn and not text:continue
                if text and w<40:
                    parent=tr.get(bygo.get(go,''),(0,0,1,1,''))[4];parentgo=next((k for k,v in bygo.items() if v==parent),None);pb=widgets.get(parentgo,'');w=float(val(pb,'mWidth',max(300,w)));h=max(h,float(val(pb,'mHeight',h)))
                # NGUI pivot enum: TopLeft, Top, TopRight, Left, Center, Right, BottomLeft, Bottom, BottomRight.
                pivot=int(val(b,'mPivot',4));ax=(pivot%3)/2;ay=(pivot//3)/2
                n={'x':328+x-w*ax,'y':481-y-h*(1-ay),'w':w,'h':h,'z':int(val(b,'mDepth',0))}
                if sn:n['src']=sprite(sn)
                else:n.update(text=text,font=font*sy)
                if n.get('src') or n.get('text'):nodes.append(n)
            pages.append({'width':656,'height':962,'background':bg,'nodes':nodes});li+=lc;ii+=ic
        guides[key]={'name':g['skin_name'],'pages':pages}
    print('Missing sprites:',sorted(set(missing)))
    result={'guides':guides,'sources':sources};(target/'catalog.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    print(len(guides),'guides',sum(len(g['pages']) for g in guides.values()),'pages',len(list(target.glob('*.png'))),'sprites')
if __name__=='__main__':extract()
