package com.quangho.goddess.battle.offline;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

/** Contract tests for the intentionally narrow campaign_mvp offline slice. */
public final class OfflineGameProviderTest {
    @Test public void newGuestHasCampaignMvpAndFormation() throws Exception {
        File root = Files.createTempDirectory("gxb3-offline-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            JSONObject state = provider.state().body;
            assertEquals(3, state.getInt("save_version"));
            assertEquals(1, state.getInt("next_stage"));
            assertEquals(30, state.getJSONArray("stages").length());
            assertTrue(state.getJSONArray("stages").getJSONObject(0).getBoolean("unlocked"));
            assertFalse(state.getJSONArray("stages").getJSONObject(1).getBoolean("unlocked"));
            assertEquals(1, state.getJSONArray("formation").length());
        } finally {
            delete(root);
        }
    }

    @Test public void formationAndProfileMutationsArePersisted() throws Exception {
        File root = Files.createTempDirectory("gxb3-offline-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            JSONArray partners = new JSONArray()
                    .put(new JSONObject().put("partner_id", 1).put("table_id", 41001).put("lv", 7).put("pos", 1))
                    .put(new JSONObject().put("partner_id", 2).put("table_id", 52017).put("lv", 3).put("pos", 2));
            OfflineLocalApi.Response formation = provider.action(new JSONObject()
                    .put("message", "SET_HANG_TEAM")
                    .put("data", new JSONObject().put("partners", partners)).toString());
            assertEquals(200, formation.status);
            assertEquals(1, formation.body.getJSONObject("state").getJSONArray("formation").length());
            assertEquals(200, provider.profile(new JSONObject().put("name", "Tester").toString()).status);

            OfflineGameProvider reopened = new OfflineGameProvider(root);
            assertEquals("Tester", reopened.state().body.getJSONObject("profile").getString("name"));
            assertEquals(1, reopened.state().body.getJSONArray("formation").length());
        } finally {
            delete(root);
        }
    }

    @Test public void singlePlayerCatalogRoutesExposeOnlyLocalState() throws Exception {
        File root = Files.createTempDirectory("gxb3-offline-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            assertEquals(200, provider.partners().status);
            assertEquals(1, provider.partners().body.getJSONArray("partners").length());
            assertEquals(200, provider.formation().status);
            assertEquals(1, provider.formation().body.getJSONArray("partners").length());
            assertEquals(10000, provider.inventory().body.getJSONObject("items").getInt("1"));
        } finally {
            delete(root);
        }
    }

    @Test public void legacySaveMigratesWithoutDroppingCampaignOrFormation() throws Exception {
        File root = Files.createTempDirectory("gxb3-offline-").toFile();
        try {
            File save = new File(new File(root, "offline"), "profile.json");
            assertTrue(save.getParentFile().mkdirs());
            JSONObject legacy = new JSONObject()
                    .put("profile", new JSONObject().put("name", "Legacy Player"))
                    .put("formation", new JSONArray().put(new JSONObject().put("partner_id", 9).put("table_id", 53016)));
            Files.write(save.toPath(), legacy.toString().getBytes(StandardCharsets.UTF_8));

            OfflineGameProvider migrated = new OfflineGameProvider(root);
            JSONObject state = migrated.state().body;
            assertEquals(3, state.getInt("save_version"));
            assertEquals("Legacy Player", state.getJSONObject("profile").getString("name"));
            assertEquals(9, state.getJSONArray("formation").getJSONObject(0).getInt("partner_id"));
            assertEquals(30, state.getJSONArray("stages").length());
            assertEquals(3, new JSONObject(new String(Files.readAllBytes(save.toPath()), StandardCharsets.UTF_8))
                    .getInt("save_version"));
        } finally {
            delete(root);
        }
    }

    @Test public void levelUpConsumesResourcesUpdatesStatsAndSurvivesReload() throws Exception {
        File root = Files.createTempDirectory("gxb3-level-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            JSONObject before = provider.state().body.getJSONArray("roster").getJSONObject(0);
            int gold = provider.state().body.getJSONObject("items").getInt("1");
            OfflineLocalApi.Response result = provider.action(new JSONObject().put("message", "PARTNER_LEVUP")
                    .put("data", new JSONObject().put("partner_id", 1).put("incr_lv", 1)).toString());
            assertEquals(200, result.status);
            JSONObject after = result.body.getJSONObject("state").getJSONArray("roster").getJSONObject(0);
            assertEquals(2, after.getInt("lv"));
            assertTrue(after.getInt("power") > before.getInt("power"));
            assertEquals(gold - 200, result.body.getJSONObject("state").getJSONObject("items").getInt("1"));
            assertEquals(2, new OfflineGameProvider(root).state().body.getJSONArray("roster").getJSONObject(0).getInt("lv"));
        } finally { delete(root); }
    }

    @Test public void starUpRequiresDistinctOwnedMaterialsAndPersists() throws Exception {
        File root = Files.createTempDirectory("gxb3-star-").toFile();
        try {
            File save = new File(new File(root, "offline"), "profile.json");
            assertTrue(save.getParentFile().mkdirs());
            JSONArray roster = new JSONArray()
                    .put(new JSONObject().put("partner_id", 1).put("table_id", 41001).put("name", "Base").put("lv", 1).put("stars", 5).put("level_cap", 20))
                    .put(new JSONObject().put("partner_id", 2).put("table_id", 41001).put("name", "Material").put("lv", 1).put("stars", 5));
            Files.write(save.toPath(), new JSONObject().put("roster", roster).put("items", new JSONObject().put("1", 1000)).toString().getBytes(StandardCharsets.UTF_8));
            OfflineGameProvider provider = new OfflineGameProvider(root);
            OfflineLocalApi.Response result = provider.action(new JSONObject().put("message", "AWAKE_PARTNER")
                    .put("data", new JSONObject().put("partner_id", 1).put("material_ids", new JSONArray().put(2))).toString());
            assertEquals(200, result.status);
            assertEquals(6, result.body.getJSONObject("state").getJSONArray("roster").getJSONObject(0).getInt("stars"));
            assertEquals(1, result.body.getJSONObject("state").getJSONArray("roster").length());
            assertEquals(6, new OfflineGameProvider(root).state().body.getJSONArray("roster").getJSONObject(0).getInt("stars"));
        } finally { delete(root); }
    }

    @Test public void summonConsumesCostAddsRosterAndSurvivesReload() throws Exception {
        File root = Files.createTempDirectory("gxb3-summon-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            int before = provider.state().body.getJSONObject("items").getInt("33");
            OfflineLocalApi.Response result = provider.action(new JSONObject().put("message", "SUMMON")
                    .put("data", new JSONObject().put("summon_id", 1).put("times", 1)).toString());
            assertEquals(200, result.status);
            assertEquals(before - 1, result.body.getJSONObject("state").getJSONObject("items").getInt("33"));
            assertEquals(2, result.body.getJSONObject("state").getJSONArray("roster").length());
            assertEquals(1, new OfflineGameProvider(root).state().body.getJSONObject("summon").getJSONArray("history").length());
        } finally { delete(root); }
    }

    @Test public void shopAndHomeMutationsPersistLocally() throws Exception {
        File root = Files.createTempDirectory("gxb3-shop-home-").toFile();
        try {
            OfflineGameProvider provider = new OfflineGameProvider(root);
            assertEquals(200, provider.action(new JSONObject().put("message", "SHOP_BUY")
                    .put("data", new JSONObject().put("shop", 7).put("index", 1).put("num", 1)).toString()).status);
            assertEquals(1010, provider.state().body.getJSONObject("items").getInt("3"));
            assertEquals(200, provider.action(new JSONObject().put("message", "HOME_ACTION")
                    .put("data", new JSONObject().put("action", "travel_start")).toString()).status);
            assertEquals(200, provider.action(new JSONObject().put("message", "HOME_ACTION")
                    .put("data", new JSONObject().put("action", "travel_collect")).toString()).status);
            assertTrue(new OfflineGameProvider(root).state().body.getJSONObject("home_systems").getBoolean("started_travel"));
        } finally { delete(root); }
    }

    @Test public void campaignSettlementUsesEngineResultAndPersistsFirstClear() throws Exception {
        File root = Files.createTempDirectory("gxb3-campaign-").toFile();
        try {
            AtomicBoolean engineWin = new AtomicBoolean(false);
            OfflineGameProvider provider = new OfflineGameProvider(root, input -> {
                assertTrue(input.contains("{teamA="));
                assertTrue(input.contains("teamB="));
                return new JSONObject().put("isWin", engineWin.get()).put("engine", "test");
            });
            int initialGold = provider.state().body.getJSONObject("items").getInt("1");
            JSONObject request = new JSONObject().put("message", "MAP_FIGHT")
                    .put("data", new JSONObject().put("stage_id", 1).put("isWin", true));

            OfflineLocalApi.Response defeat = provider.action(request.toString());
            assertEquals(200, defeat.status);
            JSONObject afterDefeat = defeat.body.getJSONObject("state");
            assertFalse(afterDefeat.getJSONObject("last_battle").getBoolean("win"));
            assertEquals(0, afterDefeat.getJSONArray("cleared").length());
            assertEquals(1, afterDefeat.getInt("next_stage"));
            assertEquals(initialGold, afterDefeat.getJSONObject("items").getInt("1"));

            engineWin.set(true);
            OfflineLocalApi.Response victory = provider.action(request.toString());
            assertEquals(200, victory.status);
            JSONObject afterVictory = victory.body.getJSONObject("state");
            assertTrue(afterVictory.getJSONObject("last_battle").getBoolean("win"));
            assertEquals(2, afterVictory.getInt("next_stage"));
            assertEquals(1, afterVictory.getJSONArray("cleared").length());
            assertEquals(initialGold + 1100, afterVictory.getJSONObject("items").getInt("1"));
            long battleId = afterVictory.getJSONObject("last_battle").getLong("id");
            assertEquals("test", provider.battle(battleId).body.getString("engine"));

            OfflineGameProvider reopened = new OfflineGameProvider(root);
            JSONObject saved = reopened.state().body;
            assertEquals(2, saved.getInt("next_stage"));
            assertEquals(1, saved.getJSONArray("cleared").length());
            assertEquals(initialGold + 1100, saved.getJSONObject("items").getInt("1"));
        } finally { delete(root); }
    }

    private static void delete(File file) {
        if (file.isDirectory()) {
            File[] children = file.listFiles();
            if (children != null) for (File child : children) delete(child);
        }
        if (file.exists()) file.delete();
    }
}
