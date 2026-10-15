/** Same-origin, tightly scoped GXB3 bridge for the independent Vercel Studio.
 * No tokens or SUPER GM identity are stored by this deployment. The upstream
 * checks the authenticated session and the separate GM key on every mutation.
 */
const UPSTREAM='https://180-93-111-99.sslip.io';
const allowed=(p)=>/^\/api\/(auth\/(?:me|login)|giftcode\/(?:catalog|list|redemptions|redeem|check|sso\/exchange|admin\/(?:create|revoke|unlock))|skin-shop\/(?:catalog|bank\/(?:create|orders)|admin\/(?:catalog|update|bulk|bank\/(?:orders|review)))|admin\/gm\/verify-key)$/.test(p);
export default async function handler(req,res){
  const host=String(req.headers.host||'').toLowerCase();
  const origin='https://'+host;
  if(req.method!=='GET'&&req.method!=='POST'){
    res.status(405).json({error:'Phương thức không được hỗ trợ'});return;
  }
  if(req.method==='POST'&&req.headers.origin!==origin){
    res.status(403).json({error:'Nguồn yêu cầu không hợp lệ'});return;
  }
  // req.query.slug may be an object depending on Vercel routing.
  // Read the literal URL path instead, then apply the exact allowlist.
  const original=new URL(req.url,origin);
  const route=String(req.query.route||'');
  const path='/api/'+route;
  if(!allowed(path)){res.status(404).json({error:'API không được hỗ trợ'});return;}
  try{
    const target=new URL(path,UPSTREAM);
    for(const [k,v] of original.searchParams){if(k!=='slug'&&k!=='route')target.searchParams.append(k,v);}
    const headers={'Accept':'application/json','Origin':UPSTREAM};
    if(req.headers.cookie)headers.Cookie=req.headers.cookie;
    if(req.method==='POST'){
      headers['Content-Type']='application/json';
      if(req.headers['x-gxb3-gm-key'])headers['X-GXB3-GM-Key']=String(req.headers['x-gxb3-gm-key']);
      if(req.headers['x-gxb3-giftcode-access'])headers['X-GXB3-Giftcode-Access']=String(req.headers['x-gxb3-giftcode-access']);
    }
    const upstream=await fetch(target,{method:req.method,headers,
      body:req.method==='POST'?JSON.stringify(req.body||{}):undefined,
      redirect:'manual',signal:AbortSignal.timeout(15000)});
    const cookie=upstream.headers.get('set-cookie');
    if(cookie)res.setHeader('Set-Cookie',cookie);
    res.setHeader('Cache-Control','private, no-store, max-age=0');
    res.setHeader('X-Content-Type-Options','nosniff');
    const data=await upstream.text();
    res.status(upstream.status);
    res.setHeader('Content-Type','application/json; charset=utf-8');
    res.end(data);
  }catch{
    res.status(502).json({error:'Chưa kết nối được máy chủ GXB 3'});
  }
}
