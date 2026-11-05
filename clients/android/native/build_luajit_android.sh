#!/usr/bin/env bash
set -euo pipefail

# Reproducible LuaJIT Android build for the battle engine.
# LuaJIT commit is pinned to the desktop runtime compatibility commit used by GXB3.
LUAJIT_COMMIT="c6ffc141a8762b41703f9287d63d93622a13dd8f"
NDK_DIR="${ANDROID_NDK_HOME:-${ANDROID_NDK_ROOT:-}}"
if [[ -z "$NDK_DIR" || ! -d "$NDK_DIR" ]]; then
  echo "Set ANDROID_NDK_HOME or ANDROID_NDK_ROOT to an Android NDK directory." >&2
  exit 2
fi
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SRC="${LUAJIT_SOURCE_DIR:-$ROOT/third_party/LuaJIT}"
BIN="$NDK_DIR/toolchains/llvm/prebuilt/linux-x86_64/bin"
OUT="$ROOT/clients/android/app/src/main/jniLibs"
BUILD_ROOT="${TMPDIR:-/tmp}/gxb3-luajit-android"

if [[ ! -f "$SRC/src/Makefile" ]]; then
  mkdir -p "$(dirname "$SRC")"
  git clone https://github.com/LuaJIT/LuaJIT.git "$SRC"
fi
if [[ "$(git -C "$SRC" rev-parse HEAD)" != "$LUAJIT_COMMIT" ]]; then
  git -C "$SRC" fetch --depth=1 origin "$LUAJIT_COMMIT"
  git -C "$SRC" checkout --detach "$LUAJIT_COMMIT"
fi

build_one() {
  local abi="$1" host_cc="$2" cross="$3" cc="$4" out_dir="$5" gc_flag="$6"
  local work="$BUILD_ROOT/$abi"
  rm -rf "$work" "$OUT/$abi"
  mkdir -p "$work" "$OUT/$abi"
  cp -a "$SRC"/. "$work"/
  make -C "$work" clean >/dev/null 2>&1 || true
	  make -C "$work" -j"${JOBS:-2}" BUILDMODE=dynamic TARGET_SYS=Linux \
	    HOST_CC="$host_cc" CROSS="$BIN/$cross" \
	    STATIC_CC="$BIN/$cc" DYNAMIC_CC="$BIN/$cc -fPIC" \
	    TARGET_LD="$BIN/$cc" TARGET_AR="$BIN/llvm-ar rcus" TARGET_STRIP="$BIN/llvm-strip" \
	    TARGET_SONAME="libluajit.so" \
	    XCFLAGS="$gc_flag"
  cp "$work/src/libluajit.so" "$OUT/$abi/libluajit.so"
  "$BIN/llvm-strip" "$OUT/$abi/libluajit.so"
}

# arm64 intentionally disables GC64 to match the existing GXB3 bytecode frame layout.
build_one arm64-v8a "gcc" "aarch64-linux-android-" "aarch64-linux-android21-clang" \
  arm64-v8a "-DLUAJIT_DISABLE_GC64"
# armeabi-v7a requires a 32-bit host compiler for LuaJIT's build-time VM generator.
build_one armeabi-v7a "gcc -m32" "arm-linux-androideabi-" "armv7a-linux-androideabi26-clang" \
  armeabi-v7a "-DLUAJIT_DISABLE_GC64"

echo "Built LuaJIT shared libraries under $OUT/{arm64-v8a,armeabi-v7a}."
