-- Read-only native battle data contract: dynamic local table augmentation.
-- This test runs in a new LuaJIT process, never touches Neon/player state.
package.path='/opt/gxb3/runtime/lua/?.lua;'..package.path
local patch=require('lib.battle.LyrSoniaPatch')
patch.register()
local function find(mod,id)
 local t=require('data.tables.'..mod)
 local cur=t.rows
 while cur do
  for _,row in pairs(cur)do
   if type(row)=='table' and tonumber(row[t.keys.id])==id then
    local obj={}
    for k,pos in pairs(t.keys)do obj[k]=row[pos] end
    return obj
   end
  end
  local mt=getmetatable(cur);cur=mt and type(mt.__index)=='table' and mt.__index or nil
 end
end
local expect={
 [1758014]={'spdSteal',1321,40,2,0.40},
 [1758015]={'seal',1271,0,1,0.25},
 [1758016]={'stunH',1127,0,1,0.18},
 [1758017]={'hpShieldByAD',1557,2,0,1},
}
for id,rule in pairs(expect)do
 local e=find('effect2',id)
 assert(e,'missing native effect '..id)
 assert(e.buff==rule[1] and tonumber(e.type)==rule[2], 'wrong native mechanic '..id)
 assert(tonumber(e.num)==rule[3] and tonumber(e.round)==rule[4], 'wrong duration or amount '..id)
 assert(math.abs(tonumber(e.prob)-rule[5])<.0001,'wrong chance '..id)
end
local a=find('skill7',75800101)
local b=find('skill7',75800100)
local p=find('skill7',75800103)
assert(a and b and p,'missing Sonia skill')
for _,id in ipairs({'1758014','1758015'}) do
 assert(tostring(a.effect1):find(id,1,true),'active effect missing '..id)
end
assert(tostring(a.effect2)=='1758017' and tonumber(a.target2)==1,'self shield absent')
assert(tostring(b.effect1):find('1758016',1,true),'turn ban missing')
assert(tostring(p.effect1):find('1758007',1,true),'original shield removed')
assert(tostring(a.effect1):find('1758001',1,true),'original active damage removed')
print('PASS: native Lord Dracula speed steal, Promethea seal, real shield, and turn ban; original skills preserved')
