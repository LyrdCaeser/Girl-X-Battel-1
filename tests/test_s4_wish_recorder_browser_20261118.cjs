'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const src=fs.readFileSync('web/wish-recorder.js','utf8');
const handlers={};let recordingStopped=0,fileClicks=0,urlCreated=0,requested=0;
function node(tag='div'){
 const e={tagName:tag,className:'',children:[],style:{},isConnected:true,dataset:{},
  append(...c){this.children.push(...c)},remove(){this.isConnected=false},
  querySelector(t){return t==='button'?this.children.find(x=>x.tagName==='button'):this.children[0]},
  click(){fileClicks++}};
 return e;
}
const body=node(),root=node();
const video={stop:()=>{recordingStopped++;},addEventListener:()=>{}};
const stream={getTracks:()=>[video],getVideoTracks:()=>[video]};
class FakeRecorder {
 static isTypeSupported(){return true;}
 constructor(s,opts){this.state='inactive';this.mimeType=opts.mimeType;}
 start(){this.state='recording'}
 requestData(){this.ondataavailable?.({data:new Blob(['test-'.repeat(800)])})}
 stop(){this.state='inactive';this.onstop?.()}
}
const win={GxbFrame:{root:()=>root},MediaRecorder:FakeRecorder,
 addEventListener:(type,handler)=>{handlers[type]=handler;}};
const doc={body,createElement:node,querySelectorAll:()=>[]};
const scope=vm.createContext({
 window:win,document:doc,Date,Number,Promise,Blob,MediaRecorder:FakeRecorder,
 navigator:{mediaDevices:{getDisplayMedia:async(opts)=>{requested++;assert(opts.video);return stream;}}},
 URL:{createObjectURL:blob=>{assert(blob.size>1024);urlCreated++;return 'blob:test';},revokeObjectURL:()=>{}},
 setTimeout:()=>1,console
});
const recorder=vm.runInContext(src+'; WishRecorder',scope);
(async()=>{
 assert(recorder.supported());
 assert.equal(fileClicks,0);
 await recorder.startRecording();
 assert.equal(requested,1);
 assert(recorder.isRecording());
 recorder.finishWish();
 assert.equal(recorder.status,'saved');
 assert.equal(fileClicks,1,'Web fallback triggers browser download');
 assert.equal(urlCreated,1,'Only one finished WebM saved');
 assert.equal(recordingStopped,1);
 assert(!recorder.isRecording());
 recorder.finishWish();
 assert.equal(fileClicks,1);
 console.log('PASS: desktop browser permission, real MediaRecorder, WebM download and auto-stop');
})().catch(e=>{console.error(e);process.exitCode=1;});
