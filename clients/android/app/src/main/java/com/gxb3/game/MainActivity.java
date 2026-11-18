package com.quangho.goddess.battle;

import android.app.Activity;
import android.app.AlertDialog;
import android.Manifest;
import android.content.Intent;
import android.content.Context;
import android.media.projection.MediaProjectionManager;
import android.webkit.JavascriptInterface;
import org.json.JSONObject;
import java.lang.ref.WeakReference;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.util.Log;
import android.webkit.ConsoleMessage;
import android.webkit.CookieManager;
import android.webkit.JsResult;
import android.webkit.ValueCallback;
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
    private static final String GAME_ORIGIN = "https://180-93-111-99.sslip.io";
    private static final String READY_URL = GAME_ORIGIN + "/readyz";
    private WebView webView;
    private boolean notificationPermissionAsked;
    private static final int PROFILE_PHOTO_PICK_REQUEST = 3612;
    private static final int WISH_CAPTURE_CONSENT_REQUEST = 3613;
    private static final int WISH_GALLERY_PERMISSION_REQUEST = 3614;
    private static WeakReference<MainActivity> visibleActivity = new WeakReference<>(null);
    private boolean wishCapturePermissionPending;
    private ValueCallback<Uri[]> profilePhotoCallback;

    /** Origin restricted: this JS bridge must never be available to untrusted pages. */
    private boolean isTrustedGamePage() {
        Uri current = Uri.parse(webView == null || webView.getUrl() == null
                ? "" : webView.getUrl());
        return "https".equalsIgnoreCase(current.getScheme())
                && "180-93-111-99.sslip.io".equalsIgnoreCase(current.getHost());
    }

    public final class WishRecorderBridge {
        @JavascriptInterface public boolean isSupported() { return true; }
        @JavascriptInterface public boolean isRecording() {
            return WishCaptureService.isRecording();
        }
        @JavascriptInterface public void start() {
            runOnUiThread(() -> {
                if (!isTrustedGamePage() || wishCapturePermissionPending
                        || WishCaptureService.isRecording()) return;
                beginWishScreenRecording();
            });
        }
        @JavascriptInterface public void stop() {
            runOnUiThread(() -> {
                if (!isTrustedGamePage() || !WishCaptureService.isRecording()) return;
                Intent stop=new Intent(MainActivity.this,WishCaptureService.class);
                stop.setAction(WishCaptureService.ACTION_STOP);
                startService(stop);
            });
        }
    }

    static void wishRecorderEvent(String state,String message) {
        MainActivity activity=visibleActivity.get();
        if (activity == null) return;
        activity.runOnUiThread(() -> {
            if (!activity.isTrustedGamePage()) return;
            String js="window.dispatchEvent(new CustomEvent('gxb3-wish-recording', "
                    + "{detail:{state:"+JSONObject.quote(state)
                    + ",message:"+JSONObject.quote(message)+"}}));";
            activity.webView.evaluateJavascript(js,null);
        });
    }

    private void beginWishScreenRecording() {
        if (Build.VERSION.SDK_INT <= 28 &&
                checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
            wishCapturePermissionPending=true;
            requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                    WISH_GALLERY_PERMISSION_REQUEST);
            return;
        }
        launchProjectionConsent();
    }

    private void launchProjectionConsent() {
        wishCapturePermissionPending=true;
        try {
            MediaProjectionManager manager=(MediaProjectionManager)
                    getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            startActivityForResult(manager.createScreenCaptureIntent(),
                    WISH_CAPTURE_CONSENT_REQUEST);
            wishRecorderEvent("requesting","Đang chờ quyền quay màn hình của Android.");
        } catch (Exception error) {
            wishCapturePermissionPending=false;
            wishRecorderEvent("error","Không mở được quyền ghi màn hình.");
        }
    }

    @Override public void onRequestPermissionsResult(int requestCode,
                    String[] permissions,int[] grantResults) {
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        if (requestCode != WISH_GALLERY_PERMISSION_REQUEST) return;
        wishCapturePermissionPending=false;
        if (grantResults.length>0 &&
                grantResults[0]==PackageManager.PERMISSION_GRANTED) {
            launchProjectionConsent();
        } else {
            wishRecorderEvent("error","Cần quyền lưu Video vào thư viện trên Android 8–9.");
        }
    }

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
        visibleActivity = new WeakReference<>(this);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(9, 11, 18));
        setContentView(webView);
        WebView.setWebContentsDebuggingEnabled((getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        // User-consented native recorder; the bridge performs an HTTPS origin
        // check again on the UI thread before every start/stop operation.
        webView.addJavascriptInterface(new WishRecorderBridge(),"GXB3WishRecorder");
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(false);
        // Required only for content:// grants received from the OS document
        // picker. Keep file:// access OFF to prevent local file disclosure.
        settings.setAllowContentAccess(true);
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

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                             WebChromeClient.FileChooserParams params) {
                // An installed Android WebView never opens <input type=file>
                // without this callback. Only the trusted GXB 3 HTTPS origin
                // may request a photo; no broad storage permissions are needed.
                Uri current = Uri.parse(view.getUrl() == null ? "" : view.getUrl());
                if (!"https".equalsIgnoreCase(current.getScheme())
                        || !"180-93-111-99.sslip.io".equalsIgnoreCase(current.getHost())) {
                    callback.onReceiveValue(null);
                    return true;
                }
                if (profilePhotoCallback != null) {
                    profilePhotoCallback.onReceiveValue(null);
                }
                profilePhotoCallback = callback;
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("image/*");
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                try {
                    startActivityForResult(intent, PROFILE_PHOTO_PICK_REQUEST);
                } catch (Exception error) {
                    profilePhotoCallback.onReceiveValue(null);
                    profilePhotoCallback = null;
                }
                return true;
            }

            @Override
            public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
                String text = localizeConfirm(message);
                AlertDialog dialog = new AlertDialog.Builder(MainActivity.this)
                    .setTitle("GXB 3")
                    .setMessage(text)
                    .setNegativeButton("Hủy", (d, which) -> result.cancel())
                    .setPositiveButton("Xác nhận", (d, which) -> result.confirm())
                    .setOnCancelListener(d -> result.cancel())
                    .create();
                dialog.setCanceledOnTouchOutside(false);
                dialog.show();
                return true;
            }

            @Override
            public boolean onConsoleMessage(ConsoleMessage message) {
                Log.d("GXB3-WebView", message.message()
                    + " -- line " + message.lineNumber()
                    + " of " + message.sourceId());
                return true;
            }
        });
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if ("https".equalsIgnoreCase(uri.getScheme())
                        && "180-93-111-99.sslip.io".equalsIgnoreCase(uri.getHost())) {
                    return false;
                }
                if ("https".equalsIgnoreCase(uri.getScheme())
                        || "http".equalsIgnoreCase(uri.getScheme())
                        || "zalo".equalsIgnoreCase(uri.getScheme())) {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, uri));
                    } catch (Exception ignored) { }
                }
                return true;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                Uri uri = Uri.parse(url == null ? "" : url);
                if ("https".equalsIgnoreCase(uri.getScheme())
                        && "180-93-111-99.sslip.io".equalsIgnoreCase(uri.getHost())) {
                    requestNotificationPermissionIfNeeded();
                }
            }
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showError();
                }
            }
        });

        boolean restoredProductionPage = false;
        if (state != null && webView.restoreState(state) != null) {
            String restoredUrl = webView.getUrl();
            restoredProductionPage = restoredUrl != null && restoredUrl.startsWith(GAME_ORIGIN);
            if (!restoredProductionPage) {
                // Never keep the temporary gxb3.local loading/error document as the
                // WebView origin: relative /api/* calls would fail with TypeError:
                // Failed to fetch instead of reaching the production server.
                webView.stopLoading();
                webView.clearHistory();
            }
        }
        if (restoredProductionPage) {
            CookieManager.getInstance().flush();
            return;
        }
        showLoading();
        wakeServerThenOpen();
    }

    private String localizeConfirm(String message) {
        String raw = message == null ? "" : message.trim();
        if (raw.equalsIgnoreCase("This is irreversible. Are you sure you want to do this?")) {
            return "Thao tác này không thể hoàn tác. Bạn có chắc chắn muốn tiếp tục?";
        }
        if (raw.toLowerCase().contains("irreversible")) {
            return "Thao tác này không thể hoàn tác. Bạn có chắc chắn muốn tiếp tục?";
        }
        if (raw.isEmpty()) {
            return "Bạn có chắc chắn muốn tiếp tục?";
        }
        return raw;
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

    private void requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && !notificationPermissionAsked
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            notificationPermissionAsked = true;
            requestPermissions(new String[] { Manifest.permission.POST_NOTIFICATIONS }, 1001);
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
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == WISH_CAPTURE_CONSENT_REQUEST) {
            wishCapturePermissionPending=false;
            if (resultCode == RESULT_OK && data != null && isTrustedGamePage()) {
                try {
                    Intent start=new Intent(this,WishCaptureService.class);
                    start.setAction(WishCaptureService.ACTION_START);
                    start.putExtra(WishCaptureService.EXTRA_RESULT_CODE,resultCode);
                    start.putExtra(WishCaptureService.EXTRA_RESULT_DATA,data);
                    if (Build.VERSION.SDK_INT>=26) startForegroundService(start);
                    else startService(start);
                } catch (Exception error) {
                    wishRecorderEvent("error","Không khởi động được ứng dụng quay Wish.");
                }
            } else {
                wishRecorderEvent("cancelled","Đã hủy cấp quyền quay màn hình.");
            }
            return;
        }
        if (requestCode != PROFILE_PHOTO_PICK_REQUEST) return;
        if (profilePhotoCallback != null) {
            Uri photo = resultCode == RESULT_OK && data != null ? data.getData() : null;
            profilePhotoCallback.onReceiveValue(photo == null ? null : new Uri[]{photo});
            profilePhotoCallback = null;
        }
    }

    @Override
    protected void onDestroy() {
        if (visibleActivity.get() == this) visibleActivity.clear();
        if (profilePhotoCallback != null) {
            profilePhotoCallback.onReceiveValue(null);
            profilePhotoCallback = null;
        }
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
