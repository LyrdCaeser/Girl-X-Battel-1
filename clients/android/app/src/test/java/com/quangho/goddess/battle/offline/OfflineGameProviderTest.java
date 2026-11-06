package com.quangho.goddess.battle.offline;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

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
            assertEquals(1, state.getInt("save_version"));
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
            assertEquals(2, formation.body.getJSONObject("state").getJSONArray("formation").length());
            assertEquals(200, provider.profile(new JSONObject().put("name", "Tester").toString()).status);

            OfflineGameProvider reopened = new OfflineGameProvider(root);
            assertEquals("Tester", reopened.state().body.getJSONObject("profile").getString("name"));
            assertEquals(2, reopened.state().body.getJSONArray("formation").length());
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
            assertEquals(1, state.getInt("save_version"));
            assertEquals("Legacy Player", state.getJSONObject("profile").getString("name"));
            assertEquals(9, state.getJSONArray("formation").getJSONObject(0).getInt("partner_id"));
            assertEquals(30, state.getJSONArray("stages").length());
            assertEquals(1, new JSONObject(new String(Files.readAllBytes(save.toPath()), StandardCharsets.UTF_8))
                    .getInt("save_version"));
        } finally {
            delete(root);
        }
    }

    private static void delete(File file) {
        if (file.isDirectory()) {
            File[] children = file.listFiles();
            if (children != null) for (File child : children) delete(child);
        }
        if (file.exists()) file.delete();
    }
}
