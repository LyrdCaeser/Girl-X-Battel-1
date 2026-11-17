'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const wallpaper=fs.readFileSync(path.join(root,'web/wallpaper.js'),'utf8');
const html=fs.readFileSync(path.join(root,'web/index.html'),'utf8');

function fakeHero(){
 const attrs={};
 return {
   attrs,hidden:false,style:{visibility:''},
   classList:{toggle(){}},
   getAttribute(k){return attrs[k]??null;},
   removeAttribute(k){delete attrs[k];},
   set src(v){attrs.src=v;},
   get src(){return attrs.src;}
 };
}

async function testOverlay(){
 const prelude=app.slice(app.indexOf('function renderHome(){')+'function renderHome(){'.length,app.indexOf("$('home-level')",app.indexOf('function renderHome(){')));
 const run=new Function('homeHeroIndex','Wallpaper','LobbyDialogue','$',prelude);
 for(const [index,expected] of [
   [0,null],[1,'/assets/hero-42001.png'],[2,'/assets/hero-43001.png']
 ]){
   const hero=fakeHero(), w={heroSrc:()=>null,mountHome:()=>Promise.resolve(false)};
   run(index,w,{sync:()=>{}},selector=>{assert.equal(selector,'home-hero');return hero;});
   await Promise.resolve();
   assert.equal(hero.attrs.src||null,expected);
   assert.equal(hero.hidden,!expected);
 }
 assert.match(html,/<img id="home-hero" class="home-hero" alt="" hidden>/);
 assert.match(html,/<div class="home-background"><\/div>/,'the original home background remains');
 assert.doesNotMatch(html,/<img id="home-hero"[^>]*src="[^"]*41001/);
}

async function testSavedWallpaper(){
 const stage={querySelector(){return null;}},calls=[];
 const ctx=vm.createContext({
   document:{addEventListener(){},querySelector(sel){return sel==='#home-view .home-stage'?stage:null;}},
   localStorage:{getItem(){return '';}},
   state:{profile:{wallpapers:[41001],wallpaper_random:0}},
   GirlUI:{picture(id){calls.push(id);return '/assets/pictures/'+id+'.webp';}},
   api:async()=>{throw Error('No API read needed to hide ID 41001');},
   $:()=>null,
 });
 vm.runInContext(wallpaper,ctx);
 assert.equal(vm.runInContext('Wallpaper.heroSrc(0)',ctx),null);
 assert.equal(await vm.runInContext('Wallpaper.mountHome(0)',ctx),false);
 assert.equal(calls.length,0);
 const before=ctx.state.profile.wallpapers.slice();
 ctx.state.profile.wallpapers=[42001];
 assert.equal(vm.runInContext('Wallpaper.heroSrc(0)',ctx),'/assets/pictures/42001.webp');
 assert.deepEqual(before,[41001], 'the saved wallpaper list is not mutated');
 assert.equal(html.includes('/app.js?v=20261117-anima-convert-r4'),true);
 assert.equal(html.includes('/wallpaper.js?v=20261116-remove-home-41001-r3'),true);
}

(async()=>{await testOverlay();await testSavedWallpaper();console.log('HOME 41001 HIDDEN — other heroes preserved and wallpaper untouched: PASS');})()
 .catch(e=>{console.error(e);process.exitCode=1;});
