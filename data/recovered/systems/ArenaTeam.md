# ArenaTeam — contrato recuperado

Investigación del cliente; no certifica implementación local ni reglas del servidor.

## Tablas originales

- `arena_rank_award_team`: 12 filas; campos: id, rank, season_awards, rank_front
- `filterword`: 2575 filas; campos: id, word, ignore_case
- `misc`: 1332 filas; campos: key, value, desc

## Mensajes y esquemas de solicitud

- `ARENA_TEAM_ACCEPT`: ID 1642
- `ARENA_TEAM_ACCEPT_INVITATION`: ID 1651
- `ARENA_TEAM_APPLY_TEAM`: ID 1641
- `ARENA_TEAM_CHANGE_TEAM`: ID 1647
- `ARENA_TEAM_CREATE_TEAM`: ID 1640
- `ARENA_TEAM_DISSOLVE_TEAM`: ID 1645
- `ARENA_TEAM_FIGHT`: ID 1636
- `ARENA_TEAM_GET_APPLY_LIST`: ID 1653
- `ARENA_TEAM_GET_INVITE_PLAYERS`: ID 1649
- `ARENA_TEAM_GET_INVITE_TEAMS`: ID 1652
- `ARENA_TEAM_GET_RECOMMEND_TEAMS`: ID 1648
- `ARENA_TEAM_INVITE_MEMBER`: ID 1650
- `ARENA_TEAM_JOIN_TEAM`: ID 1646
- `ARENA_TEAM_QUIT`: ID 1643
- `ARENA_TEAM_REFUSE_APPLY`: ID 1654
- `ARENA_TEAM_REFUSE_INVITATION`: ID 1655
- `ARENA_TEAM_REMOVE_MEMBER`: ID 1644
- `ARENA_TEAM_TRANSFER_LEADER`: ID 1656
- `GET_ARENA_TEAM_INFO`: ID 1632
- `GET_ARENA_TEAM_MATCH_INFOS`: ID 1635
- `GET_ARENA_TEAM_OTHER_TEAM_INFO`: ID 1639
- `GET_ARENA_TEAM_RANK_LIST`: ID 1634
- `GET_ARENA_TEAM_RECORDS`: ID 1637
- `GET_ARENA_TEAM_REPORTS`: ID 1638
- `SET_ARENA_TEAM_PARTNERS`: ID 1633
- `arena_team_accept_invitation_req`: team_id (campo 1, tipo 5, label 2)
- `arena_team_accept_req`: member_id (campo 1, tipo 5, label 2)
- `arena_team_apply_team_req`: team_id (campo 1, tipo 5, label 2)
- `arena_team_change_team_req`: member_ids (campo 1, tipo 5, label 3)
- `arena_team_create_team_req`: team_name (campo 1, tipo 9, label 2), need_power (campo 2, tipo 5, label 2)
- `arena_team_dissolve_team_req`:
- `arena_team_fight_req`: enemy_id (campo 1, tipo 5, label 2)
- `arena_team_get_apply_list_req`:
- `arena_team_get_invite_players_req`:
- `arena_team_get_invite_teams_req`:
- `arena_team_get_recommend_teams_req`:
- `arena_team_invite_member_req`: member_id (campo 1, tipo 5, label 2)
- `arena_team_join_team_req`:
- `arena_team_quit_req`:
- `arena_team_refuse_apply_req`: member_ids (campo 1, tipo 5, label 3)
- `arena_team_refuse_invitation_req`: team_ids (campo 1, tipo 5, label 3)
- `arena_team_remove_member_req`: member_id (campo 1, tipo 5, label 2)
- `arena_team_transfer_leader_req`: member_id (campo 1, tipo 5, label 2)
- `get_arena_team_info_req`:
- `get_arena_team_match_infos_req`:
- `get_arena_team_other_team_info_req`: other_player_id (campo 1, tipo 5, label 2)
- `get_arena_team_rank_list_req`:
- `get_arena_team_records_req`:
- `get_arena_team_reports_req`: record_ids (campo 1, tipo 5, label 3)
- `set_arena_team_partners_req`: partners (campo 1, tipo 11, label 3), pet_id (campo 2, tipo 5, label 1), formation_id (campo 3, tipo 5, label 1)

## Métodos del modelo (líneas de la fuente original)

- Línea 6: `ArenaTeam:ctor()`
- Línea 22: `ArenaTeam:checkFunctionOpen()`
- Línea 26: `ArenaTeam:checkOpen()`
- Línea 32: `ArenaTeam:isCaptain()`
- Línea 40: `ArenaTeam:reqArenaInfo()`
- Línea 46: `ArenaTeam:onGetArenaInfo(event)`
- Línea 72: `ArenaTeam:updateTeamInfo(teamInfo)`
- Línea 103: `ArenaTeam:onFight(event)`
- Línea 110: `ArenaTeam:updateRank(rank)`
- Línea 114: `ArenaTeam:updateScore(score)`
- Línea 118: `ArenaTeam:updateFormation(partners)`
- Línea 126: `ArenaTeam:updateLock(defPartners)`
- Línea 156: `ArenaTeam:getTeamName()`
- Línea 164: `ArenaTeam:getRank()`
- Línea 168: `ArenaTeam:getScore()`
- Línea 172: `ArenaTeam:getDDL()`
- Línea 176: `ArenaTeam:getStartTime()`
- Línea 180: `ArenaTeam:getEnergyTime()`
- Línea 184: `ArenaTeam:getEnergy()`
- Línea 188: `ArenaTeam:setEnergy(num)`
- Línea 192: `ArenaTeam:getPower()`
- Línea 196: `ArenaTeam:getTeamId()`
- Línea 204: `ArenaTeam:getIsJoin()`
- Línea 212: `ArenaTeam:setDefFormation(partners)`
- Línea 223: `ArenaTeam:onsetDefFormation(event)`
- Línea 236: `ArenaTeam:getDefFormation()`
- Línea 240: `ArenaTeam:getPet()`
- Línea 244: `ArenaTeam:reqRankList()`
- Línea 250: `ArenaTeam:onGetRankList(event)`
- Línea 254: `ArenaTeam:getRankList()`
- Línea 258: `ArenaTeam:reqEnemyList()`
- Línea 274: `ArenaTeam:onGetEnemyList(event)`
- Línea 284: `ArenaTeam:getEnemyList()`
- Línea 288: `ArenaTeam:fight(enemyID)`
- Línea 296: `ArenaTeam:reqRecord()`
- Línea 302: `ArenaTeam:reqReport(ids)`
- Línea 313: `ArenaTeam:getTmpReports()`
- Línea 317: `ArenaTeam:setTmpReports(data, index)`
- Línea 322: `ArenaTeam:resetTmpReports(index)`
- Línea 328: `ArenaTeam:getTempIndex()`
- Línea 332: `ArenaTeam:resetTempIndex()`
- Línea 336: `ArenaTeam:getNextReport()`
- Línea 350: `ArenaTeam:getNowBattleIndex()`
- Línea 354: `ArenaTeam:isLastReport()`
- Línea 362: `ArenaTeam:reqEnemyInfo(player_id)`
- Línea 370: `ArenaTeam:setSkipReport(flag)`
- Línea 381: `ArenaTeam:isSkipReport()`
- Línea 389: `ArenaTeam:onRegister()`
- Línea 426: `ArenaTeam:createTeam(teamName, needForce)`
- Línea 435: `ArenaTeam:onCreateTeam(event)`
- Línea 439: `ArenaTeam:applyTeam(teamId)`
- Línea 447: `ArenaTeam:onApplyTeam(event)`
- Línea 451: `ArenaTeam:accept(memberId)`
- Línea 460: `ArenaTeam:onAccept(event)`
- Línea 468: `ArenaTeam:quit()`
- Línea 474: `ArenaTeam:onQuit(event)`
- Línea 478: `ArenaTeam:removeMember(memberId)`
- Línea 486: `ArenaTeam:onRemoveMember(event)`
- Línea 490: `ArenaTeam:dissolveTeam()`
- Línea 496: `ArenaTeam:onDissolveTeam(event)`
- Línea 500: `ArenaTeam:joinTeam()`
- Línea 506: `ArenaTeam:onJoinTeam(event)`
- Línea 510: `ArenaTeam:changeTeam(memberIds)`
- Línea 521: `ArenaTeam:onChangeTeam(event)`
- Línea 525: `ArenaTeam:getRecommendTeams()`
- Línea 531: `ArenaTeam:onGetRecommendTeams(event)`
- Línea 535: `ArenaTeam:getInvitePlayers()`
- Línea 541: `ArenaTeam:onGetInvitePlayers(event)`
- Línea 545: `ArenaTeam:inviteMember(memberID)`
- Línea 553: `ArenaTeam:onInviteMember(event)`
- Línea 557: `ArenaTeam:acceptInvitation(teamID)`
- Línea 566: `ArenaTeam:onAcceptInvitation(event)`
- Línea 574: `ArenaTeam:reqInviteTeams()`
- Línea 580: `ArenaTeam:onGetInviteTeams(event)`
- Línea 590: `ArenaTeam:getInviteTeams()`
- Línea 594: `ArenaTeam:getMyTeamInfo()`
- Línea 598: `ArenaTeam:changeTeamLeader(memberID)`
- Línea 606: `ArenaTeam:onChangeTeamLeader(event)`
- Línea 610: `ArenaTeam:reqApplyList()`
- Línea 616: `ArenaTeam:onGetApplyList(event)`
- Línea 628: `ArenaTeam:getApplyList()`
- Línea 632: `ArenaTeam:refuseApply(memberIds)`
- Línea 647: `ArenaTeam:onRefuseApply(event)`
- Línea 655: `ArenaTeam:removeApplyByID(id)`
- Línea 665: `ArenaTeam:refuseInvitation(teamIDs)`
- Línea 680: `ArenaTeam:onRefuseInvitation(event)`
- Línea 688: `ArenaTeam:removeInvitationByID(id)`
- Línea 700: `ArenaTeam:updateRedMark()`
- Línea 712: `ArenaTeam:onServerBroadCast(event)`
- Línea 735: `ArenaTeam:isShowServerId(id)`

## Evidencia de costes, límites y tiempo

Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.

### `lua/app/models/ArenaTeam.lua`

```lua
-- 27: local startTime = self:getStartTime() - xyd.getServerTime()
-- 29: return startTime < 0
-- 60: self.startTime = data.start_time or 0
-- 176: function ArenaTeam:getStartTime()
-- 177: return self.startTime or 0
-- 739: if displayMarks[3] < xyd.getServerTime() then
```

### `lua/app/windows/ArenaTeamAwardWindow.lua`

```lua
-- 22: local awardGroup = infoGroup:NodeByName("awardGroup").gameObject
-- 23: local leftBg = awardGroup:ComponentByName("leftBg", typeof(UITexture))
-- 24: local rightBg = awardGroup:ComponentByName("rightBg", typeof(UITexture))
-- 26: xyd.setUITextureAsync(leftBg, "Textures/arena_web/arena_award_bg", function()
-- 29: xyd.setUITextureAsync(rightBg, "Textures/arena_web/arena_award_bg", function()
-- 33: self.labelRank = awardGroup:ComponentByName("labelRank", typeof(UILabel))
-- 34: self.nowAward = awardGroup:NodeByName("nowAward").gameObject
-- 37: self.awardContainer = infoGroup:NodeByName("scroller/vs/awardContainer").gameObject
-- 77: NGUITools.DestroyChildren(self.awardContainer.transform)
-- 79: for i = 1, #selfAwardInfo.award do
-- 80: local item = selfAwardInfo.award[i]
-- 93: local awardItem = ArenaAwardItem.new(self.awardContainer, self)
-- 95: awardItem:setInfo({
-- 96: colName = "award",
-- 102: self.awardContainer:GetComponent(typeof(UILayout)):Reposition()
-- 119: return "Prefabs/Components/arena_team_award_item"
-- 127: self.awardGroup = go:NodeByName("awardGroup").gameObject
-- 128: self.awardGroupLayout = self.awardGroup:GetComponent(typeof(UILayout))
-- 148: NGUITools.DestroyChildren(self.awardGroup.transform)
-- 156: uiRoot = self.awardGroup,
-- 163: self.awardGroupLayout:Reposition()
```

### `lua/app/windows/ArenaTeamChoosePlayerWindow.lua`

```lua
-- 94: local nextTime = lastEnergyTime + interval - xyd.getServerTime()
-- 115: local fixEnergy = self.model_:getEnergy() + math.floor((xyd.getServerTime() - lastEnergyTime) / interval)
```

### `lua/app/windows/ArenaTeamRecordWindow.lua`

```lua
-- 145: local resTime = xyd:getServerTime() - params.time
```

### `lua/app/windows/ArenaTeamWindow.lua`

```lua
-- 283: local startTime = self.model_:getStartTime() - xyd.getServerTime()
-- 285: return startTime < 0
-- 289: local ddl = self.model_:getDDL() - xyd.getServerTime()
-- 297: local startTime = self.model_:getStartTime() - xyd:getServerTime()
-- 299: if startTime > 0 then
-- 303: self.seasonCountDown.text = xyd.secondsToString(startTime)
-- 310: duration = math.floor(startTime)
-- 314: duration = math.floor(startTime)
-- 320: if startTime > xyd.TimePeriod.DAY_TIME * (xyd.ARENA_WAIT_TIME.ARENA_TEAM - 1) then
-- 383: xyd.WindowManager.get():openWindow("arena_team_award_window", {})
```

## Pendiente para volverlo jugable

Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. Los métodos y mensajes recuperados no contienen la implementación del servidor.
