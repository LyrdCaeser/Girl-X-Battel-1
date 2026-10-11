# Recuperación de tablas — 01/10/2026

**904/904 tablas Lua recuperadas**, 202.878 filas en segmentos originales; 17 tablas compuestas resueltas (321.434 filas si se cuentan también sus copias compuestas); **252 tablas inglesas**, 73,656 filas. Errores: 0.

Generado con `python3 tools/recover_client_tables.py`. Fuentes originales en solo lectura; no se ejecuta Lua. Los nombres y posiciones de columnas se toman de `table.keys`, evitando las columnas desalineadas de `data.db`.

318 tablas tienen referencias léxicas locales; **586 no las tienen**. Una referencia puede pertenecer únicamente a un extractor. Recuperado no significa jugable ni verificado.

## Archivos y uso

- `data/recovered/manifest.json`: hashes, campos, tamaños, consumidores del cliente y referencias locales.
- `data/recovered/tables/<nombre>.json`: `keys` conserva posiciones desde 1; `rows` conserva los arrays originales; las tablas compuestas se resuelven con prioridad del primer segmento y se enumeran en `components`. Para leer un campo: `rows[id][keys[campo] - 1]`, comprobando antes la longitud de la fila.
- `data/recovered/texts/en_en/`: textos originales con columnas y filas completas.

Se preservan listas/costes/premios codificados como cadenas, celdas vacías, ceros y -1; no se deducen reglas de servidor. No se conectan estos datos automáticamente al runtime ni se cambian partidas.

## Contratos de sistemas para continuar

`data/recovered/systems/ArenaTeam.md`, `data/recovered/systems/FairArena.md`, `data/recovered/systems/GuildWar.md`, `data/recovered/systems/GrowthDiary.md`, `data/recovered/systems/NewbieCamp.md`, `data/recovered/systems/ArenaAllServerNew.md`, `data/recovered/systems/ArenaAllServerScore.md`, `data/recovered/systems/PetTraining.md`

Cada dossier incluye tablas/campos, métodos con líneas de origen, mensajes/IDs, esquemas protobuf recuperados y evidencias de costes/tiempo. Son investigación, no funciones jugables.

## Tablas pendientes de referencias locales

| Tabla | Filas | Campos | Modelos/ventanas del cliente |
|---|---:|---|---|
| `activity_3birthday_vip_awards` | 17 | id, vip_level, daily_awards, once_awards | Activity3BirthdayVipAwardWindow |
| `activity_4birthday_gamble` | 8 | id, awards, sort, type | Activity4BirthdayChoiceAwardWindow, Activity4birthdayMusicAwardViewWindow |
| `activity_4birthday_plot` | 289 | id, next_id, select_next_ids, select, plot, day, activity_plot_list_id, name, image_path, type … | StoryWindow |
| `activity_4birthday_story` | 7 | id, day, begin_plot_id, finish_plot_id | Activity4BirthdayPartyStoryWindow |
| `activity_5week_awards` | 4 | id, num, awards | ActivityLimitCultivateWindow |
| `activity_5week_gamble` | 8 | id, awards, num, weight | ActivityLimitCultivateWindow |
| `activity_arena` | 8 | id, type, point, awards, getway | ActivityPointTips |
| `activity_beach_island` | 10 | id, next_id, open_day, battle_id, initial_partner, awards, challenge1, challenge2, challenge3 | ActivityBeachIslandFightWindow, BattleFormationWindow |
| `activity_beach_puzzle` | 66 | id, num, area, area_line, area_award, final_award, bg, is_repeat | ActivityBeachPuzzleAwardPreviewWindow |
| `activity_beach_star_awards` | 6 | id, point, awards | ActivityBeachIslandAwardWindow |
| `activity_boss` | 24 | id, type, next_id, battle_id, dropbox_id, final_award, hp, monster_hp, mail_id, monthly_act_count … | ActivityWorldBossWindow |
| `activity_candy_collect` | 5 | id, awards_1, cost_1, awards_2, cost_2, awards_3, cost_3, awards_4, cost_4 | ActivityCandyCollectWindow |
| `activity_chose_gift` | 5 | id, awards1, awards2, num | ActivityDragonBoatAwardSelectWindow |
| `activity_christmas_sale_awards` | 12 | id, award0, award1, award2, award3, num, cost, limit, requirement | ActivityChristmasSaleAwardSelectWindow |
| `activity_christmas_sale_show` | 5 | id, award_show, is_new | AwardLookWindowNew |
| `activity_compose` | 4 | id, star, type, limit, awards, mail_id, getway | ActivityPointTips |
| `activity_crystal_ball` | 5 | id, desc, day, image_png, question_text_id, false_text_id, select_text_id, true_id, move, partner_picture_id … | ActivityCrystalBallQAWindow, ActivityCrystalBallStoryWindow |
| `activity_crystal_ball_plot` | 381 | id, next_id, select_next_ids, select, plot, day, activity_plot_list_id, name, image_path, type … | ActivityCrystalBallQAWindow, ActivityCrystalBallStoryWindow, StoryWindow |
| `activity_date_plot` | 1530 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, scale … | StoryWindow |
| `activity_demo_fight` | 13 | id, monster1, monster2 | ActivitySportsPartyDetailWindow, ActivitySportsShowsWindow |
| `activity_dragonboat2022_chose` | 4 | id, awards, num, desc | ActivityDragonboat2022AwardSelectWindow |
| `activity_easter_egg_point` | 14 | id, point, awards | ActivityEasterEggAwardWindow |
| `activity_encounter_battle` | 5 | id, next_id, battle_id, initial_partner, awards, time, challenge1, challenge2, challenge3 | ActivityEnconterStoryFightWindow, BattleFormationWindow |
| `activity_encounter_star_awards` | 3 | id, point, awards | ActivityBeachIslandAwardWindow |
| `activity_ept_cell_type` | 14 | id, function_id, battle_count, battle_count_2, battle_ids, icon, building_icon, building_fx, contribution, power … | ArcticExpeditionBossInfoWindow, ArcticExpeditionCellDetailWindow, ArcticExpeditionCellWindow, ArcticExpeditionMainWindow, ArcticExpeditionRecordWindow, ArcticExpeditionRecordWindow2 (+3) |
| `activity_ept_cells` | 169 | id, cell_xy, group_id, type_id | ArcticExpeditionBossInfoWindow, ArcticExpeditionCellDetailWindow, ArcticExpeditionCellWindow, ArcticExpeditionMainWindow, ArcticExpeditionRecordWindow, ArcticExpeditionRecordWindow2 (+3) |
| `activity_ept_era` | 3 | id, name, next_id, win_limit, unlock | ArcticExpeditionRecordWindow |
| `activity_ept_era_task` | 7 | id, era_id, type, complete, score, limit, check_era, desc | ArcticExpeditionTimeWindow |
| `activity_ept_gruop_rank_award` | 3 | rank, awards | ArcticExpeditionAwardWindow |
| `activity_ept_rank_award` | 8 | id, awards, rank1, rank2, rank3, string1, string2, string3 | ArcticExpeditionAwardWindow |
| `activity_ept_task` | 10 | id, type, complete, awards, limit, value_type, desc | ArcticExpeditionMissionWindow |
| `activity_equip_levelup` | 29 | id, equip_show, group, type, cost_show, awards, cost, limit | ActivityEquipLevelUpAwardWindow, ActivityWindow |
| `activity_equip_levelup_suit` | 5 | id, suit | ActivityEquipLevelUpChooseWindow |
| `activity_fair_arena_box_buff` | 52 | id, name, desc, effect, skillA, skillB, weight, box_id, icon | GroupBuffDetailWindow |
| `activity_fair_arena_box_equip` | 88 | id, equip_id, weight, box_id | FairArena, FairArenaBackpackWindow, FairArenaChooseEquipWindow, FairArenaCollectionWindow, FairArenaExploreWindow |
| `activity_fair_arena_box_partner` | 139 | id, partner_id, name, box_id, weight, lv, grade, equips, is_new, is_up | FairArena, FairArenaCollectionWindow, FairArenaExploreWindow, FairArenaPartnerInfoWindow |
| `activity_fair_arena_level` | 11 | id, level, win_time, style, awards, score, box_partner, box_partner_elite, box_equip, box_buff … | FairArenaAwardPreviewWindow, FairArenaAwardWindow, FairArenaExploreWindow, FairArenaRecordDetailWindow, FairArenaRecordWindow |
| `activity_fair_arena_rank` | 12 | id, rank, awards, rank_front | FairArenaAwardWindow, FairArenaRankWindow |
| `activity_fair_arena_robot` | 34 | id, name, lv, server, avatar_id, show_id, partner_ids, equip_ids, buff_ids, treasure_level | FairArena, FairArenaEnemyFormationWindow, FairArenaVideoWindow |
| `activity_fairytale` | 5 | id, name, npc_id | ActivityFairyTaleCellDetailWindow |
| `activity_fairytale_battle` | 143 | id, name, avatar_id, battle_id, skill_ids, hp | ActivityFairyTaleCellDetailWindow, ActivityFairyTaleMapWindow |
| `activity_fairytale_buff` | 21 | id, buff_type, name, desc, skill, fx | ActivityFairyTaleChallengeWindow, GroupBuffDetailWindow |
| `activity_fairytale_cell` | 600 | id, map_id, cell_xy, cell_type, def_unlock, cell_content, is_main, is_point, cell_img, cell_name | ActivityFairyTaleCellDetailWindow, ActivityFairyTaleChallengeWindow, ActivityFairyTaleMain, ActivityFairyTaleMapWindow, ActivityFairyTaleSelectionWindow |
| `activity_fairytale_event` | 84 | id, day, map_id, condition_type, condition, event_type, effect, complete_value | ActivityFairyTaleMapWindow |
| `activity_fairytale_level` | 8 | id, mission_id, buff_ids, awards | ActivityFairyTaleChallengeWindow, ActivityFairyTaleGiftPreviewWindow, ActivityFairyTaleMapWindow |
| `activity_fairytale_option` | 113 | id, name, avatar_id, decision_id, hp | ActivityFairyTaleCellDetailWindow, ActivityFairyTaleMapWindow, ActivityFairyTaleSelectionWindow |
| `activity_fairytale_plot_list` | 25 | id, next_id, is_first, map_id, plot_id, chapter_icon, unlock, award | ActivityFairyTaleMapWindow, ActivityFairyTaleStoryWindow |
| `activity_fairytale_support` | 103 | id, hp, avatar_id, partner_id | ActivityFairyTaleCellDetailWindow, ActivityFairyTaleMapWindow |
| `activity_firework_shop_rank` | 4 | id, point | ActivityFireworkShopWindow |
| `activity_free_revert` | 14 | id, award_self, group_1, group_2, group_3, group_4, group_5, group_6, cost, bento_ratio … | PotentialityBackWindow |
| `activity_freebuy_awards` | 21 | id, type, day, awards | ActivityFreebuyAwardWindow |
| `activity_freebuy_giftbag` | 3 | id, cost, limit, days, awards, rate | ActivityFreebuyAwardWindow |
| `activity_growth_plan` | 14 | id, point, free_award, sp_free_award, paid_award, sp_paid_award, light_show | ActivityGrowthPlanAwardWindow, ActivityGrowthPlanWindow |
| `activity_halloween2022_gamble` | 2 | id, cost, award, weight, dropbox | ActivityHw2022SummonDetailWindow, ActivityHw2022SummonWindow |
| `activity_halloween2022_rank` | 9 | id, rank, awards, rank_front | ActivityHw2022RankWindow |
| `activity_ice_secret_boss_reward` | 9 | id, damage, reward | BattleWinWindow, BattleWindow, IceSecretBossChallengeHelpWindow |
| `activity_lafuli_buff` | 10 | id, desc, type, params, weight, text_id, icon | ActivityDriftCardWindow |
| `activity_lafuli_rudder` | 4 | id, num, awards | ActivityLafuliRudderWindow |
| `activity_legendary_skin_award` | 17 | id, desc, award, type, weight, is_special | ActivityLegendarySkinDetailWindow |
| `activity_legendary_skin_shop` | 8 | id, awards, cost, limit | ActivityLegendarySkinShopWindow |
| `activity_level_push_optional` | 36 | id, name, num, awards1, awards2, awards3 | PushActivityWindow |
| `activity_level_up` | 12 | id, level, award | FoudGiftbagPushWindow |
| `activity_limit_boss_awards` | 12 | id, damage, award | BattleWinWindow, BattleWindow, LimitCallBossAwardWindow |
| `activity_limit_partner_awards` | 6 | id, point, award | ActivityTimeLimitCallAwardWindow |
| `activity_limit_point_awards` | 8 | id, point, award | ActivityTimeLimitCallAwardWindow |
| `activity_lottery` | 12 | id, awards, type, weight, type2, show_id | ActivityRechargeLotteryBoxDetailWindow, ActivityRechargeLotteryWindow |
| `activity_luckyboxes_exchange` | 1 | id, awards, cost, limit | ActivityLuckyboxesGiftbagWindow |
| `activity_make_cake` | 5 | id, extra_awawrds, awards_1, cost_1, limit_1, awards_2, cost_2, limit_2, awards_3, cost_3 … | MakeCakeExchangeWindow |
| `activity_mission_point` | 12 | id, point, awards, effect, awards2, effect2 | ArtifactShopWarmUpAwardWindow, ArtifactShopWarmUpWindow |
| `activity_monthly_chapter` | 6 | id, desc, stage_id, map, line | ActivityMonthlyHikeAwardWindow, ActivityMonthlyHikeAwardWindow2 |
| `activity_monthly_stage` | 53 | id, desc, chapter, level, next_id, battle_id, dropbox_id, final_awards, mail_id, skill_point … | ActivityMonthlyHikeAwardWindow, ActivityMonthlyHikeAwardWindow2 |
| `activity_monthly_stage_skill` | 25 | id, desc, icon_id, area_id, place, skill_id, limit, follow_id, skill_cost, text_id | ActivityMonthlyHikeSkillDetailWindow, ActivityMonthlyHikeSkillWindow |
| `activity_new_first_recharge` | 3 | id, awards | ActivityRedeemCodeWindow, NewFirstRechargePopUpWindow |
| `activity_new_growth_plan_award` | 12 | id, point, free_award, sp_free_award, paid_award, sp_paid_award, light_show | ActivityGrowthPlanAwardWindow, ActivityGrowthPlanWindow |
| `activity_new_growth_plan_task` | 5 | id, desc, complete_value, limit, awards, activity_id, getway | ActivityGrowthPlanWindow |
| `activity_new_story` | 60 | id, next, fort_final, name, fort_id, type, point, initial_partner, battle_id, activity_plot_list_id … | BattleLoadingWindow, BattleWindow, StoryMemoryWindow |
| `activity_newbee_fund` | 30 | id, awards, cost, preview, effect, new_show | ActivityNewbeeFundAwardWindow |
| `activity_newbee_fund2` | 20 | id, awards, cost, preview, effect, new_show | ActivityNewbeeFundAwardWindow, NewbeeFundPopupWindow |
| `activity_newbee_fund3` | 20 | id, awards, cost, preview, effect, new_show | ActivityNewbeeFund3AwardWindow, NewbeeFund3PopupWindow |
| `activity_newbee_gacha` | 10 | id, point, award | NewbeeGachaPoolAwardWindow |
| `activity_newbee_gacha_new` | 10 | id, point, award | NewbeeGachaPoolAwardWindow |
| `activity_newyear_award` | 9 | id, point, item_id, awards | ActivityBaoxiangAwardWindow |
| `activity_old_building_award2` | 10 | id, rank, awards, rank_front | ActivityExploreOldCampusPVERankWindow |
| `activity_old_building_buff` | 25 | id, name, type, skill, point, icon, is_lock, cost | ActivityExploreOldCampusWayBuyWindow |
| `activity_partner_gallery_point` | 92 | partner_id, desc, id, point | ActivityPartnerGalleryDetailWindow |
| `activity_partner_jackpot` | 5 | id, partner_id, desc, partner_xy, partner_scale, dropbox_id, shop_new | ActivitySuperHeroClubPreWindow |
| `activity_pirate_plot_list` | 23 | id, title, desc, type, unlock_id, text_type, open_plot_id, icon_image, disappear_plot_id, place_id | ActivityPirateStoryListWindow |
| `activity_plot` | 5314 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | BattleWindow, StoryWindow |
| `activity_plot_fort` | 7 | id, name, desc, fort_img_id, is_show | StoryListModel, StoryListWindow |
| `activity_plot_list` | 187 | id, fort_id, name, plot_id, memory_plot_id, chapter_icon, is_show, unlock, unlock_plot_list_id, plot_text_table … | StoryListModel, ActivityAngleTeaPartyWindow, ActivityMemoryWindow, ActivityValentineRecordWindow, StoryListUnlockWindow, StoryListWindow |
| `activity_popularity_vote_award` | 7 | id, complete, awards | ActivityPopularityVoteWindow |
| `activity_popularity_vote_task` | 8 | id, mission_des, complete, award, getway, limit, display | ActivityPopularityVoteWindow |
| `activity_pray_partner` | 6 | id, awards, partner_ids, weight | ActivityAllStarsPrayHerosWindow |
| `activity_pub_mission` | 4 | id, star, complete_value, awards, getway | ActivityPointTips |
| `activity_repair_console_awards` | 176 | id, type, rank, awards, target, desc, show_award_type | ActivityRepairConsoleAwardWindow |
| `activity_return2_add` | 5 | id, desc, translation, multiple, getway_id | GameAssistant, ActivityResidentReturnGrowWindow, CampaignStageDetailWindow, DailyQuiz2Window, DailyQuizWindow, GameAssistantMarketWindow (+9) |
| `activity_return2_gift_optional` | 2 | id, num, awards1, awards2, awards3, awards4 | ActivityReturnGiftOptionalWindow |
| `activity_return2_reward` | 12 | id, point, awards, effect, awards2, effect2 | ActivityResidentReturnSupportAwardWindow, ActivityResidentReturnSupportScoreWindow, ActivityResidentReturnSupportWindow |
| `activity_return_pmission` | 15 | id, mission_desc, complete_value, award, repeat_times, go_window, go_params, rank | ActivityReturnPersonalWindow |
| `activity_return_tmission` | 9 | id, mission_desc, complete_value1, complete_value2, award1, award2, go_window, rank | ActivityReturnActiveWindow, ActivityReturnPersonalWindow |
| `activity_school_gift_exchange` | 6 | id, awards, condition_id, cost | SchoolGiftbagExchangeWindow |
| `activity_secrettreasure_award` | 100 | id, award, step, average, weight, light | ActivitySecretTreasureHuntAwardWindow |
| `activity_secrettreature_event` | 7 | id, name, weight, icon, random_type, type, dropbox, extra_item | ActivitySecretTreasureHuntEventWindow |
| `activity_shelter` | 6 | id, show_partner, show_fx, awards, partner_cost, item_cost, bg_source, partner_picture_xy, partner_picture_scale, partner_picture_offset … | ActivityShelterMissionWindow |
| `activity_smash_egg` | 3 | id, cost, dropbox_id | SmashEggAwardWindow, SmashEggDropProbabilityWindow |
| `activity_smash_egg_awards` | 19 | id, complete_value, awards | SmashEggAwardWindow |
| `activity_space_explore_map` | 200 | id, monster_id, boss_id, map_awards, place_id | ActivitySpaceExploreMapWindow, ActivitySpfarmRankWindow, NewDressRankWindow |
| `activity_space_explore_monster` | 1200 | id, name, avatar, partner_model, show_ids, atk_id, type, hp, atk, arm … | ActivitySpaceExploreBattleWindow, ActivitySpaceExploreMapWindow |
| `activity_space_explore_partner` | 27 | id, name, name1, avatar, partner_model, atk_id, grade, min_lv, max_lv, base_atk … | ActivitySpaceExploreBattleWindow, ActivitySpaceExploreMapWindow, ActivitySpaceExplorePartnerUpWindow, ActivitySpaceExploreTeamWindow |
| `activity_space_explore_place` | 30 | id, door, boss, award, monster | ActivitySpaceExploreMapWindow |
| `activity_space_explore_reward` | 14 | id, limit, reward | ActivitySpaceExploreCheckAwardWindow |
| `activity_space_explore_skill` | 21 | id, skill_desc, skill_level, type1, value | ActivitySpaceExploreMapWindow, ActivitySpaceExplorePartnerUpWindow |
| `activity_spfarm_awards` | 15 | id, level, awards | ActivitySpfarmCheckAwardWindow, ActivitySpfarmMapWindow |
| `activity_spfarm_battlepass` | 9 | id, num, free_award, paid_award | ActivitySpfarmBattlepassWindow |
| `activity_spfarm_building` | 17 | id, name, type, icon, outcome, defense, cost, cost_exchange, cost_fast | ActivitySpfarmBuildUpWindow, ActivitySpfarmBuildWindow, ActivitySpfarmMapWindow, ActivitySpfarmRecordDetailWindow |
| `activity_spfarm_policy` | 56 | id, level, type, num, cost, params, image | SpfarmPolicyShowWindow, SpfarmPolicyWindow |
| `activity_sports_achievement` | 18 | id, desc, next_achieve_id, type, complete_value, awards | ActivitySportsExchangeWindow |
| `activity_sports_energy` | 4 | id, score, max, cd | ActivitySportsFightWindow |
| `activity_sports_mission` | 3 | id, mission_des, is_limit, complete_value, award, go_window | ActivitySportsExchangeWindow |
| `activity_sports_rank_award1` | 12 | id, rank, is_percentage, awards, rank_front | ActivitySportsFightWindow, ActivitySportsRank2Window, ActivitySportsRankWindow |
| `activity_sports_rank_award2` | 9 | id, rank, awards, awards2, rank_front | ActivitySportsFightWindow, ActivitySportsRank2Window, ActivitySportsRankWindow |
| `activity_sports_rank_award3` | 6 | id, rank, awards, rank_front | ActivitySportsRank1Window |
| `activity_sports_robot` | 40 | id, name, type, lv, score, power, partner_ids, partner_lv, avatar_id, show_id … | ActivitySportsFightRecordWindow |
| `activity_spring_festival_award` | 6 | id, cost, awards, limit | ActivitySpringFestivalExchangeChooseWindow |
| `activity_sprouts_cost_award` | 13 | id, award, weight, is_height | SproutsItemAwardWindow |
| `activity_sprouts_height_award` | 24 | id, award, height | SproutsPointAwardWindow |
| `activity_sprouts_partner_award` | 6 | id, point, awards | SproutsPointAwardWindow |
| `activity_star_altar_cost` | 5 | id, num, awards | ActivityStarChargeWindow |
| `activity_star_altar_login` | 7 | id, awards | ActivityStarChargeWindow |
| `activity_star_plan_award` | 17 | id, num, awards, gamble_id | ActivityStarPlanMissionWindow |
| `activity_star_plan_gamble` | 4 | id, award, num, weight, pic, award_show | ActivityStarPlanDropboxWindow, ActivityStarPlanMissionWindow |
| `activity_study_quest` | 202 | id, quest_id, text, answer, need_level, in_use, weight, choice_num, get_way | ActivityStudyQuestionAnswerWindow |
| `activity_swimsuit_costaward` | 4 | id, award, weight | IceSummerAwardWindow |
| `activity_swimsuit_plot` | 339 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | StoryWindow |
| `activity_swimsuit_storyaward` | 7 | id, plot, award, cost, bg | IceSummerAwardWindow |
| `activity_time_gamble` | 12 | id, dropbox_id, weight, cool, is_big, show, prob | ActivityTimeGambleDropWindow |
| `activity_time_point_award` | 6 | id, awards, point | ActivityTimeMissionAwardWindow |
| `activity_tour_plot` | 470 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, scale … | StoryWindow |
| `activity_tower_fund_giftbag` | 90 | id, giftbag_id, tower_id, awards, level | FoudGiftbagPushWindow, TowerFundGiftbagWindow |
| `activity_tree_group_award` | 5 | id, point, awards | ActivityPointTips |
| `activity_trickortreat` | 6 | id, awards, weight, fall, up, down | ActivityHalloweenTrickPreviewWindow |
| `activity_valentine_plot` | 973 | id, next_id, select_next_ids, select, select_limit, end_type, day, activity_plot_list_id, plot, name … | ActivityValentineRecordWindow, StoryWindow |
| `activity_vampire_grow` | 3 | id, num, award | ActivityRecallLotteryAwakeWindow |
| `activity_warm_card_award` | 5 | id, amount, awards | WarmUpAwardWindow |
| `activity_warmup_arena_award` | 12 | id, rank, is_percentage, awards, rank_front | ActivityEntranceTestFinalRankWindow, ActivityEntranceTestRankWindow |
| `activity_warmup_arena_boss` | 3 | id, battle_id, boss_score, god_skill, desc | ActivityEntranceTestChallengeTaskWindow, ActivityEntranceTestPveWindow |
| `activity_warmup_arena_equip` | 31 | id, name, equip_id, type, rank, period | ActivityEntranceTestCrystalWindow, ActivityEntranceTestSoulWindow |
| `activity_warmup_arena_partner` | 18 | id, name, partner_id, is_newpartner, equips, equip_skill, period | ActivityEntranceTestPartnerWindow, ActivityEntranceTestPveWindow, ActivityEntranceTestSlotWindow, BattleFormationWindow, GuildCompetitionSpecialPartnerWindow |
| `activity_warmup_arena_rank` | 4 | id, name, rank_percent, star, awake, potential, lv, elite_skill, antique_lv, pet_lv … | ActivityEntranceTestRankWindow, PetDetailWindow, PetEvolutionWindow |
| `activity_warmup_arena_task` | 9 | id, energy, type, type_1, complete, desc | ActivityEntranceTestChallengeTaskWindow |
| `activity_warmup_arena_taskaward` | 9 | id, energy, awards, pack_awards, plot_id | ActivityAngleTeaPartyWindow, ActivityEntranceTestChallengeTaskWindow |
| `activity_warmup_guess_battle` | 7 | id, monster1, monster1_desc, monster2, monster2_desc | ActivityEntranceTestShowsWindow |
| `activity_warmup_guess_monster` | 39 | id, name, partner_id, crystal, antique, equip_skill, potentials | ActivityEntranceTestShowsCheckWindow |
| `activity_warmup_robot` | 24 | id, name, lv, server, show_id, rank, score, monsters, pet, avatar_id | ActivityEntranceTestEnemyWindow, ActivityEntranceTestFinalRankWindow, ActivityEntranceTestRankWindow, ActivityEntranceTestRecordWindow, BattleFailWindow, BattleWinWindow |
| `activity_wedding_vote2_rank` | 4 | id, rank1, rank2, rank3 | ActivityVoteHistoryWindow |
| `activity_wedding_vote_award` | 5 | id, complete, awards | ActivityVoteAwardWindow |
| `activity_wedding_vote_mission` | 4 | id, mission_des, complete_value, award, go_window | ActivityVoteMissionWindow |
| `activity_year_fund` | 30 | id, awards, cost, preview, effect, new_show | ActivityYearFundAwardWindow |
| `arena_all_server_award` | 4 | id, rank, award | ArenaAllServerFightAwardPreviewWindow, ArenaAllServerWindow, MailDetailWindow |
| `arena_all_server_mission` | 6 | id, type, desc, complete, awards, limit | ArenaAllServerScore, ArenaAllServerWindow |
| `arena_all_server_rank` | 22 | id, desc, level, level_num, point, season_awards, front_num, back_num, pet_num, hide_num … | ArenaAllServerNew, ArenaAllServerScore, Arena3V3ResultWindow, Arena3v3ChoosePlayerWindow, Arena3v3RecordWindow, ArenaAllScoreServerAwardWindow (+4) |
| `arena_all_server_robot` | 800 | id, name, lv, show_id, server, avatar_id, partner_ids, power, score | Arena3V3ResultWindow, Arena3v3ChoosePlayerWindow, Arena3v3RecordDetailWindow, Arena3v3RecordWindow, ArenaAllServerFormationWindow, ArenaAllServerWindow (+1) |
| `arena_rank_award_team` | 12 | id, rank, season_awards, rank_front | ArenaTeamAwardWindow |
| `battle_challenge` | 49 | id, desc, type, params | HeroChallengeFightWindow |
| `battlepass_2` | 3 | id, name, brief, core_award, pre_award | Activity |
| `battlepass_award_2` | 50 | id, cost_total, cost_bpexp, cost_diamonds, cost_dct_diamonds, free_award, paid_award, is_bigreward | Activity |
| `be_stronger` | 17 | id, title, icon, text, is_goto | EnhanceWindow |
| `beginner_quest` | 33 | id, phase_id, rank, limit_phase, limit_lev, desc, note, type, complete_value, award … | Activity, NewbieCamp, NewbieCampListWindow |
| `beginner_quest_board` | 3 | id, next_id, award, unlock_lev | NewbieCamp, NewbieCampListWindow |
| `common_trigger_guide` | 40 | id, type, mark, obj_id, no_click, record, mask_type, offset, mask_icon, icon_offset … | CommonTriggerGuideWindow |
| `custom_background_group` | 6 | id, desc, cover | Background, BackGroundWindow |
| `device_notify` | 25 | id, contents, go_to_id, delay_time, switch, priority, special_treatment, remark | Chat, DeviceNotify, ExploreModel, Map, Mission, TimeCloisterModel |
| `device_notify_category` | 6 | id, push_category, include | DeviceNotify, NotifyManagerWindow |
| `device_red_mark` | 9 | id, push_category, red_mark_types | RedMark, RedPointManagerWindow |
| `direct_monster` | 325 | id, name, type, monster_id | PartnerDataStation |
| `dog_mini_game_level` | 100 | id, bee_house, dog, awards, border, stage_id, bee_last_y | BattleFailWindow, BattleWinWindow, DogMiniGameChoiceLevelWindow, DogMiniGameWindow |
| `dog_mini_game_type` | 34 | id, desc, type, image, scale_x, angle, is_death, bee_num, obj_name, size | DogMiniGameWindow |
| `emoticon` | 24 | id, image, collection_id, words | Chat, CollectionFaceDetailWindow, CollectionFaceWindow |
| `emoticon_gif` | 51 | id, image, gif, is_show, gif_pos_zh_tw, gif_pos_en_en, gif_pos_de_de, gif_pos_fr_fr, gif_pos_jp_jp, gif_pos_ko_kr … | Chat, CollectionFaceDetailWindow, CollectionFaceWindow |
| `fight_test_partner` | 263 | id, table_id, desc, grade, level, awake, equips, love_point, is_vowed, potentials … | BattleTestWindow |
| `fight_test_team` | 424 | id, partner_ids, stands, pet, pet_grade, pet_level, pet_skill_level, pet_exskill, guild_info, god_skill … | BattleTestWindow |
| `filterword` | 2575 | id, word, ignore_case | ActivityPopularityVoteSupportMessageWindow, ArenaTeamCreateWindow, ChatWindow, ComicCommentWindow, ComicWindow, DressNewSuitWindow (+10) |
| `filterword_super` | 5 | id, word | Chat, QuestionnaireWindow |
| `friend_boss_help_award` | 5 | id, help_times, awards | FriendBossAssistAwardWindow |
| `friend_boss_new` | 12 | id, power, battle_id, dropbox_ids, avatar_id | FriendBossSwitchBossLevelWindow, FriendBossWindow, FriendWindow |
| `friend_rank` | 15 | id, rank, awards | FriendRankAwardsWindow |
| `func_guide` | 2 | id, level, award_item, award_num | Backpack |
| `galaxy_trip_battlepass2` | 12 | id, point_limit, free_awards, pay_awards, begin_season | GalaxyBattlePassWindow |
| `galaxy_trip_mission2` | 50 | id, desc, explore_points, type, complete, text_id, begin_season | GalaxyBattlePassWindow |
| `getway` | 252 | id, name, lv_limit, function_id, stage, go_window, go_params, is_close, close_win_name, lv_hide … | DeviceNotify, ActivityAngleTeaPartyWindow, ActivityCommonGetwayWindow, ActivityStudyQuestionAnswerWindow, ActivityTaskGetAwardWindows, ActivityVoteMissionWindow (+7) |
| `getway_equip` | 3558 | id, equip_id, stage_id | ItemTips |
| `getway_item` | 113 | id, name, item_id, get_limit, show_activity, lv_limit, function_id, go_window, go_params | ActivityItemGetwayWindow |
| `giftbox_optional` | 387 | id, name, stars, item | AwardSelectWindow, ChoosePartnerDebrisWindow, ChoosePartnerWindow, DropProbabilityWindow |
| `girls_img` | 4 | id, desc, resource, enter_dialog, enter_dialog_time, enter_dialog_scale, click_dialog1, click_dialog1_time, click_dialog1_scale, click_dialog2 … | ShopWindow |
| `govern_flag` | 20 | id, picture | FriendTeamBossApplyWindow, FriendTeamBossFlagWindow, FriendTeamBossTeamEditWindow, FriendTeamBossWindow |
| `govern_guide` | 16 | id, mark, obj_id, type, no_click, record, mask_type, mask_icon, icon_offset, obj_scale … | FriendTeamBossGuideWindow |
| `govern_team` | 60 | id, next_id, monster1_avater, monster1_misc, monster1_skill, monster1_skill_id, monster1_battle_id, monster1_hp, monster1_xy, monster2_avater … | BattleFailWindow, BattleWinWindow, FriendTeamBossInfoWindow, FriendTeamBossRecordWindow, FriendTeamBossWindow |
| `govern_team_award` | 60 | id, downgrade_award, relegation_award, upgrade_award | BookResearchRankWindow, FriendTeamBossAwardWindow |
| `govern_team_weather` | 11 | id, weather_name, weather_desc, weather_icon, skill, is_new | FriendTeamBossWindow |
| `growth_diary_mission` | 160 | id, desc, type, complete_value, limit, awards, activity_id, getway, chapter_id, chapter_awards … | GrowthDiary, GrowthDiaryWindow |
| `guild_boss_rank` | 7 | id, rank, name, show | GuildBossAwardWindow, GuildBossHistoryWindow, GuildFinalBossRankWindow |
| `guild_competition_active_award` | 4 | id, awards, value | GuildCompetitionActiveWindow |
| `guild_competition_boss` | 10 | id, next_id, battle_awards, kill_awards, point, battle_id1_1, battle_challenge1_1, battle_skill1_1, skill_tips1_1, battle_id2_1 … | Guild, BattleWinWindow, GuildCompetitionFightWindow |
| `guild_competition_group_rank` | 14 | id, rank, awards, frame, is_percentage, show | GuildCompetitionBossRankWindow |
| `guild_competition_mission` | 8 | id, brief, complete_value, limit, awards, active, type | GuildCompetitionActiveWindow |
| `guild_competition_personal_rank` | 4 | id, rank, show, awards | GuildCompetitionBossRankWindow |
| `guild_new_war_base` | 6 | id, desc, type, flag_num, skill_id, guild_points, attack_win_awards, attack_lose_awards, sweep_awards, flag_awards … | GuildNewWarDestroyResultWindow, GuildNewWarDestroyWindow, GuildNewWarFightInfoWindow, GuildNewWarPreviewWindow, GuildNewWarSetDefPlayerWindow |
| `guild_new_war_guild_rank` | 12 | id, rank, rank_front, season_awards, mail_id | GuildNewWarRankWindow |
| `guild_new_war_message` | 4 | id, string, explanation, connect_type | GuildNewWarFightInfoWindow |
| `guild_new_war_person_rank` | 6 | id, rank, rank_front, person_awards, mail_id | GuildNewWarRankWindow |
| `guild_new_war_pk_awards` | 1 | id, win_awards, lose_awards | GuildNewWarSeasonResultWindow, GuildNewWarVsTotalWindow |
| `guild_war_point_award` | 12 | id, rank, season_awards, rank_front, awards_1, awards_2, awards_3 | GuildWarAwardWindow |
| `house_dialog` | 179 | id, name, dialog, length | HouseDialog |
| `house_dialog_list` | 95 | id, group, dialog, type, value, is_move, move_end_action, flip | HouseDialog |
| `house_furniture_effect` | 44 | id, name, effect_name, scale, pos, hero_pos, count, action, next_action, type … | HouseItem |
| `house_guide` | 7 | id, mark, obj_id, no_click, record, mask_type, mask_icon, icon_offset, obj_scale, hand_type … | HouseWindow |
| `house_partner` | 747 | id, name, is_ride, sit_pos_offset, lie_pos_offset, idle_pos_offset, house_idle_num | HouseHero, HouseMap, HouseSelectHerosWindow |
| `img_guide` | 14 | name, prename, guide_number, guide_size, hide_mask, skin_name, label_number, label_name, icon_number | ImgGuideWindow |
| `item_exchange` | 9 | id, desc, title, cost, item | ItemPurchaseWindow |
| `new_player_activity_tips` | 3 | id, desc, item_id, cost, awards, activity_id, days | NewPlayerTipsWindow |
| `new_trial_battlepass_awards` | 30 | id, exp, free_award, free_optional_award, paid_optional_award, paid_award | NewTrialBattlepassCheckAwardWindow, NewTrialBattlepassCheckAwardWindow2, NewTrialBattlepassSelectAwardWindow |
| `new_trial_plot` | 8 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, scale … | StoryWindow |
| `old_building_a_award2` | 10 | id, rank, awards, frame_awards, rank_front | OldSchool |
| `old_building_award3` | 10 | id, rank, awards, rank_front | OldSchoolHarmRankWindow |
| `old_building_award3_point` | 50 | id, rank, point | OldSchool, OldSchoolHarmRankWindow |
| `old_building_b_award2` | 10 | id, rank, awards, frame_awards, rank_front | OldSchool |
| `old_building_buff` | 22 | id, name, type, skill, point, icon, is_lock, cost, buff_belong | ActivityExploreCampusFightWindow, ActivityExploreOldCampusPVECheckBuffWindow, ActivityExploreOldCampusWaysWindow |
| `old_building_shop1` | 15 | id, item, desc, point, cost, buy_time | OldSchoolShopWindow |
| `old_building_shop2` | 36 | id, item, desc, num, point, cost, buy_time | OldSchoolShopWindow |
| `partner_4up5` | 38 | id, id_4, name | Backpack |
| `partner_challenge_chess` | 40 | id, next_id, fort_first, fort_id, type, skill_ids, initial_partner, box_id, grade_weight, battle_id … | HeroChallenge, BattleFormationWindow, BattleWindow, HeroChallengeDetailWindow, HeroChallengeFightWindow, HeroChallengeMemoryWindow (+3) |
| `partner_challenge_speed` | 10 | id, battle_id, skill_ids, reward, chapter_icon, fort_img | BattleFormationWindow, BattleWindow, HeroChallengeWindow |
| `partner_exskill` | 416 | id, ex_id, desc_num1, desc_num2, desc_num3, desc_num4, desc_num5, desc_num6, desc_num7, desc_num8 … | Partner, ExSkillGradeUpWindow, ExSkillPreviewWindow, FairArenaPartnerInfoWindow, GuideDetailWindow, PartnerDetailWindow (+3) |
| `partner_exskill_guide` | 7 | id, mark, obj_id, no_click, record, mask_type, mask_icon, icon_offset, obj_scale, hand_type … | ExskillGuideWindow, PartnerDetailWindow |
| `partner_id_rule` | 462 | id, star, group, job, icon, icon_frame | ShenXue, Slot, ActivityShelterMissionSelectWindow, ActivityShelterMissionWindow, BatchAwakeWindow, BatchShenXueWindow (+5) |
| `partner_name_translation` | 179 | id, name_zh_tw, name_en_en, name_ja_jp, name_fr_fr, name_ko_kr, name_de_de | ACDFA |
| `partner_recommend_simulation` | 15 | id, partner_id, name | ActivitySimulationGachaExchangeWindow, ActivitySimulationGachaRecordWindow, SummonResultWindow |
| `partner_warmup` | 3 | id, next_id, fort_first, partner_id, initial_partner, stands, battle_id, reward, plot_id, unlock_day | BattleFailWindow, BattleWinWindow, BattleWindow, NewPartnerWarmingUpEntryWindow, NewPartnerWarmupPreviewWindow |
| `partner_warmup_award` | 5 | id, amount, awards | NewPartnerWarmingUpEntryWindow |
| `partner_warmup_plot` | 5170 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | StoryWindow |
| `pet_exskill_guide` | 5 | id, mark, obj_id, no_click, record, mask_type, mask_icon, icon_offset, obj_scale, hand_type … | PetDetailWindow |
| `pet_story` | 12 | id, pet_id, unlock_value | PetSlot |
| `pet_training` | 10 | id, exp | PetTraining, PetTrainingWindow |
| `pet_training_boss` | 10 | id, level, battle_awards, final_awards, hp | PetTraining, GameAssistantResultWindow, PetTrainingBossAwardWindow, PetTrainingBossSelectWindow, PetTrainingWindow |
| `pet_training_lesson` | 15 | id, name, level, awards, time, rank_unlocked | PetTraining, PetTrainingLessonDetailWindow, PetTrainingLessonWindow |
| `pet_training_new_awards` | 10 | id, awards1, awards2, time, desc | GameAssistant, PetTraining, PetTrainingDetail2Window, PetTrainingWindow |
| `player_language` | 7 | id, true_name, name, match_id, language_code, true_language_code, display, time_stamp | Chat, Guild, SelfPlayer, SettingUp, ChangeLanguageWindow, GuildApplyDetailWindow (+3) |
| `player_return_story` | 7 | id, next_id, select_next_ids, select, plot, name, is_memory, res_path, scale, partner_picture_xy … | StoryWindow |
| `questionnaire` | 382 | id, next_id, this_number, type, question_type, options, is_first, is_optional, is_jump, jump_to_id … | QuestionnaireStartWindow, QuestionnaireWindow, SettingUpWindow |
| `questionnaire_options` | 1168 | id, is_fillable, lang_hide | QuestionnaireWindow |
| `resource_effect` | 797 | name, res_name | BattleLoadingWindow, BattleWindow, LoginLoadingWindow |
| `school_practise` | 600 | id, next_id, school_sort, fort_first, fort_id, battle_id1, battle_id2, battle_id3, first_reward, sweep_reward … | AcademyAssessment, AcademyAssessmentDetailWindow, AcademyAssessmentRankWindow |
| `school_practise_frame` | 6 | id, award | AcademyAssessmentFinalRankWindow, AcademyAssessmentRankWindow2 |
| `school_practise_guide` | 8 | id, mark, obj_id, no_click, record, mask_type, mask_icon, icon_offset, obj_scale, hand_type … | AcademyAssessmentGuideWindow |
| `school_practise_new` | 480 | id, next_id, school_sort, fort_first, fort_id, battle_id1, battle_id2, battle_id3, first_reward, sweep_reward … | AcademyAssessment, AcademyAssessmentDetailWindow2, AcademyAssessmentWindow, BattleWinWindow, OneClickClearanceWindow |
| `school_practise_point` | 19 | id, point, point_text, award | AcademyAssessment |
| `school_practise_point_2` | 11 | id, point, point_text, award | AcademyAssessment |
| `server_map` | 995 | id, host_1, id_text, host_trial, host_arena, host_team, host_32, host_guild_war, host_chat, server_name … | FriendTeamBossInviteFriendsWindow, GuildApplyDetailWindow |
| `shop_battlepass_2` | 21 | id, type, item, desc, cost, buy_time, shelf | Activity |
| `shop_hero_new` | 80 | id, item, cost, rank, name, group, shop_new | Shop, ShopWindow |
| `shop_school_practise` | 8 | id, item, cost, desc, num_choose | ShopWindow |
| `shrine_plot` | 1410 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | StoryWindow |
| `skin_show_stage` | 324 | id, battle_id1, battle_id2, battle_scens | GuideDetailWindow, ItemTips |
| `soul_land_battlepass_awards` | 30 | id, exp, free_award, paid_award | SoulLandBattlePass, SoulLandBattlePassBuyWindow |
| `time_cloister_battle_rank` | 30 | id, rank, is_percentage, awards, rank_front, rank_front_mail, group | CommonRankWithAwardWindow, MailDetailWindow, TimeCloisterBattleRankWindow |
| `time_cloister_crystal_buff` | 4 | id, cloister, items, tec_id, num | TimeCloisterModel, TimeCloisterCrystalCardBuyWindow, TimeCloisterCrystalChoiceWindow |
| `time_cloister_crystal_card` | 480 | id, next_id, level, card_num, cost, point, skill, img, cloister, type | TimeCloisterModel, TimeCloisterCrystalBattleCardWindow, TimeCloisterCrystalCardBuyWindow, TimeCloisterCrystalDetailWindow |
| `time_cloister_crystal_point` | 61 | id, point, base1, base2, base3 | TimeCloisterCrystalCardBuyWindow, TimeCloisterCrystalShowNextWindow |
| `time_cloister_dress_mission` | 120 | id, pos, type, num | TimeCloisterShowDressWindow |
| `time_cloister_guide` | 47 | id, type, mark, obj_id, no_click, record, mask_type, offset, mask_icon, icon_offset … | ArcticExpeditionCellWindow, ArcticExpeditionMainWindow, TimeCloisterCardRecordWindow, TimeCloisterMainWindow, TimeCloisterProbeWindow |
| `time_cloister_partner` | 12 | id, level, table_id, grade, awake | BattleFormationWindow, TimeCloisterHelpPartnerWindow |
| `tips_activity_point` | 8 | id, activity_id, title, point, content, connect_type | ActivityPointTips, ActivityPointTipsWindow |
| `trial_node` | 5 | id, stage_node, awards | TrialAwardWindow |
| `window_go` | 178 | id, name, params, activity_id, function_id, desc | FloatMessageWindow, MailDetailWindow, NewNoticeWindow |
| `window_go_operation_map` | 177 | id, desc, type, value, go_window_id | FloatMessageWindow, MailDetailWindow |
| `activity_2birthday_cake` | 16 | id, awards | Sin acceso estático detectado |
| `activity_2birthday_cake_end` | 25 | id, awards | Sin acceso estático detectado |
| `activity_3birthday_dinner` | 2 | id, cost, awards, weight, get, dropbox_id | Sin acceso estático detectado |
| `activity_3birthday_dinner_point` | 16 | id, point, awards | Sin acceso estático detectado |
| `activity_3birthday_gamble` | 33 | id, type, weight, awards, num | Sin acceso estático detectado |
| `activity_4anniversary_sign` | 12 | id, awards, is_show | Sin acceso estático detectado |
| `activity_4birthday_award` | 20 | id, type, num, awards | Sin acceso estático detectado |
| `activity_4birthday_task_award` | 12 | id, awards, cost | Sin acceso estático detectado |
| `activity_5week_giftbag` | 3 | id, awards, pre_giftbag_id, pre_award_id | Sin acceso estático detectado |
| `activity_angelteaparty_award` | 4 | id, point, awards, plot_id, battle_id | Sin acceso estático detectado |
| `activity_beach_awards` | 7 | id, point, buy_cost, awards_1, awards_2 | Sin acceso estático detectado |
| `activity_beach_boss` | 8 | id, hp, modle, queue, queue_rate, point | Sin acceso estático detectado |
| `activity_beach_matchup` | 148 | id, type, matchup, weight | Sin acceso estático detectado |
| `activity_birthday_colour` | 20 | id, colour | Sin acceso estático detectado |
| `activity_birthday_colour_award` | 5 | id, complete, awards | Sin acceso estático detectado |
| `activity_black_card` | 4 | id, award, multiply_type | Sin acceso estático detectado |
| `activity_blind_box_battlepass` | 14 | id, awards1, awards2, awards3 | Sin acceso estático detectado |
| `activity_boss_award` | 22 | id, rank, awards | Sin acceso estático detectado |
| `activity_boss_type` | 3 | id, start_id | Sin acceso estático detectado |
| `activity_card` | 10 | id, name, award, num, weight, is_big | Sin acceso estático detectado |
| `activity_christmas_socks` | 10 | id, award, weight, icon_png | Sin acceso estático detectado |
| `activity_christmas_socks_award` | 14 | id, complete, award | Sin acceso estático detectado |
| `activity_christmas_socks_change` | 30 | id, award, cost1, cost2, limit, type, level, share | Sin acceso estático detectado |
| `activity_christmas_socks_level` | 7 | id, level, award | Sin acceso estático detectado |
| `activity_compose_10` | 2 | id, star, limit, awards, mail_id | Sin acceso estático detectado |
| `activity_countdown_awards` | 24 | id, type, dropbox_id, giftbag_id | Sin acceso estático detectado |
| `activity_course_learning` | 7 | id, level, awards | Sin acceso estático detectado |
| `activity_course_learning_2` | 7 | id, level, awards | Sin acceso estático detectado |
| `activity_crystal_gift` | 1 | id, awards, cost, limit | Sin acceso estático detectado |
| `activity_cupid_gift_award` | 3 | id, award, draw_times | Sin acceso estático detectado |
| `activity_cv` | 7 | id, name, click_sound, time_sound, start_pos, picture_path, outline_path, outline_pos | Sin acceso estático detectado |
| `activity_date_battle_cell` | 128 | id, brief, battle_id, favor_award, effect_id, key_award, awards, lose_scale | Sin acceso estático detectado |
| `activity_date_boss` | 9 | id, brief, battle_id, partner_id, need_favor, awards, buff_lv, boss_img, boss_id | Sin acceso estático detectado |
| `activity_date_buff` | 3 | id, brief, desc, effect_lv, skill | Sin acceso estático detectado |
| `activity_date_cell` | 220 | id, next_id, map_id, is_first, cell_xy, cell_type, action_id, partner_id, cell_img, cell_name … | Sin acceso estático detectado |
| `activity_date_chat_cell` | 45 | id, brief, childcell_id | Sin acceso estático detectado |
| `activity_date_chat_childcell` | 135 | id, brief, cell_chat_id, plot_id, decision_id | Sin acceso estático detectado |
| `activity_date_decision` | 165 | id, brief, plot_id, options_id, memory_options_id, section_icon, decision_icon | Sin acceso estático detectado |
| `activity_date_earn_cell` | 15 | id, brief, decision_id | Sin acceso estático detectado |
| `activity_date_map` | 10 | id, name, partner_id, partner_name, need_favor, start_cell_id, image_path | Sin acceso estático detectado |
| `activity_date_memory` | 45 | id, brief, partner_id, decision_id, chapter_img, location | Sin acceso estático detectado |
| `activity_date_options` | 474 | id, brief, decision_id, plot_id, earn_id, cost, favor_award, effect_id, awards, is_memory | Sin acceso estático detectado |
| `activity_date_plot1` | 1112 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, scale … | Sin acceso estático detectado |
| `activity_date_plot2` | 418 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, scale … | Sin acceso estático detectado |
| `activity_doll_exchange` | 18 | doll_id, item_cost, awards, show | Sin acceso estático detectado |
| `activity_dragon_boat` | 4 | id, award0, award1, award2, award3, limit | Sin acceso estático detectado |
| `activity_dragonboat2022` | 13 | id, awards, num | Sin acceso estático detectado |
| `activity_dress_gacha_award` | 8 | id, desc, type, rank, qlt, point, star, award | Sin acceso estático detectado |
| `activity_duanwu_chosen_award` | 5 | id, awards1, awards2, num | Sin acceso estático detectado |
| `activity_easter_egg` | 7 | id, type, desc, awards, image, item_id | Sin acceso estático detectado |
| `activity_encounter_story` | 5 | id, type, cost, text_id | Sin acceso estático detectado |
| `activity_ept_buff_daily` | 12 | id, name, buff, icon | Sin acceso estático detectado |
| `activity_ept_group` | 4 | id, group_name, icon, pos_initial, netural | Sin acceso estático detectado |
| `activity_ept_labor` | 4 | id, name, labor_value, debuff | Sin acceso estático detectado |
| `activity_ept_message` | 7 | id, string, explanation, range, channel, connect_type | Sin acceso estático detectado |
| `activity_ept_server_map` | 995 | id, id_text, host, group | Sin acceso estático detectado |
| `activity_equip_gacha` | 5 | id, point, awards | Sin acceso estático detectado |
| `activity_equip_gacha_task` | 3 | id, task_desc, complete_value, limit, award | Sin acceso estático detectado |
| `activity_equip_level_antique` | 75 | id, awards, desc, type, qlt1, cost, cost2, cost3, limit, reverse … | Sin acceso estático detectado |
| `activity_factory` | 12 | id, name, belong_id, awards, cost, limit | Sin acceso estático detectado |
| `activity_fairytale_award1` | 7 | id, damage, award | Sin acceso estático detectado |
| `activity_fairytale_award2` | 6 | id, level, point1, point2, award1, award2 | Sin acceso estático detectado |
| `activity_fairytale_award3` | 20 | id, name, award, point | Sin acceso estático detectado |
| `activity_fairytale_sell` | 54 | id, map_id, cell_xy, cell_type, def_unlock, cell_content, is_main, is_point, cell_img, cell_name | Sin acceso estático detectado |
| `activity_festival_chose` | 3 | id, num, awards | Sin acceso estático detectado |
| `activity_festival_in_file1` | 7 | id, awards, condition_id, cost | Sin acceso estático detectado |
| `activity_festival_in_file2` | 7 | id, awards, condition_id, cost | Sin acceso estático detectado |
| `activity_festival_login` | 12 | id, award, cost | Sin acceso estático detectado |
| `activity_firework_award` | 8 | id, award, weight | Sin acceso estático detectado |
| `activity_firework_rank_award` | 18 | id, awards, point | Sin acceso estático detectado |
| `activity_fish_surprise` | 6 | id, fish, length, awards | Sin acceso estático detectado |
| `activity_fit_up_dorm` | 3 | id, slot_num, awards_1, cost_1, pic_1, awards_2, cost_2, pic_2, awards_3, cost_3 … | Sin acceso estático detectado |
| `activity_food_consume` | 9 | id, type, cost, award, limit, bento_num, exp, gold_grade, gold_crystal, crystal … | Sin acceso estático detectado |
| `activity_gacha_new_server` | 3 | id, point, awards | Sin acceso estático detectado |
| `activity_gacha_partner_award` | 6 | id, point, award | Sin acceso estático detectado |
| `activity_gamble_plus` | 7 | id, point, awards, ex_awards | Sin acceso estático detectado |
| `activity_giftbag_optional` | 3 | id, num, awards | Sin acceso estático detectado |
| `activity_graduate_gift` | 15 | id, star, awards, cost, giftbag_id, limit_times | Sin acceso estático detectado |
| `activity_guard` | 7 | id, name, res_path, scale, partner_picture_xy, image_path, type, next_id, switch_type | Sin acceso estático detectado |
| `activity_halloween2022_award` | 22 | id, awards, complete_value | Sin acceso estático detectado |
| `activity_halloween2022_giftbag` | 5 | id, num, award, giftbag, open_time | Sin acceso estático detectado |
| `activity_house` | 3 | id, awards, cost, limit | Sin acceso estático detectado |
| `activity_invitation_all_award` | 10 | id, desc, parameter, awards_new, awards_senpai, point | Sin acceso estático detectado |
| `activity_invitation_old_award` | 10 | id, complete_value, awards, point | Sin acceso estático detectado |
| `activity_jackpot_gamble` | 24 | id, type, awards, weight, num | Sin acceso estático detectado |
| `activity_jackpot_point` | 7 | id, point, awards | Sin acceso estático detectado |
| `activity_keyboard_award` | 39 | id, award, weight, type, is_big_award, level, unlock | Sin acceso estático detectado |
| `activity_legendary_skin` | 1 | id, skin_award, cost, skin, skin_xy, skin_xy2, skin_scale, type | Sin acceso estático detectado |
| `activity_lflcastle_award` | 14 | id, award, count, type | Sin acceso estático detectado |
| `activity_lflcastle_progress` | 10 | id, progress, object, count, type | Sin acceso estático detectado |
| `activity_limited_task_award` | 5 | id, desc, master_mission, sub_mission, complete_value, awards | Sin acceso estático detectado |
| `activity_love_point` | 2 | id, point, limit, awards, mail_id | Sin acceso estático detectado |
| `activity_making_coffee` | 5 | id, award, point, limit, time, unlock | Sin acceso estático detectado |
| `activity_making_coffee_award` | 6 | id, bench, point, award, unlock_item | Sin acceso estático detectado |
| `activity_month_gift` | 1 | id, name, award, cost, limit | Sin acceso estático detectado |
| `activity_monthly_total` | 7 | id, type, point, awards, ex_awards, desc, mail_id, ex_mail_id, hide | Sin acceso estático detectado |
| `activity_music_day` | 20 | id, complete_value, unlocking_time, awards | Sin acceso estático detectado |
| `activity_music_day_award` | 9 | id, rank, awards, rank_front | Sin acceso estático detectado |
| `activity_music_game` | 30 | id, music, name, difficulty, next_id, next_unlock, bpm, max_hit, background, default_hero … | Sin acceso estático detectado |
| `activity_music_game_stage` | 7826 | id, stage_id, start, end, type, pos, tap, color, chara | Sin acceso estático detectado |
| `activity_music_game_stage1` | 6667 | id, stage_id, start, end, type, pos, tap, color, chara | Sin acceso estático detectado |
| `activity_music_game_stage2` | 1159 | id, stage_id, start, end, type, pos, tap, color, chara | Sin acceso estático detectado |
| `activity_music_plot_random` | 5 | id, plot_sort | Sin acceso estático detectado |
| `activity_new_story_award` | 6 | id, complete, awards | Sin acceso estático detectado |
| `activity_new_story_stage` | 227 | id, type, stage_belong, offsetX, offsetY | Sin acceso estático detectado |
| `activity_new_trial_boss_reward` | 10 | id, damage_to_boss, rewards, rewards_on_account | Sin acceso estático detectado |
| `activity_new_trial_buff` | 15 | id, name, desc, buff_type, skill_ids, icon | Sin acceso estático detectado |
| `activity_new_trial_offset` | 26 | id, type, stage_belong, offsetX, offsetY | Sin acceso estático detectado |
| `activity_new_trial_stage` | 9 | id, type, power, step, rewards, buff_id, battle_id, battle_scens | Sin acceso estático detectado |
| `activity_newbee_lesson` | 99 | id, desc, type, day_limit, complete_value, award, getway | Sin acceso estático detectado |
| `activity_newbee_lesson_2` | 99 | id, desc, type, day_limit, complete_value, award, getway | Sin acceso estático detectado |
| `activity_newyear_welfare` | 16 | id, type, item, cost, limit, desc | Sin acceso estático detectado |
| `activity_nsshaft_award1` | 5 | id, complete, awards | Sin acceso estático detectado |
| `activity_nsshaft_award2` | 9 | id, rank, awards, rank_front | Sin acceso estático detectado |
| `activity_nsshaft_stage` | 0 | id, stage_id, type, line_x | Sin acceso estático detectado |
| `activity_old_building` | 10 | id, area, stage, awards | Sin acceso estático detectado |
| `activity_old_building_area` | 3 | id, floor, awards, buff, time | Sin acceso estático detectado |
| `activity_old_building_award1` | 10 | id, point, awards | Sin acceso estático detectado |
| `activity_old_building_stage` | 25 | id, name, area, floor, level, battle_id, point, partner_id | Sin acceso estático detectado |
| `activity_partner_gallery_award` | 5 | id, point, awards | Sin acceso estático detectado |
| `activity_partner_miracle` | 7 | id, group_type, complete_value, awards, rank | Sin acceso estático detectado |
| `activity_pay_day_awards1` | 15 | id, awards, weight | Sin acceso estático detectado |
| `activity_pay_day_awards2` | 15 | id, awards, weight | Sin acceso estático detectado |
| `activity_pet_task` | 6 | id, type, desc, complete, awards, mail_id | Sin acceso estático detectado |
| `activity_plot1` | 1112 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | Sin acceso estático detectado |
| `activity_plot2` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | Sin acceso estático detectado |
| `activity_plot3` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | Sin acceso estático detectado |
| `activity_plot4` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | Sin acceso estático detectado |
| `activity_plot5` | 869 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, spine_path … | Sin acceso estático detectado |
| `activity_plot_finish` | 2 | id, fort, awards | Sin acceso estático detectado |
| `activity_popularity_vote_list` | 93 | id, show_ids, name, group | Sin acceso estático detectado |
| `activity_pray_award` | 11 | id, complete, awards | Sin acceso estático detectado |
| `activity_pray_cost` | 6 | id, cost, get, merge, omni_get, award | Sin acceso estático detectado |
| `activity_pray_gift` | 1 | id, awards, cost, limit | Sin acceso estático detectado |
| `activity_promotion_test` | 5 | id, point, free_awards, extra_awards, condition | Sin acceso estático detectado |
| `activity_recharge` | 10 | id, point, awards, is_new | Sin acceso estático detectado |
| `activity_red_riding_hood` | 1 | id, daily_awards, cost, limit, days | Sin acceso estático detectado |
| `activity_relay_gift` | 3 | id, awards, pre_giftbag_id, pre_award_id | Sin acceso estático detectado |
| `activity_ring_giftbag` | 1 | id, logo_side, logo_scale, time_y, buy_side, model, model_xy, model_scale, item_id, model_side … | Sin acceso estático detectado |
| `activity_sakura_date_award` | 6 | id, complete, awards | Sin acceso estático detectado |
| `activity_school_explore` | 9 | id, name, unlock, xy, time, event_ids, weight, awards1, awards2 | Sin acceso estático detectado |
| `activity_school_explore_award` | 5 | id, complete, awards | Sin acceso estático detectado |
| `activity_school_explore_award1` | 5 | id, complete, awards | Sin acceso estático detectado |
| `activity_school_explore_award2` | 182 | id, name, award, add_time | Sin acceso estático detectado |
| `activity_school_explore_event` | 109 | id, name, options_id, type, coefficient | Sin acceso estático detectado |
| `activity_school_gift` | 3 | id, daily_awards, unlock_type | Sin acceso estático detectado |
| `activity_search_book` | 6 | id, type, complete_value, awards, desc, getway | Sin acceso estático detectado |
| `activity_secrettreasure_gift` | 1 | id, awards, desc, cost, limit, dynamic_limit | Sin acceso estático detectado |
| `activity_server_open` | 7 | id, awards | Sin acceso estático detectado |
| `activity_shop_hero` | 4 | id, item, cost, desc | Sin acceso estático detectado |
| `activity_shop_new_trial` | 16 | id, stage_id, item, weight, cost | Sin acceso estático detectado |
| `activity_simulation_gacha` | 11 | id, weight, dropbox1, dropbox2, dropbox3, dropbox4, desc, is_guarantee, guarantee_weight | Sin acceso estático detectado |
| `activity_spfarm_dialog` | 8 | id, time, level, content | Sin acceso estático detectado |
| `activity_spfarm_match` | 9 | id, interval, coefficient1, step1, coefficient2, step2 | Sin acceso estático detectado |
| `activity_sports_achv_type` | 4 | id, start_achievement, end_achievement, desc, type, show_rank, show_rank_done | Sin acceso estático detectado |
| `activity_sports_battle_award` | 5 | id, score, bonus, item_id | Sin acceso estático detectado |
| `activity_sports_point` | 5 | id, interval, coefficient | Sin acceso estático detectado |
| `activity_sports_pvpscore` | 10 | id, interval, coefficient | Sin acceso estático detectado |
| `activity_spring_festival_point` | 6 | id, point, awards | Sin acceso estático detectado |
| `activity_spring_festival_task` | 4 | id, desc, complete, limit, awards | Sin acceso estático detectado |
| `activity_spring_giftbag` | 4 | id, num, awards1, awards2 | Sin acceso estático detectado |
| `activity_sprouts_mission` | 1 | id, mission_desc, complete_value, award, limit | Sin acceso estático detectado |
| `activity_study_award` | 9 | id, award, quest, row, col | Sin acceso estático detectado |
| `activity_study_score` | 36 | id, partner_name, partner_id, score, in_use, unity_offset, scale | Sin acceso estático detectado |
| `activity_swimsuit_mission` | 2 | id, mission_desc, complete_value, award, limit | Sin acceso estático detectado |
| `activity_table_list` | 341 | id, tables | Sin acceso estático detectado |
| `activity_therm_story` | 30 | id, next, fort_final, name, fort_id, type, point, initial_partner, is_battle, battle_id … | Sin acceso estático detectado |
| `activity_therm_story_award` | 3 | id, complete, awards | Sin acceso estático detectado |
| `activity_therm_story_stage` | 99 | id, type, stage_belong, offsetX, offsetY | Sin acceso estático detectado |
| `activity_time_mission_tab` | 7 | time, id | Sin acceso estático detectado |
| `activity_time_partner_award` | 6 | id, point, awards | Sin acceso estático detectado |
| `activity_tour` | 8 | id, plot_id, res_path, position_xy, titleSort, layer | Sin acceso estático detectado |
| `activity_tour_item` | 26 | id, name, type, cost, contribute | Sin acceso estático detectado |
| `activity_trickortreat_awards` | 32 | id, complete, awards | Sin acceso estático detectado |
| `activity_valentine_awards` | 5 | id, item | Sin acceso estático detectado |
| `activity_vampire_battlepass` | 20 | id, cost_total, cost_exp, free_award, paid_award | Sin acceso estático detectado |
| `activity_vampire_gamble` | 6 | id, prob, prob_add, cost, award, weight, bigaward_show | Sin acceso estático detectado |
| `activity_warmup_arena_match` | 8 | id, interval, coefficient1, step1, coefficient2, step2 | Sin acceso estático detectado |
| `activity_warmup_arena_score` | 11 | id, interval, coefficient | Sin acceso estático detectado |
| `activity_warmup_robot_monster` | 44 | id, name, partner_id, crystal, antique, equip_skill, potentials | Sin acceso estático detectado |
| `activity_wedding_vote2_award` | 5 | id, complete, awards | Sin acceso estático detectado |
| `activity_wedding_vote2_list` | 76 | id, name, show_ids, group, rank, partner_picture_scale, partner_picture_offset | Sin acceso estático detectado |
| `activity_wedding_vote2_mission` | 5 | id, mission_des, complete_value, award1, award2, award3, getway, go_window | Sin acceso estático detectado |
| `activity_wedding_vote_list` | 133 | id, name, show_ids | Sin acceso estático detectado |
| `activity_week_award1` | 3 | id, day_limit, label, mission_detail, awards, award2, cost, limit | Sin acceso estático detectado |
| `activity_week_buy` | 21 | id, day_limit, desc | Sin acceso estático detectado |
| `activity_week_exchange` | 21 | id, day_limit, label, mission_detail, type, awards, award2, cost, limit, vip_limit | Sin acceso estático detectado |
| `activity_week_free` | 7 | id, day_limit, desc, awards, limit | Sin acceso estático detectado |
| `activity_week_mission` | 105 | id, day_limit, type, text_type, data_type, label, mission_detail, complete_show, complete_value, award … | Sin acceso estático detectado |
| `activity_week_score` | 4 | id, point, awards | Sin acceso estático detectado |
| `annual_report` | 30 | id, 描述, 类型 | Sin acceso estático detectado |
| `arena_all_server_attr_ratio` | 11 | id, star, ratio | Sin acceso estático detectado |
| `arena_all_server_match` | 16 | id, interval, coefficient1, step1, coefficient2, step2 | Sin acceso estático detectado |
| `arena_all_server_score` | 21 | id, interval, coefficient, challenged | Sin acceso estático detectado |
| `arena_battle_award_all_server` | 12 | id, level_begin, level_end, dropbox_id | Sin acceso estático detectado |
| `arena_rank_new_award` | 14 | id, rank, awards, season_awards, rank_front, frame_id | Sin acceso estático detectado |
| `arena_rank_new_award2` | 14 | id, rank, awards, season_awards, rank_front, frame_id | Sin acceso estático detectado |
| `arena_sport_match` | 13 | id, interval, coefficient1, step1, coefficient2, step2 | Sin acceso estático detectado |
| `battle1` | 8572 | id, monsters, stands, map, boss_map, boss_map_xy, boss_map_scale | Sin acceso estático detectado |
| `battle2` | 310 | id, monsters, stands, map, boss_map, boss_map_xy, boss_map_scale | Sin acceso estático detectado |
| `battle_target` | 141 | id, target, type, no_change, random_enemy | Sin acceso estático detectado |
| `battle_trigger` | 186 | id, trigger, desc, is_god_skill, limit_times, is_die_pas, is_hp_pas, is_can_use_by_pas, round_limit_times | Sin acceso estático detectado |
| `cost_return_treasure` | 23 | id, cost | Sin acceso estático detectado |
| `cost_total_grade` | 10 | id, cost, gold | Sin acceso estático detectado |
| `cost_total_treasure` | 23 | id, cost | Sin acceso estático detectado |
| `custom_background_unlock` | 13 | id, description, type | Sin acceso estático detectado |
| `daily_mail_award` | 63 | id, award, multiply_type | Sin acceso estático detectado |
| `dropbox1` | 10001 | id, name, dropbox_id, weight, item, cost | Sin acceso estático detectado |
| `dropbox2` | 6386 | id, name, dropbox_id, weight, item, cost | Sin acceso estático detectado |
| `dynamic_gift_item` | 4 | id, award_item_id, times, type | Sin acceso estático detectado |
| `equip_levelup_guide` | 3 | id, obj_id, obj_type, hand_offset | Sin acceso estático detectado |
| `friend_boss` | 13 | id, weight, lv, type, search_dropbox_id, battle_id, battle_dropbox_ids, final_award, kill_award, coefficient … | Sin acceso estático detectado |
| `fx1` | 2069 | id, type, next_texiao, res_name, res_path, texiao_name, texiao_is_pos, target_pos, is_loop, retain … | Sin acceso estático detectado |
| `fx2` | 160 | id, type, next_texiao, res_name, res_path, texiao_name, texiao_is_pos, target_pos, is_loop, retain … | Sin acceso estático detectado |
| `galaxy_trip_difficulty` | 12 | id, atkP, hpP | Sin acceso estático detectado |
| `galaxy_trip_match` | 6 | id, power1, step1 | Sin acceso estático detectado |
| `gift_double` | 33 | id, name, awards | Sin acceso estático detectado |
| `giftcode_group` | 39 | id, player_created_time, gift_id, type, min_map_id | Sin acceso estático detectado |
| `giftcode_list` | 20 | id, code, gift_id, start_time, end_time, is_open, group_id | Sin acceso estático detectado |
| `girlsh5_item_type_config` | 4 | id, type_column, exchange_column | Sin acceso estático detectado |
| `girlsh5_item_type_desc` | 30 | id, desc, is_monitor | Sin acceso estático detectado |
| `girsh5_item_type_config` | 4 | id, type_column, exchange_column | Sin acceso estático detectado |
| `girsh5_item_type_desc` | 40 | id, desc, is_monitor | Sin acceso estático detectado |
| `gm_avatar` | 5 | id, name, item_id | Sin acceso estático detectado |
| `govern_team_weather_deploy` | 4 | id, lv_low, lv_high, weather1, weather2 | Sin acceso estático detectado |
| `guide_1` | 168 | id, name, step, mark, condition, forced, window_name, obj_type, obj_id, no_click … | Sin acceso estático detectado |
| `guide_1_new` | 178 | id, name, step, mark, condition, forced, window_name, obj_type, obj_id, no_click … | Sin acceso estático detectado |
| `guide_2` | 108 | id, name, step, mark, condition, forced, window_name, obj_type, obj_id, no_click … | Sin acceso estático detectado |
| `guide_3` | 108 | id, name, step, mark, condition, forced, window_name, obj_type, obj_id, no_click … | Sin acceso estático detectado |
| `guild_competition_personal_num` | 10 | id, num, ratio | Sin acceso estático detectado |
| `guild_final_boss_award` | 7 | id, damage, awards | Sin acceso estático detectado |
| `guild_guide` | 6 | id, mark, obj_id, no_click, record, mask_type, mask_icon, icon_offset, obj_scale, hand_type … | Sin acceso estático detectado |
| `guild_new_war_initial_points` | 6 | id, desc, strength, guild_initial_points | Sin acceso estático detectado |
| `guild_new_war_match` | 12 | id, desc, guild_total_points | Sin acceso estático detectado |
| `guild_war_final_award` | 5 | id, rank, season_awards, rank_front, awards_1, awards_2, awards_3, avatar_frame | Sin acceso estático detectado |
| `house_slot` | 3 | id, name, default, type, new_furniture | Sin acceso estático detectado |
| `item1` | 1429 | id, name, brief, desc, name1, type, type_config, qlt, group, is_economy … | Sin acceso estático detectado |
| `item2` | 1429 | id, name, brief, desc, name1, type, type_config, qlt, group, is_economy … | Sin acceso estático detectado |
| `item3` | 1428 | id, name, brief, desc, name1, type, type_config, qlt, group, is_economy … | Sin acceso estático detectado |
| `item4` | 1429 | id, name, brief, desc, name1, type, type_config, qlt, group, is_economy … | Sin acceso estático detectado |
| `item5` | 518 | id, name, brief, desc, name1, type, type_config, qlt, group, is_economy … | Sin acceso estático detectado |
| `job_suit_skill` | 45 | id, name, all_level | Sin acceso estático detectado |
| `json_fight` | 1 | id, name, desc, not_run, conditions | Sin acceso estático detectado |
| `language_font` | 7 | language, font | Sin acceso estático detectado |
| `main_plot2` | 1091 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, image_xy … | Sin acceso estático detectado |
| `main_plot3` | 1091 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, image_xy … | Sin acceso estático detectado |
| `main_plot4` | 96 | id, next_id, select_next_ids, select, plot, name, image_path, is_memory, res_path, image_xy … | Sin acceso estático detectado |
| `message_push` | 23 | id, title_1, contents_1, title_2, contents_2, title_4, contents_4, title_5, contents_5, title_6 … | Sin acceso estático detectado |
| `mission_type` | 183 | id, desc, actvity_id, function_id, special_type, mission_id | Sin acceso estático detectado |
| `monster1` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster10` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster11` | 1764 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster12` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster13` | 806 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster2` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster3` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster4` | 1764 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster5` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster6` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster7` | 1764 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster8` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `monster9` | 1765 | id, partner_link, skin, name, lv, grade, hp, atk, hpP, atkP … | Sin acceso estático detectado |
| `national_flag` | 120 | id, flag_icon, short_name, language, location_code, order | Sin acceso estático detectado |
| `partner_challenge_chess_box` | 108 | id, name, lvlup_id, grade, is_freebuy, box_id | Sin acceso estático detectado |
| `partner_challenge_chess_buff` | 6 | id, name, type, skill, point, group, icon | Sin acceso estático detectado |
| `partner_challenge_chess_weight` | 9 | id, grade1, grade2, grade3 | Sin acceso estático detectado |
| `partner_challenge_mission` | 10 | id, challenge_stage_id, type, desc, complete_value, awards, mail_id | Sin acceso estático detectado |
| `partner_challenge_speed_award` | 9 | id, rank, awards, rank_front | Sin acceso estático detectado |
| `partner_data_battle_type` | 7 | id, desc, battle_id | Sin acceso estático detectado |
| `partner_data_report_filter` | 3 | id, name, type, num, is_update | Sin acceso estático detectado |
| `partner_plot2` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_plot3` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_plot4` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_plot5` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_plot6` | 865 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_return_rule` | 6 | id, group_1, group_2, group_3, group_4, group_5, group_6 | Sin acceso estático detectado |
| `partner_warmup_plot1` | 1112 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_warmup_plot2` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_warmup_plot3` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_warmup_plot4` | 1111 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `partner_warmup_plot5` | 725 | id, next_id, select_next_ids, select, plot, name, image_path, type, res_path, map_swap … | Sin acceso estático detectado |
| `senpai_dress_achievement` | 18 | id, desc, next_achieve_id, complete_value, cost, awards | Sin acceso estático detectado |
| `senpai_dress_achievement_type` | 10 | id, start_achievement, end_achievement, desc, type, show_rank, show_rank_done | Sin acceso estático detectado |
| `senpai_dress_effect` | 10 | id, num, base1_effect, base2_effect, base3_effect | Sin acceso estático detectado |
| `shop_activity_date` | 12 | id, item, desc, cost, buy_time | Sin acceso estático detectado |
| `shop_arena` | 31 | id, item, cost, desc, shop_new | Sin acceso estático detectado |
| `shop_black` | 60 | id, dropbox_id, lv_min, lv_max, limit_num, weight, desc | Sin acceso estático detectado |
| `shop_brave` | 32 | id, item, cost, desc | Sin acceso estático detectado |
| `shop_guild` | 22 | id, item, cost | Sin acceso estático detectado |
| `shop_new_trial` | 32 | id, item, cost, desc | Sin acceso estático detectado |
| `shrine_hurdle_restore` | 3 | id, desc, num, volume | Sin acceso estático detectado |
| `skill1` | 1251 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill2` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill3` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill4` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill5` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill6` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill7` | 1250 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill8` | 707 | id, partner, name, desc, is_exskill, sub_skill, trigger, is_pass, is_unseal, is_cost_energy … | Sin acceso estático detectado |
| `skill_resonate` | 8 | id, ex_id, desc_num1, desc_num2, desc_num3, desc_num4, desc_num5, desc_num6, desc_num7, desc_num8 … | Sin acceso estático detectado |
| `skin_unlcok` | 5 | id, description, type | Sin acceso estático detectado |
| `stage_fx_xy` | 18 | id, stage_fx_xy | Sin acceso estático detectado |
| `star_background` | 18 | id, layer, layer_name, ex, ey, has_effect | Sin acceso estático detectado |
| `summon_rate` | 45 | id, partner_id, name, group, job, qlt, lev, type, weight | Sin acceso estático detectado |
| `time_cloister_dress_effect` | 10 | id, num, base1_effect, base2_effect, base3_effect | Sin acceso estático detectado |
| `time_cloister_sp_battle` | 23 | id, point, crit, smash, block | Sin acceso estático detectado |
| `time_cloister_tec_type` | 12 | id, desc, num_type | Sin acceso estático detectado |
| `trial_match` | 15 | id, power, step | Sin acceso estático detectado |
| `trial_offset` | 54 | id, type, stage_belong, offsetX, offsetY | Sin acceso estático detectado |
| `weak_guide` | 4 | id, next, window_name, condition_name, obj, obj_type, obj_uncertain, offset, offset_xiaogan | Sin acceso estático detectado |
| `wedding_dress` | 8 | id, name, partner_id | Sin acceso estático detectado |

## Relevo y límites

Priorizar tablas con consumidores y sin referencias locales; revisar mensajes del consumidor en el manifest, costes/premios/desbloqueos y sus ventanas antes de implementar. Los nombres internos se conservan porque no todos tienen una etiqueta visible inequívoca. El calendario, rivales, rankings y sorteos que generaba el servidor siguen requiriendo contratos locales explícitos y pruebas.
Los textos de otras lenguas permanecen en sus bases originales; esta tanda exporta inglés, idioma de la interfaz actual.

## Validación de esta tanda

5 pruebas del lector aprobadas: escapes/tipos, nombres Unicode, esquemas con posiciones sin nombre, filas cortas, rechazo de expresiones, prioridad/orden de segmentos y desajustes de IDs/anchura. Los 904 hashes de fuentes y JSON se comprobaron. Se compararon íntegramente 6 tablas de costes/sorteos/tienda con el extractor independiente existente, con igualdad exacta. 73.656 filas de textos ingleses recuperadas.

Suite completa: 336/336 pruebas aprobadas en 48 segundos. Dos conexiones HTTP de pruebas cerraron el socket durante la respuesta y produjeron avisos BrokenPipe; la suite terminó OK. Las 252 tablas inglesas se compararon celda por celda contra SQLite con igualdad exacta. No se realizó QA visual porque esta tanda no cambia la interfaz.
