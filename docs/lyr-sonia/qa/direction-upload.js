/* Lyr Sonia v1.7 -- native Spine 3.6 six-view QA. No GIF, no synthetic art.
   The owner supplies the approved v1.4 ZIP locally in their browser. */
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const rules=window.LyrSoniaDirectionRules;
if(!rules)throw Error('Missing six-view runtime rules');
const VIEWS=rules.VIEWS.map(v=>[v.id,v.label]);
const PREFIX='spine/';
const textDecoder=new TextDecoder('utf-8',{fatal:true});
let direction=null, actor=null,urls=[],loaded=false, app=null, hero=null;
function setMessage(text,error=false){
 const e=$('direction-status');
 e.textContent=text;e.style.color=error?'#ffb5be':'#b8f1d4';
}
function zipEntries(buffer){
 const b=new Uint8Array(buffer),v=new DataView(buffer),read16=i=>v.getUint16(i,true),read32=i=>v.getUint32(i,true);
 let e=-1;for(let p=b.length-22;p>=Math.max(0,b.length-65557);p--){
  if(read32(p)===0x06054b50){e=p;break}
 }
 if(e<0)throw Error('Không phải tệp ZIP chuẩn');
 if(read16(e+4)||read16(e+6))throw Error('ZIP nhiều ổ đĩa không được hỗ trợ');
 const n=read16(e+10),offset=read32(e+16),entries=new Map();
 if(n>200||offset>b.length)throw Error('ZIP không hợp lệ');
 let p=offset;
 for(let i=0;i<n;i++){
  if(read32(p)!==0x02014b50)throw Error('Bảng ZIP không hợp lệ');
  const method=read16(p+10),size=read32(p+20),uncompressed=read32(p+24);
  const nlen=read16(p+28),extra=read16(p+30),comment=read16(p+32),local=read32(p+42);
  if(size>8e6||uncompressed>12e6||method!==0&&method!==8)throw Error('Tệp ZIP quá lớn hoặc kiểu nén không hỗ trợ');
  const name=textDecoder.decode(b.slice(p+46,p+46+nlen));
  if(name.startsWith(PREFIX)&&['spine/model.json','spine/model.atlas','spine/lyr_sonia_6_directions.webp'].includes(name)){
    if(read32(local)!==0x04034b50)throw Error('Tệp ZIP hỏng');
    const st=local+30+read16(local+26)+read16(local+28);
    if(st+size>b.length)throw Error('ZIP quá ngắn');
    entries.set(name,{method,data:b.slice(st,st+size),uncompressed});
  }
  p+=46+nlen+extra+comment;
 }
 return entries;
}
async function inflate(item){
 if(item.method===0)return item.data;
 if(!('DecompressionStream' in window))throw Error('Chrome này không hỗ trợ giải nén ZIP; hãy cập nhật Chrome');
 let raw;
 try{
  raw=await new Response(new Blob([item.data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer();
 }catch(err){throw Error('Không giải nén được ZIP: '+err.message)}
 if(raw.byteLength!==item.uncompressed)throw Error('Độ dài dữ liệu ZIP không khớp');
 return new Uint8Array(raw);
}
async function get(e,key){
 const obj=e.get(key);if(!obj)throw Error('ZIP thiếu '+key);
 return inflate(obj);
}
function cleanUrls(){for(const u of urls)URL.revokeObjectURL(u);urls=[]}
async function importZip(file){
 if(!file) return;
 try{
  if(!file.name.toLowerCase().endsWith('.zip')||file.size>15e6)throw Error('Chọn ZIP 6 hướng v1.4 (tối đa 15 MB)');
  setMessage('Đang đọc ảnh sáu hướng đã duyệt...');
  const entries=zipEntries(await file.arrayBuffer());
  const model=JSON.parse(textDecoder.decode(await get(entries,'spine/model.json')));
  const atlas=textDecoder.decode(await get(entries,'spine/model.atlas'));
  const imgBytes=await get(entries,'spine/lyr_sonia_6_directions.webp');
  if(model.skeleton?.spine!=='3.6.37')throw Error('Model khác Spine 3.6.37');
  if(!VIEWS.every(([v])=>model.animations?.['face_'+v]&&model.skins?.default?.direction_sprite?.[v]))
      throw Error('ZIP không chứa đủ sáu góc nhìn đã duyệt');
  if(imgBytes.length<1000)throw Error('Ảnh texture trống');
  cleanUrls();
  const imageURL=URL.createObjectURL(new Blob([imgBytes],{type:'image/webp'}));urls.push(imageURL);
  const image=await new Promise((resolve,reject)=>{
    const im=new Image();im.onload=()=>resolve(im);
    im.onerror=()=>reject(new Error('Không đọc được texture WebP'));
    im.src=imageURL;
  });
  const baseTexture=PIXI.BaseTexture.from(image);
  const blobJSON=URL.createObjectURL(new Blob([JSON.stringify(model)],{type:'application/json'}));
  urls.push(blobJSON);
  const loader=new PIXI.Loader();
  loader.pre((resource,next)=>{if(resource.name==='lyr_direction')resource.xhrType=PIXI.LoaderResource.XHR_RESPONSE_TYPE.JSON;next()});
  loader.add('lyr_direction',blobJSON,{metadata:{
    atlasRawData:atlas,image:baseTexture
  }});
  const result=await new Promise((resolve,reject)=>{
    loader.onError.add(e=>reject(new Error(e.message||'Không dựng được atlas')));
    loader.load((_loader,r)=>resolve(r.lyr_direction));
  });
  if(!result?.spineData)throw Error('Runtime không tạo được SpineData sáu hướng (type='+(result?.type||'?')+', xhr='+(result?.xhrType||'?')+', data='+typeof result?.data+', ext='+(result?.extension||'?')+', error='+(result?.error?.message||'-')+')');
  const bridge=window.__soniaCombatStage;
  if(!bridge?.app||!bridge?.getHero())throw Error('Chưa khởi tạo được sân thử chiến đấu');
  app=bridge.app;hero=bridge.getHero();
  if(actor){app.stage.removeChild(actor);actor.destroy({children:true});}
  actor=new PIXI.spine.Spine(result.spineData);
  actor.autoUpdate=false;actor.position.set(340,570);actor.scale.set(.90);
  app.stage.addChild(actor);
  loaded=true;
  for(const button of document.querySelectorAll('[data-facing]'))button.disabled=false;
  setMessage('Đã nạp sáu hướng bằng Spine/WebGL thật. Các góc chưa có rig Attack/Skill sẽ không giả hoạt ảnh.');
  selectDirection('front');
 }catch(err){setMessage('Lỗi: '+String(err.message||err),true);loaded=false}
}
function selectDirection(next){
 if(!loaded||!VIEWS.some(([v])=>v===next))return;
 direction=next;
 const front=rules.hasAnimatedRig(next,'skill');
 actor.visible=!front;
 hero.visible=front;
 for(const id of ['clip','play','stop','scrub'])$(id).disabled=!front;
 for(const b of document.querySelectorAll('[data-facing]')){
  b.setAttribute('aria-pressed',b.dataset.facing===next?'true':'false');
 }
 if(!front){
  actor.state.setAnimation(0,'face_'+next,false);
  actor.update(0);
  setMessage('Đang xem '+VIEWS.find(x=>x[0]===next)[1]+' bằng attachment thật. Attack/Skill hướng này chưa rig nên đã khóa, không lật ảnh giả.');
 }else{
  const b=window.__soniaCombatStage;
  b.showFront();
  setMessage('Chính diện: bật năm hoạt ảnh chiến đấu để kiểm tra. Hướng khác chỉ kiểm tra góc hình thật.');
 }
 app.renderer.render(app.stage);
 window.__soniaDirectionQA={loaded,view:next,spine:!!actor,frontCombatReady:front};
}
window.addEventListener('DOMContentLoaded',()=>{
 const input=$('direction-zip');
 if(!input)return;
 input.onchange=()=>importZip(input.files[0]);
 for(const b of document.querySelectorAll('[data-facing]'))b.onclick=()=>selectDirection(b.dataset.facing);
});
})();
