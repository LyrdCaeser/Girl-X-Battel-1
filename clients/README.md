# GXB 3 release clients — ALPHA RC7 hotfix

Native launcher clients for the current GXB 3 production server, with authoritative gameplay served live from https://180-93-111-99.sslip.io/.

- Android 8.0+ APK (API 26+, 64-bit and 32-bit compatible WebView wrapper); built with Android Gradle, debug-signed for RC distribution.
- Windows x64 EXE (PyWebView / Edge WebView2 wrapper); requires working WebView2 and network access.
- iOS 15.0+ unsigned IPA (WKWebView, arm64) for developers to sign with their own Apple provisioning profile; **unsigned IPAs cannot be directly installed on customer iPhones**.
- iOS Safari Web Clip (.mobileconfig) to open the production web game from the Home Screen without Apple signing. Users can also open the URL in Safari and choose Share > Add to Home Screen, no profile needed.

All launchers connect to the online server. Gameplay, login, payments, PvP, guild progress and inventory are stored server-side; these packages do not contain an offline game.

**Android signature caveat:** The RC workflow currently uses the ephemeral CI debug signing identity. A later rebuild may use a different key and require uninstalling an earlier RC APK before installation. This does not remove server-side account progress but can remove device-local application data. For a permanent production Android release, use a private, persistent release keystore rather than the debug key.

The ALPHA RC7 workflow writes download artifacts for Windows, Android and iOS, with 30-day retention. The build run's commit SHA identifies the source revision of each artifact.


### 2026-10-15 client build
All three platform launchers continue to open the production GXB 3 URL. Rebuild after publisher-shard image, bulk summon and original Dates/Oath interface recovery; no game items are shipped or generated inside the wrappers.

Shards now support a verified bulk quantity (maximum 50 uses per request) and original Dates/Oath routes remain server-authenticated. This README revision rebuilds all native clients from the final tested source.
