# Inventario del cliente descompilado

> Generado por `tools/build_client_inventory.py` desde `~/Downloads/Decomp files` (solo lectura). No editar a mano: actualizar el mapa `LOCAL` del script y volver a ejecutarlo. JSON completo en `validation/client-inventory.json`.

## Resumen

El mapa de estados LOCAL se mantiene manualmente y puede conservar estados históricos; una casilla vacía no prueba ausencia de implementación. Las referencias de tabla son léxicas y no certifican que se lean en ejecución.

- Modelos de juego del cliente: **71**; con implementación local (total o parcial): **51** (72%).
- Tablas de datos originales: **330/904** leídas por el proyecto (37%); sin eventos `activity_*`: **235/462** (51%).
- Mensajes de red referenciados por modelos: 497; el proyecto usa su propia API HTTP, así que la columna de mensajes solo cuenta los que `engine.py`/`protocol.py` nombran.

## Modelos (sistemas) del cliente

| Modelo | Estado local | Módulo local | Tablas usadas | Mensajes | Ventanas principales |
|---|---|---|---|---|---|
| GameAssistant | [ ] | — | 24/25 | 1/8 | BattleFormationWindow, GameAssistantDungeonShopWindow, GameAssistantMarketWindow, GameAssistantResultWindow (+2) |
| Chat | [ ] | — | 2/8 | 0/21 | ArcticExpeditionMainWindow, ArenaFormationWindow, ChatBlackListWindow, ChatGMWindow (+12) |
| ArenaTeam | [ ] | — | 1/3 | 0/25 | ArenaTeamApplyWindow, ArenaTeamAwardWindow, ArenaTeamChangeTeamWindow, ArenaTeamChoosePlayerWindow (+15) |
| House | [ ] | — | 11/16 | 0/12 | HouseCombineWindow, HouseComfortWindow, HouseDialog, HouseEditNameWindow (+16) |
| FriendTeamBoss | [ ] | — | 2/8 | 0/18 | BattleChooseWindow, BattleFailWindow, BattleFormationWindow, BattleWinWindow (+15) |
| ArenaAllServer | [ ] | — | 7/11 | 0/11 | Arena3v3BattleFormationWindow, Arena3v3ChoosePlayerWindow, Arena3v3RecordDetailWindow, Arena3v3RecordWindow (+12) |
| FairArena | [ ] | — | 8/14 | 0/6 | FairArenaAlertWindow, FairArenaAwardPreviewWindow, FairArenaAwardWindow, FairArenaBackpackWindow (+15) |
| DressShow | [ ] | — | 11/11 | 1/8 | DressShowAwardWindow, DressShowBuffsDetailWindow, DressShowChooseWindow, DressShowEntranceWindow (+3) |
| Arena3v3 | [ ] | — | 10/12 | 0/6 | Arena3v3AwardWindow, Arena3v3BattleFormationWindow, Arena3v3ChoosePlayerWindow, Arena3v3FormationWindow (+8) |
| GuildWar | [ ] | — | 2/3 | 0/12 | BattleFormationWindow, GuildWarAllFormationWindow, GuildWarAwardWindow, GuildWarFormationWindow (+6) |
| PartnerDataStation | [ ] | — | 8/10 | 0/4 | ActivityFairyTaleBattleFormationWindow, BattleFormationWindow, DatesWindow, EditStationPartnerWindow (+5) |
| ActivityPointTips | [ ] | — | 8/13 | 0/0 | ActivityPointTipsWindow, ActivityWindow, MainWindow |
| ArenaAllServerNew | [ ] | — | 1/2 | 0/11 | Arena3v3RecordDetailWindow, Arena3v3RecordWindow, ArenaAllServerBattleFormationWindow, ArenaAllServerFormationWindow (+5) |
| ArenaAllServerScore | [ ] | — | 1/3 | 0/9 | Arena3v3ChoosePlayerWindow, Arena3v3RecordDetailWindow, Arena3v3RecordWindow, ArenaAllScoreServerAwardWindow (+5) |
| Background | [ ] | — | 5/6 | 0/3 | BackGroundWindow, BackgroundGroupWindow, BackgroundPreviewConfirmWindow, BackgroundPreviewWindow (+1) |
| QuickFormation | [ ] | — | 7/7 | 0/2 | BattleFormationWindow, QucikFormationEditNameWindow, QuickFormationPartnerDetailWindow, QuickFormationWindow |
| Comic | [ ] | — | 2/3 | 0/3 | ComicCommentWindow, ComicDetailWindow, ComicWindow |
| Vip | [ ] | — | 4/4 | 0/2 | VipWindow |
| PartnerComment | [ ] | — | 1/1 | 0/4 | ActivityPopularityVoteSupportMessageWindow, EditStationPartnerWindow, PartnerDataStationWindow |
| Community | [ ] | — | 0/0 | 0/0 | CommunityActivityDetailWindow, CommunityActivityWindow, SettingUpWindow |
| Activity | [P][M] | events.py / point_events.py | 65/181 | 0/8 | AcademyAssessmentAwardWindow, Activity2LoveDetailWindow, Activity2LoveMissionWindow, Activity2LoveWindow (+399) |
| Guild | [P][M] | guild_lab.py / guild-lab.js (solo laboratorio) | 22/39 | 3/39 | ActivityEntranceTestCrystalWindow, ActivityReturnCommendWindow, ActivityReturnCommunityWindow, ActivityStudyQuestionAnswerWindow (+67) |
| TimeCloisterModel | [T][P][M] | echoes.py Echoes of Time | 17/26 | 0/19 | BattleChooseWindow, BattleFormationWindow, BattleWindow, TimeCloisterAchievementDetailWindow (+27) |
| Partner | [T][P] | engine.py / girls | 25/29 | 4/13 | ActivityFairyTaleBattleFormationWindow, ActivityPopularityVoteSupportMessageWindow, BattleFormationWindow, DatesWindow (+10) |
| Friend | [T][P][M] | home_systems.py contactos / friend_boss.py actual | 7/14 | 2/17 | ActivityReturnCommendWindow, ActivityReturnCommunityWindow, ArenaFormationWindow, ArenaTeamFormationWindow (+30) |
| Slot | [T][P] | engine.py (roster/slot) | 9/10 | 1/21 | AchievementWindow, Activity4BirthdayChoiceAwardWindow, ActivityAllStarsPrayHerosWindow, ActivityAntiqueChooseWindow (+103) |
| ExploreModel | [T][M] | explore.py | 17/18 | 0/11 | AdventureBoxPreviewWindow, AdventureLevelUpWindow, AutoAdventureSetupWindow, BattleFormationWindow (+16) |
| ShrineHurdleModel | [T][P][M] | shrine.py Realm of Trials | 18/18 | 0/11 | BattleChooseWindow, BattleFailWindow, BattleFormationWindow, BattleWinWindow (+18) |
| GalaxyTrip | [T][P][M] | galaxy.py Galaxy Voyage | 17/17 | 0/11 | BattleFormationWindow, BattleWinWindow, GalaxyBattleBuffWindow, GalaxyExploreProgressWindow (+9) |
| Shrine | [T][M] | shrine.py Message Board / Pond | 21/21 | 0/6 | BattleChooseWindow, BattleFailWindow, BattleFormationWindow, BattleWinWindow (+21) |
| Arena | [T][M] | arena.py Junior Varsity | 12/18 | 0/8 | ActivityEntranceTestRecordWindow, ActivityHw2022RankWindow, ActivityItemGetwayWindow, ActivitySportsFightRecordWindow (+53) |
| Dress | [T][P][M] | dress.py Outfits | 19/20 | 1/6 | AcademyAssessmentFinalRankWindow, AcademyAssessmentRankWindow2, ActivityLostSpaceMapWindow, ActivitySpfarmMapWindow (+44) |
| OldSchool | [T][P][M] | old_campus.py Old Campus | 13/19 | 0/7 | ActivityExploreCampusFightWindow, ActivityExploreOldCampusFloorAwardWindow, ActivityExploreOldCampusPVEPointWindow, ActivityExploreOldCampusWaysWindow (+12) |
| SoulLand | [T][P][M] | soul_land.py Land of Souls | 13/14 | 0/12 | BattleChooseWindow, BattleFailWindow, BattleFormationWindow, BattleWinWindow (+9) |
| Summon | [T][P] | acquisition.py / capsule | 15/16 | 2/9 | AchievementWindow, DebrisSummonWindow, DressSummonWindow, ItemTips (+9) |
| HeroChallenge | [T][P][M] | hero_challenge.py Normal+Puzzle | 9/12 | 0/12 | ActivityFairyTaleBattleFormationWindow, BattleChooseWindow, BattleFormationWindow, BattleLoadingWindow (+14) |
| Backpack | [T] | engine.py / bag | 12/14 | 1/9 | AcademyAssessmentBuyWindow, AcademyAssessmentFinalRankWindow, AcademyAssessmentRankWindow2, AccountWindow (+264) |
| AcademyAssessment | [T][M] | house_exam.py House Exam | 10/16 | 0/4 | AcademyAssessmentAwardWindow, AcademyAssessmentBattleSetWindow, AcademyAssessmentBuyWindow, AcademyAssessmentDetailWindow (+17) |
| HeroAttr | [T] | battle.py attrs | 20/20 | 0/0 | — |
| Tavern | [T][M] | internship.py Internship | 9/10 | 0/10 | TavernDetailWindow, TavernMultimissionWindow, TavernUseScrollWindow, TavernWindow |
| Collection | [P] | galería | 14/16 | 0/2 | ActivityEntranceTestPartnerWindow, ActivityEntranceTestSoulWindow, BackgroundPreviewWindow, BackpackWindow (+20) |
| Dungeon | [T][M] | patrol.py Patrol | 11/11 | 0/7 | BattleChooseWindow, BattleFailWindow, BattleWinWindow, DungeonBuyItemWindow (+6) |
| Pet | [T][P] | home_systems.py Servants | 13/15 | 0/0 | Arena3v3BattleFormationWindow, ArenaAllServerBattleFormationWindow, BattleFormationWindow, BattleTestWindow (+19) |
| Trial | [T][P][M] | sanctuary.py Sanctuary | 9/10 | 0/5 | ActivityFairyTaleBattleFormationWindow, ActivityNewTrialBlessWindow, BattleChooseWindow, BattleFailWindow (+11) |
| Mail | [T][M] | home_systems.py | 4/9 | 0/5 | MailDetailWindow, MailSendWindow, MailWindow |
| PetTraining | [T][P][M] | pet_training.py / remaining-systems.js | 6/6 | 8/8 | GameAssistantResultWindow, GameAssistantWindow, PetStartWindow, PetTrainingBossAwardWindow (+7) |
| SelfPlayer | [T][P] | engine.py perfil | 3/4 | 0/10 | AcademyAssessmentFinalRankWindow, AcademyAssessmentRankWindow2, AccountWindow, ActivityEntranceTestFinalRankWindow (+81) |
| Shop | [T][P][M] | shops.py | 6/10 | 3/3 | BaseShop, CollectionShopWindow, CollectionWindow, CommonShopWindow (+11) |
| Hero | [T] | battle.py / engine.py | 9/12 | 0/0 | ActivityFairyTaleBattleFormationWindow, BattleChooseWindow, BattleFormationWindow, BattleLoadingWindow (+14) |
| Map | [T][P] | campaign.py | 1/2 | 3/10 | Activity2LoveMissionWindow, ActivityDragonBoatAwardSelectWindow, ActivityEntranceTestAddHeroWindow, ActivityOptionalAwardWindow (+25) |
| Gamble | [T][P][M] | acquisition.py Slots | 6/6 | 3/5 | GambleRewardsWindow, GambleTipsWindow, GambleWindow, GameAssistantResultWindow (+1) |
| PetSlot | [T][P][M] | home_systems.py / pet_training.py Ulticore | 1/2 | 3/9 | Arena3v3BattleFormationWindow, ArenaAllServerBattleFormationWindow, BattleFormationWindow, BattleTestWindow (+11) |
| StoryListModel | [T][P] | story.py Main story + Memories | 5/8 | 0/3 | StoryListUnlockWindow, StoryListWindow |
| SettingUp | [P] | localStorage mute | 4/6 | 0/4 | ChangeLanguageWindow, LoginWindow, MainWindow, NewNoticeWindow (+9) |
| Achievement | [T][P] | missions.py Trophies | 5/5 | 0/4 | AchievementWindow, BattlePassWindow, CampaignAwardWindow, CampaignWindow (+5) |
| DailyQuiz | [T][P] | engine.py daily quiz | 3/4 | 0/5 | ActivityReturnDoubleWindow, BattleChooseWindow, BattleFormationWindow, BattleWinWindow (+9) |
| Prophet | [T][P][M] | acquisition.py Exchange | 7/7 | 1/2 | ProphetChoosePartnerWindow, ProphetDropProbabilityWindow, ProphetWindow |
| SoulEquip2 | [T][P][M] | souls.py Anima Stones | 8/8 | 0/0 | SoulEquip2StrengthenWindow |
| Mission | [T][P][M] | missions.py | 3/4 | 0/3 | ArtifactShopWarmUpWindow, BattlePassWindow, DailyMissionWindow, GameAssistantResultWindow |
| ShenXue | [T][P] | engine.py Graduate | 5/6 | 1/1 | ShenXueSelectWindow, ShenXueWindow |
| GrowthDiary | [T][P][M] | growth_diary.py / growth-diary.js | 2/2 | 3/4 | GrowthDiaryWindow |
| SoulEquip1 | [T][P][M] | souls.py Anima Artifact | 6/6 | 0/0 | SoulEquip1StrengthenWindow |
| TowerMap | [T][P] | engine.py Tests | 1/1 | 0/5 | BattleFailWindow, BattleWinWindow, ItemTips, TowerFundGiftbagWindow (+3) |
| Midas | [T][M] | midas.py Alchemy | 3/3 | 0/2 | GameAssistantResultWindow, MidasWindow |
| NewbieCamp | [T][P][M] | newbie_camp.py / newbie-camp.js | 3/3 | 2/2 | NewbieCampListWindow |
| Monster | [T] | battle.py | 3/3 | 0/0 | — |
| ActivityData | [P] | events.py | 1/1 | 0/0 | — |
| RedMark | [P] | web (parcial) | 0/1 | 0/0 | ActivityGrowthPlanWindow, ActivityPopularityVoteWindow, ActivityRedeemCodeWindow, ActivityResidentReturnMainWindow (+54) |
| ActivityDatas | [P] | events.py | 0/0 | 0/0 | — |
| Player | [P] | engine.py perfil | 0/0 | 0/0 | — |
| TeamFormation | [T] | engine.py formación | 0/0 | 0/0 | — |

## Cobertura de tablas por prefijo

| Prefijo | Usadas / total |
|---|---|
| `activity_*` | 95/442 |
| `partner_*` | 15/44 |
| `guild_*` | 8/26 |
| `shop_*` | 12/21 |
| `arena_*` | 8/20 |
| `time_*` | 8/18 |
| `galaxy_*` | 11/15 |
| `shrine_*` | 13/15 |
| `old_*` | 6/13 |
| `soul_*` | 11/12 |
| `house_*` | 5/11 |
| `senpai_*` | 8/11 |
| `new_*` | 6/9 |
| `pet_*` | 7/9 |
| `school_*` | 3/9 |
| `main_*` | 5/8 |
| `travel_*` | 8/8 |
| `govern_*` | 0/6 |
| `show_*` | 6/6 |
| `battlepass_*` | 3/5 |
| `direct_*` | 4/5 |
| `exp_*` | 5/5 |
| `battle_*` | 1/4 |
| `dungeon_*` | 4/4 |
| `friend_*` | 3/4 |
| `guide_*` | 0/4 |
| `skill_*` | 3/4 |
| `star_*` | 3/4 |
| `trial_*` | 1/4 |
| `chime_*` | 3/3 |
| `collection_*` | 3/3 |
| `cost_*` | 0/3 |
| `custom_*` | 1/3 |
| `device_*` | 0/3 |
| `gamble_*` | 3/3 |
| `getway_*` | 1/3 |
| `pub_*` | 3/3 |
| `skin_*` | 1/3 |
| `stage_*` | 2/3 |
| `summon_*` | 2/3 |
| `window_*` | 1/3 |

## Tablas sin usar por modelo pendiente

- **GameAssistant**: `activity_return2_add`, `battlepass_mission`, `dungeon_drug`, `dungeon_shop`, `function`, `gamble_config`, `guild_mill`, `guild_order`, `item`, `midas`, `midas_buy_coin`, `misc`, `pet_training_boss`, `pet_training_new_awards` …
- **Chat**: `device_notify`, `emoticon`, `emoticon_gif`, `filterword`, `filterword_super`, `function`, `misc`, `player_language`
- **ArenaTeam**: `arena_rank_award_team`, `filterword`, `misc`
- **House**: `collection`, `house_award`, `house_dialog`, `house_dialog_list`, `house_furniture`, `house_furniture_effect`, `house_furniture_group`, `house_guide`, `house_partner`, `item`, `misc`, `model`, `partner`, `senpai_dress` …
- **FriendTeamBoss**: `function`, `govern_flag`, `govern_guide`, `govern_team`, `govern_team_award`, `govern_team_weather`, `misc`, `server_map`
- **ArenaAllServer**: `arena_all_server_award`, `arena_all_server_mission`, `arena_all_server_rank`, `arena_all_server_robot`, `arena_robot`, `fort`, `item`, `misc`, `partner`, `senpai_dress_slot`, `stage`
- **FairArena**: `activity_fair_arena_box_equip`, `activity_fair_arena_box_partner`, `activity_fair_arena_level`, `activity_fair_arena_rank`, `activity_fair_arena_robot`, `buff`, `equip`, `group_buff`, `item`, `misc`, `model`, `partner`, `partner_exskill`, `stage`
- **DressShow**: `function`, `item`, `misc`, `senpai_dress`, `senpai_dress_item`, `show_window`, `show_window_award`, `show_window_shop1`, `show_window_shop2`, `show_window_shop3`, `show_window_slot`
- **Arena3v3**: `arena_all_server_rank`, `arena_all_server_robot`, `arena_rank_award_3v3`, `arena_robot`, `fort`, `function`, `group`, `item`, `misc`, `partner`, `partner_picture`, `stage`
- **GuildWar**: `guild_flag`, `guild_war_point_award`, `misc`
- **PartnerDataStation**: `direct`, `direct_array`, `direct_label`, `direct_label_type`, `direct_monster`, `equip`, `filterword`, `item`, `misc`, `partner`
- **ActivityPointTips**: `achievement`, `achievement_type`, `activity`, `activity_arena`, `activity_compose`, `activity_gacha`, `activity_gamble`, `activity_pub_mission`, `activity_tree`, `activity_tree_group_award`, `partner`, `pub_mission`, `tips_activity_point`
- **ArenaAllServerNew**: `arena_all_server_rank`, `misc`
- **ArenaAllServerScore**: `arena_all_server_mission`, `arena_all_server_rank`, `misc`
- **Background**: `collection`, `custom_background`, `custom_background_group`, `item`, `misc`, `partner_picture`
- **QuickFormation**: `equip`, `group_buff`, `item`, `misc`, `partner`, `pet`, `skill`
- **Comic**: `comic`, `filterword`, `misc`
- **Vip**: `activity`, `giftbag`, `misc`, `vip`
- **PartnerComment**: `misc`
