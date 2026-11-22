-- Native publisher table contract; no player account, no database writes.
package.path='/opt/gxb3/runtime/lua/?.lua;'..package.path
require('lib.battle.LyrSoniaPatch').register()
local function find(mod,id)
 local t=require('data.tables.'..mod)
 local cur=t.rows
 while cur do
  for _,row in pairs(cur) do
   if type(row)=='table' and tonumber(row[t.keys.id])==id then
    local result={}
    for k,p in pairs(t.keys) do result[k]=row[p] end
    return result
   end
  end
  local mt=getmetatable(cur);cur=mt and type(mt.__index)=='table' and mt.__index or nil
 end
 error('Missing '..mod..' '..id)
end
local poisonHit=find('effect2',1758018)
local poisonTick=find('effect2',1758019)
assert(poisonHit.buff=='hurt' and tonumber(poisonHit.num)==0.65)
assert(poisonTick.buff=='hpDotPoison' and tonumber(poisonTick.num)==0.02)
assert(tonumber(poisonTick.round)==3 and tonumber(poisonTick.prob)==1)
local skill=find('skill7',75800101)
assert(tonumber(skill.target3)==108 and tonumber(skill.rand3)==5)
assert(skill.effect3=='1758018|1758019')
assert(skill.effect1:find('1758001',1,true)~=nil)
assert(skill.effect1:find('1758014',1,true)~=nil)
assert(skill.effect1:find('1758015',1,true)~=nil)
assert(skill.effect2=='1758017')
local src=assert(io.open('runtime/lua/lib/battle/LyrSoniaPatch.lua','r')):read('*a')
assert(src:find('for id = 1758001, 1758039 do',1,true))
assert(src:find('ReportBuff.setIsHit = function',1,true))
assert(src:find('ShieldBuff.excuteBuff = function',1,true))
print('PASS: five random native poison knives at 65% ATK, 2% HP native DOT for 3 rounds; all Sonia effects registered')
