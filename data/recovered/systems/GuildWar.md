# GuildWar — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `guild_flag`: 20 filas; campos: id, picture
- `guild_war_point_award`: 12 filas; campos: id, rank, season_awards, rank_front, awards_1, awards_2, awards_3
- `misc`: 1332 filas; campos: key, value, desc

## Mensajes y esquemas de solicitud

- `GUILD_WAR_FIGHT`: ID 1576
- `GUILD_WAR_GET_FINAL_INFO`: ID 1580
- `GUILD_WAR_GET_FINAL_RECORD`: ID 1581
- `GUILD_WAR_GET_INFO`: ID 1570
- `GUILD_WAR_GET_RANK_LIST`: ID 1579
- `GUILD_WAR_GET_RECORDS`: ID 1577
- `GUILD_WAR_GET_RECORD_DETAIL`: ID 1575
- `GUILD_WAR_GET_REPORT`: ID 1578
- `GUILD_WAR_JOIN`: ID 1573
- `GUILD_WAR_MATCH`: ID 1574
- `GUILD_WAR_SAVE_TEAMS`: ID 1572
- `GUILD_WAR_SET_PARTNERS`: ID 1571
- `fight_partner`: partner_id (campo 1, tipo 5, label 2), pos (campo 2, tipo 5, label 2)
- `guild_war_fight_req`:
- `guild_war_get_final_info_req`:
- `guild_war_get_final_record_req`: round (campo 1, tipo 5, label 2), battle_index (campo 2, tipo 5, label 2)
- `guild_war_get_info_req`:
- `guild_war_get_rank_list_req`:
- `guild_war_get_record_detail_req`: record_ids (campo 1, tipo 5, label 3)
- `guild_war_get_records_req`:
- `guild_war_get_report_req`: record_id (campo 1, tipo 5, label 2)
- `guild_war_join_req`:
- `guild_war_match_req`:
- `guild_war_save_teams_req`: member_ids (campo 1, tipo 5, label 3), hide_ids (campo 2, tipo 5, label 3)
- `guild_war_set_partners_req`: partners (campo 1, tipo 11, label 3), pet_id (campo 2, tipo 5, label 1), formation_id (campo 3, tipo 5, label 1)

## Métodos del modelo (líneas de la fuente original)

- Línea 6: `GuildWar:ctor()`
- Línea 13: `GuildWar:getMatchDirtyFlag()`
- Línea 17: `GuildWar:getMatchCD()`
- Línea 21: `GuildWar:SetMatchDirtyFlag(flag)`
- Línea 25: `GuildWar:setMatchCD(time)`
- Línea 29: `GuildWar:onRegister()`
- Línea 40: `GuildWar:Join()`
- Línea 46: `GuildWar:onSaveTeams(event)`
- Línea 66: `GuildWar:onMatch(event)`
- Línea 71: `GuildWar:onJoin(e)`
- Línea 83: `GuildWar:reqGuildWarInfo()`
- Línea 89: `GuildWar:onGetGuildWarInfo(event)`
- Línea 137: `GuildWar:updateRank(rank)`
- Línea 143: `GuildWar:updateScore(score)`
- Línea 147: `GuildWar:onFight(event)`
- Línea 158: `GuildWar:getRank()`
- Línea 162: `GuildWar:getScore()`
- Línea 166: `GuildWar:getDDL()`
- Línea 170: `GuildWar:getEnergyTime()`
- Línea 174: `GuildWar:getEnergy()`
- Línea 178: `GuildWar:setEnergy(num)`
- Línea 182: `GuildWar:getTeamId()`
- Línea 190: `GuildWar:getIsSigned()`
- Línea 198: `GuildWar:setDefFormation(partners, petID, team_index)`
- Línea 219: `GuildWar:onsetDefFormation(event)`
- Línea 271: `GuildWar:getDefFormation()`
- Línea 275: `GuildWar:setTeamFormation(member_ids, hide_ids)`
- Línea 289: `GuildWar:fight()`
- Línea 295: `GuildWar:reqRecordDetail(record_ids)`
- Línea 305: `GuildWar:reqRecord()`
- Línea 311: `GuildWar:reqReport(id)`
- Línea 319: `GuildWar:getTmpReports()`
- Línea 323: `GuildWar:setTmpReports(data)`
- Línea 327: `GuildWar:getNowBattleIndex()`
- Línea 331: `GuildWar:isLastReport()`
- Línea 339: `GuildWar:reqEnemyInfo()`
- Línea 347: `GuildWar:setSkipReport(flag)`
- Línea 358: `GuildWar:reqRankList()`
- Línea 364: `GuildWar:judgeMoment()`
- Línea 387: `GuildWar:reqFinalInfo()`
- Línea 393: `GuildWar:onGetFinalInfo(e)`
- Línea 407: `GuildWar:reqFinalRecord(round, index)`
- Línea 416: `GuildWar:getInfo()`
- Línea 420: `GuildWar:getMatchInfo()`
- Línea 424: `GuildWar:getFinalInfo()`
- Línea 428: `GuildWar:getmatchDirtyFlag()`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/GuildWar.lua`

```lua
-- 366: local nowTime = xyd.getServerTime()
-- 368: local startTime
-- 371: startTime = self.info_.week_start_time or xyd.getGMTWeekStartTime(nowTime)
-- 373: startTime = xyd.getGMTWeekStartTime(nowTime)
-- 376: local timePass = nowTime - startTime
```

### `lua/app/windows/GuildWarAwardWindow.lua`

```lua
-- 48: return "Prefabs/Components/arena_award_item"
-- 56: self.awardGroup = go:NodeByName("awardGroup").gameObject
-- 57: self.awardGroupLayout = self.awardGroup:GetComponent(typeof(UILayout))
-- 77: NGUITools.DestroyChildren(self.awardGroup.transform)
-- 85: uiRoot = self.awardGroup,
-- 93: self.awardGroupLayout:Reposition()
-- 113: self.grid_ = conTrans:ComponentByName("scrollview/awardContainer", typeof(MultiRowWrapContent))
-- 117: xyd.WindowManager.get():closeWindow("guild_war_award_window")
-- 183: local endTime = ddl - xyd.getServerTime()
-- 186: params.duration = endTime
-- 198: for _, itemInfo in ipairs(selfAwardInfo.award) do
```

### `lua/app/windows/GuildWarInfoWindow.lua`

```lua
-- 156: xyd.WindowManager.get():openWindow("guild_war_award_window")
-- 290: local cd = guildModel.enlistTime + tonumber(xyd.tables.miscTable:getVal("guild_recruit")) - xyd.getServerTime()
-- 307: guildModel.enlistTime = xyd.getServerTime()
-- 492: local endTime = self.info_.week_start_time + intervals[moment] - xyd.getServerTime()
-- 495: params.duration = endTime
-- 984: local nextTime = interval - (xyd.getServerTime() - xyd.models.guildWar:getInfo().week_start_time) % interval
-- 1556: local endTime = xyd.models.guildWar:getInfo().week_start_time + timeIntervals[moment + 1] - xyd.getServerTime()
-- 1558: self:updateCountDown(endTime)
-- 1561: function GuildWarBeforeFinal:updateCountDown(endTime)
-- 1564: params.duration = endTime
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
