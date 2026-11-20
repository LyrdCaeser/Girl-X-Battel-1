package com.quangho.goddess.battle;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.MediaRecorder;
import android.media.MediaScannerConnection;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.MediaStore;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Surface;
import android.view.WindowManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * User-consented real screen recording for S4 Wish, saved as H.264 MP4 to
 * Movies/GXB3 Wish via MediaStore. No uploads and no game-state modification.
 *
 * Android 14+ requires a fresh MediaProjection permission token per session,
 * a mediaProjection foreground service and callback before createVirtualDisplay.
 * The notification provides Stop even when the Wish WebView is paused.
 */
public final class WishCaptureService extends Service {
    public static final String ACTION_START = "com.quangho.goddess.battle.WISH_START";
    public static final String ACTION_STOP  = "com.quangho.goddess.battle.WISH_STOP";
    public static final String EXTRA_RESULT_CODE = "projectionResultCode";
    public static final String EXTRA_RESULT_DATA = "projectionResultData";
    private static final String CHANNEL = "wish_recording";
    private static final int NOTIFICATION_ID = 42017;
    private static volatile boolean recording = false;

    private MediaProjection projection;
    private VirtualDisplay display;
    private MediaRecorder recorder;
    private File temporary;
    private long startedAt;
    private boolean finishing;
    private MediaProjection.Callback projectionCallback;

    public static boolean isRecording() { return recording; }

    @Override public IBinder onBind(Intent intent) { return null; }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;
        if (ACTION_STOP.equals(intent.getAction())) {
            finishCapture(true);
            return START_NOT_STICKY;
        }
        if (!ACTION_START.equals(intent.getAction()) || finishing || recording || recorder != null) {
            return START_NOT_STICKY;
        }
        try {
            makeForeground();
            int resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0);
            @SuppressWarnings("deprecation")
            Intent token = (Intent) intent.getParcelableExtra(EXTRA_RESULT_DATA);
            if (resultCode != android.app.Activity.RESULT_OK || token == null) {
                throw new IllegalArgumentException("Thiếu quyền quay màn hình");
            }
            beginCapture(resultCode, token);
            recording = true;
            startedAt = System.currentTimeMillis();
            MainActivity.wishRecorderEvent("recording", "Đang quay Wish");
        } catch (Exception | LinkageError e) {
            Log.e("GXB3-WishRecorder", "Cannot start MediaProjection", e);
            MainActivity.wishRecorderEvent("error", "Không khởi động được ghi màn hình.");
            cleanup();
            stopSelf();
        }
        return START_NOT_STICKY;
    }

    private void makeForeground() {
        NotificationManager manager=(NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel=new NotificationChannel(CHANNEL,
                    "Đang quay Wish", NotificationManager.IMPORTANCE_LOW);
            channel.setDescription("Thông báo tiến trình ghi màn hình Wish S4.");
            manager.createNotificationChannel(channel);
        }
        Intent stop = new Intent(this, WishCaptureService.class);
        stop.setAction(ACTION_STOP);
        PendingIntent stopAction=PendingIntent.getService(this,42,stop,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b=Build.VERSION.SDK_INT>=26
                ?new Notification.Builder(this, CHANNEL):new Notification.Builder(this);
        b.setSmallIcon(android.R.drawable.presence_video_online)
         .setContentTitle("GXB 3 • Đang quay Wish")
         .setContentText("Chạm Dừng để lưu video vào Thư viện.")
         .setOngoing(true).setCategory(Notification.CATEGORY_SERVICE)
         .addAction(new Notification.Action.Builder(
                 android.R.drawable.ic_media_pause,"Dừng và lưu",stopAction).build());
        if (Build.VERSION.SDK_INT >= 29) {
            startForeground(NOTIFICATION_ID,b.build(),
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
        } else {
            startForeground(NOTIFICATION_ID,b.build());
        }
    }

    private void beginCapture(int code,Intent token) throws Exception {
        DisplayMetrics metrics=new DisplayMetrics();
        WindowManager window=(WindowManager)getSystemService(Context.WINDOW_SERVICE);
        @SuppressWarnings("deprecation")
        android.view.Display actual=window.getDefaultDisplay();
        actual.getRealMetrics(metrics);
        // Bound video encoding to 1080x1920 for entry-level phones.
        float ratio=Math.min(1.0f,Math.min(1080.0f/Math.max(1,metrics.widthPixels),
                                        1920.0f/Math.max(1,metrics.heightPixels)));
        int width=Math.max(16,((int)(metrics.widthPixels*ratio)/16)*16);
        int height=Math.max(16,((int)(metrics.heightPixels*ratio)/16)*16);
        temporary=new File(getCacheDir(),"wish_capture_"+System.currentTimeMillis()+".mp4");

        recorder=new MediaRecorder();
        recorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
        recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        recorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
        recorder.setVideoSize(width,height);
        recorder.setVideoFrameRate(24);
        recorder.setVideoEncodingBitRate(4_000_000);
        recorder.setOutputFile(temporary.getAbsolutePath());
        recorder.prepare();

        MediaProjectionManager mgr=(MediaProjectionManager)getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        projection=mgr.getMediaProjection(code,token);
        if (projection==null) throw new IllegalStateException("Android không cấp quyền ghi màn hình");
        projectionCallback=new MediaProjection.Callback() {
            @Override public void onStop() {
                new Handler(Looper.getMainLooper()).post(()->finishCapture(true));
            }
        };
        projection.registerCallback(projectionCallback,new Handler(Looper.getMainLooper()));
        Surface surface=recorder.getSurface();
        display=projection.createVirtualDisplay("GXB3 Wish",
                width,height,metrics.densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                surface,null,new Handler(Looper.getMainLooper()));
        recorder.start();
    }

    private void finishCapture(boolean save) {
        if (finishing) return;
        finishing=true;
        boolean good=recording && recorder!=null && System.currentTimeMillis()-startedAt>=800;
        if (display!=null) { display.release(); display=null; }
        if (recorder!=null) {
            try { recorder.stop(); } catch (RuntimeException error) {
                good=false;
                Log.w("GXB3-WishRecorder","Incomplete MP4 removed",error);
            }
        }
        recording=false;
        if (projection!=null) {
            try { projection.unregisterCallback(projectionCallback); } catch (Exception ignored) { }
            try { projection.stop(); } catch (Exception ignored) { }
            projection=null;
        }
        if (recorder!=null) {
            try { recorder.reset();recorder.release(); } catch (Exception ignored) { }
            recorder=null;
        }
        final File clip=temporary;
        temporary=null;
        if (save && good && clip!=null && clip.isFile() && clip.length()>1024) {
            // MediaStore may need to copy hundreds of MB. Never block the
            // WebView/UI thread (previous Wish freezes were unacceptable).
            new Thread(() -> {
                String state="saved",detail="Đã lưu video vào Thư viện → GXB3 Wish.";
                try {
                    String name="GXB3_Wish_S4_"+new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US)
                            .format(new Date())+".mp4";
                    saveToGallery(clip,name);
                } catch (Exception error) {
                    Log.e("GXB3-WishRecorder","Cannot save MP4",error);
                    state="error";detail="Không lưu được video vào Thư viện.";
                } finally {
                    clip.delete();
                    final String reportState=state,reportDetail=detail;
                    new Handler(Looper.getMainLooper()).post(() -> {
                        MainActivity.wishRecorderEvent(reportState,reportDetail);
                        try {stopForeground(STOP_FOREGROUND_REMOVE);}catch(Exception ignored){}
                        stopSelf();
                    });
                }
            },"gxb3-wish-save-video").start();
        } else {
            if (clip!=null)clip.delete();
            MainActivity.wishRecorderEvent("cancelled",
                    "Video quá ngắn hoặc phiên quay đã bị dừng.");
            try {stopForeground(STOP_FOREGROUND_REMOVE);}catch(Exception ignored){}
            stopSelf();
        }
    }

    private void saveToGallery(File input,String filename) throws Exception {
        if (Build.VERSION.SDK_INT>=29) {
            ContentValues values=new ContentValues();
            values.put(MediaStore.Video.Media.DISPLAY_NAME,filename);
            values.put(MediaStore.Video.Media.MIME_TYPE,"video/mp4");
            values.put(MediaStore.Video.Media.RELATIVE_PATH,Environment.DIRECTORY_MOVIES+"/GXB3 Wish");
            values.put(MediaStore.Video.Media.IS_PENDING,1);
            Uri saved=getContentResolver().insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI,values);
            if (saved==null) throw new IllegalStateException("MediaStore từ chối lưu video");
            try {
                try (FileInputStream in=new FileInputStream(input);
                     OutputStream out=getContentResolver().openOutputStream(saved,"w")) {
                    if (out==null) throw new IllegalStateException("Không mở được đích video");
                    byte[] buffer=new byte[65536];int n;
                    while ((n=in.read(buffer))!=-1)out.write(buffer,0,n);
                }
                ContentValues publish=new ContentValues();
                publish.put(MediaStore.Video.Media.IS_PENDING,0);
                getContentResolver().update(saved,publish,null,null);
            } catch (Exception error) {
                getContentResolver().delete(saved,null,null);
                throw error;
            }
        } else {
            // On Android 8–9, Activity requests legacy WRITE permission prior
            // to MediaProjection, so this public Movies folder is writable.
            File folder=new File(Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_MOVIES),"GXB3 Wish");
            if (!folder.exists()&&!folder.mkdirs())throw new IllegalStateException("Không tạo được thư mục Video");
            File target=new File(folder,filename);
            try (FileInputStream in=new FileInputStream(input);
                 FileOutputStream out=new FileOutputStream(target)) {
                byte[] buffer=new byte[65536];int n;
                while ((n=in.read(buffer))!=-1)out.write(buffer,0,n);
            } catch (Exception error) {
                target.delete();throw error;
            }
            MediaScannerConnection.scanFile(this,new String[]{target.getAbsolutePath()},
                    new String[]{"video/mp4"},null);
        }
    }

    private void cleanup() {
        recording=false;
        if (display!=null) {display.release();display=null;}
        if (projection!=null) {
            try {projection.unregisterCallback(projectionCallback);}catch(Exception ignored){}
            try {projection.stop();}catch(Exception ignored){}
            projection=null;
        }
        if (recorder!=null) {
            try {recorder.reset();recorder.release();}catch(Exception ignored){}
            recorder=null;
        }
        if (temporary!=null) {temporary.delete();temporary=null;}
        try {stopForeground(STOP_FOREGROUND_REMOVE);}catch(Exception ignored){}
    }

    @Override public void onDestroy() {
        if (recording && !finishing) finishCapture(true);
        else if(!finishing)cleanup();
        super.onDestroy();
    }
}
