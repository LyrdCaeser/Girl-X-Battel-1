> **02/10/2026 — actualización 088:** nuevas tablas y sistemas locales, ajustes de Campaign y Tests, guías contextuales, iconos y efectos de brillo, textos de interfaz en inglés, estados de batalla, formación centrada y rótulos VICTORY/DEFEAT. [Notas de distribución](DISTRIBUCION_2026-10-02.md).

> **01/10/2026 — CONTENT-072:** Friend Boss actual, Servant Training, Ulticore y Practical Work disponibles desde Inicio → Training & Bosses. Growth Diary **157/160**. **364 tests aprobados** y combates nativos comprobados en DB temporal. [Alcance y límites](SISTEMAS_PENDIENTES_RECONSTRUIDOS.md). Reiniciar servidor para cargar el código.

> **01/10/2026 — GXB2-CONTENT-071:** Growth Diary actualizado a **154/160** misiones; Newbie Camp con **tres etapas, 30 tareas y tres premios**, **28/30** tareas conectadas. API y mensajes originales, premios persistentes y comprobación sobre partida temporal. Reiniciar servidor; botones en Inicio. [Newbie Camp](NEWBIE_CAMP.md) · [Diario actualizado](GROWTH_DIARY.md).

# Girls X Battle 2 — versión local

Proyecto de preservación y reconstrucción para jugar en un servidor local, con código, datos, ilustraciones, animaciones, iconos y voces incluidos. Hay sistemas completos y otros parciales; consulta [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) y [GXB2_MASTER_CHECKLIST.md](GXB2_MASTER_CHECKLIST.md) para conocer el alcance real.

## Inicio en macOS

Necesitas Python 3.10 o posterior. El motor de combate incluye LuaJIT para macOS Intel. En Apple Silicon, este ejecutable necesita Rosetta; también puedes usar un LuaJIT nativo como se indica abajo.

```sh
git clone https://github.com/Armenidez/gxb2-local.git
cd gxb2-local
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 server.py --open
```

Abre `http://localhost:9080/`. Para detener el servidor, pulsa Ctrl+C. El repositorio es privado: necesitas acceso desde tu cuenta de GitHub para descargarlo. La descarga es grande porque incluye los recursos gráficos y de sonido.

Si esos puertos ya están ocupados:

```sh
python3 server.py --open --http-port 9242 --tcp-port 9243
```

## Inicio en Windows 10/11 (64 bits)

1. Instala Python 3.10 o posterior desde https://www.python.org/downloads/windows/ y activa la opción de añadir Python al PATH.
2. Descarga este repositorio privado con **Code → Download ZIP** (o usa Git) y descomprime toda la carpeta.
3. Haz doble clic en **Iniciar-Windows.cmd**. La primera vez crea el entorno de Python e instala la dependencia; después abre el juego en el navegador.

El motor LuaJIT para Windows x64 ya está incluido y se selecciona automáticamente. No necesitas instalar LuaJIT ni ffmpeg. La primera instalación de la dependencia de Python necesita conexión a Internet; los recursos del juego están incluidos.

Si necesitas cambiar los puertos, abre una terminal en la carpeta y ejecuta:

```bat
Iniciar-Windows.cmd --http-port 9242 --tcp-port 9243
```

La consola debe permanecer abierta mientras juegas. Pulsa Ctrl+C para detener el servidor. Windows ARM y versiones anteriores a Windows 10 no están verificados.

## LuaJIT en otros equipos

El motor de combate necesita LuaJIT 2.x. Para utilizar tu propia instalación compatible (por ejemplo, macOS con LuaJIT nativo o Linux), configura la ruta al ejecutable antes de arrancar:

```sh
export GXB2_LUAJIT="$(command -v luajit)"
python3 server.py --open
```

Se incluyen ejecutables separados para macOS x64 y Windows x64. En Linux, instala LuaJIT; el servidor lo busca en PATH o acepta `GXB2_LUAJIT`. Se mantienen los avisos de licencia de las bibliotecas en `runtime/` y `web/vendor/`.

## Partidas y modo de desarrollador

El primer inicio crea una partida nueva en `state/profile.sqlite3` y una partida independiente de desarrollador en `state/profile.developer.sqlite3`. Las bases de datos y exportaciones personales se excluyen de Git. Cambiar el modo de juego en la interfaz permite probar con la partida de desarrollador.

Para abrir otra copia guardada:

```sh
python3 server.py --db state/mi-partida.sqlite3 --open
```

Para hacer una copia coherente, incluso con el servidor abierto:

```sh
python3 tools/save_archive.py backup state/profile.sqlite3 backups/mi-partida.sqlite3
```

La reconstrucción no recupera por sí misma una cuenta alojada en los antiguos servidores.

## Archivos incluidos

- `server.py`, `gxb2/`: servidor y reglas locales.
- `web/`: interfaz, bibliotecas del navegador y todos los assets exportados.
- `data/`: tablas y datos necesarios para jugar.
- `runtime/`: motor Lua y LuaJIT para macOS x64 y Windows x64.
- `tools/` y documentos de estado: herramientas e historial del proyecto.

Las pruebas de desarrollo y las capturas de referencia se conservan en el Mac de trabajo y se excluyen de la versión final del repositorio.

No necesitas las carpetas originales de `Downloads` para iniciar el juego. Los extractores de `tools/` sirven para reconstruir recursos desde las fuentes originales y algunos sí requieren esas fuentes; no es necesario ejecutarlos tras descargar este repositorio. Las voces ya están convertidas a MP3. Su regeneración opcional requiere ffmpeg y la carpeta de sonidos original.

## Verificación

```sh
python3 tools/bundle_voices.py --check
```

Los informes históricos no certifican la fidelidad completa del juego y pueden enlazar a pruebas o capturas en `tests/`, `docs/references/` y `validation/`, conservadas localmente y excluidas de la versión final del repositorio junto con las partidas usadas para pruebas. Consulta [LEEME.md](LEEME.md) para el historial y la arquitectura.


Comprobación de distribución: copia limpia en macOS y [arranque/combate en Windows x64](https://github.com/Armenidez/gxb2-local/actions/runs/36729034925) aprobados. La comprobación de Windows usa Windows Server 2022; no representa una revisión visual completa de todas las pantallas de Windows 10/11.

## Recuperación completa de tablas — 01/10/2026

[Tablas recuperadas](TABLAS_RECUPERADAS.md): 904/904 tablas originales, 202.878 filas en segmentos, 252 tablas inglesas y ocho dossiers de sistemas. Datos y manifest en `data/recovered/`; extractor reproducible en `tools/recover_client_tables.py`. Recuperación documental completa de estas fuentes; la integración jugable sigue siendo parcial. No cambia reglas ni partidas.

## Growth Diary — 01/10/2026

Nuevo botón en Inicio tras la fase 5: 40 capítulos / 160 misiones, 121 con seguimiento local, reclamación única y guardado. [Alcance y 39 objetivos pendientes](GROWTH_DIARY.md). Reinicia el servidor para cargarlo.
