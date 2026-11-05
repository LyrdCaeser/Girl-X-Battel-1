# LuaJIT Android runtime

This directory contains the reproducible cross-build entry point and Lua headers used by the Android JNI battle bridge.

- Pinned LuaJIT commit: `c6ffc141a8762b41703f9287d63d93622a13dd8f`
- `arm64-v8a`: Android API 21 compiler, `LUAJIT_DISABLE_GC64` for compatibility with the current GXB3 bytecode layout.
- `armeabi-v7a`: Android API 26 compiler, 32-bit host compiler required for LuaJIT's VM generator.
- Output: `app/src/main/jniLibs/<abi>/libluajit.so`.
- `libluajit.so` uses an Android-safe SONAME so `libgxb_battle.so` resolves the dependency inside the APK.

Build:

```bash
export ANDROID_NDK_HOME=/path/to/android-ndk
clients/android/native/build_luajit_android.sh
```

## JNI bridge

`app/src/main/java/com/quangho/goddess/battle/BattleRuntimeBridge.java` extracts
`battle_host.lua` and `runtime/lua` from APK assets into app-private storage,
writes one temporary Lua table literal, and calls the native
`libgxb_battle.so`. The C++ bridge recreates the existing CLI contract:

```text
arg[1] = runtime root
arg[2] = battle | attrs
arg[3] = input Lua file
```

It captures the JSON line printed by `battle_host.lua`; battle rules remain in
the existing Lua engine. Build/link verification has passed for both
`arm64-v8a` and `armeabi-v7a`. A physical Android smoke test and the Local API
route adapter are still separate tasks.
