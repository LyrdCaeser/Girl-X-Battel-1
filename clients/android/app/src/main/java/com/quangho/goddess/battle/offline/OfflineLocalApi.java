package com.quangho.goddess.battle.offline;

import org.json.JSONException;
import org.json.JSONObject;

import android.content.Context;

import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Pattern;

/**
 * Local-only, JSON-shaped API contract for WebView RPC. It intentionally does not
 * emulate online authentication or invent game results while the offline engine
 * and durable profile store are still being integrated.
 */
public final class OfflineLocalApi {
    public static final String JS_OBJECT_NAME = "Gxb3LocalApi";
    public static final int MAX_MESSAGE_BYTES = 64 * 1024;

    private static final String HEALTH_PATH = "/api/offline/health";
    private static final Pattern REQUEST_ID = Pattern.compile("[A-Za-z0-9_-]{1,64}");
    private static final Pattern API_PATH = Pattern.compile("/api/[A-Za-z0-9._/-]{1,256}");
    private final OfflineGameProvider gameProvider;

    public OfflineLocalApi() {
        this.gameProvider = null;
    }

    public OfflineLocalApi(Context context) throws java.io.IOException {
        this.gameProvider = new OfflineGameProvider(context);
    }

    /** A response body follows the existing server convention: JSON with `error` on failure. */
    public static final class Response {
        public final int status;
        public final JSONObject body;

        Response(int status, JSONObject body) {
            this.status = status;
            this.body = body;
        }
    }

    /**
     * Accepts one bounded message from the local WebView and returns a JSON
     * envelope: {id, status, body}. The caller must separately verify origin and
     * top-frame status before setting trustedOrigin=true.
     */
    public String handleMessage(String rawMessage, boolean trustedOrigin) {
        if (rawMessage == null) {
            return envelope(null, error(400, "invalid_local_api_message"));
        }
        if (rawMessage.length() > MAX_MESSAGE_BYTES || utf8Length(rawMessage) > MAX_MESSAGE_BYTES) {
            return envelope(null, error(413, "local_api_message_too_large"));
        }
        if (!hasSafeJsonNesting(rawMessage)) return envelope(null, error(400, "local_api_json_too_deep"));

        final JSONObject request;
        try {
            request = new JSONObject(rawMessage);
        } catch (JSONException error) {
            return envelope(null, error(400, "invalid_local_api_message"));
        }

        String id = request.optString("id", "");
        if (!REQUEST_ID.matcher(id).matches()) {
            return envelope(null, error(400, "invalid_local_api_request_id"));
        }
        if (!trustedOrigin) {
            return envelope(id, error(403, "local_api_origin_rejected"));
        }
        if (request.optInt("v", -1) != 1) {
            return envelope(id, error(400, "unsupported_local_api_protocol"));
        }

        String method = request.optString("method", "").toUpperCase(Locale.ROOT);
        String path = request.optString("path", "");
        Object bodyValue = request.opt("body");
        String bodyJson = null;
        if (bodyValue != null && bodyValue != JSONObject.NULL) {
            if (!(bodyValue instanceof JSONObject)) {
                return envelope(id, error(400, "local_api_body_must_be_object"));
            }
            bodyJson = ((JSONObject) bodyValue).toString();
        }
        return envelope(id, handleRequest(method, path, bodyJson));
    }

    /** Route handler shared by WebView transport and JVM unit tests. */
    public Response handleRequest(String method, String path, String bodyJson) {
        if (method == null || !("GET".equals(method) || "POST".equals(method))) {
            return error(405, "local_api_method_not_allowed");
        }
        if (path == null || !path.startsWith("/api/")) return error(404, "local_api_not_found");
        if (path.length() > 261 || !API_PATH.matcher(path).matches()
                || path.contains("..") || path.contains("//")) {
            return error(400, "invalid_local_api_path");
        }
        if (bodyJson != null) {
            if (bodyJson.length() > MAX_MESSAGE_BYTES || utf8Length(bodyJson) > MAX_MESSAGE_BYTES) {
                return error(413, "local_api_body_too_large");
            }
            if (!hasSafeJsonNesting(bodyJson)) return error(400, "local_api_json_too_deep");
            try {
                new JSONObject(bodyJson);
            } catch (JSONException error) {
                return error(400, "invalid_local_api_body");
            }
            if ("GET".equals(method)) return error(400, "get_body_not_supported");
        }

        if (HEALTH_PATH.equals(path)) {
            if (!"GET".equals(method)) return error(405, "local_api_method_not_allowed");
            JSONObject body = new JSONObject();
            put(body, "offline", true);
            put(body, "api_version", 1);
            put(body, "gameplay_ready", gameProvider != null);
            JSONObject pending = new JSONObject();
            put(pending, "state_action_provider", gameProvider == null ? false : true);
            put(pending, "local_save", gameProvider == null ? false : true);
            put(pending, "frontend_adapter", true);
            put(body, "pending", pending);
            return new Response(200, body);
        }

        if (gameProvider != null && "/api/state".equals(path) && "GET".equals(method)) {
            return gameProvider.state();
        }
        if (gameProvider != null && "/api/partners".equals(path) && "GET".equals(method)) {
            return gameProvider.partners();
        }
        if (gameProvider != null && "/api/formation".equals(path) && "GET".equals(method)) {
            return gameProvider.formation();
        }
        if (gameProvider != null && "/api/inventory".equals(path) && "GET".equals(method)) {
            return gameProvider.inventory();
        }
        if (gameProvider != null && "/api/action".equals(path) && "POST".equals(method)) {
            return gameProvider.action(bodyJson);
        }
        if (gameProvider != null && "/api/profile".equals(path) && "POST".equals(method)) {
            return gameProvider.profile(bodyJson);
        }
        if (gameProvider != null && "/api/graduate/preview".equals(path) && "POST".equals(method)) {
            return gameProvider.graduatePreview(bodyJson);
        }
        if (gameProvider != null && path.matches("/api/battle/[0-9]+") && "GET".equals(method)) {
            try { return gameProvider.battle(Long.parseLong(path.substring("/api/battle/".length()))); }
            catch (NumberFormatException ignored) { return error(400, "invalid_battle_id"); }
        }

        if (isOnlineOnlyPath(path)) return error(403, "offline_online_only");

        if (path.startsWith("/api/")) {
            // Deliberately fail rather than return plausible but non-persistent game data.
            return error(501, "offline_api_not_implemented");
        }
        return error(404, "local_api_not_found");
    }

    private static boolean isOnlineOnlyPath(String path) {
        return path.equals("/api/login") || path.startsWith("/api/auth/")
                || path.startsWith("/api/payment/") || path.startsWith("/api/pvp/")
                || path.startsWith("/api/guild/") || path.startsWith("/api/chat/")
                || path.startsWith("/api/leaderboard/") || path.startsWith("/api/cloud/");
    }

    public String errorEnvelope(String rawMessage, int status, String code) {
        String id = null;
        if (rawMessage != null && rawMessage.length() <= MAX_MESSAGE_BYTES
                && utf8Length(rawMessage) <= MAX_MESSAGE_BYTES && hasSafeJsonNesting(rawMessage)) {
            try {
                String candidate = new JSONObject(rawMessage).optString("id", "");
                if (REQUEST_ID.matcher(candidate).matches()) id = candidate;
            } catch (JSONException ignored) { }
        }
        return envelope(id, error(status, code));
    }

    private static Response error(int status, String code) {
        JSONObject body = new JSONObject();
        put(body, "error", code);
        put(body, "offline", true);
        return new Response(status, body);
    }

    private static String envelope(String id, Response response) {
        JSONObject result = new JSONObject();
        put(result, "id", id == null ? JSONObject.NULL : id);
        put(result, "status", response.status);
        put(result, "body", response.body);
        return result.toString();
    }

    private static void put(JSONObject object, String key, Object value) {
        try {
            object.put(key, value);
        } catch (JSONException impossible) {
            throw new IllegalStateException("Unable to construct local API JSON", impossible);
        }
    }

    private static int utf8Length(String value) {
        return value.getBytes(StandardCharsets.UTF_8).length;
    }

    private static boolean hasSafeJsonNesting(String value) {
        int depth = 0;
        boolean inString = false;
        boolean escaped = false;
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (inString) {
                if (escaped) escaped = false;
                else if (c == '\\') escaped = true;
                else if (c == '"') inString = false;
                continue;
            }
            if (c == '"') inString = true;
            else if (c == '{' || c == '[') {
                if (++depth > 32) return false;
            } else if (c == '}' || c == ']') {
                if (depth > 0) depth--;
            }
        }
        // Syntax, matching delimiters and unterminated strings are checked by org.json.
        return true;
    }
}
