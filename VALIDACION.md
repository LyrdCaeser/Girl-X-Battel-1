# Graduate estrella naranja — GXB2-GRADUATE-058, 30/09/2026

Filtros independientes en una columna vertical bajo ?. 10★ usa `web/assets/girl-ui/star_orange.png`, igual a la referencia de Alice aportada; aplicado en filtro, cabecera, materiales y candidatos10★. QA navegador: activar filtro10 actualiza receta y todos los iconos con estrella naranja; vista `validation/graduate-2026-09-30/graduate-orange-star.png`. Sintaxis app.js OK. Sin cambio de reglas/backend.

---

# Graduate filtros on/off y orden — GXB2-GRADUATE-057, 30/09/2026

Filtros2–10★ independientes, todos off inicialmente; sin contadores, estrellas superpuestas debajo de ?. Sin filtros: primero recetas listas ordenadas por potencia estimada de la base (power si existe, o ATK+Armor+HP/6 y crecimiento local), después pendientes5★ y10★. Una entrada por nombre de chica, priorizando la receta lista; filtros múltiples también deduplican. Al completar se reconstruye la lista con el nuevo inventario. Nombre sin panel; icono≡ abre revisión de materiales; punto rojo para listas, ✓ para seleccionada. Escena usa overflow:clip para evitar desplazamiento interno del retrato/nombre.

`node validation/graduate-2026-09-30/check-list.cjs` OK: prioridad de listas/potencia, facción, filtros múltiples/off, deduplicado. Sintaxis app.js OK. QA navegador: filtros2 y3 on simultáneos, ambos off recuperan lista por defecto; botón≡ abre selector con base2★ y copia1★. Screenshot `validation/graduate-2026-09-30/graduate-toggles.png`. Backend intacto; última suite funcional318 OK. Vista9240 permanece abierta para la usuaria sobre la partida QA separada.

---

# Graduate iconos y disponibilidad — GXB2-GRADUATE-056, 30/09/2026

Lista derecha usa portrait(), el mismo avatar cuadrado del gacha, con facción y estrellas superpuestas. Cápsula muestra destino sin flechas: amarillas2–5, rojas6–9, dorada10. Menú calcula listas/total por facción con graduateSelection() y costes actuales; pendientes siguen seleccionables, listas llevan ✓. QA temporal: 3★ muestra1/7, Skarivine lista con40.000oro y materiales1/1; resto atenuado. Las demás estrellas0 listas; cambiar filtro actualiza receta. node --check app.js OK. Sin reglas/backend ni consumos nuevos; suite318 anterior. Captura `validation/graduate-2026-09-30/graduate-availability.png`.

---

# Graduate referencia visual — 30/09/2026, GXB2-GRADUATE-055

Retrato ampliado y diálogo sobre la escena; ayuda arriba a la derecha con filtro de evolución en cápsula debajo; sidebar dedicado a chicas; base y materiales en tarjetas compactas. QA en partida separada9240: filtro2→3 y cambio de facción/selección Selene4→5, botón visible, cantidades y selector actualizados. Sintaxis app.js correcta. Sin cambios de reglas/backend; suite318 anterior sigue como última verificación funcional. Captura: `validation/graduate-2026-09-30/graduate-reference.png`. Partida habitual intacta.

---

# Graduate y ascensión local — 30/09/2026, GXB2-GRADUATE-054

**318 pruebas, OK** (`validation/graduate-2026-09-30/tests.txt`). Siete pruebas nuevas cubren identidad y persistencia, consumos atómicos, bloqueos/duplicados/coste, facción y copias, recorrido completo 1→10★, cap250, atributos/power y combate Lua real. Sintaxis de app.js/girl-ui.js y compilación Python correctas.

QA visual en partida SQLite separada, puerto9240: Graduate nativo 4→5, filtro1→2, selector manual consume #3 conservando #1, oro1.000.000→990.000, base11001/awake1, copia#2 intacta; receta2→3 habilitada. Facción Ángel/2→3 limpia retrato y materiales previos y desactiva botón. Captura `validation/graduate-2026-09-30/graduate.png`. Retrato reducido, marcos y materiales compactos, botón completo y margen frente a la navegación. Fuentes y partidas habituales sin modificar. Balance de LOCAL-072 propio, sin habilidades adicionales ni evolución superior a10★. No se certifican todos los móviles ni cada receta histórica en interfaz.

---

# Verificación — checklist, Chimes y partidas (30/09/2026)

**GXB2-CHECKLIST-CHIME-049:** `python3 -m unittest discover -s tests` → **274 pruebas, OK**. La prueba nueva de Chimes alterna dos partidas con bonificaciones distintas y comprueba atributos y argumentos de combate. Las dos pruebas nuevas de archivo hacen copia de una base SQLite activa en WAL, modifican la partida viva, restauran la copia en otra ruta y comprueban que contiene el estado previo; también rechazan un origen inválido y un destino existente. `python3 -m py_compile` de los módulos de combate pasó. Todo usó bases temporales; no se abrió ni modificó la partida habitual. Durante la suite los tests HTTP produjeron avisos `BrokenPipeError`/`ConnectionResetError` al cerrar clientes de prueba; no causaron fallos.

Quedan sin verificar: migración de formatos antiguos, restauración dentro de la interfaz, import del guardado original y todos los reportes/skills originales. El checklist actualizado usa `[P]` para esos sistemas globales.

---

> **Iconos corregidos — 29/09/2026, GXB2-PORTRAITS-008.** El selector legado conocía81 IDs y dejaba Selene y otras chicas como cuadros oscuros. Ahora usa el avatar original de cada registro:439 PNG íntegros,637 registros y359/359 chicas visibles. Comprobado en invocación y formación sobre partida temporal. [Causa, pruebas y relevo](validation/portraits-2026-09-29/README.md). No cambia progresión ni saves.

# Verificación actual — 29/09/2026

GXB2-SLOTS-LUCKY-004: **49/49 pruebas**,11 JS propios válidos. [Registro y alcance](validation/slots-lucky-2026-09-29/RESEARCH.md), [resultados QA](validation/slots-lucky-2026-09-29/qa-result.json), [capturas](validation/slots-lucky-2026-09-29/normal.jpg). Normal50/40,50 puntos, Lucky compra/límite y Skip/bulk tras recarga comprobados en fixture normal, sin DEV. Fondos/idle originales de ambos dealers visibles. No se certifica touch/responsive/audio/FX ni juego completo. Registros siguientes son históricos.

---

# Referencias/UI — GXB2-REF-UI-002, 29/09/2026

**47/47 pruebas** pasan otra vez: [tests.txt](validation/reference-ui-2026-09-29/tests.txt). Once JS propios pasan sintaxis. Backend/tablas de la tanda anterior conservados; no se reemplazan premios por los de una captura de otra versión.

Revisión visual en servidor de pruebas 9190/9191, bases temporales: Exchange con panel superior/inferior y chibis originales Nona/Zombia, y selección de Nun. [Captura de selección](validation/reference-ui-2026-09-29/exchange.jpg). Selector Slots10→20→50: dos botones de compra, costes8/16/40, saldo de tickets sin aumento/disminución al cambiar selector; [captura ×50 por 40](validation/reference-ui-2026-09-29/slots-50.jpg). Los botones de compra aparecen deshabilitados cuando no hay tickets, conservando el control de saldo.

No se ejecutó una compra ×50 en esta QA visual: coste/serialización/persistencia permanecen cubiertos por las pruebas de backend, no por esa captura. Herramienta de navegador produjo respuestas de acción inconsistentes y la recarga final no completó la carga en el estado observado; **persistencia visual de la preferencia tras recarga y click/touch habituales siguen pendientes**. Código conserva la preferencia en localStorage; no declararlo probado solo por existir. Montajes tardíos cancelados por generación en código; stress/GPU leak testing pendiente. No se detuvo el servidor habitual ni se usaron las partidas reales.

[Nueve capturas originales y comparación](docs/references/2026-09-29/README.md), [hashes finales](validation/reference-ui-2026-09-29/inventory.json), [handoff](AI_WORKBOARD.md). Las5 rondas de Slot Points en la imagen 02 son otra variante de premios frente a8 en datos locales; no se cambiaron tablas. Holiday Break Exchange, Atelier, Entrance Exam, Limit-Break/Astral Core y Voice son referencias investigadas, no sistemas implementados por esta tarea.

---

# Validación de reconstrucción — GXB2-RECON-WAVE-001

Cierre 29/09/2026 (sesión iniciada 28/09). **47 pruebas aprobadas** con bases temporales, log [tests.txt](validation/reconstruction-2026-09-28/tests.txt). Once JS propios pasan sintaxis: [javascript.txt](validation/reconstruction-2026-09-28/javascript.txt). Fuentes, reglas e incertidumbres: [RESEARCH](validation/reconstruction-2026-09-28/RESEARCH.md).

Nueve casos nuevos cubren: propuesta Exchange→restart→save y conservación del build/formación; descarte/rechazos/consumo protegido; lock vía esquema y persistencia; costes/premios limitados/Slot Points; descuento/gates/free y paid refresh; VIP y refresh24h con historial; semanas ISO/reloj atrás/progreso legado; idle histórico/cap/remainders/botín; recursos HTTP y pureza de GET. Los rechazos comparan el estado persistente. Pruebas antiguas de snapshots usan reloj fijo para no confundir el paso de un segundo con una escritura.

QA visual en **partida temporal Normal**, nivel80 y recursos concedidos solo a esa fixture, sin DEV, puertos9180/9181. Normal×1: tickets10→9, Coupons500→510, premioEXP. Normal×10: tickets9→1, Coupons510→610, premios y límite de Miya agotado. High Stakes×1: fichas12→11, premioOro, Coupons 610 sin aumento; diez deshabilitado porVIP. Exchange: Portfolios300→280, Zombia→propuestaFlash; recarga mantieneFlash y280; guardar transforma chica manteniendo número de integrantes. Detalle Flash: Bloquear→Desbloquear. Sin errores de consola observados. Se usó activación por teclado accesible: el control de clic del navegador de pruebas no fue fiable; **clic/touch en un navegador habitual queda pendiente**.

Capturas: [Slots](validation/reconstruction-2026-09-28/slots-qa.jpg), [propuesta Exchange](validation/reconstruction-2026-09-28/exchange-qa.jpg), [Exchange guardado](validation/reconstruction-2026-09-28/exchange-saved-qa.jpg), [lock](validation/reconstruction-2026-09-28/lock-qa.jpg). Evidencia no equivale a revisión de todas las chicas, premios, tamaños o animaciones. Las capturas muestran una partida sintética, no progreso original.

No se usaron las partidas habituales, sources/ ni APK. El servidor de QA se cerró al acabar; no se usó Iniciar.command. Ver inventario/hash y handoff para reproducir. Lucky Store, cool/pity, calendario oficial, restore integral, sostenibilidad de economía y conexión APK **no están verificados ni completos**.

## Registro de validaciones anteriores

Se conserva el historial y sus recuentos de pruebas tal como se registraron.

---

> **Registro vigente añadido el 28/09/2026:** consultar la auditoría al final de este archivo y [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md). Los resultados que siguen son históricos y se conservan con su alcance original. [Checklist](GXB2_MASTER_CHECKLIST.md) · [LEEME](LEEME.md) · [Workboard](AI_WORKBOARD.md).

# Validación del prototipo local

Fecha: 27 de septiembre de 2026.

## Resultado comprobado

- **8 pruebas automatizadas aprobadas**, ejecutadas en un perfil temporal y por conexiones de bucle local.
- Combate original reproducible con igual equipo y semilla; serialización y deserialización del informe con los descriptores originales.
- Recompensa de fase 1: 2.400 de oro y 55 de experiencia de jugador; repetirla no concede otra primera recompensa.
- Subida de nivel, deducción de recursos y progreso conservados tras cerrar y reabrir la base de datos.
- Peticiones inválidas rechazadas sin modificar el perfil.
- Inicio de sesión, mensajes TCP fragmentados y concatenados, combate con notificaciones y consulta HTTP verificados.
- Bonificaciones de grupo de fase 16: los identificadores textuales producidos por Lua se convierten a enteros conforme al descriptor. Prueba de regresión incluida.
- Una formación con posiciones 2, 4 y 6 conserva esas mismas posiciones en el informe de combate. La pantalla de equipo muestra 1–2 delante y 3–6 detrás; los personajes aparecen en las coordenadas verticales de `Battle.lua`.
- Pantalla del navegador inspeccionada: portada con atlas recompuesto, rutas de campaña/equipo/cápsula, invocación de dos integrantes en partida temporal, formación ampliada, combate con ilustraciones y fondo de fase, victoria, recompensas y progreso visibles. No aparecieron errores de consola en la comprobación.

## Prueba de campaña

Perfil temporal independiente, tres personajes iniciales. Se intentó cada fase secuencialmente; tras una derrota se subió un nivel a cada integrante siempre que hubiera recursos.

| Fase superada | Nivel de las tres integrantes al ganar |
|---|---|
| 1–8 | 1 |
| 9 | 3 |
| 10–11 | 8 |
| 12–13 | 11 |
| 14 | 14 |
| 15 | 21 |
| 16 | 22 |

En fase 17 el equipo perdió a nivel 23 y no hubo suficientes recursos para continuar mejorando a todas. Esto demuestra una ruta jugable de 16 fases con esta estrategia; **no demuestra que la fase 17 sea imposible con otra estrategia**, ni que las 530 fases extraídas sean jugables. La economía sostenida requiere implementar los sistemas pendientes.

La primera prueba descubrió un error de formato al llegar a fase 16; se corrigió y la segunda campaña la superó. Al terminar esa segunda campaña, la exportación del registro de prueba a disco falló por una ruta relativa incorrecta; los combates ya habían terminado y sus resultados se recogieron de la salida del proceso. La ruta del script de comprobación quedó corregida. El fallo de exportación no afectó a la partida del usuario ni al servidor.

## Integridad y límites de la validación

SHA256 del APK original comprobado al finalizar:

`70de79349ec7d593d92a8dac72880dbd216be29c51aa791448e5105523501efe`

No se abrió ninguna sesión contra servicios reales del juego. La validación TCP se realizó con un cliente de prueba, **no con el APK Android**. No se validaron Unity, SDK de plataforma, actualizaciones de recursos ni todos los sistemas de la pantalla principal. El cliente Android conserva su funcionamiento original.

## Prueba visual y funcional de portada y reclutamiento

En una partida separada (`127.0.0.1:9082`) se abrió la portada, se invocó una integrante con un pergamino y otra con la tirada gratuita, se incorporó la primera a la formación y se superó la fase 1. La pantalla mostró cinco integrantes, nueve pergaminos restantes, enfriamiento de la invocación gratuita y recompensa de victoria. Esta prueba no alteró el perfil principal.

En otra sesión temporal de prueba se comprobó visualmente la cuadrícula de seis posiciones y la batalla sobre el fondo original. Se trasladó una chica de la posición 1 a la 2, se guardó la formación y, tras recargar, la posición 2 seguía ocupada y la 1 vacía. La partida principal no se modificó en esta comprobación.

## Mapa de menús (septiembre de 2026)

Se trazaron las rutas de `MainWindow`, `SchoolChooseWindow`, `BattleChooseWindow`, `ShopMapWindow`, `GuildTerritoryWindow` y `SettingUpWindow` en el Lua recuperado. `web/app.js` contiene 70 entradas conectadas; 66 imágenes originales se extrajeron a `web/assets/menus/` sin modificar las fuentes.

Se comprobó en el navegador la entrada a Menú, Campus → Study → Shopping Street, Campus → Life → Date y Gremio → Territorio; el mapa de Shopping Street muestra cinco edificios seleccionables sobre el fondo original. El botón Volver regresó a la pantalla anterior. `node --check web/app.js`, la comprobación de referencias entre rutas y recursos, y las ocho pruebas existentes del backend pasaron. La navegación visual no valida las acciones del servidor original, que permanecen señaladas como pendientes en sus pantallas.

## Tests (torre)

`tools/extract_tower.py` convirtió los 2.000 pisos de `tower.lua` y copió los sprites cortados de Tests. La pantalla se abrió en el navegador desde Inicio → League → Battle → Tests; se vieron los pisos, la ficha del primero, sus seis rivales y los premios originales. Un combate de práctica produjo un informe de victoria sin gastar fichas ni modificar `state/profile.sqlite3`: el SHA256 del archivo fue `c3dbdac0a7addb300318ad898ad738ee4a0c826947bd86f66b4ecbac8e34982d` antes y después. En una base temporal, un equipo fortalecido ganó el primer piso, recibió 5.000 de oro y 5 Lunch Box, abrió el piso 2 y pasó de 10 a 9 fichas. La prueba automatizada verificó práctica, rechazo de pisos futuros, recompensas, persistencia y recarga tras 30 minutos. Las 11 pruebas del backend pasan.

## Reproducción de batallas de Tests y Daily Quiz

En el navegador se ejecutaron dos combates de práctica desde la partida local. Tests mostró a los dos equipos sobre `battle_map_14_1`, con acciones por ronda y barras de vida; Daily Quiz usó el mapa propio del desafío. En ambos casos `Ver resultado` saltó al desenlace y `Volver al evento` abrió la ficha del resultado. Las prácticas no concedieron premios ni gastaron fichas o intentos. El SHA256 de `state/profile.sqlite3` fue `8fb8af151de1ed4b557d6528aeceed89224e541c06953c836487350356142a83` antes y después. `node --check web/app.js` y las 11 pruebas del backend pasaron.

En un servidor temporal con otra base de datos se verificó que campaña conserva el visor y las recompensas de fase 1 tras compartir el código de reproducción. También se comprobó `Ver batalla otra vez` en Tests y el regreso al evento durante una reproducción. El servidor y la pestaña temporales se cerraron al terminar.

## Exportación de datos reales locales

`tools/export_real_save.py` leyó `game.db` en modo solo lectura y generó `real_save_export/`. Comprobó 31 formaciones, 62 alias de chicas y 3 de mascotas; tres selecciones de atuendo se resolvieron a nombres de assets Spine presentes en el respaldo real. Los inventarios de recursos contienen 6578 bundles y 5632 entradas de los manifiestos webview. La comparación de nombres de texturas sin distinguir mayúsculas no encontró texturas del respaldo ausentes de la decompilación.

Una revisión automática confirmó que ni el identificador de cuenta, ni el token, ni el nombre de jugador, ni los identificadores originales de las unidades aparecen en los archivos exportados. Las tablas `player_info` y `activity` de `game.db` están vacías, de modo que esta copia no permite recuperar el inventario o el progreso completo del servidor.


## 28/09/2026 — modo desarrollador y animaciones originales

- `python3 -m unittest discover -s tests -q`: 14 pruebas correctas. Las tres nuevas verifican guardado separado, persistencia, repetición de invocaciones gratuitas, Quiz tras agotar el límite normal y separación de peticiones HTTP.
- Comprobaciones sintácticas de `app.js`, `developer.js`, `battle-animation.js` y Python correctas.
- 647 registros asociados a 427 modelos; 0 modelos ausentes en la importación. Los 359 registros del catálogo visible tienen animación. Se valida el consumo completo del binario y la versión en cada conversión.
- Navegador: Inicio con sprites cortados originales; activación de desarrollo con nivel 400 y recursos de prueba; herramientas de nivel; Tests y Daily Quiz con equipos animados, movimientos originales de ataque/habilidad/daño/caída, rondas, controles de velocidad, salto y repetición.
- Verificación en una copia temporal del guardado, servidor 9082/9083. La partida habitual y sus 25 informes se compararon fila por fila con `state/backups/before-developer-chibis-2026-09-28.sqlite3`: iguales tras reiniciar el servidor principal. La comprobación usa datos SQLite, pues un checkpoint WAL puede cambiar el hash físico sin cambiar el progreso.
- Pendientes: revisar todos los modelos visualmente, efectos externos al esqueleto y audio. Los iconos restaurados no implican que todos sus servicios estén implementados.

Capturas: `validation/inicio-original.png` (partida habitual, nivel 15 y 9.406 de oro) y `validation/chibis-quiz.png` (Quiz de práctica con nueve modelos animados). Se verificó salto al resultado y repetición sin iniciar un nuevo combate.


## 28/09/2026 — auditoría de estado, GXB2-DOC-AUDIT-001 (ChatGPT)

- `python3 -m unittest discover -s tests -v`: **38 tests, 6,147 s, OK**. Se ejecutaron las pruebas existentes con sus bases temporales, sin abrir la partida habitual mediante Engine. [Salida completa](validation/audit-2026-09-28/unittest.txt).
- `node --check` de los diez JS propios: correctos. [Registro](validation/audit-2026-09-28/javascript.txt). No se comprobó el comportamiento visual ni se revalidaron los vendors.
- Revisión de referencias: 530 fases con batalla/monstruos/posiciones resueltas; 1.500 de 2.000 pisos Tests disponibles. 647 entradas chibi, 427 modelos y ningún `model.json` referenciado ausente. No acredita batallas/animaciones/recursos completos. [Inventario y hashes de código/tests](validation/audit-2026-09-28/inventory.json).
- Dos sondas solo en memoria: cambiar fase idle 1→10 con el mismo tiempo cambia EXP pendiente 100→120; eventos de puntos no tienen periodo/reset en su API/estado. [Sondas y límites](validation/audit-2026-09-28/probes.txt).
- Se leyeron backend, adaptador Lua, vistas/rutas web relevantes, datos, exportador y documentos técnicos previos. No se ejecutó el exportador ni se inspeccionaron sesiones de Android.
- No se hizo QA visual nueva, instalación portable, recorrido completo, cobertura individual de habilidades/efectos ni ejecución del APK. Ningún sistema global recibe `[X]` por esta auditoría.
- Solo documentación/logs cambiados. La [matriz de estado](ESTADO_PROYECTO.md) y el [registro de adaptaciones](DESIGN_DECISIONS.md) explican qué queda por investigar/implementar/verificar. El [handoff](AI_WORKBOARD.md) libera bloqueos al terminar.


## GXB2-CLAUDE-WAVE-007 — Patrol (29/09/2026, Claude)

- `python3 -m unittest discover -s tests`: **76/76 OK** (10 nuevas en `tests/test_patrol.py`, una de ellas con el motor LuaJIT real). `node --check` OK en todos los JS.
- QA en navegador: base temporal y puertos 9180/9181. El lanzador de QA adelanta el reloj a la siguiente ventana abierta, porque el 29/09 Patrol está cerrada; con el calendario local abre el 01/10 a las 00:00. Comprobado: desbloqueo (fase 120 ≥ 92), selección de 3 chicas, replay Normal con chibis originales, Quick, derrota con HP conservado (chica a 0 y enemigo al 3%), selección automática de la siguiente chica viva, victoria → fase 2 con Protractor 1/20, oferta del mercader (5 Arena Tickets por 70 gemas), Skip→tienda, compra (−175 gemas), Plain Riceball 11%→31%, tarjeta League → Patrol y Back. Consola sin errores.
- Pendiente: la vista "cerrada" solo se ha probado en unitarias; faltan clics táctiles reales y tamaños de pantalla distintos.


## GXB2-CLAUDE-WAVE-008 — House Exam (29/09/2026, Claude)

- 85/85 pruebas (9 nuevas en `tests/test_house_exam.py`, una con el motor real). `node --check` OK.
- QA en navegador con base temporal y puerto 9180 (6 chicas Demon de nivel 240, campaña en la fase 200): lista de casas, detalle Demon, formación automática, victoria en la fase 1 (+1 Exam Score, ticket 25→24, Raid desbloqueado), Raid ×2 (certificados 2→0), enemigos (!) de la fase 3, compra de certificado (−100 gemas) y flechas a House Angel. Consola sin errores. `state/` no se tocó.
- No verificado en el navegador: el cambio de temporada y el día de resultados (cubiertos por las pruebas unitarias).


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

## GXB2-CLAUDE-WAVE-013 — Echoes of Time (2026-09-29)
- `python3 -m unittest discover -s tests` → 139 tests OK (10 nuevos en `tests/test_echoes.py`, incluido un combate real con LuaJIT).
- QA en el navegador (puerto 9180, base temporal):
  - reloj de mundos: II y III bloqueados;
  - observar con 6 chicas (+480 verde);
  - acelerar con 20 Time Essence → 40 cartas, Clockwork 47/80;
  - terminar y reclamar: 585 puntos → 30 Time Shards;
  - mejorar Observation Length → Clockwork 84;
  - Fase 1 ganada con premios, chips 9/10;
  - reclamar el logro "Pass Stage 1".
- Logros de Echoes (captura g/03): el progreso cuenta los pasos reclamados (`TimeCloisterAchievementWindow`); 3 % (2/61) y sello Collected comprobados en el navegador; 139 tests OK.

## GXB2-CLAUDE-WAVE-014 — Santuario Tsuruga (2026-09-29)
- `tests/test_shrine.py`: 12 tests, incluido un combate real con LuaJIT.
- Motor: la misma batalla a dificultad 1, 95 y 300 hace que el enemigo reciba 131k, 16,6M y 165M de daño. Se confirma que `shrineId` aplica `shrine_difficulty`.
- QA en el navegador (puerto 9180, base temporal con Tests 600 y chicas de 10★):
  - prólogo (captura 04) y entrada (captura 05);
  - Trial of Intelligence 1/15 con 3 buffs (captura 06) y fase de combate con el mismo enemigo que la captura 07;
  - derrota total: la prueba termina, como en el original;
  - camino Batalla/Tienda con los Spines originales;
  - tienda: compra 500→320 y mejoras;
  - recuperación: resurrección 0→100;
  - Message Board y Pond of Prayers.
- Resultados de la QA:
  - se corrigió un choque de clases CSS con `shops.css`;
  - se corrigió que abandonar con 0 puntos subiera la dificultad;
  - se corrigió `chip_next` de Echoes (fallo intermitente de `test_developer`).
- Fallo intermitente de `test_developer.test_separate_save_refills_resources_and_survives_restart`:
  - **Causa:** comparaba dos snapshots tomados con segundos de diferencia, y la snapshot tiene temporizadores por segundo (`server_time`, arena, huecos de adquisición y `chip_next` de Echoes).
  - **Arreglo:** reloj fijo en el motor "normal" del test, y `chip_next` solo cuando los chips se están recuperando.
  - **Resultado:** 8/8 ejecuciones de la suite completa OK (159 tests).

## GXB2-HOUSE-DRESS-014 — 29/09/2026
9/9 tests de House/Outfit en bases temporales y compilación Python OK. QA navegador: guardar/girar mueble/renombrar, comprar taza, equipar combinación con gafas, Save y Cancel; recarga conserva nombre/atuendo. Perfil QA con stock de ejemplo separado de normal/DEV. Suite general durante integración:158 tests,4 fallos+2 errores; cinco de Shrine reservado por Claude y un test Developer compara snapshots cuyo reloj cambió. Pendiente repetición tras integración, no se declara verde. [Logs/capturas/diffs/sources/handoff](validation/house-dress-2026-09-29/README.md).

## GXB2-CLAUDE-WAVE-015 — Galaxy Voyage (2026-09-29)
- `tests/test_galaxy.py`: 10 tests. Cubren el generador de los 8 sistemas contra la tabla, cupones, rutas, vida persistente, debilitamiento del Ruler, requisitos, equipos, Tyrant, piratas, tareas, pase, tienda, final de temporada y un combate real con LuaJIT.
- Motor: `galaxy_info {hpP: 0.4, atkP: 0.4}` baja el daño que recibe el equipo de 2,04M a 0,82M en la misma batalla, lo que confirma el debilitamiento.
- QA en el navegador (puerto 9180, base temporal):
  - vista de sistemas (captura 06) y ventana del sistema (captura 07);
  - mapa de System of Origin con máscara, eventos y fila de inicio;
  - exploración de 2 h con temporizador y Recall, y reclamo;
  - combate ganado: cupón 10→9 y +2 puntos;
  - tareas y Passport;
  - Eternity con 2 piratas y la ventana del Galaxy Tyrant con Enemy Details (captura 08).
- Galaxy Voyage ajustado con las capturas 2026-09-29-h:
  - mapa sin huecos en las filas normales;
  - celdas oscuras, explorables con borde cian y rutas con pines numerados;
  - panel "Exploring… Time Remaining" (4 áreas = 07:59:59);
  - barra Return · Route · Progress · Recall · Team;
  - ventana "Details" con Claim; tras reclamar, la ruta sigue con las áreas que faltan;
  - el scroll se conserva entre renders y empieza en la fila de inicio.

## GXB2-CLAUDE-WAVE-016 — Historia principal + ventana Battle de Galaxy (2026-09-29)
- `tests/test_story.py`: 5 tests. Cubren los datos (`#1#`, `#24#43`), la cadena `next_id` con la primera variante, que las escenas salen una sola vez, los desbloqueos de Memories con llaves y los endpoints del motor.
- QA en el navegador (puerto 9180, base temporal):
  - Memories → Chapter 1 → Opening Ceremony: fondo del salón, "???", nombre del jugador y Michael con su imagen;
  - campaña 1-3: la escena sale antes del combate, se salta, se gana y ya no se repite;
  - campaña 1-4: escena 24 antes del combate y escena 43 ("You're so screwed.") tras la victoria.
- Galaxy Battle:
  - 6 Demon activan el aura Demon;
  - un equipo mixto no activa ninguna;
  - poder total de 383.755 con el HeroAttr real;
  - filtro de facción e iconos (ruta `/assets/factions/N.png`).


### GXB2-CARDS-CAMPUS-015 — ChatGPT,29/09/2026
Campus elevado60px de lienzo; tarjetas compactas con marco original, nombre sobre retrato, emblemas según estrellas/facción y hover sin desplazamiento. QA visual9232 sobre partida temporal, filtros/detalle/galería e imágenes revisados, sintaxis JS válida. [Evidencia y límites](validation/cards-campus-2026-09-29/README.md). Incremento visual entregado; sistemas globales siguen parciales. Claims015 liberados. No cambios de backend ni guardados habituales.

## GXB2-CLAUDE-WAVE-017 — Outfits (2026-09-29)
- `tests/test_dress.py`: 8 tests. Cubren los datos, el traje por defecto (Standard Uniform), la garantía a 100, que los repetidos se convierten en fragmentos, la tirada gratis, el coste de 3★→4★ (240 + 20 de seda, 40 fragmentos propios y 90/100/50 comunes), el bonus especial por estrellas del conjunto, equipar, los atributos en Echoes y el motor.
- QA en el navegador (puerto 9180, base temporal):
  - chibi con el uniforme estándar (igual que la captura i/01) y luego con Violet Charm, Warm Coffee y la máscara Sleepy Magic en la cabeza;
  - capas separadas: el pelo de atrás queda detrás del cuerpo;
  - 10 tiradas, con 10 piezas nuevas y el contador a 90;
  - atributos 169/…;
  - Outfit Upgrade: 1★→3★ con seda; a 3★ pide fragmentos propios 0/20 y comunes 500/30, con Lv. Up desactivado (como la captura j/02).
- Se descartaron 8 combinaciones de signos para las imágenes de ranura; la correcta es la convención y-down de pixi-spine.


### GXB2-CARD-CORNERS-016 — entregado, ChatGPT29/09/2026
Esquina de facción corregida con marco en9 secciones:22px de esquina para22px de icono, sin estirar textura completa. Dorado y avanzado verificados en QA temporal9232; assets/backend/saves intactos. [Evidencia](validation/card-corners-2026-09-29/README.md). Claim016 liberado.

## GXB2-CLAUDE-WAVE-018 — Skins (2026-09-29)
- `tests/test_skins.py`: 5 tests. Cubren Full Bloom (7024: `zhouyu_pifu01`, HP +3 %, DMG Red. +20, 74#128), ponerla, quitarla, el bloqueo en otra chica, `show_skin`, la colección, `release` y un combate real (HP con skin > HP sin skin y `skin_id` en `display_units`).
- Motor: HP de 40.511 a 41.726 y poder de 14.969 a 15.193 con la skin puesta.
- QA en el navegador (base temporal): pestaña Skins de Sapphire (51001) con Original, Full Bloom (Amount 2, Legendary), All-Star Jogger y Racing Queen. Tras Wear, `equips[7] = 7024`, la bolsa baja a 1 y el retrato pasa a Full Bloom.
- **Bug de las flechas en la ficha de chica** (lo informó el usuario):
  - **Causa:** en la pestaña Skins, `scrollIntoView` también desplazaba 58 px de lado el `.detail-scene` (con overflow oculto). Las flechas, el icono de facción y el corazón quedaban fuera del marco al cambiar de chica.
  - **Arreglo:** solo se desplaza el carrusel. En 9 cambios seguidos el scroll lateral se queda en 0.
  - Además, una chica sin ilustración ya no muestra la hoja entera `avatars.png`: muestra su avatar.

## GXB2-CLAUDE-WAVE-019 — Tarjetas de skin, ficha sin scroll, House Exams (2026-09-29)
- `python3 -m unittest discover -s tests`: 187 tests OK (cambios solo de frontend y extractores).
- QA en el navegador (puerto 9180, base temporal). Pestaña Skins de Amelia (755001):
  - carta 10-Star con check y ornamentos; Summer Breeze y Violet Prophecy con "Amount:0" y la cinta Epic morada;
  - al seleccionar una skin, el retrato cambia y aparecen los atributos y el botón Skin Shop.
- Scroll de `#game-root`: 853/853 en las pestañas Skins y Attribute (esta hace scroll dentro del panel), tanto en escritorio como en móvil 375×812.
- House Exams:
  - el encabezado y las casas coinciden con la captura k/01;
  - el chevron despliega la prueba actual, y su Battle abre la formación "Fight · House Human";
  - la estrella abre la ventana de temporada;
  - Shop abre la tienda 9 y el botón atrás vuelve a House Exams;
  - al pulsar una casa se abre su detalle con las 100 pruebas.

## GXB2-CLAUDE-WAVE-020 — Ficha a pantalla completa, Gear con ventanas, Limit-Break, partida dev (2026-09-29)
- `python3 -m unittest discover -s tests`: 187 tests OK. `test_developer` comprueba que la partida dev tiene todas las chicas de la guía, cósmicas incluidas, y que la normal no cambia.
- QA en el navegador (puerto 9180, base temporal, partida dev):
  - 446 chicas; Syrcotte (757001, cósmica) con su ilustración a tamaño nativo, recortada por el panel igual que en la captura l/07;
  - Gear:
    - Gear Up equipa el set Assassin;
    - Assassin Dagger abre la ventana Remove / Replace;
    - una ranura vacía abre el selector "Weapon · Select the Gear to equip:";
    - el cristal abre Exchange / Lv. Up;
  - Limit-Break: la pestaña muestra el banner, los 5 nodos y Reverse / Replace / Switch; la ventana muestra el emblema 1, MAX LVL 260, Unlock, los materiales 1/1 y 0/1, el coste de 10.000 y el botón;
  - Vivian (5★): pestañas Attribute / Gear / Skins / Awake; Attribute con flecha de subir nivel y barra de coste;
  - `#game-root` 853/853, sin scroll.

## GXB2-CLAUDE-WAVE-021 — Potenciales, Anima Gear, Land of Souls, Synchronize, Reverse / Exchange (2026-09-29)
- `python3 -m unittest discover -s tests`: 195 tests OK. Nuevos: `test_potentials` (1), `test_souls` (4) y `test_soul_land` (3, incluidos Reverse, Exchange y Synchronize).
- Atributos con el HeroAttr original:
  - Potential Life: HP ×1.12;
  - set Lucky Goldfish con Artifact: HP 518.078 → 776.465;
  - Synchronize 40: crit 720, critTime 1000, hit 800.
- QA en el navegador (puerto 9180, base temporal, partida dev):
  - Syrcotte a 15★: potencial Backwaters activado en la etapa 2, y su icono aparece en el nodo;
  - Amelia: botones Anima Gear y Elite Skills; ventana Anima Gear con las 5 ranuras equipadas, Overview con atributos y la habilidad del set;
  - Bolsa → Anima Gear con las piezas;
  - Syrcotte: Skill-Synchronize, habilidad 1 → 2/10 con el texto en color;
  - Scythe (755002): Reverse devuelve 7 chicas; ventana Exchange;
  - Land of Souls desde League: combate con Skip, derrota con ticket devuelto; Store y recompensa acumulada.
- **Corrección 2026-09-29 (informe de la usuaria):**
  - **Síntoma:** al invocar con una chica que llevaba Anima Gear, salía "Unexpected partners_info fields: ['soul_infos']".
  - **Causa:** `soul_infos` es un campo local (los parámetros de `ReportHero.souls`) que no existe en el mensaje original `partners_info`.
  - **Arreglo:** `protocol.LOCAL_ONLY` lo quita al codificar; `souls`, con los ids equipados, sí se envía porque el original también lo tiene.
  - **Verificación:** test `test_wire_messages_with_anima_gear` (SUMMON y GET_SLOT_INFO con Anima Gear equipado); 196 tests OK.
- **Corrección 2026-09-29: Switch y Attribute.**
  - **Switch** (`PotentialitySwitchWindow`) rehecho según la captura fb/119 (`IMG_5194`): 5 filas con insignia de estrella y 3 potenciales, el activo iluminado; debajo, el detalle del seleccionado y Activate.
  - **QA:** Syrcotte 15★, activar Life en la etapa 1 deja `potentials` = `[1, 2, 0, 0, 0]`.
  - **Attribute:** HeroAttr da a todas las chicas `sklP = 1000`, que es el valor neutro, y la ficha lo mostraba como "Skill DMG +100000%". Ahora solo se muestra lo que supera esa base (en Syrcotte quedan Crit +160, Crit DMG +140 y Armor Brk +160).
  - **Índice de capturas de Facebook:** `docs/references/2026-09-29-fb/INDEX.md` (120 capturas: 34 de sistemas ya hechos, 39 de sistemas nuevos y 47 de eventos).

## GXB2-CLAUDE-WAVE-022 — Astral Core (2026-09-29)
- `tests/test_astral.py`:
  - bloqueado a 10★;
  - a 15★, el nodo 1 sube a 20 y el nodo 3 sigue bloqueado hasta que el 2 llegue a 20;
  - la vida sube con HeroAttr;
  - el reinicio deja todo a 0.
- Total: 197 tests OK.
- QA en el navegador (base temporal, partida dev): Amelia a 15★ muestra la pestaña Astral Core con la constelación; el nodo I ×10 lleva a Lv 10/60, con HP 92.560 ▸ 101.816 y coste de 15 y 150 esferas.

## GXB2-CLAUDE-WAVE-029 — Outfit Showcase (2026-09-29)
- `tests/test_dress_show.py`: primer Slot abierto; 1102 exige Tests 50; una pieza 6★ de Courage 96 en Booth 1 da 96 puntos y 60/25 Tags diarios; Claim tras 2 días da ×2; compra en la Showcase Store.
- Total: 206 tests OK.
- QA en el navegador (base temporal q4, puerto 9180, partida dev):
  - la entrada coincide con la captura fb/40: logo, SHOP, puntuación, 4 vitrinas con medalla y cinta;
  - el detalle del Booth muestra ID / Slot / Rating / Daily Reward, las flechas y 3 estanterías;
  - al colocar una pieza desde un selector con 194 candidatas, el Booth sube a 96 (96+0+0) con recompensa 60/25;
  - la ventana Slot Unlock muestra la condición original en rojo y el requisito;
  - la tienda muestra los bloqueos por puntuación.
- Bug latente corregido: 45 piezas de `senpai_dress` (p. ej. 101231) no tienen items en `senpai_dress_item` (datos sin publicar del cliente). `dress.attrs` y `dress_show` ahora las ignoran en vez de fallar (test `test_orphan_piece_does_not_break_attributes`).

## GXB2-CLAUDE-WAVE-030 — Wish Capsule y resultado de invocación (2026-09-29)
- `tests/test_wish.py`: pesos 100/200/720/940, garantía en la tirada 500, cambiar de chica conserva el progreso, recompensa repetible ×5 a las 500 tiradas, la gratis sólo una vez al día, sin Wish Girl no se puede invocar.
- Total: 209 tests OK.
- QA en el navegador (q4, puerto 9180, partida dev):
  - banner Wish con Diana elegida y progreso 10/500 tras un ×10;
  - panel del evento 140 igual que la captura fb/47;
  - ×10 avanzada → Skip → ventana de resultado con 10 HeroIcons → "Draw 10" repite la tirada (476 → 496 chicas).
- Corrección tras revisión del usuario:
  - Wish Capsule ocupa el mismo hueco que las Advanced Capsules; las flechas (`wish_capsule_arrow_*`) y los puntos (`wish_capsule_dot*`) alternan entre ambas páginas (SummonWindow `groupMiddle`, `btnLeft_` / `btnRight_`).
  - El huevo de 5★ (summon 9) ya no pasa por la máquina de cápsulas: solo aparece la chica de 5★ (probado: revelación directa de Ennmaya).

## GXB2-CLAUDE-WAVE-031 — Magic Card (2026-09-29)
- `tests/test_magic_card.py`:
  - preview de 25 cartas; la Ultimate Reward de Round 21 está bloqueada en Round 1;
  - Start, y la Ultimate Reward en el primer giro la convierte en NEXT; se puede seguir girando; NEXT pasa a Round 2 y hay que volver a elegir;
  - misiones 4 y 3;
  - un tablero completo da las 24 normales más la Ultimate Reward.
- QA en el navegador (q4, puerto 9180):
  - preview igual que la captura fb/53;
  - elegir la recompensa (50 opciones, con bloqueadas por ronda), Start, y 3 giros: 150 → 105 varitas, huecos vacíos como en la captura fb/112;
  - Magician's Assistant con 13 misiones; la de "Magician's Assistant" completa tras girar cartas.

## GXB2-CLAUDE-WAVE-032 — Matching Pairs (2026-09-29)
- `tests/test_two_love.py`: primer intento gratis, Arrow diaria, pareja 1 (20#8), tablero completo, repartir de nuevo, Recharge Task con la popularidad provisional.
- Total: 212 tests OK.
- QA en el navegador (q4, puerto 9180):
  - la vista coincide con la captura fb/88;
  - Free → carta revelada, Start con la Arrow diaria → segunda carta, y sin flechas "Not enough Arrow of Love";
  - los iconos de Fate Crystal (artefacto) y Ancient Coin (Anima Gear) ya se ven.

## GXB2-CLAUDE-WAVE-033 — Lost Space Zone (2026-09-30)
- `tests/test_lost_space.py`:
  - 30 radares iniciales;
  - el snapshot enseña el mismo primer tablero que usa la primera acción;
  - solo se exploran vecinos;
  - auto → portal → Zone 2 con el cofre de la Zone 1;
  - Sweep Laser explora solo la fila;
  - 3 coordenadas abren el Supply Stash (64 contenidos).
- Total: 215 tests OK.
- QA en el navegador (q4, puerto 9180): la vista coincide con la captura fb/62 y explorar un bloque revela un Copier ×2.

## GXB2-CLAUDE-WAVE-034 — Flujo de combate de campaña (2026-09-30)
- `tests/test_campaign_hang.py`: el equipo de patrulla admite hasta 3 y no toca la formación de combate. Total: 216 tests OK.
- QA en el navegador (q4, puerto 9180):
  - al tocar 1-1 sale el popup Stage 1-1 (Output +20/5s, +2/5s, +5/5s; Loot; Auto-Battle);
  - al tocar la escena sale Auto-Battle con Front 1 / Back 2;
  - Fight → Battle (poder 701, 2+4 huecos, Servant) → Battle Start → carga "Saint" (cv: Rie Tanaka, "Now loading... 7%") → historia 24 → barrido `switch` → "Round 1".

## GXB2-CLAUDE-WAVE-041 — Halloween Pumpkin Patch (2026-09-30)
- `tests/test_pumpkin.py`: 10 dagas iniciales; 10 cortes con la primera recompensa de cada fila; no se puede cortar más; Claim da la recompensa de la ronda 1 y pasa a la 2; compra de 3 dagas por 450 gemas.
- Suite 266/266.
- QA en el navegador (q4, puerto 9180): la vista coincide con la captura fb/78 (10 calabazas abiertas con ✔, Claim, Pack Reward).

## GXB2-CLAUDE-WAVE-045 — Pulido: Campus, Transfer/Altar, Slots, Dorm (2026-09-30)
- `tests/test_altar.py` (retiro, recursos devueltos, límite de 6★+). Suite: 269/269 OK.
- QA en el navegador (q4, puerto 9180):
  - Altar: Smart llena 12, Preview muestra zumos y cajas de almuerzo, Retire pasa de 503 a 491 chicas.
  - Slots: la cabecera muestra fichas, pestañas con sprite y botones redondos.
  - Dorm:
    - los botones originales se ven bien en modo normal y en Manage (Storage Box con tarjetas);
    - Rest con 2 chicas: salen en el café y el botón marca 2/5;
    - Furniture Store: compra de Wall of Cafe (en propiedad 1 y gris por el límite);
    - Outfit Store abre la gacha de Dress y el botón atrás vuelve al Dorm.

## GXB2-CLAUDE-WAVE-046 — Pulido según referencias (2026-09-30)
- `tests/test_internship.py` +2 tests: la recompensa se sortea al aparecer el encargo y se paga esa misma; los encargos antiguos la reciben al abrir. Suite 271/271 OK.
- QA en el navegador (q4, puerto 9180):
  - **Slots:** Normal y High Stakes coinciden con las capturas 01 / 05 (máquina 3×3, Next Refresh, X1 / X10, palanca 10×). Una tirada ilumina la casilla ganadora y abre los premios.
  - **Menú:** coincide con la captura 07.
  - **Collection:** coincide con la 06 (7 entradas con su %).
  - **Manga:** coincide con la 02 (Episode 212 como el más reciente, 24 páginas); el lector abre la página.
  - **Girls:**
    - Category / Display Order como la 03; con ATK sale primero Syrcotte;
    - el filtro de clase Mage con la facción Luz deja 9 chicas.
  - **Intern:**
    - como la 04; Multi-Intern empezó 14 encargos;
    - Speed + Claim in Bulk muestran "Completed 1 Internship Quest(s)!".
  - El botón "Aceptar" ya no sale deformado.


## GXB2-CLAUDE-WAVE-047 — Arreglos (2026-09-30)
- QA en el navegador (q4, puerto 9180):
  - Selene 5★ (546003) › Skins muestra su carta en "Original" (`partner_card_46003`); `/assets/cards/partner_card_546003.png` da 200.
  - El filtro de clases aguanta 9 pulsaciones rápidas; con Warrior quedan 117 chicas y el botón ya no queda tapado.
- Suite: 271/271 OK.

## GXB2-CLAUDE-WAVE-048 (2026-09-30)
- QA (q4, puerto 9180):
  - la fila de clases aparece en horizontal sobre las facciones;
  - Wallpaper lista 770 opciones (446 chicas y 324 skins): Zombia, Flash, Werewolf y Nona tienen imagen, y solo Intertwined queda sin arte.
- Suite: 271/271 OK.


## Recuperación original — tanda050, 2026-09-30

[R][P] Android auditado: 31 formaciones anónimas, 62 chicas sin identificar y preferencias; no contiene roster/inventario completo y no permite migración jugable. Herramientas de auditoría y lector de índice de respaldo iPad implementados, con 5 pruebas específicas aprobadas. El usuario conserva la app en iPad, pero falla por conexión. Próximo paso: obtener respaldo Finder y comprobar archivos de la app. Importación completa sigue pendiente; no se tocó la partida habitual. [Evidencia](validation/original-save-2026-09-30/README.md).

## GXB2-CLAUDE-WAVE-049 — Tiendas y multijugador simulado (2026-09-30)
- Tests: `tests/test_collection.py` y `tests/test_arena3v3.py`; la suite completa pasa.
- QA (q4, puerto 9180, partida dev):
  - **Collection:** 11.874 puntos. Comprar "Avatar for Beginner Collector" (300 gemas) lo deja en la bolsa y sube los puntos a 11.894.
  - **Arena 3v3:** se entra desde Junior Varsity; Auto rellena 6/6/6; el combate contra "brink" termina 2-0 (+42), con carta de 15 gemas.


## GXB2-CLAUDE-WAVE-050 (2026-09-30)
- QA (q4, puerto 9180):
  - **Amelia con la skin 7033:** la cabeza ya no queda cortada.
  - **Front Page con 4 wallpapers:** Iron Fist, Amelia animada, Selene 5★ (ilustración 46003) y Sunbath quedan en su sitio.
  - **Skin Store desde la Shopping Street:** 130 skins; comprar Sunbath deja 2 copias de 7001.
- Suite: 292/292 OK.


## Recuperación iOS — tanda051, 2026-09-30

[T][R][P] Exportación iMazing de iPhone japonés analizada sin modificar: 71 filas de formación, cuatro cuentas separadas, 45 selecciones de estilo y caché histórica de 24 conjuntos en la cuenta principal de la caché. Sin roster completo ni inventario actual; personaje especial de Guild Competition excluido de importación por ser modificable. Auditor de exportación implementado y 3 pruebas específicas OK. La migración completa continúa pendiente. Próxima fuente posible: exportación del iPad, sin asumir que contiene la cuenta completa. [Informe](validation/ios-save-2026-09-30/README.md).

## Eventos — tanda052, 2026-09-30

[T][P][M] Jigsaw (37) y Puppet Parade (189) jugables en Inicio → Eventos → Exclusives. Jigsaw conserva 24 ilustraciones, las 216 piezas originales, intercambio de dos posiciones por 1 energía, 50 compras progresivas y seis hitos. Puppet conserva 17 hitos y sus premios; las marionetas no se consumen al cobrar. Progreso persistente y premios protegidos contra doble cobro. LOCAL-070 sustituye el calendario/suministro del servidor: eventos permanentes, 3 energías y 40 marionetas diarias, premios directamente a la bolsa. Falta la presentación/animación completa y el calendario original. Suite completa: 303/303 OK; siete pruebas propias y QA visual con partida temporal. [Evidencia](validation/events-2026-09-30/README.md). Próximo foco: Firework Project, Winning Pair y calendario de eventos.

QA de navegador: intercambio de posiciones 1/2 deja energía 0 y se conserva al recargar. Puppet: suministro deja 40 marionetas; hito 10 entrega 800 gemas y 50 fragmentos; aparece «Recogido» y monedas 150→950. Sin errores de consola. Solo `validation/events-2026-09-30/qa.sqlite3`; partidas habituales intactas.

## Firework Project — tanda053, 2026-09-30

[T][P][M] Firework Project 196 jugable en Inicio → Eventos → Exclusives: fabricar ×1/×10, cuatro resultados ponderados (15/50/20/15), coste de 25 polvos, nivel por 100 polvos gastados, 21 canjes con niveles y límites originales. No confundir con Firework Display 274. Estado persistente; operaciones inválidas no gastan recursos. LOCAL-071: archivo permanente y 250 polvos por día local para sustituir fuentes del servidor. Faltan calendario, fuentes originales de polvo y animación Spine de fabricación. Siete pruebas específicas; suite completa 311/311 OK. [Evidencia](validation/firework-2026-09-30/README.md). Siguiente foco: Winning Pair y calendario de eventos.

## CV, Marriage Certificate, Manga y Excursiones — WAVE-055, 2026-09-30

[T][P] Suite: 322 tests OK. QA en navegador sobre una base temporal (puerto 9180):
- Oath de Dracula: entrega la skin de boda 7018 y el certificado la muestra. Iron Fist también.
- Las portadas de manga muestran la primera viñeta.
- Main Center:
  - asignar a Succuba al hueco 1 se conserva;
  - la mejora de HP da Lv.2, +2.0 % → +3.0 % y coste 1300K / 60, como en la captura de referencia.
- Explore:
  - la mejora compara Lv.1 con Lv.2 (huecos 1→2, enemigo 80→100, calidades ordenadas y requisitos 0/8, 0/5);
  - el «!» lista los cofres 1–6 con premios fijos y aleatorios;
  - la chibi exploradora ya no sale como un cuadro blanco.

## Discuss / Partner Data Station — WAVE-056, 2026-09-30

[T][P] Suite: 323 tests OK. QA en navegador sobre una base temporal (puerto 9180), con la partida de desarrollador:
- Zombia: Strategy muestra el radar, las etiquetas Frontliner y DoT, el rango «No Record» y sus habilidades. Lineup dice «No suitable Lineup now~».
- Succuba: Tests muestra una formación de 6 chicas con 4★.
- Review: etiquetas Tank, Support y AoE; un comentario y un Like se guardan en `state.station['851003']`.

## Retoques con las capturas de Reference — WAVE-057, 2026-09-30

[T][P] Suite: 325 tests OK. QA sobre una base temporal (puerto 9180), con el navegador integrado y Chrome headless:
- Varsity y Junior Varsity:
  - filas con icono, nivel, poder, «S1» y Points; el top 3 en oro, plata y bronce;
  - la ficha de eleven92 muestra sus 3 equipos de defensa.
- Game Assistant:
  - 4 pestañas con sus ilustraciones;
  - «Initiate All» dio Alchemy 6,3 M, Campaign Loot, cápsulas, correo, 2 combates de Junior Varsity y las Daily Tasks; los pasos imposibles salen con su motivo.
- Help: los 11 temas y el FAQ; Faction Aura con los iconos de las auras.
- Explore:
  - el evento Help Seeker se ve con su rótulo, «Go 10 pan» y «Retreat»;
  - Girls List guarda 2 exploradoras.
- Dormitorio: la ventana Comfort muestra el oro que se va acumulando (40 tras unos segundos); Collect lo entrega y vuelve a empezar.


## GXB2-GITHUB-068 — Distribución privada Mac/Windows (30/09/2026)

Repositorio: https://github.com/Armenidez/gxb2-local (privado). Asset tree: 27.022 archivos, 4.591.491.170 bytes; voces: 6.108/6.108. Sin partidas SQLite, exports, credenciales, tests o capturas de referencia en el árbol final. Se mantienen en este Mac los materiales de desarrollo; pruebas/capturas entraron en el primer commit antes de que el usuario pidiera omitirlas y se retiraron posteriormente del árbol final.

- Suite previa: 331 tests OK. Tras selección de LuaJIT por plataforma: 11 tests de backend OK.
- Copia Git limpia y venv nuevo en Mac: instalación de requirements, partida nueva, `/health`, interfaz, `/api/state`, bootstrap, atributos con LuaJIT, PNG y MP3 empaquetado OK. No se usaron partidas personales.
- Windows Server 2022 x64, Python 3.11: https://github.com/Armenidez/gxb2-local/actions/runs/36729034925 aprobado. LuaJIT nativo sin GC64 carga el bytecode original; combate determinista de ejemplo y atributos OK. Iniciar-Windows.cmd crea su venv, instala protobuf, inicia ambos servidores y sirve health/UI/state/bootstrap/voz correctamente. UTF-8 activado para las tablas originales.
- Primeras revisiones detectaron ruta del script de comprobación y GC64 incompatible en la compilación moderna; corregidos. Procedencia, licencia y flags del ejecutable Windows incluidos en runtime/.

Límites: no se recorrieron visualmente todas las pantallas en Windows 10/11, no Windows ARM; esta verificación no certifica fidelidad/completitud de sistemas pendientes. Las instrucciones de Windows son para x64. No se detuvo el servidor habitual ni se modificó la partida del usuario.

## GXB2-CONTENT-071 — 2026-10-01

352 tests generales aprobados (work/content-verified.log). 11 tests de integración en test_content_expansion.py aprobados; dos añadidos tras la suite (Guild Boss damage y nested Excursion chest claims). JS syntax y git diff --check OK. HTTP 200 script/icono/apertura Newbie; UI premios Campaña1/Lv30, fase2 por nivel y persistencia tras restart/reload en validation/content-2026-10-01/qa.sqlite3. Captura GxB2-Newbie-Camp.jpg en outputs del chat actual. No partidas habituales modificadas.

## GXB2-CONTENT-072 — 2026-10-01

364/364 tests generales OK (138,256 s), incluidos diez nuevos de Friend Boss, PetTraining, Ulticore y Practical Work. Mensaje original Friend Boss codificado con victoria nativa; Practical Work BattleType13 descontó 26.058.208 HP exactamente. QA web aislada: desbloquear Ulticore, entrenamiento HP3600→2932, energía2→1, desafíos3→2 y persistencia al recargar. Captura Training con rótulos legibles. Los diez hashes de tablas normalizadas coinciden con las fuentes recuperadas. Sintaxis JS y diff sin errores. Avisos históricos HTTP de conexión cerrada no fallaron las pruebas. Partidas y servidores habituales intactos.

## GXB2-NAV-073

Chat: botón azul original lateral izquierdo; correo sólo receptor/adjuntos y borradores trasladados a Chat. Friend Boss en cuarta pestaña Co-op de Amigos, sin acceso independiente de Inicio. 18 pruebas relacionadas OK y QA visual temporal; ver NAVEGACION_CHAT_AMIGOS.md. Envío social sigue pendiente.

## GXB2-CAMPAIGN-074

Estados de botín/Collect, cinco chibis más grandes, dos entradas superiores y contadores de campaña ajustados a las referencias. Error de fort_finish corregido: premio de capítulo sólo tras última etapa. Suite366 OK y QA temporal; detalle en CAMPANA_ESTADOS_REFERENCIA.md. ProtectDoggy aún pendiente de minijuego.

075: cambio/vistas previas de campaña y14 guías ilustradas/26 páginas.13 tests relacionados OK y QA aislada; detalles en CAMPANA_CAMBIO_Y_GUIAS.md.

## Showcase, dormitorio vivo, Book por temporadas, Hearts y calendario — WAVE-059, 2026-10-01

[T][P] Suite: 371 tests OK. QA con Chrome headless sobre una base temporal (puerto 9180):
- Outfit Showcase: barra con oro y gemas; al entrar llega «Daily Reward» (140 Rare Tags y 45 Metal Tags) sin botón Claim.
- Dormitorio: chibis nítidas a ×2; en 22 s las 5 cambian de sitio; una se sienta en el Paper Stool y otra se tumba en la Straw Mat.
- Fantasy Book: la temporada Engine se ve con «Restart the Engine!», Gearwheel y Screws (forzada en la interfaz para la captura).
- Amigos: 3 contactos añadidos desde Recommended; la barra de Hearts y los botones Enviar / Reclamar aparecen.
- Eventos: 6 semanales y 4 mensuales abiertos con su tiempo restante; el panel Calendar lista los reinicios y lo que viene.

## 2026-10-01 · WAVE-060..065 (Claude)
- Suite completa: 373 tests OK. Prueba de humo (`tools/smoke.mjs`, 50 pantallas): 0 excepciones, 0 imágenes rotas; único 404 la carta de la skin 7235 (tiene reserva).
- Guild (WAVE-065) comprobado con capturas en Chrome headless sobre la base temporal de QA: Office (antes y después de Sign In), Cafeteria (Order, Lv. Up, Rank), Gym, ventana Boss y combate, Playground y la lista Members.
- No comprobado a mano: pedidos al terminar su cuenta atrás (Finished) y jefes ya superados con FINISH, porque la partida de QA no los tiene.
