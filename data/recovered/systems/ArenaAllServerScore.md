# ArenaAllServerScore — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `arena_all_server_mission`: 6 filas; campos: id, type, desc, complete, awards, limit
- `arena_all_server_rank`: 22 filas; campos: id, desc, level, level_num, point, season_awards, front_num, back_num, pet_num, hide_num, inherit_point
- `misc`: 1332 filas; campos: key, value, desc

## Mensajes y esquemas de solicitud

- `ARENA_ALL_SERVER_GET_ENEMY_INFO_NEW`: ID 1863
- `ARENA_ALL_SERVER_GET_REPORT`: ID 1862
- `ARENA_ALL_SERVER_RECORD`: ID 1861
- `GET_ALL_SEVER_FIGHT`: ID 1860
- `GET_ARENA_ALL_SERVER_INFO`: ID 1856
- `GET_MATCH_ALL_SEVER_INFOS`: ID 1859
- `GET_RANK_ALL_SERVER_LIST`: ID 1858
- `REFRESH_MATCH_INFOS`: ID 1865
- `SET_PARTNERS_ALL_SERVER`: ID 1857
- `arena_all_server_get_enemy_info_new_req`: other_player_id (campo 1, tipo 5, label 2)
- `arena_all_server_get_report_req`: record_ids (campo 1, tipo 5, label 3)
- `arena_all_server_record_req`:
- `fight_partner`: partner_id (campo 1, tipo 5, label 2), pos (campo 2, tipo 5, label 2)
- `get_all_sever_fight_req`: enemy_id (campo 1, tipo 5, label 2), partners (campo 2, tipo 11, label 3), front_prs (campo 3, tipo 5, label 3), back_prs (campo 4, tipo 5, label 3), pet_ids (campo 5, tipo 5, label 3), is_revenge (campo 6, tipo 5, label 1), table_id (campo 7, tipo 5, label 2)
- `get_arena_all_server_info_req`:
- `get_match_all_sever_infos_req`:
- `get_rank_all_server_list_req`: level (campo 1, tipo 5, label 2)
- `set_partners_all_server_req`: partners (campo 1, tipo 11, label 3), front_prs (campo 2, tipo 5, label 3), back_prs (campo 3, tipo 5, label 3), pet_ids (campo 4, tipo 5, label 3)

## Métodos del modelo (líneas de la fuente original)

- Línea 5: `ArenaAllServerScore:ctor()`
- Línea 28: `ArenaAllServerScore:onRegister()`
- Línea 39: `ArenaAllServerScore:onGetArenaInfo(event)`
- Línea 51: `ArenaAllServerScore:checkNoInfo()`
- Línea 59: `ArenaAllServerScore:getPower()`
- Línea 67: `ArenaAllServerScore:getStartTime()`
- Línea 77: `ArenaAllServerScore:getRank()`
- Línea 85: `ArenaAllServerScore:getRankType()`
- Línea 92: `ArenaAllServerScore:getRefreshTime()`
- Línea 96: `ArenaAllServerScore:getCanRefreshNum()`
- Línea 100: `ArenaAllServerScore:reqRankList(rankType)`
- Línea 111: `ArenaAllServerScore:getReqRankTime(rankType)`
- Línea 115: `ArenaAllServerScore:onGetRankList(event)`
- Línea 120: `ArenaAllServerScore:getRankList(rankType)`
- Línea 124: `ArenaAllServerScore:getDefFormation()`
- Línea 128: `ArenaAllServerScore:getScore()`
- Línea 136: `ArenaAllServerScore:getMissionCompletes()`
- Línea 140: `ArenaAllServerScore:getMissionValues()`
- Línea 144: `ArenaAllServerScore:getAwards()`
- Línea 148: `ArenaAllServerScore:getRankLevel()`
- Línea 155: `ArenaAllServerScore:getDDL()`
- Línea 161: `ArenaAllServerScore:getOpenTime()`
- Línea 167: `ArenaAllServerScore:isInOpentime()`
- Línea 177: `ArenaAllServerScore:reqSetTeams(partnerParams, petIDs)`
- Línea 231: `ArenaAllServerScore:checkDefFormation()`
- Línea 283: `ArenaAllServerScore:reqFight(partnerParams, petIDs, enemy_id, enemy_level, is_revenge)`
- Línea 350: `ArenaAllServerScore:onAreanAsFight(event)`
- Línea 383: `ArenaAllServerScore:getFightCost()`
- Línea 395: `ArenaAllServerScore:onSetTeams(event)`
- Línea 416: `ArenaAllServerScore:updateFormation(teams)`
- Línea 422: `ArenaAllServerScore:updateLock(teams)`
- Línea 480: `ArenaAllServerScore:reqEnemyList()`
- Línea 503: `ArenaAllServerScore:refreshEnemyList()`
- Línea 509: `ArenaAllServerScore:onGetEnemyList(event)`
- Línea 534: `ArenaAllServerScore:onRefreshEnemyList(event)`
- Línea 562: `ArenaAllServerScore:removePlayerInEnemyList(enemyInfo)`
- Línea 578: `ArenaAllServerScore:getEnemyList()`
- Línea 586: `ArenaAllServerScore:reqEnemyInfo(player_id)`
- Línea 594: `ArenaAllServerScore:checkMissionValue()`
- Línea 632: `ArenaAllServerScore:updateDefendRed()`
- Línea 665: `ArenaAllServerScore:setSkipReport(flag)`
- Línea 676: `ArenaAllServerScore:isSkipReport()`
- Línea 680: `ArenaAllServerScore:getTmpReports()`
- Línea 684: `ArenaAllServerScore:updateBaseInfo()`
- Línea 694: `ArenaAllServerScore:checkFunctionOpen()`
- Línea 702: `ArenaAllServerScore:setTmpReports(data)`
- Línea 707: `ArenaAllServerScore:resetTmpReports()`
- Línea 713: `ArenaAllServerScore:getRecordId()`
- Línea 717: `ArenaAllServerScore:updateRank(rank)`
- Línea 722: `ArenaAllServerScore:updateScore(score)`
- Línea 726: `ArenaAllServerScore:getNextReport()`
- Línea 736: `ArenaAllServerScore:isLastReport()`
- Línea 744: `ArenaAllServerScore:checkInfoOtherDay()`
- Línea 756: `ArenaAllServerScore:onGetMissionAwardBack(event)`
- Línea 773: `ArenaAllServerScore:reqRecord()`
- Línea 779: `ArenaAllServerScore:reqReport(ids)`
- Línea 789: `ArenaAllServerScore:getBattleAddRank()`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/ArenaAllServerScore.lua`

```lua
-- 46: value = xyd.getServerTime()
-- 67: function ArenaAllServerScore:getStartTime()
-- 69: local startTime_ = self.info_.start_time
-- 71: return startTime_
-- 108: self.reqTimeList[rankType] = xyd.getServerTime()
-- 145: return self.info_.awards
-- 156: local startTime = self:getStartTime()
-- 158: return startTime + 19 * xyd.DAY_TIME
-- 162: local startTime = self:getStartTime()
-- 164: return startTime - 1 * xyd.DAY_TIME
-- 168: local serverTime = xyd.getServerTime()
-- 170: if serverTime >= self:getOpenTime() and serverTime <= self:getDDL() then
-- 384: local fightCostList = xyd.tables.miscTable:split2Cost("arena_all_server_cost", "value", "|#")
-- 424: local numTime = xyd.getServerTime() - self:getStartTime()
-- 481: if xyd.getServerTime() - self:getRefreshTime() > xyd.HOUR or self.needGetList_ then
-- 486: self.info_.refresh_time = xyd.getServerTime()
-- 535: self.info_.refresh_time = xyd.getServerTime()
-- 603: if not arena_all_server_score_mission_time_show or arena_all_server_score_mission_time_show and not xyd.isSameDay(tonumber(xyd.getServerTime()), tonumber(arena_all_server_score_mission_time_show)) then
-- 634: local startTime = self:getStartTime()
-- 640: if xyd.getServerTime() < startTime - xyd.DAY_TIME or xyd.getServerTime() > startTime + 19 * xyd.DAY_TIME then
-- 658: if self.defFormation and self.defFormation.partners and #self.defFormation.partners > 0 and self:getDDL() - xyd.getServerTime() < xyd.DAY_TIME * 3 and self:getDDL() - xyd.getServerTime() > xyd.DAY_TIME then
-- 747: if getTime and not xyd.isSameDay(getTime, xyd.getServerTime()) then
-- 758: local common_progress_award_window_wd = xyd.WindowManager.get():getWindow("common_progress_award_window")
-- 760: if common_progress_award_window_wd and common_progress_award_window_wd:getWndType() == xyd.CommonProgressAwardWindowType.ARENA_ALL_SERVER_SCORE_MISSION_WINDOW then
-- 764: common_progress_award_window_wd:updateItemState(table_id, 3)
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
