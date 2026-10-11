# Campaña: Change, vistas previas y guías originales — 075

Las fases superadas hasta max_stage ofrecen Change debajo de Loot. STAGE_HANG conserva los relojes y el historial de recursos/botín; las fases futuras únicamente muestran producción, botín posible y premios de primera victoria. Se pueden consultar todos los capítulos/dificultades, incluidos Nightmare y capítulo50, sin desbloquearlos. Fight continúa limitado a la siguiente fase y sus requisitos.

Se usa max_stage para Change: la lista de combates guardados puede ser incompleta en partidas antiguas. El servidor sigue validando la fase. El encabezado/escena representa la patrulla activa; recorrer otro capítulo no la cambia. Reward after representa las etapas restantes para terminar el capítulo del próximo trofeo tipo25, separado del botín aleatorio por fase.

Monedas originales Spine reducidas de900 a660 unidades de ancho y ancladas573; lienzo extendido a627 sin cambiar posiciones de actores. Recorte inferior573 evita tapar Collect y mantiene las monedas encima de la fila. Botín del detalle seis columnas y24vh, botones visibles debajo; primera victoria usa iconos correctos para oro/EXP.

## Guías

Tabla img_guide:14 sistemas,26 páginas.65 sprites PNG originales y traducciones inglesas.15 páginas reconstruidas de sus prefabs ingleses con posiciones NGUI, pivotes, jerarquía y tipografías.11 páginas sin prefab inglés disponible usan imágenes/textos originales con distribución adaptada, indicada en la vista. No se añaden funciones de servidor por mostrar una guía.

Biblioteca en Menú → Guías ilustradas y Menú → Help. Ayuda contextual: Graduate, Internship, Enrollment, High Stakes, Tests, Daily Missions, League, Dates, Hero Challenge, Crystal y Co-op/Friend Boss. Beach/Music/Jump disponibles en la biblioteca aunque la función esté pendiente. No se abren automáticamente ni alteran progreso. Graduate reproduce la lámina aportada. Visor con anterior/siguiente, biblioteca y cierre.

Extractor tools/extract_img_guides.py normaliza la tabla recuperada, localización y prefabs; copia sprites cut y guarda hashes de fuentes. server.py sirve únicamente archivos conocidos del directorio y los dos módulos nuevos.

## Verificación

13 pruebas existentes de campaña/reconstrucción OK (11.967s), incluyendo cambio de fase, persistencia, economía histórica, relojes y cap12h. Comprobación sintáctica de ocho módulos JS, compilación Python y diff sin errores.66 assets servidos y comparados byte a byte; hashes originales verificados y cada página contiene texto. QA navegador sobre partida temporal propia: Change13-8→13-7 conserva recursos; bloqueada13-10 y50-1 muestra loot/recompensas sin Change/Fight; Graduate sin marcadores de formato; Internship página2; Friend Boss adaptada; montaña por encima de Collect. El usuario puede continuar en localhost59074. No se tocaron partidas habituales.
