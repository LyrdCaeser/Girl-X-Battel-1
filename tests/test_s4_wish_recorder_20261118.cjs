'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/wish-recorder.js','utf8');
const windowEvents={};
function E(tag='div'){
 this.tagName=tag;this.children=[];this.className='';this.style={};this.dataset={};
 this.isConnected=true;this.textContent='';this.disabled=false;
 this.append=(...items)=>{this.children.push(...items);return this;};
 this.remove=()=>{this.isConnected=false;};
 this.querySelector=(q)=>q==='button'?this.children.find(x=>x.tagName==='button'):
     this.children.find(x=>x.className==='gxb-wish-record-label');
 this.click=()=>{if(this.onclick)this.onclick();};
}
const root=new E(),body=new E();
const document={
 body,createElement:tag=>new E(tag),
 querySelectorAll:()=>[],
};
let starts=0,stops=0,requestGranted=false;
let captureOn=false;
const bridge={
 isSupported:()=>true,isRecording:()=>captureOn,
 start(){
  starts++;
  // Android asks the user; no call starts capture until consent is granted.
  if(requestGranted){captureOn=true;fire('gxb3-wish-recording',
    {state:'recording',message:'Đang quay Wish'});}
 },
 stop(){
  stops++;captureOn=false;
  fire('gxb3-wish-recording',
    {state:'saved',message:'Đã lưu video vào Thư viện → GXB3 Wish.'});
 }
};
const win={
 GXB3WishRecorder:bridge,GxbFrame:{root:()=>root},
 addEventListener:(type,fn)=>windowEvents[type]=fn,
 MediaRecorder:null,
};
function fire(type,detail){windowEvents[type]({detail});}
const context=vm.createContext({
 window:win,document,navigator:{mediaDevices:null},
 console,URL,Date,Number,Promise,setTimeout,clearTimeout,
 GirlUI:{toast:()=>{}}
});
const recorder=vm.runInContext(source+'; WishRecorder',context);
(async()=>{
 assert(recorder.supported());
 assert(!recorder.isRecording());
 const parent=new E();
 const controls=recorder.mount(parent);
 assert.equal(parent.children.length,1);
 assert.equal(controls.children[0].textContent,'Quay Wish');
 assert.equal(starts,0,'Screen recording NEVER starts automatically');
 // User must tap and grant Android's MediaProjection permission.
 await recorder.startRecording();
 assert.equal(starts,1);
 assert(!recorder.isRecording(),'Without permission, no capture');
 fire('gxb3-wish-recording',{state:'cancelled',message:'Quyền bị từ chối'});
 assert.equal(recorder.status,'cancelled');
 requestGranted=true;
 await recorder.startRecording();
 assert.equal(starts,2);
 assert(recorder.isRecording());
 assert(root.children.length>=1,'Stop button is shown during full Wish animation');
 recorder.finishWish();
 assert.equal(stops,1,'Wish ending automatically stops and saves Android MP4');
 assert(!recorder.isRecording());
 assert.equal(recorder.status,'saved');
 recorder.finishWish();
 assert.equal(stops,1,'Do not issue duplicate stop/save calls');
 assert(controls.children[0].className.includes('gxb-wish-record-action'));
 const html=fs.readFileSync('web/index.html','utf8');
 assert(html.includes('/wish-recorder.js?v=20261118-wish-capture-r1'));
 assert(html.includes('/wish-recorder.css?v=20261118-wish-capture-r1'));
 const home=fs.readFileSync('web/home-menus.js','utf8');
 assert(home.includes("state?.server_id==='S4'"));
 assert(home.includes('WishRecorder.mount(parent)'));
 assert(home.includes('WishRecorder.finishWish()'));
 assert(home.includes('finally'));
 const manifest=fs.readFileSync('clients/android/app/src/main/AndroidManifest.xml','utf8');
 for(const part of ['FOREGROUND_SERVICE_MEDIA_PROJECTION',
                    'android:foregroundServiceType="mediaProjection"',
                    'WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28"']){
  assert(manifest.includes(part),part);
 }
 const service=fs.readFileSync('clients/android/app/src/main/java/com/gxb3/game/WishCaptureService.java','utf8');
 for(const part of ['getMediaProjection(code,token)',
                    'projection.registerCallback(projectionCallback',
                    'MediaStore.Video.Media.IS_PENDING,1',
                    'MediaStore.Video.Media.IS_PENDING,0',
                    'stopForeground(STOP_FOREGROUND_REMOVE)',
                    'new Thread(() ->','"GXB3 Wish"','"video/mp4"']){
  assert(service.includes(part),part);
 }
 console.log('PASS: Android Wish recording requires consent, auto-stops, saves MP4 to gallery, no duplicate saves');
})().catch(e=>{console.error(e);process.exitCode=1;});
