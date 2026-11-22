local M = {}

local function appendRaw(moduleName, values)
    local data = require('data.tables.' .. moduleName)
    local rows = data.rows
    local keys = data.keys
    local maxIndex = 0
    local cursor = rows
    while cursor do
        for index in pairs(cursor) do
            if type(index) == 'number' and index > maxIndex then maxIndex = index end
        end
        local mt = getmetatable(cursor)
        cursor = mt and type(mt.__index) == 'table' and mt.__index or nil
    end
    local row = {}
    for key, value in pairs(values) do
        local pos = keys[key]
        if pos then row[pos] = value end
    end
    rows[maxIndex + 1] = row
end

local function effect(id, buff, kind, num, rounds, prob)
    appendRaw('effect2', {id=id, buff=buff, type=kind, num=num,
        round=rounds or 0, prob=prob or 1})
end

local function skill(id, values)
    values.id = id
    values.partner = -1
    values.name = values.name or -1
    values.desc = values.desc or -1
    values.icon_id = values.icon_id or ''
    appendRaw('skill7', values)
end

function M.register()
    appendRaw('partner2', {
        id=758001, name=-1, name2=-1, ver=1, group=8, job=2,
        max_grade=6, max_star=10, max_lv=250,
        base_atk=1056, base_hp=13680, base_arm=60, base_spd=312,
        grow_atk=105.6, grow_hp=1368, grow_arm=6, grow_spd=2,
        energy_base=50, decompose='7#25000|9#200000|10#25000',
        ex_skill=0, star_origin=0, atk_id=75800100,
        act_skill_id=75800101, pas_skill1_id=75800102,
        pas_skill2_id=75800103, pas_skill3_id=75800104,
        pas_tier1=1, pas_tier2=1, pas_tier3=1,
        host='', material='', avatar='partner_avatar_758001',
        partner_model=75800101, show_in_guide=1, show_in_forge=1,
        show_in_guide_auditing=0, show_in_forge_auditing=0,
        awake_material='758001|758001|758001|758001|758001',
        awake_grow='116.69#1572#6#2|128.83#1800.88#6#2|142.23#2062.8#6#2|152.88#2261.18#6#2|164.32#2478.78#6#2',
        awake_skill='75800101#75800102#75800103#75800104|75800101#75800102#75800103#75800104|75800101#75800102#75800103#75800104|75800101#75800102#75800103#75800104|75800101#75800102#75800103#75800104',
        stone_material='10#10000|10#10000|10#15000|10#15000|10#20000',
        potential='100101#100102#100103|100201#100202#100203|100301#100302#100303|100401#100402#100403|100501#100502#100503',
        n_id='', star_10='', skin_ids='', wedding_skin_id='', wedding_skin_time='',
        comment_id=858001, show_ids='758001', hero_list='758001',
        achievement_id='', partner_data_id='583|584|585|586',
        gift_type1='1000012|1000005', gift_type2='1000021|1000003',
        shenxue_table_id=0, partner_shard=0
    })

    effect(1758001, 'hurt', 1019, 2.60, 0, 1)
    effect(1758002, 'kawenMark', 1459, '0|0|0|5', 3, 1)
    effect(1758003, 'sklP', 1005, 0.25, 2, 1)
    effect(1758004, 'hurt', 1019, 1.30, 0, 1)
    effect(1758005, 'energy', 1013, -20, 0, 1)
    effect(1758006, 'energy', 1013, 40, 0, 1)
    effect(1758007, 'hpShieldByAD', 1557, 6, 0, 1)
    effect(1758008, 'stunless', 1125, 0, 0, 1)
    effect(1758009, 'energy', 1013, 80, 0, 1)
    effect(1758010, 'spd', 1004, 30, 2, 1)
    effect(1758011, 'hpShieldEndToHeal', 1558, 1758009, 99, 1)
    effect(1758012, 'realHurt', 1457, 2.60, 0, 1)
    effect(1758013, 'kawenCountMark', 1456,
        '1758012|1015166|1758001|1758001', 0, 1)

    skill(75800100, {is_pass=0, trigger=1, target1=108, rand1=3,
        effect1='1758004|1758005', sub_skill='75800105|75800107'})
    skill(75800101, {is_pass=0, trigger=3, is_cost_energy=1,
        target1=12, effect1='1758001|1758002|1758002',
        sub_skill='75800106|75800107', icon_id='skill_icon_75800101'})
    skill(75800102, {is_pass=1, trigger=28, attr_pas=1, target1=1,
        effect1='', icon_id='skill_icon_75800102', level=3})
    skill(75800103, {is_pass=1, trigger=28, target1=1,
        effect1='1758007|1758008|1758011', icon_id='skill_icon_75800103', level=3})
    skill(75800104, {is_pass=1, trigger=15, target1=1,
        effect1='', icon_id='skill_icon_75800104', level=3})
    skill(75800105, {is_pass=1, is_cost_energy=2, is_add_energy=1,
        is_unseal=1, target1=1, effect1=1758006, sub_skill=0})
    skill(75800106, {is_pass=1, is_cost_energy=2, is_add_energy=1,
        is_unseal=1, target1=1, effect1=1758003, sub_skill=0})
    skill(75800107, {is_pass=1, is_cost_energy=2, is_add_energy=1,
        is_unseal=1, target1=1, effect1=1758013, sub_skill=0})
end

function M.apply()
    local function readRaw(moduleName, wanted)
        local data = require('data.tables.' .. moduleName)
        local cursor = data.rows
        while cursor do
            for _, row in pairs(cursor) do
                if tonumber(row[data.keys.id]) == wanted then
                    local out = {}
                    for key, pos in pairs(data.keys) do
                        if row[pos] ~= nil then out[key] = row[pos] end
                    end
                    return out
                end
            end
            local mt = getmetatable(cursor)
            cursor = mt and type(mt.__index) == 'table' and mt.__index or nil
        end
    end
    local function split(value)
        local out = {}
        if value == nil or value == '' or tonumber(value) == 0 then return out end
        for token in tostring(value):gmatch('[^|]+') do out[#out + 1] = tonumber(token) or token end
        return out
    end
    local partner = assert(readRaw('partner2', 758001))
    local pt = xyd.tables.partnerTable
    pt.datas_[758001] = partner
    pt.ids_[#pt.ids_ + 1] = 758001
    local function partnerMethod(name, fn)
        local original = pt[name]
        pt[name] = function(self, id, ...)
            if tonumber(id) == 758001 then return fn(partner, ...) end
            return original(self, id, ...)
        end
    end
    partnerMethod('getGroup', function(p) return tonumber(p.group) end)
    partnerMethod('getJob', function(p) return tonumber(p.job) end)
    partnerMethod('getPugongID', function(p) return tonumber(p.atk_id) end)
    partnerMethod('getAllPugongIDs', function(p) return {tonumber(p.atk_id)} end)
    partnerMethod('getEnergyID', function(p) return tonumber(p.act_skill_id) end)
    partnerMethod('getInitMp', function(p) return tonumber(p.energy_base) or 0 end)
    partnerMethod('getModelID', function(p) return tonumber(p.partner_model) end)
    partnerMethod('getMaxlev', function(p) return tonumber(p.max_lv) end)
    partnerMethod('getMaxStar', function(p) return tonumber(p.max_star) end)
    partnerMethod('getStarOrigin', function(p) return tonumber(p.star_origin) or 0 end)
    partnerMethod('getExSkill', function(p) return tonumber(p.ex_skill) or 0 end)
    partnerMethod('getBaseAtk', function(p) return tonumber(p.base_atk) end)
    partnerMethod('getBaseHp', function(p) return tonumber(p.base_hp) end)
    partnerMethod('getBaseArm', function(p) return tonumber(p.base_arm) end)
    partnerMethod('getBaseSpd', function(p) return tonumber(p.base_spd) end)
    partnerMethod('growAtk', function(p) return tonumber(p.grow_atk) end)
    partnerMethod('growHp', function(p) return tonumber(p.grow_hp) end)
    partnerMethod('growArm', function(p) return tonumber(p.grow_arm) end)
    partnerMethod('growSpd', function(p) return tonumber(p.grow_spd) end)
    partnerMethod('getPasTier', function(p, index) return tonumber(p['pas_tier' .. tostring(index)]) or 1 end)
    partnerMethod('getPasSkill', function(p, index)
        if index then return tonumber(p['pas_skill' .. tostring(index) .. '_id']) end
        return {tonumber(p.pas_skill1_id), tonumber(p.pas_skill2_id), tonumber(p.pas_skill3_id)}
    end)
    partnerMethod('awakeSkill', function(p)
        local out = {}
        for value in tostring(p.awake_skill or ''):gmatch('[^|]+') do out[#out + 1] = value end
        return out
    end)
    partnerMethod('awakeGrow', function(p)
        local out = {}
        for value in tostring(p.awake_grow or ''):gmatch('[^|]+') do out[#out + 1] = value end
        return out
    end)

    local et = xyd.tables.effectTable
    local customEffects = {}
    for id = 1758001, 1758013 do
        local record = readRaw('effect2', id)
        if record then
            et.datas[id] = record
            customEffects[id] = record
            et.ids_[#et.ids_ + 1] = id
            et.TableLua.ids[#et.TableLua.ids + 1] = id
        end
    end
    local function effectMethod(name, fn)
        local original = et[name]
        et[name] = function(self, id, ...)
            local row = customEffects[tonumber(id)]
            if row then return fn(row, ...) end
            return original(self, id, ...)
        end
    end
    effectMethod('buff', function(r) return r.buff end)
    effectMethod('getType', function(r) return r.buff end)
    effectMethod('getNum', function(r)
        if type(r.num) == 'string' and r.num:find('|', 1, true) then return split(r.num) end
        return tonumber(r.num) or r.num
    end)
    effectMethod('num', function(r)
        if type(r.num) == 'string' and r.num:find('|', 1, true) then return split(r.num) end
        return tonumber(r.num) or r.num
    end)
    effectMethod('round', function(r) return tonumber(r.round) or 0 end)
    effectMethod('prob', function(r) return tonumber(r.prob) or 1 end)
    effectMethod('fxHurt', function(r) return r.fx_hurt1 end)

    local customSkills = {}
    local st = xyd.tables.skillTable
    for id = 75800100, 75800107 do
        customSkills[id] = readRaw('skill7', id)
        st.ids_[#st.ids_ + 1] = id
        st.TableLua.ids[#st.TableLua.ids + 1] = id
    end
    local function skillMethod(name, fn)
        local original = st[name]
        st[name] = function(self, id, ...)
            local row = customSkills[tonumber(id)]
            if row then return fn(row, ...) end
            return original(self, id, ...)
        end
    end
    skillMethod('isPass', function(r) return tonumber(r.is_pass) or 0 end)
    skillMethod('getTrigger', function(r) return tonumber(r.trigger) or 0 end)
    skillMethod('trigger', function(r) return tonumber(r.trigger) or 0 end)
    skillMethod('getTargets', function(r, index)
        if index then return tonumber(r['target' .. tostring(index)]) end
        local out = {}
        for n = 1, 3 do if r['target' .. n] ~= nil then out[#out + 1] = tonumber(r['target' .. n]) end end
        return out
    end)
    skillMethod('getRandNum', function(r, index)
        if index then return tonumber(r['rand' .. tostring(index)]) or 1 end
        local out = {}
        for n = 1, 3 do if r['target' .. n] ~= nil then out[#out + 1] = tonumber(r['rand' .. n]) or 1 end end
        return out
    end)
    skillMethod('getSubSkills', function(r) return split(r.sub_skill) end)
    skillMethod('isCostEnergy', function(r) return tonumber(r.is_cost_energy) or 0 end)
    skillMethod('getIsAddEnergy', function(r) return tonumber(r.is_add_energy) or 0 end)
    skillMethod('isUnSeal', function(r) return tonumber(r.is_unseal) or 0 end)
    skillMethod('isAttrPas', function(r) return tonumber(r.attr_pas) or 0 end)
    skillMethod('attrPas', function(r) return tonumber(r.attr_pas) or 0 end)
    skillMethod('getSkillLev', function(r) return tonumber(r.level) or 1 end)
    skillMethod('getName', function(r) return r.name end)
    skillMethod('getDesc', function(r) return r.desc end)
    skillMethod('getSkillIcon', function(r) return r.icon_id end)
    skillMethod('animation', function(r) return r.animation end)
    skillMethod('getSound', function(r) return r.sound end)
    skillMethod('isBlackScreen', function(r) return r.black_screen end)
    skillMethod('isShake', function(r) return tonumber(r.shake_screen) or 0 end)
    skillMethod('getEffectAdd', function(r) return {} end)
    skillMethod('getFx', function(r) return {} end)
    skillMethod('getFxHurt1', function(r) return {} end)
    skillMethod('getFxHurt1Add', function(r) return {} end)
    skillMethod('getFxHurt2', function(r) return {} end)
    skillMethod('getNoAct', function(r) return 0 end)
    skillMethod('getNoCrit', function(r) return 0 end)
    skillMethod('getNoMiss', function(r) return 0 end)
    skillMethod('getSkillEffects', function(r) return 0 end)
    skillMethod('getTargetNoEffect', function(r) return {} end)
    skillMethod('getTargetSkillIndex', function(r) return nil end)
    skillMethod('getPreTime', function(r) return nil end)
    skillMethod('atkIndex', function(r) return nil end)
    skillMethod('heroPosType', function(r) return 0 end)
    skillMethod('heroPosTypeXY', function(r) return {} end)
    skillMethod('jump', function(r) return 0 end)
    skillMethod('jumpDelta', function(r) return {} end)
    skillMethod('shakeTime', function(r) return '' end)
    skillMethod('getEffect', function(r, index) return split(r['effect' .. tostring(index or 1)]) end)
    skillMethod('getEffects', function(r)
        local out = {}
        for index = 1, 3 do
            local effects = split(r['effect' .. tostring(index)])
            if #effects > 0 then
                local values = {}
                for _, value in ipairs(effects) do values[#values + 1] = tostring(value) end
                out[#out + 1] = values
            end
        end
        return out
    end)
end

return M
