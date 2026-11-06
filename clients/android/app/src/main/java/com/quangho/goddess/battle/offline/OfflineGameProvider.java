package com.quangho.goddess.battle.offline;

import android.content.Context;

import com.quangho.goddess.battle.BattleRuntimeBridge;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Small, deterministic offline gameplay provider. The JSON file is the authoritative
 * local save; every mutation is written through a temporary file and renamed atomically.
 */
public final class OfflineGameProvider {
    private static final int SAVE_VERSION = 1;
    private final Context context;
    private final File saveFile;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private JSONObject save;

    public OfflineGameProvider(Context context) throws IOException {
        this.context = context.getApplicationContext();
        this.saveFile = new File(this.context.getFilesDir(), "offline/profile.json");
        load();
    }

    /** File-backed constructor for JVM contract tests; production uses the Context constructor. */
    OfflineGameProvider(File filesDirectory) throws IOException {
        this.context = null;
        this.saveFile = new File(filesDirectory, "offline/profile.json");
        load();
    }

    public OfflineLocalApi.Response state() {
        lock.readLock().lock();
        try { return ok(copy(save)); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response partners() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("partners", save.optJSONArray("roster"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response formation() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("partners", save.optJSONArray("formation"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response inventory() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("items", save.optJSONObject("items"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response profile(String body) {
        lock.writeLock().lock();
        try {
            JSONObject request = object(body);
            JSONObject profile = save.optJSONObject("profile");
            if (profile == null) { profile = new JSONObject(); put(save, "profile", profile); }
            for (String key : new String[] {"name", "avatar", "signature"}) {
                if (request.has(key)) put(profile, key, request.optString(key, ""));
            }
            persist();
            return ok(new JSONObject().put("state", copy(save)));
        } catch (IOException | JSONException error) {
            return error(500, "offline_save_failed");
        } finally { lock.writeLock().unlock(); }
    }

    public OfflineLocalApi.Response action(String body) {
        lock.writeLock().lock();
        try {
            JSONObject request = object(body);
            String message = request.optString("message", "");
            JSONObject data = request.optJSONObject("data");
            if ("SET_HANG_TEAM".equals(message)) {
                if (data == null || !data.has("partners")) return error(400, "invalid_team");
                put(save, "formation", data.optJSONArray("partners"));
                persist();
                return ok(new JSONObject().put("state", copy(save)));
            }
            if ("MAP_FIGHT".equals(message)) return fight(data);
            return error(501, "offline_action_not_implemented");
        } catch (IOException | JSONException error) {
            return error(500, "offline_save_failed");
        } finally { lock.writeLock().unlock(); }
    }

    public OfflineLocalApi.Response battle(long id) {
        lock.readLock().lock();
        try {
            JSONObject reports = save.optJSONObject("battle_reports");
            JSONObject report = reports == null ? null : reports.optJSONObject(Long.toString(id));
            return report == null ? error(404, "battle_not_found") : ok(report);
        } finally { lock.readLock().unlock(); }
    }

    private OfflineLocalApi.Response fight(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_battle_request");
        int stage = data.optInt("stage_id", 1);
        if (stage < 1 || stage > 30) return error(400, "invalid_stage");
        JSONArray team = data.optJSONArray("partners");
        if (team == null) team = save.optJSONArray("formation");
        if (team == null || team.length() == 0) return error(400, "empty_team");
        String input = battleInput(team, stage);
        JSONObject report;
        try {
            report = new JSONObject(BattleRuntimeBridge.runBattle(context, "battle", input));
        } catch (RuntimeException error) {
            return error(503, "offline_battle_engine_unavailable");
        }
        long id = save.optLong("next_battle_id", 1L);
        put(save, "next_battle_id", id + 1L);
        JSONObject summary = new JSONObject();
        put(summary, "id", id); put(summary, "stage", stage);
        boolean win = report.optBoolean("isWin", false);
        put(summary, "win", win);
        put(summary, "rewards", win ? rewards(stage) : new JSONObject());
        JSONObject reports = save.optJSONObject("battle_reports");
        if (reports == null) { reports = new JSONObject(); put(save, "battle_reports", reports); }
        put(reports, Long.toString(id), report);
        put(save, "last_battle", summary);
        JSONArray cleared = save.optJSONArray("cleared");
        if (cleared == null) { cleared = new JSONArray(); put(save, "cleared", cleared); }
        if (win && !contains(cleared, stage)) cleared.put(stage);
        put(save, "next_stage", Math.min(30, Math.max(save.optInt("next_stage", 1), stage + (win ? 1 : 0))));
        if (win) {
            JSONArray stages = save.optJSONArray("stages");
            if (stages != null) {
                for (int i = 0; i < stages.length(); i++) {
                    JSONObject current = stages.optJSONObject(i);
                    if (current != null && current.optInt("id", -1) <= stage + 1) put(current, "unlocked", true);
                    if (current != null && current.optInt("id", -1) == stage) put(current, "cleared", true);
                }
            }
        }
        persist();
        return ok(new JSONObject().put("state", copy(save)));
    }

    private static JSONObject rewards(int stage) throws JSONException {
        return new JSONObject().put("1", 1000 + stage * 100).put("3", 50 + stage * 5).put("9", 100 + stage * 10);
    }

    private static String battleInput(JSONArray team, int stage) throws JSONException {
        StringBuilder out = new StringBuilder("{teamA=");
        out.append("{");
        int count = Math.min(6, team.length());
        for (int i = 0; i < count; i++) {
            if (i > 0) out.append(",");
            JSONObject p = team.optJSONObject(i);
            if (p == null) p = new JSONObject();
            out.append("{table_id=").append(Math.max(1, p.optInt("table_id", 41001)))
                    .append(",partner_id=").append(Math.max(1, p.optInt("partner_id", i + 1)))
                    .append(",lv=").append(Math.max(1, p.optInt("lv", 1)))
                    .append(",pos=").append(i + 1).append("}");
        }
        out.append("},teamB={{table_id=1,isMonster=true,pos=7}},battle_id=").append(100000 + stage)
                .append(",random_seed=").append(1000 + stage).append("}");
        return out.toString();
    }

    private void load() throws IOException {
        lock.writeLock().lock();
        try {
            if (!saveFile.isFile()) { save = initial(); persist(); return; }
            byte[] bytes;
            try (FileInputStream in = new FileInputStream(saveFile)) { bytes = readAll(in); }
            save = migrate(new JSONObject(new String(bytes, StandardCharsets.UTF_8)));
            persist();
        } catch (JSONException error) { throw new IOException("Corrupt offline save", error); }
        finally { lock.writeLock().unlock(); }
    }

    private static JSONObject initial() throws JSONException {
        JSONObject s = new JSONObject();
        put(s, "save_version", SAVE_VERSION); put(s, "revision", 0L); put(s, "level", 1);
        put(s, "next_stage", 1); put(s, "cleared", new JSONArray()); put(s, "items", new JSONObject().put("1", 10000).put("3", 1000).put("9", 1000));
        put(s, "profile", new JSONObject().put("name", "Offline Player").put("avatar", "41001"));
        put(s, "formation", new JSONArray().put(new JSONObject().put("table_id", 41001).put("partner_id", 1).put("lv", 1).put("pos", 1)));
        put(s, "roster", new JSONArray().put(new JSONObject()
                .put("partner_id", 1).put("table_id", 41001).put("name", "Gwen")
                .put("lv", 1).put("stars", 5).put("level_cap", 100)
                .put("next_cost", new JSONObject().put("1", 100).put("9", 10))
                .put("atk", 100).put("arm", 80).put("hp", 1000).put("power", 347)));
        JSONArray stages = new JSONArray();
        for (int i = 1; i <= 30; i++) stages.put(new JSONObject().put("id", i).put("chapter", 1).put("level_required", 1).put("unlocked", i == 1));
        put(s, "stages", stages); put(s, "battle_reports", new JSONObject()); put(s, "next_battle_id", 1L);
        return s;
    }

    /**
     * Upgrades the pre-MVP save shape without discarding campaign progress. Version zero
     * files were written before the durable save contract was pinned and may only contain
     * profile/formation/cleared fields. Missing MVP fields receive the same deterministic
     * defaults as a new guest profile.
     */
    static JSONObject migrate(JSONObject legacy) throws JSONException, IOException {
        int version = legacy.optInt("save_version", 0);
        if (version > SAVE_VERSION) throw new IOException("Unsupported offline save version");
        if (version == SAVE_VERSION) return legacy;
        JSONObject defaults = initial();
        copyIfMissing(legacy, defaults, "revision");
        copyIfMissing(legacy, defaults, "level");
        copyIfMissing(legacy, defaults, "next_stage");
        copyIfMissing(legacy, defaults, "cleared");
        copyIfMissing(legacy, defaults, "items");
        copyIfMissing(legacy, defaults, "profile");
        copyIfMissing(legacy, defaults, "formation");
        copyIfMissing(legacy, defaults, "roster");
        copyIfMissing(legacy, defaults, "stages");
        copyIfMissing(legacy, defaults, "battle_reports");
        copyIfMissing(legacy, defaults, "next_battle_id");
        legacy.put("save_version", SAVE_VERSION);
        return legacy;
    }

    private static void copyIfMissing(JSONObject target, JSONObject defaults, String key) throws JSONException {
        if (!target.has(key)) target.put(key, defaults.get(key));
    }

    private void persist() throws IOException {
        put(save, "revision", save.optLong("revision", 0L) + 1L);
        File parent = saveFile.getParentFile(); if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("Cannot create save directory");
        File tmp = new File(saveFile.getPath() + ".tmp");
        try (FileOutputStream out = new FileOutputStream(tmp)) { out.write(save.toString().getBytes(StandardCharsets.UTF_8)); out.getFD().sync(); }
        if (!tmp.renameTo(saveFile)) {
            try { java.nio.file.Files.move(tmp.toPath(), saveFile.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING); }
            catch (java.io.IOException error) { if (!tmp.delete()) { /* best effort cleanup */ } throw new IOException("Cannot atomically replace offline save", error); }
        }
    }

    private static byte[] readAll(FileInputStream in) throws IOException { byte[] b = new byte[8192]; java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream(); int n; while ((n = in.read(b)) >= 0) out.write(b, 0, n); return out.toByteArray(); }
    private static JSONObject copy(JSONObject source) { try { return new JSONObject(source.toString()); } catch (JSONException e) { throw new IllegalStateException(e); } }
    private static JSONObject object(String raw) throws JSONException { return raw == null ? new JSONObject() : new JSONObject(raw); }
    private static boolean contains(JSONArray a, int value) { for (int i = 0; i < a.length(); i++) if (a.optInt(i, -1) == value) return true; return false; }
    private static OfflineLocalApi.Response ok(JSONObject body) { return new OfflineLocalApi.Response(200, body); }
    private static OfflineLocalApi.Response error(int status, String code) {
        JSONObject body = new JSONObject();
        put(body, "error", code); put(body, "offline", true);
        return new OfflineLocalApi.Response(status, body);
    }
    private static void put(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (JSONException e) { throw new IllegalStateException(e); } }
}
