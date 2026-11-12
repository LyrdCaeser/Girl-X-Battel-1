-- Headless adapter: original APK bytecode, isolated Lua environment.
local root=assert(arg[1])
local mode=arg[2] or 'battle'
local target=arg[3]
local function quote(s)return '"'..s:gsub('[%z\1-\31\\"]',function(c)local m={['"']='\\"',['\\']='\\\\',['\n']='\\n',['\r']='\\r',['\t']='\\t'}return m[c] or string.format('\\u%04x',string.byte(c)) end)..'"'end
local function json(v)
 local t=type(v);if t=='nil'then return 'null' elseif t=='boolean'or t=='number'then return tostring(v)elseif t=='string'then return quote(v)end
 assert(t=='table',t);local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 local a=#keys>0;for i=1,#keys do if v[i]==nil then a=false end end
 local r={};if a then for i=1,#keys do r[#r+1]=json(v[i])end;return '['..table.concat(r,',')..']'end
 for _,k in ipairs(keys)do r[#r+1]=quote(tostring(k))..':'..json(v[k])end;return '{'..table.concat(r,',')..'}'
end
local env={io={},os={}}
for _,k in ipairs({'assert','error','ipairs','pairs','next','pcall','xpcall','select','tonumber','tostring','type','unpack','setmetatable','getmetatable','rawget','rawset','rawequal','setfenv','getfenv'})do env[k]=_G[k]end
for _,k in ipairs({'math','string','table'})do env[k]={};for a,b in pairs(_G[k])do env[k][a]=b end end
local function log(...)local a={};for i=1,select('#',...)do a[i]=tostring(select(i,...))end;io.stderr:write(table.concat(a,'\t')..'\n')end
local function vec(...)return {...}end
local constructor=setmetatable({New=vec,New2=vec},{__call=function(_,...)return vec(...)end})
env.Vector2=constructor;env.Vector3=constructor;env.Vector4=constructor;env.Quaternion=constructor;env.Color=constructor
env.reportLog=function()end;env.reportLog2=function()end;env.print=log;env.dump=function()end;env.print_r=function()end
env.debug={traceback=debug.traceback,getlocal=debug.getlocal,getinfo=debug.getinfo}
env.xyd={Global={isLoginInfoReceived=false,lang='en_en'},models={}};env._G=env;env.unpack=unpack
local loaded={};local stack={};local used={}
env.package={loaded=loaded,preload={}}
env.require=function(name)
 if loaded[name]~=nil then return loaded[name]end
 if name=='cjson'then return {encode=json,decode=function()error('JSON decode not used in this headless path')end}end
 assert(name:match('^[%w_%.]+$') and not name:find('%.%.'),'invalid module')
 assert(name:match('^app%.common%.')or name:match('^app%.models%.')or name:match('^data%.tables%.')or name:match('^lib%.battle%.')or name:match('^base%.'),'module denied: '..name)
 local file=root..'/'..name:gsub('%.','/')..'.lua'
 local f=assert(loadfile(file));setfenv(f,env);stack[#stack+1]=name;used[name]=true
 local r=f(name);stack[#stack]=nil;loaded[name]=r or true;return loaded[name]
end
env.import=function(name)
 if name:sub(1,1)=='.'then local current=assert(stack[#stack],'relative import outside module load');name=current:match('^(.*)%.')..name end
 return env.require(name)
end
env.require('base.functions')
local cocos=env.require('lib.battle.framework.cocos');env.string.split=cocos.string.split
for _,name in ipairs({'app.common.enums','app.common.const','app.common.Battle','app.common.utils'})do env.require(name)end
env.require('app.common.tables.TableManager').get()
if mode=='tables'then
 for i=4,#arg do
  local name=arg[i];local t=env.require('data.tables.'..name)
  local function flatten(v)local a={};local m=getmetatable(v);if m and type(m.__index)=='table'then a=flatten(m.__index)end;for k,x in pairs(v)do a[k]=x end;return a end
  local out={keys=flatten(t.keys),rows=flatten(t.rows),ids=t.ids}
  local f=assert(io.open(target..'/'..name..'.json','wb'));f:write(json(out));f:close();log('table',name)
 end
 return
end
env.xyd.models.heroAttr=env.require('app.models.HeroAttr').new()
env.xyd.models.reportPetAttr=env.require('app.models.ReportPetAttr').new()
-- LOCAL-072: low-star girls retain their native skills; Python strips unsupported
-- awake indices and passes local_growth separately. Same math in detail/combat.
local nativeAttr=env.xyd.models.heroAttr.attr
env.xyd.models.heroAttr.attr=function(self,hero,params)
 local awake=hero.getAwake and tonumber(hero:getAwake()) or 0
 local breakSteps=math.max(0,awake-5)
 -- The archived HeroAttr bytecode only has native growth through 15★.
 -- For 16–25★, calculate the exact native 15★ baseline, then apply the
 -- approved per-star growth to the same HP/ATK/DEF fields used by combat.
 if breakSteps>0 then hero.awake_=5 end
 local result=nativeAttr(self,hero,params)
 if breakSteps>0 then hero.awake_=awake end
 local before=(result.atk or 0)+(result.arm or 0)+math.floor((result.hp or 0)/6)
 local localGrowth=tonumber(hero.local_growth or 0) or 0
 if localGrowth>0 then
  for _,key in ipairs({'hp','atk','arm'})do if result[key] then result[key]=math.floor(result[key]*(1+0.25*localGrowth)) end end
 end
 if breakSteps>0 then
  local hpGrowth={14.56,14.56,9.62,9.62}
  local atkGrowth={10.40,10.40,7.49,7.49}
  local hp=tonumber(result.hp or 0);local atk=tonumber(result.atk or 0)
  for step=1,breakSteps do
   local idx=((step-1)%4)+1
   hp=math.floor(hp*(1+hpGrowth[idx]/100))
   atk=math.floor(atk*(1+atkGrowth[idx]/100))
  end
  result.hp=hp;result.atk=atk
  -- Approved DEF rule: 102% at 16★ through 120% at 25★,
  -- each percentage point is measured from the 15★ baseline.
  result.arm=math.floor((tonumber(result.arm or 0))*(1+0.02*breakSteps))
 end
 if localGrowth>0 or breakSteps>0 then
  result.power=(result.power or 0)-before+(result.atk or 0)+(result.arm or 0)+math.floor((result.hp or 0)/6)
 end
 return result
end

local Hero=env.require('lib.battle.ReportHero')
local Report=env.require('lib.battle.BattleCreateReport')
local input={teamA={{table_id=41001,partner_id=1,lv=1,pos=1}},teamB={{table_id=1,isMonster=true,pos=1}},battle_id=100001,random_seed=12345}
if target then local f=assert(loadfile(target));setfenv(f,{});input=f() end
if mode=='attrs'then
 -- Real partner attributes (HeroAttr:attr) for the detail screen; input = list of partner rows.
 local out={}
 for _,item in ipairs(input.partners or input)do local hero=Hero.new();hero:populate(item);hero.local_growth=item.local_growth;hero:setGuildInfo(input.guildSkills or {});if input.chimeBonus and hero.setChimeBonus then hero:setChimeBonus(input.chimeBonus) end;local a=env.xyd.models.heroAttr:attr(hero);local r={};for k,v in pairs(a)do if type(v)=='number'then r[k]=v end end;out[tostring(item.partner_id)]=r end
 print(json(out));return
end
local function team(rows,guildSkills,chimeBonus)
 local out={}
 for _,item in ipairs(rows)do
  local hero=Hero.new()
  if item.isMonster then hero:populateWithTableID(item.table_id,item)else hero:populate(item);hero.local_growth=item.local_growth end
  if hero.setGuildInfo then hero:setGuildInfo(guildSkills or {}) end
  if chimeBonus and hero.setChimeBonus then hero:setChimeBonus(chimeBonus) end
  out[#out+1]=hero
 end
 return out
end
-- Servant (ReportPet.populate: pet_id, grade, lv, skills[4], ex_lv) when the local save has one selected.
local petA=nil
if input.petA then petA=env.require('lib.battle.ReportPet').new();petA:populate(input.petA) end
local petB=nil
if input.petB then petB=env.require('lib.battle.ReportPet').new();petB:populate(input.petB) end
local r=Report.new({
 petA=petA,petB=petB,
 herosA=team(input.teamA,input.guildSkillsA,input.chimeBonusA),
 herosB=team(input.teamB,input.guildSkillsB,input.chimeBonusB),
 guildSkillsA=input.guildSkillsA or {},guildSkillsB=input.guildSkillsB or {},
 battleID=input.battle_id,random_seed=input.random_seed,battle_type=input.battle_type or 1,
 god_skills=input.god_skills or {},shrineId=input.shrine_id,maxRound=input.max_round,
 galaxy_info=input.galaxy_info,chimeBonusA=input.chimeBonusA,chimeBonusB=input.chimeBonusB
})
r:run()
local report=r:getReport();report.random_seed=input.random_seed
if r.getTotalHarm then report.total_harm=r:getTotalHarm() end
-- End status per fighter (Patrol keeps HP/energy between fights): getPos() is 1-6 for team A and 7-12 for team B.
report.end_status={}
for _,side in ipairs({'teamA','teamB'})do for _,v in ipairs(env.xyd.Battle[side] or {})do report.end_status[#report.end_status+1]={pos=v:getPos(),hp=math.ceil(100*v:getHpPercent()),mp=v:getEnergy()}end end
print(json(report))
if arg[4] then local f=assert(io.open(arg[4],'wb'));f:write(json(used));f:close()end
