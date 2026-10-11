# AI Workboard — GxB2 Reborn

## GXB2-DISTRIBUTION-088 — ChatGPT, 2026-10-02
Status: [D:GPT] Código de la entrega preparado: avances069–087, 374 tests OK, 71 JS válidos y 6108 voces verificadas. 36697 archivos versionados; partidas, referencias, pruebas y work excluidos. Notas DISTRIBUCION_2026-10-02.md. ZIP se genera desde el commit de esta entrega; hash y confirmación de push se registran en el cierre del chat.


## GXB2-BATTLE-087 — ChatGPT, 2026-10-02
Status: [D:GPT] Formación compartida bajada 200/1920 con HP, estados y efectos ligados a los mismos anclajes. Rótulos nativos VICTORY/DEFEAT en inglés añadidos al resultado junto a animaciones existentes. QA visual Campaign2-8 seis vs cinco, ambos resultados y carga assets200 en59074. Sintaxis/diff check OK; partida sin modificar. Documento BATALLAS_CENTRADAS_087.md y tres capturas en outputs. Reservas liberadas.


## GXB2-TESTS-086 — ChatGPT, 2026-10-02
Status: [D:GPT] Tests recreado con pisos nativos, chibis, aviso de hito, ventana Enemy/Reward/Fight y KEEP OUT en pisos superados. Backend rechaza repetir pisos completados. Visor compartido de eventos ocupa pantalla completa, Continue vuelve al origen, carga Tests con barra de nueve cortes. QA copia independiente nivel413/414, bloqueo y replay; prueba de progreso/recompensas/fichas pasó. Capturas y documento TESTS_PANTALLA_COMPLETA_086.md. Sin cambios en partida principal por QA. Reservas liberadas.


## GXB2-PROFILE-067 — ChatGPT, 2026-09-30
Status: [D:GPT] Selector Avatares sin rótulos ni tooltips por tile (aria-label preservada), 5 columnas, bordes redondeados, preview/Cambiar arriba y lista con scroll independiente. QA desarrollador Chicas:409 opciones,0 captions,5 columnas iguales; captura avatar-picker-clean.png. Sin aplicar cambio de avatar. Reservas hooks app.js/profile-senpai.js/CSS/docs liberadas.


## GXB2-PROFILE-066 — ChatGPT, 2026-09-30
Status: [D:GPT] Dígitos VIP con altura20px y ancho nativo; marco/avatar88px reales. VIP/nombre comparten altura32px y avatar/firma88px. ID separado debajo. QA navegador midió mismas coordenadas y alturas por fila, ambos dígitos iguales, frame contenido e ID sin solapamiento. Captura profile-rows-aligned.png. Reservas CSS/docs liberadas.


## GXB2-PROFILE-065 — ChatGPT, 2026-09-30
Status: [D:GPT] Corona, VIP y dígitos originales en original-ui/profile-vip. Badge/avatar con el mismo centro comprobado en navegador, ID/gremio en fila propia, botones sin margen heredado y EXP centrada en barra. Beneficios VIP abre/cierra sin desplazar rejilla. QA desarrollador y carga de todos los sprites OK; captura profile-vip-aligned.png. Reservas liberadas profile-senpai.js/skin-collection.css/assets/docs.


## GXB2-ASSISTANT-064 — ChatGPT, 2026-09-30
Status: [D:GPT] Inicio compacto, asistente superior y avisos reales. Perfil flotante con chibi/radar, edición existente preservada, VIP desplegable y Wallpaper en Ajustes. Posición final top16%/bottom14%, entre avatar y navegación. QA visual desarrollador y editar nombre sin guardar, pruebas de señales y 2 tests Assistant OK. Reservas liberadas game-assistant.js/app.js/profile-senpai.js/skin-collection.css/docs. Ventana ga2 preexistente preservada; no ejecutar automatización ni tocar girl-ui/servant/excursion. Capturas validation/assistant-2026-09-30/.


## GXB2-GRADUATE-063 — ChatGPT, 2026-09-30
Status: [D:GPT] ALL y filtro exclusivo reemplazan multiselección por indicación nueva. Revisión de base/materiales oculta, abierta sólo desde tarjetas y cerrada con Listo. QA 5→6→ALL y abrir/cerrar OK. Reservas liberadas app.js/graduate.css/docs. Servidor 9242 activo, misma partida de QA desarrollador, ninguna graduación realizada.

## GXB2-GRADUATE-062 — ChatGPT, 2026-09-30
Status: [D:GPT] Ayuda visual original integrada, notas en español, tarjetas abren selector y copias usadas excluidas de otros huecos. QA desarrollador: cuatro materiales distintos completan receta sin ejecutar Graduate. Reservas liberadas app.js/graduate.css, asset original-ui/graduate/help-reference.png y docs.

## GXB2-GRADUATE-061 — ChatGPT, 2026-09-30
Status: [D:GPT] Referencia aplicada: filtros emblema+número, tres líneas con preview real read-only y auto-selección 5★ on/off. Reservas liberadas app.js/index.html/graduate.css, método acotado engine.py, ruta server.py, tests/docs. Diez pruebas Python + auto-selección JS + filtros OK. QA desarrollador separado; ningún Graduate ejecutado. Servidor 9240 reiniciado con la misma base de datos para habilitar preview.

## GXB2-POLISH-060 — ChatGPT, 2026-09-30
Status: [D:GPT] Tanda de pulido comprobada. Reservas liberadas: web/graduate.css, app.js/index.html, tools/extract_pictures.py, picture-layouts y docs/QA. Tarjetas de skins por copia, Galería con 323 tarjetas originales, Graduate encuadrado y Menú con navegación visible/operativa. 13 tests específicos y orden/filtros OK. QA separado en modo desarrollador; guardados habituales intactos. Pendiente revisión del resto de referencias. girl-ui.js, Dates y Excursiones de Claude intactos.


## GXB2-PORTRAITS-059 — ChatGPT, 2026-09-30
Status: [D:GPT] Cayla/Kitty recuperadas,537 assets con índice coherente, QA navegador de ambas y orden/filtros OK. Reservas liberadas: extractor, pictures, app.js y docs. Referencias4311 inventariadas; falta revisión visual completa. girl-ui.js y partidas habituales intactos.

## GXB2-GRADUATE-058 — ChatGPT, 2026-09-30
Status: [D:GPT] Filtros verticales y estrella naranja original de10★ comprobados en navegador; reservas liberadas: app.js/graduate.css; docs.

## GXB2-GRADUATE-057 — ChatGPT, 2026-09-30
Status: [D:GPT] Filtros on/off, lista sin duplicados y marcadores aplicados; prueba de orden/filtros y QA navegador OK. Reservas liberadas: app.js/graduate.css/index.html; docs.

## GXB2-GRADUATE-056 — ChatGPT, 2026-09-30
Status: [D:GPT] Iconos del gacha, estrellas de destino y disponibilidad según chicas/recursos; QA visual comprobado. Reservas liberadas: graduate.css y app.js; documentación.

## GXB2-GRADUATE-055 — ChatGPT, 2026-09-30
Status: [D:GPT] Referencia visual Graduate aplicada y comprobada en navegador; reservas liberadas: graduate.css y hooks acotados app.js/index.html; documentación.

## GXB2-GRADUATE-054 — ChatGPT, 2026-09-30
Status: [D:GPT] Graduate UI y ruta local 1–3★ hasta10★ completadas; 318 pruebas OK y QA en partida temporal. Reservas liberadas: gxb2/local_promotion.py, tests/test_local_promotion.py, web/graduate.css; cambios acotados engine.py, battle.py, runtime/battle_host.lua, app.js, girl-ui.js, server.py, index.html y docs. No modificar fuentes ni partidas habituales.

## GXB2-EVENTS-053 — ChatGPT, 2026-09-30
Status: [D:GPT] Firework Project 196 implementado, 311 pruebas OK; reservas liberadas. Reservados tools/extract_firework_project.py, data/firework_project.json, gxb2/firework_project.py, web/firework-project.js/.css, web/assets/firework-project, tests/test_firework_project.py. Hooks acotados engine/server/events/index y documentación. Fuentes y partidas habituales intactas.

## GXB2-EVENTS-052 — ChatGPT, 2026-09-30
Status: [D:GPT] Jigsaw 37 y Puppet Parade 189 implementados y verificados; reservas liberadas. Reservados tools/extract_puzzle_events.py, data/puzzle_events.json, gxb2/puzzle_events.py, web/puzzle-events.js/.css y assets/puzzle-events, tests/test_puzzle_events.py; hooks acotados engine.py/server.py/events.js/index.html y documentación. Partidas habituales/fuentes intactas. Recuperar reglas/costes/premios originales y documentar suministro local.


## GXB2-IOS-RECOVERY-051 — ChatGPT, 2026-09-30
Status: [T][R][P] análisis finalizado; reservas liberadas. Sin importación jugable: no se encontró roster/inventario completo. Reservados tools/recover_imazing_save.py, tests/test_imazing_recovery.py, validation/ios-save-2026-09-30/ y documentación de recuperación. Original en Documents/seguridad copia intacto; no tocar saves habituales. Objetivo: comprobar roster/inventario antes de cualquier importación. Handoff: tools/recover_imazing_save.py genera informe anónimo por cuenta; 3 tests OK y reporte real en validation/ios-save-2026-09-30/report.json. Son cuatro cuentas, sin duplicar IDs numéricos/texto; no importar snapshot especial de Guild Competition. Original y saves habituales intactos. Próxima fuente: exportación del iPad.


## GXB2-RECOVERY-050 — partida original (ChatGPT, 2026-09-30)
Status: [T][R][P] investigación Android y herramientas terminadas; reservas liberadas. Migración pendiente del respaldo iPad.
Owner: ChatGPT. Archivos reservados: `tools/recover_original_save.py`, `tools/inspect_ipad_backup.py`, `tests/test_original_save_recovery.py`, `validation/original-save-2026-09-30/`, documentación de checklist/estado/validación/LEEME y este workboard. `real_save_export/`, fuentes Android/Downloads y saves habituales permanecen intactos.
Objetivo: identificar qué progreso real está en la copia Android, excluir credenciales y datos de cuenta, y generar una migración separada únicamente si hay IDs/conteos comprobables. No inferir propiedad de assets ni inventar un roster a partir de formaciones.

Handoff: 5 pruebas específicas OK; informe Android real en validation/original-save-2026-09-30/report.json. No hay roster/inventario recuperable en esa copia. Usuario conserva app iPad que falla por conexión; respaldo Finder pendiente. tools/inspect_ipad_backup.py solo lista dominios candidatos, detecta cifrado y no extrae datos. No se alteraron fuentes ni guardados habituales.


## GXB2-CHECKLIST-CHIME-049 (ChatGPT, 2026-09-30)
Status: [T] cerrado 2026-09-30; bloqueo de archivos liberado. Las tres entregas tienen pruebas de alcance, no cierran sistemas globales.
Owner: ChatGPT. Archivos reservados: `GXB2_MASTER_CHECKLIST.md`, `ESTADO_PROYECTO.md`, `AI_WORKBOARD.md`, `gxb2/battle.py`, `gxb2/engine.py`, `gxb2/chimes.py`, `tools/save_archive.py`, pruebas específicas y `VALIDACION.md`. No modificar los archivos de otra tanda activa.
Objetivo: actualizar el checklist con la evidencia de WAVE-019–048, evitar que la partida cargada por una petición cambie el bonus de combate de otra y permitir copia/restauración en ruta nueva sin tocar el save habitual. Validar sobre partidas temporales.

Handoff: la sección 40 del master y el encabezado de ESTADO_PROYECTO son el estado vigente. `battle.CONTEXT` desapareció; Engine pasa `chimes.bonus(state)` a los 3 cálculos de atributos y 15 rutas de combate. `tools/save_archive.py` usa SQLite online backup, comprueba integridad/estructura y publica un solo archivo en destino nuevo sin sobrescribir. Tests: 274/274, con pruebas específicas para dos partidas y para copia WAL/restauración/rechazos. `VALIDACION.md` detalla alcance. No se tocó la partida habitual. Pendientes: migraciones, import original, restauración UI, corpus amplio de combate y calendario de eventos.


Leer [GXB2_MASTER_CHECKLIST.md](GXB2_MASTER_CHECKLIST.md) y [LEEME.md](LEEME.md) antes de reclamar tareas. Los bloqueos siguientes son de coordinación; confirmar que siguen vigentes antes de editar. No se detectó un workboard previo en esta carpeta; esto no prueba que no existan sesiones externas.

## GXB2-DOC-AUDIT-001
Status: [X] — auditoría documental terminada; no certifica sistemas del juego
Owner: ChatGPT
Started: 2026-09-28
Goal: integrar el checklist aportado, comparar documentación/código/pruebas y registrar estado verificable y prioridades sin alterar reglas del juego.

Files touched (bloqueos liberados al terminar):
- AI_WORKBOARD.md
- GXB2_MASTER_CHECKLIST.md (copia nueva junto a LEEME)
- LEEME.md (añadidos y aclaraciones, conservar historial)
- VALIDACION.md (nuevo registro de auditoría)
- MAPA_MENUS.md (aclaraciones de estado)
- ESTADO_PROYECTO.md (nuevo informe de evidencia y cobertura)
- DESIGN_DECISIONS.md (registro nuevo de sustituciones ya existentes; no cambiar reglas)
- validation/audit-2026-09-28/ (logs nuevos de verificación)

Dependencies:
- Checklist adjunto recuperado de la conversación, SHA256 fd04ca6ee675e7acc5a1a8f15daa39e984660416c76fa0d2546e627a94b62e5e.
- Proyecto localizado en /Users/schroyle/Documents/Codex/2026-09-26/referenced-chatgpt-conversation-this-is-an/outputs/gxb2_local (carpeta sin .git).

Findings:
- /mnt/data no existe en este equipo. Las copias de Downloads y el adjunto recuperado son idénticas.
- sources/ del espejo ChatGPT está vacío; no se modifica.
- LEEME contiene afirmaciones históricas superadas por actualizaciones posteriores; no usar una sola lista antigua como estado actual.

Completed: 2026-09-28
- Checklist integrado junto a LEEME, original conservado íntegramente.
- LEEME, VALIDACION y MAPA_MENUS conservados íntegramente con aclaraciones actuales.
- ESTADO_PROYECTO cubre las 38 secciones y todos los milestones, con estado/evidencia/limitaciones.
- DESIGN_DECISIONS registra adaptaciones ya presentes; ningún cambio de reglas.
- 38 pruebas existentes aprobadas, sintaxis de diez JS correcta, inventario y sondas en memoria registrados.
- Enlaces relativos y hashes de código comprobados; no hay tarea de implementación activa de esta auditoría.

Next step:
- Reclamar GXB2-TIME-001 o coordinar su alcance con GXB2-EVENT-RESET-001 y GXB2-IDLE-SETTLE-001; prioridades/criterios en ESTADO_PROYECTO.



## HANDOFF — GXB2-DOC-AUDIT-001
From: ChatGPT
To: Claude, ChatGPT, Nava o siguiente responsable
Status: [X] para documentación; reconstrucción del juego [P]
Date: 2026-09-28

Completed:
- Integración sin borrar información; enlaces cruzados y roles de cada documento.
- Estado real basado en código/datos/tests, separado de investigación y de sustituciones offline.
- Hallazgos y tareas estables; no dependen de chats antiguos.

Verified:
- 38/38 pruebas sobre sus bases temporales; ver validation/audit-2026-09-28/unittest.txt.
- Diez JS propios pasan sintaxis; 38 secciones cubiertas; enlaces locales resueltos.
- Todos los textos originales de checklist, LEEME, VALIDACION y MAPA_MENUS están preservados; ver document-provenance.json.
- Los hashes de código/tests coinciden con inventory.json al cerrar la auditoría.
- Sondas en memoria confirman aplicación de tarifa idle actual y ausencia de periodo/reset de puntos.

Not verified:
- Navegador actual, all-model/skill/recipe coverage, campaña completa, economía sin DEV.
- APK/Unity, instalación portable, migraciones/restore integral, timers/resets globales.
- Nuevo análisis de game.db o import del progreso original; export anónimo previo sigue siendo la referencia limitada.

Files changed:
- LEEME.md, VALIDACION.md, MAPA_MENUS.md (solo añadidos/aclaraciones, historial íntegro).
- GXB2_MASTER_CHECKLIST.md, ESTADO_PROYECTO.md, DESIGN_DECISIONS.md, AI_WORKBOARD.md (nuevos).
- validation/audit-2026-09-28/: unittest.txt, javascript.txt, inventory.json, probes.txt, document-provenance.json, document-checks.txt.

Do not change:
- sources/ del espejo ChatGPT, APK, fuentes de Downloads, export original y partidas habituales.
- No tomar los modelos/skins instalados como propiedad ni el save local/DEV como cuenta original recuperada.
- No modificar reglas originales o sus tablas para solucionar balance antes de documentar la evidencia y una capa de diseño aparte.

Recommended next action:
- Leer checklist → este workboard → LEEME → ESTADO_PROYECTO.
- Elegir y reclamar una tarea con archivos/dependencias; no hay bloqueos activos de esta auditoría.
- Prioridad P0: contrato de tiempo, periodo de eventos de puntos y liquidación idle al cambiar fase. Investigar primero comportamiento original.
- Para QA manual: usar copia/partida temporal y puertos distintos (por ejemplo `python3 server.py --db /ruta/temporal/qa.sqlite3 --http-port 9180 --tcp-port 9181`). Iniciar.command detiene procesos server.py por nombre; evitarlo durante QA.
- Tras ejecutar extractores autorizados en futuras tareas, reiniciar solo el servidor de pruebas: las listas blancas de assets se calculan al arrancar.

## GXB2-RECON-WAVE-001
Status: [T] — tanda implementada y verificada en alcance descrito; sistemas globales [P]
Owner: ChatGPT
Started: 2026-09-28
Goal: reconstruir una primera ampliación funcional desde fuentes originales: Exchange/Slots y recompensas sencillas cuando sus datos permitan reproducirlas; estabilizar periodos de eventos/idle con decisiones explícitas y pruebas. No completar por apariencia.

Files claimed during work (bloqueos liberados al cierre):
- gxb2/clock.py, gxb2/campaign.py, gxb2/point_events.py, gxb2/events.py, gxb2/home_systems.py, gxb2/engine.py
- gxb2/acquisition.py, data/acquisition.json, tools/extract_acquisition.py (nuevos si la investigación lo permite)
- web/assets/slots/ (copias nuevas de sprites originales)
- web/girl-ui.js (excluir materiales protegidos), bloqueo manual de chicas mediante LOCK_PARTNER
- server.py, web/enroll.js, web/enroll.css, web/slots.js, web/slots.css, web/app.js, web/index.html, web/events.js
- tests/test_local_backend.py (reloj fijo para comparar snapshots), tests/test_reconstruction.py, tests/test_progression.py (si cambian expectativas documentadas)
- LEEME.md, GXB2_MASTER_CHECKLIST.md, ESTADO_PROYECTO.md, DESIGN_DECISIONS.md, VALIDACION.md, AI_WORKBOARD.md
- validation/reconstruction-2026-09-28/, tools/extract_events.py, data/events.json

Dependencies:
- Fuentes Lua/tablas/prefabs/assets de Downloads, exclusivamente lectura.
- QA y ejecución sobre partidas temporales y puertos separados, sin detener el servidor habitual.

Findings:
- ProphetReplace está dentro de ProphetWindow.lua; tablas SQLite Gamble desplazadas, usar claves Lua.
- Backend servidor no recuperado: selección/refresh/calendario/liquidación son adaptaciones explícitas.
- NewLevelUpGiftBag es de pago, no se implementó como regalo gratis.
- Contratos, fuente/hash y unknowns en validation/reconstruction-2026-09-28/RESEARCH.md.

Completed: 2026-09-29 (hora local; iniciado el 28/09)
- Exchange: costes/pool/filtros, propuesta persistente, guardar/descartar, campos wire de reapertura.
- Slots Normal/High Stakes: premios/tiradas/gates/costes, coupons/puntos, límites/refresh/historial/persistencia, assets originales e iconos complementarios.
- LOCK_PARTNER: flag manual original, protección de materiales y de propuestas Exchange.
- Reloj Engine inyectable, reset semanal de puntos y liquidación idle por fase histórica.
- 47 pruebas y once JS correctos; QA visual con keyboard sobre base temporal, límites de click/touch documentados.
- Documentos/handoff actualizados; no hay bloqueos activos de esta tanda.

Next step:
- Reclamar GXB2-SAVE-001 o GXB2-LUCKY-001 según prioridades actuales de ESTADO_PROYECTO; no reutilizar el objetivo antiguo de la auditoría.


## HANDOFF — GXB2-RECON-WAVE-001
From: ChatGPT
To: Claude, ChatGPT, Nava o siguiente responsable
Status: [T] para operaciones verificadas; [P][M] para fidelidad/sistemas completos
Date: 2026-09-29 (cierre local)

Completed:
- Lo descrito en la tarea; rutas Campus→Enroll→Exchange y Campus→Slots, evento Slot→máquina y Chicas→detalle→lock.
- Investigación diferenciada de implementación; tablas originales intactas y decisiones LOCAL-013–017.

Verified:
- 47/47 en validation/reconstruction-2026-09-28/tests.txt; once JS en javascript.txt.
- UI por teclado: Normal1/10 y premio/coste; High Stakes1 y restricción de10; Exchange→reload→save; lock; capturas en esa carpeta.
- Bases temporales; QA Normal nivel80 con recursos de fixture, no DEV. Servidor de QA detenido; no se tocó el servidor habitual.
- Hashes finales, assets y fuentes en inventory.json/data/acquisition.json. Carpeta sin Git; no hay commit ni PR.

Not verified / partial:
- Click/touch en navegador habitual, todas las resoluciones/iconos/pools/recetas, estadística/pity/cool.
- Lucky Store (solo22 filas recuperadas); animación de la máquina; UI probabilidades y variantes Exchange.
- Calendario oficial/semántica servidor, todos los resets, economía sostenible y restore/migración integral.
- APK sigue sin conectar. No marcar sistemas completos por la UI o por estos tests.

Files changed (definitivos):
- gxb2/engine.py, campaign.py, events.py, point_events.py; nuevos clock.py y acquisition.py.
- tools/extract_acquisition.py, data/acquisition.json, web/assets/slots/.
- server.py; web/app.js, girl-ui.js, enroll.js, enroll.css, events.js, index.html; nuevos slots.js y slots.css.
- tests/test_local_backend.py (reloj fijo), tests/test_reconstruction.py (nuevo).
- LEEME, ESTADO_PROYECTO, MASTER_CHECKLIST, DESIGN_DECISIONS, VALIDACION, MAPA_MENUS, AI_WORKBOARD y validation/reconstruction-2026-09-28/.
- home_systems.py, extract_events.py, data/events.json y test_progression.py se reclamaron preventivamente pero no cambiaron; comparar manifiesto contra auditoría.

Do not change:
- sources/ del espejo, Downloads, APK/export ni state/profile.sqlite3/DEV. No usar Iniciar.command durante QA, detiene procesos por nombre.
- No identificar la fixture/capturas como cuenta original. No atribuir reglas LOCAL al servidor oficial.
- No borrar texto histórico para ocultar cambios; encabezados actuales indican qué reemplaza cada pendiente.

Recommended next action:
- Master → workboard → LEEME → estado → RESEARCH. Reclamar archivos antes de editar; todos los bloqueos de esta tanda liberados.
- Lucky Store: investigar LuckShopWindow/Shop, límites y refresh con shop_luck. Backup/restore primero sobre copias.
- Para relanzar QA: crear fixture nueva o usar qa-db-path.txt si aún existe, python3 server.py --db RUTA_TEMPORAL --http-port9180 --tcp-port9181. Las bases temporales no son dependencia portable; recrearlas con tests. Reiniciar solo servidor QA después de añadir assets.
- Snapshots de código anterior disponibles en before/ solo para los archivos que allí figuran; no son backup completo del proyecto.
- El usuario puede aportar capturas/recursos puntuales; no hace falta pedirlos para los contratos ya recuperados. Pedir pantallas concretas para afinar fidelidad visual cuando haya dudas.


## GXB2-REF-UI-002
Status: [T][P] — referencias integradas y UI contrastada; límites de verificación pendientes
Owner: ChatGPT
Started: 2026-09-29
Goal: preservar nueve capturas aportadas; contrastar versiones/reglas; ajustar Exchange vertical con chibis originales y texto de rondas en eventos sin sustituir datos originales por capturas de otra edición.
Files changed (bloqueos liberados): docs/references/2026-09-29/, web/slots.js, web/slots.css, web/enroll.js, web/enroll.css, web/events.js, LEEME.md, ESTADO_PROYECTO.md, GXB2_MASTER_CHECKLIST.md, AI_WORKBOARD.md, VALIDACION.md, validation/reference-ui-2026-09-29/.
Dependencies: fuentes y partidas originales solo lectura; QA temporal.


## HANDOFF — GXB2-REF-UI-002
From: ChatGPT
To: Claude, ChatGPT, Nava
Date: 2026-09-29
Completed:
- Nueve adjuntos copiados intactos con SHA256 y notas imagen por imagen.
- Aclaración del usuario: selector de Slots permite50 tiradas por 40; fuente GambleWindow muestra ciclo10/20/50 e índices2/4/5. Normal usa dos botones y palanca; High Stakes1/10 sin palanca. Cambiar cantidad no gasta.
- Exchange vertical: tarjetas+chibis, resultado arriba/actual abajo; cancelación de montajes obsoletos.
- Texto de rondas Slot Points deriva del estado. Variante5 de captura no sustituye8 recuperada.
Verified: 47/47 backend tests, once JS, geometría/chibis/selector y costes mostrados; capturas y hashes en validation/reference-ui-2026-09-29/.
Not verified: click/touch habitual; persistencia visual de preferencia tras recarga (carga incompleta en herramienta); compra50 E2E visual; todos los modelos/resoluciones/GPU stress. No declarar esos casos completos.
Do not change: sources/, Downloads, APK, saves habituales; no usar las cifras/roster de capturas como progreso importado. No confundir Holiday Break Exchange con ProphetReplace.
Next: fuente/version de premios5 vs8; dealer/Skip/probabilidades/reloj vivo/Shop Slots; contratos Holiday/Atelier/Entrance/Voice antes de implementarlos. Leer docs/references/2026-09-29/README.md con unknowns y referencias exactas. No hay bloqueos activos de esta tarea. Servidor QA propio cerrado.


## GXB2-REF-003
Status: [X] para archivo/investigación acotada; dealer web [ ]
Owner: ChatGPT
Started: 2026-09-29
Goal: preservar décima captura High Stakes y localizar assets originales; investigación, sin alterar reglas o partidas.
Files changed (bloqueos liberados): docs/references/2026-09-29/, AI_WORKBOARD.md, GXB2_MASTER_CHECKLIST.md.

Completed: 2026-09-29
- Captura10.jpg preservada; manifest tiene10 imágenes con SHA256.
- Fuentes precisas de ambos dealers localizadas; tabla/window y8 recursos originales con hashes.
- Investigación registrada; no hubo cambio de código/datos/economía, extracción de Spine ni verificación del render original.
HANDOFF: leer README de referencias, sección Décima captura, y slots-original-assets.json. Reclamar tools/extract_visuals.py o extractor dedicado, web/assets/spine/, server.py y slots.js/css para exportar/montar ambos con cancelación de carga. Usar partida temporal. No inferir cifras/pools desde píxeles borrosos ni reconstruir imágenes con IA. Nuevos hashes de documentos sustituyen los de la tarea visual previa; manifiestos anteriores son históricos. No hay bloqueos activos.


## GXB2-SLOTS-LUCKY-004
Status: [P][M] — implementación acotada y QA cerrados; fidelidad global pendiente
Owner: ChatGPT
Started: 2026-09-29
Goal: exportar dealers originales; Lucky Store transaccional; controles, probabilidades, Skip y reloj vivo de Slots. Separar contrato cliente y sustitución del servidor.
Files changed (bloqueos liberados): gxb2/acquisition.py, gxb2/engine.py, server.py, tools/extract_acquisition.py, tools/extract_slots_dealers.py (nuevo), data/acquisition.json, web/assets/slots/, web/assets/spine/gamble_girl/, web/assets/spine/gamble_up_girl/, web/slots.js, web/slots.css, web/events.js, tests/test_reconstruction.py, LEEME.md, ESTADO_PROYECTO.md, GXB2_MASTER_CHECKLIST.md, VALIDACION.md, DESIGN_DECISIONS.md, AI_WORKBOARD.md, validation/slots-lucky-2026-09-29/.
Dependencies: fuentes read-only; saves originales intocados; pruebas en SQLite temporal y puertos propios.


## HANDOFF — GXB2-SLOTS-LUCKY-004
From: ChatGPT
To: Claude, ChatGPT, Nava
Date: 2026-09-29
Completed:
- Dealers Normal gamble_girl / High Stakes gamble_up_girl exportados de Spine original y montados con idle; cancelación de cargas obsoletas y destrucción al salir. Exportador independiente tools/extract_slots_dealers.py, fuentes/output SHA256 en dealers.json.
- Lucky Store3: GET_SHOP_INFO432/REFRESH_SHOP433/BUY_SHOP_ITEM434, ocho ofertas, nivel14, Coupons, límite1/casilla y refresh24h/50 Coupons. Guardado/reinicio/rollback, snapshot puro y clamp de reloj. Otros shop_type rechazados; login general sigue siendo adaptador parcial.
- UI: Shop/Records originales como botones, tienda operativa, High sin Shop/palanca, Skip por modalidad, reloj vivo, probabilidades locales explícitas, Go to Slot Points20. Highlight web local breve; no confundir con FX originales completos.
Verified:
-49/49 tests (tests.log) y11 JS. Casos nuevos Lucky: coste/límite/fondos/protobuf/reinicio/refresh/IDs/booleanos/rollback.
- QA fixture normal nivel80/VIP3, sin DEV:50 tiradas por40 tickets, +500 Coupons/+50 puntos; compra50 Red Antique shards por10000 Coupons y sold out; dealer de ambos visible; Skip/bulk50 persisten recarga; navegación a puntos20. Contadores vivos. Capturas/resultados en validation/slots-lucky-2026-09-29/.
Limitations:
- Fuente de muestreo/server calendar de Lucky no recuperada. Ocho filas distintas ponderadas y refresh manual al vencer son LOCAL-018, sin reinterpretar limit_num como fórmula original. UI Lucky conserva fondo Slots/grid web; falta ShopWindow original.
- Skip/preferencia están en localStorage por origen, no SQLite. Efectos talk/speak/texiao exportados pero solo idle usado; voces originales no montadas; cool/pity/desgaste pendiente.
- Clic/check de herramienta irregular; teclado Return/Space fiable. Primera carga Failed to fetch resuelta con recarga. No certificar touch/GPUs/resoluciones ni todos los modelos.
- Primera importación de extract_visuals regeneró legacy catalog/icons/cards/skills por efecto lateral de extract_inventory_assets. Nuevo extractor ya no importa generadores.130 assets con hashes históricos iguales; resto no tenía manifest histórico completo. No usar extract_visuals como librería hasta eliminar import con efecto lateral.
Do not change:
- sources/ espejo, Downloads, APK/export, state/profile.sqlite3 ni DEV habitual. No usar Iniciar.command para QA; detiene servidores por nombre. Servidor habitual no detenido.
Next:
- Checklist → workboard → LEEME/estado actualizado → validation/slots-lucky-2026-09-29/RESEARCH.md. Reclamar una tarea concreta; todos los bloqueos de004 liberados.
- Prioridad backup/restore/migraciones sobre copias; después contratos Holiday/Atelier/Entrance y fidelidad/audio/FX. No llamar todo el juego terminado.
- Fixture temporal localizada por qa-db-path.txt, no parte del paquete portable. Tests la recrean. Servidor/pestaña QA propios cerrados al entregar. No reiniciar habitual automáticamente; cargar cambios cuando el usuario decida su próximo arranque.


## GXB2-CLAUDE-WAVE-005 (UI de tamaño fijo, Servants, Excursión, Dates)
Status: [T][P] — cerrada; bloqueos liberados (Dates no empezado)
Owner: Claude
Started: 2026-09-29
Goal:
1. GXB2-UI-FRAME-001: que todas las pantallas usen un marco de tamaño fijo (lienzo de diseño 720×1280 escalado para caber en la ventana), como el cliente original, en vez de que cada vista tenga su propio ancho y alto.
2. GXB2-SERVANT-UI-001: pantalla de Servant fiel a las capturas del usuario (Attribute / Servant Aura, Lv. Up con coste, 4 habilidades, lista con Train/Tame y detalles de habilidad), sobre las reglas ya existentes en home_systems.py. Integrar el Servant elegido en el combate si el motor lo permite.
3. GXB2-EXCURSION-001: mapa de Excursión (Food Truck, Main Center, Wishing Tree, Store, Explore, Claim All) y ventana Explore (nivel, cofres con temporizador, pan, abrir ya con gemas, Auto Explore, comprar Tasty Bread) según las tablas travel_*.
4. GXB2-DATE-001 (si da tiempo): Date/intimidad.
Files claimed:
- web/app.js, web/index.html, web/style.css (solo el marco global y los enganches)
- web/frame.css (nuevo), web/servant.js/.css (nuevos), web/excursion.js/.css (nuevos)
- web/home-menus.js (enrutar Servant/Excursión a las vistas nuevas)
- gxb2/home_systems.py, gxb2/engine.py, server.py, tools/extract_home_systems.py y/o tools/extract_servant_excursion.py (nuevo)
- web/assets/servant/, web/assets/excursion/ (nuevos)
- tests/test_home_systems.py y tests nuevos
- LEEME.md, GXB2_MASTER_CHECKLIST.md, ESTADO_PROYECTO.md, AI_WORKBOARD.md
Dependencies: fuentes de Downloads solo lectura; QA sobre una base temporal y el puerto 9180; no se toca el servidor habitual.


## HANDOFF — GXB2-CLAUDE-WAVE-005
From: Claude
To: ChatGPT, Nava o siguiente responsable
Date: 2026-09-29

Completed:
- **Marco fijo** `web/frame.css` y `web/frame.js`: `#app-frame` de 480×853 escalado; `#game-root` es el elemento que hace scroll y `window.scrollTo` se redirige a él. Los overlays nuevos se añaden a `GxbFrame.root()`. `frame.css` debe ser la **última** hoja de estilos.
- **Servants:** `web/servant.js/.css`; datos y Spine con `tools/extract_servants.py` (`data/servants.json`, `web/assets/servant`, `web/assets/spine/pets/<modelo por grado>`). Reglas en `home_systems.py` sin cambios. Combate: `Engine.battle_pet(state)` → `simulate(..., pet_a)` → `battle_host.lua` crea ReportPet. Hubo que copiar el bytecode original `ReportPetAttr.lua` desde `work/gxb2/game/luajit_chunks` al runtime.
- **Excursión:** `web/excursion.js/.css`; assets con `tools/extract_excursion.py` (escenas recortadas, sprites y Spine `travel_main`, `travel_box_all`, `travel_fog`). Backend nuevo `gxb2/explore.py` + `Engine.explore_action` + `POST /api/explore/action` (`go`, `resolve`, `open`, `open_ready`, `upgrade`, `buy_bread`); el snapshot trae `explore_info`. Pruebas en `tests/test_explore.py`.

Verified:
- 53/53 pruebas y sintaxis de todos los JS.
- QA en base temporal y puerto 9180: mapa, ventana Explore (evento → cofre → abrir con gemas → combate real), lista y detalle de Servants (domar, subir nivel y aura), y marco fijo en ocho vistas.

Not verified / pending:
- Dates. Ulticore/ex-level de Servants, Reborn, PetTraining, visualización del Servant en el replay.
- Asignar chicas a edificios desde la UI (la acción `travel_assign` existe). Tienda misteriosa de Explore, cambio de explorador y probabilidades oficiales.
- Clic y táctil en el navegador habitual; todos los tamaños de ventana.

Do not change:
- Fuentes de Downloads, APK y saves habituales. Las reglas LOCAL-020…024 están en DESIGN_DECISIONS.
- Tras ejecutar los extractores, reiniciar solo el servidor de QA.


## GXB2-CLAUDE-WAVE-006 (Dates, misiones, tiendas, arena)
Status: [DONE] (cerrado 2026-09-29)
Owner: Claude
Started: 2026-09-29
Goal: reconstruir, en orden, (1) relaciones y Dates: intimidad, regalos, citas y vow; (2) misiones diarias, semanales y logros; (3) tiendas de Shopping Street; (4) arena Junior Varsity / Elite League contra rivales NPC persistentes. Todo desde tablas y ventanas originales; lo que dependa del servidor queda como LOCAL-0xx.
Files claimed:
- gxb2/relations.py, gxb2/missions.py, gxb2/shops.py, gxb2/arena.py (nuevos); gxb2/engine.py, server.py
- web/dates.js/.css, web/missions.js/.css, web/shops.js/.css, web/arena.js/.css (nuevos); web/app.js, web/index.html (solo enganches)
- tools/extract_relations.py, tools/extract_missions.py, tools/extract_shops.py, tools/extract_arena.py (nuevos); data/*.json nuevos; web/assets/dates|missions|shops|arena/
- tests/test_relations.py, test_missions.py, test_shops.py, test_arena.py (nuevos)
- LEEME.md, ESTADO_PROYECTO.md, DESIGN_DECISIONS.md, GXB2_MASTER_CHECKLIST.md, AI_WORKBOARD.md
Dependencies: fuentes de Downloads solo lectura; QA en base temporal y puerto 9180.

### Handoff GXB2-CLAUDE-WAVE-006 — Claude, 2026-09-29
- Hecho: Dates/relaciones, Daily Tasks + Trophies, tiendas de Shopping Street y Junior Varsity con combate real. 66/66 tests.
- Rutas API: `/api/relations|missions|shops|arena/action`. Datos estáticos: `/assets/relations.json`, `/assets/shops.json`. Snapshot: `missions_info`, `shops_info`, `arena_info`.
- Estado guardado: `state['relations_init']`, `state['missions']`, `state['shop_boards']` (Market/Girls/…; la Lucky Store sigue en `state['shops']['3']` de acquisition.py), `state['arena']`.
- Hooks de misiones: forja, Slots, Enroll/cápsulas, recogida idle, quiz y arena (engine.py y home_systems.record).
- Tablas: `shop_config` y las tiendas se leen de `lua/data/tables` (en data.db están desalineadas) con `extract_acquisition.read_table`.
- Siguientes pasos sugeridos: bonus de intimidad en HeroAttr; Varsity 3v3 y Elite League; Skin Store; misiones semanales; Internship (tavern) para desbloquear su Daily Task; animación de cartas de arena.
- QA hecho en la base temporal (puerto 9180), servidor QA detenido. No se tocó `state/profile.sqlite3`.

### Fix 2026-09-29 (Claude): animaciones que desaparecían
- Causa: lienzos PIXI/WebGL que no se destruían (una tarjeta Spine por Servant en cada redibujado, explorador de Excursión, etc.). Al pasar de ~16 contextos el navegador descarta los más antiguos y los chibis de batalla dejan de verse.
- Arreglo en `web/campaign-ui.js` (GxbSpine): registro `live`; `sweep()` cada 1,5 s destruye los lienzos que llevan 2 barridos fuera del DOM. Nuevo `GxbSpine.snapshot()` para listas: pinta un fotograma a PNG y libera el contexto (lo usan las tarjetas de Servant).
- Regla para nuevas pantallas: usa siempre `GxbSpine.mount` (o destruye tú el `PIXI.Application`); para listas con muchas figuras usa `snapshot`.


## GXB2-CLAUDE-WAVE-007 (Inventario de cliente + Patrol)
Status: [DONE] (cerrado 2026-09-29)
Owner: Claude
Started: 2026-09-29
Goal: (1) inventario automático del cliente descompilado (modelos → ventanas/tablas/mensajes) con cobertura local; (2) reconstruir Patrol (modelo `Dungeon`, tablas `dungeon_*`) con combate original y HP persistente.
Files claimed:
- tools/build_client_inventory.py (nuevo), INVENTARIO_CLIENTE.md (nuevo)
- gxb2/patrol.py, tools/extract_patrol.py, data/patrol.json, web/patrol.js/.css, web/assets/patrol/, tests/test_patrol.py (nuevos)
- gxb2/engine.py, server.py, web/app.js, web/index.html, web/home-menus.js (solo enganches)
- LEEME.md, ESTADO_PROYECTO.md, DESIGN_DECISIONS.md, GXB2_MASTER_CHECKLIST.md, AI_WORKBOARD.md
Dependencies: `~/Downloads/Decomp files` solo lectura; QA en base temporal y puerto 9180; no tocar state/profile.sqlite3.

### Handoff GXB2-CLAUDE-WAVE-007 — Claude, 2026-09-29
- Hecho: `tools/build_client_inventory.py` → `INVENTARIO_CLIENTE.md` + `validation/client-inventory.json` (volver a ejecutarlo al cerrar cada tanda; actualizar su mapa `LOCAL`). Patrol completo: `gxb2/patrol.py`, `Engine.patrol_action`, `POST /api/patrol/action` (`start`, `fight`, `use_drug`, `merchant`, `buy`, `skip_report`), snapshot `patrol_info`, `web/patrol.js/.css`, tarjeta `btn_dungeon_battle` en League. 76/76 tests.
- Runtime: `runtime/battle_host.lua` acepta `battle_type` (por defecto 1) y añade `end_status` [{pos, hp%, mp}] al informe; `simulate(..., battle_type=)` en `gxb2/battle.py`. Los demás modos no cambian (siguen con tipo 1).
- Estado guardado: `state['patrol']` = period, max_stage, current_stage, partners (copia de la build + status), enemies (+status), battle_id, drugs, shop_items, curr_shop_item, skip_report, last.
- Decisiones: LOCAL-028. Siguiente sugerido: Sanctuary (`Trial`, tablas `new_trial_*`, `ReportBattleType.TRIAL_NEW`), House Exam (`AcademyAssessment`, `school_practise_*`), Character Challenge (`HeroChallenge`). Mismo patrón: extractor → módulo → hook en engine → vista → tests → inventario.
- No se tocó `state/profile.sqlite3`; el servidor QA está detenido.


## GXB2-PORTRAITS-008
Status: [T][P] — corrección acotada cerrada; bloqueos liberados
Owner: ChatGPT
Started: 2026-09-29
Goal: corregir iconos negros/vacíos de Selene y todas las chicas: el atlas legado cubre81 IDs, catálogo359. Recuperar avatar indicado por tabla partner; no inferir icono desde nombre/facción ni cambiar saves.
Files changed (bloqueos liberados): tools/extract_portraits.py (nuevo), web/assets/portraits/ (salida provisional), web/assets/original-ui/portraits/ (salida final), web/assets/avatars.json, web/app.js (solo portrait), web/style.css (solo portrait), server.py (solo assets/portraits), LEEME.md, ESTADO_PROYECTO.md, GXB2_MASTER_CHECKLIST.md, VALIDACION.md, AI_WORKBOARD.md, validation/portraits-2026-09-29/.
Dependencies: fuentes read-only, workboard Claude005/006/007 cerrado; preservar cambios de marco/Patrol y hooks actuales. QA temporal.


### HANDOFF — GXB2-PORTRAITS-008, ChatGPT, 2026-09-29
- Causa: portrait() consultaba81 IDs de atlas;278/359 visibles no tenían entrada (Selene incluida). Fuente exacta partner.avatar; compartir retrato entre variantes es regla de tabla.
- Implementado: tools/extract_portraits.py,439 copias PNG intactas en web/assets/original-ui/portraits; avatars.json mantiene81 coords+src en637 IDs. portrait común usa img con fallback tarjeta/arte/atlas; tamaños se heredan del host. Ruta HTTP segura ya existente (original-ui); server.py queda idéntico a antes del fix. No cambiar RNG o guardar assets de referencia como progreso.
- QA:439 hashes iguales a fuente, PNG100×100, ninguna imagen casi negra,439 HTTP200; JS propios válidos. Invocación temporal con los diez nombres de referencia:10/10 imgs cargadas, Selene correcta. Roster/formación17/17 cargadas y Selene en4. Capturas y script synthetic en validation/portraits-2026-09-29/. Backend gameplay no cambiado, no se repitió suite76 de Claude ni se afirma test nuevo de economía.
- Pendiente:10 filas auxiliares/no visibles sin fuente en assets.json, no inventar retratos; no comparar manualmente439 caras/todas las pantallas.
- Respetados: cambios recientes Claude005–007 de marco/Patrol/hooks; fuentes Downloads/sources solo lectura y saves habituales intactos. No detuvo servidor habitual. Servidor/pestaña QA cerrados.
- Siguiente: refrescar navegador habitual carga JS/manifest/iconos nuevos; no hace falta detenerlo para estos recursos. Si se reejecuta generador legado de avatars, ejecutar extract_portraits después para restaurar src. No importar extract_inventory_assets/extract_visuals como bibliotecas porque generan archivos al importar. Todos los bloqueos008 liberados.

### Addendum WAVE-007b — Claude, 2026-09-29
- Patrol UI rehecha según [la captura de referencia](docs/references/2026-09-29-b/README.md): `web/patrol.js` (posiciones en píxeles de diseño con `at()`, chibis y efectos cacheados en `hosts` para no recargar en cada render) y `web/patrol.css`. `tools/extract_patrol.py` exporta ahora 7 Spines de `dungeon_web` a `web/assets/spine/` y `img_group1-7`. El snapshot añade `map_scale`, `map_position`, `group` y `stars`.
- QA en base temporal y puerto 9180: montaje de 5 chicas, mercader tier 2 con Spine, Skip→tienda, casilla Skip (Quick), derrota con cambio automático de chica y chibi. Consola sin errores. 76/76 tests. Servidor QA detenido; `state/` sin tocar.
- Siguiente sugerido: House Exam / Demon Exam (`AcademyAssessment`, ver captura 07).


## GXB2-CLAUDE-WAVE-008 (House Exam / Demon Exam)
Status: [DONE] (cerrado 2026-09-29)
Owner: Claude
Started: 2026-09-29
Goal: reconstruir House Exam (modelo `AcademyAssessment`, tablas `academy_assessment*`) con el motor original, según la captura 07 de docs/references/2026-09-29-b.
Files claimed: gxb2/house_exam.py, tools/extract_house_exam.py, data/house_exam.json, web/house-exam.js/.css, web/assets/house-exam/, tests/test_house_exam.py (nuevos); gxb2/engine.py, server.py, web/app.js, web/index.html (enganches); docs de estado.

### Handoff GXB2-CLAUDE-WAVE-008 — Claude, 2026-09-29
- Hecho: `tools/extract_house_exam.py` → `data/house_exam.json` (también servido en `/assets/house-exam.json`) y `web/assets/house-exam/`; `gxb2/house_exam.py`; `Engine.house_exam_action`; `POST /api/house-exam/action` (`open`, `enemies`, `formation`, `fight`, `sweep`, `buy_tickets`, `buy_certs`); snapshot `house_exam_info`; `web/house-exam.js/.css`. La tarjeta `btn_school_practice` de League se llama ahora «House Exam» y abre esta vista. 1.800 batallas (600 fases × 3 variantes) presentes en el motor.
- Estado guardado: `state['house_exam']` = season, current/max por casa, first_done, score, history_score, day (UTC), cert_bought, formations, last_award. Ítems: 63 Certificate, 64 Admission Ticket, 173 moneda de la House Exam Store (ya en shops.py).
- QA en base temporal y puerto 9180: lista de casas, detalle Demon igual que la captura 07, formación automática de 6 chicas Demon, victoria (+1 punto, ticket 25→24, fase 1 pasa a Raid), Raid ×2, enemigos (!), compra de certificado a 100 gemas, flechas entre casas. Consola sin errores. 85/85 tests.
- Pendiente: ventana de rango/marco, Rematch como botón propio (ahora un aviso), Game Assistant.


## GXB2-CAPSULE-EGG-009
Status: [P][M] — tanda cerrada y probada; bloqueos liberados
Owner: ChatGPT
Started: 2026-09-29
Goal: subir gacha, restaurar huevo1000/5★ y separar BFF/puntos correctamente.
Files claimed: gxb2/engine.py (solo rama SUMMON); web/app.js (solo renderCapsule y botones SUMMON); web/index.html (solo capsule-view); web/style.css (solo Capsules); tests/test_capsule_egg.py; web/assets/original-ui/capsule-egg/; docs/references/2026-09-29-c/; validation/capsule-egg-2026-09-29/.
Coordinación compartida autorizada explícitamente por usuario29/09: no editar hooks HouseExam ni server.py; cambios quirúrgicos y relectura antes de escribir. Claude trabaja fuera de los chats accesibles de Codex; este registro es el handoff común. Docs generales se actualizarán por adición sin sustituir trabajo Claude.

### Handoff CAPSULE-EGG-009 — ChatGPT
-90/90 pruebas,20 JS, QA normal temporal9220/9221.1630→630 y1030→30 con chicas5★, recarga conserva; BFF110→10sin gastar puntos. Snapshot `summon.egg_points/egg_cost` y friend_hearts ahoraitem11.
- Cambios quirúrgicos en SUMMON/Capsules, hooks HouseExam conservados; WAVE008 quedó DONE. No se envió mensaje a Claude externo (no está en lista de chats), handoff por archivos autorizado por usuario.
- Estado normal12 intacto, sin compensación retroactiva ni transferir12→11. VIP original omitido por decisión explícita documentada. Nuevos puntosadvanced segúnaward.
- [Investigación/diferencias/pruebas](validation/capsule-egg-2026-09-29/README.md). Próximo: FX huevo/colección/VIP independiente y comparación Alfheim/tareas/quiz; evitar asumir implementación completa.
- QA cerrado al finalizar; server.py intacto por esta tarea, no se paró servidor habitual. Reinicio habitual necesario para nuevo backend.


## GXB2-GUILD-LAB-010
Status: [P][M] — tanda verificada y cerrada; bloqueos liberados
Owner: ChatGPT
Started:2026-09-29
Goal: recuperar laboratorio80 mejoras/5clases/2páginas, costes/requisitos/reset y aplicar bonos con motor original.
Files claimed: tools/extract_guild_lab.py, data/guild_lab.json, gxb2/guild_lab.py, tests/test_guild_lab.py, web/guild-lab.js/.css, web/assets/original-ui/guild-lab/, validation/guild-lab-2026-09-29/, docs/references/2026-09-29-d/ (nuevos); gxb2/engine.py, gxb2/battle.py, runtime/battle_host.lua, server.py, web/app.js, web/index.html (hooks acotados); docs generales por adición. Sin bloqueos activos al iniciar. Fuentes/saves originales solo lectura; QA temporal9230/9231.


## GXB2-CLAUDE-WAVE-009 (Sanctuary + animación de invocación)
Status: [DONE] (cerrado 2026-09-29): animación hecha; Sanctuary solo investigado
Owner: Claude
Started: 2026-09-29
Goal: (1) Sanctuary (modelo `Trial`, tablas `new_trial_*`); (2) animación de invocación del cliente con su variante cuando sale una chica de 5★.
Files claimed: gxb2/sanctuary.py, tools/extract_sanctuary.py, data/sanctuary.json, web/sanctuary.js/.css, web/assets/sanctuary/, tests/test_sanctuary.py (nuevos); web/summon-anim.js (nuevo) y enganche en la vista de cápsulas de web/app.js; gxb2/engine.py, server.py, web/index.html; docs de estado.

### Handoff GXB2-CLAUDE-WAVE-009 — Claude, 2026-09-29
- Hecho: `tools/extract_summon_anim.py` exporta 4 Spines (`fx_ui_gacha_revision`, `fx_ui_newgirl_gaino/gainp/gain_star`), `summon_scene` y 7 sonidos. `web/summon-anim.js/.css` define `SummonAnim.play(summonId, [{table_id, star, name}])`; en `web/app.js` se llama en `action('SUMMON')` antes de `renderSummon`. La cápsula que se abre con Enroll (`enroll.js`) todavía no la usa.
- QA en base temporal y puerto 9180: máquina `gaoji04` en espera → deslizar → `01/02/03` → revelación 3★ `gainp` → "222" → revelación 5★ `gaino` con toque; invocación real con gemas (−250) y vuelta a Capsule con el resultado. Todos los recursos devuelven 200. 90/90 tests (la cuenta incluye trabajo paralelo de otro agente: `guild-lab.js/.css`).
- Sanctuary y Character Challenge: investigación en el checklist (WAVE-009). Ninguno se implementó porque dependen de enemigos o candidatos que generaba el servidor. Propuesta pendiente de validar con el usuario.
- No se tocó `state/profile.sqlite3`; servidor QA detenido.

### Ampliación de claim GUILD-LAB-010 — 29/09
La captura original Lab enviada durante QA se archiva en referencias d/6. Ajuste de modal/fondo/círculo con prefab original; se añade tools/build_client_inventory.py e INVENTARIO_CLIENTE.md + validation/client-inventory.json al claim para corregir el estado del modelo Guild. No hay locks activos sobre estos archivos.

### Handoff GUILD-LAB-010 — ChatGPT,29/09/2026
-80 mejoras/3920refunds/116 hashes, assets completos, backend guild_lab + UI modal cotejada con captura d/6/prefab, buffs al motor Lua original.99/99 pruebas, JS y QA temporal9230/9231. Ver [registro](validation/guild-lab-2026-09-29/README.md) para reglas, arquitectura, adaptaciones y pruebas.
- Hooks Claude conservados: HouseExam/Patrol/SummonAnim; todos los archivos compartidos re-leídos antes de hooks. WAVE009 está DONE, Sanctuary investigado sin implementación. Fuentes/saves normales/DEV intactos. Sin mensaje a Claude externo no accesible; relevo por archivos compartidos autorizado.
- Estado nuevo `guild_lab.levels/reset_times`, item4 GuildCoin. No regalar moneda en normal. DEV incluye4. Inventario Guild corregido a[P][M], no Guild completo. Prerequisitos/reembolsos originales; cascada reset desconocida, local borra grupo únicamente.
- Prioridades: fuentes Guild coin/boss/Gym/Comedor→comparar avanzado/FX/reset→regalos/Oath/dificultades de refs d. Reiniciar servidor habitual+recargar para backend; no se detuvo el habitual. Vista QA9230 abierta para comparación del usuario (sesión98273; SQLite temporal, no save habitual). No cerrarla ni detenerla mientras la esté usando. Todos los claims de edición010 liberados.


## GXB2-CLAUDE-WAVE-010 (Character Challenge + Sanctuary)
Status: [DONE] (cerrado 2026-09-29)
Owner: Claude
Started: 2026-09-29
Goal: Character Challenge modo Normal (`HeroChallenge`, `partner_challenge*`) y Sanctuary (`Trial`, `new_trial_*`) con las propuestas aceptadas por el usuario: candidatos ponderados de las cajas originales y enemigos de Sanctuary generados a partir de las mejores chicas del jugador escaladas por `power`.
Files claimed: gxb2/hero_challenge.py, gxb2/sanctuary.py, tools/extract_hero_challenge.py, tools/extract_sanctuary.py, data/hero_challenge.json, data/sanctuary.json, web/hero-challenge.js/.css, web/sanctuary.js/.css, web/assets/hero-challenge/, web/assets/sanctuary/, tests/test_hero_challenge.py, tests/test_sanctuary.py (nuevos); enganches acotados en gxb2/engine.py, server.py, web/app.js, web/index.html (coordinar con GXB2-GUILD-LAB-010, que también toca esos archivos).


## GXB2-GUILD-LAB-011 — centrado visual
Status: [X] — ajuste visual verificado; claim liberado
Owner: ChatGPT
Started:2026-09-29
Goal: centrar verticalmente Lab entre barra superior y navegación, según capturas nuevas del usuario.
Files claimed: web/guild-lab.css; docs/references/2026-09-29-e/; validation/guild-lab-centered-2026-09-29/; AI_WORKBOARD.md y docs generales por adición. No toca hooks compartidos reservados por Claude WAVE010, backend ni saves.

### Handoff GUILD-LAB-011
- Centrado con flex/margenauto, nav76px, CSS[hidden] explícito. Geometría básica/avanzada revisada en QA9230; avanzado65.918/65.907px de margen. [Evidencia](validation/guild-lab-centered-2026-09-29/README.md). Solo CSS, reglas/saves/hooks Claude intactos. Refs e/1 avanzado Ranger y e/2 territorio archivadas. QA sigue abierta para usuario.


## GXB2-GUILD-LAB-012 — flechas de páginas
Status: [X][M] — navegación visual verificada; claim liberado
Owner: ChatGPT
Started:2026-09-29
Goal: sustituir pestañas Básico/Avanzado por flecha lateral y puntos originales, conservando centrado011.
Files claimed: web/guild-lab.js/.css; tools/extract_guild_lab.py, data/guild_lab.json y assets/original-ui/guild-lab (tres sprites/catálogos); validation/guild-lab-arrows-2026-09-29/; docs generales por adición. Sin tocar hooks/backend reservados por Claude WAVE010 ni saves.

### Handoff GUILD-LAB-012
- Pestañas de texto sustituidas por flecha lateral/dos puntos con sprites originales. Centrado011 conservado,80.7259px ambos márgenes. Ida/vuelta y clase Ranger verificadas en QA9230. [Evidencia](validation/guild-lab-arrows-2026-09-29/README.md). Sin reglas/gasto/save habitual/hooks Claude. Transición0.4s/FX pendientes; consulta de avanzado habilitada antes de completar requisitos, investigación sigue bloqueada.119 hashes del extractor actualizado. QA sigue abierta, claims liberados.


## GXB2-GUILD-UI-013 — hover y territorio
Status: [I][V parcial] — cerrado; claims liberados
Owner: ChatGPT
Started:2026-09-29
Goal: corregir transform hover de iconos Lab y restaurar edificios/fuente/comerciante/rótulos del territorio según referencia e/2.
Files claimed: web/guild-lab.js/.css, web/style.css; web/app.js únicamente renderMenuExplorer y cleanup de render (coordinación de hooks compartidos previamente autorizada por usuario; conservar hooks Claude WAVE010); tools/extract_guild_territory.py; web/assets/menus/guild_territory_icon*_mask.png; validation/guild-ui-2026-09-29/; docs por adición. No toca backend/server/index ni saves.

### Handoff GXB2-CLAUDE-WAVE-010 — Claude, 2026-09-29
- Hecho: `gxb2/hero_challenge.py` + `/api/hero-challenge/action` (`open`, `fight`, `pick`, `reset`) + `web/hero-challenge.js/.css` (tarjeta de League «Character Challenge»); `gxb2/sanctuary.py` + `/api/sanctuary/action` (`open`, `fight`, `pick`, `continue`, `reset`) + `web/sanctuary.js/.css` (la tarjeta Sanctuary abre la vista de mapa; vista `sanctuary-mode`).
- Motor: `simulate(..., god_skills=)` y `battle_host.lua` pasa `god_skills` a `BattleCreateReport`. Los informes del jefe de Sanctuary llevan `boss_bar`.
- Replay (`web/app.js`): la barra inferior ahora muestra la energía del Servant (`frame.eps` pos 13) con su avatar; se oculta sin Servant. Barra del jefe `.battle-bossbar` cuando el informe trae `boss_bar`. Afecta a todas las repeticiones de combate.
- Tests: 114/114 (15 nuevos). QA en base temporal 9180: lista de desafíos, victoria con elección de chicas y bendiciones, formación de 6; mapa de Sanctuary, combate normal con barra de Servant, jefe con barra de daño y cofre. `state/` sin tocar; QA detenido.
- Pendiente: jefe de Sanctuary a escala grande (ahora chibi normal), rueda de Chaos Crystals, Sanctuary Pass, Character Challenge Speed/Chess.

Ampliación013: assets de edificios se sirven por original-ui/guild-territory (ruta dinámica existente) para evitar reiniciar QA o servidor habitual por el catálogo de menus cacheado.

### Addendum WAVE-010b — jefes a escala original (Claude, 2026-09-29)
- `gxb2/engine.py`: `mark_bosses(report)` añade `display_units[].boss = {scale, offset, center}` a los monstruos `is_boss` o `is_real_boss`, a partir de `data/models.json` (model.lua: scale y battle_pos). Se aplica a todos los combates (closures, Tests, Quiz y `get_battle`).
- `web/battle-animation.js`: los jefes usan su escala de modelo (×1,5 en el lienzo de 1080) en vez de la altura común de 270 px. Se colocan como en la captura de referencia: pies al 80 % y centrados en su mitad. Su marcador flotante de nivel/HP se oculta (`.boss-unit`).
- Sanctuary Deep Sea: los mapas `bg_trail_sences_*` se traducen a `battle_map_trail_sences_*`. El patrón de mapas de `app.js` acepta ahora nombres con letras (`battle_map_\w+`), siempre que existan en `battle-maps.json`.

Ampliación013 QA: reclamar web/shops.js únicamente botón de vuelta para sid6/origin menu-explorer; la comerciante debe volver a su territorio, no a Shopping Street. Sin cambiar inventario ni compras.

### Handoff GUILD-UI-013
Edificios originales, fuente y Merchant idle restaurados; hover conserva centrado. Navegación Lab y tienda ida/vuelta, cinco sprites cargados, sintaxis JS verificados en QA9230 sin gasto. [Fuentes, capturas, limitaciones y relevo](validation/guild-ui-2026-09-29/README.md). Confirmación física hover y FX ambientales pendientes; Guild global parcial. Backend/server/index, partidas y hooks Claude preservados. Claims013 liberados.


## GXB2-CLAUDE-WAVE-011 (Internship / Tavern)
Status: [DONE] (cerrado 2026-09-29; incluye Alchemy/Midas)
Owner: Claude
Started: 2026-09-29
Goal: Internship (modelo `Tavern`, tablas `pub_mission*`, `pub_scroll`) con encargos, requisitos de chicas, duración, recompensas, refresco y pergaminos; enganche con la misión diaria de Internship.
Files claimed: gxb2/internship.py, tools/extract_internship.py, data/internship.json, web/internship.js/.css, web/assets/internship/, tests/test_internship.py (nuevos); enganches acotados en gxb2/engine.py, gxb2/missions.py, server.py, web/app.js, web/index.html.

### Handoff GXB2-CLAUDE-WAVE-011 — Claude, 2026-09-29
- Internship: `tools/extract_internship.py`, `gxb2/internship.py`, `/api/internship/action` (`open`, `start`, `cancel`, `speed`, `complete`, `lock`, `refresh`, `scroll`), `web/internship.js/.css`; `openMenu('intern')`. Alchemy: `tools/extract_midas.py`, `gxb2/midas.py`, `/api/midas/action` (`free`, `buy`), `web/midas.js` (ventana sobre el marco; se abre desde la píldora de oro de Inicio). `missions.py` ya no marca tavern/midas como no rastreados; en `missions.js`, `GO` mapea `midas_window` y `tavern_window`.
- Tests 121/121. QA en base temporal: ciclo completo de Internship (Auto → Start → Speed gratis → Claim) y de Alchemy (gratis + compra, tarea 2/2). `state/` sin tocar; QA detenido.


## GXB2-CLAUDE-WAVE-012 (Old Campus Exploration)
Status: [DONE] (cerrado 2026-09-29)
Owner: Claude
Started: 2026-09-29
Goal: Old Campus Exploration (modelo `OldSchool`, tablas `old_building_*`) según docs/references/2026-09-29-e (capturas 04-05): áreas con 2 fases, equipos por fase, plan de handicaps que suben la puntuación, mejor puntuación, puntuación total, cuenta atrás y premios.
Files claimed: gxb2/old_campus.py, tools/extract_old_campus.py, data/old_campus.json, web/old-campus.js/.css, web/assets/old-campus/, tests/test_old_campus.py (nuevos); enganches acotados en gxb2/engine.py, gxb2/battle.py si hace falta, server.py, web/app.js, web/index.html.

### Handoff GXB2-CLAUDE-WAVE-012 — Claude, 2026-09-29
- `tools/extract_old_campus.py`, `gxb2/old_campus.py`, `/api/old-campus/action` (`open`, `teams`, `plans`, `fight`, `claim_level`, `claim_score`), `web/old-campus.js/.css`. La entrada es el botón `old_school_enter_active` en la vista de Tests (como `TowerWindow.oldSchoolBtn`).
- Planes: `season_plans(n)` reproduce las 4 categorías del servidor. Las chicas de las áreas usan `GxbSpine.snapshot` (imagen fija) para no gastar contextos WebGL.
- QA en base temporal: Set Team de 2 fases, plan +1 → Stage Score 11, derrota con 3 chicas, victoria con 6 → Area 2 abierta, Total 10 y premio de nivel (1500 de la moneda 198). Tests 129/129. QA detenido; `state/` sin tocar.
- Siguiente: Echoes of Time (`TimeCloisterModel`, capturas 01-03) y Galaxy Voyage (`GalaxyTrip`, capturas 06-09).


## GXB2-CLAUDE-WAVE-013 (Echoes of Time)
Status: [W:CLAUDE]
Owner: Claude
Started: 2026-09-29
Goal: Echoes of Time (modelo `TimeCloisterModel`, tablas `time_cloister*`) según docs/references/2026-09-29-e (01-03) y 2026-09-29-f (01-07): mundos del tiempo, tablero de cartas con observación, mazos Supply/Challenge/Encounter, Planetarium (tecnologías), logros y Time Vortex.
Files claimed: gxb2/echoes.py, tools/extract_echoes.py, data/echoes.json, web/echoes.js/.css, web/assets/echoes/, tests/test_echoes.py (nuevos); enganches acotados en gxb2/engine.py, server.py, web/app.js, web/index.html.
Status: [D] done 2026-09-29
Handoff:
- Backend `gxb2/echoes.py` y extractor `tools/extract_echoes.py` → `data/echoes.json` + `web/assets/echoes/`. Enganches: `Engine.echoes_action` (devuelve `detail`), `snapshot echoes_info`, `POST /api/echoes/action`, `openMenu('echoes')` desde Liga, `showView`, `render`, `index.html`, audio.
- UI `web/echoes.js/.css`: reloj de mundos, tablero, mazos, Record, Speed Up, Planetarium, Fases/Time Vortex, Logros y selector de chicas. LOCAL-036.
- Tests: `tests/test_echoes.py` (10). Suite: 139 OK. QA en el puerto 9180 con base temporal: observar, acelerar, terminar, reclamar, mejorar tecnología, combate en Fase 1 y reclamo de logro.

## GXB2-HOUSE-DRESS-014
Status: [D] incremento entregado; sistemas globales [P][M]
Owner: ChatGPT
Started: 2026-09-29
Goal: recuperar Cafe/House, muebles, editor guardado y base Locker Room/Closet/Outfit Store de las cuatro capturas nuevas; avanzar según evidencia sin declarar sistema entero completo.
Files claimed: tools/extract_house_dress.py, data/house_dress.json, gxb2/house_dress.py, tests/test_house_dress.py, web/house-dress.js/.css, web/assets/original-ui/house-dress/, docs/references/2026-09-29-f/, validation/house-dress-2026-09-29/. Hooks acotados engine.py snapshot/house_dress_action, server.py ruta/archivos, app.js openMenu/render/showView e index.html enlaces/scripts/sección. Coordinar hooks según autorización existente y preservar trabajo concurrente Claude ECHOES017. Sin editar fuentes sincronizadas/Downloads ni saves normales/DEV.

Handoff: 297 muebles/269 ofertas/13 series,425 estilos/276 modelos,1486 imágenes recuperadas. House editor/tienda/guardado/confort/dos pisos/chicas propias y vestuario con accesorios implementados. Outfit Store visual, tiradas desactivadas.9/9 tests propios OK; QA temporal9232/9233 continúa para revisar (qa_server.py). [Evidencia/límites/prioridades](validation/house-dress-2026-09-29/README.md). Claims liberados; hook diffs preservan Shrine concurrente. Aviso coordinación Claude: tests.log de la suite general contiene fallos de test_shrine durante WAVE014; no se tocó ese código. Repetir al cerrar integración. No saves normales/DEV ni fuentes sincronizadas editados.

## GXB2-CLAUDE-WAVE-014 (Tsuruga Grand Shrine · Realm of Trials)
Status: [W:CLAUDE]
Owner: Claude
Started: 2026-09-29
Goal: `ShrineHurdleModel` + `Shrine` según docs/references/2026-09-29-g (04-07): entrada con 4 zonas, Realm of Trials (3 pruebas por temporada, dificultad 1-300, 15 fases: combate, bendiciones, tienda, recuperación, jefe), Message Board (tareas/logros) y Pond of Prayers (tienda). Tree of Chimes queda para otra tanda.
Files claimed: gxb2/shrine.py, tools/extract_shrine.py, data/shrine.json, web/shrine.js/.css, web/assets/shrine/, tests/test_shrine.py (nuevos); runtime/battle_host.lua (shrineId/maxRound), gxb2/battle.py; enganches acotados en gxb2/engine.py, server.py, web/app.js, web/index.html.
Status: [D] done 2026-09-29
Handoff:
- Backend `gxb2/shrine.py`. Extractor `tools/extract_shrine.py`, que genera:
  - `data/shrine.json`;
  - `web/assets/shrine/` (154 archivos, escenas en WebP, fondo del Trial recortado);
  - los Spines `shrine_zhandou/jiangli/shangdian/huifu`;
  - la carta de Liga `btn_shrine_hurdle`.
- `runtime/battle_host.lua` y `gxb2/battle.simulate` aceptan `shrine_id` y `max_round`.
- Enganches:
  - `Engine.shrine_action` y `shrine_story`, `snapshot shrine_info`;
  - `POST /api/shrine/action` y `/api/shrine/story`;
  - carta "Tsuruga Shrine" en Liga;
  - `openMenu('shrine')`, `showView`, `render`, `index.html`, audio.
- UI `web/shrine.js/.css`:
  - usa el prefijo `ts-`, porque `sh-` ya lo usa `shops.css`;
  - pantallas: entrada, prólogo, Review, pruebas, dificultad, fases (camino, combate, buffs, tienda, recuperación, jefe), resultados, Message Board y Pond of Prayers.
- Tests: `tests/test_shrine.py` (12). También se corrigió `chip_next` de Echoes, que hacía fallar de forma intermitente `test_developer`. LOCAL-037.

## GXB2-CLAUDE-WAVE-015 (Galaxy Voyage)
Status: [W:CLAUDE]
Owner: Claude
Started: 2026-09-29
Goal: `GalaxyTrip` según docs/references/2026-09-29-e (06-09): 8 sistemas + System of Eternity, mapa de cuadrícula con eventos (enemigos con vida persistente, élites, Ruler debilitable, Blank Space / Mystery Planet / Supply Crate con tiempo, ruta), cupones de desafío, Space Pirates y Galaxy Tyrant (dificultad 1-20), 3 Voyage Teams, Voyager Passport, tienda, tareas.
Files claimed: gxb2/galaxy.py, tools/extract_galaxy.py, data/galaxy.json, web/galaxy.js/.css, web/assets/galaxy/, tests/test_galaxy.py (nuevos); runtime/battle_host.lua (galaxy_info), gxb2/battle.py; enganches acotados en gxb2/engine.py, server.py, web/app.js, web/index.html.
Status: [D] done 2026-09-29
Handoff:
- Backend `gxb2/galaxy.py` (generador de mapas incluido). Extractor `tools/extract_galaxy.py`, que genera `data/galaxy.json` y `web/assets/galaxy/` (152 archivos, mapas en WebP recortados).
- `runtime/battle_host.lua` y `gxb2/battle.simulate` aceptan `galaxy_info` (debilitamiento del enemigo, `{hpP, atkP}` positivos).
- Enganches:
  - `Engine.galaxy_action` (estado de vida de los enemigos por posición, tipo de combate 66), `snapshot galaxy_info`;
  - `POST /api/galaxy/action`;
  - `openMenu('galaxy')` y un botón "Galaxy Voyage" dentro de Cosmos Portal (`home-menus.js`, como `GalaxyStartWindow`);
  - `showView`, `render`, `index.html`, audio.
- UI `web/galaxy.js/.css` (prefijo `gv-`): sistemas, ventana de sistema, mapa con niebla, iconos y rutas, combate, progreso y requisitos, Eternity (Tyrant y piratas), Voyage Teams, Passport, Tareas y Tienda.
- Tests: `tests/test_galaxy.py` (10, incluido un combate real). LOCAL-038.

## GXB2-CLAUDE-WAVE-016 (Historia principal · Main Story + Memories) + ventana Battle de Galaxy
Status: [W:CLAUDE]
Owner: Claude
Started: 2026-09-29
Goal: reproductor de historia (StoryWindow: fondo, personajes, nombre, diálogo, CG, música/voces, temblor, Auto/Recall/Skip) y la historia principal de campaña (main_plot: escena antes del combate y tras la victoria, main_plot_list) + Memories (episodios → capítulos → secciones, desbloqueo por fase o Key of Memory 208). Además, ventana Battle de Galaxy igualada a la captura 2026-09-29-h/03 (poder, auras de facción group_buff, filtro).
Files claimed: gxb2/story.py, tools/extract_story.py, data/story.json, web/story.js/.css, web/assets/story/, tests/test_story.py, tools/extract_group_buff.py, web/assets/group-buff/ (nuevos); enganches en gxb2/engine.py (story_action, partners_power), server.py, web/app.js (MAP_FIGHT), web/index.html, web/galaxy.js/.css.
Status: [D] done 2026-09-29
Handoff:
- **Historia principal:**
  - `tools/extract_story.py` genera `data/story.json` (3369 líneas, 230 secciones, 19 capítulos, 3 episodios) y `web/assets/story/` (fondos, imágenes y CG en WebP, música, voces y ambiente en OGG; unos 21 MB);
  - backend `gxb2/story.py`;
  - `Engine.story_action/story_scene/story_stage` y `snapshot story_info`;
  - `POST /api/story/action|scene|stage|catalog`; el servidor sirve `.ogg` como `audio/ogg`.
- **UI** `web/story.js/.css`: `StoryPlayer.play(plot)` (reutilizable) y `Story` (Memories en Menú → memories).
  - Enganche en `app.js` `action('MAP_FIGHT')`: escena `pre` antes del combate y `post` tras ganar, solo la primera vez.
  - `GxbAudio.pause/resume/muted`.
- **Ventana Battle de Galaxy** igualada a 2026-09-29-h/03: poder (`GET /api/partners/power`, `Engine.partners_power` con el HeroAttr original), Skip, Servant, Front/Back, auras de facción (`tools/extract_group_buff.py` → `web/assets/group-buff/`, lógica de `GroupBuffTable:getBuffIds`), filtro de facción y rejilla.
- **Tests:** `tests/test_story.py` (5). LOCAL-039.

## GXB2-CARDS-CAMPUS-015
Status: [W:GPT]
Owner: ChatGPT
Goal: subir Campus eliminando espacio vacío y restaurar tarjetas compactas con marcos originales, nombre superpuesto y estrellas según progresión; referencia capturas b9215784/9406226f/c4bb940d del usuario.
Files claimed: web/style.css (solo campus-body padding), web/girl-ui.css (tarjetas), web/app.js (solo metadatos girlCard), web/assets/girl-ui/ (marcos/emblemas originales), validation/cards-campus-2026-09-29/ y docs de estado. Hooks de historia/Galaxy de Claude intactos. QA en9232 sobre partida temporal existente; fuentes y saves habituales preservados.


### GXB2-CARDS-CAMPUS-015 — ChatGPT,29/09/2026
Campus elevado60px de lienzo; tarjetas compactas con marco original, nombre sobre retrato, emblemas según estrellas/facción y hover sin desplazamiento. QA visual9232 sobre partida temporal, filtros/detalle/galería e imágenes revisados, sintaxis JS válida. [Evidencia y límites](validation/cards-campus-2026-09-29/README.md). Incremento visual entregado; sistemas globales siguen parciales. Claims015 liberados. No cambios de backend ni guardados habituales.

## GXB2-CARD-CORNERS-016
Status: [W:GPT]
Owner: ChatGPT
Goal: corregir esquina de facción ensanchada al estirar marcos completos.
Files claimed: web/girl-ui.css (solo pseudo-marco), validation/card-corners-2026-09-29/; documentación al cerrar. Sin hooks de Claude/backend/partidas.

## GXB2-CLAUDE-WAVE-017 (Outfits / Dress)
Status: [D] done 2026-09-29
Handoff:
- `tools/extract_dress.py` genera:
  - `data/dress.json`;
  - `web/assets/dress/`: 337 Spines del Senpai con páginas en WebP y atlas reescrito, imágenes de ranura, iconos y marcos `lead_skin_border`, fondos;
  - las cartas de Campus `btn_dress` y `btn_dress_buy`.
- Backend `gxb2/dress.py`. `Engine.dress_action`, `snapshot dress_info`, `POST /api/dress/action|catalog`.
- UI `web/dress.js/.css`:
  - `SenpaiDoll`: chibi compuesto con capas y ranuras;
  - `Dress`: Locker Room (edición Cancel/Save, estilos 1/2, Set), Closet con Gallery y Outfit Upgrade, Outfit Store/Sale.
  - Entradas: Campus → Outfit y Outfit Store.
- Echoes of Time usa `dress.attrs` (`echoes.outfit`).
- `server.py`: `LocalHTTPServer` con `request_queue_size = 128`.
- Tests: `tests/test_dress.py` (8). LOCAL-040.


### GXB2-CARD-CORNERS-016 — entregado, ChatGPT29/09/2026
Esquina de facción corregida con marco en9 secciones:22px de esquina para22px de icono, sin estirar textura completa. Dorado y avanzado verificados en QA temporal9232; assets/backend/saves intactos. [Evidencia](validation/card-corners-2026-09-29/README.md). Claim016 liberado.

## GXB2-CLAUDE-WAVE-018 (Skins de chicas)
Status: [D] done 2026-09-29
Handoff:
- `tools/extract_skins.py` (7 s) genera:
  - `data/skins.json` (336 skins);
  - los retratos por id de skin en `web/assets/pictures/<skin>.webp`, añadidos a `pictures.json`;
  - los avatares en `web/assets/skins/`;
  - 336 chibis de skin en `web/assets/chibis/<modelo>`, con entradas de `catalog.json` por id de skin.
- Backend `gxb2/skins.py`. `Engine.skins_action`, `snapshot skins_info`, `POST /api/skins/action|catalog`.
- Combate: `mark_bosses` marca `skin_id` en `display_units`; `battle-animation.js` usa el chibi de la skin.
- `equipment.release` devuelve también la skin.
- UI `web/skins.js/.css`: pestaña Skins de la ficha (carrusel, Amount, rareza, Method, Wear / Take off, Skin Shop, vista del chibi, visible u oculta en combate, colección).
- `app.js`: la ficha muestra el retrato de la skin elegida o puesta.
- Tests: `tests/test_skins.py` (5). LOCAL-041.

## GXB2-CLAUDE-WAVE-019 (Tarjetas de skin, ficha sin scroll, House Exams)
Status: [D] done 2026-09-29
Refs: `docs/references/2026-09-29-k/01` (House Exams) y `/05` (pestaña Skins).
Handoff:
- `tools/extract_skins.py` copia las cartas `partner_card_<modelo>` (`web/assets/skins/cards/<skin>.webp`, 321) y los sprites de `PartnerCard:setSkinCard` y de la pestaña a `web/assets/skins/ui/`: marco `partner_card03` (9-slice 37/18/42/57), cintas `collection_dress_new_bg_1-4`, `img_group1-7`, `skin_icon01`, `skin_bg01/02`, `skin_btn01/02`, `skin_show_btn` y los botones rojo y azul.
- `web/skins.js/.css`: tarjetas con las medidas del prefab `partner_card` (160×240). La rareza sale de `collection.qlt`: 1 Common, 2 Rare, 3 Epic, 4 Legendary (`COLLECTION_SKIN_TEXT13-16`). La carta original se llama Original/Awaken/10-Star/13-Star/15-Star. Botones Put on / Take off, ojo (`show_skin`) y chibi. Arreglado el formato de los atributos: `crit#40` = 4 %, `sklP#100` = 10 %.
- `web/girl-ui.css`: la ficha de la chica es una columna flex del alto del marco. La escena ocupa el espacio que queda, y el panel de pestañas tiene un máximo del 48 % con scroll interno. La página ya no hace scroll (853/853 en escritorio y en 375×812).
- `web/house-exam.js/.css`: la lista sigue el prefab `academy_assessment_window`:
  - Encabezado de 720×260 con Help, Rank y Award a la izquierda; el logo entre las dos mitades de `academy_assessment_title_bg_new` y el texto "Time Remaining: 8D 16H"; Shop (tienda 9) y la estrella de Exam Score a la derecha.
  - Cada casa es un `academy_assessment_item` de 682×214 con título, lema, "Current Progress: X/100", sello DONE y un chevron. El chevron despliega la prueba anterior y la actual con Battle/Raid, más un enlace a las 100 pruebas.
  - `stageRow` se comparte con la vista de detalle.
- `web/shops.js`: al abrir la tienda desde House Exams, el botón atrás vuelve directamente a House Exams.

## GXB2-CLAUDE-WAVE-020 (Ficha de chica a pantalla completa, Gear con ventanas, Limit-Break, partida dev completa)
Status: [D] done 2026-09-29
Refs: `docs/references/2026-09-29-l/01-07` (Anima Gear, Limit-Break, Exchange, Blue Crystal, Skill-Synchronize).
Handoff:
- **Catálogo de chicas:** `tools/extract_girls_catalog.py` (nuevo) regenera `web/assets/girls-catalog.json`.
  - Regla: `show_in_guide` a 1 o con fecha de lanzamiento.
  - Pasa de 359 a 446 chicas. Las 359 anteriores salen idénticas, y ahora entran las 87 publicadas después, entre ellas las 3 cósmicas (757001-757003).
  - Copia además las 87 cartas que faltaban.
- **Partida dev** (`Engine(developer=True)`):
  - al arrancar añade una copia de cada chica de la guía (`Engine.guide_girls`, `_add_all_girls`), a su nivel máximo y grado máximo;
  - repone el equipo de prueba `DEV_GEAR`: armas, ropa, accesorios y botas de nivel ≥24 de cada clase, y las 12 antigüedades más altas;
  - hay un botón nuevo "Todas las chicas" en el diálogo de desarrollador.
- **Ficha de chica** (`web/girl-ui.css`, en unidades de diseño 720×1280 del prefab `partner_detail_window`):
  - la ilustración ocupa toda la pantalla a su tamaño nativo, con `partner_picture_xy` y `scale` (los lihui Spine usan la misma escala y origen);
  - las pestañas (`nav_btn_*`) están en y=790 y el panel `9gongge20` de 710×426 en y=846, encima de las piernas;
  - el candado y el zoom son iconos (`partner_lock_btn`/`partner_unlock_btn`, `partner_zoom_btn`), y el zoom oculta la interfaz;
  - la frase de la chica sale en `main_bubble` al tocarla;
  - la pestaña Attribute sigue el layout de content_1: `force_icon`, flecha `partner_detail_arrow_up` y barra de coste `9gongge22`;
  - los sprites se extraen con `tools/extract_girl_sheet.py` a `web/assets/detail/sheet/`, que el servidor sirve por prefijo.
- **Gear** (`web/equipment.js/.css`):
  - la pestaña muestra solo el tablero de content_2;
  - una ranura con objeto abre `item_tips_window` con Remove / Replace; en las antigüedades añade Lv. Up, y el cristal ofrece Exchange / Lv. Up;
  - una ranura vacía abre `choose_equip_window` (marco `9gongge21`), que ordena primero las piezas de la clase de la chica;
  - los mensajes salen como toast.
- **Limit-Break** (`web/girl-ui.js`):
  - la pestaña 4 se llama "Limit-Break" desde 10★;
  - `potentiality_component` muestra el banner con el emblema, los 5 nodos en W y los botones Reverse / Replace / Switch;
  - la ventana Limit-Break muestra el emblema siguiente, MAX LVL, Unlock, las cartas de material (1/1 o 0/1), el coste y el botón, que llama a `AWAKE_PARTNER`.
- **Helper común:** `GirlUI.win` / `GirlUI.toast`.
- **Skins:** las tarjetas pasan a unidades `--u`.

## GXB2-CLAUDE-WAVE-021 (Potenciales, Anima Gear, Land of Souls, Skill-Synchronize, Elite Skills, Reverse / Exchange / Switch)
Status: [D] done 2026-09-29
Handoff:
- **Potenciales de Limit-Break.** `CHOOSE_PARTNER_POTENTIAL` en el engine:
  - la etapa i se abre con Limit-Break i;
  - `partner.potentials` son índices 1-3 de `partner.potential`, y `ReportHero:getSkillIDs` los aplica en combate (Life = HP +12 % verificado con HeroAttr);
  - `tools/extract_potentials.py` genera `data/potentials.json` (15 habilidades, iconos, `hero_break_lv_cap` y `hero_break_attr_up` +14 % / +10 %).
  - UI: nodos clicables, ventana "Select Potential" / Activate, y Switch con las 5 etapas.
- **Anima Gear.** `gxb2/souls.py` y `tools/extract_souls.py` generan `data/souls.json` y `web/assets/souls/`.
  - Anima Artifact (soul_equip1, ranura 1) y Anima Stones (soul_equip2, ranuras 2-5, con set de 4).
  - El partner guarda `souls` y `soul_infos` en el formato de `ReportHero.souls`, así que HeroAttr y el combate usan las fórmulas originales.
  - Acciones: equip / unequip / lock, `lv_up` (Artifact con `exp_soul_equip1`; Stone con Soul Essence o Stones con `exp_soul_equip2`), `awake`, `roll_ex` / `save_ex` / `discard_ex`, `open` (cofres 435 y 520010x) y `summon` (Anima Stone Ritual).
  - `equipment.release` también libera el Anima Gear.
  - `web/souls.js/.css` (prefijo `ag-`): botón "Anima Gear" en la ficha (Lv 200+); ventana `SoulEquipInfoWindow` con 5 ranuras, Unequip y pestañas Overview / Replace / Plan; ventana de pieza (Equip / Remove / Lock / Lv. Up / Awaken / atributos extra); pestaña Anima Gear de la Bolsa.
  - `GirlUI.win` funciona en cualquier vista (`.gs-overlay` define su propia `--u`).
- **Land of Souls.** `gxb2/soul_land.py` y `Engine.soul_land_action`, ruta `POST /api/soul-land/action`.
  - 3 áreas de 50 fases, con `BattleType` 71 y la habilidad de dios de la fase.
  - Ticket 421: 10 al inicio, +10 al día, 100 como máximo.
  - Recompensas de primera vez y un drop del dropbox (Anima Stones).
  - Soul Branches por hora, hasta 24 h (`soul_land_award`), y Store con límites por ciclo de 28 días.
  - `web/soul-land.js/.css` (prefijo `lsl-`), con tarjeta "Land of Souls" en League.
- **Skill-Synchronize** (chicas cósmicas):
  - `tools/extract_resonate.py` genera `data/resonate.json`;
  - `UPGRADE_PARTNER_EX_SKILL` usa `skill_resonate_cost` (máximo 10);
  - HeroAttr suma `skill_resonate_effect` (verificado crit 720 / critTime 1000 / hit 800 a nivel 40);
  - ventana circular `GirlUI.resonate` con el texto de cada nivel en color (`GirlUI.rich`).
- **Elite Skills:** ahora es una ventana abierta desde el botón izquierdo de la ficha; ya no está dentro de Attribute.
- **Reverse** (`ROLLBACK_PARTNER`, `partner_return_rule2`): devuelve muñecas de la casa con su despertar, copias homónimas de 5★, EXP al 65 %, fiambreras y el equipo. Botón en Limit-Break y en el lateral para menos de 10★.
- **Exchange / Replace** (`REPLACE_10_STAR`): 5 Diplomas y `replace_10_cost_hero` copias idénticas de una 5★ de la misma casa; conserva nivel, grado, equipo, cristal, antigüedad y Limit-Break.
- **Partida dev:** Anima Gear inicial (24 Artifacts y un set 6★ de cada grupo), materiales 14/47/417-426/435 y la herramienta "Chica a 15★".

## GXB2-CLAUDE-WAVE-022 (Astral Core, Switch, índice de capturas de Facebook)
Status: [D] done 2026-09-29
Handoff:
- **Astral Core** (StarOriginDetailWindow).
  - `tools/extract_astral.py` genera `data/astral.json` (`star_origin`, `star_origin_list`, `star_origin_node`, `star_origin_reset_cost`).
  - Engine: `UPGRADE_STAR_ORIGIN` (`node`, `times`; el nodo k exige `limits[k]` = nodo previo en nivel N; coste de `star_origin.cost` en esferas 359/360) y `RESET_STAR_ORIGIN` (500 gemas, devuelve los materiales).
  - `partner.star_origin` son 10 niveles, y `HeroAttr:getStarOrigin` aplica el efecto acumulado.
  - Roster: `astral_list` (solo a 15★).
  - UI: quinta pestaña "Astral Core" (`GirlUI.astralTab`) con la constelación, líneas de desbloqueo, suma de atributos y Reset; ventana "Node Upgrade" (Lv, efecto actual ▸ siguiente, coste, Upgrade / ×10). El coste coincide con la captura fb/54.
- **Switch** rehecho según la captura fb/119.
- **Attribute:** se oculta la base neutra `sklP` = 1000.
- **Capturas:** `docs/references/2026-09-29-fb/INDEX.md`.

## GXB2-CLAUDE-WAVE-023 (Stellar Altar)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `gxb2/stellar_altar.py` y `tools/extract_stellar_altar.py` (genera `data/stellar_altar.json` y `web/assets/stellar/`).
  - Filas permanentes 4 (Surprise) y 5 (Accumulate) de `starry_altar`.
  - Cada tirada cuesta 1 Star Token y da una recompensa básica del dropbox 80001.
  - 10 % de probabilidad de 5 fragmentos cósmicos personalizados (940059), y 0,25 % de la chica cósmica elegida en modo Sorpresa.
  - En modo Acumulación, +10 fragmentos cada 40 tiradas.
  - 100 fragmentos dan la chica cósmica de 10★ elegida.
  - Registro de las 50 últimas tiradas y apertura tras la fase 15-10.
- **Migración:** el Cosmos Portal genérico (`home_systems` 'cosmos') se migra: modo, chica elegida y contador.
- **Engine y servidor:** `Engine.stellar_altar_action`, `POST /api/stellar-altar/action` y `/assets/dropbox-80001.json` (probabilidades).
- **UI:** `web/stellar-altar.js/.css` (prefijo `sa-`), según las capturas fb/13, 46 y 115:
  - fondo del altar, logo y chibi de la chica elegida;
  - carta para cambiarla; panel de modo con cambio;
  - Draw 1 / 10 y ventana Acquired (OK / ×10);
  - Record, Rate y Help;
  - fragmentos con Summon y acceso a Galaxy Voyage.
  - El menú 'starry-altar' (Cosmos Portal) abre esta vista.
- **Tests:** `tests/test_stellar_altar.py` (2).
- **Añadido a WAVE-023 · CampaignFortWindow** (capturas fb/94-95): el selector de capítulos de `web/campaign-map.js` (`chapters()`) tiene ahora:
  - pestañas Normal / Hard / Extreme / Fantasy / Nightmare (`fort.lv`: fuertes 1-10 … 41-50);
  - filas con banner `fort_img_1-10`, "Chapter N" y texto del fuerte;
  - capítulos bloqueados en gris con "???" y candado;
  - espadas en el capítulo actual y aviso "Unlock at Lv.N".
  - Sprites copiados por `tools/extract_campaign.py`.

## GXB2-CLAUDE-WAVE-024 (Quick Formation · alineaciones)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `gxb2/quick_formation.py` y `Engine.quick_formation_action`, ruta `POST /api/quick-formation/action`.
  - 3 alineaciones (se abren tras la fase 8-5).
  - `save`: la formación actual, o un `team` dado, con el equipo (1-4, 6) y los potenciales de cada chica.
  - `set`: aplica formación y potenciales, y mueve el equipo guardado desde la Bolsa o desde la chica que lo lleve (devuelve las piezas que falten).
  - `rename` (6 caracteres como máximo) y `clear`.
- **UI:** `web/quick-formation.js/.css` (prefijo `qf-`), según la captura fb/44: pestañas Lineup 1-3 (+ bloqueado), Set, filas Front 1-2 / Back 1-4 con la chica, 6 piezas, potenciales y "−", y Return / Save. Botón "Lineups" junto a "← Colección" en la formación.
- **Tests:** `tests/test_quick_formation.py` (2).

## GXB2-CLAUDE-WAVE-025 (Skin Collection)
Status: [D] done 2026-09-29
Handoff:
- **Backend:**
  - `tools/extract_skins.py` añade los nombres de los temas (`collection_skin_group_text`).
  - `skins.snapshot` añade `level` (nivel de moda), `next_point` y `theme_claimed`.
  - Nueva acción `theme_claim` (`collection_skin_group.awards`, "n#377#x": Fashion Points al reunir n skins del tema).
- **UI:** `web/skin-collection.js/.css` (prefijo `scol-`), según las capturas fb/17 y 33:
  - nivel, barra de puntos y "Attribute Boost";
  - búsqueda y "Hide locked Skins";
  - modo Rarity (Common / Rare / Epic / Legendary) y modo Theme (temas con owned/total, "!" con premios y Claim; Festival / Oath / Swimsuit / Other);
  - tarjetas con el marco de la pestaña Skins; las bloqueadas salen en gris.
  - Botón "Skin Collection" en la Galería de Chicas.
- **Tests:** `SkinCollectionThemeTests`.
- **WAVE-025 · Perfil:** `web/profile-senpai.js` añade a "Mi perfil" la tarjeta de Personal Info (captura fb/15): chibi del Senpai con su Outfit (`SenpaiDoll`), triángulo Courage / Charisma / Knowledge (`dress_info.attrs`) y Adjust, que abre el Locker Room.
- **WAVE-025 · Story Items:** `web/story-items.js` (prefijo `si-`), según las capturas fb/35 y 103-105. Muestra la colección de tipo 7 (objetos 94, 95 y 175) en una rejilla gris hasta obtenerlos; el detalle lleva `icon_<id>_big`, nombre, sello Collected / Not Collected, monedas de colección, texto y ‹ ›. Botón "Story Items" en la Galería de Chicas.

## GXB2-CLAUDE-WAVE-026 (Game Assistant)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `Engine.assistant_run` y `POST /api/assistant/run` (captura fb/83).
  - Encadena las acciones del propio jugador: Alchemy gratis, botín de campaña, Regular / Adv. Capsule gratis, correo, Internship terminadas, batallas gratis de Junior Varsity y tareas diarias.
  - Devuelve un informe por paso; un paso que no aplica ese día se omite con su motivo.
- **UI:** `web/game-assistant.js` (prefijo `ga-`).
  - Icono `gameAssistant_icon_yxzs` en la columna izquierda de Inicio.
  - Ventana con los pasos marcables (Daily / Challenges, guardados en localStorage), "Initiate All" y Overview "✔ Completed" con las recompensas por paso.
- **Tests:** `tests/test_assistant.py`.
- **No se puede hacer todavía:** el manga (`comic.lua`) solo tiene URLs de `mhome.carolgames.com`; sus páginas no están en el cliente.

## GXB2-CLAUDE-WAVE-027 (Evento Beach Treasure Hunt)
Status: [D] done 2026-09-29
Handoff:
- **Datos:** `tools/extract_ev_sand.py` genera `data/ev_sand.json` (`activity_sand_gamble`, `award`, `mission` + textos, `shop`) y `web/assets/ev-sand/`.
- **Backend:** `gxb2/ev_sand.py`, `Engine.ev_sand_action` y `POST /api/events/sand`.
  - Castillo de 50 partes (32×10, 10×50 y 5×100 puntos, más Water Ball, Hermit Crab y Water Valve).
  - Cada excavación cuesta 1 Sand Shovel (390).
  - Barra de ronda 160 / 320 / 640 con sus premios; a 640 empieza una ronda nueva con castillo nuevo. Auto desde la ronda 3.
  - Midsummer Task: misiones diarias ligadas a contadores reales (`missions.record`: `echoes_obs` al reclamar una observación, `arena`, `house_exam` al combatir y `tavern3` en Internship de 3★ o más) y misiones del evento (especiales, skin comprada, palas usadas, puntos).
  - Ocean Coin Exchange (391) con límites.
- **UI:** `web/ev-sand.js/.css` (prefijo `bs-`) dentro del hub de Eventos (id 309 en `WORKING`), con pestañas Beach Treasure Hunt / Midsummer Task / Ocean Coin Exchange, según la captura fb/61.
- **Tests:** `tests/test_ev_sand.py`.

## GXB2-CLAUDE-WAVE-028 (Wallpaper Girls)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `Engine.update_profile` acepta `wallpapers` (hasta 6 chicas o skins propias) y `wallpaper_random`.
- **UI:** `web/wallpaper.js` (prefijo `wp-`), según la captura fb/34: rejilla de chicas y skins con ✔, filtro por facción, "Current Wallpaper Girl" con 6 huecos, "Random Switch when entering Frontpage" y OK.
  - Inicio muestra la ilustración de las elegidas por turno o al azar; sin elección, las 3 heroínas de siempre.
  - Botón "Wallpaper Girls" en "Mi perfil".
- **Tests:** `WallpaperTests`.

## GXB2-CLAUDE-WAVE-029 (Outfit Showcase)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `gxb2/dress_show.py` (4 Booths × 3 filas × 5 Slots; desbloqueo por condición, colocar pieza de Outfit, puntuación, rating, Tags diarios, Showcase Store 2/3); `Engine.dress_show_action`, `POST /api/dress-show/action`, `/assets/dress-show.json`.
- **Extractor:** `tools/extract_dress_show.py` (tablas, textos de condición/requisito, sprites y fondos `dress_show_entrance_bg` / `dress_show_main_bg`).
- **UI:** `web/dress-show.js/.css` (prefijo `ds-`), maqueta tomada de los prefabs `dress_show_entrance_window` y `dress_show_main_window` sobre el lienzo 720×1280 (captura fb/40). Entrada desde Campus → Outfit Showcase; la tarjeta "Costume Wardrobe" abre Skin Collection.
- **Dev:** la partida de desarrollo recibe Tags 314/315.
- **Tests:** `tests/test_dress_show.py`.

## GXB2-CLAUDE-WAVE-030 (Wish Capsule + ventana de resultado de invocación)
Status: [D] done 2026-09-29
Handoff:
- **Wish Capsule (evento 140):**
  - Backend: `gxb2/wish.py` (Wish Girl, probabilidad creciente y garantía a 500, recompensas por tiradas); el `SUMMON` del motor acepta 22-26 y la gratis diaria (26); `POST /api/wish/action`, `/assets/wish.json`.
  - Extractor: `tools/extract_wish.py`.
  - UI: `web/wish.js/.css` (prefijo `wc-`): banner Wish en Cápsula (chica sobre el pedestal, progreso, rate, Switch, Gratis / ×1 / ×10 / gemas), selector de las 24 Wish Girls, ventana de progreso, y panel del evento 140 en Eventos (captura fb/47).
- **Resultado de invocación:** `web/summon-result.js/.css` (prefijo `sr-`) según `summon_result_window.prefab` y la captura del usuario: tras la animación o Skip, banda `summon_res` con HeroIcons (avatar, marco, facción, estrellas), OK y "Draw 10" del mismo tipo (fichas / gemas). Skip ya no pide confirmación. Extractor `tools/extract_summon_result.py`.
- **Tests:** `tests/test_wish.py`.

## GXB2-CLAUDE-WAVE-031 (Magic Card)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `gxb2/magic_card.py` (actividad 134 = ActivityIceSecret con la piel Magic Card): preview de 25 cartas, Ultimate Reward por ronda (desbloqueo por `level`, límite de usos), Start, girar carta (15 Magic Wands), NEXT → ronda siguiente, misiones de Magician's Assistant. `Engine.magic_card_action`, `POST /api/magic-card/action`, `/assets/magic-card.json`.
- **Contadores nuevos en `missions`:** `tower` (combate en Tests), `advanced` (cápsulas avanzadas), `star5` (chicas de 5★ obtenidas), `graduate` (Compose / Awake) y `login` (días jugados, en `totals`).
- **Extractor:** `tools/extract_magic_card.py`.
- **UI:** `web/magic-card.js/.css` (prefijo `mc-`), maqueta de `ice_secret_content.prefab` (693×997): escenario, logo, la maga (skin 7085 en Spine), pedestal de la Ultimate Reward, contador de varitas, "Round N", tablero 5×5, Start / NEXT; pestaña Magician's Assistant (diarias / semanales). Capturas fb/53 y 112.
- **Tests:** `tests/test_magic_card.py`.

## GXB2-CLAUDE-WAVE-032 (Matching Pairs)
Status: [D] done 2026-09-29
Handoff:
- **Backend:** `gxb2/two_love.py` (actividad 331): 16 cartas / 8 parejas, Start (1 Arrow of Love, el primero gratis), revelar por peso, premio al completar la pareja, repartir de nuevo al terminar, Recharge Task. `Engine.two_love_action`, `POST /api/two-love/action`, `/assets/two-love.json`.
- **`missions`:** contador provisional `totals.popularity` (10 por tarea diaria, 25 por trofeo) como sustituto de la VIP EXP hasta LOCAL-050.
- **Extractor:** `tools/extract_two_love.py`.
- **UI:** `web/two-love.js/.css` (prefijo `tl-`), maqueta de `activity_2love_window.prefab` (captura fb/88): cupido y logo, 4×4 cartas (recompensas restantes → Start → corazones → tocar), contador de flechas (abre Recharge Task), Free / Start / Ongoing, ventana de recompensas.
- **`itemPicture` global:** ahora resuelve iconos `artfact_*` (equipment) y `soul_equip_*` (souls).
- **Dev:** la partida de desarrollo recibe Magic Wands y Arrows of Love.
- **Tests:** `tests/test_two_love.py`.

## GXB2-CLAUDE-WAVE-033 (Lost Space Zone)
Status: [D] done 2026-09-30
Handoff:
- **Backend:** `gxb2/lost_space.py` (actividad 292): tableros 6×11, explorar junto a lo explorado (1 Space Radar), recompensas por reclamar / Claim All, eventos (Copier, Hologram, Energía +2 / +4, Portal → cofre de zona y zona siguiente, Supply Coordinates → Supply Stash), los 6 láseres con su forma original (`getSkillIds`), Auto Explore, compra de radares. `Engine.lost_space_action`, `POST /api/lost-space/action`, `/assets/lost-space.json`.
- **`missions`:** contador `radar`; las misiones "Use Space Radars" de Magic Card ya cuentan.
- **Extractor:** `tools/extract_lost_space.py`.
- **UI:** `web/lost-space.js/.css` (prefijo `ls-`). Entrada en Eventos (banner, Begin) y vista completa `#lost-space-view` con la maqueta de `activity_lost_space_map_window.prefab`: cofres de zona, tablero (UIGrid 100×85), barra inferior (coordenadas, Copier, láser + energía, Auto Explore, Claim All), ventanas de láser / preview / resultado. No se muestra el chibi del senpai.
- **Tests:** `tests/test_lost_space.py`.

## GXB2-CLAUDE-WAVE-034 (Flujo de combate de campaña)
Status: [D] done 2026-09-30
Handoff (capturas del usuario 2026-09-30):
- **Fight → ventana "Battle"** (BattleFormationWindow): poder (HeroAttr vía `/api/partners/power`), Servant, Front 2 / Back 4, filtro por facción, rejilla con ✔, Battle Start. Guarda la formación de combate (`SET_HANG_TEAM`).
- **Carga** (BattleLoadingWindow): una de las 10 imágenes `battle_loading_N` con su texto `battle_loading_N_en_en` y los textos `BATTLE_LOADING_N` / `_CV_N` según el grupo del prefab, y la barra "Now loading... N%". Se muestra mientras se calcula el combate.
- **Después:** la historia de la fase, el barrido Spine `switch` (`xyd.Battle.effect_switch`, texiao01; la batalla aparece al segundo) y el combate.
- **Tocar una fase** (CampaignStageDetailWindow): "Stage X-Y · nombre", Output (+oro, +zumo, +EXP /5s), Loot (`dropbox_show`), Auto-Battle (patrullar allí) o Fight.
- **Tocar la escena de patrulla** (CampaignHangFormationWindow): equipo de patrulla de 3 (1 delante, 2 detrás), separado del de combate. `Engine.set_campaign_hang`, `POST /api/campaign/hang-team`, `state.campaign_hang`; los chibis de la escena salen de ahí.
- **Código:** `web/campaign-flow.js/.css` (prefijo `cf-`); cambios en `action()` (MAP_FIGHT) y en `campaign-map.js`.
- **Extractor:** `tools/extract_campaign_flow.py` (imágenes de carga, barra, `switch`).
- **Tests:** `tests/test_campaign_hang.py`.


## GXB2-CLAUDE-WAVE-035 (VIP por logros · LOCAL-050)
Status: [D] done 2026-09-30
Handoff:
- **Backend:** `gxb2/vip.py` (+ `tools/extract_vip.py`, `data/vip.json`): VIP EXP derivado del guardado (campaña, nivel, tareas/trofeos, días jugados, Laboratorio); nivel por la tabla `vip` original. `Engine._load` rellena `state['vip']`/`vip_level` (dev = máximo); el snapshot trae `vip_info`.
- **Efectos:** `campaign.pending` aplica `extra_output` (idle); ya lo leían Midas, Internship, Excursión y Slots. `two_love` mide su Recharge Task con VIP EXP (`vip_base`, con migración del contador provisional).
- **UI:** tarjeta VIP en Mi perfil (`renderVip` en `web/app.js`): nivel, barra, fuentes y ventajas actual/siguiente.
- **Tests:** `tests/test_vip.py`; `test_reconstruction` alcanza VIP 3 con `max_stage=120` en vez de inyectar `vip_level`. 221/221 y JS correcto; QA en base temporal, puerto 9190 (9180 estaba ocupado por otro proceso; no se tocó).
- **Pendiente:** confirmar pesos con la usuaria; aplicar `partners_limit`, `quiz_buy_times`, `battle_speed`, `login_double`; ventana VIP original con regalos por nivel (`vip_awards`, `vip_giftbox` son de pago: decidir sustitución).


## GXB2-CLAUDE-WAVE-036 (Contrato de tiempo y eventos · GXB2-TIME-001, parte 1)
Status: [D] done 2026-09-30; frontera del día [ ] pendiente de decisión
Handoff:
- **Hallazgo/prueba:** con el reloj yendo atrás y adelante, `missions.saved` reiniciaba tareas y sumaba días `login` (3 vaivenes = 7 días) y `events.touch` añadía días pasados al check-in.
- **Arreglo:** `Engine.now()` monótono con suelo persistido (`clock` en SQLite, `clock_behind` en el snapshot, dev sigue el reloj real); `events.touch` / `missions.saved` solo avanzan. LOCAL-057.
- **Tests:** `tests/test_clock.py` (suelo y reinicio, dev, vaivén de fecha, check-in, puntos semanales en el lunes UTC y sin reabrir semana anterior). 226/226.
- **Verificado en pruebas:** semana de puntos (límite exacto lunes 00:00 UTC), no reabrir semana vieja. **No verificado:** DST/zonas horarias reales en cada módulo, UI de aviso cuando `clock_behind>0`, calendario de eventos (los WORKING están siempre disponibles; la rotación de archivados es solo JS por semana ISO).
- **Siguiente:** decidir día local vs UTC (LOCAL-057, abierto); calendario/periodo de eventos con inicio-fin; liquidación idle al cambiar fase (IDLE-SETTLE-001).

### Addendum WAVE-036b — día/semana locales (Claude, 2026-09-30)
- Decisión de la usuaria: cada jugador usa la hora de su máquina. LOCAL-058; `clock.py` es la única fuente de día/semana (`day`, `week`, `week_end`, `week_index`, `week_start`).
- Módulos migrados: midas, internship, house_exam, sanctuary, home_systems (Quiz/Libro), magic_card, arena, explore, missions, shops; textos UI de Midas, Pasantías, Sanctuary y Eventos.
- Tests de límites en hora local (`test_reconstruction.epoch`, `test_sanctuary.NOW`); `test_clock` añade coherencia entre módulos. Suite completa lanzada con TZ=Asia/Tokyo, UTC, America/Santiago, Pacific/Auckland y America/Los_Angeles.
- No verificado: cambio real de horario de verano en vivo, viajar entre zonas, calendario de eventos con inicio/fin.

### Nota 2026-09-30 (Claude): hoja de ruta de pendientes en [PENDIENTES.md](PENDIENTES.md) (eventos 10/322, familias y orden recomendado; INVENTARIO_CLIENTE.md está desactualizado).


## GXB2-CLAUDE-WAVE-037 (Motor de eventos, Gremio v1, sorteos con ficha)
Status: [D] done 2026-09-30
Handoff:
- **Motor genérico de eventos:** `gxb2/activity_kit.py` + `tools/extract_activity_kit.py` + `web/act-kit.js/.css` (`POST /api/act-kit/action`, `/assets/activity-kit.json`, `state['act_kit']`, snapshot `act_kit_info`). 28 eventos con canje y/o misiones; contadores derivados del texto de la misión; misiones no rastreables visibles pero no reclamables; suministro diario cuando el minijuego no existe (LOCAL-059). Engancha en el hub de Eventos: `events.js` añade los ids de `ActKit.ids()` a `WORKING`.
- **Gremio v1:** `gxb2/guild.py`, `tools/extract_guild.py`, `web/guild.js/.css`, `POST /api/guild/action`, `state['guild']`, snapshot `guild_info`; hooks `Guild.handles/open` en `openMenu`/`menuForward` y vista `guild-view` (LOCAL-060). Jefes de Gym con `simulate` y tu formación.
- **Sorteos con ficha:** `gxb2/activity_draw.py`, `tools/extract_activity_draw.py`, `POST /api/act-draw/action`, `state['act_draw']`, snapshot `act_draw_info`; misma pestaña "Juego" (LOCAL-061).
- **Tests:** `test_activity_kit` (6), `test_guild` (7), `test_activity_draw` (8); suite 249/249 y 15 JS correctos. QA en navegador (base temporal, puerto 9190): panel de Skin Exchange/Kid's Store, crear gremio, Office, Gym con combate real (derrota con el equipo inicial), Cafeteria con pedido en marcha, Goldfish (fichas diarias, ×10, hitos).
- **Bug corregido de paso:** `times=0` se convertía en 1 por `or 1` en compras/sorteos.
- **Sin verificar:** táctil/tamaños, victoria de jefes con un equipo fuerte, catch-up de EXP tras muchos días reales, texto/arte fiel de cada evento (paneles genéricos), balance de las cifras locales.
- **Siguiente:** Jackpot/Lucky Draw, Blind Box, Pirate, Chime, Firework, Jigsaw y demás minijuegos con mecánica propia; calendario de eventos; Guild War/Playground; Girls Exchange (selector de chica); paneles de eventos de las pestañas de pago.

## GXB2-CLAUDE-WAVE-038 (Jackpot of Fortune + Wish Upon a Chime)
Status: [D] done 2026-09-30
Handoff:
- **Jackpot (64):** `gxb2/jackpot.py`, `tools/extract_jackpot.py`, `data/jackpot.json`, `web/assets/jackpot/`, `web/jackpot.js/.css`, `POST /api/jackpot/action`, `state['jackpot']`, snapshot `jackpot_info`; pestañas Máquina / Canje (el canje reutiliza `ActKit.render`, `NO_SUPPLY={64}` en `activity_kit`). Referencia: `docs/references/2026-09-29-fb/IMG_5072.JPG`. LOCAL-062.
- **Chime (308):** añadido a `activity_draw` (dos modos, garantía cada 20 Gilded, contador `spent`); las misiones "Consume … Cranes" del kit leen `activity_draw.spent`. Los Chimes como equipo siguen pendientes (`chime.lua`, `chime_decompose`, `chime_lv_cost`; referencia IMG_5147).
- **Contraste con capturas:** fb/82 (Seaside Fishing, hitos "Fish N time(s)") coincide con los hitos por cuenta del motor; fb/71 (Xmas Sock Hunt) confirma que `limit` = veces reclamables ("Limit 0/20"); fb/93 y fb/72 (Celebration Party, Starry Bonus) son juegos propios (baile/excitación, botellas por nivel) que aún no tienen motor.
- **Tests:** `test_jackpot` (5), ampliación de `test_activity_draw`; suite 255/255 y todos los JS correctos; QA en navegador (base temporal, puerto 9190): máquina Basic, giro con animación, energía 15→10.
- **Siguiente (referencias ya en el repo):** Chimes (equipo), Celebration Party/Melodic Notes (IMG_5166/5165), Starry Bonus (IMG_5143), Dimensional Maze (IMG_5146/5176/5184), Halloween Pumpkin Patch (IMG_5149), Pumpkin Artisan (IMG_5151), Carnival Puzzle (IMG_5163), Collector's Treasure (IMG_5160), Study Session (IMG_5152), Explorer Pack (IMG_5145). Sin referencia: Blind Box Frenzy, Pirate/Deep Sea Treasures, Lucky Draw (258), Firework, Jigsaw, Cake/Coffee, Puppet Parade → pedir capturas al usuario.

## GXB2-CLAUDE-WAVE-039 (Blind Box Frenzy + referencias de la usuaria)
Status: [D] done 2026-09-30
Handoff:
- **Referencias:** 14 imágenes de la usuaria en `docs/references/2026-09-30-user/` (`INDEX.md`, SHA256SUMS): Blind Box (promo), Winning Pair (2), Secret Sanctuary, Deep Sea Treasures (mapa + Raid), Palace Vaults, Sweet Melody, Exchange, Jigsaw (2), Firework Project, Puppet Parade, Yume Tea Party.
- **Blind Box (338):** `gxb2/blind_box.py`, `tools/extract_blind_box.py`, `data/blind_box.json`, `web/assets/blind-box/`, `web/blind-box.js/.css`, `POST /api/blind-box/action`, `state['blind_box']`, snapshot `blind_box_info`. La pestaña muestra debajo el tablero de misiones del kit (los cupones salen de la VIP EXP). LOCAL-063.
- **Tests:** `test_blind_box` (5); QA en navegador: ventana de selección por niveles, confirmación, cupones diarios, apertura ×1 con porcentajes en la rejilla.
- **Siguiente con referencia ya disponible:** Winning Pair (52/84; tablero de cartas, 1 Game Card por carta), Deep Sea Treasures (329; Raid con % y cofre garantizado en 10), Jigsaw (37; puzle deslizante 3×3 con energía), Firework Project (196; tienda + Craft), Puppet Parade (189; hitos por marionetas), Yume Tea Party (63; platos numerados), Sweet Melody (142; piano), Celebration Party/Melodic Notes, Starry Bonus, Dimensional Maze, Pumpkin Patch/Artisan, Carnival Puzzle, Collector's Treasure. Sin referencia: Lucky Draw (258).

## GXB2-CLAUDE-WAVE-040 (Deep Sea Treasures + Palace Vaults)
Status: [D] done 2026-09-30
Handoff:
- **Backend/datos:** `gxb2/pirate.py`, `tools/extract_pirate.py`, `data/pirate.json`, `web/assets/pirate/`, `POST /api/pirate/action`, `state['pirate']`, snapshot `pirate_info`. El motor de canje (`activity_kit`) ahora respeta `unlock` por moneda gastada en Palace Vaults; 330 dejó de tener misiones en el kit (la colección la lleva `pirate`). LOCAL-064.
- **UI:** `web/pirate.js/.css`: mapa de 5 tierras con Raid y ventana de Raid (dropbox y cofres con % iguales a la captura, selector de cantidad, cofre garantizado), Collection Progress con "Go" a Palace Vaults; Palace Vaults con pestañas Secret Vault (ActKit) y Collection Reward.
- **Tests:** `test_pirate` (5); QA en navegador con la captura 06 como referencia.
- **Pendiente:** historia (plot 348 líneas) y sus iconos de chicas por isla; el fondo original del mapa (no está en los sprites recortados: se usa un degradado).


## GXB2-CLAUDE-WAVE-041 (Halloween Pumpkin Patch)
Status: [D] done 2026-09-30
Handoff:
- **Backend:** `gxb2/pumpkin.py` (actividad 150): 10 calabazas (filas 1-10 de `activity_halloween_award` con pesos), Cut con 1 Pumpkin Dagger (182), Claim con la recompensa de ronda (filas `times>=1`, 27 rondas, la última se repite), compra con gemas. `Engine.pumpkin_action`, `POST /api/pumpkin/action`, `/assets/pumpkin.json`, snapshot `pumpkin_info`.
- **Extractor:** `tools/extract_pumpkin.py`.
- **UI:** `web/pumpkin.js/.css` (prefijo `pk-`). Campo de calabazas de `halloween_pumpkin_field.prefab` (696×875): logo, 10 calabazas enteras / abiertas con la recompensa y ✔, contador de dagas con +, Cut / Claim y Pack Reward con la lista de rondas; al tocar una calabaza se ven sus premios con %. Captura fb/78. La recompensa de la ronda 1 es un avatar (20001043 → `head_1043`).
- **Dev:** la partida de desarrollo recibe dagas.
- **Tests:** `tests/test_pumpkin.py`. Suite 266/266.

## GXB2-CLAUDE-WAVE-042 (Pulido: Servant en "Battle" y ventana de Anima Artifact)
Status: [D] done 2026-09-30
Handoff:
- **Servant en la ventana "Battle"** (`web/campaign-flow.js`): el botón abre la lista de los 9 Servants (bloqueados en gris) y elige el que combate (`home_systems.selected_pet`, que ya usan todos los combates); "Sin Servant" lo quita (`pet_select` con id 0, nuevo en `home_systems.action`). El botón muestra el avatar del elegido. `GirlUI.win` acepta `stack:true` para abrir una ventana sobre otra sin cerrarla.
- **Partida dev:** recibe todos los Servants abiertos.
- **Anima Artifact** (`web/souls.js`, `artDetail`, como SoulEquip1StrengthenWindow y la captura fb/120):
  - cabecera con alas (`chess_exchange`), Equip / Remove y candado;
  - pestañas Star up / Upgrade / Infuse con los sprites `nav_btn_*`:
    - Star up: rango, nivel máximo y capacidad actual ➜ siguiente, más la copia como material;
    - Upgrade: nivel y atributos base / Infuse ahora ➜ siguiente, con coste, Upgrade y ×10;
    - Infuse: Infuse Attribute · I-V con Infuse / Convert, bloqueados hasta la estrella que los abre, y Save / Cancel del cambio.
  - Las Anima Stones mantienen su ventana. Sprites nuevos en `tools/extract_souls.py`.
- Suite completa OK.
- **Addendum WAVE-042 — combate a pantalla completa:** mientras se juega, `#arena` ocupa todo `#app-frame` (sin la cabecera "COMBATE ORIGINAL", ni la línea de narración ni la navegación inferior), como la captura de la usuaria (Round, barra del Servant, velocidad, saltar). "Continuar" de `CampaignUI.result` cierra la arena en cualquier vista (antes solo en Campaña). CSS en `web/campaign-flow.css`. Suite OK.

## GXB2-CLAUDE-WAVE-043 (Partida dev avanzada, copias de chicas, arte de las re-ediciones 5★)
Status: [D] done 2026-09-30
Handoff:
- **Partida dev avanzada (una vez, `state.dev_advanced`):**
  - campaña en la fase 480 de 530 (patrulla en 47-10; quedan 50 por combatir);
  - Tests piso 300; Patrol fase 300 (estado completo con `patrol.fresh`, y reparación si quedó a medias);
  - todas las chicas al grado máximo y a su tope real de nivel (`level_cap(real=True)`; en dev el tope sigue siendo 330 para poder subirlas).
- **Copias de una chica:** ya existían (cada invocación crea su propio `partner_id`, con nivel, estrellas y equipo propios; la herramienta dev "girl" crea hasta 20). Ni el cliente original ni el local prohíben dos copias en un equipo. Arreglo: la lista de Chicas pintaba una tarjeta por chica (`table_id`) y ocultaba las copias; ahora pinta una por copia (`girlCard(row, owned, skin, copy)`), cada una abre su ficha.
- **Arte de las re-ediciones 5★** (54xxxx: Lily 542004, Liz, Lightin, Litana, Lisa… 254 ids, 38 sin arte propio): el cliente usa el de su `host` (la chica base). `extract_girls_catalog.py` exporta `host`; `artId()` en `app.js` lo aplica en tarjetas, retratos, avatares (`campaign-flow`, `summon-result`) y en la ficha (`girl-ui.js`: `picture` y lihui). Captura de la usuaria 2026-09-30.

## GXB2-CLAUDE-WAVE-044 (Chimes como equipo · Tree of Chimes)
Status: [D] done 2026-09-30
Handoff:
- **Backend:** `gxb2/chimes.py`. Los 10 Chimes de cuenta: activar con fragmentos; Charge (Chimelight 0-100 %, coste por calidad de `chime_lv_cost`); Enchant 1-3 en orden (límite de Chimelight y coste); Ascend (limit4: Chimelight y nº de Enchantments); transferir fragmentos sobrantes a Chime Chips (373). `Engine.chimes_action`, `POST /api/chimes/action`, `/assets/chimes.json`, snapshot `chimes_info`.
- **Combate:**
  - `battle.CONTEXT['chimeA']`, que rellena `Engine._load` con `chimes.bonus(state)`, llega al Report original como `chimeBonusA` (atributos por HeroAttr:getChimeAttr y las habilidades de Ascensión como god skills del equipo A);
  - `battle.attributes` pasa `chimeBonus` para que el poder de la ficha lo incluya;
  - `runtime/battle_host.lua` fija `xyd.Global.lang='en_en'` (ChimeTextTable lo necesita).
  - Ojo: `CONTEXT` es global del proceso; las partidas normal y dev comparten servidor, así que en teoría una petición simultánea de la otra partida podría cruzar los Chimes.
- **UI:** `web/chimes.js/.css` (prefijo `ch-`), como ChimeMainWindow: fondo del árbol (`chime_bg_ysm` recortado), cordones (`chime_bg_ysm_x`), 3 Chimes por fila en las posiciones originales, balanceo, nombre en color de calidad (NameColor), % de Chimelight / candado / punto rojo, y menú lateral Gallery / Shards. Ventana de detalle con Status / Charge / Enchant / Ascend y activación con fragmentos; ventana de fragmentos con Transfer; Gallery con los máximos. Se entra por Shrine → Tree of Chimes (el marcador de posición se sustituyó).
- **Dev:** fragmentos de los 10 Chimes, Fantasy Dust y Fantasy Talisman.
- **Extractor:** `tools/extract_chimes.py` (tablas, textos y los Spines `yushenmu_main`, `fengling_*` y efectos en `web/assets/spine/`, aún no usados en la UI).
- **Tests:** `tests/test_chimes.py`, incluida la comprobación numérica de HP con HeroAttr.

## GXB2-CLAUDE-WAVE-045 (Pulido: Campus, Transfer/Altar, Slots, Dorm)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). Reclamado: Campus (tarjetas Study/Life), Transfer (AltarWindow: `DECOMPOSE_PARTNERS`, `web/altar.js/.css`), pulido de Slots (`web/slots.*`) y Dorm (`web/house-dress.*`, `gxb2/house_dress.py`).
- Hecho: Campus Study ya no muestra Outfit / Outfit Store (van en Life, como SchoolChooseWindow); Tree of Chimes más arriba.
- Transfer = AltarWindow (`web/altar.js/.css`, `/api/altar/preview`, acción `DECOMPOSE_PARTNERS` en el motor):
  - pestañas Altar / Reverse, 12 huecos, filtros de facción y estrellas;
  - Smart (≤4★ libres), Preview y Retire (hasta cinco 6★+ al día);
  - el equipo vuelve a la mochila y la chica sale de la formación y de la patrulla;
  - Reverse abre `GirlUI.reverse`. Decisión en LOCAL-066. Test: `tests/test_altar.py`.
- Slots:
  - barra superior con fichas 35/29/6 y botón atrás;
  - pestañas con sprite `nav_btn` (High Stakes gris con candado si está cerrado);
  - botones redondos Probabilidad / Ayuda.
- Dorm (`web/house-dress.js/.css`), maquetado sobre `house_window`, `house_select_heros_window` y `house_shop_window`:
  - placa `house_name_bg` y chip de Comfort;
  - botones de ayuda y ocultar interfaz;
  - botones redondos Manage / Store / Floor / Date y botón grande Rest con n/5;
  - en edición: Clear, Cancel / Save con los sprites y la Storage Box con tarjetas `house_icon_7`;
  - Rest es la ventana de 5 huecos con Cancel / Confirm;
  - Furniture Store usa tarjetas `house_icon_8`.
- Locker Room / Outfit Store (pestañas del Dorm y tarjetas de Life) abren ahora el módulo completo `Dress` (Locker Room, Closet y gacha real) en vez de la copia antigua de `house-dress`.
- Dev: fichas 69 (muebles) y 258/259 (botones de atuendo) en la recarga.
- Suite: 269 tests OK.
- Handoff: el sorteo de muebles, las visitas y los temas de `house_window` siguen sin hacer (son sociales o de servidor).

## GXB2-CLAUDE-WAVE-046 (Pulido según referencias: Slots, Manga, Category de Girls, Intern, Yume Collection, Menu)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). Referencias: `docs/references/2026-09-30-user-b/01-07`. Reclamado: `web/slots.*`, la vista de Manga/Memories, la ventana Category de Girls, la lista de Intern, Collection y el Menú.
- Slots (`web/slots.js/.css`):
  - GambleWindow en coordenadas del prefab: cabecera con ficha + gemas, pestañas Slot Machine / High Stakes Slot Machine, Prob. / Help, Record y Shop;
  - la crupier con su bocadillo (`girls_model_text` 3 / 4), Skip y Go to Slot Points;
  - la máquina 3×3 con `gb_icon_bg` e iconos con marco de calidad, Next Refresh + Refresh verde, X1 / X10 (`gb_btn_use_bg`) y la palanca 10×;
  - Record, Shop, Prob. y Help son paneles sobre la máquina.
- Menú (`web/settings-menu.js/.css`, `tools/extract_settings_menu.py`, `/assets/menu/`):
  - SettingUpWindow sobre `setting_up_bg`: Memories / Collection, Game (Notice, Help, Tips, Social, GM) y Others (Manga, Image, Redeem);
  - el botón Menú de la barra inferior abre esta vista (`openMenu('settings')`).
- Yume Collection: CollectionWindow con logo, heroína, cuaderno, Collect Points y las 7 entradas con su % (LOCAL-067).
- Manga: ComicWindow con libro, 9 episodios por página y paginación, más un lector.
  - Las 215 páginas y 62 mangas de cumpleaños vienen de la carpeta de la usuaria `~/Downloads/Decompiled/Manga` (`tools/extract_manga.py`, WebP, 63 MB).
  - Seis URLs del cliente tienen erratas y se resuelven por número de episodio.
- Girls:
  - el selector "★ Todas" es ahora el botón de orden, que abre Category / Display Order (PartnerSortWindow, LOCAL-067);
  - el botón de la izquierda (`btn_zk` / `btn_sq`) despliega el filtro de clases (`icon_zybq_*`);
  - facciones y clases funcionan como interruptores.
- Intern (`web/internship.*`, `gxb2/internship.py`):
  - filas de TavernWindow: nombre, candado, barra de estrellas, progreso, recompensa y tiempo;
  - "Quest(n/d) will be reset", filtros de estrellas `pub_sort1-7`, y Use / Multi-Intern / Claim in Bulk;
  - la recompensa se sortea al aparecer el encargo y se paga esa misma. 2 tests nuevos.
- Iconos de oro y gemas: las versiones `icon_1_small` / `icon_2_small` usan ahora el icono grande (también en `extract_navigation_assets.py`).
- Botones azules y blancos de 65×65 con 9-slice (`.cr-btn` "Aceptar", `.gu-btn`, Graduate) en vez de estirados.
- Suite: 271 tests OK.


## GXB2-CLAUDE-WAVE-047 (Arreglos: carta de las reediciones, filtro de clases, botón de música)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido).
- Cartas de reediciones:
  - `server.py` calcula `CARD_ALIAS`: 38 reediciones sin carta propia siguen su cadena `host` (p. ej. Selene 546003 → 46003);
  - `/assets/cards.json` las incluye y `/assets/cards/partner_card_<id>.png` sirve la carta base, lo que arregla Skins (captura de la usuaria), Enroll, Stellar Altar, Graduate, etc.;
  - `artId()` (app.js) sigue la cadena completa y `skins.js` usa la carta base en "Original".
- Filtro de clases de Girls: ahora es una burbuja vertical pequeña (`bg_zk`) sobre el botón `btn_zk` / `btn_sq`, en vez de una fila bajo toda la cuadrícula; con 446 chicas quedaba fuera de la vista.
- El botón de música (`.gxb-mute`) tapaba ese botón (y otros de la esquina inferior izquierda): pasa al borde izquierdo a media altura, más pequeño y semitransparente.
- Suite: 271 tests OK.

## GXB2-CLAUDE-WAVE-048 (Filtro de clases horizontal, Wallpaper con skins)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido).
- Girls: la fila de clases se abre en horizontal (de izquierda a derecha) justo encima de la fila de facciones, con el mismo tamaño que sus botones.
- Wallpaper Girls list (`web/wallpaper.js`):
  - cada chica muestra imagen: carta, carta de la chica base (reediciones) o ilustración; las cartas sin arte mantienen su tamaño con un hueco;
  - lista las skins que tienes (en la bolsa, coleccionadas o puestas), bajo la chica que las viste, con su nombre;
  - el Front Page resuelve las reediciones.
- Partida dev: una copia de cada skin, una sola vez (`dev_skins`).
- `tools/extract_skins.py`: el cliente escribe `partner_crad_*` en 5600105 / 5301502 (errata); se usan esas cartas. Intertwined (5401307) no tiene arte en el cliente.
- Suite: 271 tests OK.

## GXB2-CLAUDE-WAVE-049 (Multijugador simulado y tiendas)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). No se ha tocado `gxb2/guild.py` (otra sesión).
- Collection Store (`gxb2/collection.py`, `tools/extract_collection.py`, `/api/collection/action`, ventana en `web/settings-menu.js`):
  - Rare Store (`shop_collection1`, compra única) y Common Store (`shop_collection2`, límites cada lunes);
  - tramos por Collect Points 500 / 1500 / 2500 (`collection_point_level`), coste en oro o gemas;
  - los Collect Points los calcula ahora el servidor (`state.collection_info`: puntos, % por entrada, ids conseguidos).
- Corrección: las skins daban 0 puntos. Su `new_awards` es `377#n`; los Collect Points están en `awards` (`123#n`). Los puntos máximos pasan de 35.740 a 64.580.
- VIP por logros (LOCAL-050, `gxb2/vip.py`): nueva fuente `collection` = 1 VIP EXP por Collect Point (idea de la usuaria: los trofeos alimentan el VIP). Aparece como "Yume Collection (trofeos)" en el desglose VIP.
- Arena 3v3 (`gxb2/arena3v3.py`, `tools/extract_arena3v3.py`, `/api/arena3v3/action`, `web/arena3v3.js/.css`):
  - 3 equipos de 1 a 6 chicas, al mejor de tres con el motor original (equipo k contra equipo k del rival);
  - 3 Arena Tickets por combate y 5 de regalo al abrir;
  - cartas de premio (`arena_battle_award_3v3`) y premios de temporada (`arena_rank_award_3v3`);
  - rivales de Junior Varsity con tres alineaciones cada uno (LOCAL-069);
  - entrada desde Junior Varsity con el botón `btn_arena_3v3`.
- Iconos de premios: `CampaignUI` resuelve avatares (2000xxxx), marcos (8xxx) y muebles.
- Partida dev: recarga también Arena Tickets (34).
- Tests: `tests/test_collection.py` (6) y `tests/test_arena3v3.py` (5).
- Pendiente de multijugador: Arena entre servidores / Fair Arena, amigos y Friend Boss, Guild War y chat.

## GXB2-CLAUDE-WAVE-050 (Collection más arriba, posición de ilustraciones, Wallpaper en portada, Skin Store)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido).
- Yume Collection: las siete entradas suben 90 unidades y quedan pegadas a la fila de puntos, como en la captura 06.
- Ficha de chica, skins demasiado altas. Dos causas:
  - las skins animadas: `GirlsModelLite:setModelInfo` baja el Spine con `SetLocalPosition(0, -200)` dentro del partnerImg y no se aplicaba; ahora el origen es `640 + y + 200·scale`;
  - si se muestra la imagen fija de la chica como respaldo, se coloca con las coordenadas de esa imagen y no con las de la skin.
- Nueva función `hostChain()` (app.js): recorre la cadena de reediciones buscando ilustraciones. Hace falta porque desde WAVE-047 las reediciones tienen carta propia (alias) y `artId()` se detenía en ella.
- Wallpaper en el Front Page (MainMap:updateImg):
  - capa de 720×1280 con la ilustración en `partner_picture_xy2` (nuevo campo `xy2` en `data/partner_pictures.json`, también en `tools/extract_visuals.py`) y su escala a tamaño real;
  - las skins animadas se montan como Spine con el −200;
  - antes era un `<img>` recortado y cada ilustración quedaba en otro sitio.
- Skin Store:
  - `skins.action('buy')` usa `shop_skin` (130 skins, Costume Tickets 74);
  - la ventana `Skins.store()` (SkinDetailBuyWindow) se abre desde el edificio Skin de la Shopping Street;
  - la partida dev recarga el ticket 74;
  - `tests/test_skin_store.py`.
- Suite: 292 tests OK.

## GXB2-CLAUDE-WAVE-051 (Dorm: chicas a una escala, sin senpai, Manage con HouseSelectBox)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). `web/house-dress.js/.css`.
- Chicas en descanso:
  - todas a la misma escala (Spine 0.2, pies en la casilla) con su animación `houseidle`, en lugar de ajustarse cada una a su caja;
  - colocadas en casillas libres del suelo con 2 casillas de margen alrededor de los muebles y separadas entre sí;
  - el chibi del senpai ya no aparece en el cuarto (solo las chicas, a petición de la usuaria).
- Muebles de suelo: se anclan en la esquina lejana de su huella `(x + largo, y + ancho)` con pivote abajo (HouseMap:getMapPosByInfo / HouseItem pivot Bottom); antes flotaban sobre sus casillas.
- Manage, al seleccionar un mueble:
  - aparece el anillo `house_select_box` con sus 5 botones: Flip arriba, OK a la derecha, Cancel a la izquierda, Store abajo a la izquierda y Details abajo a la derecha;
  - la huella se pinta en verde o rojo (`house_floor_unit_*`) según quepa;
  - añadido local: flechas isométricas (↖ ↗ ↙ ↘) para mover una casilla, además de arrastrar;
  - Cancel devuelve la posición anterior (o el mueble al almacén si acababa de salir) y OK no deja confirmar si no cabe.
- La barra "Rotate / Retrieve / Details" queda sustituida por el anillo.
- QA: 5 chicas del mismo tamaño y repartidas; mover la Tiny Table con las flechas, OK y Save → "Guardado".

## GXB2-CLAUDE-WAVE-052 (Dates: pantalla de la cita y regalos)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). `web/dates.js/.css`, `gxb2/relations.py`, `tools/extract_relations.py`, `web/wallpaper.js`.
- DatesWindow en coordenadas de `dates_window.prefab` (lienzo 720×1280):
  - la ilustración colocada como en la ficha: PartnerImg en `partner_picture_xy`, imagen fija a tamaño real o Spine con −200; tocarla reproduce una línea de voz;
  - nombre con su facción, pestañas Gift / Voice (`dates_icon05/06`);
  - panel `dates_bg02` con el icono de intimidad (tocarlo abre el Oath) y 5 corazones;
  - "Tap to send gift", la caja de regalos en 2 columnas con marca de favorito, Gift Box y Make Gift;
  - burbuja de diálogo y botones Discuss / File / Date.
- `Wallpaper.mountArt(host, id, 'xy'|'xy2')`: la colocación común (portada, Dates).
- Regalos (corrección de reglas):
  - Make Gift (DatesGiftsWindow) fabrica el regalo **elegido**, en pestañas Food / Toy / Accessory / Variety (`dates_gifts`), 10 Gift Shards cada uno; antes daba uno al azar;
  - nueva Gift Box (objeto 43, gift 30001): 1 regalo del dropbox 800001 más 3-5 Gift Shards (800002).
- Partida dev: recarga 43 / 44 / 45 y los 40 regalos.
- Tests: `tests/test_relations.py` (Make elige y no cobra si falta el regalo; Gift Box).
- QA: regalo favorito a Iron Fist → +40 y "For me?! Really?"; Make Rum ×1; Gift Box abre.

## Eventos — tanda052, 2026-09-30

[T][P][M] Jigsaw (37) y Puppet Parade (189) jugables en Inicio → Eventos → Exclusives. Jigsaw conserva 24 ilustraciones, las 216 piezas originales, intercambio de dos posiciones por 1 energía, 50 compras progresivas y seis hitos. Puppet conserva 17 hitos y sus premios; las marionetas no se consumen al cobrar. Progreso persistente y premios protegidos contra doble cobro. LOCAL-070 sustituye el calendario/suministro del servidor: eventos permanentes, 3 energías y 40 marionetas diarias, premios directamente a la bolsa. Falta la presentación/animación completa y el calendario original. Suite completa: 303/303 OK; siete pruebas propias y QA visual con partida temporal. [Evidencia](validation/events-2026-09-30/README.md). Próximo foco: Firework Project, Winning Pair y calendario de eventos.

## GXB2-CLAUDE-WAVE-053 (Dates según las capturas: CV, placa, File, Date y Oath)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). Referencias de la usuaria: Dates de Sonya, Dracula, Lovely Date y Friends.
- Pantalla:
  - PartnerNameTag (`partner_name_frame_bg`, facción, estrellas y nombre) y el CV en una píldora arriba a la derecha (`partner_text.cv_name`, 460 chicas); ambos, las pestañas y el panel suben arriba, como en la captura;
  - `dates_bg02` y `dates_btn` en 9-slice (antes se estiraban enteros);
  - los regalos con marco de calidad y la barra inferior (FrontPage / Girls / …) visible.
- File (DatesDataWindow): los textos `partner_data_id` → `appointment_partner_data_text`, que se desbloquean a 20 / 40 / 60 / 80 de intimidad, con colores `[c][f55090]`, más el bonus de intimidad.
- Date (DatesStoryWindow): la cadena `partner_achievement` de las 15 chicas que la tienen:
  - tipos de tarea: 3 nivel, 4 intimidad, 6 wallpaper, 2 forjas (`missions.totals.forge`), 5 consumir (se paga al completar, LOCAL-070);
  - `date_step` desbloquea y reproduce la historia `partner_plot` (nuevo `tools/extract_partner_plot.py` → `data/partner_plot.json`, 6421 líneas, `/api/relations/plot` + `Story.play`); Replay para las ya vistas;
  - `state.dates_info` en el snapshot.
- Oath (DatesPledgeWindow, el objetivo de casarse):
  - intimidad, bonus y el texto VOW_OATH;
  - el sello `dates_icon41` → `dates_icon42`, con un Oath Ring; el máximo sube a 12000;
  - se abre al tocar el icono de intimidad.
- Tests: `tests/test_relations.py` (cadena de Date). Suite completa OK.
- QA: Saint → wallpaper → historia 1 (22 líneas); 260 regalos favoritos → 10000; Vow → Oath formado.
- Pendiente: Discuss (comentarios en línea) y el evento Lovely Date (capturas 3, 4 y 6 de la usuaria).

## Firework Project — tanda053, 2026-09-30

[T][P][M] Firework Project 196 jugable en Inicio → Eventos → Exclusives: fabricar ×1/×10, cuatro resultados ponderados (15/50/20/15), coste de 25 polvos, nivel por 100 polvos gastados, 21 canjes con niveles y límites originales. No confundir con Firework Display 274. Estado persistente; operaciones inválidas no gastan recursos. LOCAL-071: archivo permanente y 250 polvos por día local para sustituir fuentes del servidor. Faltan calendario, fuentes originales de polvo y animación Spine de fabricación. Siete pruebas específicas; suite completa 311/311 OK. [Evidencia](validation/firework-2026-09-30/README.md). Siguiente foco: Winning Pair y calendario de eventos.

## GXB2-CLAUDE-WAVE-054 (Chicas: Anima Gear, Limit-Break y constelaciones del Astral Core)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). `web/girl-ui.js/.css`, `web/souls.css`, `web/style.css`, `tools/extract_astral.py`.
- Hover: la elevación global de `button:hover` (y el `scale` del Front Page) usaba `transform` y **sustituía** el `translate(-50%, -50%)` de los botones centrados.
  - Síntoma: los huecos del Anima Gear, los nodos del Limit-Break y del Astral Core, etc. saltaban al pasar el ratón.
  - Arreglo: ahora usan las propiedades independientes `translate` / `scale`, que se suman al `transform`; las excepciones (Guild Lab, territorio, Dorm) usan `translate:none`.
- Anima Gear › Replace: la rejilla de 5 columnas desbordaba (iconos fijos de 108u); ahora se ajusta.
- Limit-Break (`potentiality_component2`):
  - `partner_potential_bg_big` es el fondo de alas (con espejo), no el marco de cada nodo;
  - los nodos llevan `skill_icon_bg` 86u y el candado `academy_assessment_lock`, en W en (-228,88) (-132,-16) (0,30) (131,-17) (231,88), unidos por líneas `partner_potential_light/dark_big`;
  - ya no hay barra `potentiality_bg01`; la ventana de Limit-Break tiene sitio para el esquema.
- Astral Core (constelaciones):
  - pestaña (PartnerDetailWindow content_6): emblema de la facción `group.star_origin_img1` (Cosmos: `partner_group7`) en el `xy` de `star_origin_list`; estrellas de 48u en `xy × 0,66`, en estado `star_origin_bg_xy_zh / kq / dl` (bloqueada / abierta / con nivel), con líneas `…_1`; botón Empower;
  - Node Upgrade (StarOriginDetailWindow): el paisaje `star_origin_img2` detrás, estrellas `…_sj_*` de 70u con el nivel `n/60` y el marco `sj_xz` en la seleccionada; tocar otra estrella cambia de nodo;
  - antes eran círculos genéricos con números romanos, que además se solapaban;
  - las cinco pestañas de la ficha caben en una sola línea.
- QA: Succuba a 15★ (herramienta dev); Limit-Break con alas y W; Astral Core con emblema y estrellas; Node I ×10 → 10/60 y estrella dorada.

## GXB2-CLAUDE-WAVE-055 (CV en la ficha, Marriage Certificate, Manga, Excursiones)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). Referencias: `docs/references/2026-09-30-user-c/01-06`.
- CV (seiyuu) en la ficha de la chica (`cvTag`, `web/assets/dates/cv.json`).
- Marriage Certificate (DatesPledgeWindow):
  - Groom/Bride, intimidad, fecha y sello, con la chica en su marco del prefab.
  - El Oath entrega la skin de boda, que aparece en el certificado (LOCAL-073, `test_oath_gives_wedding_skin`).
- Manga: las portadas se recortan de la primera viñeta.
- Excursiones:
  - Main Center (ExploreTrainingRoomWindow): 5 disciplinas, 3 huecos con chibi (`travel_train_set`), atributos Current/Next y coste por nivel.
  - Explore: botones «?» (TRAVEL_EXPLORE_HELP_U3) y «!» (detalle de los 6 cofres).
  - La ventana de mejora se abre encima con Level N / N+1, valores siguientes en verde y «Claim Stage g Chest n Time(s)».
  - La chibi exploradora reutiliza su canvas, lo que corrige el cuadro blanco por pérdida del contexto WebGL.
- Suite: 322 tests OK.

## GXB2-CLAUDE-WAVE-056 (Discuss: Partner Data Station «Student Files»)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). `web/station.js/.css`, `gxb2/relations.py`, `tools/extract_data_station.py`.
- Discuss, en la cita, abre PartnerDataStationWindow: el cuaderno de anillas con las pestañas Strategy, Lineup y Review, la carta de la chica y el cambio entre sus versiones reeditadas.
- Datos: `tools/extract_data_station.py` genera `web/assets/station/station.json` (143 chicas, 104 con formaciones, 38 etiquetas) y copia los sprites `station_*`.
- Strategy: radar de 5 ejes (Attack, Armor, Speed, Control, HP, sobre `direct_partner_point_full` = 5), Tags, Description, Rank, las 4 habilidades recomendadas con icono y nota, y las 2 antigüedades recomendadas.
- Lineup: Dummy Test, Tests y Guild Boss con la «Popular Lineup», su nota de Popularity en estrellas, 2 chicas delante y 4 detrás, y Details.
- Review: Like, etiquetas propias (Customize, máximo 3) y comentarios propios (LOCAL-074).
- Tests: `test_data_station_review`. Suite: 323 tests OK.

## GXB2-CLAUDE-WAVE-057 (Retoques con `~/Downloads/Reference`: Varsity / Junior Varsity y Game Assistant)
Status: [~] en curso 2026-09-30 (Claude, sesión campaña/pulido). La usuaria pasó 4313 capturas en 14 carpetas; se revisan por zonas.
- Varsity y Junior Varsity (`6. Varsity & Junior Varsity`, 22 capturas):
  - las filas del ranking siguen `arena_window_item`: fondo `9gongge17`, y `9gongge30/31/32` para el top 3; icono de jugador con su nivel, nombre, poder, etiqueta de servidor («S1», un único servidor local) y «Points»;
  - tocar el icono de un rival abre su ficha con la defensa (1 equipo en Junior Varsity, 3 en Varsity); el backend manda `id`, `lv`, `power` y `teams` en `board`;
  - barra superior (oro, gemas, volver) y barra inferior como en el juego; textos «Ending in:», «Points», «Reward», «Defense».
- Game Assistant (`Game Assistant`, 114 capturas):
  - la ventana sigue `game_assistant_window.prefab`: el pingüino, 4 pestañas (Daily / Challenges / Growth / Guild), secciones con título, filas ilustradas YES/NO, contadores ⏮ − n + ⏭, e «Initiate this page» / «Initiate All»;
  - pasos nuevos en `assistant_run`: compra de Alchemy con gemas (hasta el límite VIP), Daily Quiz (Raid de la dificultad más alta superada), Raids de House Exam con certificados, recursos y Tasty Bread de la Excursión, firma del gremio y empezar pedidos del Cafeteria;
  - el Overview lista cada paso con sus premios, o el motivo si se omitió;
  - test: `GameAssistantPagesTests`.
- Menú › Help (`Menu`, 187 capturas):
  - antes abría el Game Assistant por error; ahora abre SettingUpInfoWindow con las pestañas Help / FAQ;
  - 11 temas de ayuda y 4 de FAQ que se despliegan (`setting_text`, con `tools/extract_help.py` → `web/assets/menu/help.json`);
  - Status Icons con sus 104 iconos de estado; Faction Aura con las auras de `group_buff`.
- Excursión › Explore (`Excursion`, 167 capturas):
  - con un evento pendiente, el nombre aparece sobre la escena («Help Seeker», «Market»…) y abajo salen «Go» con su coste y «Retreat» subrayado (ExploreAdventureWindow.setBtn), en vez de una tarjeta flotante;
  - bocadillos originales: TRAVEL_MAIN_TEXT38 (Food Truck) y 65 (mercader); el que pide ayuda muestra el objeto que quiere;
  - «Girls List» en el botón de cambiar explorador: hasta 6 chicas y la opción Random. Se guarda en `localStorage`, como el original, que también la guardaba en el cliente (`xwtx_chosen_models`);
  - Auto Explore con interruptor; en el detalle de cofres, «Guaranteed Rewards» y el pie «Chests at or above Stage 4 provide 2 Random Rewards».
- Outfit Showcase (`5. Outfit Showcase`, 163 capturas):
  - la cabecera (logo, descripción, tienda, puntuación) queda bajo la franja de monedas, como en el juego;
  - barra inferior de navegación; Claim solo aparece si hay Tags pendientes.
- Dormitorio (`3. Dorm`, 145 capturas):
  - tocar el Comfort abre HouseComfortWindow con lo producido (oro, gemas y Crystal Chisel) y Collect (LOCAL-075, `tests/test_house_income.py`);
  - el Game Assistant gana «Claim Dorm resource».
- Herramienta de QA: `scratchpad/shot.mjs` (Chrome headless por CDP contra el puerto 9180 con la partida de desarrollador) para capturas cuando la ventana de la app está minimizada.
- Suite: 325 tests OK.
- Anotado para más adelante: Elite League (51 capturas: liga por equipos con amigos) no existe todavía; es una función nueva, no un retoque.

## GXB2-CLAUDE-WAVE-058 (Fantasy Book, desfases de Manga y Outfit Showcase)
Status: [x] hecho 2026-09-30 (Claude, sesión campaña/pulido). Capturas: `~/Downloads/Reference/Fantasy Book`, `5. Outfit Showcase`, `docs/references/2026-09-30-user-c/01-manga.jpg`.
- Fantasy Book (nuevo, LOCAL-077): `gxb2/fantasy_book.py`, `tools/extract_fantasy_book.py`, `web/fantasy-book.js/.css`; se abre desde el icono «Libro» de la portada.
  - Progress: 50 niveles con Basic Book (reclamable) y Luxury Book (bloqueado), «Current Pages», compra de niveles con gemas y Claim All.
  - Task: Daily / Weekly / Extra con barra de progreso, Claim y el sello «Collected».
  - Exchange: Crystal Leaf / Floral Stamp, y los sorteos de Flora Bookmark con sus probabilidades.
  - Trophies: los logros generales.
  - Tests: `tests/test_fantasy_book.py`.
- Manga: la regla `.sm-banner img:first-child` estiraba la portada del último episodio. Ahora el marco y la portada siguen `comic_window.prefab`, con el rótulo «NEW» (`comic_word_en_en`).
- Outfit Showcase:
  - la Showcase Store tiene pestañas Buff / Rare / Common, con cuenta atrás, «Purchase limit», «n stack(s) in active» y agrupada por Stage; las mejoras son jugables (LOCAL-076, `tests/test_showcase_buffs.py`);
  - la ventana del hueco sigue DressShowChooseWindow: puntuación total, los 5 huecos A–E, «Slot X · Slot Score», Display, filtros por parte y cuadrícula;
  - la flecha derecha del Booth info ahora apunta a la derecha.
- Suite: 331 tests OK.

## GXB2-GITHUB-068 — Repositorio privado y ejecución autónoma
Status: [X] cerrado 2026-09-30. Usuario autoriza Armenidez/gxb2-local privado con todos los assets necesarios.
Files claimed: README.md, .gitignore, tools/bundle_voices.py (nuevos), web/assets/voices/ (MP3 faltantes), metadatos Git; documentos de coordinación por adición. No se cambian archivos de la tanda Claude ni partidas. Excluir state, bases SQLite, exports de recuperación, secretos y temporales. Verificar voces completas, arranque desde copia limpia y privacidad/remoto antes de cerrar.

GXB2-GITHUB-068 ampliación Windows: usuario solicita arranque también en Windows. Reclamo gxb2/battle.py solo selección de intérprete; Iniciar-Windows.cmd, runtime/luajit-windows-x64.exe y documentación/licencia/procedencia, comprobación Windows de arranque/combate. Referencias y tests quedan locales a petición del usuario; se retiran de la versión final sin borrar originales. Tandas de assets 1–7 subidas.

GXB2-GITHUB-068 cierre: https://github.com/Armenidez/gxb2-local privado confirmado. 27.022 assets, incluidas 6.108 voces; recursos enviados en siete tandas. Código/datos/runtime e instrucciones incluidos. State, bases SQLite, exports personales y credenciales excluidos desde el inicio; tests/docs de capturas retirados del árbol final a petición del usuario (se mantienen locales). No se borraron fuentes ni partidas ni se detuvieron servidores habituales.
Verificación: 331 tests antes del traslado; 11 tests de backend tras seleccionar intérprete por plataforma; copia Git limpia con entorno nuevo y partida nueva: health/UI/bootstrap/LuaJIT/PNG/voz OK. Windows Server 2022 x64 vía GitHub Actions: runtime, combate determinista, atributos, Iniciar-Windows.cmd, HTTP, partida nueva y voz OK. Ejecución aprobada: https://github.com/Armenidez/gxb2-local/actions/runs/36729034925. LuaJIT Windows exige GC64 desactivado para el bytecode original; procedencia y compilación en runtime/LuaJIT-WINDOWS-BUILD.md. Primera revisión falló por ruta del comprobador, segunda detectó GC64 incompatible; ambas corregidas antes del cierre. No certifica todas las pantallas en Windows ni Windows ARM. Claims liberados.

## GXB2-TABLES-069 — Recuperación íntegra y mapa de tablas
Status: [W:GPT] 2026-10-01. Solicitud: localizar tablas pendientes y recuperar contenido por ingeniería inversa.
Files claimed: tools/recover_client_tables.py (nuevo), data/recovered/ (nuevo), TABLAS_RECUPERADAS.md (nuevo); adiciones a README/LEEME/master/estado/workboard. Fuentes originales solo lectura. No modifica reglas existentes ni partidas. Objetivo: exportación literal con esquema y hashes, textos ingleses, consumidores cliente y referencias locales verificables; distinguir recuperación de integración jugable. No reclama archivos de tandas Claude.

GXB2-TABLES-069 cierre `[D]` recuperación / `[P]` integración global, 2026-10-01. 904/904 tablas, 17 wrappers resueltos con prioridad/orden original; 202.878 filas físicas (321.434 contando wrappers), 252 tablas inglesas/73.656 filas. 586 tablas sin referencias léxicas previas, no ausencia de sistemas. Añadido tests/test_recover_client_tables.py local (5 casos); 336 tests completos OK, dos avisos BrokenPipe por desconexiones de cliente durante las pruebas. 904 hashes de fuente/exportación verificados; seis tablas idénticas al extractor independiente previo; textos ingleses idénticos celda por celda a SQLite. Sin cambios de gxb2/server/web ni partidas. Dossiers en data/recovered/systems para ArenaTeam/FairArena/GuildWar/GrowthDiary/NewbieCamp/ArenaAllServerNew/ArenaAllServerScore/PetTraining: tablas, métodos/líneas, mensajes/IDs, schemas y evidencias originales. Archivo base INVENTARIO_CLIENTE no regenerado: su mapa LOCAL arrastra estados históricos que requerirán revisión manual. Fuentes originales intactas. No se subió a GitHub ni se actualizó el ZIP de distribución del juego. Claims liberados. Relevo: escoger un dossier, revisar fuentes y respuestas del servidor, definir contrato local y probar antes de declararlo jugable.

## GXB2-GROWTH-070 — Growth Diary jugable
Status: [W:GPT] 2026-10-01. Reclamo tools/extract_growth_diary.py, data/growth_diary.json, gxb2/growth_diary.py, tests/test_growth_diary.py, web/growth-diary.js/.css, web/assets/growth-diary; integración en gxb2/engine.py, server.py, web/app.js, web/index.html; adiciones a documentos de estado. Implementar capítulos/misiones/premios originales y métricas respaldadas por saves/acciones. Reglas históricas desconocidas como adaptación explícita; objetivos sin equivalente quedan visibles bloqueados. No modificar partidas habituales ni fuentes; QA sobre DB temporal.

GXB2-GROWTH-070 cierre 2026-10-01 `[T][P][M]`. 40 capítulos/160 misiones, 121 métricas y 39 pendientes listadas en GROWTH_DIARY.md. Baselines de objetivos estrella al desbloqueo; progreso máximo conservado en _save_profile (sustituye UPDATE existentes sin escrituras en snapshot), registro de oro idle/Echoes, Transfer, Market/League Store, BFF/Shards/Graduate/Exchange/High Stakes, Internship 4/6★. Sin cambios de premios existentes. Type15 distinguido por registros70/157; cristales por item_lv original3/5/8/11. 343 tests OK (7 nuevos), dos JS sintácticamente válidos, QA visual partida temporal: cuatro misiones + capítulo200 gemas + avance2 + recarga y capítulo1 reclamado. Una expectativa errónea de test se corrigió según tabla; suite repetida completa OK. No se tocaron partidas habituales ni servidores habituales; código no subido a GitHub y ZIP de juego no regenerado. Datos/extractor/UI/backend/docs listos, claims liberados. Próximo: métricas de funciones ya presentes y rutas Go que faltan; después otros dossiers.

GXB2-GROWTH-070 complemento: actualizado mapa LOCAL de tools/build_client_inventory.py con GrowthDiary y aviso explícito de estados históricos/referencias léxicas; inventario regenerado (48/71 estados declarados, 320/904 referencias de tabla; no porcentaje certificado de juego). QA temporal cerrada y servidor temporal detenido; captura e informe entregables en outputs del chat. No se detuvieron otros servidores.

## GXB2-CONTENT-071 — Ampliar Growth Diary y contenido recuperado
Status: [D:GPT] 2026-10-01. Diary 154/160, 33 objetivos adicionales; Newbie Camp 3 etapas/33 filas, 28/30 tareas visibles conectadas y tres premios automáticos originales. HTTP y protocolo Growth/Rookie, guardado/rollback/concurrencia/rachas. Suite general 352 OK, 11 tests de ampliación OK (dos nuevos después); QA Camp premios/etapa2/reinicio sin errores, scripts y assets 200. LOCAL-079, NEWBIE_CAMP.md y Diary actualizado; inventario 49/71 modelos declarados, referencias léxicas 322/904. Servidor temporal propio cerrado; fuentes/partidas/servidores habituales intactos. Reservas liberadas engine, Diary, módulos de hooks, Newbie, web, extractores y documentación. Relevo: Friend Boss bloquea capítulo25; luego Training/Ulticore y Practical Work, Chat/Elite League. No auto-completar ni sustituir Practical Work por Soul Land.

## GXB2-CONTENT-072 — Friend Boss, Training, Ulticore y Practical Work
Status: [D:GPT] 2026-10-01. Datos originales normalizados, diez hashes verificados, backend/transacciones/protocolo Friend Boss y Training/Ulticore, UI y Practical Work con motor original y premio final por correo. Diary157/160; pendientes116/130/160 por diez etapas antiguas frente a ocho actuales. 364 tests OK, diez nuevos; QA nativa/web aislada y captura. LOCAL-080 y SISTEMAS_PENDIENTES_RECONSTRUIDOS.md documentan calendario/damage local y límites. Claims liberados sobre engine, módulos, server, web, extractores y docs. Relevo: Chat/Elite League, apoyo social Friend Boss, calendario/protocolo de Practical Work y discrepancia de etapas. Sin push ni regeneración del instalador; paquete incremental separado.

## GXB2-NAV-073 — Chat y Co-op en Amigos
Status: [D:GPT] 2026-10-01. Icono azul original chat_icon_v3_h5 en borde izquierdo de Inicio, Chat separado de Correo y borradores conservados en Chat. Amigo cuarta pestaña Co-op identificada en FriendWindow:getItem(4)=FriendAssistant2; Friend Boss integrado, rutas Go y retorno del combate coherentes. Acceso independiente Training & Bosses retirado; Training sigue en Servant. 18 tests relacionados OK, JS/diff OK, QA temporal con capturas. Servicio social pendiente; no se simula envío ni completa Newbie Chat. Claims liberados web y docs. Servidor propio QA localhost:55321 disponible para la revisión del usuario, PID en validation/navigation-2026-10-01/pid.

## GXB2-CAMPAIGN-074 — Estados de botín y escena
Status: [D:GPT] 2026-10-01. Montaña Spine guajijiemian original con RGB/Alpha y umbrales originales; Collect real y aviso por tiradas, contador que conserva economía histórica y reloj de botín independiente. Chibis190 unidades centrados y tres chicas/dos monstruos según BattleHangUp. ProtectDoggy icono/ruta identificados, minijuego pendiente; campaña premio real Claim/etapas pendientes y vista de dos premios. Monedas/EXP chicas alineadas y abreviadas también tras actualizar. Corregido fort_finish como número de capítulos terminados, no flag; 13-8→12 capítulos, 13-10→13. Dos pruebas nuevas; suite366 OK, JS/diff OK, QA aislada/capturas. No se revocan premios reclamados ni se tocan partidas habituales. Claims liberados. Servidor QA propio59074 listo para revisar.

## GXB2-CAMPAIGN-075 — Cambio de patrulla y guías ilustradas
Status: [D:GPT] 2026-10-01. Change en fases superadas, vista previa de todos los capítulos sin desbloquear, monedas reducidas sobre Collect, loot compacto y primera victoria.14 guías/26 páginas originales (15 con prefab,11 adaptadas),65 sprites, biblioteca y ayudas contextuales.13 pruebas relacionadas OK,66 assets HTTP verificados, hashes/JS/Python/diff OK y QA aislada Change/persistencia/vista50-1/guías. Claims liberados web/server/extractor/docs. Servidor QA59074 disponible.

## GXB2-LAYOUT-076
Status: [D:GPT] Unión batalla/suelo en fila de recursos, contadores reducidos y monedas apoyadas encima de Collect. Biblioteca/entradas extra retiradas; guías en ? propios y Exchange página2. QA menú, Enrollment/Internship y fondos, ocho JS/diff OK. Claims liberados web/docs. Ver CAMPANA_FONDOS_AYUDAS_076.md.

## GXB2-LAYOUT-077
Status: [D:GPT] Campaña: suelo RGBA original, plantas delante del oro a ancho completo, conexiones continuas centradas, sin scrollbar, Fight/libro/regalo más abajo, cápsula/Collect con bordes conservados. Internship: barras/bandas/botones con nueve cortes y Refresh original junto a filtros; coste previo, bloqueados/en curso protegidos. Ocho pruebas Internship OK, JS/Python/diff OK, QA visual y capturas. Claims liberados web/extractor/docs. Ver CAMPANA_CAPAS_Y_BORDES_077.md.

## GXB2-CLAUDE-WAVE-059 (Showcase, Dorm vivo, Book por temporadas, Hearts y Calendario)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). Petición de la usuaria con captura de la Outfit Showcase.
- Outfit Showcase: la barra superior muestra oro y gemas centrados (los Tags solo en la tienda); la recompensa diaria se entrega al entrar («Rewards sent at 0:00») y desaparece el botón Claim.
- Dormitorio (LOCAL-083):
  - chibis nítidas: `GxbSpine.mount` acepta `resolution` y el dormitorio dibuja con supermuestreo ×3;
  - las chicas caminan, se sientan, se tumban y reaccionan al toque.
- Fantasy Book: temporadas alternas «Fantasy Book» / «Restart the Engine!» con su arte, iconos y monedas (LOCAL-077 ampliado). Las tareas de Hearts y Friend Boss ya cuentan; Friend Boss lee `gxb2/friend_boss.py`, de la otra sesión.
- Hearts (LOCAL-081): `gxb2/hearts.py`, `/api/hearts/action`, barra de Hearts y botones en Amigos › Lista, y «Recommended» en Buscar. Test: `tests/test_hearts.py`.
- Calendario (LOCAL-082): `gxb2/game_calendar.py`, `state.calendar_info`; Eventos muestra solo los abiertos, con su tiempo restante, y un botón Calendar. Test: `tests/test_game_calendar.py`.
- Archivos compartidos tocados (cambios pequeños y aditivos): `web/events.js`, `web/home-menus.js`, `web/campaign-ui.js`, `gxb2/missions.py` y `gxb2/engine.py`.
- Suite: 371 tests OK.

## GXB2-CLAUDE-WAVE-060 (Trophies / Daily Tasks sin sprites estirados)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). `web/missions.js/.css`, sprites en `web/assets/missions`.
- Filas según `achievement_window.prefab` (AchievementItem 668×109): `9gongge17` en 9-slice; barra `pub_bar_bg1` con el relleno `pub_bar1` recortado al progreso (antes `activity_bar_thumb` se estiraba y se salía del marco); botón `blue_btn_60_60` / `white_btn_60_60`; sello `mission_awarded_en_en` en lo ya reclamado.
- El progreso se muestra acotado al objetivo (130/130 en vez de 400/130) y las cantidades grandes se abrevian (10M, 100K).
- Se retira la nota obsoleta de Daily Tasks.

## GXB2-CLAUDE-WAVE-061 (Enroll › Exchange según capturas, con sus efectos; guía ilustrada pág. 2)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). `web/enroll.js/.css`, `tools/extract_exchange_fx.py`, `tools/extract_img_guides.py`.
- Exchange rehecho sobre `prophet_replace.prefab` (708×908): dos paneles `prophet_bg02`, cartas PartnerCardLarge (vacía con «?», silueta `partner_card00`, carta con facción, nivel, nombre y estrellas), flecha, y botones Exchange (con coste) / Cancel / Save.
- Selector de chicas como hoja inferior con los 4 filtros de facción (prophet_choose_partner_window).
- Efectos Spine originales (ProphetReplace.LoadResource) en `web/assets/spine/fx_*`: `fx_guanghuan` (orbe sin selección), `fx_wenhao` («?» del resultado), `fx_saomiao` (barrido de 1,333 s que revela la carta), `fx_guangzhu` (columna de luz) y `fx_daiji` (anillo bajo cada chibi).
- El revelado aguanta redibujados (se calcula por tiempo transcurrido). El aviso de Oath usa una ventana propia en vez de `confirm()`.
- Partida dev: recarga Seals (20) y Portfolios (19).
- Guía ilustrada: `img_guide_prophet2` llevaba dentro una copia de `img_guide_arena2_zh_tw`; el extractor ahora ignora ramas `img_guide_*` ajenas (solo cambia Enrollment pág. 2: 42 → 24 nodos). Los números «n /» ya no se parten.
- QA: Fencer → propuesta → Save: la chica 94 pasa a 51007 y conserva Lv.100. Suite: 371 tests OK.

## GXB2-CLAUDE-WAVE-062 (Audio completo, efectos de combate, iconos y animaciones bajo demanda)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). Petición: aprovechar lo que falta de los archivos originales. LOCAL-084.
- Audio: de 23 a 371 efectos y de 6 a 17 pistas (`web/assets/sounds`, 51 MB).
  - `GxbAudio.id(n)`, `GxbAudio.skill(id)` y `GxbAudio.bgm(pista)`; sonidos de botón globales; tabla `ACTION_SOUNDS`.
  - El combate ya suena: 3258 habilidades con su sonido.
  - Menú › Music: Jukebox con las 7 pistas y las 10 canciones del Music Game.
- Efectos de combate: 420 esqueletos de impacto / área (`web/assets/battle-fx`, WebP) para 2704 habilidades; `battleAnimation.fx`.
- Iconos: catálogo de 2350 → 4646 objetos, +1587 iconos.
- Animaciones: cualquier Spine de «Animation (Misc)» (982) bajo demanda en `/assets/spine/<nombre>`; `GxbSpine.burst`.
  - Enganchadas: subir nivel (`shenji`), subir grado (`fx_ui_jinjie`), despertar (`fx_ui_zhanjijinjie`), forja (`fx_ui_zbhc_up`), Daily Login (`fx_login_finish`), VS de arena (`vs_shining`) y subida de nivel del jugador (`shengji`).
  - Portada: 23 escenas animadas de login elegibles en la ventana de Wallpaper.
- Sprites y fondos originales bajo demanda (`/assets/sprite/`, `/assets/bg/`).
- Archivos compartidos tocados: `server.py`, `web/app.js`, `web/campaign-ui.js`, `web/battle-animation.js`.

## GXB2-CLAUDE-WAVE-063 (Retoques con Reference: Land of Souls, Tsuruga y Guild)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). Capturas: la de Land of Souls de la usuaria, `Reference/1. Tsuruga Grand Shrine` y `Reference/Guild`.
- Land of Souls (`web/soul-land.js/.css`): pantalla principal rehecha sobre `soul_land_main_window.prefab`: mapa a tamaño nativo, logo y «Remaining Time», las 3 zonas con su icono (`soul_land.fort_img` + `xy`) y «Progress: n/50», árbol con el efecto `soul_land_award`, cantidad, «n/5 min» y Collect, botones Shop / Ritual y barra inferior. Tocar una zona abre la ventana de su fase (regla, premios, Skip, Fight).
- Tsuruga › Realm of Trials (`web/shrine.js/.css`): tres paneles `shrine_hurdle_select_way_bg1` con Environment (iconos `environment_*`, al tocarlos muestran la regla), Highest Score, Difficulty Level y Enter con el ticket. `data/shrine.json` gana `route_text[*].icon` (`tools/extract_shrine.py`).
- Guild (`web/guild.js/.css`, solo interfaz; `gxb2/guild.py` sin tocar): título por edificio y barra azul; Office con la ficha del gremio, aviso, miembros con avatar y rol, y Sign in / Log / Settings; Cafeteria con Order / Lv. Up, Get Order · Upgrade Order · Start Order y los pedidos en tarjetas con duración, estrellas, premios y barra de cuenta atrás.
- Sprites y fondos nuevos llegan por las rutas bajo demanda `/assets/sprite/` y `/assets/bg/`.

## GXB2-CLAUDE-WAVE-064 (Bots y pasada de pruebas por todas las pantallas)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). LOCAL-085.
- Prueba de humo: `tools/smoke.mjs` + `tools/smoke_steps.json` (Chrome headless por CDP contra el servidor de QA en 9180): abre 45 pantallas y sub-pantallas y recoge excepciones, errores de consola, respuestas 4xx e imágenes rotas. Uso: `SP=<carpeta temporal> node tools/smoke.mjs "$(cat tools/smoke_steps.json)"`.
  - Encontró y se corrigieron: excepción de PIXI al destruir un efecto de combate dentro de su propio `complete` (ahora se oculta y se libera en el siguiente frame); iconos de zona de Land of Souls con prefijo equivocado.
  - Resultado final: 0 errores, 0 imágenes rotas. Quedan dos 404 sin efecto visible: `/favicon.ico` y la carta de la skin 7235, que tiene imagen de reserva.
- Bots: rankings en Land of Souls, Tsuruga y Cafeteria; comentarios en Student Files; mensajes en el chat. Test: `tests/test_bots.py`.
- Archivos compartidos tocados: `web/home-menus.js` (chat), `web/guild.js`, `gxb2/engine.py`, `server.py`.

## GXB2-LAYOUT-078
Status: [D:GPT] Dorm: nav inferior ahora borderImageSource con nueve cortes, extremos sin estirar; Save/Cancel, Rest y comprar con bordes conservados. Trophies: integrada la actualización concurrente de sprites pub_bar y botones; ancho del relleno independiente del marco, lleno llega al extremo y vacío sin relleno; pestañas con cortes proporcionales. Newbie Camp/Growth Diary movidos a home-left. QA visual Inicio, Dorm, Rest y Trophies (0%, parcial, 100%); cuatro JS y diff OK. Sin cambios de economía/guardados. Capturas en outputs del chat 2026-10-01/si. Reservas liberadas.

## GXB2-CLAUDE-WAVE-065 (Guild según capturas: Office, Cafeteria, Gym y Playground)
Status: [x] hecho 2026-10-01 (Claude, sesión campaña/pulido). Capturas de la usuaria (Office, Cafeteria, Playground, Gym). Solo interfaz: `gxb2/guild.py` sin tocar.
- `web/guild.js/.css` rehechos sobre el lienzo 720×1280 con las coordenadas de `guild_window`, `guild_dininghall`, `guild_gym_window`, `guild_boss_window` y `guild_war_info_window`; sprites originales por `/assets/sprite/`. Fondo: mapa del territorio oscurecido, barra de oro/gemas y botón de volver. Se quitan las pestañas Office/Cafeteria/Gym (cada edificio se abre desde el territorio).
- Office: ficha (bandera, ID, Main Language, Member, Verification, Power Limit, Priority, nivel y barra), aviso, LOG · Mail · Sign In (con la cuenta atrás al firmar), miembros con nivel, cargo, espadas y última conexión, y Settings · Requests · Members · Recruit · salir.
- Cafeteria: pestañas Order / Lv. Up / Rank; tarjetas de pedido del prefab (horas, flecha de mejora con confirmación, plato, estrellas, recompensas, Start / barra / Finished); Lv. Up con los dos edificios, barra y Donate*1 / Donate*10.
- Gym: 9 cartas por página con flechas y puntos; carta actual con encaje y el efecto `jianxg`; al tocarla abre la ventana Boss (vida, Chances, Fight con su coste, ayuda, recompensas y Damage rank).
- Playground (nuevo, `guild-war`): Rest Area con los equipos de los 3 miembros simulados más fuertes, Score, Countdown y los botones; Register, Record, Rank y Competition Area avisan de que Guild War no está reconstruido (LOCAL: sin gremios rivales).
- Los contadores se actualizan sin repintar la ventana. `tools/smoke_steps.json` gana Lv. Up, Boss, Playground y Members. Prueba de humo: 0 errores; suite: 373 tests OK.

## GXB2-PORTRAITS-079
Status: [D:GPT] itemPicture prioriza retrato cuadrado original mediante girlIconSource y cadena host; sin fallback a ilustración vertical. SummonResult comparte fuentes verificadas y expone HeroIcon reutilizado al reclutar desde Shards. Shards aleatorios muestran iconos originales en vez de recuadro vacío; específicos usan retratos, sin URLs de characters inexistentes. QA: iconos940001/940003 cargados, 280 imágenes de Shards/resultado cargadas sin errores tras pruebas del usuario; retrato42001 de recompensa de nivel HTTP200. JS/diff OK, sin cambios de economía ni guardados. Auditoría: tres entradas de items sin retrato directo en archivo (55001,75700,75701), una antigua no visible y dos variantes; no se inventan retratos. Reservas liberadas app/SummonResult/docs.

## GXB2-SUMMON-080
Status: [D:GPT] Rangos reales de Shards/Dolls 5/6/9/10, awaken_lv original al adquirir, coste según cantidad; revelado espera textura, resuelve variantes/avatar y aplica posición/escala originales. 21 pruebas OK, 647 rangos auditados, QA visual Ghost Doll 9★ y Sakura. Entrada 55001 sin avatar/ilustración original. Servidor 59074 actualizado conservando DB. Claims liberados. Ver SHARDS_E_INVOCACION_080.md.

## GXB2-HERO-GLOW-081
Status: [D:GPT] Recuperados shiziui_touxiang y variante Cosmos; animaciones originales texiao01/02/03 según rango 10 o superior. Marcos hero_frame/hero_frame2 en Shards, chicas e invocaciones; ilustraciones originales de colección conservadas; avatares comunes con marco y brillo por rango. Avatar del jugador: 19 animaciones originales según marco en Inicio/Perfil/vista previa; estático oculto al animar. Un renderer compartido copia a canvases visibles, limpia tarjetas retiradas y pausa ocultas. Extractor reproducible y rutas de servidor añadidos. JS/Python/diff OK, QA visual colección y Shards sin errores, capturas guardadas. Claims liberados.

## GXB2-ENGLISH-082
Status: [D:GPT] Menús, navegación, botones, estados, avisos y ayudas web traducidos a inglés; facciones y Lv. unificados; formato en-US. Catálogo preparatorio localization/ui.csv de 1.294 entradas key/en/es_reference, sin selector de idioma aún. 71 JS y diff OK; QA visual FrontPage/Menu/Girls/Shards/Campaign/Campus/Internship; captura y catálogo en outputs del chat. Sin cambios de economía/guardados. Claims liberados. Ver INTERFAZ_INGLES_082.md.

## GXB2-CLICK-MAGIC-083
Status: [D:GPT] Recuperado fx_dianji original (texiao01 fondo/texiao02 controles) según WindowManager. Efecto global de clic/toque en capa top-layer sin bloquear interacción, escala del juego, un renderer reutilizado y RAF solo mientras anima; se oculta al terminar o esconder pestaña. JS/Python/diff OK; QA visual Menu/Campaign y navegación. Extractor reproducible. Sin cambios de partida ni servidor. Claims liberados. Ver CLICK_MAGICO_083.md.

## GXB2-CAMPAIGN-FIT-084
Status: [D:GPT] Oro animado ampliado hasta bordes con recorte de transparencia. sheetRoot deja de usar body al abrir Auto-Battle desde Campaign: fallback a GxbFrame, unidades relativas al overlay y límites 94%; slots de formación adaptables. QA visual oro y ventana 475/505 px, apertura/cierre sin guardar equipo. Dos JS/diff OK. Sin cambios de economía/partida. Claims liberados. Ver CAMPANA_ORO_VENTANA_084.md.

## GXB2-BATTLE-STATUS-085
Status: [D:GPT] 2-8 confirmado stage20/battle100020: seis aliadas/cinco enemigos. Escala y anclaje especial Sanctuary limitado a boss_bar; jefe normal centrado en formación, escala acotada y HUD visible/alineado. Estados originales:144 iconos/158 entradas, lifecycle buffOn0/1/2/3/4, acumulaciones y título inglés. Test JS lifecycle, sintaxis/diff y QA once modelos/iconos cargados sin errores. Preview temporal cerrado, partida intacta. Claims liberados. Ver BATALLA_ESTADOS_085.md.
