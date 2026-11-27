'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const girls=read('web/assets/girls-catalog.json'),byId=new Map(girls.map(g=>[Number(g.id),g]));
const relations=read('data/relations.json'),translation=read('web/assets/dates/dialogues-vi.json'),sonia=read('web/assets/chaos/lyr_sonia_voice.json');
const hostChain=id=>{const out=[Number(id)];for(let k=0;k<5;k++){const h=byId.get(out.at(-1))?.host;if(!h)break;out.push(Number(h));}return out;};
const clips=[];
class Audio{constructor(src){clips.push(src)}pause(){}play(){return Promise.resolve()}}
const ctx=vm.createContext({window:{addEventListener(){}},hostChain,Audio,GxbAudio:{volume:()=>90},GxbVi:{t:x=>x},
api:async path=>{if(path==='/assets/relations.json')return structuredClone(relations);
if(path.startsWith('/assets/dates/dialogues-vi.json'))return translation;
if(path.startsWith('/assets/chaos/lyr_sonia_voice.json'))return sonia;
throw Error(path);}});
const src=fs.readFileSync('web/dates.js','utf8');
vm.runInContext(src.replace('return {open,render,playGirlVoice,playGirlVoiceByType};','return {open,render,playGirlVoice,playGirlVoiceByType,allLines};'),ctx);
const Dates=vm.runInContext('Dates',ctx);
(async()=>{
 let count=0,lines=0;
 for(const g of girls){
  const id=Number(g.id);if(id===758001)continue;
  const canonical=hostChain(id).find(x=>relations.dialogs[String(x)]?.length);
  assert(canonical,'No native dialogue for '+id);
  let caption='';
  assert(await Dates.playGirlVoice(id,x=>caption=x),String(id));
  const expected=relations.dialogs[String(canonical)];
  const first=expected.find(x=>x.sound&&[1,2,3,26].includes(Number(x.type)));
  assert.equal(clips.at(-1),'/assets/voices/'+first.sound+'.mp3',g.name+' '+id);
  assert.equal(caption,translation.translations[String(first.id)]);
  const actual=Dates.allLines({table_id:id});
  assert.equal(actual.length,expected.length);
  for(let i=0;i<actual.length;i++){
   assert.equal(actual[i].id,expected[i].id);
   assert.equal(actual[i].sound,expected[i].sound);
   if(actual[i].sound)assert(fs.existsSync('web/assets/voices/'+actual[i].sound+'.mp3'),actual[i].sound);
   if(expected[i].text&&expected[i].text!=='-1')assert.equal(actual[i].text,translation.translations[String(actual[i].id)]);
   lines++;
  }
  count++;
 }
 for(const [ids,base] of [[[55011,655020,755010],55011],[[55010,655019,755009],55010]]){
  for(const id of ids){
   const expected=relations.dialogs[String(base)].find(x=>x.type===4&&x.sound);
   let caption='';assert(await Dates.playGirlVoiceByType(id,4,x=>caption=x));
   assert.equal(clips.at(-1),'/assets/voices/'+expected.sound+'.mp3');
   assert.equal(caption,translation.translations[expected.id]);
   assert.equal(Dates.allLines({table_id:id}).length,32);
  }
 }
 assert.equal(Dates.allLines({table_id:758001})[0].id,sonia.dialogs[0].id);
 assert.equal(Dates.allLines({table_id:955010}).length,0,'Unknown ID must never borrow voice');
 console.log('PASS: '+count+' native forms, '+lines+' dialogue references; Maia and Frexie independently verified, Sonia preserved');
})().catch(e=>{console.error(e);process.exitCode=1;});
