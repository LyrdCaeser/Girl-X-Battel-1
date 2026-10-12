# GXB 3 release clients

Thin native clients for the production service:

- Windows x64: PyWebView/WebView2 wrapper.
- Android: native WebView APK, Android 8.0+ (API 26+).

Production origin: `https://gxb3-production.onrender.com`.

The Android RC currently uses the Android debug signing identity so the generated
APK is installable for release-candidate testing. Before the first permanent
public Android release, replace it with a private long-lived release keystore;
after users install a permanently signed build, losing/changing that key prevents
in-place updates.

Both clients intentionally keep authoritative game state, authentication, PvP,
Guild War and payments on the production server.
