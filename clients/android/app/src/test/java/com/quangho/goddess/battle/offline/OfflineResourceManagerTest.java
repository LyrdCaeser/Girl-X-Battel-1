package com.quangho.goddess.battle.offline;

import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public final class OfflineResourceManagerTest {
    private static final String PACK_HASH = repeat('b', 64);
    private static final String FILE_HASH = repeat('a', 64);

    private static Set<String> hosts(String... values) {
        Set<String> result = new HashSet<>();
        Collections.addAll(result, values);
        return result;
    }

    private static String manifest(String path, String url) {
        return "{\"manifest_version\":1,\"resource_version\":\"test.1\",\"packs\":[{" +
                "\"id\":\"core-01\",\"url\":\"" + url + "\",\"size_bytes\":42," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"" + path + "\",\"size_bytes\":7,\"sha256\":\"" + FILE_HASH + "\"}]}]}";
    }

    @Test public void parsesValidManifestAndIndexesFile() throws Exception {
        OfflineResourceManager.Manifest parsed = OfflineResourceManager.parseManifest(
                manifest("web/index.html", "https://cdn.example.com/packs/core.zip"),
                hosts("cdn.example.com"));
        assertEquals("test.1", parsed.resourceVersion);
        assertEquals(1, parsed.packs.size());
        assertEquals(1, parsed.filesByPath.size());
        assertEquals(7L, parsed.totalFileBytes);
        assertEquals(FILE_HASH, parsed.filesByPath.get("web/index.html").sha256);
    }

    @Test public void rejectsTraversalAndNonCanonicalPaths() throws Exception {
        for (String path : new String[] {"../secret", "web/../../secret", "/rooted", "web\\\\file", "web//file", "web/./file"}) {
            try {
                OfflineResourceManager.normalizeRelativePath(path);
                fail("Expected unsafe path rejection for: " + path);
            } catch (IOException expected) {
                assertTrue(expected.getMessage().length() > 0);
            }
        }
    }

    @Test public void acceptsCanonicalNestedPath() throws Exception {
        assertEquals("web/assets/ui/logo.png", OfflineResourceManager.normalizeRelativePath("web/assets/ui/logo.png"));
    }

    @Test public void rejectsUntrustedOrInsecurePackUrl() throws Exception {
        for (String url : new String[] {
                "http://cdn.example.com/packs/core.zip",
                "https://evil.example.org/packs/core.zip",
                "https://user@cdn.example.com/packs/core.zip",
                "https://cdn.example.com/packs/core.zip#fragment"
        }) {
            try {
                OfflineResourceManager.parseManifest(manifest("web/index.html", url), hosts("cdn.example.com"));
                fail("Expected URL rejection for: " + url);
            } catch (IOException expected) {
                assertTrue(expected.getMessage().length() > 0);
            }
        }
    }

    @Test public void rejectsDuplicateResourcePathAndPackId() throws Exception {
        String duplicatePath = "{\"manifest_version\":1,\"resource_version\":\"test.1\",\"packs\":[{" +
                "\"id\":\"one\",\"url\":\"https://cdn.example.com/one.zip\",\"size_bytes\":1," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"same.bin\",\"size_bytes\":1,\"sha256\":\"" + FILE_HASH + "\"}]},{" +
                "\"id\":\"two\",\"url\":\"https://cdn.example.com/two.zip\",\"size_bytes\":1," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"same.bin\",\"size_bytes\":1,\"sha256\":\"" + FILE_HASH + "\"}]}]}";
        assertInvalid(duplicatePath);

        String duplicatePack = "{\"manifest_version\":1,\"resource_version\":\"test.1\",\"packs\":[{" +
                "\"id\":\"same\",\"url\":\"https://cdn.example.com/one.zip\",\"size_bytes\":1," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"one.bin\",\"size_bytes\":1,\"sha256\":\"" + FILE_HASH + "\"}]},{" +
                "\"id\":\"same\",\"url\":\"https://cdn.example.com/two.zip\",\"size_bytes\":1," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"two.bin\",\"size_bytes\":1,\"sha256\":\"" + FILE_HASH + "\"}]}]}";
        assertInvalid(duplicatePack);
    }

    @Test public void extractsVerifiedFilesIntoContentAddressedStore() throws Exception {
        File appFiles = Files.createTempDirectory("gxb3-resource-test").toFile();
        byte[] content = "offline-resource".getBytes(StandardCharsets.UTF_8);
        String fileHash = sha256(content);
        OfflineResourceManager.Manifest manifest = OfflineResourceManager.parseManifest(
                singleFileManifest("core-01", "web/index.html", content.length, fileHash),
                hosts("cdn.example.com"));
        File archive = new File(appFiles, "pack.zip");
        writeZip(archive, "web/index.html", content);
        try (OfflineResourceManager manager = new OfflineResourceManager(appFiles, hosts("cdn.example.com"))) {
            long storedBytes = manager.extractPack(archive, manifest.packs.get(0));
            assertEquals(content.length, storedBytes);
            File object = manager.objectFile(manifest.filesByPath.get("web/index.html"));
            assertTrue(manager.dataDirectory().isDirectory());
            assertTrue(manager.obbDirectory().isDirectory());
            assertTrue(object.toPath().startsWith(manager.dataDirectory().toPath()));
            assertTrue(object.isFile());
            assertArrayEquals(content, Files.readAllBytes(object.toPath()));
        }
    }

    @Test public void storesLargeMediaInObbDirectory() throws Exception {
        File appFiles = Files.createTempDirectory("gxb3-resource-media").toFile();
        byte[] content = "media-resource".getBytes(StandardCharsets.UTF_8);
        String hash = sha256(content);
        OfflineResourceManager.Manifest manifest = OfflineResourceManager.parseManifest(
                singleFileManifest("media-01", "web/assets/cover.webp", content.length, hash),
                hosts("cdn.example.com"));
        File archive = new File(appFiles, "media.zip");
        writeZip(archive, "web/assets/cover.webp", content);
        try (OfflineResourceManager manager = new OfflineResourceManager(appFiles, hosts("cdn.example.com"))) {
            manager.extractPack(archive, manifest.packs.get(0));
            File object = manager.objectFile(manifest.filesByPath.get("web/assets/cover.webp"));
            assertTrue(object.toPath().startsWith(manager.obbDirectory().toPath()));
            assertArrayEquals(content, Files.readAllBytes(object.toPath()));
        }
    }

    @Test public void rejectsZipSlipEntryWithoutWritingOutsideObjectStore() throws Exception {
        File appFiles = Files.createTempDirectory("gxb3-resource-zip-slip").toFile();
        byte[] expected = "safe".getBytes(StandardCharsets.UTF_8);
        OfflineResourceManager.Manifest manifest = OfflineResourceManager.parseManifest(
                singleFileManifest("core-02", "safe.txt", expected.length, sha256(expected)),
                hosts("cdn.example.com"));
        File archive = new File(appFiles, "malicious.zip");
        writeZip(archive, "../escaped.txt", "attack".getBytes(StandardCharsets.UTF_8));
        try (OfflineResourceManager manager = new OfflineResourceManager(appFiles, hosts("cdn.example.com"))) {
            try {
                manager.extractPack(archive, manifest.packs.get(0));
                fail("Expected malicious ZIP entry to be rejected");
            } catch (IOException expectedFailure) {
                assertFalse(new File(appFiles, "escaped.txt").exists());
            }
        }
    }

    @Test public void progressPercentIsBounded() {
        OfflineResourceManager.Progress progress = new OfflineResourceManager.Progress(
                OfflineResourceManager.Phase.DOWNLOADING_PACK, "core-01", 1, 2, 5, 10, 0);
        assertEquals(50, progress.percent());
        OfflineResourceManager.Progress complete = new OfflineResourceManager.Progress(
                OfflineResourceManager.Phase.COMPLETE, null, 1, 1, 0, 0, 1);
        assertEquals(100, complete.percent());
        assertFalse(progress.percent() > 100);
    }

    private static String singleFileManifest(String packId, String path, long size, String hash) {
        return "{\"manifest_version\":1,\"resource_version\":\"test.1\",\"packs\":[{" +
                "\"id\":\"" + packId + "\",\"url\":\"https://cdn.example.com/p.zip\",\"size_bytes\":42," +
                "\"sha256\":\"" + PACK_HASH + "\",\"files\":[{" +
                "\"path\":\"" + path + "\",\"size_bytes\":" + size + ",\"sha256\":\"" + hash + "\"}]}]}";
    }

    private static void writeZip(File file, String path, byte[] bytes) throws IOException {
        try (ZipOutputStream zip = new ZipOutputStream(Files.newOutputStream(file.toPath()))) {
            zip.putNextEntry(new ZipEntry(path));
            zip.write(bytes);
            zip.closeEntry();
        }
    }

    private static String sha256(byte[] bytes) throws Exception {
        byte[] hash = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder result = new StringBuilder(hash.length * 2);
        for (byte value : hash) result.append(String.format(java.util.Locale.ROOT, "%02x", value & 0xff));
        return result.toString();
    }

    private static void assertInvalid(String json) throws Exception {
        try {
            OfflineResourceManager.parseManifest(json, hosts("cdn.example.com"));
            fail("Expected invalid manifest rejection");
        } catch (IOException expected) {
            assertTrue(expected.getMessage().length() > 0);
        }
    }

    private static String repeat(char character, int count) {
        StringBuilder result = new StringBuilder(count);
        for (int i = 0; i < count; i++) result.append(character);
        return result.toString();
    }
}
