# GrowthDiary — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `getway`: 252 filas; campos: id, name, lv_limit, function_id, stage, go_window, go_params, is_close, close_win_name, lv_hide, need_extra_params
- `growth_diary_mission`: 160 filas; campos: id, desc, type, complete_value, limit, awards, activity_id, getway, chapter_id, chapter_awards, special_mission, single_value

## Mensajes y esquemas de solicitud

- `GET_GROWTH_CHAPTER_AWARDS`: ID 423
- `GET_GROWTH_MISSIONS`: ID 421
- `GET_GROWTH_MISSIONS_AWARDS`: ID 422
- `LOG_PARTNER_DATA_TOUCH`: ID 1770
- `get_growth_chapter_awards_req`: id (campo 1, tipo 5, label 2)
- `get_growth_missions_awards_req`: mission_ids (campo 1, tipo 5, label 3)
- `get_growth_missions_req`: mission_ids (campo 1, tipo 5, label 3)
- `log_partner_data_touch_req`: touch_id (campo 1, tipo 5, label 2), desc (campo 2, tipo 9, label 1)

## Métodos del modelo (líneas de la fuente original)

- Línea 6: `GrowthDiary:ctor()`
- Línea 15: `GrowthDiary:onRegister()`
- Línea 23: `GrowthDiary:reqChapterAward(chapter_id)`
- Línea 31: `GrowthDiary:reqAward(mission_id)`
- Línea 38: `GrowthDiary:reqMissionData(chapter_id)`
- Línea 74: `GrowthDiary:getChapter()`
- Línea 78: `GrowthDiary:clearTime()`
- Línea 82: `GrowthDiary:onGetAwards(event)`
- Línea 94: `GrowthDiary:onGetChapterAwards(event)`
- Línea 119: `GrowthDiary:onGetMissionList(event)`
- Línea 132: `GrowthDiary:updateRedMark()`
- Línea 163: `GrowthDiary:updateChapter()`
- Línea 188: `GrowthDiary:checkFinish()`
- Línea 192: `GrowthDiary:getMissionInfo(mission_id)`
- Línea 196: `GrowthDiary:onRedMarkInfo(event)`
- Línea 213: `GrowthDiary:onLoginInfo(event)`
- Línea 224: `GrowthDiary:checkChapterAwarded(chapter_id)`
- Línea 228: `GrowthDiary:checkCanAward(chapter_id)`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/GrowthDiary.lua`

```lua
-- 10: self.awardsData_ = {}
-- 24: local msg = messages_pb.get_growth_chapter_awards_req()
-- 32: local msg = messages_pb.get_growth_missions_awards_req()
-- 48: is_awarded = 1,
-- 56: if not self.reqTimeList_[chapter_id] or xyd.getServerTime() - self.reqTimeList_[chapter_id] > 30 or xyd.models.redMark:getRedState(xyd.RedMarkType.GROWTH_DIARY) then
-- 66: self.reqTimeList_[chapter_id] = xyd.getServerTime()
-- 88: missionData.is_awarded = 1
-- 97: self.awardsData_[id] = 1
-- 145: if missionData and missionData.is_completed == 1 and missionData.is_awarded ~= 1 then
-- 156: if completeNum >= #ids and self.awardsData_[self.chapter_id] ~= 1 then
-- 166: for index, value in ipairs(self.awardsData_) do
-- 214: self.awardsData_ = {}
-- 216: for index, value in ipairs(event.awards) do
-- 217: self.awardsData_[index] = value
-- 225: return self.awardsData_[chapter_id] == 1
-- 235: if missionData.is_completed == 1 and missionData.is_awarded == 1 then
```

### `lua/app/windows/GrowthDiaryWindow.lua`

```lua
-- 24: self.btnAward_ = itemTrans:NodeByName("awardBtn").gameObject
-- 25: self.btnAwardLabel_ = itemTrans:ComponentByName("awardBtn/label", typeof(UILabel))
-- 26: self.btnAwardMask_ = itemTrans:NodeByName("awardBtn/mask").gameObject
-- 27: self.awardImg_ = itemTrans:ComponentByName("awardImg", typeof(UISprite))
-- 35: self:awardFunction()
-- 54: local is_awarded = self.missionData_.is_awarded == 1
-- 62: self.btnAward_:SetActive(not is_awarded)
-- 74: local awardItem = xyd.tables.grouthDiaryMissionTable:getAward(self.missionID_)
-- 83: itemID = awardItem[1],
-- 84: num = awardItem[2]
-- 87: itemIcon:setChoose(is_awarded)
-- 97: self.btnAwardMask_:SetActive(is_awarded or not isUnlock)
-- 99: xyd.setUISpriteAsync(self.awardImg_, nil, "mission_awarded_" .. xyd.Global.lang)
-- 100: self.awardImg_.gameObject:SetActive(is_awarded)
-- 126: function MissionItem:awardFunction()
-- 129: if self.missionData_.is_awarded ~= 1 and isUnlock then
-- 180: self.awardPart_ = self.contentGroup_:NodeByName("awardPart")
-- 181: self.awardLabel_ = self.awardPart_:ComponentByName("awardLabel", typeof(UILabel))
-- 182: self.itemGrid_ = self.awardPart_:ComponentByName("itemGrid", typeof(UILayout))
-- 183: self.awardBtn_ = self.awardPart_:NodeByName("awardBtn").gameObject
-- 184: self.awardBtnSprite_ = self.awardPart_:ComponentByName("awardBtn", typeof(UISprite))
-- 185: self.awardBtnLabel_ = self.awardPart_:ComponentByName("awardBtn/label", typeof(UILabel))
-- 186: self.awardBtnMask_ = self.awardPart_:NodeByName("awardBtn/mask").gameObject
-- 187: self.aawrdBtnRed_ = self.awardPart_:NodeByName("awardBtn/redPoint").gameObject
-- 188: self.awardTipsLabel_ = self.awardPart_:ComponentByName("tipsLabel", typeof(UILabel))
-- 198: self.awardLabel_.text = __("GROWTH_DIARY_TEXT03")
-- 224: if missionData.is_awarded == 1 then
-- 281: UIEventListener.Get(self.awardBtn_).onClick = function()
-- 305: local awardItem = xyd.tables.grouthDiaryMissionTable:getAward(id)
-- 309: item_id = awardItem[1],
-- 310: item_num = awardItem[2]
-- 351: local awards = xyd.tables.grouthDiaryMissionTable:getChapterAwards(chapter_id)
-- 353: self.awardBtnMask_:SetActive(false)
-- 357: for _, item in ipairs(awards) do
-- 408: local awards = xyd.tables.grouthDiaryMissionTable:getChapterAwards(self.chapter_)
-- 413: for i = 1, #awards do
-- 414: local awardItem = awards[i]
-- 419: itemID = awardItem[1],
-- 420: num = awardItem[2],
-- 430: self.awardBtnSprite_.color = Color.New2(4294967295)
-- 431: self.awardBtn_:GetComponent(typeof(UnityEngine.BoxCollider)).enabled = true
-- 432: self.awardBtn_:GetComponent(typeof(UIButtonScale)).enabled = true
-- 433: self.awardBtnLabel_.text = __("GROWTH_DIARY_TEXT12")
-- 434: self.awardBtnLabel_.color = Color.New2(4278124287)
-- 435: self.awardBtnLabel_.effectStyle = UILabel.Effect.Outline8
-- 436: self.awardBtnLabel_.effectColor = Color.New2(1012112383)
-- 438: self.awardBtnMask_:SetActive(false)
-- 441: self.awardBtnLabel_.text = __("GROWTH_DIARY_TEXT12")
-- 442: self.awardBtnSprite_.color = Color.New2(4294967295)
-- 443: self.awardBtn_:GetComponent(typeof(UnityEngine.BoxCollider)).enabled = true
-- 444: self.awardBtn_:GetComponent(typeof(UIButtonScale)).enabled = false
-- 445: self.awardBtnLabel_.color = Color.New2(4278124287)
-- 446: self.awardBtnLabel_.effectStyle = UILabel.Effect.Outline8
-- 447: self.awardBtnLabel_.effectColor = Color.New2(1012112383)
-- 449: self.awardBtnMask_:SetActive(true)
-- 451: self.awardBtnSprite_.color = Color.New2(255)
-- 452: self.awardBtn_:GetComponent(typeof(UnityEngine.BoxCollider)).enabled = true
-- 453: self.awardBtn_:GetComponent(typeof(UIButtonScale)).enabled = false
-- 454: self.awardBtnLabel_.text = __("GROWTH_DIARY_TEXT11")
-- 455: self.awardBtnLabel_.color = Color.New2(4294967295)
-- 456: self.awardBtnLabel_.effectStyle = UILabel.Effect.Outline8
-- 457: self.awardBtnLabel_.effectColor = Color.New2(1414812927)
-- 459: self.awardBtnMask_:SetActive(false)
-- 463: self.awardBtnLabel_.text = __("GROWTH_DIARY_TEXT10")
-- 467: self.awardBtn_:GetComponent(typeof(UnityEngine.BoxCollider)).enabled = false
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
