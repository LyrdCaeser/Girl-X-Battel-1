package com.gxb3.game;

import android.app.Activity;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public final class MainActivity extends Activity {
    private static final String GAME_ORIGIN = "https://gxb3-production.onrender.com";
    private static final String READY_URL = GAME_ORIGIN + "/readyz";
    private WebView webView;

    private static final String LOADING_HTML =
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        + "<style>html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:sans-serif}"
        + ".w{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:18px}"
        + ".l{font-size:38px;font-weight:800;letter-spacing:3px}.s{color:#b9c1d9;font-size:14px;text-align:center;padding:0 24px}"
        + ".p{width:42px;height:42px;border:4px solid #252b3d;border-top-color:#8f5cff;border-radius:50%;animation:r 1s linear infinite}"
        + "@keyframes r{to{transform:rotate(360deg)}}</style></head><body><div class='w'>"
        + "<div class='l'>GXB 3</div><div class='p'></div><div class='s'>Đang khởi động máy chủ và chuẩn bị trò chơi...</div>"
        + "</div></body></html>";

    private static final String ERROR_HTML =
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        + "<style>html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:sans-serif}"
        + ".w{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:24px;box-sizing:border-box}"
        + "p{color:#b9c1d9;line-height:1.6}</style></head><body><div class='w'><h1>GXB 3</h1>"
        + "<p>Không thể kết nối máy chủ.<br>Kiểm tra mạng rồi mở lại trò chơi.</p></div></body></html>";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(9, 11, 18));
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setUseWideViewPort(false);
        settings.setLoadWithOverviewMode(false);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(100);
        settings.setUserAgentString(settings.getUserAgentString() + " GXB3-Android/1.0 MobileApp");

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(webView, false);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                return !("https".equalsIgnoreCase(uri.getScheme())
                        && "gxb3-production.onrender.com".equalsIgnoreCase(uri.getHost()));
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showError();
                }
            }
        });

        if (state != null && webView.restoreState(state) != null) {
            return;
        }
        showLoading();
        wakeServerThenOpen();
    }

    private void showLoading() {
        webView.loadDataWithBaseURL("https://gxb3.local/", LOADING_HTML, "text/html", "UTF-8", null);
    }

    private void showError() {
        webView.loadDataWithBaseURL("https://gxb3.local/", ERROR_HTML, "text/html", "UTF-8", null);
    }

    private boolean serverReady() {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(READY_URL).openConnection();
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(15000);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("User-Agent", "GXB3-Android/1.0");
            if (connection.getResponseCode() != 200) {
                return false;
            }
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            StringBuilder body = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null && body.length() < 65536) {
                body.append(line);
            }
            reader.close();
            String compact = body.toString().replace(" ", "").replace("\n", "").replace("\r", "");
            return compact.contains("\"ready\":true");
        } catch (Exception ignored) {
            return false;
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void wakeServerThenOpen() {
        new Thread(() -> {
            long deadline = System.currentTimeMillis() + 150000L;
            while (System.currentTimeMillis() < deadline) {
                if (serverReady()) {
                    runOnUiThread(() -> webView.loadUrl(GAME_ORIGIN));
                    return;
                }
                try {
                    Thread.sleep(3000L);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
            runOnUiThread(this::showError);
        }, "gxb3-server-wakeup").start();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
