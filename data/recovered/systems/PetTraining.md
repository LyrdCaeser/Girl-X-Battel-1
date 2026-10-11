# PetTraining — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `misc`: 1332 filas; campos: key, value, desc
- `pet`: 9 filas; campos: id, name, name2, ver, max_grade, max_lv, max_exlevel, active_cost, grade_lv2, grade_exp2, grade_lv3, grade_exp3, grade_lv4, grade_exp4, act_skill_id, pas_skill1_id, pas_skill2_id, pas_skill3_id, pas_skill4_id, exskill_id, pas_tier1, pas_tier2, pas_tier3, pas_tier4, pas_skills, pas_skill_exlevel, pet_card_bg, pet_bg, pet_model, pet_avatar, is_open, pet_frame, pet_frame_group, is_show, training_xy, training_scale, pet_battle_avatar
- `pet_training`: 10 filas; campos: id, exp
- `pet_training_boss`: 10 filas; campos: id, level, battle_awards, final_awards, hp
- `pet_training_lesson`: 15 filas; campos: id, name, level, awards, time, rank_unlocked
- `pet_training_lesson_text`: sin datos resueltos
- `pet_training_new_awards`: 10 filas; campos: id, awards1, awards2, time, desc
- `pet_training_text`: sin datos resueltos

## Mensajes y esquemas de solicitud

- `PET_TRAINING_BUY_TIMES`: ID 1598
- `PET_TRAINING_CANCEL_MISSION`: ID 1595
- `PET_TRAINING_COMPLETE_MISSION`: ID 1594
- `PET_TRAINING_FIGHT`: ID 1597
- `PET_TRAINING_GET_AWARD`: ID 1611
- `PET_TRAINING_GET_INFO`: ID 1592
- `PET_TRAINING_SELECT_BOSS`: ID 1596
- `PET_TRAINING_START_MISSION`: ID 1593
- `pet_training_buy_times_req`: pet_id (campo 1, tipo 5, label 2)
- `pet_training_cancel_mission_req`: id (campo 1, tipo 5, label 2)
- `pet_training_complete_mission_req`: id (campo 1, tipo 5, label 2)
- `pet_training_fight_req`: pet_id (campo 1, tipo 5, label 2), pet_ids (campo 2, tipo 5, label 3)
- `pet_training_get_award_req`:
- `pet_training_get_info_req`:
- `pet_training_select_boss_req`: boss_id (campo 1, tipo 5, label 2)
- `pet_training_start_mission_req`: id (campo 1, tipo 5, label 2), mission_id (campo 2, tipo 5, label 2), pets (campo 3, tipo 5, label 3)

## Métodos del modelo (líneas de la fuente original)

- Línea 7: `PetTraining:ctor()`
- Línea 17: `PetTraining:reset()`
- Línea 25: `PetTraining:onRegister()`
- Línea 38: `PetTraining:onGetPetTrainingInfo(event)`
- Línea 59: `PetTraining:setRedMark()`
- Línea 63: `PetTraining:getRedMarkStatus()`
- Línea 82: `PetTraining:onFight(event)`
- Línea 91: `PetTraining:onSelectBoss(event)`
- Línea 98: `PetTraining:onBuyTimes(event)`
- Línea 106: `PetTraining:onStartMission(event)`
- Línea 116: `PetTraining:onCancelMission(event)`
- Línea 124: `PetTraining:onCompleteMission(event)`
- Línea 134: `PetTraining:getMissionNum()`
- Línea 158: `PetTraining:getHangTime()`
- Línea 162: `PetTraining:getBattleTimes()`
- Línea 166: `PetTraining:getPetBattleTimes()`
- Línea 170: `PetTraining:getBuyTimeTimes()`
- Línea 174: `PetTraining:getBossID()`
- Línea 178: `PetTraining:getBossHp()`
- Línea 182: `PetTraining:getMissionInfo(pos)`
- Línea 213: `PetTraining:cleanTempMission(pos)`
- Línea 218: `PetTraining:saveTempMission(pos)`
- Línea 240: `PetTraining:startTempMission()`
- Línea 252: `PetTraining:isMissionRun(tableId, pos)`
- Línea 262: `PetTraining:getMissionPets()`
- Línea 276: `PetTraining:onPetLevUp(event)`
- Línea 291: `PetTraining:onGetTrainingAward(event)`
- Línea 297: `PetTraining:isTrainOpen()`
- Línea 303: `PetTraining:getTrainingLevel()`
- Línea 334: `PetTraining:fight(id)`
- Línea 342: `PetTraining:selectBoss(id)`
- Línea 350: `PetTraining:buyTimes(id)`
- Línea 358: `PetTraining:startMission(missionId, pos, pets)`
- Línea 371: `PetTraining:cancelMission(missionId, pos)`
- Línea 379: `PetTraining:completeMission(pos)`
- Línea 387: `PetTraining:reqTrainingInfo()`
- Línea 393: `PetTraining:reqTrainingAward()`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/PetTraining.lua`

```lua
-- 30: self:registerEvent(xyd.event.PET_TRAINING_BUY_TIMES, handler(self, self.onBuyTimes))
-- 66: local hangStartTime = self:getHangTime()
-- 68: if hangStartTime == 0 then
-- 72: local nowTime = xyd.getServerTime(true)
-- 75: if maxHangTime <= nowTime - hangStartTime then
-- 98: function PetTraining:onBuyTimes(event)
-- 144: local startTime = missionInfo.start_time
-- 146: local nowTime = xyd.getServerTime()
-- 147: local duration = nowTime - startTime
-- 202: missionData.startTime = mission.start_time
-- 350: function PetTraining:buyTimes(id)
-- 394: local msg = messages_pb.pet_training_get_award_req()
```

### `lua/app/windows/PetTrainingBossAwardWindow.lua`

```lua
-- 24: self.awardContainer = go:NodeByName("bGroup/e:Scroller/awardContainer").gameObject
-- 55: local awardsDataList = xyd.tables.petTrainingBossTable:getBattleAwards(1)
-- 57: for i = 1, #awardsDataList do
-- 58: local itemData = awardsDataList[i]
-- 76: local awardsData = xyd.tables.petTrainingBossTable:getFinalAwards(ids[i])
-- 77: local go = NGUITools.AddChild(self.awardContainer, self.item)
-- 78: local awardItem = PetTrainingBossKillAwardItem.new(go, {
-- 79: awardsData = awardsData,
-- 85: self.awardContainer:GetComponent(typeof(UILayout)):Reposition()
-- 91: self.awardsData = params.awardsData
-- 112: for i = 1, #self.awardsData do
-- 113: local itemData = self.awardsData[i]
```

### `lua/app/windows/PetTrainingDetail1Window.lua`

```lua
-- 47: local levExtraDatas = xyd.tables.miscTable:split2Cost("pet_training_hangup_awards2_coefficient", "value", "|#")
```

### `lua/app/windows/PetTrainingDetail2Window.lua`

```lua
-- 71: local award1 = xyd.tables.petTrainingNewAwardsTable:getAward(id, 2)
-- 73: label2.text = award1[2]
-- 79: local award2 = xyd.tables.petTrainingNewAwardsTable:getAward(id, 1)
-- 81: label3.text = award2[2]
```

### `lua/app/windows/PetTrainingDetailWindow.lua`

```lua
-- 40: local awardItem = PetTrainingDetailItem.new(go, {
```

### `lua/app/windows/PetTrainingLessonDetailWindow.lua`

```lua
-- 113: self.awardGroup_ = self.content_:NodeByName("awardGroup").gameObject
-- 181: local awards = xyd.tables.petTrainingLessonTable:getAwards(self.missionID)
-- 184: NGUITools.DestroyChildren(self.awardGroup_.transform)
-- 196: local extraDatas = xyd.tables.miscTable:split2Cost("pet_training_lesson_award", "value", "|#")
-- 208: for _, award in ipairs(awards) do
-- 209: local itemId = award[1]
-- 210: local itemNum = math.floor(award[2] * extraRate)
-- 215: uiRoot = self.awardGroup_
-- 219: self.awardGroup_:GetComponent(typeof(UIGrid)):Reposition()
```

### `lua/app/windows/PetTrainingLessonWindow.lua`

```lua
-- 48: local awards = xyd.tables.petTrainingLessonTable:getAwards(self.id)
-- 50: for _, award in ipairs(awards) do
-- 53: itemID = award[1],
-- 54: num = award[2],
```

### `lua/app/windows/PetTrainingWindow.lua`

```lua
-- 31: self.awardBtn = self.topActionGroup:NodeByName("awardBtn").gameObject
-- 32: self.awardRedPoint = self.topActionGroup:ComponentByName("awardBtn/redPoint", typeof(UISprite))
-- 34: self.awardGroup1 = self.topActionGroup:NodeByName("award_group_1").gameObject
-- 35: self.awardGroup2 = self.topActionGroup:NodeByName("award_group_2").gameObject
-- 56: self.bossAwardBtn = self.bossGroup:NodeByName("awardBtn").gameObject
-- 108: if xyd.tables.miscTable:getNumber("pet_training_boss_limit", "value") - self.petTrainingModel:getBattleTimes() > 0 then
-- 109: self.timesLabel.text = __("PET_TRAINING_TEXT13", xyd.tables.miscTable:getNumber("pet_training_boss_limit", "value") - self.petTrainingModel:getBattleTimes())
-- 110: elseif self.petTrainingModel:getBuyTimeTimes() < xyd.tables.miscTable:getNumber("pet_training_energy_buy_limit", "value") then
-- 318: UIEventListener.Get(self.awardBtn).onClick = function()
-- 338: if xyd.tables.miscTable:getNumber("pet_training_boss_limit", "value") - self.petTrainingModel:getBattleTimes() > 0 then
-- 349: elseif self.petTrainingModel:getBuyTimeTimes() < xyd.tables.miscTable:getNumber("pet_training_energy_buy_limit", "value") then
-- 369: xyd.openWindow("pet_training_boss_award_window")
-- 372: if self.petTrainingModel:getBuyTimeTimes() >= xyd.tables.miscTable:getNumber("pet_training_energy_buy_limit", "value") then
-- 373: xyd.showToast(__("PET_TRAINING_TEXT18", xyd.tables.miscTable:getNumber("pet_training_energy_buy_limit", "value")))
-- 375: xyd.alert(xyd.AlertType.YES_NO, __("PET_TRAINING_TEXT19", xyd.tables.miscTable:split2Cost("pet_training_energy_buy_cost", "value", "|#")[self.petTrainingModel:getBuyTimeTimes() + 1][2]), function(yes)
-- 377: self.petTrainingModel:buyTimes(self.chosenPet:getPetID())
-- 391: self.awardBtn = self.topActionGroup:NodeByName("awardBtn").gameObject
-- 393: local awardBtnLabel = self.awardBtn:ComponentByName("btn_label", typeof(UILabel))
-- 395: awardBtnLabel.text = __("ACTIVITY_GROWTH_PLAN_TEXT07")
-- 401: local levExtraDatas = xyd.tables.miscTable:split2Cost("pet_training_hangup_awards2_coefficient", "value", "|#")
-- 417: local hangStartTime = self.petTrainingModel:getHangTime()
-- 418: local nowTime = xyd.getServerTime(true)
-- 420: self.hangTime = math.min(nowTime - hangStartTime, maxHangTime)
-- 430: self.awardRedPoint:SetActive(false)
-- 438: self.awardRedPoint:SetActive(true)
-- 448: self.awardIcon1 = self:initHangAward(1, self.hangTime, extraNum, cycleTime)
-- 449: self.awardIcon2 = self:initHangAward(2, self.hangTime, extraNum, cycleTime)
-- 458: self.awardRedPoint:SetActive(true)
-- 461: self.awardIcon1 = self:initHangAward(1, self.hangTime, extraNum, cycleTime)
-- 462: self.awardIcon2 = self:initHangAward(2, self.hangTime, extraNum, cycleTime)
-- 466: local awards = xyd.tables.petTrainingNewAwardsTable:getAward(self.level, pos)
-- 467: local awardNum = math.floor(awards[2] * math.floor(hangTime / cycleTime) * extraNum)
-- 471: itemID = awards[1],
-- 472: num = awardNum
-- 476: if self["awardIcon" .. pos] then
-- 477: icon = self["awardIcon" .. pos]
-- 481: iconParams.uiRoot = self["awardGroup" .. pos]
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
