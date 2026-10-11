# LuaJIT para Windows x64

Ejecutable compilado desde el repositorio oficial https://github.com/LuaJIT/LuaJIT, rama v2.1, commit `c6ffc141a8762b41703f9287d63d93622a13dd8f`.

Compilación cruzada en macOS ARM64 con MinGW-w64 14.0.0_3:

```sh
make -C src -j4 HOST_CC=cc CROSS=x86_64-w64-mingw32- TARGET_SYS=Windows BUILDMODE=static TARGET_LDFLAGS=-static-libgcc XCFLAGS=-DLUAJIT_DISABLE_GC64
```

`src/luajit.exe` se distribuye como `runtime/luajit-windows-x64.exe`; su licencia se conserva en `LuaJIT-WINDOWS-COPYRIGHT`. No necesita una DLL de LuaJIT adicional. Requiere Windows x64 con Universal CRT (incluido en Windows 10/11). Los módulos C externos que dependan de lua51.dll no forman parte de esta distribución; el juego usa los módulos Lua incluidos en `runtime/lua/`.

El procedimiento de compilación cruzada está documentado por LuaJIT en https://github.com/LuaJIT/LuaJIT/blob/v2.1/doc/install.html.

GC64 se desactiva expresamente para leer el bytecode original de `runtime/lua/`, cuyo formato usa marcos de una ranura (igual que el LuaJIT macOS incluido). Una compilación x64 moderna con GC64 activado rechaza ese bytecode como incompatible.
