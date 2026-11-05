package com.quangho.goddess.battle.offline;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.pm.ServiceInfo;
import android.os.Build;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;
import androidx.work.Data;
import androidx.work.ForegroundInfo;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import java.io.File;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.TimeUnit;

/** Long-running, resumable resource install independent of the Activity lifecycle. */
public final class OfflineResourceDownloadWorker extends Worker {
    public static final String UNIQUE_WORK_NAME = "gxb3-offline-resource-install";
    public static final String KEY_MANIFEST_URL = "manifest_url";
    public static final String KEY_TRUSTED_HOSTS = "trusted_hosts";
    public static final String KEY_PUBLIC_KEY = "public_key_b64";
    public static final String KEY_PHASE = "phase";
    public static final String KEY_PACK_ID = "pack_id";
    public static final String KEY_PACK_INDEX = "pack_index";
    public static final String KEY_PACK_COUNT = "pack_count";
    public static final String KEY_COMPLETED_BYTES = "completed_bytes";
    public static final String KEY_TOTAL_BYTES = "total_bytes";
    public static final String KEY_VERSION = "resource_version";
    public static final String KEY_FILE_COUNT = "file_count";
    public static final String KEY_ERROR = "error";

    private static final String CHANNEL_ID = "gxb3-resource-download";
    private static final int NOTIFICATION_ID = 3407;
    private volatile OfflineResourceManager resourceManager;
    private long lastProgressTimeNanos;
    private long lastProgressBytes;

    public OfflineResourceDownloadWorker(@NonNull Context context, @NonNull WorkerParameters parameters) {
        super(context, parameters);
    }

    @NonNull @Override public Result doWork() {
        String manifestUrl = getInputData().getString(KEY_MANIFEST_URL);
        String hostsCsv = getInputData().getString(KEY_TRUSTED_HOSTS);
        String publicKey = getInputData().getString(KEY_PUBLIC_KEY);
        if (manifestUrl == null || hostsCsv == null || publicKey == null) {
            return Result.failure(outputError("Missing signed resource source configuration"));
        }
        Set<String> hosts = new HashSet<>();
        for (String host : hostsCsv.split(",")) {
            if (!host.trim().isEmpty()) hosts.add(host.trim().toLowerCase(Locale.ROOT));
        }
        try {
            setForegroundAsync(createForegroundInfo("Đang chuẩn bị tải gói đã ký", 0, true)).get(20, TimeUnit.SECONDS);
            if (isStopped()) return Result.failure(outputError("Download cancelled before starting"));
            File root = getApplicationContext().getExternalFilesDir(null);
            if (root == null) root = getApplicationContext().getFilesDir();
            resourceManager = new OfflineResourceManager(root, hosts, publicKey);
            OfflineResourceManager.InstallResult result = resourceManager.installFromUrl(manifestUrl,
                    new OfflineResourceManager.Listener() {
                        @Override public void onProgress(OfflineResourceManager.Progress progress) {
                            publishProgress(progress);
                        }
                        @Override public void onComplete(OfflineResourceManager.InstallResult result) { }
                        @Override public void onError(Throwable error) { }
                    });
            Data output = new Data.Builder()
                    .putString(KEY_VERSION, result.resourceVersion)
                    .putInt(KEY_FILE_COUNT, result.fileCount)
                    .putInt(KEY_PACK_COUNT, result.packCount)
                    .build();
            return Result.success(output);
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            return Result.failure(outputError("Download interrupted; partial pack is retained for resume"));
        } catch (Exception error) {
            if (isStopped()) return Result.failure(outputError("Download cancelled; partial pack is retained for resume"));
            return Result.failure(outputError(safeMessage(error)));
        } finally {
            OfflineResourceManager manager = resourceManager;
            resourceManager = null;
            if (manager != null) manager.close();
        }
    }

    private void publishProgress(OfflineResourceManager.Progress progress) {
        long now = System.nanoTime();
        boolean terminalOrPhaseChange = progress.phase != OfflineResourceManager.Phase.DOWNLOADING_PACK;
        if (!terminalOrPhaseChange && now - lastProgressTimeNanos < TimeUnit.MILLISECONDS.toNanos(400)
                && progress.completedBytes - lastProgressBytes < 1024L * 1024L) return;
        lastProgressTimeNanos = now;
        lastProgressBytes = progress.completedBytes;
        Data data = new Data.Builder()
                .putString(KEY_PHASE, progress.phase.name())
                .putString(KEY_PACK_ID, progress.packId)
                .putInt(KEY_PACK_INDEX, progress.packIndex)
                .putInt(KEY_PACK_COUNT, progress.packCount)
                .putLong(KEY_COMPLETED_BYTES, progress.completedBytes)
                .putLong(KEY_TOTAL_BYTES, progress.totalBytes)
                .build();
        setProgressAsync(data);
        int percent = progress.totalBytes <= 0 ? 0 : (int) Math.min(100L, progress.completedBytes * 100L / progress.totalBytes);
        String message = progress.totalBytes > 0
                ? "Đang tải tài nguyên · " + percent + "%"
                : "Đang xác minh và cài tài nguyên";
        setForegroundAsync(createForegroundInfo(message, percent, progress.totalBytes <= 0));
    }

    private ForegroundInfo createForegroundInfo(String message, int progress, boolean indeterminate) {
        Context context = getApplicationContext();
        NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, "Tải tài nguyên trò chơi", NotificationManager.IMPORTANCE_LOW);
            if (manager != null) manager.createNotificationChannel(channel);
        }
        Notification notification = new NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.stat_sys_download)
                .setContentTitle("GXB 3 · Tải tài nguyên")
                .setContentText(message)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setProgress(100, progress, indeterminate)
                .build();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            return new ForegroundInfo(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
        }
        return new ForegroundInfo(NOTIFICATION_ID, notification);
    }

    private static Data outputError(String message) {
        return new Data.Builder().putString(KEY_ERROR, message).build();
    }

    private static String safeMessage(Throwable error) {
        if (error == null) return "Unknown download error";
        String message = error.getMessage();
        return message == null || message.trim().isEmpty() ? error.getClass().getSimpleName() : message;
    }

    @Override public void onStopped() {
        OfflineResourceManager manager = resourceManager;
        if (manager != null) manager.cancel();
        super.onStopped();
    }
}
