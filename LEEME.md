> **01/10/2026 — CONTENT-072:** Friend Boss actual, Servant Training, Ulticore y Practical Work disponibles desde Inicio → Training & Bosses. Growth Diary **157/160**. **364 tests aprobados** y combates nativos comprobados en DB temporal. [Alcance y límites](SISTEMAS_PENDIENTES_RECONSTRUIDOS.md). Reiniciar servidor para cargar el código.

> **01/10/2026 — GXB2-CONTENT-071:** Growth Diary actualizado a **154/160** misiones; Newbie Camp con **tres etapas, 30 tareas y tres premios**, **28/30** tareas conectadas. API y mensajes originales, premios persistentes y comprobación sobre partida temporal. Reiniciar servidor; botones en Inicio. [Newbie Camp](NEWBIE_CAMP.md) · [Diario actualizado](GROWTH_DIARY.md).

> **Estado y protección de partidas — 30/09/2026.** La [sección 40 del checklist](GXB2_MASTER_CHECKLIST.md#40-actualización-de-cobertura--2026-09-30) contiene el estado después de WAVE-048 y la tanda049. `tools/save_archive.py` crea una copia SQLite coherente incluso con el servidor abierto y permite restaurarla **en un archivo nuevo**, sin sobrescribir la partida habitual. Desde esta carpeta:
>
> `python3 tools/save_archive.py backup state/profile.sqlite3 backups/mi-partida.sqlite3`
>
> `python3 tools/save_archive.py restore backups/mi-partida.sqlite3 state/restaurada.sqlite3`
>
> Para jugar con la copia restaurada sin detener el servidor habitual, usa `python3 server.py --db state/restaurada.sqlite3 --http-port 9240 --tcp-port 9241` y abre `http://127.0.0.1:9240/`. La herramienta comprueba integridad/estructura y rechaza un destino existente. Todavía faltan migraciones de formatos antiguos y el import de la partida original. Pruebas: [VALIDACION](VALIDACION.md).

> **Iconos corregidos — 29/09/2026, GXB2-PORTRAITS-008.** El selector legado conocía81 IDs y dejaba Selene y otras chicas como cuadros oscuros. Ahora usa el avatar original de cada registro:439 PNG íntegros,637 registros y359/359 chicas visibles. Comprobado en invocación y formación sobre partida temporal. [Causa, pruebas y relevo](validation/portraits-2026-09-29/README.md). No cambia progresión ni saves.

# Actualización — Patrol e inventario del cliente (29/09/2026)

League → Battle → **Patrol** ya es jugable (ver [ESTADO_PROYECTO](ESTADO_PROYECTO.md)). Datos: `python3 tools/extract_patrol.py` (genera `data/patrol.json` y `web/assets/patrol/`). Para saber qué sistemas del cliente original faltan, ver [INVENTARIO_CLIENTE](INVENTARIO_CLIENTE.md) o ejecutar `python3 tools/build_client_inventory.py`.

---

# Actualización — Slots y Lucky Store (29/09/2026)

**GXB2-SLOTS-LUCKY-004:** dealers originales animados en Normal/High Stakes; Lucky Store funcional con ocho ofertas, Coupons, límite por oferta, refresh y guardado; Skip por modalidad, probabilidades del tablero, contadores vivos, Records y enlace directo a Slot Points. **49 pruebas aprobadas** y11 JS válidos. QA en partida temporal normal:50 tiradas por40,500 Coupons/50 puntos; compra de tienda y preferencias tras recarga verificadas. La partida habitual no se abrió ni se detuvo su servidor.

El sistema sigue **[P][M]**: sorteo/calendario local de la tienda y highlight web son adaptaciones explícitas; faltan FX/dialogue/audio originales y verificación táctil/responsive completa. [Investigación, capturas y límites](validation/slots-lucky-2026-09-29/RESEARCH.md), [decisiones](DESIGN_DECISIONS.md), [handoff](AI_WORKBOARD.md). Este encabezado sustituye pendientes de dealers/Skip/reloj/Shop descritos abajo; los registros históricos se preservan.

---

> **Referencias del29/09 incorporadas:** [nueve capturas y diferencias de versión](docs/references/2026-09-29/README.md). Exchange ahora dispone de paneles verticales con chibis; Slots usa selector lateral10→20→50 y dos botones de compra.50 tiradas cuestan40. Las capturas de Slot Points con5 rondas se registran como variante; no sustituyen los datos recuperados con8. Reglas de backend conservadas.

# Actualización funcional — GXB2-RECON-WAVE-001

Tanda iniciada el 28/09 y cerrada el 29/09/2026 (hora del equipo). Se reconstruyeron **Exchange y Slots Normal/High Stakes**, con costes, premios, guardado y protección de chicas; se corrigieron periodos semanales de puntos y liquidación idle al cambiar fase. **47 pruebas aprobadas**, sintaxis de los once JS propios comprobada y recorridos visuales sobre una partida temporal. No certifica el juego completo.

- **Campus → Enroll → Exchange:** elegir chica4★/5★ apta, gastar Portfolios, volver después para guardar/descartar la propuesta. Guardar conserva build/formación y limpia skin/relación según el contrato local documentado.
- **Campus → Slots:** Normal y High Stakes, ocho premios, tiradas/costes según tablas, refresh gratis/pagado, límites e historial. Normal produce Slot Points y Coupons. Lucky Store sigue pendiente.
- **Chicas → detalle → Bloquear:** protege contra Exchange y consumo como material. La chica con Exchange pendiente también queda protegida contra consumo.
- **Eventos13/16/20:** periodo semanal Reborn lunes 00:00 UTC, sin conceder de nuevo una semana anterior al retroceder el reloj; conserva progreso legado al vincularlo por primera vez.
- **Idle:** fase histórica para cada tick completado, cap12h, fracciones conservadas. El botín cada600s y la liquidación son adaptaciones locales identificadas.

Reglas del cliente y decisiones del servidor local están separadas en [investigación y contratos](validation/reconstruction-2026-09-28/RESEARCH.md) y [DESIGN_DECISIONS](DESIGN_DECISIONS.md). [Estado actual y siguientes prioridades](ESTADO_PROYECTO.md); [pruebas/capturas](VALIDACION.md); [relevo y archivos](AI_WORKBOARD.md).

La partida habitual y las fuentes originales no se usaron ni modificaron. Para probar en tu partida, reinicia únicamente su servidor cuando decidas cargar los archivos nuevos; no se detuvo durante esta revisión. Arranque normal descrito más abajo. Las pruebas manuales usaron otros puertos y una base temporal, sin DEV.

## Registro anterior conservado

Las afirmaciones de 38 pruebas, Exchange/Slots pendientes, ausencia de reset y tarifa idle retroactiva del texto siguiente corresponden a la auditoría anterior. Este encabezado y ESTADO_PROYECTO sustituyen esos pendientes concretos.

---

> **Estado actualizado — 28/09/2026:** la auditoría de documentación y código está en [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md). Se conserva todo el texto anterior como historial: sus listas tempranas de pendientes y recuentos de pruebas fueron superados parcialmente por actualizaciones posteriores. La matriz auditada indica alcance, evidencia y lo no verificado.
>
> **Para Claude, ChatGPT o Nava:** leer primero [GXB2_MASTER_CHECKLIST.md](GXB2_MASTER_CHECKLIST.md), después [AI_WORKBOARD.md](AI_WORKBOARD.md), este LEEME y el informe de estado. Reclamar una tarea y declarar archivos antes de editar; respetar bloqueos. Documentar investigación y adaptación offline por separado, preservar el comportamiento original y cerrar con pruebas/limitaciones/handoff.

## Qué documento sirve para qué

| Documento | Uso |
|---|---|
| [GXB2_MASTER_CHECKLIST.md](GXB2_MASTER_CHECKLIST.md) | Inventario completo de preservación, protocolo multi-agente y definición de terminado. |
| [LEEME.md](LEEME.md) | Arranque, arquitectura, fuentes y registro histórico de avances. |
| [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) | Estado contrastado por sección del checklist, evidencias, pendientes y prioridades actuales. |
| [AI_WORKBOARD.md](AI_WORKBOARD.md) | Responsables, archivos reclamados, bloqueos y relevo sin chats antiguos. |
| [VALIDACION.md](VALIDACION.md) | Pruebas ejecutadas y límites; las capturas históricas no sustituyen la revisión de cambios recientes. |
| [MAPA_MENUS.md](MAPA_MENUS.md) | Rutas visuales y ventanas originales; navegar no demuestra implementar. |
| [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) | Supuestos de servidor y sustituciones Reborn existentes, separados de datos originales. |

**Resumen actual:** 38 pruebas existentes aprobadas; el backend contiene operaciones de equipo/forja/tesoro/antigüedad, progresión hasta 15★, idle y Enroll, además de partes de Servants, Libro, Excursion, Cosmos y contactos/correo locales. Son sistemas de alcance parcial; no se afirma preservación completa. Hay 530 fases con referencias de combate y 1.500 de 2.000 pisos Tests con datos; falta validación integral de jugabilidad. Puntos de eventos no tienen reset semanal backend y el idle requiere estudiar la liquidación al cambiar fase.

Las prioridades son reloj/reset de eventos, liquidación idle, migración/restore y verificación de fidelidad/UI. Detalles y criterios en [ESTADO_PROYECTO](ESTADO_PROYECTO.md). La siguiente guía y las actualizaciones se preservan íntegramente; al trasladar el proyecto, incluir también los nuevos documentos y reclamar una tarea concreta en lugar de reutilizar un objetivo antiguo.

---

# Girls X Battle 2 — prototipo local de preservación

## Empezar

Abre **Iniciar.command** en esta carpeta y visita <http://127.0.0.1:9080>. Mantén abierta la ventana del servidor. Si ya está funcionando, basta con abrir el enlace. Para detenerlo, pulsa Ctrl+C en su terminal.

Esta versión permite entrar desde una portada inspirada en la captura aportada, formar un equipo, invocar integrantes, combatir, mejorar personajes y conservar el progreso. La pantalla del navegador es una interfaz de prueba nueva: **el APK original todavía no está conectado**.

El mapa de pantallas recuperadas está en [MAPA_MENUS.md](MAPA_MENUS.md). Shopping Street tiene un mapa interactivo con los edificios originales; Campus, Life, Battle/League, Gremio y Menú enlazan decenas de ventanas con sus recursos visuales. Las acciones que requieren servicios del juego original se indican dentro de cada ventana.

## Guía para continuar el proyecto en otro chat

Este documento es el punto de partida para Claude, ChatGPT u otra persona que vaya a continuar el trabajo. El otro chat no puede ver automáticamente las carpetas de tu Mac: adjunta una copia comprimida de `gxb2_local` y, si necesita un recurso externo concreto, pídele que indique su nombre y carpeta para que tú puedas adjuntarlo después.

### Qué contiene este proyecto

| Carpeta o archivo | Qué hay dentro |
|---|---|
| `server.py` | Servidor local para navegador y socket de pruebas. El juego funciona sin conectarse a los servidores oficiales. |
| `web/` | Interfaz web: portada, equipo, campaña, invocación y combate. `web/assets/characters/` contiene imágenes estáticas; `battle-maps/`, fondos de combate. |
| `gxb2/` | Código del backend local: reglas de perfil, niveles, formación, invocación, campaña, persistencia y mensajes. |
| `runtime/battle_host.lua` | Adaptador usado para ejecutar el cálculo de batalla recuperado del juego. |
| `runtime/lua/` | Código Lua recuperado y datos necesarios para el combate. Es voluminoso, pero forma parte del motor actual. |
| `runtime/luajit-macos-x64` | Intérprete incluido para macOS Intel/Rosetta. En Windows, Linux o Mac sin Rosetta podría hacer falta otro LuaJIT compatible. |
| `data/` | Tablas y esquemas JSON que usa el backend, como personajes, fases, enemigos, costes y mensajes. |
| `state/profile.sqlite3` | Partida **local de este prototipo**: progreso, equipo e informes de batalla. Inclúyela si quieres que el otro chat preserve esta partida; guarda una copia antes de compartir. |
| `tests/` | Pruebas automatizadas del backend. |
| `LEEME.md` y `VALIDACION.md` | Descripción del alcance y registro de lo comprobado. |
| `Iniciar.command` y `requirements.txt` | Inicio rápido en Mac y dependencia de Python. |

### Recursos que están fuera de este proyecto

Estas rutas solo existen en tu equipo; el otro chat no puede abrirlas hasta que le adjuntes archivos:

- `~/Downloads/Decomp files/`: copia de la decompilación basada en el APK 1.5.686. Tiene Lua, retratos y recursos ya extraídos. La carpeta Unity completa es grande; comparte solo la parte concreta que te pidan.
- `~/Downloads/Decompiled/`: paquete adicional aportado por el usuario. Contiene 640 atlas PNG sin cortar, 17.365 sprites cortados, fondos, sonidos y tablas. Los nombres de sus 640 atlas coinciden con los directorios de atlas de `Decomp files` ignorando mayúsculas. `main_window_h5.png` coincide píxel a píxel con el atlas Unity anterior una vez recortado el margen transparente; `tools/import_decompiled_main_h5.py` usa esa hoja y el prefab para regenerar los seis iconos inferiores originales en `web/assets/nav-reference/`. No se ha copiado todo el paquete al proyecto.
- `tools/extract_tower.py` copia de ese paquete solo los sprites de Tests necesarios para la nueva pantalla, incluidos puertas, cofres y ficha. Los fondos de piso se copian de `Decomp files/unity/Assets/hotres/textures/scenes_web`.
- `~/Downloads/com.carolgames.moemoegirls/`: copia descomprimida de Android/data, con recursos de versión 1.5.410. Sus recursos están en `files/Bundles/Android/` y `files/Download/webview/cache/resource/`. Hay sprites, atlas, tablas y animaciones Spine. Muchos archivos `.bytes` usan el formato de Unity; no son imágenes listas para abrir.

La copia de Android/data también contiene `files/Databases/game.db` con campos de sesión de la cuenta. **No adjuntes esa base ni la carpeta completa**. Para trabajo gráfico, pide que especifiquen un recurso y comparte solo la subcarpeta necesaria, por ejemplo `Bundles/Android/spine/hero_web/<personaje>` o una textura concreta. `spine/hero_web` completa ocupa cerca de 1 GB. No envíes credenciales, tokens ni registros de cuenta.

La base local del juego original no contiene el inventario y el nivel completos de la cuenta: esos datos no aparecen en las tablas locales inspeccionadas. Sí hay configuraciones guardadas de formación, que podrían servir como referencia. El APK y los archivos originales deben permanecer intactos.

Se generó una [exportación anónima de los datos reales recuperables](real_save_export/LEEME.md): 31 formaciones, tres referencias de atuendo y catálogos de nombres de assets de los bundles y la caché webview. El exportador está en `tools/export_real_save.py` y excluye la tabla de sesión, chats e identificadores de cuenta.

### Texto para iniciar el nuevo chat

Después de adjuntar una copia de `gxb2_local`, puedes pegar este mensaje:

> Continúo un proyecto de preservación de Girls X Battle 2 para navegador. Lee primero `LEEME.md` y `VALIDACION.md`, revisa el código adjunto y sigue desde el estado actual. No quiero crear ni modificar un APK. La formación tiene seis casillas: 1–2 delante y 3–6 detrás; hay que conservar sus posiciones en batalla. Mantén intactas las fuentes originales. No accedas a servidores oficiales ni uses credenciales. Si necesitas recursos que no están adjuntos, dime el nombre o la ruta concreta para que pueda compartir solo esos archivos. Mi siguiente objetivo es aprovechar los gráficos disponibles y estudiar cómo mostrar las animaciones Spine.

### Cómo abrirlo en este Mac

1. Descomprime la copia del proyecto.
2. Abre `Iniciar.command`.
3. Visita <http://127.0.0.1:9080>.
4. Deja abierta la ventana del servidor mientras juegas. `Ctrl+C` lo detiene.

El progreso del prototipo se conserva en `state/profile.sqlite3`. Para continuar esa misma partida en otro equipo, incluye una copia de `state/`; para empezar de cero, no la incluyas. No envíes la base de datos original de Android para trasladar el progreso: no contiene los datos completos de la cuenta.

### Requisitos

Probado en este Mac con Python 3, Protocol Buffers 6.33.6 y Rosetta. El intérprete LuaJIT incluido es x86_64 para macOS; Apple Silicon lo ejecuta mediante Rosetta. En otra plataforma hace falta un LuaJIT compatible con bytecode v2, FR2=0; `GXB2_LUAJIT` permite indicar su ruta.

Si falta Protocol Buffers, desde esta carpeta:

```sh
python3 -m pip install -r requirements.txt
python3 server.py --open
```

El servidor escucha exclusivamente en `127.0.0.1`: HTTP 9080 y TCP 9081. No conecta con servidores del juego. No usa cuentas ni credenciales reales.

## Qué funciona

- Perfil ficticio local y tres personajes iniciales: Zombia, Miya y Nun.
- Formación editable de seis casillas (1–2 delante, 3–6 detrás), lista de personajes con retratos y subida de nivel con costes extraídos del APK. Cada casilla se guarda con su número exacto.
- Combate ejecutado por el bytecode original de `BattleCreateReport`, con semilla reproducible, enemigos y estadísticas de las tablas originales.
- Portada con el fondo `mapBg.png`, iconos y arte de personajes recuperados; entradas a campaña, equipo e invocación. La ilustración central se puede alternar entre tres personajes iniciales.
- Reproducción de acciones y vida en el navegador sobre fondos originales, con animaciones Spine originales asociadas a los 647 registros de personajes del motor (427 modelos distintos). Cada bando se coloca con las coordenadas 1–12 de `Battle.lua`, en dos columnas con lectura vertical; los turnos del motor Lua activan movimientos visuales y actualizan las barras de vida.
- Invocación local de cápsulas regulares, avanzadas y BFF. El coste, los grupos de personajes y los pesos salen de `summon.json` y `dropbox.json` de la versión decompilada. La gratuita regular se refresca cada 8 h y la avanzada cada 48 h. Los perfiles reciben recursos de prueba solo cuando faltan esos campos; el resto del progreso se conserva.
- Las avanzadas aceptan pergaminos o gemas según la tabla del juego. El cliente decompilado incluye el sorteo BFF de una unidad (ID 9), sin configuración de diez; el botón local de diez hace diez tiradas con el mismo grupo y coste unitario, como una ampliación documentada del prototipo.
- Menú Chicas con pestañas Chicas, Fragmentos y Galería; colección propia filtrable por las siete facciones y estrellas, acceso a Preset para volver a la formación, y catálogo de 359 chicas. Las tablas enumeran skins para 228 chicas (678 referencias); solo se muestra arte propio cuando existe una imagen local. Los siete iconos de facción salen del atlas CommonUI RGB+Alpha.
- Fragmentos específicos y aleatorios cargados de las tablas de objetos y de invocación. La combinación valida la cantidad guardada, consume el coste exacto y sortea con el dropbox local correspondiente; se guardó el extracto de metadatos en `data/debris.json`. El objeto 11 es Heart (moneda BFF), no fragmento.
- La pantalla de cápsulas usa recortes originales del atlas `Assets/hotres/atlases/summon` (fondos Normal/Super/Friendly, títulos y botones), reconstruidos con las coordenadas del prefab. Los atlas globales `Assets/Texture2D/Common*_{RGB,Alpha}.png` también están disponibles para recuperar más iconos y marcos; sus máscaras Alpha se combinan con RGB usando los metadatos del cliente.
- Recompensas de primera victoria, desbloqueo secuencial y guardado SQLite. Repetir una fase no duplica recompensas.
- Respuestas Protocol Buffers y encuadre TCP reconstruidos del cliente. El navegador y el socket comparten el mismo estado y las mismas reglas.

Los recursos, pergaminos y el equipo iniciales son una elección del prototipo. Las recompensas y los costes proceden de las tablas del cliente; las reglas de concesión son una reconstrucción local, no código recuperado del servidor oficial.

## Guardado

`state/profile.sqlite3` contiene el perfil y los informes de combate. Para copiar una partida, detén primero el servidor y copia la carpeta `state` completa. Para una partida independiente sin tocar la actual:

```sh
python3 server.py --db state/otra-partida.sqlite3
```

## Alcance y límites

**Tests** (League → Battle) ya es jugable en el navegador. `tower.lua` enumera 2.000 pisos y sus recompensas; el motor Lua recuperado y `battle.json` incluyen los combates de los primeros 1.500. Los pisos restantes se señalan como pendientes porque sus enemigos no existen en el motor actual. Una victoria avanza al piso siguiente y concede su recompensa, mientras cada intento real gasta una ficha. El máximo es 10 y se repone una cada 30 minutos, según `misc.lua`. El estado se guarda en la partida local. Práctica permite probar un piso alcanzado sin gastar fichas ni guardar premios. La lista visible muestra el piso actual y hasta nueve pisos futuros. Todavía no están reconstruidos el ranking, los registros de otros jugadores ni las compras de fichas.

Los combates de **Tests y Daily Quiz** usan ahora el mismo visor de rondas que la campaña: mapa original del encuentro, posiciones del equipo, arte de personajes, barras de vida y acciones tomadas del informe Lua. `Ver resultado` termina la reproducción; el botón de regreso vuelve a la pantalla del evento con sus premios o estado de práctica. `Ver batalla otra vez` reproduce el informe que sigue en memoria sin hacer otro combate ni gastar recursos. Las recompensas se calculan en el backend antes de la animación; saltarla no cambia el resultado.

La portada se reconstruyó a partir de la captura y la batalla tomó el video aportado como referencia de distribución. El personaje central no es el de la captura, sino una de las tres integrantes iniciales. Los combates de Campaña, Tests y Daily Quiz reproducen ahora los esqueletos Spine originales: reposo, ataque, habilidad, daño y caída. Los controles permiten ×1/×2/×4 y salto al resultado. El cálculo sigue procediendo del informe Lua; los efectos externos al esqueleto y el sonido siguen pendientes. La pantalla muestra las primeras 30 fases; se extrajeron 530 registros de fase, pero esto no implica que toda la campaña esté implementada o comprobada. Se verificó una ruta de 16 fases; en la fase 17 la estrategia de prueba agotó los recursos de mejora. La partida habitual conserva sus límites actuales de nivel. Graduate y las ascensiones hasta 10★ están implementados con recetas locales del cliente; siguen pendientes equipamiento, recompensas por tiempo, tiendas, otros eventos, gremios, PvP, tutorial completo y compras. Algunos objetos se guardan pero aún no tienen uso. La progresión puede detenerse por estos sistemas pendientes.

La respuesta de inicio de sesión es válida según el esquema y coherente para el prototipo. Falta comprobar todas las suposiciones de la interfaz Unity. El arranque HTTP es una respuesta de laboratorio; no sustituye todavía el SDK original. La reconexión valida la identidad local, pero no recupera una cola histórica de notificaciones.

## Mapa de la implementación

| Ruta | Función |
|---|---|
| `server.py` | HTTP local, transporte TCP y control de sesión local |
| `gxb2/protocol.py` | Esquema dinámico, serialización y encuadre |
| `gxb2/engine.py` | Estado persistente, formación, niveles, campaña y recompensas |
| `gxb2/battle.py` | Ejecución aislada del cálculo de combate |
| `runtime/battle_host.lua` | Adaptador del bytecode original; sustituye objetos gráficos y registro de mensajes |
| `runtime/lua` | Bytecode y tablas extraídos de la copia del APK |
| `data` | Descriptores y tablas convertidos a JSON |
| `web` | Pantalla local de prueba |
| `tests` | Pruebas de combate, persistencia, transacciones y transporte |

### Mensajes implementados

`CHECK_LOGIN` 6, `RECONNECT` 3, `HEART_BEAT_SYNC` 32785, `GET_LOGIN_INFO` 8, `GET_SUMMON_INFO` 272, `SUMMON` 273, `GET_MAP_INFO` 288, `GET_SLOT_INFO` 304, `GET_BACKPACK_INFO` 256, `SET_HANG_TEAM` 291, `STAGE_HANG` 289, `PARTNER_LEVUP` 309 y `MAP_FIGHT` 293. Notificaciones: `ITEM_CHANGE` 4096 y mapa 288. Los demás mensajes devuelven error explícito.

Peticiones: `uint32_le(longitud) | uint16_le(ID) | protobuf`.
Respuestas: `uint32_le(4 + longitud protobuf) | uint16_le(ID) | uint32_le(secuencia) | protobuf`.

## Procedencia y método

- APK 1.5.686 proporcionado por el usuario, paquete `com.carolgames.moemoegirls`. SHA256 del original: `70de79349ec7d593d92a8dac72880dbd216be29c51aa791448e5105523501efe`.
- Del APK se recuperaron los 1.721 tipos de mensaje y 4.529 campos; el esquema completo se carga correctamente en Protocol Buffers. Motor de combate y datos usados en ejecución provienen de ese APK.
- [GxB2Decomp de Escartem](https://github.com/Escartem/GxB2Decomp): el repositorio público conserva un aviso de retirada del contenido en junio de 2025. Se recuperó una copia archivada compartida públicamente para estudiar fuentes del cliente. El usuario también aportó `Decomp files`; se usó su atlas de retratos. El archivo corresponde al cliente y recursos de distintas versiones, no contiene un backend oficial listo para ejecutar. Su proyecto Unity no está listo para compilar.
- LuaJIT se compiló desde el [código oficial, revisión 0bee44c9dc9bee64d1143aa0febd2b61819d35bd](https://github.com/LuaJIT/LuaJIT/tree/0bee44c9dc9bee64d1143aa0febd2b61819d35bd), en modo x86_64 sin GC64. La licencia está en `runtime/LuaJIT-COPYRIGHT`.
- No se modificó el APK original, no se extrajeron credenciales y no se accedió a servidores del juego.

## Siguientes fases para conectar el cliente original

1. Preparar un entorno Android compatible con ARMv7 y conservar un duplicado del APK para pruebas. No hay un emulador Android ni Unity instalado en el entorno comprobado.
2. En esa copia, añadir un arranque local explícito que seleccione el servidor de preservación y una identidad ficticia, con recursos locales y sin ejecutar el inicio de sesión de plataforma. Esto requiere adaptar el cliente; cambiar únicamente la dirección no basta.
3. Ejecutar el arranque aislado, registrar únicamente peticiones locales y completar las respuestas que realmente consume Unity hasta llegar a la pantalla principal. Validar assets y catálogos de la misma versión.
4. Conectar formación → campaña → informe de combate → recompensas en la interfaz original. Comparar sus informes con el motor Lua ya operativo.
5. Añadir ascensión, equipamiento, reclutamiento y recompensas por tiempo; después extender modos. Cada sistema necesita reglas persistentes y pruebas, además de su formato de mensaje.

Reconstruir la UI desde el proyecto exportado es una alternativa más costosa: las clases IL2CPP exportadas no equivalen al código C# original funcional.

## Verificación

```sh
python3 -m unittest discover -s tests -v
```

Once pruebas aprobadas: reproducibilidad y serialización de combate, posiciones explícitas conservadas hasta el informe, recompensas sin duplicación y persistencia, rechazo de cambios inválidos sin mutar el perfil, respuesta de inicio de sesión y transporte TCP real con fragmentación, mensajes concatenados y llamadas HTTP, conversión de identificadores de bonificaciones de la fase 16, reclutamiento y progresión de Tests. Véase también `VALIDACION.md`.

## Referencias visuales de esta fase

Las capturas aportadas por el usuario muestran la portada vertical, las tarjetas de personajes y la formación de dos casillas superiores y cuatro inferiores. Se identificó el fondo original `textures/scenes_web/mapBg.png`, además del atlas `main_window_v3_1`. `app/common/Battle.lua` confirma `DEFAULT_FRONT_NUM=2`, `DEFAULT_BACK_NUM=4` y las coordenadas de combate de cada posición. El video [GirlsxBattle2 - Tests 1978 (6 Promethea)](https://www.youtube.com/shorts/JvncPQraKIQ) muestra una batalla tardía de seis contra seis; se usó como referencia de ritmo, no como verificación de que todos esos personajes o efectos estén implementados.

Los recursos de Unity separan color y transparencia en algunos atlas. La portada recompone ambas capas localmente mediante Canvas. El combate usa fondos `battle_map_*` y las ilustraciones `partner_picture_*` copiadas del archivo aportado. Los archivos `.skel.bytes` y `.atlas.txt` de Spine 3.6.37 se conservaron como referencia para la siguiente etapa; todavía no se renderizan.

## Pantallas Chicas y Bolsa

La pestaña **Chicas** usa 321 ilustraciones `partner_card_*` recuperadas de los atlas de Unity; cuando falta una tarjeta, usa la ilustración de combate o el avatar disponible. Los iconos de facción también proceden de `CommonUI`. El botón **Preset** abre la formación local y usa un icono original de `CommonBtn`; el botón de volver usa `win_back_btn`. La galería conserva la distinción entre personajes y skins con arte disponible.

La pestaña **Bolsa** reproduce la estructura de la referencia del usuario: Gear, Items, Consumable, Antiques y Anima Gear, cinco columnas, marcos de calidad originales, cantidades y filtro por calidad. Lee las cantidades reales de `/api/state` y los metadatos extraídos de `item1.lua` a `item5.lua` con los nombres en inglés de `item_text_en_en.lua`. Hay 2.350 objetos catalogados y 451 iconos de objeto recuperados; solo se muestran los objetos presentes en la partida. Al pulsar uno aparece su ficha. **Forge** muestra el estado pendiente: todavía no hay recetas ni operaciones de forja conectadas al backend.

`tools/extract_inventory_assets.py` permite regenerar las copias de tarjeta, icono, marco y controles desde `/Users/schroyle/Downloads/Decomp files` sin escribir en esa carpeta. Los resultados están en `web/assets/cards`, `web/assets/item-icons`, `web/assets/ui`, `web/assets/cards.json`, `web/assets/item-icons.json` y `web/assets/items-catalog.json`.

Al tocar una chica poseída se abre su **ficha**. La ilustración `partner_picture_*`, la facción, los iconos de habilidades, la ocupación y la frase proceden de los recursos y tablas originales; se extraen en `web/assets/detail`, `web/assets/skills` y `web/assets/girl-details.json`. Las flechas recorren las chicas poseídas. **Attribute** permite subir un nivel usando `PARTNER_LEVUP`, que descuenta oro y EXP de chica y persiste la mejora. Los cuatro números de atributos son estimaciones `base + crecimiento × (nivel − 1)`, porque el backend de preservación aún no expone el cálculo final de atributos con bonos. **Gear** muestra las ranuras y el equipo disponible en la Bolsa; equipar aún no está conectado. **Skins** permite previsualizar el arte existente sin cambiar la partida. **Awake** indica el progreso guardado y su implementación pendiente.

La subida de nivel se comprobó de extremo a extremo con una base de datos temporal: Miya pasó de nivel 1 a 2, el oro de 10.000 a 9.920 y el nivel siguió en 2 después de recargar. La partida principal del usuario no se modificó durante esa comprobación.

## Campus y Graduate

El botón **Campus** de la portada abre ahora un menú distinto de **Chicas**. Usa las seis ilustraciones originales de `main_window_v3_2` y los rótulos de `main_win_text_en_en_web`. **Study → Graduate** abre la evolución; los otros accesos de Campus todavía indican que están pendientes. La pestaña **Life** muestra ese mismo estado.

Graduate muestra las seis facciones, candidatos de 4★, su arte, las copias y materiales necesarios. `data/graduate.json` contiene 38 recetas extraídas de `partner_4up5.lua` y `partner.lua`. Para crear una chica de 5★ se necesita una base de 4★, otra copia idéntica, cuatro chicas de 3★ de la misma facción y seis chicas de 4★ de esa facción. El botón usa el mensaje local `COMPOSE_PARTNER` (ID 308) y valida las doce chicas distintas dentro de una transacción. Conserva el identificador, nivel y equipo de la base; consume las once restantes y quita de la formación cualquier material consumido. El servidor rechaza recetas incompletas o manipuladas sin cambiar el guardado.

La selección de materiales es automática; la selección manual, las recetas de 6★ o más y las mejoras de grado todavía están pendientes. La partida inicial no incluye suficientes duplicados ni materiales para evolucionar de inmediato; se obtienen jugando e invocando.


## Actualización 28/09/2026 — desarrollo y chibis

En **Inicio → DEV** puedes activar una partida de pruebas independiente. Se guarda en `state/profile.developer.sqlite3`; la partida habitual permanece en `state/profile.sqlite3`. Con `--db otra.sqlite3`, la partida de desarrollo se llama `otra.developer.sqlite3`. La selección se conserva por pestaña mientras dura su sesión.

- Oro, gemas, experiencia de chica, materiales, fichas de cápsula, BFF y fragmentos se reponen a 1.000.000.000 al leer la partida de desarrollo. El jugador recibe nivel 400 para abrir las dificultades del Quiz.
- Invocaciones gratuitas sin espera, Daily Quiz sin límite diario y Tests con fichas ilimitadas. Las batallas y las recetas siguen calculándose con las tablas del juego.
- El panel permite añadir 1–20 copias de una chica, elegir nivel 1–330, aplicar nivel a toda la colección, elegir un piso de Tests 1–1500 y abrir las 30 fases visibles.
- **Volver a mi partida** recupera el guardado habitual. Las herramientas se rechazan cuando una petición usa la partida habitual.

Los iconos de Inicio se han sustituido por sprites cortados del paquete `Decompiled`: Gift Packs, Events, regalo temporal, Luvly’s Castle, Adrift Message, Friends, Fantasy Book, Servant, Excursion, Cosmos Portal y Campus/Campaign/League. Los seis iconos inferiores originales se conservan. Las entradas nuevas del castillo, mensajes y portal muestran su alcance pendiente; sus sistemas de evento todavía no se simulan.

`tools/spine36.py` convierte el formato binario 3.6.37 a JSON manteniendo huesos, attachments, mallas, deformaciones, curvas, restricciones y eventos. `tools/import_battle_assets.py` importa modelos desde `Decomp files/unity/Assets/hotres/spine/hero_web` y `hero`, reconstruye las texturas RGB+Alpha y deja un catálogo por ID. Los 359 registros del catálogo visible tienen modelo; también están incluidos los registros especiales del motor. `data/chibi-import.json` informa de la cobertura. Los archivos originales permanecen intactos.

El visor usa PixiJS 6.5.10 y pixi-spine 3.1.2, guardados localmente en `web/vendor`. Incluye el adaptador de PixiJS para conservar la política CSP sin `unsafe-eval`. Las referencias y licencias se encuentran en `web/vendor/README.md`. Los efectos que forman parte del propio esqueleto se reproducen; proyectiles, efectos externos, voz y música todavía no están conectados. No se verificaron visualmente los 427 modelos uno por uno.

La importación de animaciones ocupa aproximadamente 1,2 GB adicionales. Para regenerarla en este Mac: `python3 tools/import_battle_assets.py` (requiere Pillow). Para jugar, no hace falta esa dependencia ni las carpetas originales.


## Actualización 28/09/2026 — Eventos (Claude)

**Inicio → Eventos** abre ahora el hub de actividades reconstruido a partir de `ActivityWindow.lua`, en lugar del menú provisional. Tiene cuatro pestañas según `xyd.EventType`: Eventos (type1=2), Novato (3), Festivales (7) y Packs (1). La tira superior usa los fondos originales `activity_icon_0/1_middle` y los 322 iconos de `activity.lua` que existen en `Decompiled/Sprites (atlases, cut)`. Un punto rojo marca lo que se puede recoger.

- **Daily Login (ID 1)** es jugable. Sigue `windows/activity/CheckIn.lua` y el prefab `prefabs/windows/activity/check_in.prefab`: tres filas de 5 casillas en la pizarra, marcos por fila, marcos de "can get" y "has gotten", números de tiza, círculo y máscara de recibido, bocadillo con `CHECKIN_POPUP_TEXT1/2` y arte `partner_picture_11001`. Usa los 390 días de `activity_login` y, a partir del 391, repite en bucle desde el día 31 (`misc.login_loop_exclude`). Al pulsar una casilla disponible se recogen todas las del bloque, igual que `getAwards`. El doble por VIP no se aplica porque la partida local no tiene VIP.
- **7 Day Bonus (ID 116)**, en Novato, es jugable. Usa `activity_sevendays_awards` y las tarjetas `day_N_1/_2` (la `_2` lleva el sello de recibido). Desaparece de la lista después del día 7, como en el original.
- El resto de eventos aparecen como **archivados**: icono, título y descripción originales, sin jugabilidad.
- **Días de sesión:** en el original, el servidor contaba `online_days`. En local, un día cuenta cuando abres Eventos o haces una acción de evento en esa fecha (hora local del Mac). Con cada día nuevo se desbloquea una casilla.

Archivos: `gxb2/events.py` (reglas y guardado en `state['events']`), `web/events.js` y `web/events.css` (vista `#events-view`), `data/events.json` y `web/assets/events/` (generados por `tools/extract_events.py`), y `tests/test_events.py`. Rutas: `GET /assets/events/catalog.json`, `GET /assets/events/<nombre>.png` (limitado a los archivos de esa carpeta) y `POST /api/events/action` con `{action: visit|checkin|sevenday}`. El snapshot de `/api/state` incluye `event_hub`.

También se corrigió `Engine.level_cap`: fallaba con chicas cuyo `grade_lv1` está vacío, y ahora usa `max_lv`. Con esto, las 25 pruebas pasan (`python3 -m unittest discover -s tests`).

## Actualización 28/09/2026 — Equipamiento, Forja, Tesoros y Antigüedades (Claude)

**Arreglo de navegación:** la vista de menús de Inicio tenía el atributo `data-menu`. Por eso cualquier clic dentro, incluido el de volver, lo capturaba el listener global de `app.js` y reabría el menú. Ahora ese atributo se llama `data-hm-root`, y `home-menus.js` guarda una pila (`stack`): por ejemplo, Castillo → Adrift → volver regresa al Castillo, y Regalo temporal → Correo → volver regresa a los regalos.

**Equipo (Chica → Gear):** hay seis ranuras, como `Partner.equipments`: 1 Arma, 2 Ropa, 3 Accesorio, 4 Zapatos, 5 Tesoro y 6 Antigüedad (la 7 es la skin y no se toca aquí). Cada ranura muestra el icono y las estrellas originales, y un punto rojo si hay algo equipable en la Bolsa. Al elegir una ranura se ve la pieza actual con sus atributos, el bono de clase o facción (`act`, en verde si aplica) y los bonos de conjunto 2/3/4 piezas (`form`/`suit1-3`, en verde según las piezas puestas). Debajo aparece la lista de la Bolsa con **Equipar**, bloqueado si la pieza es de otra clase. **Equipar todo** usa el algoritmo de `onclickBtnEquipAll`: el `item_lv` más alto y, en caso de empate, la pieza de su clase. **Quitar todo** devuelve el equipo a la Bolsa. La pieza equipada sale de `state['items']` y se guarda en `partner['equips']` (siempre 7 enteros).
- **El combate original ya usa el equipo:** `ReportHero:populate` lee `equips` y `HeroAttr` suma atributos, conjuntos, bonos de clase o facción, tesoro y antigüedad. No hubo que tocar el motor de combate.
- **Atributos reales:** la pestaña Attribute muestra ahora el **Poder** y los HP, ATK, DEF y SPD reales calculados por `HeroAttr:attr` del juego. Para ello `runtime/battle_host.lua` tiene un modo `attrs`, accesible con `GET /api/partner/<id>/attrs`. Antes eran estimaciones.
- **Tesoro (ranura 5):** se desbloquea gratis desde el nivel 40 de la chica (`misc.treasure_open_level`) con un atributo aleatorio del nivel 1. **Mejorar** usa el coste `treasure_upgrade` (item 14 + oro) y da un atributo aleatorio del nivel siguiente. **Mejorar con bloqueo** añade las gemas de `treasure_lock_up` y lleva al id fijado. **Cambiar** (`treasure_refresh`) genera un atributo nuevo del mismo nivel, que se puede Guardar o Descartar. Los pesos salen de `treasure_weight`. Como el algoritmo del servidor no está en el cliente, se sortea por peso.
- **Antigüedades (ranura 6 y Bolsa → Antiques):** la pantalla Mejorar antigüedad sigue `ArtifactUpWindow`. Se añaden antigüedades como material hasta `artifact_upg` de experiencia (`artifact_exp` de cada una, con botón Auto) y la pieza pasa a `artifact_next`. El exceso vuelve como Afterglow (6000), 1 por cada 10 de experiencia (`misc.artifact_upgrade_excess_return`).
- **Forja (Bolsa → Forge, o desde una ranura):** sigue la maqueta de `smithy_window.prefab`, con pestañas por tipo, material → resultado, barra de progreso, cantidad con −/+/Máx, coste en oro, **Forjar** y **Forja automática** (`SmithyWindow:autoCompose`, que forja en cascada por toda la cadena de ese tipo). Las recetas vienen de `need_formula`, por ejemplo `1021#3|1#1000`.
- Al consumir chicas en Graduate o Awake, su equipo y su antigüedad vuelven a la Bolsa. El tesoro va ligado a la chica y se pierde con ella.

Archivos: `gxb2/equipment.py`, `web/equipment.js` y `web/equipment.css` (vista `#smithy-view`), `tools/extract_equipment.py` (genera `data/equipment.json` con 1307 piezas y sus nombres de `equip_text_en_en`, y copia los iconos a `web/assets/equipment/`), `tests/test_equipment.py`, y el modo `attrs` de `runtime/battle_host.lua` con `attributes()` en `gxb2/battle.py`. Ruta nueva: `POST /api/equipment/action` con las acciones `equip, unequip, equip_all, unequip_all, forge, forge_auto, artifact_upgrade, treasure_on, treasure_upgrade, treasure_refresh, treasure_save, treasure_discard`. Pasan 32 pruebas.

**Pendiente de equipo:** elegir la habilidad del conjunto de calidad 7 (`suit_skills` y `SUIT_SKILL`, que va en `skill_index`), el Anima Gear o Soul Equip (`SoulEquip*`, tablas `soul_equip1/2`), las skins en la ranura 7, los tesoros de reserva (`treasures`/`select_treasure`), la venta y el desguace de equipo, y las fuentes de equipo (botín de campaña). Ahora mismo el equipo solo llega por eventos, invocaciones o el modo DEV.

## Actualización 28/09/2026 — Campaña idle, botín, resultado, música, 15★/330 y visuales de chicas (Claude)

**Campaña**
- **Idle (patrulla):** `gxb2/campaign.py`. La fase actual da su `gold`, `exp_partner` y `exp_player` cada 5 s (`CampaignWindow.lua`), con un tope de 12 h (`misc.hang_up_time_max`). Además hay **botín**: cada `DROP_INTERVAL` (600 s) se tira una vez cada caja de `dropbox_ids` de la fase (pesos de `dropbox.lua` sobre 10000; `id#min#max` da una cantidad aleatoria). Así caen equipo, fragmentos, polvo, fichas, etc. **El intervalo de botín es una suposición**, porque en el original lo decidía el servidor. La barra idle muestra el acumulado en vivo, el reloj y el número de tiradas. **Collect** llama a `POST /api/campaign/action {action:'collect'}` y enseña una ventana de recompensas. El estado se guarda en `state['hang']` y el snapshot trae `hang_info`.
- **Las 530 fases** van ahora en `state.stages` (antes solo 30).
- **Ventana de resultado:** reproduce los Spine originales `battle_result/shengli_new` y `shibai_new` (texiao01 y después texiao02 en bucle, en la pista 1). En victoria enseña las recompensas y en derrota consejos con un botón "Mejorar chicas". Sale al final de cualquier `replay()`, tanto en campaña como en eventos.
- **Música y sonidos:** `GxbAudio` en `web/campaign-ui.js`. Suena `home_bg_music` en Inicio y menús, `campaign_bg_music` en campaña y torre, `battle_bg_music_1` durante el combate, `main_story_campus` en Campus/Graduate, y `battle_win`/`battle_lose` y `gain_window_sound` como efectos. Hay un botón 🔊 fijo para silenciar, guardado en localStorage. El audio arranca con el primer clic por la política de los navegadores. Los `.ogg` se convierten a MP3 con ffmpeg y el servidor responde con Range (Safari lo exige).

**Progresión hasta 15★ y nivel 330**
- **Grado:** `PARTNER_GRADEUP` cobra `grade_exp{grado+1}` y exige estar en el tope de nivel. El tope es `Partner:getMaxLev`: `grade_lv{grado+1}`, o `max_lv` en el último grado. Por debajo de 10★ el despertar suma +20 niveles (`awake_add_level_limit`). De 11 a 15★ los topes salen de `misc.hero_break_lv_cap = 260|270|290|310|330`. **Antes el tope era siempre `grade_lv1`: este era el fallo que impedía subir de nivel.**
- **De 11 a 15★:** `AWAKE_PARTNER` para chicas de 10★ usa `awake_material[despertar]` (por ejemplo `99999#51001`, es decir una 9★ cualquiera más una copia 5★) y `stone_material` como coste (`Engine.awake_recipe`). Las recetas de 6 a 10★ siguen en `ascension.json`.
- **Habilidades únicas:** `UPGRADE_PARTNER_EX_SKILL` sirve para chicas de 10★ o más con `ex_skill=1`: 4 habilidades de nivel 0 a 5 con el coste de `partner_exskill_cost` (items 198 y 199). Se guardan en `partner['ex_skills']` y el combate ya las lee.
- El roster incluye ahora `group, job, max_grade, grade_cost, next_awake, has_ex_skills` y `ex_skill_cost`.

**Ficha de chica** (`web/girl-ui.js`): fondo `college_scene{facción}`, que era el `updateBg` original y se ha recortado del relleno negro de la textura. Usa la ilustración grande `partner_picture_*` (482 imágenes en WebP, en `web/assets/pictures`, 106 MB). Si la skin previsualizada o equipada tiene retrato animado, se reproduce su Spine (`partner_picture.dragon_bone` → `girls_model.resource` → `spine/picture_web`, 274 animaciones en `web/assets/lihui`, 713 MB); solo las skins tienen animación, igual que en el original. También muestra los hexágonos de grado con el botón Grade Up, COST en MAX y las habilidades únicas con sus niveles. La pestaña **Awake** permite de 6 a 15★, con materiales elegidos automáticamente (primero los que no están en la formación y los de menor nivel).

**Graduate:** tiene el fondo de la facción, filtros de estrella redondos (5 a 10), el retrato del material elegido en cada ranura y una fila de costes con iconos, siguiendo la captura de referencia.

Archivos nuevos: `gxb2/campaign.py`, `web/campaign-ui.js/.css`, `web/girl-ui.js/.css`, `tools/extract_visuals.py` (escenas, `data/partner_pictures.json`, Spine de resultado, sonidos; con `--lihui` también los retratos animados), `tools/extract_pictures.py`, `data/exskill.json` y `tests/test_progression.py`. Pasan 36 pruebas.

**Pendiente:** Reverse / star origin (`UPGRADE_STAR_ORIGIN`), Anima Gear, elegir la habilidad del conjunto T7, efectos de sonido de cada habilidad en combate (`battle_sound_web`), voces de las chicas (`partner_sound`) y el diseño exacto de la ficha (voz CV, botones laterales, corazón). Para la ficha conviene usar `python3 tools/prefab_layout.py windows/partner_detail_window`.

## Actualización 28/09/2026 — Campaña rehecha según el original y ventana de Eventos (Claude)

**Campaña** (`web/campaign-map.js/.css`, reconstruida desde `campaign_window.prefab` y `CampaignWindow.lua`; la unidad CSS `--u` equivale a un píxel del prefab de 720 de ancho). La vista antigua sigue en el DOM pero oculta (`.panel.campaign.cmp-on`), para conservar los id que usa `app.js`.
- **Escena de patrulla (720×547):** el mapa de la fase (`set_map`, 67 mapas recortados del relleno negro en `web/assets/campaign/maps/*.webp`) con el título "2-8 Shining Band". Una sola app PIXI dibuja los **chibis Spine** de tu formación a la izquierda (delante los puestos 1–2) y los monstruos de la fase (`monsterShow`) a la derecha. Tu equipo ataca y lanza habilidades cada 1,5 s, los enemigos hacen `hurt`, y salen monedas y EXP flotando cada 5 s.
- **Barra de recursos (hang_top_group):** botones de ayuda y clasificación, `campaign_resource` con oro, EXP de chicas y EXP de jugador en vivo, y **Collect** con brillo tras una hora acumulada.
- **Mapa en zigzag (stage_scroller):** usa `StageItem`. Las fases impares van abajo (+27) y las pares arriba (−42), separadas 153 px y unidas por `route_bg`. Cada hexágono lleva su `stage_img`, el marco `stage_frame01`, el dorado `stage_frame02` para la actual o siguiente, y `stage_lock` si está bloqueada. El fondo es `campaign_select_bg`. Al tocar una fase superada se cambia la fase de patrulla (`STAGE_HANG`); al tocar la siguiente se combate.
- **Parte inferior:** el libro abre los **capítulos** (50, con nombres de `fort_text`). **Fight** (capas `recover_bg` + `recover` + `campaign_battle_01`) combate la siguiente fase y avisa si falta nivel de jugador. El regalo muestra el ritmo por hora, el botín posible (`dropbox_show`) y las tiradas pendientes. Al cerrar el resultado se vuelve al mapa y el capítulo avanza solo.
- Datos: `tools/extract_campaign.py` genera los sprites en `web/assets/campaign/`, `data/campaign.json` (imagen, nombre, monstruos y botín por fase, y capítulos) y los mapas, y completa `web/assets/battle-maps` y `battle-maps.json` con `textures/local_tex`.

**Eventos**, con el cromo de `activity_window.prefab`: fondo `fort_bg_1_up`, pestañas `nav_btn_*` de 9 cortes (bordes leídos de `CommonBtn.prefab`) y marco `activity_bg_new` (bordes 169/20/25/30). Hay tres pestañas: **Exclusives** (`ACTIVITY_NAV_TEXT_2_1`, es decir type1 2 o 7 con type2 distinto de 3), **Novato** (EventType.NEWBIE, que en el original tenía su propia entrada) y **Monthly Events** (`ACTIVITY_NAV_TEXT_2_3`, type2 3). Aparecen todos los eventos jugables y una **rotación semanal** de 5 archivados por pestaña (semana ISO como semilla), imitando cómo el servidor abría pocos eventos a la vez.

**Aviso:** el servidor calcula las listas blancas de recursos (`EVENT_ASSETS`, `EQUIP_ASSETS`, etc.) al arrancar. **Después de ejecutar un extractor hay que reiniciar el servidor.**

## Actualización 28/09/2026 — Capturas del usuario: eventos de puntos, Enroll, estadísticas, Gear, emblemas (Claude)

Trabajo guiado por capturas reales del juego que aportó el usuario.

- **Eventos de puntos** (`gxb2/point_events.py`, `data/point_events.json`): Capsule Points (13, tabla `activity_gacha`, suma con las Adv. Capsules; **10 puntos por tirada es una suposición**), Enroll Exam (16, `activity_tree`, 1 punto por Seal) y Slot Points (20, `activity_gamble`, 1 punto por tirada; la tragaperras no está reconstruida y su botón queda desactivado). `activity.round = "max|veces"`: los puntos dan la vuelta al llegar a max y cuentan una vez "Completed (x/y)". Cada nivel se entrega directamente en la Bolsa (en el original llegaba por Correo). La vista reproduce el banner (`*_bg01` + título en inglés), la franja Completed/tiempo restante/botón y los niveles "Get N point(s)" con barra `activity_bar_*` y marcas `icon_check`. El tiempo restante cuenta hasta el lunes, cuando cambia la rotación.
- **Enroll** (`web/enroll.js/.css`, `tools/extract_enroll.py`): se abre desde Campus → Enroll y desde el evento. Fondo `prophet_bg03`, la profesora es el Spine `caopi` (girls_model 5), pestañas de facción a la derecha (Ghost, Human, Monster, Fairy, Light & Dark), escritorio y carpeta de la facción, sello `prophet_icon06` con el efecto Spine `fx_yinzhang`, contador X1/X10 y la casilla "Use 10 Seals". Cada tirada usa `SUMMON` con los ids 10–14 (×1) y 17–21 (×10), según `Prophet.SUMMONMID`. Son invocaciones **de objetos** (`is_partner=0`): dan fragmentos de la caja de la facción más Portfolios (19, `award 19#10#30`). El motor ahora acepta cualquier invocación `is_partner=0`. La pestaña Exchange (ProphetReplace) sigue pendiente.
- **Estadísticas de combate:** el botón `battle_detail_icon_2` de la ventana de resultado abre Ally | Enemy con las pestañas Damage / Damage Taken / Heal, con datos de `report.hurts` (hurt/tank/heal por posición), retratos, nivel y barras.
- **Pestaña Gear** con la disposición de `partner_detail_window` (content_2): arma (−259,40), ropa (−87,118), accesorio (84,118), zapatos (250,40), tesoro (−87,−45) y antigüedad (84,−45). Botones **Unequip** (rojo) y **Gear Up** (azul, equipar lo mejor).
- **Emblemas de estrellas** (`GirlUI.stars`): 1–5 estrellas amarillas, 6–9 rojas, 10 emblema alado `potentiality_card_star` y 11–15 emblema con número; con 15★ usa la variante `_max`. Se usan en la rejilla de chicas (con las estrellas reales de la chica, incluido el despertar) y en la placa de nombre de la ficha.
- Los iconos de fragmentos en ventanas de recompensa y eventos usan ahora `itemPicture()` de la Bolsa.

**Capturas aún no implementadas (pendiente):** Elite League / Junior Varsity (arena: habría que simular rivales con bots), Personal Info con chibi y Courage/Charisma/Knowledge, página Menú (Memories, Collection, Notice…), Old Campus, Anima Gear, HUD de combate con iconos de buff y bocadillos, selección de fondo (Image) y Campus Guide (no tiene sentido sin servidor).

## Actualización 29/09/2026 — Marco fijo, Servants y Excursión (Claude, GXB2-CLAUDE-WAVE-005)

- **Tamaño fijo:** toda la app se muestra en un lienzo 9:16 de 480×853 que se escala entero a la ventana, como el cliente original (`web/frame.css/js`). Ninguna pantalla cambia ya de ancho.
- **Servants** (Inicio → Servant): lista con Tame/Train y detalles de habilidades, y ficha con fondo `pet_scene1`, Spine por grado, **Attribute** (nivel, habilidad activa, evolución) y **Servant Aura** (4 pasivas con nivel y suma de bonos). **El Servant elegido ("Llevar al equipo") combate de verdad:** el motor original recibe `petA`.
- **Excursión** (Inicio → Excursión): mapa original con los edificios animados. **Store** (oro), **Wishing Tree** (gemas) y **Food Truck** (pan): iniciar producción, recoger, mejorar y comprar Tasty Bread. **Main Center** (entrenamiento) y **Claim All**. **Explore**: 10 panes por exploración, encuentros (enemigos comunes o élite con combate real, cofres, Help Seeker, Market, Food Truck), cofres con temporizador o apertura con gemas, ranuras según nivel, subida de nivel y Auto Explore.
- Detalles, decisiones LOCAL-020…024 y pendientes en AI_WORKBOARD (handoff) y ESTADO_PROYECTO.

## Actualización 29/09/2026 — Dates, Tasks, Tiendas y Junior Varsity (Claude, GXB2-CLAUDE-WAVE-006)

- **Dates** (Inicio → Dates, o el corazón en la ficha de la chica): intimidad, regalos (favoritos, ×10, Compose), voces que se desbloquean con la intimidad, bonus y **Oath** (anillo, tope 12000). API `/api/relations/action`.
- **Tasks** (botón en la columna derecha de Inicio): **Daily Tasks** con Go/Claim y **Trophies** en cadena. API `/api/missions/action`.
- **Tiendas:** **Shopping Street** (Campus → Shopping Street) con el mapa original. **Market** (8 por página, se reinicia a medianoche, el "+" de oro abre Market), **Girls Store** (fragmentos por grupo), **Antique Store** y la ventana con pestañas (**Sanctuary, League, Guild, House Exams**; Lucky abre Slots). Tenderas Spine originales en la posición del prefab. API `/api/shops/action`.
- **Junior Varsity** (Liga → Arena): clasificación, 4 rivales, **combate real** con el motor original, puntos por banda, 2 combates gratis al día y después Arena Tickets, cartas de premio, premio diario y de temporada, y acceso a la League Store. API `/api/arena/action`.
- Extractores nuevos: `tools/extract_relations|missions|shops|arena.py`. Hay que reiniciar el servidor después de ejecutarlos. Decisiones LOCAL-025…027 en DESIGN_DECISIONS.

## Relevo entre IAs (Claude ⇄ ChatGPT) — leer antes de trabajar

Este proyecto se desarrolla por turnos entre Claude y ChatGPT. Para no gastar tokens redescubriendo cosas:

1. **Punto de entrada:** este `LEEME.md`, las secciones "Actualización …" (en orden cronológico) y `MAPA_MENUS.md`. Al terminar cada fase, añade una sección `## Actualización <fecha> — <tema> (<IA>)` con: qué funciona, archivos tocados, rutas API y qué queda pendiente.
2. **Fuentes de verdad** (solo lectura, no modificar):
   - Lógica: `~/Downloads/Decomp files/lua/app/windows/<Ventana>.lua` y `windows/activity/<Evento>.lua`. El mapa de ID de evento → clase está en `ActivityWindow.ContentClass` (≈ línea 1077 de `ActivityWindow.lua`). Los nombres de los ID están en `xyd.ActivityID` (`lua/app/common/enums.lua`, ≈ línea 708).
   - Tablas: `lua/data/tables/<tabla>.lua`, o bien `~/Downloads/Decomp files/data/data.db` (SQLite con las mismas tablas). Textos en inglés: `data/en_en.db`, en las tablas `<tabla>_text_en_en` y `translation_en_en(name, translation)` para las claves `__("CLAVE")`. **Atención:** en `data.db` las columnas de `activity` están desalineadas; usa `activity.lua`, que tiene `table.keys`.
   - Maquetación: `unity/Assets/hotres/prefabs/windows/...prefab`. Ejecuta `python3 tools/prefab_layout.py windows/activity/<prefab>` para ver el árbol con posiciones, tamaños y sprites. En NGUI el origen está en el centro del padre y la Y crece hacia arriba. El diseño base mide 720 px de ancho; en CSS se usa la unidad `--u = 100cqw/720` (ver `events.css`).
   - Imágenes: el sprite suelto con nombre `<sprite>.png` está en `~/Downloads/Decompiled/Sprites (atlases, cut)/`. Las texturas grandes están en `unity/Assets/hotres/textures/<carpeta>_web/`. Los atlas Unity sin cortar tienen RGB y alfa en archivos separados (`*_RGB.png` + `*_Alpha.png`) más el `.prefab` con `mSprites`.
3. **Receta para reconstruir un evento nuevo:** (a) busca su clase en `ContentClass` y lee solo esa ventana; (b) vuelca su prefab con `prefab_layout.py`; (c) añade tablas e imágenes en `tools/extract_events.py` y vuelve a ejecutarlo; (d) añade la regla en `gxb2/events.py` (`action` + `snapshot`) y su prueba; (e) añade la vista en `web/events.js`, añade su ID a `WORKING` y ajusta `claimable()`.
4. **Reglas del proyecto:** todo es offline, sin servidores oficiales ni credenciales. No se toca el APK ni las fuentes. Las pruebas manuales se hacen sobre una copia de la base (`--db copia.sqlite3 --http-port 9180`), nunca sobre `state/profile.sqlite3`. Los GET no deben modificar la partida.
5. **Retoque visual con fotos:** el usuario enviará capturas antiguas del juego para ajustar posiciones y estilos. Compara siempre con el prefab antes de mover nada a ojo.

### Pendiente de Eventos (orden sugerido)
- Eventos de misiones/login sencillos: `activity_level_up` (recompensas por nivel), `ACTIVITY_NEWBEE_LEESON` 202 (`activity_newbee_lesson`), Online Rewards y 7-Day Mission de Novato.
- Calendario local de eventos limitados (rotación semanal de Festivales) para simular fechas y cuentas atrás (`ACTIVITY_END_COUNT`).
- Punto rojo en el icono Eventos de Inicio cuando hay recompensas.
- Efectos de recogida (`fx_sevendays_star`, flotado de objetos) y sonidos.


## Actualización 28/09/2026 — checklist, auditoría y relevo (ChatGPT)

Se integró `GXB2_MASTER_CHECKLIST.md` junto a este LEEME sin eliminar sus apartados ni el historial del proyecto. `ESTADO_PROYECTO.md` compara las 38 secciones con documentación/código/datos/pruebas y distingue implementación, investigación, adaptación y verificación pendiente. `DESIGN_DECISIONS.md` registra sustituciones ya presentes; `AI_WORKBOARD.md` contiene claim, archivos y handoff.

**Validación actual:** 38/38 pruebas existentes y sintaxis de los diez archivos JS propios correctas; logs, inventario/hashes y sondas en `validation/audit-2026-09-28/`. Esta auditoría no añadió endpoints ni cambió reglas/partidas; no ejecutó una nueva QA visual ni un recorrido completo de campaña.

**Hallazgos para continuar:** la rotación/cuenta atrás semanal de puntos no tiene reset de estado backend; `campaign.pending` aplica la tarifa actual a todo el intervalo pendiente al cambiar fase. Se observaron en código y sondas en memoria, sin modificar la partida. Las reglas originales correspondientes requieren investigación. Prioridades, criterios y tareas sin reclamar en el informe y workboard.

**Compartir/continuar:** incluir checklist, LEEME, ESTADO_PROYECTO, DESIGN_DECISIONS, AI_WORKBOARD, VALIDACION y MAPA_MENUS junto al código/datos/runtime. Las carpetas originales externas permanecen de referencia, y la recuperación de save sigue limitada al export anónimo documentado. No confundir perfiles locales/DEV con progreso recuperado de la cuenta original.


## Capsules/huevo — GXB2-CAPSULE-EGG-009,29/09/2026
Estado [P][M], alcance probado: gacha subido, huevo1.000→1 chica5★, puntos/excedente/guardado; BFF corregido a corazones11 y SUMMON15/16 (10/100), BAODI separado en12/SUMMON9.90/90 pruebas y20 JS válidos. Se preservan saldos; no se recalcula historia. VIP3 original documentado y omitido en Reborn según petición; FX/espacio pendientes. [Evidencias y handoff](validation/capsule-egg-2026-09-29/README.md), [cuatro referencias](docs/references/2026-09-29-c/README.md). Fuentes/saves usuales intactos; servidor habitual no detenido. Cargar el backend nuevo requiere reiniciarlo y recargar navegador.


## Actualización 29/09/2026 — Guild Lab (ChatGPT, GXB2-GUILD-LAB-010)

Estado global Guild `[P][M]`; laboratorio con80 mejoras originales/5clases/2páginas, costes/prerrequisitos/máximos, guardado y reset gratuito primero/pagado después. Acceso Inicio→Gremio→Territorio→Laboratorio. Bonos conectados a atributos y combate Lua original según clase. Pantalla cotejada con la captura original Lab y prefab.99/99 pruebas (9 nuevas), QA temporal separada, sprites requeridos recuperados. APIs originales `GUILD_GET_SKILLS`, `GUILD_UPGRADE_SKILL`, `GUILD_RESET_SKILL` en `/api/action`.

[Evidencia, diferencias y handoff](validation/guild-lab-2026-09-29/README.md) · [6 capturas originales](docs/references/2026-09-29-d/README.md). Pendientes: economía/membresía/actividades Guild, cascada de reset original, FX/audio; regalos/Oath/dificultades capturados archivados, sin declarar completos por imagen. Sin moneda gratis en normal; DEV permite explorar Lab con moneda4. Fuentes y saves habituales preservados. Reiniciar servidor habitual y recargar para nuevo backend.


### Lab centrado — GXB2-GUILD-LAB-011,29/09/2026
La ventana Lab se centra automáticamente entre barra y navegación, también en avanzado. Ajuste exclusivamente visual verificado, márgenes65.918/65.907px en QA temporal9230. [Evidencia y handoff](validation/guild-lab-centered-2026-09-29/README.md); [referencias nuevas](docs/references/2026-09-29-e/README.md). No cambia el alcance parcial de Guild ni las reglas; hooks Claude WAVE010 intactos.


### Lab: flechas de páginas — GXB2-GUILD-LAB-012,29/09/2026
Flecha derecha Básico→Avanzado, izquierda Avanzado→Básico y dos puntos inferiores reemplazan pestañas de texto. Sprites originales, centrado automático y clase conservados; QA de ida/vuelta correcta, sin gasto. Sigue pendiente transición original0.4s/FX; se conserva consulta de requisitos avanzados antes del desbloqueo. [Evidencia/relevo](validation/guild-lab-arrows-2026-09-29/README.md).


### Territorio del gremio y hover Lab — GXB2-GUILD-UI-013,29/09/2026
Mapa con cinco edificios/posiciones del prefab original, fuente, rótulos y comerciante yuanshu animada; canvas ajustado a densidad de pantalla. Corregida sustitución del transform de centrado de nodos/flechas por hover global. Merchant abre tienda Guild y vuelve al territorio. QA visual/navegación sin gasto y sintaxis JS correctas; ensayo físico de hover pendiente de confirmación manual. Guild global sigue parcial: actividades/membresía y FX ambientales pendientes. [Evidencia, fuentes y relevo](validation/guild-ui-2026-09-29/README.md). Sin cambios en backend ni saves habituales.

## Café y vestuario — GXB2-HOUSE-DRESS-014 (29/09/2026)
Campus → Life → Dorm / Outfit / Outfit Store. House permite editar y guardar muebles, comprarlos por serie, seleccionar chicas y abrir el segundo piso. Outfit guarda hasta cinco piezas propias con preview animado. La tienda de atuendos está reconstruida visualmente; sus tiradas siguen pendientes. Normal empieza con la dotación original; la muestra Café de QA tiene stock temporal. [Evidencia y handoff](validation/house-dress-2026-09-29/README.md). Reiniciar el servidor habitual y recargar para cargar el nuevo backend.


## Recuperación original — tanda050, 2026-09-30

[R][P] Android auditado: 31 formaciones anónimas, 62 chicas sin identificar y preferencias; no contiene roster/inventario completo y no permite migración jugable. Herramientas de auditoría y lector de índice de respaldo iPad implementados, con 5 pruebas específicas aprobadas. El usuario conserva la app en iPad, pero falla por conexión. Próximo paso: obtener respaldo Finder y comprobar archivos de la app. Importación completa sigue pendiente; no se tocó la partida habitual. [Evidencia](validation/original-save-2026-09-30/README.md).

## Recuperación completa de tablas — 01/10/2026

[Tablas recuperadas](TABLAS_RECUPERADAS.md): 904/904 tablas originales, 202.878 filas en segmentos, 252 tablas inglesas y ocho dossiers de sistemas. Datos y manifest en `data/recovered/`; extractor reproducible en `tools/recover_client_tables.py`. Recuperación documental completa de estas fuentes; la integración jugable sigue siendo parcial. No cambia reglas ni partidas.

## Growth Diary — 01/10/2026

Nuevo botón en Inicio tras la fase 5: 40 capítulos / 160 misiones, 121 con seguimiento local, reclamación única y guardado. [Alcance y 39 objetivos pendientes](GROWTH_DIARY.md). Reinicia el servidor para cargarlo.
