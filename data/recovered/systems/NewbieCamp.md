# NewbieCamp — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `beginner_quest`: 33 filas; campos: id, phase_id, rank, limit_phase, limit_lev, desc, note, type, complete_value, award, is_hide, lv_limit, go_window, go_params
- `beginner_quest_board`: 3 filas; campos: id, next_id, award, unlock_lev
- `beginner_quest_text`: sin datos resueltos
- `window`: 1007 filas; campos: name, class, resource, window_name, layer_type, hide_type, back_type, background, open_sound, open_animation, close_animation, bottom_btn_status, back_close, show_res_loading, res_loading_delay, show_scene, record_id, win_name, img_guide, animation_part, stack_type, bgs_sound

## Mensajes y esquemas de solicitud

- `GET_ROOKIE_MISSION_AWARD`: ID 419
- `GET_ROOKIE_MISSION_LIST`: ID 418
- `get_rookie_mission_award_req`: mission_id (campo 1, tipo 5, label 2)
- `get_rookie_mission_list_req`:

## Métodos del modelo (líneas de la fuente original)

- Línea 6: `NewbieCamp:ctor()`
- Línea 18: `NewbieCamp:onRegister()`
- Línea 23: `NewbieCamp:onGetMissionList(event)`
- Línea 28: `NewbieCamp:onGetMissionAward(event)`
- Línea 33: `NewbieCamp:reqData()`
- Línea 39: `NewbieCamp:reqAward(mission_id)`
- Línea 47: `NewbieCamp:onGetData(event)`
- Línea 106: `NewbieCamp:sortList()`
- Línea 130: `NewbieCamp:reqLostAward()`
- Línea 143: `NewbieCamp:onGetAward(event)`
- Línea 203: `NewbieCamp:alertItems(id)`
- Línea 219: `NewbieCamp:getAwardInfo()`
- Línea 223: `NewbieCamp:getStructureDataByPhase(phase_id)`
- Línea 227: `NewbieCamp:getCountByPhase(phase_id)`
- Línea 231: `NewbieCamp:checkCompletPhase(phase_id)`
- Línea 237: `NewbieCamp:checkLockByPhase(phase_id)`
- Línea 254: `NewbieCamp:checkAllAwardByPhase(phase_id)`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/NewbieCamp.lua`

```lua
-- 13: self.award_final_ = {}
-- 40: local msg = messages_pb.get_rookie_mission_award_req()
-- 74: if tonumber(data.is_awarded) == 1 then
-- 93: self.award_final_[data.mission_id] = true
-- 146: self.award_final_[id] = true
-- 196: if mission_id and not self.award_final_[mission_id] then
-- 220: return self.award_final_
-- 238: local limit_lev = xyd.tables.newbieCampBoardTable:getUnlockLev(phase_id)
-- 241: if limit_lev <= cur_lev then
-- 245: local limit_phase = phase_id - 1
-- 247: if limit_phase > 0 then
```

### `lua/app/windows/NewbieCampListWindow.lua`

```lua
-- 36: self.awardItems_ = goTrans:ComponentByName("awardItems", typeof(UIGrid))
-- 37: self.awradLabel_ = goTrans:ComponentByName("awardLabel", typeof(UILabel))
-- 63: local award = xyd.tables.newbieCampBoardTable:getAward(self.phase_id_)
-- 71: for i = 1, #award do
-- 72: local data = award[i]
-- 75: uiRoot = self.awardItems_.gameObject,
-- 83: self.awardItems_:Reposition()
-- 151: local award = xyd.tables.newbieCampTable:getAward(self.id_)
-- 159: for i = 1, #award do
-- 160: local data = award[i]
-- 178: xyd.setUISpriteAsync(self.imgAward_, nil, "mission_awarded_" .. tostring(xyd.Global.lang))
-- 184: local limit_params = xyd.tables.newbieCampTable:getGoLimit(self.id_)
-- 185: local level_limit = limit_params[1]
-- 186: local vip_limit = limit_params[2]
-- 188: if level_limit and #limit_params == 1 and level_limit > xyd.models.backpack:getLev() then
-- 189: xyd.alertTips(__("FUNC_OPEN_LEV", level_limit))
-- 192: elseif level_limit and level_limit > xyd.models.backpack:getLev() and vip_limit > xyd.models.backpack:getVipLev() then
-- 193: xyd.alertTips(__("GAMBLE_DOOR_TIPS", level_limit, vip_limit))
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
