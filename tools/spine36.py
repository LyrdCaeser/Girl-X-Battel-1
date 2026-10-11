"""Decode archived Spine 3.6 binary exports into equivalent JSON.
Format reference: EsotericSoftware/spine-runtimes, branch 3.6,
spine-csharp/src/SkeletonBinary.cs. Coordinates/timelines are preserved.
Unsupported versions or trailing bytes fail rather than silently losing data.
"""
import struct

class Reader:
    def __init__(self, data): self.data=data; self.at=0
    def take(self,n):
        b=self.data[self.at:self.at+n]; self.at+=n
        if len(b)!=n: raise ValueError('Truncated skeleton')
        return b
    def byte(self): return self.take(1)[0]
    def boolean(self): return bool(self.byte())
    def signed(self):
        v=self.byte(); return v if v<128 else v-256
    def var(self,positive=True):
        v=0
        for shift in range(0,35,7):
            b=self.byte(); v|=(b&127)<<shift
            if b<128: return v if positive else (v>>1)^-(v&1)
        raise ValueError('Invalid varint')
    def string(self):
        n=self.var(); return None if n==0 else self.take(n-1).decode('utf-8')
    def f(self): return struct.unpack('>f',self.take(4))[0]
    def color(self): return self.take(4).hex()
    def floats(self,n): return [self.f() for _ in range(n)]
    def shorts(self): return [struct.unpack('>H',self.take(2))[0] for _ in range(self.var())]
    def vertices(self,n):
        if not self.boolean(): return self.floats(n*2)
        out=[]
        for _ in range(n):
            k=self.var(); out.append(k)
            for _ in range(k): out.extend([self.var(),*self.floats(3)])
        return out
    def curve(self,frame):
        t=self.byte()
        if t==1: frame['curve']='stepped'
        elif t==2: frame['curve']=self.floats(4)
        elif t!=0: raise ValueError('Invalid curve')
    def frames(self,fields,curves=True):
        out=[]; n=self.var()
        for i in range(n):
            frame={'time':self.f()}
            for key,read in fields: frame[key]=read()
            if curves and i<n-1: self.curve(frame)
            out.append(frame)
        return out
    def attachment(self,key,essential,slots):
        name=self.string() or key; t=self.byte(); a={'name':name}
        if t==0:
            a.update(type='region',path=self.string() or name)
            for k in ('rotation','x','y','scaleX','scaleY','width','height'): a[k]=self.f()
            a['color']=self.color()
        elif t in (1,4,6):
            a['type']={1:'boundingbox',4:'path',6:'clipping'}[t]
            if t==4: a.update(closed=self.boolean(),constantSpeed=self.boolean())
            if t==6: a['end']=slots[self.var()]['name']
            n=self.var(); a.update(vertexCount=n,vertices=self.vertices(n))
            if t==4: a['lengths']=self.floats(n//3)
            if essential: a['color']=self.color()
        elif t==2:
            a.update(type='mesh',path=self.string() or name,color=self.color())
            n=self.var(); a['uvs']=self.floats(n*2); a['triangles']=self.shorts(); a['vertices']=self.vertices(n); a['hull']=self.var()
            if essential: a.update(edges=self.shorts(),width=self.f(),height=self.f())
        elif t==3:
            a.update(type='linkedmesh',path=self.string() or name,color=self.color())
            skin=self.string()
            if skin: a['skin']=skin
            a.update(parent=self.string(),deform=self.boolean())
            if essential: a.update(width=self.f(),height=self.f())
        elif t==5:
            a.update(type='point',rotation=self.f(),x=self.f(),y=self.f())
            if essential: a['color']=self.color()
        else: raise ValueError('Unknown attachment '+str(t))
        return a
    def skin(self,essential,slots):
        out={}
        for _ in range(self.var()):
            slot=slots[self.var()]['name']; items={};out[slot]=items
            for _ in range(self.var()):
                key=self.string();items[key]=self.attachment(key,essential,slots)
        return out
    def animation(self,j):
        a={}; slots={};bones={}
        for _ in range(self.var()):
            slot=j['slots'][self.var()]['name']; timelines={};slots[slot]=timelines
            for _ in range(self.var()):
                t=self.byte()
                fields={0:[('name',self.string)],1:[('color',self.color)],2:[('light',self.color),('dark',lambda:self.color()[2:])]}[t]
                timelines[{0:'attachment',1:'color',2:'twoColor'}[t]]=self.frames(fields,t!=0)
        for _ in range(self.var()):
            bone=j['bones'][self.var()]['name']; timelines={};bones[bone]=timelines
            for _ in range(self.var()):
                t=self.byte(); key=['rotate','translate','scale','shear'][t]
                timelines[key]=self.frames([('angle',self.f)] if t==0 else [('x',self.f),('y',self.f)])
        if slots:a['slots']=slots
        if bones:a['bones']=bones
        for section,fields in [('ik',[('mix',self.f),('bendPositive',lambda:self.signed()>0)]),('transform',[(k,self.f) for k in ('rotateMix','translateMix','scaleMix','shearMix')])]:
            timelines={}
            for _ in range(self.var()):
                name=j[section][self.var()]['name'];timelines[name]=self.frames(fields)
            if timelines:a[section]=timelines
        paths={}
        for _ in range(self.var()):
            name=j['path'][self.var()]['name'];timelines={};paths[name]=timelines
            for _ in range(self.var()):
                t=self.byte();key=['position','spacing','mix'][t]
                timelines[key]=self.frames([(key,self.f)] if t<2 else [('rotateMix',self.f),('translateMix',self.f)])
        if paths:a['paths']=paths
        deform={}; skin_names=list(j['skins'])
        for _ in range(self.var()):
            skin=skin_names[self.var()];ds={};deform[skin]=ds
            for _ in range(self.var()):
                slot=j['slots'][self.var()]['name'];da={};ds[slot]=da
                for _ in range(self.var()):
                    name=self.string(); frames=[];da[name]=frames;n=self.var()
                    for i in range(n):
                        f={'time':self.f()};count=self.var()
                        if count:f.update(offset=self.var(),vertices=self.floats(count))
                        if i<n-1:self.curve(f)
                        frames.append(f)
        if deform:a['deform']=deform
        draw=[]
        for _ in range(self.var()):
            f={'time':self.f(),'offsets':[]}
            for _ in range(self.var()):
                slot=j['slots'][self.var()]['name'];v=self.var();v=v if v<2**31 else v-2**32
                f['offsets'].append({'slot':slot,'offset':v})
            draw.append(f)
        if draw:a['drawOrder']=draw
        events=[];event_names=list(j['events'])
        for _ in range(self.var()):
            f={'time':self.f(),'name':event_names[self.var()],'int':self.var(False),'float':self.f()}
            f['string']=self.string() if self.boolean() else j['events'][f['name']]['string'];events.append(f)
        if events:a['events']=events
        return a

def decode(data):
    r=Reader(data); h=r.string();version=r.string()
    if not version.startswith('3.6.'): raise ValueError('Unsupported Spine '+version)
    j={'skeleton':{'hash':h,'spine':version,'width':r.f(),'height':r.f()},'bones':[],'slots':[],'ik':[],'transform':[],'path':[],'skins':{},'events':{},'animations':{}}
    essential=r.boolean()
    if essential:j['skeleton'].update(fps=r.f(),images=r.string())
    for i in range(r.var()):
        b={'name':r.string()}
        if i:b['parent']=j['bones'][r.var()]['name']
        for k in ('rotation','x','y','scaleX','scaleY','shearX','shearY','length'):b[k]=r.f()
        b['transform']=['normal','onlyTranslation','noRotationOrReflection','noScale','noScaleOrReflection'][r.var()]
        if essential:b['color']=r.color()
        j['bones'].append(b)
    for _ in range(r.var()):
        s={'name':r.string(),'bone':j['bones'][r.var()]['name'],'color':r.color()};dark=r.color()
        if dark!='ffffffff':s['dark']=dark[2:]
        s['attachment']=r.string();s['blend']=['normal','additive','multiply','screen'][r.var()];j['slots'].append(s)
    for section in ('ik','transform','path'):
        for _ in range(r.var()):
            c={'name':r.string(),'order':r.var(),'bones':[j['bones'][r.var()]['name'] for _ in range(r.var())]}
            c['target']=j['slots' if section=='path' else 'bones'][r.var()]['name']
            if section=='ik':c.update(mix=r.f(),bendPositive=r.signed()>0)
            elif section=='transform':
                c.update(local=r.boolean(),relative=r.boolean())
                for k in ('rotation','x','y','scaleX','scaleY','shearY','rotateMix','translateMix','scaleMix','shearMix'):c[k]=r.f()
            else:
                c.update(positionMode=['fixed','percent'][r.var()],spacingMode=['length','fixed','percent'][r.var()],rotateMode=['tangent','chain','chainScale'][r.var()])
                for k in ('rotation','position','spacing','rotateMix','translateMix'):c[k]=r.f()
            j[section].append(c)
    skin=r.skin(essential,j['slots'])
    if skin:j['skins']['default']=skin
    for _ in range(r.var()):
        name=r.string();j['skins'][name]=r.skin(essential,j['slots'])
    for _ in range(r.var()):
        name=r.string();j['events'][name]={'int':r.var(False),'float':r.f(),'string':r.string()}
    for _ in range(r.var()):
        name=r.string();j['animations'][name]=r.animation(j)
    if r.at!=len(data):raise ValueError(f'Trailing bytes: {len(data)-r.at}')
    return j
