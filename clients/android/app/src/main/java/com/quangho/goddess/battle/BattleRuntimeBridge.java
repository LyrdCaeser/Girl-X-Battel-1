package com.quangho.goddess.battle;

import android.content.Context;
import android.content.res.AssetManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

/**
 * Small JNI boundary for the existing Lua battle_host.lua contract.
 *
 * The caller supplies the same Lua table literal that the desktop adapter writes
 * to its temporary input file. The native side executes battle_host.lua inside
 * LuaJIT and returns the JSON report printed by the host.
 */
public final class BattleRuntimeBridge {
    private static final String RUNTIME_DIR = "battle-runtime-v1";
    private static final String INPUT_DIR = "battle-input";
    private static final Object INSTALL_LOCK = new Object();
    private static volatile boolean loaded;

    static {
        System.loadLibrary("gxb_battle");
        loaded = true;
    }

    private BattleRuntimeBridge() {}

    /** Extracts battle_host.lua and the Lua module tree into app-private storage. */
    public static File installRuntime(Context context) throws IOException {
        File root = new File(context.getFilesDir(), RUNTIME_DIR);
        synchronized (INSTALL_LOCK) {
            File marker = new File(root, ".commit-c6ffc141");
            if (!marker.isFile()) {
                deleteTree(root);
                if (!root.mkdirs() && !root.isDirectory()) {
                    throw new IOException("Cannot create battle runtime directory");
                }
                copyAsset(context.getAssets(), "battle_host.lua", new File(root, "battle_host.lua"));
                copyTree(context.getAssets(), "lua", new File(root, "lua"));
                writeAtomically(marker, "c6ffc141a8762b41703f9287d63d93622a13dd8f\n");
            }
        }
        return root;
    }

    /**
     * Executes one validated battle request. The input is a Lua return-table
     * literal, not arbitrary Lua code selected by the UI.
     */
    public static String runBattle(Context context, String mode, String inputLua) throws IOException {
        if (!"battle".equals(mode) && !"attrs".equals(mode)) {
            throw new IllegalArgumentException("Unsupported local battle mode: " + mode);
        }
        if (inputLua == null || inputLua.length() == 0 || inputLua.length() > 4 * 1024 * 1024) {
            throw new IllegalArgumentException("Battle input is empty or too large");
        }
        File runtime = installRuntime(context);
        File inputDir = new File(context.getFilesDir(), INPUT_DIR);
        if (!inputDir.isDirectory() && !inputDir.mkdirs()) {
            throw new IOException("Cannot create battle input directory");
        }
        File input = File.createTempFile("request-", ".lua", inputDir);
        try {
            writeAtomically(input, inputLua);
            return nativeRunBattle(runtime.getCanonicalPath(), input.getCanonicalPath(), mode);
        } finally {
            // The native call is synchronous; never leave gameplay request data behind.
            //noinspection ResultOfMethodCallIgnored
            input.delete();
        }
    }

    private static native String nativeRunBattle(String runtimeRoot, String inputPath, String mode);

    private static void copyTree(AssetManager assets, String assetPath, File destination) throws IOException {
        String[] children = assets.list(assetPath);
        if (children == null || children.length == 0) {
            copyAsset(assets, assetPath, destination);
            return;
        }
        if (!destination.isDirectory() && !destination.mkdirs()) {
            throw new IOException("Cannot create asset directory: " + destination);
        }
        for (String child : children) {
            copyTree(assets, assetPath + "/" + child, new File(destination, child));
        }
    }

    private static void copyAsset(AssetManager assets, String assetPath, File destination) throws IOException {
        File parent = destination.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IOException("Cannot create asset parent: " + parent);
        }
        File temporary = new File(destination.getPath() + ".tmp");
        try (InputStream in = assets.open(assetPath, AssetManager.ACCESS_STREAMING);
             FileOutputStream out = new FileOutputStream(temporary)) {
            byte[] buffer = new byte[32 * 1024];
            int count;
            while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
            out.getFD().sync();
        }
        if (!temporary.renameTo(destination)) {
            throw new IOException("Cannot atomically install asset: " + destination);
        }
    }

    private static void writeAtomically(File destination, String content) throws IOException {
        File parent = destination.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IOException("Cannot create parent: " + parent);
        }
        File temporary = new File(destination.getPath() + ".tmp");
        try (FileOutputStream out = new FileOutputStream(temporary)) {
            out.write(content.getBytes(StandardCharsets.UTF_8));
            out.getFD().sync();
        }
        if (!temporary.renameTo(destination)) {
            Files.move(temporary.toPath(), destination.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static void deleteTree(File file) {
        if (!file.exists()) return;
        File[] children = file.listFiles();
        if (children != null) for (File child : children) deleteTree(child);
        //noinspection ResultOfMethodCallIgnored
        file.delete();
    }
}
