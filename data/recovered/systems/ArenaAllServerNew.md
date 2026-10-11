# ArenaAllServerNew — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `arena_all_server_rank`: 22 filas; campos: id, desc, level, level_num, point, season_awards, front_num, back_num, pet_num, hide_num, inherit_point
- `misc`: 1332 filas; campos: key, value, desc

## Mensajes y esquemas de solicitud

- `ARENA_ALL_SERVER_BET_NEW`: ID 1867
- `ARENA_ALL_SERVER_CHANGE_BET_NEW`: ID 1875
- `ARENA_ALL_SERVER_GET_ALL_BATTLE_INFO_NEW`: ID 1869
- `ARENA_ALL_SERVER_GET_ENEMY_INFO_NEW2`: ID 1874
- `ARENA_ALL_SERVER_GET_HALL_AWARD_NEW`: ID 1871
- `ARENA_ALL_SERVER_GET_HALL_RANK_NEW`: ID 1872
- `ARENA_ALL_SERVER_GET_HISTORY_RANK_NEW`: ID 1870
- `ARENA_ALL_SERVER_GET_RECORD_NEW2`: ID 1878
- `ARENA_ALL_SERVER_GET_RED_INFO`: ID 1876
- `ARENA_ALL_SERVER_GET_SELF_INFO_NEW`: ID 1868
- `ARENA_ALL_SERVER_SET_TEAMS_NEW`: ID 1866
- `arena_all_server_bet_new_req`: round (campo 1, tipo 5, label 2), win_player_id (campo 2, tipo 5, label 2), zone (campo 3, tipo 5, label 2)
- `arena_all_server_change_bet_new_req`: round (campo 1, tipo 5, label 2), win_player_id (campo 2, tipo 5, label 2), zone (campo 3, tipo 5, label 2)
- `arena_all_server_get_all_battle_info_new_req`: zone (campo 1, tipo 5, label 2)
- `arena_all_server_get_enemy_info_new2_req`: other_player_id (campo 1, tipo 5, label 2), zone (campo 2, tipo 5, label 2)
- `arena_all_server_get_hall_award_new_req`: id (campo 1, tipo 5, label 2)
- `arena_all_server_get_hall_rank_new_req`:
- `arena_all_server_get_history_rank_new_req`: head (campo 1, tipo 5, label 1), tail (campo 2, tipo 5, label 1)
- `arena_all_server_get_record_new2_req`: record_ids (campo 1, tipo 5, label 3)
- `arena_all_server_get_red_info_req`:
- `arena_all_server_get_self_info_new_req`:
- `arena_all_server_set_teams_new_req`: partners (campo 1, tipo 11, label 3), front_prs (campo 2, tipo 5, label 3), back_prs (campo 3, tipo 5, label 3), pet_ids (campo 4, tipo 5, label 3), zone (campo 5, tipo 5, label 2)
- `fight_partner`: partner_id (campo 1, tipo 5, label 2), pos (campo 2, tipo 5, label 2)

## Métodos del modelo (líneas de la fuente original)

- Línea 7: `ArenaAllServerNew:ctor()`
- Línea 25: `ArenaAllServerNew:onRegister()`
- Línea 46: `ArenaAllServerNew:reqRedInfo()`
- Línea 52: `ArenaAllServerNew:onGetRedInfo(event)`
- Línea 58: `ArenaAllServerNew:getCurRound()`
- Línea 66: `ArenaAllServerNew:updateRedMark()`
- Línea 74: `ArenaAllServerNew:checkFunctionOpen()`
- Línea 82: `ArenaAllServerNew:getStartTime()`
- Línea 86: `ArenaAllServerNew:isSelect()`
- Línea 90: `ArenaAllServerNew:checkOpen()`
- Línea 100: `ArenaAllServerNew:getCurBattleType()`
- Línea 112: `ArenaAllServerNew:getFinalTimeGroup()`
- Línea 124: `ArenaAllServerNew:checkNeedUpdateInfo(nextTime)`
- Línea 135: `ArenaAllServerNew:reqSelfInfo()`
- Línea 149: `ArenaAllServerNew:onGetArenaInfo(event)`
- Línea 169: `ArenaAllServerNew:getZoneNum()`
- Línea 173: `ArenaAllServerNew:updateFormation(teams)`
- Línea 179: `ArenaAllServerNew:updateLock(teams)`
- Línea 229: `ArenaAllServerNew:isSetDefend()`
- Línea 239: `ArenaAllServerNew:getCurMatchNum()`
- Línea 248: `ArenaAllServerNew:getZoneID()`
- Línea 252: `ArenaAllServerNew:reqBattleInfo(zone_id)`
- Línea 270: `ArenaAllServerNew:onGetArenaBattleInfo(event)`
- Línea 280: `ArenaAllServerNew:changeStringKey(tableArry)`
- Línea 290: `ArenaAllServerNew:reqQuiz(playerID, zone_id)`
- Línea 303: `ArenaAllServerNew:onQuiz(event)`
- Línea 322: `ArenaAllServerNew:reqChangeQuiz(playerID, zone_id)`
- Línea 336: `ArenaAllServerNew:getCurRoundBetInfo()`
- Línea 342: `ArenaAllServerNew:getBetInfoByRound(roundID)`
- Línea 348: `ArenaAllServerNew:getBetInfo()`
- Línea 352: `ArenaAllServerNew:getBattleInfo()`
- Línea 356: `ArenaAllServerNew:reqGetAward(id)`
- Línea 364: `ArenaAllServerNew:onGetAward(event)`
- Línea 368: `ArenaAllServerNew:onGetRank(event)`
- Línea 398: `ArenaAllServerNew:onSetTeams(event)`
- Línea 409: `ArenaAllServerNew:reqSetTeams(partnerParams, petIDs, levelID)`
- Línea 460: `ArenaAllServerNew:reqGetHallRank()`
- Línea 466: `ArenaAllServerNew:onGetHallRank(event)`
- Línea 472: `ArenaAllServerNew:reqGetHistoryRank(head, tail)`
- Línea 492: `ArenaAllServerNew:hasReqHistory(season)`
- Línea 496: `ArenaAllServerNew:getHistoryRank()`
- Línea 500: `ArenaAllServerNew:getSeasons()`
- Línea 512: `ArenaAllServerNew:getMaxHistorySeason()`
- Línea 527: `ArenaAllServerNew:reqReport(ids)`
- Línea 551: `ArenaAllServerNew:onGetReport(event)`
- Línea 564: `ArenaAllServerNew:getHallRank()`
- Línea 568: `ArenaAllServerNew:reqEnemyInfo(player_id, zone_id)`
- Línea 579: `ArenaAllServerNew:getScoreID()`
- Línea 587: `ArenaAllServerNew:getPickPlayers()`
- Línea 595: `ArenaAllServerNew:getBattleInfo(zone_id)`
- Línea 601: `ArenaAllServerNew:getRounds(zone_id)`
- Línea 607: `ArenaAllServerNew:getBattlePlayerInfos(zone_id)`
- Línea 613: `ArenaAllServerNew:getBattlePlayerInfo(playerID, zone_id)`
- Línea 630: `ArenaAllServerNew:getSupportNumByPlayerID(playerID)`
- Línea 634: `ArenaAllServerNew:getPickSupportRate()`
- Línea 660: `ArenaAllServerNew:getNextFightTime()`
- Línea 664: `ArenaAllServerNew:isRestTime()`
- Línea 672: `ArenaAllServerNew:checkAlive(playerID, zone_id)`
- Línea 690: `ArenaAllServerNew:getReportIds(round, winPlayerID, zone_id)`
- Línea 716: `ArenaAllServerNew:getTimeStr(index, isShowEndYear)`
- Línea 735: `ArenaAllServerNew:getDefFormation()`
- Línea 739: `ArenaAllServerNew:getGroupFightRecords()`
- Línea 747: `ArenaAllServerNew:getSelfFightRecords()`
- Línea 812: `ArenaAllServerNew:checkChangeTime()`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/ArenaAllServerNew.lua`

```lua
-- 10: self.startTime = 0
-- 82: function ArenaAllServerNew:getStartTime()
-- 91: local startTime = self:getStartTime() or 0
-- 93: if xyd.getServerTime() - startTime >= xyd.DAY_TIME * 20 and xyd.getServerTime() - startTime < xyd.DAY_TIME * 26 then
-- 113: local startTime = self:getStartTime()
-- 115: if xyd.getServerTime() - startTime >= 20 * xyd.DAY_TIME and xyd.getServerTime() - startTime < 23 * xyd.DAY_TIME then
-- 117: elseif xyd.getServerTime() - startTime >= 23 * xyd.DAY_TIME and xyd.getServerTime() - startTime < 26 * xyd.DAY_TIME then
-- 126: local serverTime = xyd.getServerTime()
-- 128: if nextTime < serverTime then
-- 156: self.nextUpdateSelfInfoTime_ = xyd.getServerTime() + xyd.getUpdateTime()
-- 164: if not self.battleInfosList_[self.zone_] and xyd.getServerTime() - self:getStartTime() > 20 * xyd.DAY_TIME then
-- 181: local numTime = xyd.getServerTime() - self:getStartTime()
-- 241: local serverTime = xyd.getServerTime()
-- 243: local num = math.floor((serverTime - firstTime) / onceTime) + 1
-- 275: self.nextUpdateBattleInfoTime_ = xyd.getServerTime() + xyd.getUpdateTime()
-- 331: self.lastChangeTime = xyd.getServerTime()
-- 357: local msg = messages_pb.arena_all_server_get_hall_award_new_req()
-- 514: local serverTime = xyd.getServerTime()
-- 517: local num = math.floor((serverTime - firstTime) / onceTime)
-- 518: local leftTime = (serverTime - firstTime) % onceTime
-- 720: local startTime = firstTime + (index - 1) * onceTime
-- 721: local endTime = startTime + oneWeek
-- 722: local startTimeInfo = os.date("*t", startTime)
-- 723: local endTimeInfo = os.date("*t", endTime)
-- 724: local timeStr = tostring(startTimeInfo.year) .. "." .. tostring(startTimeInfo.month) .. "." .. tostring(startTimeInfo.day) .. " - "
-- 727: timeStr = tostring(timeStr) .. tostring(endTimeInfo.year) .. "." .. tostring(endTimeInfo.month) .. "." .. tostring(endTimeInfo.day)
-- 729: timeStr = tostring(timeStr) .. tostring(endTimeInfo.month) .. "." .. tostring(endTimeInfo.day)
-- 814: local serverTime = xyd.getServerTime()
-- 815: local num = serverTime - self.lastChangeTime
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
