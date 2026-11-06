# GXB 3 release clients — ALPHA RC7 hotfix

Native launcher clients for the current GXB 3 production server, with authoritative gameplay served live from https://180-93-111-99.sslip.io/.

- Android 8.0+ APK (API 26+, 64-bit and 32-bit compatible WebView wrapper); built with Android Gradle, debug-signed for RC distribution.
- Windows x64 EXE (PyWebView / Edge WebView2 wrapper); requires working WebView2 and network access.
- iOS 15.0+ unsigned IPA (WKWebView, arm64) for developers to sign with their own Apple provisioning profile; **unsigned IPAs cannot be directly installed on customer iPhones**.
- iOS Safari Web Clip (.mobileconfig) to open the production web game from the Home Screen without Apple signing. Users can also open the URL in Safari and choose Share > Add to Home Screen, no profile needed.

Windows and iOS launchers connect to the online server. The Android launcher opens a native resource screen first, with a separate **Chơi trực tuyến** entry. Android now has a signed-manifest verifier, content-addressed resource store, strict local WebView asset resolver, resumable WorkManager download job, and origin-restricted WebMessageListener transport with a local JSON API router. The router exposes `/api/offline/health`; gameplay routes deliberately return `501` until a local state/action provider and save exist. The branch also contains a LuaJIT JNI bridge for `battle_host.lua` battle/attrs calls, not yet connected to that provider. The web frontend still uses its online auth/fetch path and has not been adapted to the native RPC channel. When the online server becomes unreachable, Android automatically switches to the installed `gxb3.local` release; if no valid local release is installed, it shows a clear local-mode unavailable message and never silently retries production from the local page. No resource release is published/configured by default, so the current app is not yet full offline gameplay.

#### Android Asset Downloader (development wiring)

The default Android build intentionally leaves the download button disabled until a release manifest and trusted HTTPS hosts are configured. Supply Gradle project properties at build time; do not put CDN credentials or signing secrets in these properties:

```sh
gradle -p clients/android \
  -PgxbOfflineManifestUrl=https://cdn.example.com/offline-resources/manifest.json \
  -PgxbOfflineTrustedHosts=cdn.example.com,assets.example.com \
  -PgxbOfflineManifestPublicKeyB64='<base64 raw 32-byte Ed25519 public key>' \
  :app:assembleDebug
```

`gxbOfflineTrustedHosts` must include the manifest host and every HTTPS host used by pack URLs/redirects. `gxbOfflineManifestPublicKeyB64` is a Base64-encoded raw Ed25519 public key; the matching private key is used only by the pack-publishing tool and must never be placed in the APK or repository. The Android worker continues across Activity recreation and retains verified partial downloads for a later retry. The **Xem thử shell local** button only proves local HTML/CSS/JS asset serving; it is not the game API and is not an offline-play readiness check.

The tracked-root allowlist `tools/offline_resources_allowlist.json` packages all Git-tracked files under `web/`. `.github/workflows/offline-resource-pack.yml` uses `actions/checkout` with Git LFS enabled, verifies no pointer remains, then builds deterministic ZIP packs in a streaming manner. It auto-runs when `web/**` or `.gitattributes` changes; run it manually after changing the builder or allowlist. The working-copy pointer inventory is about 4.68 GiB for `web/` (3.74 GiB declared LFS payload plus regular files); the pipeline must run before treating these as hydrated/verified production bytes. Local sandbox currently has no LFS objects.

For CI signing, configure the repository secret `OFFLINE_MANIFEST_SIGNING_KEY_PEM` with the Ed25519 PEM private key and repository variable `OFFLINE_RESOURCE_BASE_URL` with the HTTPS immutable-pack base URL. Never commit or embed the private key. Without these settings, the workflow deliberately produces an unsigned development-only manifest using a placeholder URL; the Android app will reject it. Run the workflow manually to provide a one-off base URL. Full multi-GiB Actions artifact upload is opt-in (`upload_pack_artifact`) and retained for one day; check repository artifact quota first. The workflow builds/verifies packs but does not publish them to a CDN.

**Android signature caveat:** The RC workflow currently uses the ephemeral CI debug signing identity. A later rebuild may use a different key and require uninstalling an earlier RC APK before installation. This does not remove server-side account progress but can remove device-local application data. For a permanent production Android release, use a private, persistent release keystore rather than the debug key.

The ALPHA RC7 workflow writes download artifacts for Windows, Android and iOS, with 30-day retention. The build run's commit SHA identifies the source revision of each artifact.


### 2026-10-15 client build
All three platform launchers continue to open the production GXB 3 URL. Rebuild after publisher-shard image, bulk summon and original Dates/Oath interface recovery; no game items are shipped or generated inside the wrappers.

Shards now support a verified bulk quantity (maximum 50 uses per request) and original Dates/Oath routes remain server-authenticated. This README revision rebuilds all native clients from the final tested source.

### Hotfix packaging refresh — 2026-10-15
Native launcher artifacts are rebuilt after GXB 3 server commit `5bafac0bf6784a2feca38adee40802f10c39c8ae` (Dates/Oath syntax fix). Windows, Android and iOS wrappers all connect to the same live production server; no game state is embedded in these packages. The unsigned iOS developer IPA still requires Apple signing before device installation.
