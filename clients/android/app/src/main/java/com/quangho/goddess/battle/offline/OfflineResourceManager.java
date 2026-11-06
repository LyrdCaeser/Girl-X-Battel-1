package com.quangho.goddess.battle.offline;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.bouncycastle.crypto.params.Ed25519PublicKeyParameters;
import org.bouncycastle.crypto.signers.Ed25519Signer;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InterruptedIOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Persistent resource-pack installer for Android.
 *
 * <p>Construct this with {@code context.getExternalFilesDir(null)} and an explicit allowlist of
 * HTTPS distribution hosts. If Android returns {@code null}, the caller may pass
 * {@code context.getFilesDir()} as a private internal-storage fallback. Run
 * {@link #installFromUrl(String, Listener)} off the UI thread, or use
 * {@link #startInstall(String, Listener)}. Under the supplied app-specific directory this manager
 * creates sibling {@code data/} and {@code obb/} directories: code/config/small files and release
 * metadata go in {@code data/}; large/media objects and resumable pack downloads go in
 * {@code obb/}. This is an app-private directory layout, not the legacy Google Play Expansion
 * OBB format. No broad external-storage permission is required.</p>
 *
 * <p>Manifest v1 contract:
 * <pre>
 * {
 *   "manifest_version": 1,
 *   "resource_version": "2026.11.05.1",
 *   "packs": [{
 *     "id": "core-01",
 *     "url": "https://cdn.example.com/packs/core-01.zip",
 *     "size_bytes": 1234,
 *     "sha256": "64 lowercase hex chars",
 *     "files": [{"path":"web/index.html","size_bytes":123,"sha256":"..."}]
 *   }]
 * }
 * </pre>
 * Each ZIP entry must exactly match one manifest file path. ZIP paths are never used as output
 * paths; only validated manifest entries are written to the content-addressed store.</p>
 *
 * <p>Remote installation requires a pinned Ed25519 public key. The HTTPS manifest is an envelope
 * containing Base64 canonical JSON bytes and their Ed25519 signature; pack and file hashes then
 * provide content integrity. Never ship the signing private key in the app.</p>
 */
public final class OfflineResourceManager implements AutoCloseable {
    private static final int MANIFEST_VERSION = 1;
    private static final int MAX_MANIFEST_BYTES = 8 * 1024 * 1024;
    private static final int MAX_PACKS = 512;
    private static final int MAX_FILES = 100_000;
    private static final long MAX_PACK_BYTES = 256L * 1024L * 1024L;
    private static final long MAX_FILE_BYTES = 512L * 1024L * 1024L;
    private static final long MAX_TOTAL_FILE_BYTES = 8L * 1024L * 1024L * 1024L;
    private static final long STORAGE_RESERVE_BYTES = 32L * 1024L * 1024L;
    private static final int CONNECT_TIMEOUT_MS = 15_000;
    private static final int READ_TIMEOUT_MS = 45_000;
    private static final int BUFFER_SIZE = 64 * 1024;
    private static final int MAX_REDIRECTS = 5;
    private static final String HEX_SHA256 = "^[0-9a-f]{64}$";

    private final File root;
    private final File dataRoot;
    private final File obbRoot;
    private final File dataObjectRoot;
    private final File obbObjectRoot;
    private final File stagingRoot;
    private final File manifestRoot;
    private final File activeVersionFile;
    private final File lockFile;
    private final Set<String> trustedHosts;
    private final byte[] manifestSigningKey;
    private final ExecutorService executor;
    private final AtomicBoolean running = new AtomicBoolean(false);
    private final AtomicBoolean cancelled = new AtomicBoolean(false);
    private volatile HttpURLConnection activeConnection;
    private volatile Future<?> activeFuture;
    private volatile String cachedActiveVersion;
    private volatile Manifest cachedActiveManifest;

    public OfflineResourceManager(File appFilesDirectory, Set<String> trustedHosts) throws IOException {
        this(appFilesDirectory, trustedHosts, null);
    }

    /** The public key is raw 32-byte Ed25519 key encoded as standard Base64; null disables remote installs. */
    public OfflineResourceManager(File appFilesDirectory, Set<String> trustedHosts, String pinnedPublicKeyBase64) throws IOException {
        if (appFilesDirectory == null) throw new IllegalArgumentException("appFilesDirectory is required");
        if (trustedHosts == null || trustedHosts.isEmpty()) {
            throw new IllegalArgumentException("At least one trusted HTTPS host is required");
        }
        // Pass Activity.getExternalFilesDir(null) to obtain:
        // Android/data/<applicationId>/files/{data,obb}. These directories are app-scoped.
        this.root = appFilesDirectory.getCanonicalFile();
        this.dataRoot = new File(root, "data").getCanonicalFile();
        this.obbRoot = new File(root, "obb").getCanonicalFile();
        this.dataObjectRoot = new File(dataRoot, "objects");
        this.obbObjectRoot = new File(obbRoot, "objects");
        this.stagingRoot = new File(obbRoot, "staging");
        this.manifestRoot = new File(dataRoot, "manifests");
        this.activeVersionFile = new File(dataRoot, "active-version");
        this.lockFile = new File(dataRoot, "install.lock");
        HashSet<String> hosts = new HashSet<>();
        for (String host : trustedHosts) {
            if (host != null && !host.trim().isEmpty()) hosts.add(host.trim().toLowerCase(Locale.ROOT));
        }
        if (hosts.isEmpty()) throw new IllegalArgumentException("Trusted host list is empty");
        this.trustedHosts = Collections.unmodifiableSet(hosts);
        this.manifestSigningKey = decodePublicKey(pinnedPublicKeyBase64);
        ensureDirectory(root);
        ensureDirectory(dataRoot);
        ensureDirectory(obbRoot);
        ensureDirectory(dataObjectRoot);
        ensureDirectory(obbObjectRoot);
        ensureDirectory(stagingRoot);
        ensureDirectory(manifestRoot);
        this.executor = Executors.newSingleThreadExecutor(r -> {
            Thread thread = new Thread(r, "gxb3-resource-download");
            thread.setDaemon(true);
            return thread;
        });
    }

    /** Progress callbacks run on the download worker thread; marshal to the UI thread as needed. */
    public interface Listener {
        void onProgress(Progress progress);
        void onComplete(InstallResult result);
        void onError(Throwable error);
    }

    public enum Phase { FETCHING_MANIFEST, DOWNLOADING_PACK, VERIFYING_PACK, INSTALLING_FILES, ACTIVATING, COMPLETE }

    public static final class Progress {
        public final Phase phase;
        public final String packId;
        public final int packIndex;
        public final int packCount;
        public final long completedBytes;
        public final long totalBytes;
        public final long completedPacks;

        Progress(Phase phase, String packId, int packIndex, int packCount,
                         long completedBytes, long totalBytes, long completedPacks) {
            this.phase = phase;
            this.packId = packId;
            this.packIndex = packIndex;
            this.packCount = packCount;
            this.completedBytes = completedBytes;
            this.totalBytes = totalBytes;
            this.completedPacks = completedPacks;
        }

        public int percent() {
            if (totalBytes <= 0) return phase == Phase.COMPLETE ? 100 : 0;
            return (int) Math.min(100L, (completedBytes * 100L) / totalBytes);
        }
    }

    public static final class InstallResult {
        public final String resourceVersion;
        public final int fileCount;
        public final int packCount;
        public final long uniqueInstalledBytes;

        private InstallResult(String resourceVersion, int fileCount, int packCount, long uniqueInstalledBytes) {
            this.resourceVersion = resourceVersion;
            this.fileCount = fileCount;
            this.packCount = packCount;
            this.uniqueInstalledBytes = uniqueInstalledBytes;
        }
    }

    public static final class ResourceFile {
        public final String path;
        public final long sizeBytes;
        public final String sha256;

        private ResourceFile(String path, long sizeBytes, String sha256) {
            this.path = path;
            this.sizeBytes = sizeBytes;
            this.sha256 = sha256;
        }
    }

    public static final class Pack {
        public final String id;
        public final String url;
        public final long sizeBytes;
        public final String sha256;
        public final List<ResourceFile> files;

        private Pack(String id, String url, long sizeBytes, String sha256, List<ResourceFile> files) {
            this.id = id;
            this.url = url;
            this.sizeBytes = sizeBytes;
            this.sha256 = sha256;
            this.files = Collections.unmodifiableList(new ArrayList<>(files));
        }
    }

    public static final class Manifest {
        public final int manifestVersion;
        public final String resourceVersion;
        public final List<Pack> packs;
        public final Map<String, ResourceFile> filesByPath;
        public final long totalFileBytes;
        private final String rawJson;
        private final String persistedJson;

        private Manifest(int manifestVersion, String resourceVersion, List<Pack> packs,
                         Map<String, ResourceFile> filesByPath, long totalFileBytes, String rawJson,
                         String persistedJson) {
            this.manifestVersion = manifestVersion;
            this.resourceVersion = resourceVersion;
            this.packs = Collections.unmodifiableList(new ArrayList<>(packs));
            this.filesByPath = Collections.unmodifiableMap(new LinkedHashMap<>(filesByPath));
            this.totalFileBytes = totalFileBytes;
            this.rawJson = rawJson;
            this.persistedJson = persistedJson;
        }
    }

    /** Parse and validate manifest v1 before accepting any download URL or output path. */
    public static Manifest parseManifest(String json, Set<String> trustedHosts) throws IOException {
        if (json == null || json.getBytes(StandardCharsets.UTF_8).length > MAX_MANIFEST_BYTES) {
            throw new IOException("Manifest is missing or exceeds the size limit");
        }
        if (trustedHosts == null || trustedHosts.isEmpty()) throw new IOException("Trusted hosts are required");
        Set<String> allowed = new HashSet<>();
        for (String host : trustedHosts) if (host != null) allowed.add(host.toLowerCase(Locale.ROOT));
        try {
            JSONObject root = new JSONObject(json);
            int version = root.getInt("manifest_version");
            if (version != MANIFEST_VERSION) throw new IOException("Unsupported manifest_version: " + version);
            String resourceVersion = root.getString("resource_version");
            if (!resourceVersion.matches("[A-Za-z0-9._-]{1,80}")) throw new IOException("Invalid resource_version");
            JSONArray packArray = root.getJSONArray("packs");
            if (packArray.length() < 1 || packArray.length() > MAX_PACKS) throw new IOException("Invalid pack count");

            List<Pack> packs = new ArrayList<>();
            Map<String, ResourceFile> files = new LinkedHashMap<>();
            Set<String> packIds = new HashSet<>();
            Map<String, Long> sizeByHash = new HashMap<>();
            long totalFileBytes = 0L;
            for (int i = 0; i < packArray.length(); i++) {
                JSONObject p = packArray.getJSONObject(i);
                String id = p.getString("id");
                if (!id.matches("[A-Za-z0-9._-]{1,80}") || !packIds.add(id)) {
                    throw new IOException("Invalid or duplicate pack id: " + id);
                }
                String url = p.getString("url");
                validateHttpsUrl(url, allowed);
                long packSize = p.getLong("size_bytes");
                if (packSize < 1 || packSize > MAX_PACK_BYTES) throw new IOException("Invalid pack size: " + id);
                String packHash = requireHash(p.getString("sha256"), "pack " + id);
                JSONArray fileArray = p.getJSONArray("files");
                if (fileArray.length() < 1 || files.size() + fileArray.length() > MAX_FILES) {
                    throw new IOException("Invalid file count in pack " + id);
                }
                List<ResourceFile> packFiles = new ArrayList<>();
                for (int j = 0; j < fileArray.length(); j++) {
                    JSONObject f = fileArray.getJSONObject(j);
                    String path = normalizeRelativePath(f.getString("path"));
                    long size = f.getLong("size_bytes");
                    if (size < 0 || size > MAX_FILE_BYTES) throw new IOException("Invalid file size: " + path);
                    String hash = requireHash(f.getString("sha256"), "file " + path);
                    ResourceFile entry = new ResourceFile(path, size, hash);
                    if (files.put(path, entry) != null) throw new IOException("Duplicate resource path: " + path);
                    Long priorSize = sizeByHash.put(hash, size);
                    if (priorSize != null && priorSize.longValue() != size) {
                        throw new IOException("Same content hash has inconsistent sizes");
                    }
                    totalFileBytes = safeAdd(totalFileBytes, size, MAX_TOTAL_FILE_BYTES, "Total resource size exceeds limit");
                    packFiles.add(entry);
                }
                packs.add(new Pack(id, url, packSize, packHash, packFiles));
            }
            return new Manifest(version, resourceVersion, packs, files, totalFileBytes, json, json);
        } catch (JSONException | ArithmeticException e) {
            throw new IOException("Invalid resource manifest", e);
        }
    }

    /** Verify the Ed25519 signature over the exact UTF-8 payload bytes before parsing its URLs or paths. */
    public static Manifest parseSignedManifest(String envelopeJson, Set<String> trustedHosts,
                                               String pinnedPublicKeyBase64) throws IOException {
        byte[] publicKey = decodePublicKey(pinnedPublicKeyBase64);
        return parseSignedManifest(envelopeJson, trustedHosts, publicKey);
    }

    private static Manifest parseSignedManifest(String envelopeJson, Set<String> trustedHosts,
                                                byte[] publicKey) throws IOException {
        if (publicKey == null) throw new IOException("No pinned Ed25519 manifest public key is configured");
        if (envelopeJson == null || envelopeJson.getBytes(StandardCharsets.UTF_8).length > MAX_MANIFEST_BYTES) {
            throw new IOException("Signed manifest is missing or exceeds the size limit");
        }
        try {
            JSONObject envelope = new JSONObject(envelopeJson);
            if (envelope.length() != 2) throw new IOException("Unexpected fields in signed manifest envelope");
            byte[] payload = Base64.getDecoder().decode(envelope.getString("payload_b64"));
            byte[] signature = Base64.getDecoder().decode(envelope.getString("signature_b64"));
            if (payload.length == 0 || payload.length > MAX_MANIFEST_BYTES || signature.length != 64) {
                throw new IOException("Invalid signed manifest payload or signature size");
            }
            Ed25519Signer verifier = new Ed25519Signer();
            verifier.init(false, new Ed25519PublicKeyParameters(publicKey, 0));
            verifier.update(payload, 0, payload.length);
            if (!verifier.verifySignature(signature)) throw new IOException("Manifest Ed25519 signature verification failed");
            Manifest parsed = parseManifest(new String(payload, StandardCharsets.UTF_8), trustedHosts);
            return new Manifest(parsed.manifestVersion, parsed.resourceVersion, parsed.packs,
                    parsed.filesByPath, parsed.totalFileBytes, parsed.rawJson, envelopeJson);
        } catch (JSONException | IllegalArgumentException e) {
            throw new IOException("Invalid signed manifest envelope", e);
        }
    }

    private static byte[] decodePublicKey(String encoded) throws IOException {
        if (encoded == null || encoded.trim().isEmpty()) return null;
        try {
            byte[] decoded = Base64.getDecoder().decode(encoded.trim());
            if (decoded.length != Ed25519PublicKeyParameters.KEY_SIZE) {
                throw new IOException("Pinned Ed25519 public key must contain exactly 32 bytes");
            }
            return decoded;
        } catch (IllegalArgumentException e) {
            throw new IOException("Pinned Ed25519 public key is not valid Base64", e);
        }
    }

    /** Synchronous install. Call from a worker thread, never from an Android UI callback. */
    public InstallResult installFromUrl(String manifestUrl, Listener listener) throws IOException {
        cancelled.set(false);
        return performInstall(manifestUrl, listener);
    }

    private InstallResult performInstall(String manifestUrl, Listener listener) throws IOException {
        if (!running.compareAndSet(false, true)) throw new IOException("A resource installation is already running");
        try (FileOutputStream lockStream = new FileOutputStream(lockFile, true);
             FileChannel channel = lockStream.getChannel();
             FileLock ignored = acquireLock(channel)) {
            ensureNotCancelled();
            notifyProgress(listener, new Progress(Phase.FETCHING_MANIFEST, null, 0, 0, 0, 0, 0));
            String envelope = fetchManifest(manifestUrl);
            Manifest manifest = parseSignedManifest(envelope, trustedHosts, manifestSigningKey);
            return installManifest(manifest, listener);
        } catch (OverlappingFileLockException e) {
            throw new IOException("Another resource installation is active", e);
        } finally {
            HttpURLConnection connection = activeConnection;
            activeConnection = null;
            if (connection != null) connection.disconnect();
            running.set(false);
        }
    }

    /** Start a single background installation. Listener callbacks are not posted to the main thread. */
    public synchronized Future<?> startInstall(String manifestUrl, Listener listener) {
        if (activeFuture != null && !activeFuture.isDone()) throw new IllegalStateException("A resource installation is already running");
        cancelled.set(false);
        activeFuture = executor.submit(() -> {
            try {
                InstallResult result = performInstall(manifestUrl, listener);
                if (listener != null) listener.onComplete(result);
            } catch (Throwable error) {
                if (listener != null) listener.onError(error);
            }
        });
        return activeFuture;
    }

    /** Cancels the active transfer; a partial pack is retained so a later start can resume it. */
    public void cancel() {
        cancelled.set(true);
        HttpURLConnection connection = activeConnection;
        if (connection != null) connection.disconnect();
    }

    public boolean isRunning() { return running.get(); }

    /** Returns the currently active release version, or null if no release has been activated. */
    public synchronized String activeVersion() throws IOException {
        if (!activeVersionFile.isFile()) return null;
        String version = new String(Files.readAllBytes(activeVersionFile.toPath()), StandardCharsets.UTF_8).trim();
        if (!version.matches("[A-Za-z0-9._-]{1,80}")) throw new IOException("Corrupt active resource version pointer");
        return version;
    }

    /** Loads the active local manifest. The caller can use it to build a WebView asset resolver. */
    public synchronized Manifest activeManifest() throws IOException {
        String version = activeVersion();
        if (version == null) return null;
        if (version.equals(cachedActiveVersion) && cachedActiveManifest != null) return cachedActiveManifest;
        File manifestFile = manifestFile(version);
        if (!manifestFile.isFile()) throw new IOException("Active resource manifest is missing");
        String json = new String(Files.readAllBytes(manifestFile.toPath()), StandardCharsets.UTF_8);
        Manifest parsed = parseSignedManifest(json, trustedHosts, manifestSigningKey);
        cachedActiveVersion = version;
        cachedActiveManifest = parsed;
        return parsed;
    }

    /** Resolve a manifest path to its content-addressed file; no network fallback is performed. */
    public synchronized File resolveResourceFile(String relativePath) throws IOException {
        Manifest manifest = activeManifest();
        if (manifest == null) throw new IOException("No offline resource version is installed");
        String path = normalizeRelativePath(relativePath);
        ResourceFile resource = manifest.filesByPath.get(path);
        if (resource == null) throw new IOException("Resource is not in the active manifest: " + path);
        File file = objectFile(resource);
        if (!file.isFile() || file.length() != resource.sizeBytes) throw new IOException("Installed resource is missing or truncated: " + path);
        return file;
    }

    public InputStream openResource(String relativePath) throws IOException {
        return new BufferedInputStream(new FileInputStream(resolveResourceFile(relativePath)));
    }

    /** Check file presence/size for a release. Use deep verification in diagnostics, not every app launch. */
    public boolean isVersionInstalled(String resourceVersion) throws IOException {
        if (resourceVersion == null || !resourceVersion.matches("[A-Za-z0-9._-]{1,80}")) return false;
        File file = manifestFile(resourceVersion);
        if (!file.isFile()) return false;
        Manifest manifest = parseSignedManifest(new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8), trustedHosts, manifestSigningKey);
        if (!resourceVersion.equals(manifest.resourceVersion)) return false;
        for (ResourceFile resource : manifest.filesByPath.values()) {
            File object = objectFile(resource);
            if (!object.isFile() || object.length() != resource.sizeBytes) return false;
        }
        return true;
    }

    /** Re-hash every object referenced by a release; intended for QA/repair flows. */
    public boolean verifyVersion(String resourceVersion) throws IOException {
        if (resourceVersion == null || !resourceVersion.matches("[A-Za-z0-9._-]{1,80}")) return false;
        File file = manifestFile(resourceVersion);
        if (!file.isFile()) return false;
        Manifest manifest = parseSignedManifest(new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8), trustedHosts, manifestSigningKey);
        for (ResourceFile resource : manifest.filesByPath.values()) {
            File object = objectFile(resource);
            if (!object.isFile() || object.length() != resource.sizeBytes || !resource.sha256.equals(sha256File(object))) return false;
        }
        return true;
    }

    /** Atomically roll back to an already installed, fully verified release. */
    public synchronized void activateInstalledVersion(String resourceVersion) throws IOException {
        if (!isVersionInstalled(resourceVersion)) throw new IOException("Requested resource release is not installed");
        writeAtomically(activeVersionFile, (resourceVersion + "\n").getBytes(StandardCharsets.UTF_8));
        cachedActiveVersion = null;
        cachedActiveManifest = null;
    }

    private InstallResult installManifest(Manifest manifest, Listener listener) throws IOException {
        File versionStage = new File(stagingRoot, manifest.resourceVersion);
        ensureDirectory(versionStage);
        long missingFileBytes = 0L;
        long totalDownloadBytes = 0L;
        List<Pack> packsToDownload = new ArrayList<>();
        Set<String> countedHashes = new HashSet<>();
        for (Pack pack : manifest.packs) {
            boolean allAvailable = true;
            for (ResourceFile resource : pack.files) {
                File object = objectFile(resource);
                boolean valid = object.isFile() && object.length() == resource.sizeBytes
                        && resource.sha256.equals(sha256File(object));
                if (!valid) {
                    allAvailable = false;
                    if (countedHashes.add(resource.sha256)) missingFileBytes = safeAdd(missingFileBytes, resource.sizeBytes,
                            MAX_TOTAL_FILE_BYTES, "Required storage exceeds limit");
                }
            }
            if (!allAvailable) {
                packsToDownload.add(pack);
                totalDownloadBytes = safeAdd(totalDownloadBytes, pack.sizeBytes, Long.MAX_VALUE, "Download size overflow");
            }
        }
        long maxActivePack = 0L;
        for (Pack pack : packsToDownload) maxActivePack = Math.max(maxActivePack, pack.sizeBytes);
        long requiredSpace = packsToDownload.isEmpty() ? 0L
                : safeAdd(safeAdd(missingFileBytes, maxActivePack, Long.MAX_VALUE, "Required storage overflow"),
                STORAGE_RESERVE_BYTES, Long.MAX_VALUE, "Required storage overflow");
        if (root.getUsableSpace() < requiredSpace) {
            throw new IOException("Not enough app storage. Required approximately " + requiredSpace
                    + " bytes, available " + root.getUsableSpace() + " bytes");
        }

        long completedBytes = 0L;
        long completedPacks = 0L;
        long newlyStoredBytes = 0L;
        int index = 0;
        for (Pack pack : manifest.packs) {
            ensureNotCancelled();
            index++;
            if (!packsToDownload.contains(pack)) {
                completedPacks++;
                notifyProgress(listener, new Progress(Phase.VERIFYING_PACK, pack.id, index, manifest.packs.size(),
                        completedBytes, totalDownloadBytes, completedPacks));
                continue;
            }
            File archive = new File(versionStage, pack.id + ".zip.part");
            downloadPack(pack, archive, listener, index, manifest.packs.size(), completedBytes, totalDownloadBytes);
            ensureNotCancelled();
            notifyProgress(listener, new Progress(Phase.VERIFYING_PACK, pack.id, index, manifest.packs.size(),
                    completedBytes + pack.sizeBytes, totalDownloadBytes, completedPacks));
            if (archive.length() != pack.sizeBytes || !pack.sha256.equals(sha256File(archive))) {
                archive.delete();
                throw new IOException("Resource pack checksum/size mismatch: " + pack.id);
            }
            notifyProgress(listener, new Progress(Phase.INSTALLING_FILES, pack.id, index, manifest.packs.size(),
                    completedBytes + pack.sizeBytes, totalDownloadBytes, completedPacks));
            newlyStoredBytes += extractPack(archive, pack);
            if (!archive.delete() && archive.exists()) archive.deleteOnExit();
            completedBytes += pack.sizeBytes;
            completedPacks++;
            notifyProgress(listener, new Progress(Phase.DOWNLOADING_PACK, pack.id, index, manifest.packs.size(),
                    Math.min(completedBytes, totalDownloadBytes), totalDownloadBytes, completedPacks));
        }
        ensureNotCancelled();
        notifyProgress(listener, new Progress(Phase.ACTIVATING, null, manifest.packs.size(), manifest.packs.size(),
                totalDownloadBytes, totalDownloadBytes, completedPacks));
        File savedManifest = manifestFile(manifest.resourceVersion);
        writeAtomically(savedManifest, manifest.persistedJson.getBytes(StandardCharsets.UTF_8));
        writeAtomically(activeVersionFile, (manifest.resourceVersion + "\n").getBytes(StandardCharsets.UTF_8));
        cachedActiveVersion = manifest.resourceVersion;
        cachedActiveManifest = manifest;
        notifyProgress(listener, new Progress(Phase.COMPLETE, null, manifest.packs.size(), manifest.packs.size(),
                totalDownloadBytes, totalDownloadBytes, completedPacks));
        return new InstallResult(manifest.resourceVersion, manifest.filesByPath.size(), manifest.packs.size(), newlyStoredBytes);
    }

    long extractPack(File archive, Pack pack) throws IOException {
        Map<String, ResourceFile> expected = new HashMap<>();
        for (ResourceFile file : pack.files) expected.put(file.path, file);
        Set<String> seen = new HashSet<>();
        long expandedBytes = 0L;
        long newlyStoredBytes = 0L;
        try (ZipInputStream zip = new ZipInputStream(new BufferedInputStream(new FileInputStream(archive)), StandardCharsets.UTF_8)) {
            ZipEntry entry;
            byte[] buffer = new byte[BUFFER_SIZE];
            while ((entry = zip.getNextEntry()) != null) {
                ensureNotCancelled();
                String name = entry.getName();
                if (entry.isDirectory()) {
                    String directoryName = name.endsWith("/") ? name.substring(0, name.length() - 1) : name;
                    if (!directoryName.isEmpty()) normalizeRelativePath(directoryName);
                    zip.closeEntry();
                    continue;
                }
                String path = normalizeRelativePath(name);
                ResourceFile expectedFile = expected.get(path);
                if (expectedFile == null) throw new IOException("Unexpected file in pack " + pack.id + ": " + path);
                if (!seen.add(path)) throw new IOException("Duplicate ZIP entry: " + path);
                File target = objectFile(expectedFile);
                ensureDirectory(target.getParentFile());
                boolean reuseExisting = target.isFile() && target.length() == expectedFile.sizeBytes
                        && expectedFile.sha256.equals(sha256File(target));
                File temp = reuseExisting ? null : File.createTempFile("resource-", ".tmp", target.getParentFile());
                try {
                    MessageDigest digest = newSha256();
                    long entryBytes = 0L;
                    try (OutputStream out = temp == null ? null : new BufferedOutputStream(new FileOutputStream(temp))) {
                        int read;
                        while ((read = zip.read(buffer)) != -1) {
                            ensureNotCancelled();
                            entryBytes = safeAdd(entryBytes, read, expectedFile.sizeBytes,
                                    "ZIP entry exceeds declared size: " + path);
                            expandedBytes = safeAdd(expandedBytes, read, MAX_TOTAL_FILE_BYTES,
                                    "ZIP expands beyond configured limit");
                            digest.update(buffer, 0, read);
                            if (out != null) out.write(buffer, 0, read);
                        }
                        if (out != null) out.flush();
                    }
                    if (entryBytes != expectedFile.sizeBytes || !expectedFile.sha256.equals(toHex(digest.digest()))) {
                        throw new IOException("Resource file checksum/size mismatch: " + path);
                    }
                    if (temp != null) {
                        try (FileOutputStream sync = new FileOutputStream(temp, true)) { sync.getFD().sync(); }
                        moveAtomically(temp, target);
                        newlyStoredBytes = safeAdd(newlyStoredBytes, entryBytes, MAX_TOTAL_FILE_BYTES,
                                "Installed byte count exceeds configured limit");
                    }
                } finally {
                    zip.closeEntry();
                    if (temp != null && temp.exists()) temp.delete();
                }
            }
        }
        if (seen.size() != expected.size()) {
            Set<String> missing = new HashSet<>(expected.keySet());
            missing.removeAll(seen);
            throw new IOException("Pack is missing manifest files: " + samplePaths(missing));
        }
        return newlyStoredBytes;
    }

    private void downloadPack(Pack pack, File part, Listener listener, int packIndex, int packCount,
                              long priorPackBytes, long totalDownloadBytes) throws IOException {
        ensureDirectory(part.getParentFile());
        long offset = part.isFile() ? part.length() : 0L;
        if (offset == pack.sizeBytes && offset > 0 && pack.sha256.equals(sha256File(part))) return;
        if (offset > pack.sizeBytes || offset == pack.sizeBytes) {
            if (!part.delete()) throw new IOException("Cannot reset oversized partial pack: " + pack.id);
            offset = 0L;
        }
        int restartCount = 0;
        while (true) {
            ensureNotCancelled();
            HttpURLConnection connection = openConnection(pack.url, offset);
            activeConnection = connection;
            try {
                int status = connection.getResponseCode();
                if (status == 416 && offset > 0 && restartCount++ < 1) {
                    connection.disconnect();
                    part.delete();
                    offset = 0L;
                    continue;
                }
                if (status != HttpURLConnection.HTTP_OK && status != HttpURLConnection.HTTP_PARTIAL) {
                    throw new IOException("Pack download failed with HTTP " + status + ": " + pack.id);
                }
                if (offset > 0 && status == HttpURLConnection.HTTP_OK) {
                    // The origin ignored Range. Its 200 body starts at byte zero, so replace the part.
                    offset = 0L;
                } else if (status == HttpURLConnection.HTTP_PARTIAL) {
                    validateContentRange(connection.getHeaderField("Content-Range"), offset, pack.sizeBytes);
                } else if (offset != 0L) {
                    throw new IOException("Unexpected range response for pack " + pack.id);
                }
                long responseLength = connection.getContentLengthLong();
                if (responseLength >= 0 && responseLength > pack.sizeBytes - offset) {
                    throw new IOException("Pack response exceeds declared size: " + pack.id);
                }
                long currentOffset = offset;
                try (InputStream in = new BufferedInputStream(connection.getInputStream());
                     FileOutputStream file = new FileOutputStream(part, currentOffset > 0)) {
                    byte[] buffer = new byte[BUFFER_SIZE];
                    int read;
                    long received = currentOffset;
                    while ((read = in.read(buffer)) != -1) {
                        ensureNotCancelled();
                        received = safeAdd(received, read, pack.sizeBytes, "Pack exceeds declared size: " + pack.id);
                        file.write(buffer, 0, read);
                        notifyProgress(listener, new Progress(Phase.DOWNLOADING_PACK, pack.id, packIndex, packCount,
                                Math.min(priorPackBytes + received, totalDownloadBytes), totalDownloadBytes, packIndex - 1L));
                    }
                    file.flush();
                    file.getFD().sync();
                }
                if (part.length() != pack.sizeBytes) throw new IOException("Incomplete pack response: " + pack.id);
                return;
            } finally {
                connection.disconnect();
                if (activeConnection == connection) activeConnection = null;
            }
        }
    }

    private String fetchManifest(String manifestUrl) throws IOException {
        HttpURLConnection connection = openConnection(manifestUrl, 0L);
        activeConnection = connection;
        try {
            int status = connection.getResponseCode();
            if (status != HttpURLConnection.HTTP_OK) throw new IOException("Manifest request failed with HTTP " + status);
            long declared = connection.getContentLengthLong();
            if (declared > MAX_MANIFEST_BYTES) throw new IOException("Manifest exceeds the size limit");
            try (InputStream in = connection.getInputStream(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[16 * 1024];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    ensureNotCancelled();
                    if (out.size() + read > MAX_MANIFEST_BYTES) throw new IOException("Manifest exceeds the size limit");
                    out.write(buffer, 0, read);
                }
                return new String(out.toByteArray(), StandardCharsets.UTF_8);
            }
        } finally {
            connection.disconnect();
            if (activeConnection == connection) activeConnection = null;
        }
    }

    private HttpURLConnection openConnection(String rawUrl, long rangeStart) throws IOException {
        String nextUrl = rawUrl;
        for (int redirect = 0; redirect <= MAX_REDIRECTS; redirect++) {
            URL url = validateHttpsUrl(nextUrl, trustedHosts);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            activeConnection = connection;
            connection.setInstanceFollowRedirects(false);
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Accept-Encoding", "identity");
            connection.setRequestProperty("User-Agent", "GXB3-OfflineResources/1");
            if (rangeStart > 0) connection.setRequestProperty("Range", "bytes=" + rangeStart + "-");
            int status;
            try {
                status = connection.getResponseCode();
            } catch (IOException e) {
                connection.disconnect();
                throw e;
            }
            if (status == 301 || status == 302 || status == 303 || status == 307 || status == 308) {
                String location = connection.getHeaderField("Location");
                connection.disconnect();
                if (activeConnection == connection) activeConnection = null;
                if (location == null || redirect == MAX_REDIRECTS) throw new IOException("Too many or invalid redirects");
                URI base;
                try { base = url.toURI(); } catch (Exception e) { throw new IOException("Invalid redirect base URL", e); }
                nextUrl = base.resolve(location).toString();
                validateHttpsUrl(nextUrl, trustedHosts);
                continue;
            }
            return connection;
        }
        throw new IOException("Too many redirects");
    }

    private static void validateContentRange(String value, long expectedStart, long expectedTotal) throws IOException {
        if (value == null || !value.matches("bytes [0-9]+-[0-9]+/[0-9]+")) throw new IOException("Invalid Content-Range response");
        String[] parts = value.substring(6).split("[-/]");
        try {
            long start = Long.parseLong(parts[0]);
            long end = Long.parseLong(parts[1]);
            long total = Long.parseLong(parts[2]);
            if (start != expectedStart || end < start || total != expectedTotal || end >= total) {
                throw new IOException("Content-Range does not match the requested pack");
            }
        } catch (NumberFormatException e) {
            throw new IOException("Invalid Content-Range response", e);
        }
    }

    private static URL validateHttpsUrl(String rawUrl, Set<String> allowedHosts) throws IOException {
        try {
            URI uri = new URI(rawUrl);
            String host = uri.getHost();
            if (!"https".equalsIgnoreCase(uri.getScheme()) || host == null || uri.getUserInfo() != null
                    || uri.getFragment() != null || !allowedHosts.contains(host.toLowerCase(Locale.ROOT))) {
                throw new IOException("URL must use HTTPS and an allowlisted host");
            }
            return uri.toURL();
        } catch (IOException e) {
            throw e;
        } catch (Exception e) {
            throw new IOException("Invalid HTTPS URL", e);
        }
    }

    static String normalizeRelativePath(String rawPath) throws IOException {
        if (rawPath == null || rawPath.isEmpty() || rawPath.startsWith("/") || rawPath.startsWith("\\")
                || rawPath.contains("\\") || rawPath.contains(":") || rawPath.indexOf('\0') >= 0) {
            throw new IOException("Invalid resource path");
        }
        String[] parts = rawPath.split("/", -1);
        for (String part : parts) {
            if (part.isEmpty() || part.equals(".") || part.equals("..")) throw new IOException("Unsafe resource path: " + rawPath);
            for (int i = 0; i < part.length(); i++) {
                if (Character.isISOControl(part.charAt(i))) throw new IOException("Control character in resource path");
            }
        }
        return rawPath;
    }

    File objectFile(ResourceFile resource) throws IOException {
        if (resource == null) throw new IOException("Missing resource metadata");
        String hash = requireHash(resource.sha256, "object");
        File storageRoot = shouldStoreInObb(resource) ? obbObjectRoot : dataObjectRoot;
        File canonicalStorageRoot = storageRoot.getCanonicalFile();
        File parent = new File(canonicalStorageRoot, hash.substring(0, 2));
        File target = new File(parent, hash + ".blob").getCanonicalFile();
        if (!target.toPath().startsWith(canonicalStorageRoot.toPath())) throw new IOException("Object path escapes storage root");
        return target;
    }

    private static boolean shouldStoreInObb(ResourceFile resource) {
        if (resource.sizeBytes >= 1024L * 1024L) return true;
        String path = resource.path.toLowerCase(Locale.ROOT);
        return path.endsWith(".png") || path.endsWith(".jpg") || path.endsWith(".jpeg")
                || path.endsWith(".webp") || path.endsWith(".gif") || path.endsWith(".mp3")
                || path.endsWith(".ogg") || path.endsWith(".wav") || path.endsWith(".m4a")
                || path.endsWith(".mp4") || path.endsWith(".webm") || path.endsWith(".atlas")
                || path.endsWith(".skel") || path.endsWith(".bytes") || path.endsWith(".bin");
    }

    /** App-specific large/media resource directory (the sibling {@code obb/}). */
    public File obbDirectory() { return obbRoot; }

    /** App-specific code, metadata and smaller resource directory (the sibling {@code data/}). */
    public File dataDirectory() { return dataRoot; }

    private File manifestFile(String version) throws IOException {
        if (version == null || !version.matches("[A-Za-z0-9._-]{1,80}")) throw new IOException("Invalid resource version");
        return new File(manifestRoot, version + ".json").getCanonicalFile();
    }

    private static FileLock acquireLock(FileChannel channel) throws IOException {
        try {
            return channel.lock();
        } catch (OverlappingFileLockException e) {
            throw e;
        }
    }

    private static void writeAtomically(File target, byte[] bytes) throws IOException {
        ensureDirectory(target.getParentFile());
        File temp = File.createTempFile(target.getName(), ".tmp", target.getParentFile());
        try {
            try (FileOutputStream output = new FileOutputStream(temp)) {
                output.write(bytes);
                output.flush();
                output.getFD().sync();
            }
            moveAtomically(temp, target);
        } finally {
            if (temp.exists()) temp.delete();
        }
    }

    private static void moveAtomically(File source, File target) throws IOException {
        try {
            Files.move(source.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } catch (AtomicMoveNotSupportedException e) {
            Files.move(source.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static void ensureDirectory(File directory) throws IOException {
        if (directory == null) throw new IOException("Missing parent directory");
        if (directory.isDirectory()) return;
        if (!directory.mkdirs() && !directory.isDirectory()) throw new IOException("Cannot create directory: " + directory);
    }

    private static String requireHash(String value, String label) throws IOException {
        if (value == null || !value.matches(HEX_SHA256)) throw new IOException("Invalid SHA-256 for " + label);
        return value;
    }

    private static long safeAdd(long a, long b, long maximum, String error) throws IOException {
        if (b < 0 || a < 0 || a > maximum - b) throw new IOException(error);
        return a + b;
    }

    private static MessageDigest newSha256() throws IOException {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException e) { throw new IOException("SHA-256 is unavailable", e); }
    }

    private static String sha256File(File file) throws IOException {
        MessageDigest digest = newSha256();
        try (InputStream input = new BufferedInputStream(new FileInputStream(file))) {
            byte[] buffer = new byte[BUFFER_SIZE];
            int read;
            while ((read = input.read(buffer)) != -1) digest.update(buffer, 0, read);
        }
        return toHex(digest.digest());
    }

    private static String toHex(byte[] bytes) {
        final char[] digits = "0123456789abcdef".toCharArray();
        char[] result = new char[bytes.length * 2];
        for (int i = 0; i < bytes.length; i++) {
            int value = bytes[i] & 0xff;
            result[i * 2] = digits[value >>> 4];
            result[i * 2 + 1] = digits[value & 0x0f];
        }
        return new String(result);
    }

    private static String samplePaths(Set<String> paths) {
        StringBuilder result = new StringBuilder();
        int count = 0;
        for (String path : paths) {
            if (count++ > 0) result.append(", ");
            result.append(path);
            if (count == 5) break;
        }
        return result.toString();
    }

    private void ensureNotCancelled() throws InterruptedIOException {
        if (cancelled.get() || Thread.currentThread().isInterrupted()) throw new InterruptedIOException("Resource download cancelled");
    }

    private static void notifyProgress(Listener listener, Progress progress) {
        if (listener == null) return;
        try { listener.onProgress(progress); } catch (RuntimeException ignored) { }
    }

    @Override public void close() {
        cancel();
        executor.shutdownNow();
    }
}
