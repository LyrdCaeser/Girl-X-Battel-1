'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const girls=JSON.parse(fs.readFileSync('web/assets/girls-catalog.json','utf8'));
const byId=new Map(girls.map(g=>[Number(g.id),g]));
const hostChain=id=>{const seen=new Set(),r=[];let n=Number(id);
 while(n&&!seen.has(n)&&r.length<7){r.push(n);seen.add(n);n=Number(byId.get(n)?.host||0);}
 return r;
};
const relations=JSON.parse(fs.readFileSync('data/relations.json','utf8'));
const translated=JSON.parse(fs.readFileSync('web/assets/dates/dialogues-vi.json','utf8'));
const clips=[];class Audio{constructor(src){this.src=src;clips.push(src)}pause(){}play(){return Promise.resolve()}}
const ctx=vm.createContext({window:{addEventListener(){}},hostChain,Audio,GxbAudio:{volume:()=>95},GxbVi:{t:x=>x},
 api:async(path)=>{if(path==='/assets/relations.json')return structuredClone(relations);
  if(path.startsWith('/assets/dates/dialogues-vi.json'))return translated;throw Error('Unexpected URL '+path);},
});
vm.runInContext(fs.readFileSync('web/dates.js','utf8'),ctx);
const Dates=vm.runInContext('Dates',ctx);
(async()=>{
 let playable=0,previouslyUnmatched=0;
 for(const g of girls){
  const id=Number(g.id),legacy=[String(id),String(id%100000),String(id%10000+50000)];
  if(!legacy.some(x=>relations.dialogs[x]))previouslyUnmatched++;
  let caption='';
  const ok=await Dates.playGirlVoice(id,line=>{caption=line});
  assert.equal(ok,true,'missing voice '+id);
  assert(typeof caption==='string'&&caption.length>0,'missing translated voice caption '+id);
  assert(clips.at(-1)?.endsWith('.mp3'),'missing authentic voice clip '+id);
  const clip=clips.at(-1).split('/').at(-1);
  assert(fs.existsSync('web/assets/voices/'+clip),'missing audio asset '+clip);
  playable++;
 }
 assert.equal(previouslyUnmatched,48);
 assert.equal(playable,446);
 let dracula='';
 assert.equal(await Dates.playGirlVoice(751017,line=>{dracula=line}),true);
 assert(dracula.length>0);
 assert.equal(dracula,translated.translations[relations.dialogs['51017'][1].id]||dracula);
 console.log('PASS: '+playable+' original Goddess / upgraded forms resolve source Japanese MP3 + Vietnamese dialogue; '+previouslyUnmatched+' repaired by host chain');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
