# FairArena — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `activity_fair_arena_box_equip`: 88 filas; campos: id, equip_id, weight, box_id
- `activity_fair_arena_box_partner`: 139 filas; campos: id, partner_id, name, box_id, weight, lv, grade, equips, is_new, is_up
- `activity_fair_arena_level`: 11 filas; campos: id, level, win_time, style, awards, score, box_partner, box_partner_elite, box_equip, box_buff, chance_hard, chance_reach
- `activity_fair_arena_rank`: 12 filas; campos: id, rank, awards, rank_front
- `activity_fair_arena_robot`: 34 filas; campos: id, name, lv, server, avatar_id, show_id, partner_ids, equip_ids, buff_ids, treasure_level
- `buff`: 646 filas; campos: name, desc1, desc, has_child, type, debuff_type, is_unclean, is_debuffSame, is_hp_change, job, group, pos, actual_buff, is_percent, is_attr, factor, not_show_attr, is_pass_no_attr, show_percent, icon1, icon2, has_fx, fx, hero, hero_work_fx, layer, cover, is_attr_buff, use_origin_name
- `equip`: 1643 filas; campos: id, name, 水鏡深戀淨靈皮膚, type, pos, qlt, star, item_lv, price, base1, base2, base3, base4, skill_id, ex_skill, group, job, act, form, suit_name, suit1, suit2, suit3, suit_skills, icon, formula, need_formula, treasure_upgrade, treasure_all_upgrade, treasure_refresh, treasure_lock_up, treasure_max, treasure_weight, artifact_exp, artifact_upg, artifact_next, artifact_pink, initial_artifact, power, partner_model, avatar, fx_index, get_ways
- `group_buff`: 26 filas; campos: id, name, desc, type, group_config, effect_show, effect, effect_stands, fx, rank
- `item`: 6233 filas; campos: id, name, brief, desc, name1, type, type_config, qlt, group, is_economy, stack_limit, level, icon, light_effect, gift_id, is_auto_open, equip, pub_scroll_type, partner_cost, treasure_cost, get_ways, go_window, getway_item, dropbox_show, is_sell, sell_price, summon_id, show_in_bag, show_bag_type, filter_type, show_in_forge, skin_id, collection_id, para, avatar_frame_effect, effect_mask, dress_id, clear_act, jobGiftBoxID, is_change_border, sort_forward, is_soul_equip_box
- `misc`: 1332 filas; campos: key, value, desc
- `model`: 803 filas; campos: id, name, name2, model_name, scale, shade_pos, blood_pos, atk_time, skill_time, pet_details_pos, pet_card_pos, pet_show_pos, battle_pos, fx_pos, house_model, house_reset_state, revive
- `partner`: 647 filas; campos: id, name, name2, ver, group, job, max_grade, max_star, max_lv, base_atk, base_hp, base_arm, base_spd, grow_atk, grow_hp, grow_arm, grow_spd, energy_base, decompose, grade_lv1, grade_exp1, grade_lv2, grade_exp2, grade_lv3, grade_exp3, grade_lv4, grade_exp4, grade_lv5, grade_exp5, grade_lv6, grade_exp6, ex_skill, star_origin, atk_id, act_skill_id, pas_skill1_id, pas_skill2_id, pas_skill3_id, pas_tier1, pas_tier2, pas_tier3, host, material, avatar, partner_model, show_in_guide, show_in_forge, show_in_guide_auditing, show_in_forge_auditing, awake_material, awake_grow, awake_skill, stone_material, potential, n_id, star_10, skin_ids, wedding_skin_id, wedding_skin_time, comment_id, show_ids, hero_list, achievement_id, partner_data_id, gift_type1, gift_type2, shenxue_table_id, partner_shard, click_dialog1, click_dialog2, click_dialog3, click_dialog4, click_dialog5, dialogs, click_sound1, click_sound2, click_sound3, click_sound4, click_sound5, battle_sound, start_sound, dead_sound, skill_sound, lvlup_sound, gradeup_sound, shengxue_sound, awake_sound, equip_sound1, equip_sound2, hangteam_sound, victory_sound, failed_sound, love_point_sound1, love_point_sound2, love_point_sound3, love_point_sound4, vow_sound, house_sound, house_set_sound, idle_sound, dagong_sound, daily_mission_sound, new_stage_sound, gift_sound1, gift_sound2, gift_sound3, login_sound
- `partner_exskill`: 416 filas; campos: id, ex_id, desc_num1, desc_num2, desc_num3, desc_num4, desc_num5, desc_num6, desc_num7, desc_num8, desc_num9
- `stage`: 530 filas; campos: id, name, fort_id, fort_finish, next, fort_final, lv, power, battle_id, monsterShow, monsterskin, battle_effect, battle_time, reward, gold, exp_partner, exp_player, dropbox_ids, dropbox_show, dropbox_id_activity, dropbox_show_activity, dropbox_id_activity2, dropbox_show_activity2, dropbox_id_activity3, dropbox_show_activity3, dropbox_id_activity4, dropbox_show_activity4, set_map, stage_img, tips_type, function_id

## Mensajes y esquemas de solicitud

- `FAIR_ARENA_BATTLE`: ID 881
- `FAIR_ARENA_EQUIP`: ID 884
- `FAIR_ARENA_EXPLORE`: ID 880
- `FAIR_ARENA_GET_REPORT`: ID 886
- `FAIR_ARENA_RANK`: ID 885
- `FAIR_ARENA_RESET`: ID 883
- `FAIR_ARENA_SELECT`: ID 882
- `fair_arena_equip_req`: activity_id (campo 1, tipo 5, label 2), partner_id (campo 2, tipo 5, label 2), equip_id (campo 3, tipo 5, label 2)
- `fair_arena_explore_req`: activity_id (campo 1, tipo 5, label 2), operate (campo 2, tipo 5, label 2)
- `fair_arena_get_report_req`: activity_id (campo 1, tipo 5, label 2), id (campo 2, tipo 5, label 2)
- `fair_arena_rank_req`: activity_id (campo 1, tipo 5, label 2)
- `fair_arena_reset_req`: activity_id (campo 1, tipo 5, label 2), type (campo 2, tipo 5, label 2), partner_id (campo 3, tipo 5, label 2), table_id (campo 4, tipo 5, label 2)
- `fair_arena_select_req`: activity_id (campo 1, tipo 5, label 2), partners (campo 2, tipo 5, label 3), equips (campo 3, tipo 5, label 1), buffs (campo 4, tipo 5, label 1)

## Métodos del modelo (líneas de la fuente original)

- Línea 11: `FairArena:ctor()`
- Línea 15: `FairArena:onRegister()`
- Línea 24: `FairArena:reqArenaInfo()`
- Línea 28: `FairArena:reqExplore(type)`
- Línea 50: `FairArena:reqSelect(partners, equips, buffs)`
- Línea 72: `FairArena:reqReset(type, id, table_id)`
- Línea 83: `FairArena:reqEquip(partner_id, equip_id)`
- Línea 93: `FairArena:reqRank()`
- Línea 101: `FairArena:reqGetReport(id, enemy_infos)`
- Línea 111: `FairArena:onGetData(event)`
- Línea 123: `FairArena:onExplore(event)`
- Línea 148: `FairArena:onSelect(event)`
- Línea 173: `FairArena:onBattle(event)`
- Línea 181: `FairArena:onReset(event)`
- Línea 187: `FairArena:onEquip(event)`
- Línea 199: `FairArena:updateArenaInfo(info)`
- Línea 236: `FairArena:getArenaInfo()`
- Línea 240: `FairArena:initPartners()`
- Línea 286: `FairArena:getPartners()`
- Línea 290: `FairArena:getPartnerIds()`
- Línea 294: `FairArena:getBuffs()`
- Línea 298: `FairArena:getEquips()`
- Línea 302: `FairArena:getPartnerByID(id)`
- Línea 306: `FairArena:getEnemyInfo()`
- Línea 310: `FairArena:getHoeBuyTimes()`
- Línea 314: `FairArena:getSelfInfo()`
- Línea 324: `FairArena:getOldEnemyInfo()`
- Línea 330: `FairArena:getReportEnemyInfo()`
- Línea 336: `FairArena:checkTest()`
- Línea 340: `FairArena:readStorageFormation()`
- Línea 365: `FairArena:saveLocalformation(formation)`
- Línea 375: `FairArena:makeEnemyInfo(infos)`
- Línea 403: `FairArena:getEndTime()`
- Línea 407: `FairArena:getActBuffID(partners)`
- Línea 484: `FairArena:checkGetNewEquip()`
- Línea 488: `FairArena:updateTimeHoe()`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/FairArena.lua`

```lua
-- 137: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 142: item_id = cost_id
-- 310: function FairArena:getHoeBuyTimes()
-- 403: function FairArena:getEndTime()
-- 404: return xyd.getServerTime() + 10080
-- 496: local start_time = activityData:startTime()
-- 497: local count_time = activityData:getEndTime() - xyd.DAY_TIME
-- 501: if start_time <= xyd.getServerTime() and xyd.getServerTime() < start_time + (data[1] - 1) * xyd.DAY_TIME then
-- 509: local duration = count_time - xyd.getServerTime()
-- 525: local end_show_time = xyd.getServerTime() - count_time
```

### `lua/app/windows/FairArenaAwardPreviewWindow.lua`

```lua
-- 46: local awards = xyd.tables.activityFairArenaLevelTable:getAwards(self.stage)
-- 48: for i = 1, #awards do
-- 49: local award = awards[i]
-- 52: itemID = award[1],
-- 53: num = award[2]
```

### `lua/app/windows/FairArenaAwardWindow.lua`

```lua
-- 47: self.awardItem1 = self.seasonAward:NodeByName("scrollView/seasonAwardItem").gameObject
-- 51: self.awardItem2 = self.treasureAward:NodeByName("scrollView/treasureAwardItem").gameObject
-- 65: duration = activityData:getEndTime() - xyd.getServerTime() - xyd.TimePeriod.DAY_TIME
-- 89: self.select = tonumber(xyd.db.misc:getValue("fair_arena_award_last_select")) or 1
-- 114: local awards = rankTable:getAwardsByRank(self.data.self_rank)
-- 116: for i = 1, #awards do
-- 120: itemID = awards[i][1],
-- 121: num = awards[i][2]
-- 137: self.seasonWrapContent = FixedWrapContent.new(self.scrollView1, wrapContent, self.awardItem1, SeasonAwardItem, self)
-- 150: self.treasureWrapContent = FixedWrapContent.new(self.scrollView2, wrapContent, self.awardItem2, TreasureAwardItem, self)
-- 174: self.awardGroup = go:NodeByName("awardGroup").gameObject
-- 175: self.layout = self.awardGroup:GetComponent(typeof(UILayout))
-- 182: local awards = rankTable:getAwards(self.id)
-- 184: NGUITools.DestroyChildren(self.awardGroup.transform)
-- 186: for i = 1, #awards do
-- 189: uiRoot = self.awardGroup,
-- 190: itemID = awards[i][1],
-- 191: num = awards[i][2],
-- 211: self.awardGroup = go:NodeByName("awardGroup").gameObject
-- 212: self.layout = self.awardGroup:GetComponent(typeof(UILayout))
-- 226: xyd.setUISpriteAsync(self.levelIcon_, nil, "fair_arena_awardbox_icon" .. style)
-- 228: local awards = levelTable:getAwards(self.id)
-- 230: NGUITools.DestroyChildren(self.awardGroup.transform)
-- 232: for i = 1, #awards do
-- 235: uiRoot = self.awardGroup,
-- 236: itemID = awards[i][1],
-- 237: num = awards[i][2],
```

### `lua/app/windows/FairArenaCollectionWindow.lua`

```lua
-- 28: value = xyd.getServerTime()
```

### `lua/app/windows/FairArenaEntryWindow.lua`

```lua
-- 41: self.awardBtn_ = winTrans:NodeByName("awardBtn_").gameObject
-- 53: self.costLabel_ = self.challengeBtn_:ComponentByName("icon_/costLabel_", typeof(UILabel))
-- 69: self.awardBtn_:ComponentByName("button_label", typeof(UILabel)).text = __("FAIR_ARENA_AWARD_PREVIEW")
-- 73: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 76: id = cost_id,
-- 82: if self.activityData:getEndTime() - xyd.getServerTime() <= xyd.DAY_TIME then
-- 117: UIEventListener.Get(self.awardBtn_).onClick = handler(self, function()
-- 118: xyd.WindowManager.get():openWindow("fair_arena_award_window")
-- 136: local leftTime = self.activityData:getEndTime() - xyd.getServerTime()
-- 149: duration = self.activityData:getEndTime() - xyd.getServerTime()
-- 159: local cost_arr = xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")
-- 161: self.costLabel_.text = tostring(cost_arr[2])
-- 164: xyd.setUISpriteAsync(self.challengeIcon_UISprite, nil, "icon_" .. cost_arr[1])
-- 192: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 193: local cost_num = xyd.models.backpack:getItemNumByID(cost_id)
-- 195: if cost_num <= 0 then
-- 263: local start_time = activityData:startTime()
-- 264: local count_time = activityData:getEndTime() - xyd.DAY_TIME
-- 268: if start_time <= xyd.getServerTime() and xyd.getServerTime() < start_time + (data[1] - 1) * xyd.DAY_TIME then
-- 277: local duration = count_time - xyd.getServerTime()
```

### `lua/app/windows/FairArenaExploreWindow.lua`

```lua
-- 62: self.awardIcon_ = winTrans:ComponentByName("awardIcon_", typeof(UISprite))
-- 63: self.awardIconLabel_ = winTrans:ComponentByName("awardIcon_/awardLabel_", typeof(UILabel))
-- 65: self.awardBtn_ = winTrans:NodeByName("awardBtn_").gameObject
-- 89: self.previewBtnLabel1 = self.winGroup:ComponentByName("previewBtn_/awardLabel_", typeof(UILabel))
-- 105: self.previewBtnLabel2 = self.resultGroup:ComponentByName("previewBtn2_/awardLabel_", typeof(UILabel))
-- 161: self.awardBtn_:ComponentByName("button_label", typeof(UILabel)).text = __("FAIR_ARENA_AWARD_PREVIEW")
-- 185: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 188: id = cost_id,
-- 194: if self.activityData:getEndTime() - xyd.getServerTime() <= xyd.DAY_TIME then
-- 244: UIEventListener.Get(self.awardIcon_.gameObject).onClick = handler(self, function()
-- 245: xyd.WindowManager.get():openWindow("fair_arena_award_preview_window", {
-- 252: UIEventListener.Get(self.awardBtn_).onClick = handler(self, function()
-- 253: xyd.WindowManager.get():openWindow("fair_arena_award_window")
-- 274: xyd.WindowManager.get():openWindow("fair_arena_award_preview_window", {
-- 288: xyd.WindowManager.get():openWindow("fair_arena_award_preview_window", {
-- 359: duration = self.activityData:getEndTime() - xyd.getServerTime() - xyd.TimePeriod.DAY_TIME
-- 579: xyd.setUISpriteAsync(self.awardIcon_, nil, "fair_arena_awardbox_icon" .. style1)
-- 580: xyd.setUISpriteAsync(self.previewBtnSprite, nil, "fair_arena_awardbox_icon" .. style2)
-- 581: xyd.setUISpriteAsync(self.previewBtnSprite2, nil, "fair_arena_awardbox_icon" .. style1)
-- 583: self.awardIconLabel_.text = __("FAIR_ARENA_TITLE_GIFT", level)
-- 908: if isCanShowFirstEquipRedPoint and isCanShowFirstEquipRedPoint == "2" and (not timeStamp or timeStamp < self.activityData:startTime() or timeStamp > self.activityData:getEndTime()) then
-- 933: local awards = xyd.tables.activityFairArenaLevelTable:getAwards(level)
-- 936: for i = 1, #awards do
-- 938: item_id = awards[i][1],
-- 939: item_num = awards[i][2]
-- 996: local cost = xyd.tables.miscTable:split2num("fair_arena_explore_replay_price", "value", "#")
-- 1000: message = __("FAIR_ARENA_TIPS_REVIVE_UNLOCK" .. self.type, cost[2]),
-- 1005: local hasNum = xyd.models.backpack:getItemNumByID(cost[1])
-- 1007: if self.type == 1 and hasNum < cost[2] then
-- 1008: xyd.alertTips(__("NOT_ENOUGH", xyd.tables.itemTable:getName(cost[1])))
-- 1032: local cost = xyd.tables.miscTable:split2num("fair_arena_explore_replay_price", "value", "#")
-- 1036: message = __("FAIR_ARENA_TIPS_REVIVE_UNLOCK" .. self.type, cost[2]),
-- 1039: local hasNum = xyd.models.backpack:getItemNumByID(cost[1])
-- 1041: if self.type == 1 and hasNum < cost[2] then
-- 1042: xyd.alertTips(__("NOT_ENOUGH", xyd.tables.itemTable:getName(cost[1])))
-- 1207: if self.activityData:getEndTime() - xyd.getServerTime() > xyd.TimePeriod.DAY_TIME then
```

### `lua/app/windows/FairArenaGetHoeWindow.lua`

```lua
-- 31: self.buyTimesLabel = self.groupAction:ComponentByName("buyTimesLabel", typeof(UILabel))
-- 59: local buy_cost = self:getPrice()
-- 61: xyd.setUISpriteAsync(self.btnSureIcon_UISprite, nil, "icon_" .. buy_cost[1])
-- 63: self.btnSureIconNum.text = tostring(buy_cost[2])
-- 67: local buy_cost = xyd.tables.miscTable:split2Cost("fair_arena_explore_chance_price", "value", "|#", true)
-- 68: local now_times = xyd.models.fairArena:getHoeBuyTimes()
-- 71: if need_times > #buy_cost then
-- 72: need_times = #buy_cost
-- 75: return buy_cost[need_times]
-- 81: local start_time = activityData:startTime()
-- 82: local count_time = activityData:getEndTime() - xyd.DAY_TIME
-- 86: if start_time <= xyd.getServerTime() and xyd.getServerTime() < start_time + (data[1] - 1) * xyd.DAY_TIME then
-- 95: local duration = count_time - xyd.getServerTime()
-- 146: local allCanBuyTimes = math.ceil((xyd.getServerTime() - activityData:startTime()) / xyd.DAY_TIME) * every_day_can_buy_times
-- 147: local yet_buy_tims = allCanBuyTimes - xyd.models.fairArena:getHoeBuyTimes()
-- 154: self.buyTimesLabel.text = __("FAIR_ARENA_GET_HOE_BUY_TIMES_YET") .. yet_buy_tims
-- 160: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 164: id = cost_id
-- 185: local cost_arr = self:getPrice()
-- 187: if xyd.models.backpack:getItemNumByID(cost_arr[1]) >= cost_arr[2] then
-- 190: xyd.alertTips(__("NOT_ENOUGH", xyd.tables.itemTable:getName(cost_arr[1])))
-- 200: if not timeStamp or timeStamp < activityData:startTime() or timeStamp > activityData:getEndTime() then
-- 229: local cost_id = tonumber(xyd.tables.miscTable:split2num("fair_arena_ticket_item", "value", "#")[1])
-- 232: itemID = cost_id,
```

### `lua/app/windows/FairArenaRecordDetailWindow.lua`

```lua
-- 38: self.awardIcon_ = winTrans:ComponentByName("awardIcon_", typeof(UISprite))
-- 39: self.awardLabel_ = winTrans:ComponentByName("awardIcon_/awardLabel_", typeof(UILabel))
-- 69: self.awardLabel_.text = __("FAIR_ARENA_TITLE_GIFT", xyd.tables.activityFairArenaLevelTable:getLevel(self.data.stage))
-- 73: xyd.setUISpriteAsync(self.awardIcon_, nil, "fair_arena_awardbox_icon" .. style)
```

### `lua/app/windows/FairArenaRecordWindow.lua`

```lua
-- 249: xyd.setUISpriteAsync(self.icon_, nil, "fair_arena_awardbox_icon" .. style)
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
