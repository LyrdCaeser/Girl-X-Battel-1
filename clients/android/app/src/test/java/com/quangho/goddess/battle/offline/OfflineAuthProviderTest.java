package com.quangho.goddess.battle.offline;

import org.json.JSONObject;
import org.junit.Test;

import java.io.File;
import java.nio.file.Files;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class OfflineAuthProviderTest {
    @Test public void guestSessionSurvivesReloadAndLogoutIsDurable() throws Exception {
        File root = Files.createTempDirectory("gxb3-offline-auth-").toFile();
        try {
            OfflineAuthProvider auth = new OfflineAuthProvider(root);
            JSONObject started = auth.startGuest();
            assertTrue(started.getBoolean("authenticated"));
            assertTrue(started.getBoolean("guest"));
            assertEquals("LOCAL", started.getJSONObject("session").getString("server_id"));

            OfflineAuthProvider reopened = new OfflineAuthProvider(root);
            assertTrue(reopened.me().getBoolean("authenticated"));
            assertTrue(reopened.me().getBoolean("guest"));

            assertTrue(reopened.logout().getBoolean("logged_out"));
            OfflineAuthProvider afterLogout = new OfflineAuthProvider(root);
            assertFalse(afterLogout.me().getBoolean("authenticated"));
            assertFalse(afterLogout.me().getBoolean("guest"));
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
