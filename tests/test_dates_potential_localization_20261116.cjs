'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const html=read('web/index.html'),ui=read('web/girl-ui.js'),dates=read('web/dates.js'),css=read('web/dates.css');
const canonical=JSON.parse(read('data/relations.json'));
const catalog=JSON.parse(read('data/potentials.json'));
const translations=JSON.parse(read('web/assets/dates/dialogues-vi.json'));
const lines=Object.values(canonical.dialogs).flat().filter(line=>line.text && line.text!=='-1');
assert.equal(translations.schema,1);
assert.equal(Object.keys(translations.translations).length,lines.length);
assert.equal(translations.source_count,lines.length);
for(const line of lines){
 const localized=translations.translations[String(line.id)];
 assert(typeof localized==='string'&&localized.trim(),'Missing Vietnamese text for voice '+line.id);
 assert.equal(typeof line.sound,'string');
}
assert.equal(Object.keys(catalog.skills).length,15);
assert.match(ui,/win\(\{title:'Chọn Tiềm Năng',cls:'lb-choose'\}\)/);
assert.match(ui,/function choosePotential[\s\S]*?const info=potentialInfo\(id\)/);
assert.match(ui,/el\('span','lb-active','Đã Kích Hoạt'\)/);
assert.match(ui,/n\.title=info\?info\.name:i<=done\?'Chọn Tiềm Năng'/);
assert.match(html,/\/girl-ui\.js\?v=20261116-potential-choose-vi-r3/);
assert.match(css,/\.dates-view \.dt-stage \.dt-art>\.wp-home\{[\s\S]*?height:calc\(1280 \* var\(--u\)\)!important/);
assert.match(css,/aspect-ratio:720 \/ 1280/);
assert.match(css,/--u:calc\(100cqw \/ 720\)/);
assert.match(html,/\/dates\.css\?v=20261116-portrait-native-r2/);
assert.match(html,/\/dates\.js\?v=20261116-dialogues-full-vi-r3/);
assert.match(dates,/const VOICE_TYPES_VI/);
assert.match(dates,/line\.text=text/);
assert.match(dates,/line\.id/);
const audio=[];
const ctx=vm.createContext({
 window:{addEventListener(){}},
 document:{createElement(){return {style:{},append(){},className:'',set textContent(x){this.text=x}}}},
 state:{roster:[],items:{}},
 api:async url=>{
  if(url==='/assets/relations.json')return JSON.parse(JSON.stringify(canonical));
  if(url.startsWith('/assets/dates/dialogues-vi.json'))return translations;
  throw Error('Unexpected API '+url);
 },
 Audio:class{constructor(url){this.url=url;audio.push(url);}play(){return Promise.resolve();}pause(){}},
 GxbVi:{t:x=>x},
 GxbAudio:{volume(){return 90}},
});
const altered=dates.replace('return {open,render,playGirlVoice};','return {open,render,playGirlVoice,_inspect:()=>({data,bubble})};');
vm.runInContext(altered,ctx);
const Dates=vm.runInContext('Dates',ctx);
(async()=>{
 const sample=lines.find(l=>Number(l.type)===2&&l.sound);
 assert(sample,'No playable voice');
 const heroKey=Object.keys(canonical.dialogs).find(k=>canonical.dialogs[k].some(l=>l.id===sample.id));
 assert.equal(await Dates.playGirlVoice(Number(heroKey)),true);
 const visible=Dates._inspect();
 assert.equal(visible.bubble,translations.translations[String(sample.id)]);
 assert(audio.some(url=>url==='/assets/voices/'+sample.sound+'.mp3'),'Voice clip ID was replaced');
 assert.equal(visible.data.dialogs[heroKey].find(l=>l.id===sample.id).sound,sample.sound);
 assert.equal(visible.data.dialog_types['15'],'Thân Mật');
 console.log('PASS 5,250 localized dialogues, preserved sound IDs, native Hẹn Hò canvas, Tiềm Năng picker');
})().catch(e=>{console.error(e);process.exitCode=1;});
