# Growth Diary — implementación local, 01/10/2026

40 capítulos y 160 misiones con textos, recompensas y navegación por capítulo. Se abre desde el botón **Growth Diary** de Inicio tras superar la fase 5 de campaña. Reinicia el servidor para cargar el código nuevo.

157 misiones conectadas a métricas/acciones locales; tres todavía sin seguimiento. Los premios de las misiones y capítulos se conceden una sola vez y se guardan. Un capítulo requiere reclamar sus cuatro misiones; las misiones con estrella empiezan a contar desde que se desbloquea su capítulo.

## Fuentes y comportamiento

- `GrowthDiary.lua`, `GrowthDiaryWindow.lua`, `GrouthDiaryMissionTable.lua`, `growth_diary_mission`, `getway`, función 54 y textos ingleses originales.
- 160 filas / 40 capítulos × 4; costes/premios sin rebalanceo. Misiones 70 y 157 comparten type 15 pero miden objetivos distintos: Servant Lv15 y Girl 15★.
- `tools/extract_growth_diary.py` genera datos compactos y copia ocho sprites originales.
- API HTTP `/api/growth-diary/action`, snapshot `growth_diary_info`, botón de inicio, selector de páginas, Go, Claim y estados Locked/Claimed.

## Adaptación local (LOCAL-078)

El backend original contaba el progreso. Se mide lo reconstruible del save y las acciones locales; no se inventa historial perdido de partidas antiguas. Las métricas se conservan al guardar para que retirar una chica o quitar equipo no borre objetivos alcanzados. Las lecturas del estado no escriben en la partida. Las baselines de misiones con estrella se toman al entrar al capítulo. La interfaz usa los sprites originales disponibles con disposición web; no se certifica reproducción exacta del prefab ni animaciones de cambio de página. El protocolo TCP original del diario todavía no está conectado; esta tanda usa la API web local.

## Validación

343/343 pruebas aprobadas, incluidas siete nuevas: premios exactos y doble reclamación; cuatro misiones antes de premio de capítulo; objetivos con estrella sin retroactividad; bloqueo/IDs inválidos sin mutación; progreso persistente; colisión de type 15; calidad de equipo/cristales; objetivos no conectados; reinicio, rollback, concurrencia y lecturas sin escritura. Sintaxis de los dos JS modificados válida. Primera corrida detectó una expectativa errónea del test (premio de misión 14: 1 millón, no 2); se corrigió el test según la tabla y se repitió la suite completa.

QA visual sobre `validation/growth-2026-10-01/qa.sqlite3`, partida temporal preparada: Inicio → Diario → cuatro reclamaciones → 200 gemas del capítulo → capítulo 2 → recarga/reapertura → capítulo 1 aún reclamado. Sin errores de consola. Avisos de conexión cerrada en los tests HTTP históricos no provocaron fallos. No se modificaron partidas habituales ni se reiniciaron sus servidores.

## Ampliación GXB2-CONTENT-071

33 objetivos adicionales: contactos locales, botones pagados (excluye tiradas gratis), oro Dorm realmente recogido, daño real del informe de Guild Boss, exploraciones y cofres de Excursion, muebles comprados, antigüedades de 2★/4★ conservadas, desafíos en fases 3/6, compras Patrol, intento de combate Sanctuary fase 9, examen House Exam por su ordinal original, Star Tokens consumidos, evolución de Servants, Old Campus completado/puntos, Elite Skills, Trial finalizado y nodos Astral mejorados. Contadores nuevos no reconstruyen historia ausente; métricas recuperables de la partida se conservan por máximo.

Las misiones especiales establecen su base antes de la primera acción del capítulo; preparar una lectura no modifica la base de datos ni registra progreso ordinario. Guild Boss sólo recibe daño de sus propios informes; los cofres en lote cuentan cada apertura exactamente una vez y no pierden historia al subir de nivel Excursion.

Mensajes originales GET_GROWTH_MISSIONS, GET_GROWTH_MISSIONS_AWARDS y GET_GROWTH_CHAPTER_AWARDS, flags de capítulos en login, premios y mochila persistentes. Un lote que incluye una misión no reclamable se revierte completo. Las rutas Go incluyen los sistemas locales incorporados.

## Misiones pendientes de conectar

| ID | Capítulo | Objetivo original |
|---:|---:|---|
| 116 | 29 | Pass Stage 1-10 in Practical Work |
| 130 | 33 | Pass Stage 2-10 in Practical Work |
| 160 | 40 | Pass Stage 3-10 in Practical Work |

## Relevo

Resolver la discrepancia de diez etapas en estos textos frente a ocho en las tablas actuales, sin completar automáticamente las misiones. Friend Boss, Training y Ulticore ya tienen seguimiento; Newbie Camp se documenta en `NEWBIE_CAMP.md`.

## GXB2-CONTENT-072

Friend Boss actual (99), Training Dummy (153) y Ulticore (156) conectados. Pendientes reales: 116/130/160 por discrepancia de Practical Work 10 etapas en textos vs ocho en tablas actuales. Consultar SISTEMAS_PENDIENTES_RECONSTRUIDOS.md para estado vigente.
