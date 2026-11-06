package com.quangho.goddess.battle.offline;

import org.json.JSONObject;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class OfflineLocalApiTest {
    private final OfflineLocalApi api = new OfflineLocalApi();

    @Test public void healthIsExplicitlyOfflineAndNotGameplayReady() throws Exception {
        OfflineLocalApi.Response response = api.handleRequest("GET", "/api/offline/health", null);
        assertEquals(200, response.status);
        assertTrue(response.body.getBoolean("offline"));
        assertEquals(1, response.body.getInt("api_version"));
        assertFalse(response.body.getBoolean("gameplay_ready"));
        assertFalse(response.body.getJSONObject("pending").getBoolean("local_save"));
    }

    @Test public void trustedMessageEnvelopeReturnsMatchingResponseId() throws Exception {
        JSONObject request = new JSONObject()
                .put("v", 1)
                .put("id", "rpc_1")
                .put("method", "GET")
                .put("path", "/api/offline/health");
        JSONObject response = new JSONObject(api.handleMessage(request.toString(), true));
        assertEquals("rpc_1", response.getString("id"));
        assertEquals(200, response.getInt("status"));
        assertTrue(response.getJSONObject("body").getBoolean("offline"));
    }

    @Test public void gameplayRoutesFailClosedUntilProviderAndSaveExist() throws Exception {
        OfflineLocalApi.Response response = api.handleRequest("GET", "/api/state", null);
        assertEquals(501, response.status);
        assertEquals("offline_api_not_implemented", response.body.getString("error"));
        assertTrue(response.body.getBoolean("offline"));
    }

    @Test public void rejectsUnsupportedMethodsAndUnsafePaths() throws Exception {
        assertEquals(405, api.handleRequest("PUT", "/api/state", null).status);
        assertEquals(400, api.handleRequest("GET", "/api/../state", null).status);
        assertEquals(400, api.handleRequest("GET", "/api/state?remote=1", null).status);
        assertEquals(404, api.handleRequest("GET", "/assets/catalog.json", null).status);
    }

    @Test public void rejectsUntrustedOriginAndInvalidProtocolEnvelope() throws Exception {
        JSONObject request = new JSONObject()
                .put("v", 1)
                .put("id", "req_1")
                .put("method", "GET")
                .put("path", "/api/offline/health");
        JSONObject denied = new JSONObject(api.handleMessage(request.toString(), false));
        assertEquals("req_1", denied.getString("id"));
        assertEquals(403, denied.getInt("status"));
        assertEquals("local_api_origin_rejected", denied.getJSONObject("body").getString("error"));

        request.put("v", 99);
        JSONObject unsupported = new JSONObject(api.handleMessage(request.toString(), true));
        assertEquals(400, unsupported.getInt("status"));
        assertEquals("unsupported_local_api_protocol", unsupported.getJSONObject("body").getString("error"));
    }

    @Test public void rejectsExcessiveJsonNesting() throws Exception {
        StringBuilder deep = new StringBuilder();
        for (int i = 0; i < 33; i++) deep.append('[');
        deep.append('0');
        for (int i = 0; i < 33; i++) deep.append(']');
        OfflineLocalApi.Response response = api.handleRequest("POST", "/api/action", deep.toString());
        assertEquals(400, response.status);
        assertEquals("local_api_json_too_deep", response.body.getString("error"));
    }

    @Test public void rejectsOversizedAndMalformedRequests() throws Exception {
        char[] oversizedChars = new char[OfflineLocalApi.MAX_MESSAGE_BYTES + 1];
        java.util.Arrays.fill(oversizedChars, 'x');
        String oversized = new String(oversizedChars);
        JSONObject tooLarge = new JSONObject(api.handleMessage(oversized, true));
        assertEquals(413, tooLarge.getInt("status"));

        JSONObject malformed = new JSONObject(api.handleMessage("{", true));
        assertEquals(400, malformed.getInt("status"));
        assertEquals("invalid_local_api_message", malformed.getJSONObject("body").getString("error"));
    }
}
