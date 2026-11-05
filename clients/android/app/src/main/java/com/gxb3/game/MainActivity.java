package com.quangho.goddess.battle;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.JsResult;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceResponse;
import androidx.activity.ComponentActivity;
import androidx.webkit.WebViewAssetLoader;
import androidx.work.Data;
import androidx.work.ExistingWorkPolicy;
import androidx.work.OneTimeWorkRequest;
import androidx.work.WorkInfo;
import androidx.work.WorkManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import com.quangho.goddess.battle.offline.OfflineResourceDownloadWorker;
import com.quangho.goddess.battle.offline.OfflineResourceManager;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Collections;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/** Android launcher with an explicit resource-download screen and separate online entry. */
public final class MainActivity extends ComponentActivity {
    private static final String GAME_ORIGIN = "https://180-93-111-99.sslip.io";
    private static final String GAME_HOST = "180-93-111-99.sslip.io";
    private static final int BG = Color.rgb(11, 12, 39);
    private static final int FG = Color.rgb(245, 246, 250);
    private static final int MUTED = Color.rgb(184, 192, 212);
    private static final int PURPLE = Color.rgb(139, 79, 246);

    private FrameLayout root;
    private WebView webView;
    private OfflineResourceManager resourceManager;
    private WebViewAssetLoader localAssetLoader;
    private Set<String> trustedHosts;
    private TextView resourceStatus;
    private TextView progressText;
    private ProgressBar progressBar;
    private Button downloadButton;
    private Button cancelButton;
    private Button localPreviewButton;
    private boolean installBusy;
    private boolean onlinePageVisible;
    private volatile boolean localPageVisible;
    private volatile boolean localShellAvailable;
    private ConnectivityManager connectivityManager;
    private ConnectivityManager.NetworkCallback connectivityCallback;
    private volatile boolean switchingToLocal;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(Color.BLACK);
        root = new FrameLayout(this);
        root.setBackgroundColor(BG);
        setContentView(root);
        createResourceManager();
        showResourceHome();
        registerConnectivityMonitor();
        refreshInstalledResourceStatus();
        observeDownloadWork();
    }

    /** Watches connectivity as a trigger for local fallback; it never reopens production automatically. */
    private void registerConnectivityMonitor() {
        connectivityManager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        if (connectivityManager == null) return;
        connectivityCallback = new ConnectivityManager.NetworkCallback() {
            @Override public void onLost(Network network) {
                runOnUiThread(() -> {
                    if (onlinePageVisible && !hasUsableNetwork()) switchToLocalMode("Mất kết nối mạng");
                });
            }
        };
        try {
            connectivityManager.registerDefaultNetworkCallback(connectivityCallback);
        } catch (RuntimeException ignored) {
            connectivityCallback = null;
        }
    }

    private boolean hasUsableNetwork() {
        if (connectivityManager == null) return false;
        Network network = connectivityManager.getActiveNetwork();
        if (network == null) return false;
        NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
        return capabilities != null && capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private void createResourceManager() {
        trustedHosts = parseTrustedHosts(BuildConfig.OFFLINE_RESOURCE_TRUSTED_HOSTS);
        if (trustedHosts.isEmpty()) trustedHosts = Collections.singleton(GAME_HOST);
        File appFiles = getExternalFilesDir(null);
        if (appFiles == null) appFiles = getFilesDir();
        try {
            resourceManager = new OfflineResourceManager(appFiles, trustedHosts, BuildConfig.OFFLINE_RESOURCE_PUBLIC_KEY_B64);
            localAssetLoader = new WebViewAssetLoader.Builder()
                    .setDomain("gxb3.local")
                    .addPathHandler("/", new com.quangho.goddess.battle.offline.OfflineWebViewPathHandler(resourceManager))
                    .build();
        } catch (Exception ignored) {
            resourceManager = null;
            localAssetLoader = null;
        }
    }

    private static Set<String> parseTrustedHosts(String raw) {
        HashSet<String> hosts = new HashSet<>();
        if (raw != null) {
            for (String host : raw.split(",")) {
                String normalized = host.trim().toLowerCase(Locale.ROOT);
                if (!normalized.isEmpty()) hosts.add(normalized);
            }
        }
        return hosts;
    }

    private boolean downloaderConfigured() {
        String manifestUrl = BuildConfig.OFFLINE_RESOURCE_MANIFEST_URL;
        if (manifestUrl == null || manifestUrl.trim().isEmpty()
                || BuildConfig.OFFLINE_RESOURCE_TRUSTED_HOSTS == null
                || BuildConfig.OFFLINE_RESOURCE_TRUSTED_HOSTS.trim().isEmpty()
                || BuildConfig.OFFLINE_RESOURCE_PUBLIC_KEY_B64 == null
                || BuildConfig.OFFLINE_RESOURCE_PUBLIC_KEY_B64.trim().isEmpty()) return false;
        Uri uri = Uri.parse(manifestUrl.trim());
        return "https".equalsIgnoreCase(uri.getScheme())
                && uri.getHost() != null
                && trustedHosts.contains(uri.getHost().toLowerCase(Locale.ROOT));
    }

    private void showResourceHome() {
        onlinePageVisible = false;
        localPageVisible = false;
        if (webView != null) webView.setVisibility(View.GONE);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setVerticalScrollBarEnabled(false);
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setGravity(Gravity.CENTER_HORIZONTAL);
        page.setPadding(dp(22), dp(6), dp(22), dp(20));
        page.setBackgroundColor(BG);

        FrameLayout hero = new FrameLayout(this);
        LinearLayout.LayoutParams heroParams = matchWrap();
        heroParams.height = dp(380);
        heroParams.setMargins(-dp(22), 0, -dp(22), 0);
        page.addView(hero, heroParams);

        ImageView artwork = new ImageView(this);
        artwork.setImageResource(R.drawable.offline_hero);
        artwork.setScaleType(ImageView.ScaleType.CENTER_CROP);
        artwork.setBackgroundColor(Color.rgb(19, 18, 47));
        artwork.setContentDescription("Nhân vật trong GxB3");
        hero.addView(artwork, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        View lowerFade = new View(this);
        lowerFade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[] {0x000b0c27, 0x550b0c27, BG}));
        hero.addView(lowerFade, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        TextView brand = text("G    W    B", 12, Color.rgb(187, 190, 218), true);
        brand.setGravity(Gravity.CENTER);
        brand.setLetterSpacing(0.28f);
        FrameLayout.LayoutParams brandParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        brandParams.topMargin = dp(24);
        hero.addView(brand, brandParams);

        LinearLayout heroCaption = new LinearLayout(this);
        heroCaption.setOrientation(LinearLayout.VERTICAL);
        heroCaption.setGravity(Gravity.CENTER_HORIZONTAL);
        TextView gameTitle = text("GxB3", 38, FG, true);
        gameTitle.setGravity(Gravity.CENTER);
        gameTitle.setShadowLayer(dp(5), 0f, dp(2), Color.BLACK);
        heroCaption.addView(gameTitle, matchWrap());
        TextView tagline = text("Cánh cửa định mệnh mở ra", 17, FG, true);
        tagline.setGravity(Gravity.CENTER);
        tagline.setShadowLayer(dp(4), 0f, dp(1), Color.BLACK);
        heroCaption.addView(tagline, matchWrap());
        FrameLayout.LayoutParams captionParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM);
        captionParams.bottomMargin = dp(10);
        hero.addView(heroCaption, captionParams);

        TextView intro = text("Cùng các nữ thần viết nên chương đầu tiên của bạn.", 17, FG, false);
        intro.setGravity(Gravity.CENTER);
        intro.setLineSpacing(dp(2), 1f);
        LinearLayout.LayoutParams introParams = matchWrap();
        introParams.topMargin = dp(7);
        page.addView(intro, introParams);

        resourceStatus = text("Chưa có dữ liệu trò chơi. Hãy tải để bắt đầu cuộc phiêu lưu.", 14, MUTED, false);
        resourceStatus.setGravity(Gravity.CENTER);
        resourceStatus.setLineSpacing(dp(3), 1f);
        LinearLayout.LayoutParams statusParams = matchWrap();
        statusParams.topMargin = dp(10);
        page.addView(resourceStatus, statusParams);

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(100);
        progressBar.setProgress(0);
        progressBar.setIndeterminate(false);
        progressBar.setProgressTintList(ColorStateList.valueOf(PURPLE));
        progressBar.setVisibility(View.GONE);
        LinearLayout.LayoutParams barParams = matchWrap();
        barParams.topMargin = dp(8);
        page.addView(progressBar, barParams);
        progressText = text("", 12, MUTED, false);
        progressText.setGravity(Gravity.CENTER);
        progressText.setVisibility(View.GONE);
        page.addView(progressText, matchWrap());

        Button startButton = button("Bắt đầu hành trình", true);
        LinearLayout.LayoutParams startParams = matchWrap();
        startParams.topMargin = dp(16);
        page.addView(startButton, startParams);
        startButton.setOnClickListener(view -> startOfflineJourney());

        downloadButton = button("Tải dữ liệu trò chơi", false);
        LinearLayout.LayoutParams downloadParams = matchWrap();
        downloadParams.topMargin = dp(8);
        page.addView(downloadButton, downloadParams);
        downloadButton.setOnClickListener(view -> confirmAndStartInstall());

        cancelButton = button("Hủy tải", false);
        cancelButton.setEnabled(false);
        cancelButton.setVisibility(View.GONE);
        LinearLayout.LayoutParams cancelParams = matchWrap();
        cancelParams.topMargin = dp(8);
        page.addView(cancelButton, cancelParams);
        cancelButton.setOnClickListener(view -> cancelInstall());

        Button onlineButton = button("Chơi với kết nối mạng", false);
        LinearLayout.LayoutParams onlineParams = matchWrap();
        onlineParams.topMargin = dp(8);
        page.addView(onlineButton, onlineParams);
        onlineButton.setOnClickListener(view -> startOnlineGame());

        TextView footer = text("Chế độ chơi ngoại tuyến đầy đủ vẫn đang được hoàn thiện.", 12, MUTED, false);
        footer.setGravity(Gravity.CENTER);
        footer.setLineSpacing(dp(2), 1f);
        LinearLayout.LayoutParams footerParams = matchWrap();
        footerParams.topMargin = dp(12);
        page.addView(footer, footerParams);

        localPreviewButton = null;
        scroll.addView(page, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        root.removeAllViews();
        root.addView(scroll, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        if (webView != null) root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        updateDownloaderAvailability();
    }

    private void updateDownloaderAvailability() {
        if (downloadButton == null) return;
        boolean busy = installBusy;
        boolean ready = downloaderConfigured() && resourceManager != null;
        downloadButton.setEnabled(ready && !busy);
        downloadButton.setAlpha(ready && !busy ? 1f : 0.62f);
        if (progressBar != null) progressBar.setVisibility(busy ? View.VISIBLE : View.GONE);
        if (progressText != null) progressText.setVisibility(busy ? View.VISIBLE : View.GONE);
        if (cancelButton != null) cancelButton.setVisibility(busy ? View.VISIBLE : View.GONE);
        if (localPreviewButton != null) localPreviewButton.setEnabled(localShellAvailable && !busy);
    }

    private void refreshInstalledResourceStatus() {
        if (resourceManager == null) {
            if (resourceStatus != null) resourceStatus.setText("Chưa thể mở kho dữ liệu trên thiết bị này.");
            updateDownloaderAvailability();
            return;
        }
        new Thread(() -> {
            String version = null;
            boolean installed = false;
            boolean hasEntrypoint = false;
            String issue = null;
            try {
                version = resourceManager.activeVersion();
                installed = version != null && resourceManager.isVersionInstalled(version);
                if (installed) hasEntrypoint = hasLocalEntrypoint();
            } catch (Exception error) {
                issue = error.getMessage();
            }
            final String foundVersion = version;
            final boolean isInstalled = installed;
            final boolean shellAvailable = hasEntrypoint;
            final String problem = issue;
            runOnUiThread(() -> {
                if (resourceStatus == null || isFinishing()) return;
                localShellAvailable = shellAvailable;
                if (problem != null) {
                    resourceStatus.setText("Không đọc được trạng thái dữ liệu: " + problem);
                } else if (foundVersion == null) {
                    resourceStatus.setText("Chưa có dữ liệu trò chơi. Hãy tải để bắt đầu cuộc phiêu lưu.");
                } else if (isInstalled) {
                    resourceStatus.setText("Đã cài dữ liệu " + foundVersion + ". Gameplay ngoại tuyến vẫn đang hoàn thiện.");
                } else {
                    resourceStatus.setText("Dữ liệu trò chơi chưa đầy đủ. Hãy tải lại khi tính năng tải sẵn sàng.");
                }
                if (!downloaderConfigured()) {
                    resourceStatus.append("\nTính năng tải dữ liệu hiện chưa sẵn sàng.");
                }
                updateDownloaderAvailability();
            });
        }, "gxb3-resource-status").start();
    }

    private boolean hasLocalEntrypoint() {
        try {
            OfflineResourceManager.Manifest manifest = resourceManager.activeManifest();
            return manifest != null && manifest.filesByPath.containsKey("web/index.html");
        } catch (Exception ignored) {
            return false;
        }
    }

    private void confirmAndStartInstall() {
        if (!downloaderConfigured() || resourceManager == null) {
            updateDownloaderAvailability();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Tải tài nguyên trò chơi")
                .setMessage("Ứng dụng sẽ xác minh gói dữ liệu trước khi cài vào bộ nhớ riêng. Nên dùng Wi-Fi và bảo đảm đủ dung lượng.")
                .setNegativeButton("Để sau", (dialog, which) -> { })
                .setPositiveButton("Bắt đầu tải", (dialog, which) -> startInstall())
                .show();
    }

    private void startInstall() {
        if (!downloaderConfigured() || resourceManager == null || installBusy) return;
        downloadButton.setEnabled(false);
        cancelButton.setEnabled(true);
        cancelButton.setVisibility(View.VISIBLE);
        progressBar.setVisibility(View.VISIBLE);
        progressText.setVisibility(View.VISIBLE);
        progressBar.setIndeterminate(true);
        progressBar.setProgress(0);
        progressText.setText("Đang kết nối nguồn manifest…");
        resourceStatus.setText("Đang tải và xác minh dữ liệu trò chơi…");
        try {
            Data input = new Data.Builder()
                    .putString(OfflineResourceDownloadWorker.KEY_MANIFEST_URL, BuildConfig.OFFLINE_RESOURCE_MANIFEST_URL.trim())
                    .putString(OfflineResourceDownloadWorker.KEY_TRUSTED_HOSTS, BuildConfig.OFFLINE_RESOURCE_TRUSTED_HOSTS)
                    .putString(OfflineResourceDownloadWorker.KEY_PUBLIC_KEY, BuildConfig.OFFLINE_RESOURCE_PUBLIC_KEY_B64)
                    .build();
            OneTimeWorkRequest request = new OneTimeWorkRequest.Builder(OfflineResourceDownloadWorker.class)
                    .setInputData(input)
                    .build();
            installBusy = true;
            WorkManager.getInstance(this).enqueueUniqueWork(
                    OfflineResourceDownloadWorker.UNIQUE_WORK_NAME, ExistingWorkPolicy.REPLACE, request);
            updateDownloaderAvailability();
        } catch (Exception error) {
            installBusy = false;
            progressBar.setIndeterminate(false);
            cancelButton.setEnabled(false);
            progressText.setText("Không thể bắt đầu tác vụ");
            resourceStatus.setText("Lỗi: " + safeMessage(error));
            updateDownloaderAvailability();
        }
    }

    private void observeDownloadWork() {
        WorkManager.getInstance(this).getWorkInfosForUniqueWorkLiveData(OfflineResourceDownloadWorker.UNIQUE_WORK_NAME)
                .observe(this, workInfos -> {
                    if (workInfos == null || workInfos.isEmpty() || isFinishing()) return;
                    WorkInfo info = workInfos.get(workInfos.size() - 1);
                    WorkInfo.State state = info.getState();
                    installBusy = state == WorkInfo.State.ENQUEUED || state == WorkInfo.State.RUNNING || state == WorkInfo.State.BLOCKED;
                    if (installBusy) {
                        cancelButton.setEnabled(true);
                        renderWorkProgress(info.getProgress());
                    } else if (state == WorkInfo.State.SUCCEEDED) {
                        Data result = info.getOutputData();
                        String version = result.getString(OfflineResourceDownloadWorker.KEY_VERSION);
                        int packs = result.getInt(OfflineResourceDownloadWorker.KEY_PACK_COUNT, 0);
                        int files = result.getInt(OfflineResourceDownloadWorker.KEY_FILE_COUNT, 0);
                        progressBar.setIndeterminate(false);
                        progressBar.setProgress(100);
                        progressText.setText("Hoàn tất · " + packs + " gói · " + files + " file");
                        resourceStatus.setText("Đã cài dữ liệu " + version + ". Gameplay ngoại tuyến vẫn đang hoàn thiện.");
                        cancelButton.setEnabled(false);
                        localShellAvailable = false;
                        if (localPreviewButton != null) localPreviewButton.setEnabled(false);
                        refreshInstalledResourceStatus();
                    } else if (state == WorkInfo.State.FAILED) {
                        String message = info.getOutputData().getString(OfflineResourceDownloadWorker.KEY_ERROR);
                        progressBar.setIndeterminate(false);
                        progressText.setText("Tải chưa hoàn thành");
                        resourceStatus.setText("Không cài được resource: " + (message == null ? "lỗi không xác định" : message));
                        cancelButton.setEnabled(false);
                    } else if (state == WorkInfo.State.CANCELLED) {
                        progressBar.setIndeterminate(false);
                        progressText.setText("Đã hủy · phần tải dở được giữ để tiếp tục");
                        resourceStatus.setText("Đã hủy tải dữ liệu. Bạn có thể tiếp tục lại sau.");
                        cancelButton.setEnabled(false);
                    }
                    updateDownloaderAvailability();
                });
    }

    private void renderWorkProgress(Data data) {
        if (isFinishing() || progressBar == null) return;
        String rawPhase = data.getString(OfflineResourceDownloadWorker.KEY_PHASE);
        if (rawPhase == null || OfflineResourceManager.Phase.FETCHING_MANIFEST.name().equals(rawPhase)) {
            progressBar.setIndeterminate(true);
            progressText.setText("Đang lấy manifest…");
            return;
        }
        long completed = data.getLong(OfflineResourceDownloadWorker.KEY_COMPLETED_BYTES, 0L);
        long total = data.getLong(OfflineResourceDownloadWorker.KEY_TOTAL_BYTES, 0L);
        int percent = total <= 0 ? 0 : (int) Math.min(100L, completed * 100L / total);
        progressBar.setIndeterminate(false);
        progressBar.setProgress(percent);
        String phase = rawPhase;
        try { phase = phaseLabel(OfflineResourceManager.Phase.valueOf(rawPhase)); } catch (Exception ignored) { }
        String packId = data.getString(OfflineResourceDownloadWorker.KEY_PACK_ID);
        String pack = packId == null ? "" : " · " + packId.substring(0, Math.min(12, packId.length()));
        int index = data.getInt(OfflineResourceDownloadWorker.KEY_PACK_INDEX, 0);
        int count = data.getInt(OfflineResourceDownloadWorker.KEY_PACK_COUNT, 0);
        String packCount = count > 0 ? " · gói " + index + "/" + count : "";
        String fraction = total > 0 ? " · " + formatBytes(completed) + " / " + formatBytes(total) : "";
        progressText.setText(phase + pack + packCount + fraction + " · " + percent + "%");
    }

    private void cancelInstall() {
        WorkManager.getInstance(this).cancelUniqueWork(OfflineResourceDownloadWorker.UNIQUE_WORK_NAME);
        cancelButton.setEnabled(false);
        progressText.setText("Đang dừng an toàn; phần tải dở được giữ để tiếp tục sau.");
    }

    private static String phaseLabel(OfflineResourceManager.Phase phase) {
        switch (phase) {
            case DOWNLOADING_PACK: return "Đang tải";
            case VERIFYING_PACK: return "Đang xác minh gói";
            case INSTALLING_FILES: return "Đang cài file";
            case ACTIVATING: return "Đang kích hoạt release";
            case COMPLETE: return "Hoàn tất";
            default: return "Đang chuẩn bị";
        }
    }

    private static String formatBytes(long bytes) {
        if (bytes < 1024L) return bytes + " B";
        if (bytes < 1024L * 1024L) return String.format(Locale.ROOT, "%.1f KiB", bytes / 1024.0);
        if (bytes < 1024L * 1024L * 1024L) return String.format(Locale.ROOT, "%.1f MiB", bytes / (1024.0 * 1024.0));
        return String.format(Locale.ROOT, "%.2f GiB", bytes / (1024.0 * 1024.0 * 1024.0));
    }

    private static String safeMessage(Throwable error) {
        if (error == null) return "Lỗi không xác định";
        String message = error.getMessage();
        return message == null || message.trim().isEmpty() ? error.getClass().getSimpleName() : message;
    }

    private void startOnlineGame() {
        if (onlinePageVisible) return;
        switchingToLocal = false;
        localPageVisible = false;
        onlinePageVisible = true;
        if (webView == null) createWebView();
        webView.setVisibility(View.VISIBLE);
        webView.bringToFront();
        showLoading();
        wakeServerThenOpen();
    }

    private void openLocalShellPreview() {
        if (!localShellAvailable || resourceManager == null || localAssetLoader == null) {
            resourceStatus.setText("Không có web/index.html hợp lệ trong resource release đã cài.");
            return;
        }
        onlinePageVisible = false;
        localPageVisible = true;
        if (webView == null) createWebView();
        webView.setVisibility(View.VISIBLE);
        webView.bringToFront();
        webView.loadUrl("https://gxb3.local/");
    }

    private void startOfflineJourney() {
        if (localShellAvailable && resourceManager != null && localAssetLoader != null) {
            new AlertDialog.Builder(this)
                    .setTitle("Chế độ ngoại tuyến")
                    .setMessage("Dữ liệu giao diện local đã có, nhưng API trận đấu và lưu tiến trình offline chưa được tích hợp trong bản này.")
                    .setNegativeButton("Để sau", (dialog, which) -> { })
                    .setPositiveButton("Xem thử giao diện", (dialog, which) -> openLocalShellPreview())
                    .show();
            return;
        }
        if (downloaderConfigured() && resourceManager != null) {
            confirmAndStartInstall();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Chưa có dữ liệu trò chơi")
                .setMessage("Tính năng tải dữ liệu hiện chưa sẵn sàng. Bạn vẫn có thể vào bản chơi trực tuyến.")
                .setNegativeButton("Để sau", (dialog, which) -> { })
                .setPositiveButton("Chơi trực tuyến", (dialog, which) -> startOnlineGame())
                .show();
    }

    /** Switches to the installed local release without falling back to production. */
    private void switchToLocalMode(String reason) {
        if (switchingToLocal || localPageVisible || !onlinePageVisible) return;
        switchingToLocal = true;
        if (localShellAvailable && resourceManager != null && localAssetLoader != null) {
            onlinePageVisible = false;
            localPageVisible = true;
            if (webView == null) createWebView();
            webView.setVisibility(View.VISIBLE);
            webView.bringToFront();
            webView.loadUrl("https://gxb3.local/");
            switchingToLocal = false;
            return;
        }
        onlinePageVisible = false;
        localPageVisible = false;
        if (webView != null) {
            webView.setVisibility(View.VISIBLE);
            webView.bringToFront();
            webView.loadDataWithBaseURL("https://gxb3.local/", offlineUnavailableHtml(reason), "text/html", "UTF-8", null);
        }
        switchingToLocal = false;
    }

    private void createWebView() {
        webView = new WebView(this);
        webView.setBackgroundColor(BG);
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
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
                AlertDialog dialog = new AlertDialog.Builder(MainActivity.this)
                        .setTitle("GXB 3")
                        .setMessage(localizeConfirm(message))
                        .setNegativeButton("Hủy", (d, which) -> result.cancel())
                        .setPositiveButton("Xác nhận", (d, which) -> result.confirm())
                        .setOnCancelListener(d -> result.cancel())
                        .create();
                dialog.setCanceledOnTouchOutside(false);
                dialog.show();
                return true;
            }
        });
        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (!localPageVisible) return null;
                Uri uri = request.getUrl();
                if ("https".equalsIgnoreCase(uri.getScheme()) && "gxb3.local".equalsIgnoreCase(uri.getHost())
                        && localAssetLoader != null) {
                    WebResourceResponse response = localAssetLoader.shouldInterceptRequest(uri);
                    return response == null ? blockedLocalResponse(404, "Not Found") : response;
                }
                return blockedLocalResponse(403, "Forbidden");
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if (localPageVisible) return "https".equalsIgnoreCase(uri.getScheme()) && "gxb3.local".equalsIgnoreCase(uri.getHost()) ? false : true;
                if ("https".equalsIgnoreCase(uri.getScheme()) && GAME_HOST.equalsIgnoreCase(uri.getHost())) return false;
                if ("https".equalsIgnoreCase(uri.getScheme()) || "http".equalsIgnoreCase(uri.getScheme()) || "zalo".equalsIgnoreCase(uri.getScheme())) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) { }
                }
                return true;
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame() && onlinePageVisible) {
                    switchToLocalMode("Không kết nối được máy chủ trực tuyến");
                }
            }
        });
        root.addView(webView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
    }

    private static WebResourceResponse blockedLocalResponse(int status, String reason) {
        byte[] body = reason.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        return new WebResourceResponse("text/plain", "UTF-8", status, reason,
                Collections.singletonMap("Cache-Control", "no-store"), new ByteArrayInputStream(body));
    }

    private String localizeConfirm(String message) {
        String raw = message == null ? "" : message.trim();
        if (raw.equalsIgnoreCase("This is irreversible. Are you sure you want to do this?") || raw.toLowerCase(Locale.ROOT).contains("irreversible")) {
            return "Thao tác này không thể hoàn tác. Bạn có chắc chắn muốn tiếp tục?";
        }
        return raw.isEmpty() ? "Bạn có chắc chắn muốn tiếp tục?" : raw;
    }

    private void showLoading() {
        webView.loadDataWithBaseURL("https://gxb3.local/", loadingHtml(), "text/html", "UTF-8", null);
    }

    private void showError() {
        webView.loadDataWithBaseURL("https://gxb3.local/", errorHtml(), "text/html", "UTF-8", null);
    }

    private static String loadingHtml() {
        return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<style>html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:sans-serif}"
                + ".w{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:18px}"
                + ".l{font-size:38px;font-weight:800;letter-spacing:3px}.s{color:#b9c1d9;font-size:14px;text-align:center;padding:0 24px}"
                + ".p{width:42px;height:42px;border:4px solid #252b3d;border-top-color:#8f5cff;border-radius:50%;animation:r 1s linear infinite}"
                + "@keyframes r{to{transform:rotate(360deg)}}</style></head><body><div class='w'><div class='l'>GXB 3</div>"
                + "<div class='p'></div><div class='s'>Đang kết nối chế độ trực tuyến…</div></div></body></html>";
    }

    private static String errorHtml() {
        return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<style>html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:sans-serif}"
                + ".w{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:24px;box-sizing:border-box}"
                + "p{color:#b9c1d9;line-height:1.6}</style></head><body><div class='w'><h1>GXB 3</h1>"
                + "<p>Không thể kết nối máy chủ trực tuyến.<br>Hãy quay lại màn hình tài nguyên hoặc kiểm tra mạng.</p></div></body></html>";
    }

    private static String offlineUnavailableHtml(String reason) {
        String safeReason = reason == null ? "Mất kết nối mạng" : reason.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
        return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<style>html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:sans-serif}"
                + ".w{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:24px;box-sizing:border-box}"
                + "p{color:#b9c1d9;line-height:1.6;max-width:420px}</style></head><body><div class='w'><h1>GXB 3 · Local mode</h1>"
                + "<p>" + safeReason + ".</p><p>Chưa có resource release local hợp lệ để mở game. Hãy kết nối mạng, tải tài nguyên offline một lần rồi thử lại.</p></div></body></html>";
    }

    private boolean serverReady() {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(GAME_ORIGIN + "/readyz").openConnection();
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(15000);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("User-Agent", "GXB3-Android/1.0");
            if (connection.getResponseCode() != 200) return false;
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            StringBuilder body = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null && body.length() < 65536) body.append(line);
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
            while (!isFinishing() && onlinePageVisible && System.currentTimeMillis() < deadline) {
                if (serverReady()) {
                    runOnUiThread(() -> { if (onlinePageVisible && webView != null) webView.loadUrl(GAME_ORIGIN); });
                    return;
                }
                try { Thread.sleep(3000L); }
                catch (InterruptedException error) { Thread.currentThread().interrupt(); return; }
            }
            runOnUiThread(() -> {
                if (onlinePageVisible && webView != null) switchToLocalMode("Máy chủ trực tuyến không phản hồi");
            });
        }, "gxb3-online-server-wakeup").start();
    }

    private TextView text(String value, float sp, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private Button button(String label, boolean primary) {
        Button view = new Button(this);
        view.setText(label);
        view.setAllCaps(false);
        view.setTextSize(16);
        view.setTextColor(FG);
        view.setPadding(dp(16), 0, dp(16), 0);
        view.setMinimumHeight(dp(52));
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(primary ? PURPLE : Color.rgb(39, 45, 68));
        shape.setCornerRadius(dp(4));
        view.setBackground(new RippleDrawable(ColorStateList.valueOf(0x33ffffff), shape, null));
        return view;
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        if (webView != null && onlinePageVisible) webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override public void onBackPressed() {
        if (localPageVisible) {
            showResourceHome();
        } else if (onlinePageVisible && webView != null) {
            if (webView.canGoBack()) webView.goBack();
            else showResourceHome();
        } else {
            super.onBackPressed();
        }
    }

    @Override protected void onDestroy() {
        if (connectivityManager != null && connectivityCallback != null) {
            try { connectivityManager.unregisterNetworkCallback(connectivityCallback); } catch (RuntimeException ignored) { }
        }
        if (resourceManager != null) resourceManager.close();
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }
}
