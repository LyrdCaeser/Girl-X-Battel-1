'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const css=read('web/hero-glow.css'),html=read('web/index.html'),src=read('web/hero-glow.js');
const frames=JSON.parse(read('web/assets/spine/frame-effects.json'));
assert.equal(frames['8080'],'frame_maya','purple floral native animated frame must be the selected target');
assert(fs.existsSync(path.join(root,'web/assets/profile/frame_8080.png')));
assert.match(html,/\/hero-glow\.css\?v=20261117-frame8080-fit-r1/);
assert.match(html,/\/hero-glow\.js\?v=20261117-frame8080-fit-r1/);
assert.match(css,/#home-view \.home-profile\[data-avatar-frame="8080"\]>\.home-profile-frame/);
assert.match(css,/#profile-view \.profile-avatar\[data-avatar-frame="8080"\]>\.profile-frame-image/);
assert.match(css,/#profile-view \.profile-preview-avatar\[data-avatar-frame="8080"\]>#profile-preview-frame/);
assert.match(css,/#home-view \.home-profile\.hg-profile-animated\[data-avatar-frame="8080"\]>\.hg-glow\.hg-profile/);
assert.match(css,/top:-6%!important;left:-6%!important/);
assert.match(css,/width:112%!important;height:112%!important/);
assert.match(css,/top:-13%!important;left:-13%!important/);
assert.match(css,/width:126%!important;height:126%!important/);
assert(Math.abs((-6 + 112/2) - 50)<1e-8,'static art must center on blue outline');
assert(Math.abs((-13 + 126/2) - 50)<1e-8,'Spine art must center on blue outline');
assert.match(css,/pointer-events:none!important/);
assert(!/\.home-profile-portrait\s*\{/.test(css),'must not crop or modify uploaded portraits');
async function run(){
  class Observer{observe(){}unobserve(){}}
  const calls=[];
  class Figure{
    constructor(){this.autoUpdate=false;this.scale={set(){}};this.position={set(){}};this.state={setAnimation(){}};}
    update(){}
  }
  const ctx=vm.createContext({
    IntersectionObserver:Observer,
    GxbSpine:{load:async src=>{calls.push(src);return {};}},
    PIXI:{Container:class{constructor(){this.children=[];}addChild(x){this.children.push(x);}},spine:{Spine:Figure}},
    api:async url=>{assert.equal(url,'/assets/spine/frame-effects.json');return frames;},
    document:{addEventListener(){},body:{append(){}},hidden:false},
    requestAnimationFrame(){return 1;},
    matchMedia(){return {matches:false};},
    Image:class{},
  });
  vm.runInContext(src,ctx);
  const glow=vm.runInContext('HeroGlow',ctx);
  const classes=new Set();
  const host={
    dataset:{},children:[],classList:{add(s){classes.add(s);},remove(s){classes.delete(s);}},
    append(c){c.parent=this;this.children.push(c);},
  };
  // Test canvas instances have parent pointer and may detach.
  ctx.document.createElement=(tag)=>{
    assert.equal(tag,'canvas');
    return {tagName:tag,style:{},setAttribute(){},getContext(){return {};},remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);}};
  };
  await glow.profile(host,'frame_8080');
  assert.equal(host.dataset.avatarFrame,'8080');
  assert(classes.has('hg-profile-animated'));
  assert.equal(host.children.length,1);
  assert.equal(host.children[0].className,'hg-glow hg-profile');
  assert(calls.includes('/assets/spine/frame_maya'),'existing animated effect must stay active');
  await glow.profile(host,'frame_8007');
  assert.equal(host.dataset.avatarFrame,'8007','changing frames must clear special styling');
  assert.equal(host.children.length,0);
  assert(!classes.has('hg-profile-animated'));
  console.log('PASS: native 8080 static/Spine artwork centered and enlarged; avatar retained; switching frames restores default');
}
run().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
