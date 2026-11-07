package com.quangho.goddess.battle.offline;

import org.json.JSONException;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Locale;

/** Durable, device-local account/session store used only by offline mode. */
final class OfflineAuthProvider {
    private final File authFile;
    private JSONObject store;
    private final SecureRandom random = new SecureRandom();

    OfflineAuthProvider() {
        this.authFile = null;
        this.store = new JSONObject();
        put(store, "accounts", new JSONObject());
    }

    OfflineAuthProvider(File filesDirectory) throws IOException {
        this.authFile = new File(new File(filesDirectory, "offline"), "auth.json");
        load();
    }

    synchronized JSONObject me() throws JSONException {
        JSONObject result = worldInfo();
        String username = store.optString("session", "");
        JSONObject accounts = store.optJSONObject("accounts");
        JSONObject account = accounts == null ? null : accounts.optJSONObject(username);
        if (account != null) {
            put(result, "authenticated", true);
            put(result, "session", session(account, username));
        } else {
            put(result, "authenticated", false);
            put(result, "session", JSONObject.NULL);
        }
        return result;
    }

    synchronized JSONObject login(JSONObject request) throws IOException, JSONException {
        String username = normalizedUsername(request.optString("username", ""));
        String password = request.optString("password", "");
        JSONObject accounts = store.optJSONObject("accounts");
        JSONObject account = accounts == null ? null : accounts.optJSONObject(username);
        if (account == null || !constantTimeEquals(account.optString("password_hash", ""), hash(password))) {
            throw authError("invalid_credentials");
        }
        put(store, "session", username);
        persist();
        return new JSONObject().put("authenticated", true).put("session", session(account, username)).put("worlds", worlds());
    }

    synchronized JSONObject register(JSONObject request) throws IOException, JSONException {
        String username = normalizedUsername(request.optString("username", ""));
        String password = request.optString("password", "");
        if (!username.matches("[a-z0-9_]{4,24}")) throw authError("invalid_username");
        if (password.length() < 8 || password.length() > 128) throw authError("invalid_password");
        JSONObject accounts = store.optJSONObject("accounts");
        if (accounts == null) { accounts = new JSONObject(); put(store, "accounts", accounts); }
        if (accounts.has(username)) throw authError("username_taken");
        String recovery = recoveryCode();
        JSONObject account = new JSONObject();
        put(account, "username", username);
        put(account, "email", request.optString("email", "").trim());
        put(account, "character_name", request.optString("character_name", username).trim());
        put(account, "server_id", request.optString("server_id", "S1"));
        put(account, "password_hash", hash(password));
        put(account, "recovery_hash", hash(recovery));
        put(accounts, username, account);
        put(store, "session", username);
        persist();
        return new JSONObject().put("authenticated", true).put("recovery_code", recovery)
                .put("session", session(account, username)).put("worlds", worlds());
    }

    synchronized JSONObject resetPassword(JSONObject request) throws IOException, JSONException {
        String username = normalizedUsername(request.optString("username", ""));
        JSONObject accounts = store.optJSONObject("accounts");
        JSONObject account = accounts == null ? null : accounts.optJSONObject(username);
        String nextPassword = request.optString("new_password", "");
        if (account == null || !constantTimeEquals(account.optString("recovery_hash", ""), hash(request.optString("recovery_code", "")))) {
            throw authError("invalid_recovery_code");
        }
        if (nextPassword.length() < 8 || nextPassword.length() > 128) throw authError("invalid_password");
        put(account, "password_hash", hash(nextPassword));
        put(store, "session", JSONObject.NULL);
        persist();
        return new JSONObject().put("reset", true).put("worlds", worlds());
    }

    private JSONObject worldInfo() throws JSONException {
        return new JSONObject().put("worlds", worlds()).put("is_super_gm", false);
    }

    private JSONArray worlds() throws JSONException {
        return new JSONArray().put(new JSONObject().put("name", "Offline").put("server_id", "S1").put("status", "online"));
    }

    private JSONObject session(JSONObject account, String username) throws JSONException {
        return new JSONObject().put("username", username).put("character_name", account.optString("character_name", username))
                .put("server_id", account.optString("server_id", "S1"));
    }

    private String normalizedUsername(String value) { return value.trim().toLowerCase(Locale.ROOT); }

    private String recoveryCode() {
        byte[] bytes = new byte[8];
        random.nextBytes(bytes);
        String hex = hex(bytes).toUpperCase(Locale.ROOT);
        return hex.substring(0, 4) + "-" + hex.substring(4, 8) + "-" + hex.substring(8, 12) + "-" + hex.substring(12, 16);
    }

    private static String hash(String value) {
        try { return hex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8))); }
        catch (Exception impossible) { throw new IllegalStateException(impossible); }
    }

    private static boolean constantTimeEquals(String left, String right) {
        return MessageDigest.isEqual(left.getBytes(StandardCharsets.UTF_8), right.getBytes(StandardCharsets.UTF_8));
    }

    private static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) out.append(String.format(Locale.ROOT, "%02x", b & 0xff));
        return out.toString();
    }

    private void load() throws IOException {
        store = new JSONObject();
        if (authFile.exists()) {
            byte[] bytes = readAll(authFile);
            try { store = new JSONObject(new String(bytes, StandardCharsets.UTF_8)); }
            catch (JSONException invalid) { store = new JSONObject(); }
        }
        if (store.optJSONObject("accounts") == null) put(store, "accounts", new JSONObject());
    }

    private void persist() throws IOException {
        if (authFile == null) return;
        File parent = authFile.getParentFile();
        if (!parent.exists() && !parent.mkdirs()) throw new IOException("cannot_create_auth_directory");
        File temporary = new File(parent, authFile.getName() + ".tmp");
        try (FileOutputStream out = new FileOutputStream(temporary)) {
            out.write(store.toString().getBytes(StandardCharsets.UTF_8));
            out.getFD().sync();
        }
        if (!temporary.renameTo(authFile)) {
            if (!authFile.delete() || !temporary.renameTo(authFile)) throw new IOException("cannot_commit_auth_store");
        }
    }

    private static byte[] readAll(File file) throws IOException {
        try (FileInputStream in = new FileInputStream(file)) {
            byte[] bytes = new byte[(int) file.length()];
            int offset = 0, count;
            while (offset < bytes.length && (count = in.read(bytes, offset, bytes.length - offset)) > 0) offset += count;
            return bytes;
        }
    }

    private static JSONException authError(String code) { return new JSONException(code); }

    private static void put(JSONObject object, String key, Object value) {
        try { object.put(key, value); } catch (JSONException impossible) { throw new IllegalStateException(impossible); }
    }

}
