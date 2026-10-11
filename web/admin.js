'use strict';
window.AdminPanel=(()=>{
  let root=null,cfg=null;
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const field=(parent,label,id,type='number',step='0.1')=>{const l=el('label','',label),i=document.createElement('input');i.id=id;i.type=type;if(step)i.step=step;l.append(i);parent.append(l);return i;};
  function ensure(){
    if(root)return root;
    root=el('section','admin-view');root.id='admin-view';root.hidden=true;
    const head=el('header','admin-head');const back=el('button','','← Game');back.onclick=close;const exit=el('button','','Thoát QTV');exit.onclick=logout;head.append(back,el('h1','','Bảng Quản Trị GxB2 Local'),exit);root.append(head);
    const grid=el('div','admin-grid');

    const res=el('section','admin-card');res.append(el('h2','','Tài nguyên & nhân vật khởi đầu'));
    const ta=document.createElement('textarea');ta.id='admin-resources';res.append(el('label','','starting_resources (JSON)'),ta);
    const starters=field(res,'Starter Girls (ID, cách nhau bằng dấu phẩy)','admin-starters','text',null);
    grid.append(res);

    const summon=el('section','admin-card');summon.append(el('h2','','Tỷ lệ Triệu Hồi'));
    for(const star of [1,2,3,4,5,6])field(summon,`${star}★ multiplier`,`admin-star-${star}`);
    summon.append(el('p','admin-note','1.0 = tỷ lệ gốc; 2.0 = tăng gấp đôi trọng số; 0 = loại khỏi pool.'));
    grid.append(summon);

    const economy=el('section','admin-card');economy.append(el('h2','','Kinh tế Local'));
    field(economy,'Giá Shop ×','admin-shop');
    field(economy,'Phần thưởng ×','admin-reward');
    field(economy,'Chi phí tiến triển ×','admin-progress');
    economy.append(el('p','admin-note','Chi phí tiến triển áp dụng cho tăng cấp, tăng bậc và nguyên liệu tiền tệ của thức tỉnh. Phần thưởng áp dụng cho Campaign idle, Campaign clear, Tests và Daily Quiz.'));
    grid.append(economy);

    const tools=el('section','admin-card');tools.append(el('h2','','Công cụ QTV'));
    const toolGrid=el('div','admin-tools');
    const girl=el('div','admin-tool');const sel=document.createElement('select');sel.id='admin-girl';girl.append(sel);
    const count=field(girl,'Số lượng','admin-count','number','1');count.min=1;count.max=20;count.value=1;
    const level=field(girl,'Cấp','admin-level','number','1');level.min=1;level.max=330;level.value=80;
    const add=el('button','primary','Thêm Nữ Sinh');add.onclick=()=>act('girl');girl.append(add);toolGrid.append(girl);
    const misc=el('div','admin-tool');
    [['all_girls','Thêm toàn bộ Nữ Sinh'],['max_stars','Đưa Nữ Sinh đã chọn lên 15★'],['levels','Áp cấp cho toàn bộ'],['campaign','Mở 30 ải đang hiển thị']].forEach(([a,t])=>{const b=el('button','',t);b.onclick=()=>act(a);misc.append(b);});
    const floor=field(misc,'Tầng Tests','admin-floor','number','1');floor.min=1;floor.max=1500;floor.value=1;
    const tower=el('button','','Đến tầng Tests');tower.onclick=()=>act('tower');misc.append(tower);toolGrid.append(misc);
    tools.append(toolGrid);grid.append(tools);

    root.append(grid);
    const actions=el('div','admin-actions'),save=el('button','primary','Lưu cấu hình'),reload=el('button','','Tải lại'),reset=el('button','danger','Khôi phục mặc định');
    save.onclick=saveConfig;reload.onclick=load;reset.onclick=resetConfig;actions.append(save,reload,reset);root.append(actions);
    const status=el('p','admin-status');status.id='admin-status';root.append(status);
    document.getElementById('game-root').append(root);
    return root;
  }
  function status(t){const n=document.getElementById('admin-status');if(n)n.textContent=t||'';}
  function populateGirls(){const sel=document.getElementById('admin-girl');if(!sel||sel.childElementCount)return;for(const girl of girlsCatalog){const o=el('option','',`${girl.name} · ${girl.stars}★ · ${girl.id}`);o.value=girl.id;sel.append(o);}}
  function fill(){
    document.getElementById('admin-resources').value=JSON.stringify(cfg.starting_resources,null,2);
    document.getElementById('admin-starters').value=cfg.starter_girls.join(',');
    for(const star of [1,2,3,4,5,6])document.getElementById(`admin-star-${star}`).value=cfg.summon_rate.star_multiplier[String(star)]??1;
    document.getElementById('admin-shop').value=cfg.shop.price_multiplier;
    document.getElementById('admin-reward').value=cfg.rewards.multiplier;
    document.getElementById('admin-progress').value=cfg.progression.cost_multiplier;
  }
  async function load(){try{ensure();cfg=await api('/api/admin/config');fill();populateGirls();status('Đã tải cấu hình Local.');}catch(e){status(e.message);}}
  async function saveConfig(){try{
    const raw={
      starting_resources:JSON.parse(document.getElementById('admin-resources').value),
      starter_girls:document.getElementById('admin-starters').value.split(',').map(x=>Number(x.trim())).filter(Boolean),
      summon_rate:{star_multiplier:Object.fromEntries([1,2,3,4,5,6].map(s=>[String(s),Number(document.getElementById(`admin-star-${s}`).value)]))},
      shop:{price_multiplier:Number(document.getElementById('admin-shop').value)},
      rewards:{multiplier:Number(document.getElementById('admin-reward').value)},
      progression:{cost_multiplier:Number(document.getElementById('admin-progress').value)}
    };
    cfg=await api('/api/admin/config',raw);fill();status('Đã lưu. Cấu hình mới có hiệu lực ngay; tài nguyên/starter chỉ áp dụng khi tạo save mới.');
  }catch(e){status(e.message);}}
  async function resetConfig(){try{cfg=await api('/api/admin/config',{action:'reset'});fill();status('Đã khôi phục cấu hình mặc định.');}catch(e){status(e.message);}}
  async function act(action){try{
    const data=await api('/api/developer',{action,table_id:Number(document.getElementById('admin-girl').value),count:Number(document.getElementById('admin-count').value),level:Number(document.getElementById('admin-level').value),floor:Number(document.getElementById('admin-floor').value)});
    state=data.state;loadFormation();render();status('Đã áp dụng vào save QTV.');
  }catch(e){status(e.message);}}
  async function open(){ensure();root.hidden=false;await load();}
  function close(){if(root)root.hidden=true;showView('home');}
  async function logout(){developerMode=false;adminKey='';sessionStorage.setItem('gxb2-developer','0');sessionStorage.removeItem('gxb2-admin-key');if(root)root.hidden=true;state=await api('/api/state');loadFormation();showView('home');render();}
  return{open,close,load,logout};
})();
