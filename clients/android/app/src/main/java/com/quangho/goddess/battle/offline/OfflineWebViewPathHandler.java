package com.quangho.goddess.battle.offline;

import android.webkit.MimeTypeMap;
import android.webkit.WebResourceResponse;
import androidx.webkit.WebViewAssetLoader;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;

/** Serves only manifest-declared, locally installed web files. Missing files never fall back to CDN. */
public final class OfflineWebViewPathHandler implements WebViewAssetLoader.PathHandler {
    private final OfflineResourceManager resourceManager;

    public OfflineWebViewPathHandler(OfflineResourceManager resourceManager) {
        if (resourceManager == null) throw new IllegalArgumentException("resourceManager is required");
        this.resourceManager = resourceManager;
    }

    @Override public WebResourceResponse handle(String path) {
        String resourcePath = manifestPath(path);
        try {
            InputStream content = resourceManager.openResource(resourcePath);
            String mimeType = mimeType(resourcePath);
            String encoding = mimeType.startsWith("text/") || mimeType.contains("javascript")
                    || mimeType.contains("json") || mimeType.contains("xml") ? "UTF-8" : null;
            return new WebResourceResponse(mimeType, encoding, content);
        } catch (IOException | IllegalArgumentException error) {
            byte[] message = "Local resource not installed".getBytes(java.nio.charset.StandardCharsets.UTF_8);
            return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found",
                    Collections.singletonMap("Cache-Control", "no-store"), new ByteArrayInputStream(message));
        }
    }

    /** Maps root Web paths to the `web/` subtree in the signed manifest. */
    static String manifestPath(String path) {
        if (path == null || path.isEmpty() || "/".equals(path)) return "web/index.html";
        String normalized = path.startsWith("/") ? path.substring(1) : path;
        if (normalized.startsWith("web/")) return normalized;
        return "web/" + normalized;
    }

    private static String mimeType(String path) {
        int dot = path.lastIndexOf('.');
        String extension = dot >= 0 && dot < path.length() - 1 ? path.substring(dot + 1).toLowerCase() : "";
        String mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension);
        if (mime != null) return mime;
        if ("mjs".equals(extension)) return "text/javascript";
        if ("json".equals(extension)) return "application/json";
        if ("wasm".equals(extension)) return "application/wasm";
        return "application/octet-stream";
    }
}
