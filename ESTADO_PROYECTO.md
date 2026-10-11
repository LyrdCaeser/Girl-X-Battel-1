> **01/10/2026 — CONTENT-072:** Friend Boss actual, Servant Training, Ulticore y Practical Work disponibles desde Inicio → Training & Bosses. Growth Diary **157/160**. **364 tests aprobados** y combates nativos comprobados en DB temporal. [Alcance y límites](SISTEMAS_PENDIENTES_RECONSTRUIDOS.md). Reiniciar servidor para cargar el código.

> **01/10/2026 — GXB2-CONTENT-071:** Growth Diary actualizado a **154/160** misiones; Newbie Camp con **tres etapas, 30 tareas y tres premios**, **28/30** tareas conectadas. API y mensajes originales, premios persistentes y comprobación sobre partida temporal. Reiniciar servidor; botones en Inicio. [Newbie Camp](NEWBIE_CAMP.md) · [Diario actualizado](GROWTH_DIARY.md).

> **01/10/2026 — GXB2-GROWTH-070:** Growth Diary `[T][P][M]`: 40 capítulos/160 misiones, 121 métricas locales y 39 sin conectar; premios y progresión persistentes, 343 tests OK y QA visual temporal. [Alcance](GROWTH_DIARY.md).

> **01/10/2026 — GXB2-TABLES-069:** recuperadas 904/904 tablas originales (202.878 filas sin duplicar tablas compuestas), 252 tablas inglesas (73.656 filas) y ocho contratos de sistemas. 586 tablas no tienen referencias léxicas locales previas; esto no equivale a 586 funciones ausentes. [Informe y límites](TABLAS_RECUPERADAS.md). El inventario anterior tiene estados desactualizados de varias tandas; no usar sus casillas para certificar ausencia. Recuperación de datos no implica implementación de backend/UI.

# Estado vigente — 30/09/2026

La [sección 40 del master checklist](GXB2_MASTER_CHECKLIST.md#40-actualización-de-cobertura--2026-09-30) resume la cobertura después de WAVE-048 y prevalece sobre prioridades y «pendientes» de las notas históricas de abajo. Hay progreso importante en Girls, PVE, Gremio, Dorm, eventos y UI, pero los sistemas globales siguen parciales: faltan reglas de servidor, calendario de actividades, restauración de partidas y validación visual/combatiente exhaustiva. La suite vigente pasa 311 pruebas; no es un porcentaje de juego completado. Fuente de cada tanda: [AI_WORKBOARD](AI_WORKBOARD.md).

---

# Actualización — Skins (29/09/2026)

**GXB2-CLAUDE-WAVE-018:** las **skins** ya funcionan. En la ficha de cada chica, pestaña Skins:
- ves sus skins con su dibujo, su cantidad y su rareza;
- si tienes una, la pones: cambia el retrato, suma sus atributos y en combate sale su chibi con la skin;
- se pueden quitar, ocultar en combate y comprar en la Skin Shop.

---

# Actualización — Outfits (29/09/2026)

**GXB2-CLAUDE-WAVE-017:** los **Outfits** ya funcionan (Campus → Outfit / Outfit Store).
- **Locker Room:** vistes al Senpai con cabeza, cuerpo, piernas, sombrero y accesorio, y el chibi animado se monta con las piezas originales.
- **Closet:** mejoras las piezas con seda y fragmentos.
- **Outfit Store:** tiras con botones; la naranja está garantizada a las 100.
- Los atributos (Courage/Charisma/Knowledge) cuentan en Echoes of Time.
- Arreglado un fallo del servidor local que a veces dejaba páginas sin estilos o sin datos al cargar muchas imágenes.

---

# Actualización — Historia principal (29/09/2026)

**GXB2-CLAUDE-WAVE-016:** la **historia principal** ya funciona.
- **En campaña:** al empezar una fase con escena se reproduce su historia, y tras ganar, la escena final. Ejemplo: la ceremonia de apertura en 1-3, y el "antes" y "después" de 1-4.
- **Escenas:** fondos, personajes, voces y música originales, con Auto, Recall y Skip.
- **Menú → Recuerdos (Memories):** permite volver a verlas por episodio y capítulo.

Además, la ventana de combate de Galaxy Voyage ya es como la original: poder, auras de facción y filtro.

---

# Actualización — Galaxy Voyage (29/09/2026)

**GXB2-CLAUDE-WAVE-015:** **Galaxy Voyage** es jugable desde Home → Cosmos Portal → "Galaxy Voyage".
- **Sistemas:** 8, como la captura 06, cada uno con un mapa de cuadrícula. Se explora hacia arriba desde el inicio; los combates cuestan cupones (10 al día) y los enemigos conservan la vida.
- **Ruler:** se debilita cuanto más exploras. Al cumplir los 3 requisitos se abre el siguiente sistema.
- **System of Eternity:** Galaxy Tyrant 1-20 (captura 08) y piratas diarios.
- **Además:** Voyage Teams, Voyager Passport, tareas y tienda.

---

# Actualización — Santuario Tsuruga (29/09/2026)

**GXB2-CLAUDE-WAVE-014:** el **Santuario Tsuruga** es jugable desde Liga (carta "Tsuruga Shrine"). Se desbloquea con el piso 500 de Tests y una chica de 10★.
- **Entrada:** 4 zonas, como la captura 05, y el prólogo de la historia (captura 04).
- **Realm of Trials:**
  - 3 pruebas por temporada y dificultad 1-300, que aplica el motor original;
  - 15 fases: combate a 15 rondas con la vida que se conserva, 3 buffs a elegir o renunciar por 180 fichas (captura 06), tienda, recuperación y jefe;
  - el combate se ve como en la captura 07.
- **Message Board:** tareas y logros. **Pond of Prayers:** tiendas de temporada y permanente.
- **Pendiente:** Tree of Chimes.

---

# Actualización — Echoes of Time (29/09/2026)

**GXB2-CLAUDE-WAVE-013:** **Echoes of Time** es jugable desde Liga:
- envía chicas a observar un Mundo del Tiempo;
- sale una carta cada 5 minutos (se puede acelerar con Time Essence);
- al terminar reclamas los premios y los Time Shards;
- con los shards mejoras el Planetarium, que alarga la observación, sube el nivel de las cartas y abre fases;
- las fases se combaten con el motor original;
- los logros llevan al 85 % que abre el siguiente mundo.

---

# Actualización — Old Campus Exploration (29/09/2026)

**GXB2-CLAUDE-WAVE-012:** **Old Campus Exploration** es jugable desde Tests, con el aspecto de las capturas del usuario: áreas con jefes chibi, Set Team por fase y Plan de Exploración en 4 categorías (Primary = 10, como la captura 05), puntuaciones y premios. Capturas de Echoes of Time y Galaxy Voyage archivadas para las siguientes tandas.

---

# Actualización — Internship y Alchemy (29/09/2026)

**GXB2-CLAUDE-WAVE-011:** **Internship** (Campus → Intern) y **Alchemy** (oro de Inicio) jugables, y sus dos tareas diarias ya avanzan. Los jefes se muestran a escala original en todos los combates. 121/121 pruebas.

---

# Actualización — Character Challenge, Sanctuary y barra del Servant (29/09/2026)

**GXB2-CLAUDE-WAVE-010:** **Character Challenge** (Normal y Puzzle) y **Sanctuary** ya son jugables con las tablas y el arte originales. Las piezas que generaba el servidor se sustituyen localmente (LOCAL-031/032). En todos los combates, la barra inferior pasa a ser la energía del Servant, como en el original. 114/114 pruebas.

---

# Actualización — Animación de invocación (29/09/2026)

**GXB2-CLAUDE-WAVE-009:** las cápsulas reproducen la animación original: la máquina en espera hasta deslizar hacia abajo, abriéndose después; cada chica con su revelación, **dorada y con intro especial ("222") si es de 5★**, morada y rápida si no. Sanctuary y Character Challenge están investigados pero no implementados (ver checklist WAVE-009). 90/90 pruebas.

---

# Actualización — House Exam (29/09/2026)

**GXB2-CLAUDE-WAVE-008:** **House Exam / Demon Exam** ya es jugable (modelo `AcademyAssessment`): 6 casas × 100 fases, solo chicas de la facción de la casa, formación por casa, Admission Tickets y Certificates con refresco diario UTC, Raid, recompensas de primera vez, Exam Score, temporadas de 14 días con 3 variantes de enemigos y premio de temporada (item 173). La vista reproduce la captura 07. **85/85 pruebas**. Decisiones en LOCAL-029. El inventario pasa a 33 de 71 modelos y 102 de 904 tablas.

---

> **Iconos corregidos — 29/09/2026, GXB2-PORTRAITS-008.** El selector legado conocía81 IDs y dejaba Selene y otras chicas como cuadros oscuros. Ahora usa el avatar original de cada registro:439 PNG íntegros,637 registros y359/359 chicas visibles. Comprobado en invocación y formación sobre partida temporal. [Causa, pruebas y relevo](validation/portraits-2026-09-29/README.md). No cambia progresión ni saves.

# Actualización — Inventario de cliente y Patrol (29/09/2026)

**GXB2-CLAUDE-WAVE-007:** nuevo [INVENTARIO_CLIENTE](INVENTARIO_CLIENTE.md), generado desde la descompilación por `tools/build_client_inventory.py`. Cuenta 71 modelos de juego, de los que 32 tienen implementación local total o parcial, y 98 de las 904 tablas se leen (89 de 462 sin contar eventos). **Patrol** es jugable: 600 fases en 6 dificultades, 5 chicas con la build fija, 1 chica por combate con el motor original (tipo DUNGEON), HP y energía persistentes en ambos bandos, Rice Balls, Stationery, mercader y tienda, cofres, ventana de 48 h y Auto Smash. **76/76 pruebas** (10 nuevas de Patrol). QA en navegador sobre una base temporal y el puerto 9180 con el reloj adelantado: selección, combate Normal (replay) y Quick, derrota con HP conservado, victoria con objeto, Skip→tienda→compra, Rice Ball y la ruta League → Patrol. Sin errores en consola; `state/profile.sqlite3` no se tocó.

Sigue siendo **[T][M]**: calendario, orden de `award_weight`, nivel de tienda y reglas de Auto Smash son decisiones locales (LOCAL-028). Faltan el mercader Spine `dungeon_web`, el Game Assistant y la tarjeta de privilegio.

Prioridades tras esta tanda: seguir con los modos PVE que reutilizan el motor (**Sanctuary** `Trial`/`new_trial`, **House Exam** `AcademyAssessment`, **Character Challenge** `HeroChallenge`); mantienen su vigencia P0 GXB2-TIME-001 / EVENT-RESET-001 / IDLE-SETTLE-001 y P1 SAVE-001.

---

# Actualización — Slots y Lucky Store (29/09/2026)

**GXB2-SLOTS-LUCKY-004:** dealers originales animados en Normal/High Stakes; Lucky Store funcional con ocho ofertas, Coupons, límite por oferta, refresh y guardado; Skip por modalidad, probabilidades del tablero, contadores vivos, Records y enlace directo a Slot Points. **49 pruebas aprobadas** y11 JS válidos. QA en partida temporal normal:50 tiradas por40,500 Coupons/50 puntos; compra de tienda y preferencias tras recarga verificadas. La partida habitual no se abrió ni se detuvo su servidor.

El sistema sigue **[P][M]**: sorteo/calendario local de la tienda y highlight web son adaptaciones explícitas; faltan FX/dialogue/audio originales y verificación táctil/responsive completa. [Investigación, capturas y límites](validation/slots-lucky-2026-09-29/RESEARCH.md), [decisiones](DESIGN_DECISIONS.md), [handoff](AI_WORKBOARD.md). Este encabezado sustituye pendientes de dealers/Skip/reloj/Shop descritos abajo; los registros históricos se preservan.

Prioridades vigentes tras esta tanda:

| Prioridad | Próximo alcance | Evidencia necesaria |
|---|---|---|
| P1 | Backup/restore y migraciones de partida, siempre sobre copias | Restauración, save antiguo, fallo/corrupción controlados; ningún cambio al save habitual. |
| P1 | Holiday Break / Atelier Valeera / Entrance Exam | Identificar ventana, tabla, protocolo, coste/límites y versión antes de crear compras o batallas. Las capturas solo prueban existencia/layout. |
| P1 | Fidelidad de Slots y Lucky | Secuencias FX/voz, ShopWindow completo, muestreo/calendario/cooldown original; pruebas touch y tamaños móviles. |
| P1 | Reloj global y corpus de combate | La mejora de puntos/idle/Slots no unifica Quiz/Libro/events ni demuestra todas las habilidades. |

La compra50/preferencia que la tanda REF-UI dejó sin verificar ya se comprobó en QA con controles de teclado. Pointer/touch sigue pendiente porque los clics de la herramienta no fueron consistentes. No se importó progreso de las imágenes.

---

> Hashes de la actualización visual: [inventory.json](validation/reference-ui-2026-09-29/inventory.json); alcance de QA en [VALIDACION](VALIDACION.md).

> **Referencias del29/09 incorporadas:** [nueve capturas y diferencias de versión](docs/references/2026-09-29/README.md). Exchange ahora dispone de paneles verticales con chibis; Slots usa selector lateral10→20→50 y dos botones de compra.50 tiradas cuestan40. Las capturas de Slot Points con5 rondas se registran como variante; no sustituyen los datos recuperados con8. Reglas de backend conservadas.

# Estado actual después de reconstrucción — 29/09/2026

Tarea **GXB2-RECON-WAVE-001**, iniciada 28/09, cierre 29/09 hora local. Esta actualización prevalece sobre los hallazgos históricos de la auditoría conservada abajo. Fuentes/contratos en [investigación y contratos](validation/reconstruction-2026-09-28/RESEARCH.md); código final en [inventory.json](validation/reconstruction-2026-09-28/inventory.json). No hay Git; comparar hashes antes de reutilizar resultados.

| Secciones del master | Investigación | Implementación y verificación | Pendiente |
|---|---|---|---|
|1 Infraestructura | Contrato de tiempo local explícito | `[T][M]` reloj Engine inyectable, módulos reciben now; lecturas sin escribir; Quiz no reabre fecha pasada | Calendario original, todos los timers/reset, migración/restore integral. |
|3 Chicas y15 Adquisición | `[D]` campos/mensajes de Exchange y LOCK_PARTNER; `[R]` selección del servidor | `[T][P][M]` propuesta/coste/save/discard y reapertura, flags manuales, preserva build y formación, materiales protegidos; pruebas de wire/rollback y revisión visual | Todas las chicas/pools, dropbox_id_2, probabilidades UI, selección manual de materiales, regresión, relaciones/skins reales. |
|9 Idle | `[R]` contrato local de liquidación; regla original del servidor no recuperada | `[T][M]` historial de fases, sin aplicar nueva tarifa retroactivamente; restart, cap, fracciones, botín histórico y doble cobro probados | Fidelidad original, largas secuencias y cambios de reloj globales. |
|16 Slots | `[D]` tablas/config/costes/puertas y mensajes; `[R]` generación servidor | `[T][P][M]` Normal/High Stakes, ocho posiciones, límites/pesos, costes/coupons, puntos Normal, refresh, historial y persistencia; UI probada | Lucky Store, cool, animación completa, ventanas probabilidad, distribución/pity y calendario original. |
|17 Economía y18 Tiendas | Nuevos sumideros y fuente Coupons | Costes/premios transaccionales de Exchange/Slots; shop_luck 22 filas investigadas | Compra Lucky ausente, economía sostenible sin DEV y todos los límites/fuentes. |
|20 Eventos | Periodos propios, separados del original desconocido | `[T][P][M]` eventos13/16/20 lunes 00:00 UTC, reset/archivo8 semanas y protección ante reloj atrás; Slots20 ahora tiene productor | Framework completo de actividades y rangos originales; correo de premios sigue adaptación. |

**47/47 pruebas aprobadas.** Nueve pruebas de regresión nuevas, además de 38 previas; once JS propios pasan sintaxis. UI verificada en base temporal: Normal1/10, High Stakes1 y puerta de10, proposal→reload→save, botón lock. [VALIDACION](VALIDACION.md) delimita exactamente el alcance. Ningún sistema íntegro recibe `[X]`.

## Prioridades vigentes

1. **GXB2-SAVE-001 (P0):** backup, migración y restore sobre copias; antes de importar progreso real. Registrar schema y comprobar rollback/corrupción.
2. **GXB2-LUCKY-001 (P1):** cerrar ciclo Coupons→Lucky Store desde shop_luck/LuckShopWindow/SHOP. Investigar límites y refresh antes de implementar.
3. **GXB2-MATERIAL-001 (P1):** selección manual de materiales, mostrar todas las protecciones y casos por receta; evitar confundir automático con cobertura total.
4. **GXB2-TIME-002 (P1):** probar login/Libro/Excursion/Quiz/Tests y todos los resets con cambios de fecha. Reloj inyectable no demuestra calendario global completo.
5. **GXB2-FIDELITY-001 (P1):** corpus de combate/atributos/equipo y verificación de pools; sprites/tabla presentes no prueban fidelidad.
6. **GXB2-SLOTS-UI-001 (P2):** Lucky navigation, animaciones, cool/probabilidades y verificación de todos los tamaños e iconos de los pools.

GXB2-EVENT-RESET-001 y GXB2-IDLE-SETTLE-001 tienen implementación local probada, con fidelidad pendiente; no siguen ausentes. GXB2-TIME-001 es parcial. El siguiente relevo está en [AI_WORKBOARD](AI_WORKBOARD.md), sin bloqueos activos de esta tanda.

## Auditoría anterior — evidencia e historial

La matriz y prioridades siguientes registran el estado antes de esta implementación. Para las secciones actualizadas, usar la tabla de arriba; el resto conserva sus límites originales.

---

# GxB2 Reborn — estado contrastado con evidencia

Auditoría: **2026-09-28**, ChatGPT, tarea **GXB2-DOC-AUDIT-001**. Proyecto inspeccionado: `/Users/schroyle/Documents/Codex/2026-09-26/referenced-chatgpt-conversation-this-is-an/outputs/gxb2_local`. Es una carpeta de trabajo **sin repositorio Git**; no hay commit de referencia. Los hashes del código y tests auditados están en [inventory.json](validation/audit-2026-09-28/inventory.json). Si cambian, revisar este estado antes de reutilizarlo.

## Documentos y orden de lectura

1. [Master checklist](GXB2_MASTER_CHECKLIST.md): alcance de preservación, protocolo y criterios de terminado. Sus etiquetas originales de existencia/investigación son antecedentes, no nuevas comprobaciones de esta auditoría.
2. [Workboard](AI_WORKBOARD.md): responsables, bloqueos, tareas y handoff. Reclamar allí antes de editar.
3. [LEEME](LEEME.md): iniciar el prototipo, localizar fuentes y entender la implementación; conserva el historial de avances.
4. **Este informe**: estado actual por sección del checklist, evidencia, diferencias y prioridades.
5. [VALIDACION](VALIDACION.md): resultados y límites de cada comprobación. [MAPA_MENUS](MAPA_MENUS.md): rutas visuales; una entrada de menú no acredita una función completa.
6. [Decisiones](DESIGN_DECISIONS.md): sustituciones offline y supuestos ya presentes, separados de reglas originales recuperadas.

## Qué se verificó y qué significan los estados

Se leyó la documentación local, el backend Python, el adaptador Lua, rutas/vistas web relevantes, tablas JSON, exportador y pruebas. Se ejecutó la suite existente: **38/38 pruebas aprobadas en 6,147 s**, sobre bases temporales creadas por las propias pruebas. Los diez archivos JavaScript propios pasan la comprobación de sintaxis. Se inspeccionaron referencias de datos y modelos; se hicieron dos sondas en memoria sobre idle y eventos de puntos.

Evidencias reproducibles: [pruebas](validation/audit-2026-09-28/unittest.txt), [sintaxis JS](validation/audit-2026-09-28/javascript.txt), [inventario y hashes](validation/audit-2026-09-28/inventory.json), [sondas](validation/audit-2026-09-28/probes.txt). No se inició el servidor habitual, no se abrió la partida principal con Engine ni se ejecutaron extractores. Esta tarea modifica documentación y genera logs; no modifica reglas, APK, fuentes originales ni partidas.

**No se hizo una nueva revisión visual en navegador, una campaña completa, una instalación en otra máquina ni una prueba del APK/Unity.** Las pruebas visuales antiguas siguen identificadas por su fecha en VALIDACION. No se recuperó ni se validó un backend oficial. Ejecutar bytecode original no acredita automáticamente todos sus efectos, variantes o contextos.

- `[P]`: parte implementada; faltan elementos de la función o del sistema.
- `[T]`: operación implementada con evidencia de código y, cuando se indica, pruebas de alcance limitado; aún necesita la verificación integral del checklist.
- `[M]`: sustitución local intencional; puede coexistir con `[P]` o `[T]`.
- `[ ]`: no se encontró operación funcional en las rutas locales auditadas. Puede haber tablas/assets y navegación.
- `[BLOCKED]`: dependencia ausente concretamente identificada.
- `[R]`: investigación parcial; `[D]` solo para un contrato o tabla identificado, no para fidelidad integral.

**No se otorga `[X]` a ningún sistema completo en esta revisión.** Los checks automatizados aprobados se documentan por nombre/alcance. Las casillas originales del checklist se conservan como inventario; la matriz siguiente documenta el estado auditado y evita marcar como completas funciones solo por abrir una pantalla.

## Comparación con el LEEME y documentos anteriores

| Antecedente | Estado contrastado | Consecuencia |
|---|---|---|
| Listas tempranas: Gear, Forge, Awake y atributos estimados pendientes | `equipment.py`, `PARTNER_GRADEUP`, `AWAKE_PARTNER`, `UPGRADE_PARTNER_EX_SKILL` y modo Lua `attrs` existen; pruebas de equipo/progresión pasan | Leer las actualizaciones del 28/09 y esta matriz; conservar los párrafos antiguos como historial. |
| Campaña visible limitada a 30 fases; idle pendiente | `snapshot()` devuelve 530 fases; `campaign-map.js` y `campaign.py` implementan mapa e idle | No confundir exposición de datos con recorrido jugable completo. DEV todavía abre hasta fase 30. |
| Audio y Spine pendientes en párrafos tempranos | Chibis, retratos animados, resultados y BGM/SFX generales están conectados | Siguen pendientes voces, FX externos y cobertura visual modelo por modelo. |
| Entradas laterales solo visuales en MAPA_MENUS y actualización de chibis | `home_systems.py`, `home-menus.js` y ocho pruebas cubren operaciones locales | Servants, Libro, Excursion, contactos y correo son parciales; registrar el avance omitido por esas listas. |
| Eventos: cuatro pestañas y todo salvo login archivado | `events.js` actual agrupa tres pestañas y muestra puntos 13/16/20; Slot sigue sin productor | La lista `WORKING` no significa que los cinco eventos sean íntegramente jugables. |
| LEEME enumera 11, 25, 32 y 36 pruebas; VALIDACION llega a 14 | Ahora se descubren y pasan 38 | Esas cifras corresponden a fases históricas, no al recuento actual. |
| Todo el alcance del master está sin marcar | Hay infraestructura, datos, motor y operaciones locales comprobadas | El checklist era un marco general, no un inventario evaluado del código existente. |

## Inventario comprobado por lectura estática

| Recurso | Cantidad | Qué demuestra / qué no demuestra |
|---|---:|---|
| Tipos Protocol Buffers en `data/schema.json` | 1.721 | Esquemas presentes; no 1.721 endpoints implementados. |
| Filas `partner.json` / catálogo visible | 647 / 359 | Registros de distintas progresiones y especiales; no 647 chicas distintas. |
| Chicas con referencias de skin / referencias totales | 228 / 678 | Referencias instaladas; no propiedad ni equipamiento de skins. |
| Fases con batalla, monstruos y posiciones coherentes por referencia | 530 / 530 | Referencias resolubles; no 530 victorias ni balance/economía verificados. |
| Pisos Tests / referencias de combate resolubles | 2.000 / 1.500 | 1501–2000 bloqueados por datos ausentes del motor actual. |
| Piezas de equipo / catálogo de objetos | 1.307 / 2.350 | Datos presentes; registro de fuentes, sumideros, límites y versiones incompleto. |
| Actividades catalogadas | 322 | Muchos eventos son archivo visual. |
| Catálogo chibi / modelos únicos | 647 / 427 | No faltan `model.json` referenciados; no prueba texturas, FX ni todas las animaciones. |
| Entradas de retrato animado `lihui.json` | 274 | Datos de importación presentes; no revisión visual de 274 animaciones. |

## Matriz por sección del checklist

La columna de investigación describe lo observado localmente. Las afirmaciones `[C]`, `[P?]` y `[?]` heredadas del master no se revalidaron contra web/wiki en esta tarea; investigar cada regla original con fuentes del cliente antes de implementarla. `[M]` remite al registro de decisiones.

| Sección | Investigación / evidencia local | Implementación auditada | Falta verificar o implementar |
|---|---|---|---|
| **1 Infraestructura** | `[D]` encuadre y esquemas locales; `[R]` arranque original, identidad, resets y RNG | `[T][M]` HTTP/TCP loopback, perfil SQLite, inventario/roster, transporte, login ficticio y RNG reproducible de combate. `[P]` migración por defaults y formato 2; copia/restore manual documentada | Boot Unity/SDK, cola de reconexión, reloj común, migración validada, backup/restore probado, manejo de corrupción. No hay scheduler general de eventos. |
| **2 Perfil** | `[R]` campos y catálogo de avatar/marco en `engine.py` y `web/app.js` | `[T][M]` nombre, firma, avatar, marco, nivel/EXP y persistencia; `test_profile_customization_persists_and_rejects_unknown_assets` | VIP, privilegios, logros, estadísticas completas y restricciones de desbloqueo. Personal Info completo y Courage/Charisma/Knowledge no acreditados. |
| **3 Chicas** | `[R]` tablas partner, EXP, graduate/ascension/exskill; siete facciones en catálogo | `[T]` formación, nivel/grado, fragmentos, Graduate, ascensión/awake hasta 15★ y topes 330 en ejemplos probados. `[P]` colección y detalle | Todas las recetas y chicas; selección manual de materiales; Reverse/regression, Replace, lock/unlock, sistemas tardíos. Viabilidad de 1–4★ en endgame es diseño pendiente. |
| **4 Equipo** | `[R]` `equipment.json`, `equipment.py`, HeroAttr y prefab descrito en LEEME | `[T]` equipar/quitar, mejor equipo, forge/auto, tesoro/crystal con reroll/bloqueo, antique upgrade. Siete tests de operaciones | Persistencia y UI completas de todas las variantes; efecto diferencial de equipo en combate; T7 `skill_index`, Soul/Anima Gear, tesoros de reserva, vender/desguazar. Fuentes/sumideros completos. |
| **5 Skins/fashion** | `[R]` 678 referencias, pictures/lihui y previsualización | `[P]` galería, arte y animación de algunas skins. `[ ]` ownership/equip funcional | Ranura 7, bonos, Fashion Points/Level, tienda, temas, conjuntos/outfit skills, relación con Oath. Assets no prueban posesión. |
| **6 Relaciones** | `[R]` rutas Date/Life y recursos; no reglas locales operativas halladas | `[ ]` intimidad, regalos, dating y oath; navegación/archivo parcial | Umbrales/costes, escenas, premios, voces y persistencia; preservar sin eliminar por dependencia de red. |
| **7 Combate** | `[R]` bytecode original `BattleCreateReport`, ReportHero/HeroAttr; adaptador headless | `[T]` misma semilla → mismo informe, serialización y posiciones; `[P]` replay Spine, HP, velocidad/salto, resultados y estadísticas | Fórmulas documentadas y corpus por habilidad/efecto; revives/CC/shields/edge cases no cubiertos individualmente. Servant y guild skills no integrados; FX externos, buff HUD y voces pendientes. |
| **8 Campaña** | `[R]` 530 fases/50 capítulos en datos y mapas; historia no reproducida por esto | `[P]` fases, desbloqueo, combate, primera recompensa y mapa. Tests fases 1/16; ruta antigua de 16 fases en VALIDACION | Recorrido de todas las fases sin DEV, equilibrio de recursos, bosses/locks; diálogos, triggers, CGs y Memories. |
| **9 Idle** | `[R]` tick 5 s, cap 12 h y tablas; cadencia de loot original desconocida | `[T][M]` acumulación/collect y botín local cada 600 s; prueba de cap y cobro doble. `[P]` integración total | Cambio de fase altera tarifa de todo el intervalo pendiente; definir liquidación con evidencia. Persistencia E2E, reloj atrás, cierre/reapertura y UI live/cap. |
| **10 PVE** | `[R]` tower y Daily Quiz, batallas/rewards/reset | `[P]` Tests y Daily Quiz con premios/práctica/sweep y guardado probado. `[BLOCKED]` Tests 1501–2000 | Todas las dificultades/pisos y resets. Patrol, House Exam, Old Campus, Sanctuary, Practical Work/Experience, Entrance Exam, Admission Prep, Echoes of Time, Squad y otros conservan datos/rutas o están sin implementar. |
| **11 Galaxy** | `[R]` `starry_altar` en home_systems | `[T][M]` Cosmos Portal: elección, tiradas/coste y garantía local probados. `[ ]` Galaxy Voyage, Stellar Altar de mejoras y Astral Core | No equiparar `starry_altar`/Cosmos Portal con todo Stellar Altar; recuperar relación/nombres por versión, mapas, upgrades, efectos y resets. |
| **12 Servants** | `[R]` pet/exp_pet/pet_skill/pet_exskill, PetWindow/PetDetailWindow (PetAttr, PetPasSkill), ReportPet | `[T]` activar, nivel, grado, auras (skills), selección; **el Servant seleccionado entra en combate** (`petA` → ReportPet/ReportPetAttr originales) en campaña, Tests, Quiz y Explore; UI lista/detalle/detalles según capturas (CLAUDE-WAVE-005) | Ulticore/exskill y ex-level (`pet_exlevel_add_pas` limita el nivel de las auras), Reborn, Training (PetTraining*), animación de la habilidad del Servant en el visor, validación visual de los 36 modelos. |
| **13 PvP** | `[R]` rutas arena/team/cross-server; sin simulador operativo hallado | `[ ]` ligas, matchmaking, rankings/temporadas y rivales NPC | Junior/Varsity/Elite/Ultimate/House, tres equipos, defensa, tickets, historia, rewards y ranking persistente offline. |
| **14 Guild** | `[R]` rutas/mapa/recursos de territorio | `[ ]` membresía y transacciones; navegación visual | Tecnologías, boss, guerra, contribuciones/rewards, tienda, miembros NPC. Adaptador de batalla usa `guildSkillsA/B={}`. |
| **15 Adquisición** | `[R]` summon/dropbox/debris y tablas Enroll | `[T]` cápsulas, gratuitas, fragmentos y Enroll coste/Portfolios/puntos; `[M]` BFF ×10 | Exchange/Replace pendiente explícito en `enroll.js`; pity y banners históricos no acreditados; Elite Assembly/Cafe/Girl Store y cobertura estadística de pools. |
| **16 Slots** | `[R]` evento de puntos 20 y datos archivados | `[P]` vista/umbrales de Slot Points; `[ ]` máquina que produzca tiradas/puntos | Tickets, pool, tasas, High Stakes, refresh, coupons/Lucky Store y ciclo jugable completo. |
| **17 Economía** | `[R]` catálogo 2.350 items y tablas de coste/recompensa | `[T]` cantidades persistentes y transacciones de operaciones probadas; `[P]` economía | Registro autoritativo ID/icon/cap/fuentes/sumideros/versión; algunas monedas guardadas sin uso. No dar por saneada la economía porque DEV provee recursos. |
| **18 Tiendas** | `[R]` shop_battlepass y activity_lafuli_shop | `[P]` compras locales Libro/Castillo con coste/límite en código; mapa general visual | Pruebas específicas de compras/límites/resets; Market/Girl/Guild/Lucky/Skin/Collection/PvP y resto de tiendas pendientes. |
| **19 Tareas/logros** | `[R]` battlepass_mission y counters | `[P]` cuatro misiones activas del Libro (IDs 5/6/9/13), tiers gratis y periodos UTC | Más misiones, misiones generales diarias/semanales, logros, Internship/Exclusive Task, bulk claim y temporadas. Las misiones archivadas no producen progreso. |
| **20 Eventos** | `[R]` 322 actividades y tablas de login/puntos | `[P][M]` login 1, 7 días 116, puntos Capsule 13/Enroll 16; Slot 20 incompleto. Rotación visual semanal de archivo | Framework real de fechas/estado, reset de puntos por periodo, replay, cleanup/mail/story/minijuegos y todas las familias no operativas. No hay ciclo infinito jugable demostrado. |
| **21 Dorm/My Room** | `[R]` House y297 muebles; Excursion es otro sistema | `[T][P][M]` editor/tienda/guardado/confort/dos pisos | Visitas/ingreso/interacción autónoma/apilado completo pendientes. Ver GXB2-HOUSE-DRESS-014; no confundir producción de Excursion con Dorm. |
| **22 Colección** | `[R]` catálogo de chicas y skins | `[P]` galería de chicas y arte disponible | Colección de mobiliario/antigüedades, thresholds/rewards/hints/store, ownership e historial. |
| **23 Historia/Memories/Manga** | `[R]` rutas y recursos, nombres de capítulos | `[ ]` replay narrativo completo | Extraer diálogos/CG/manga con IDs, unlock, localización y escenas sin servidor. |
| **24 Social** | `[R]` home_systems y export anónimo | `[T][M]` contactos/borradores locales, mail con adjuntos y cobro único en tests; `[P]` sistema | Generador de correo de producción (mail_test solo DEV), amigos NPC, Hearts/rewards, Friend Boss, Security Squad, chat, requisitos sociales y anuncios. No se envían borradores. |
| **25 UI/UX** | `[R]` prefabs/rutas y sprites; pruebas visuales antiguas | `[P]` inicio, girls/bag, campaña/Tests/Quiz, equipo, Enroll, eventos/home/profile; popups/rewards y back stack en código | Nueva revisión visual completa, resize/ratios, errores, tooltips, badges, red dots consistentes, buff HUD/FX y fidelidad de cada pantalla. Sintaxis JS no verifica interacción.  **Marco fijo 480×853 (9:16) escalado a la ventana (GXB2-UI-FRAME-001, `frame.css/js`): todas las vistas comparten tamaño; barras fijas ancladas al marco.** |
| **26 Settings** | `[R]` rutas de settings | `[P][M]` mute persistido en localStorage | Volumen por categoría, voces, FPS, lenguaje, notificaciones y opciones de cuenta/graphics; catálogo completo de originales. |
| **27 Audio** | `[R]` audio local y GxbAudio | `[P]` BGM Inicio/Campaña/Battle/Campus y SFX de resultado/recogida | Voces/skills/date/oath, inventario IDs/hash, loops, categorías y archivos faltantes. No se comprobó reproducción en esta auditoría. |
| **28 Assets** | `[R]` extractores, 427 modelos chibi y 274 retratos animados | `[P]` copia/importación selectiva local; referencias a model.json resueltas | Hash/procedencia/versión por asset, atlas/audio/FX/texturas, recursos desconocidos y revisión visual exhaustiva. M0 no completo. |
| **29 Localización** | `[R]` nombres/textos ingleses extraídos y tablas originales externas | `[P]` strings locales y títulos recuperados, mezcla de idiomas | Registro por idioma/ID, story/tutorial/quest/errores, placeholders, fallback y texturas con texto. |
| **30 Tutorial** | `[R]` campos guide en login de laboratorio | `[ ]` flujo tutorial fiel | Primera entrada, battles/clicks forzados, unlocks/rewards y skip opcional separado. `guide_info` no es tutorial implementado. |
| **31 Reverse engineering** | `[D]` esquemas/encuadre concretos; `[R]` corpus/versión/autoridad server | `[P]` herramientas, datos y adaptador; documentos técnicos históricos externos | Endpoint coverage por mensaje/versión, validar requests realmente consumidos por cliente, manifest de dependencias/hashes y desconocidos. |
| **32 Save original** | `[R]` parser read-only y export anónimo documentados | `[P]` export/report existentes: 31 formaciones alias, 3 atuendos y inventarios de assets. `[BLOCKED]` import completo con evidencia actual | No hay niveles/roster/inventario completos identificados ni mapa alias→personaje; conversor y validación de import pendientes. No inferir propiedad de assets ni marcas vistas. No se releyó game.db en esta tarea. |
| **33 Reborn** | `[R]` sustituciones enumeradas en DESIGN_DECISIONS | `[P][M]` prototipo offline, DEV separado, correo/contactos y economía local parcial | VIP normal, eventos perpetuos, social NPC, rebalance y modo Classic, adquisiciones antes pagadas y endgame. No se modificó balance aquí. |
| **34 Fuentes** | `[R]` enlaces del master y corpus local | `[P]` referencias conservadas | Wiki/guías son pistas; registrar fuente/version/hash por regla. No se consultó web ni se verificó su vigencia. |
| **35 Workboard** | Protocolo leído | `[T]` claim y handoff de esta auditoría en AI_WORKBOARD | Todos los agentes deben reclamar futuras tareas y declarar archivos; estado externo de Claude/Nava no observable desde este board nuevo. |
| **36 Discovery inbox** | Hallazgos con IDs al final de este informe | `[P]` inventario de desconocidos iniciado | Resolver/categorizar sin convertir hipótesis en reglas originales. |
| **37 Milestones** | Ver tabla siguiente | Todos parciales o pendientes | No inferir cierre de un milestone por una operación aislada. |
| **38 Done** | Hay evidencia parcial para algunas preguntas | `[P]` reconstrucción global; documentación de esta tarea terminada | Resets, fidelidad integral, sistemas, import y paquete reproducible siguen abiertos. |

## Milestones sin falsas completitudes

| Hito | Estado | Evidencia y requisito pendiente |
|---|---|---|
| M0 Inventory | `[P]` | Datos/assets/protocolos inventariados parcialmente; falta reconciliar versiones y hashes completos. |
| M1 Boot | `[P][M]` | Web local arranca en pruebas HTTP; APK/Unity y paquete portable pendientes. |
| M2 Persistence | `[P]` | Save/load y rollback probados en ejemplos; falta reloj/reset/migración/restore integral. |
| M3 Girls | `[P]` | Roster, progresión y equipo con tests; faltan variantes y sistemas. |
| M4 Combat | `[P]` | Motor original reproducible; fidelidad por habilidad/contexto y integración Servant/Guild pendientes. |
| M5 Campaign | `[P]` | Mapa/idle/combat; no recorrido completo ni economía sostenida comprobada. |
| M6 Core PVE | `[P]` | Tests/Quiz; Patrol y otros modos pendientes. |
| M7 Economy | `[P]` | Summon/Enroll/equipo y algunas misiones/tiendas; resto y ciclos pendientes. |
| M8 Social | `[P][M]` | Contactos/mail locales; simuladores de PvP/guild/friends pendientes. |
| M9 Events | `[P][M]` | Login/puntos parcial; scheduler/reset/replay general pendientes. |
| M10 Late game | `[P]` | Servant/Cosmos/progresión parcial; Galaxy y efectos faltan. |
| M11 Preservation | `[P]` | Arte/skins/audio parcialmente accesibles; historias/colecciones/cobertura faltan. |
| M12 Save recovery | `[P][BLOCKED]` | Export anónimo disponible; no import de progreso completo posible con lo identificado. |
| M13 Balance | `[ ]` | Objetivos y sustituciones documentados; rebalance/Classic no implementados. |
| M14 Release | `[ ]` | Falta paquete reproducible, fuentes de la misma versión y prueba de instalación sin red. |

## Hallazgos y prioridades para el próximo turno

Las siguientes tareas están **sin reclamar**. Revisar el workboard y tomar una sola con archivos explícitos. Investigar el original antes de elegir una regla nueva; el trabajo de documentación no autoriza dar por completada su implementación.

| Prioridad / ID | Acción y alcance propuesto | Criterio de cierre |
|---|---|---|
| **P0 GXB2-TIME-001** | Unificar el contrato de tiempo y periodo; `events.py` usa fecha local, Quiz/Libro UTC y UI puntos semana local. Investigar resets originales; conservar semántica o registrar sustitución | Reloj inyectable, pruebas de medianoche/día/semana/DST/reloj atrás/reinicio; sin doble cobro. Proponer cambios de comportamiento claramente. |
| **P0 GXB2-EVENT-RESET-001** | Estudiar reset/persistencia de puntos. La cuenta atrás UI llega al lunes; backend `point_events.py` no almacena periodo y conserva rondas agotadas | Periodo de evento definido y probado, coherente UI/backend; migration del estado previo sin pérdida ni premios duplicados. |
| **P0 GXB2-IDLE-SETTLE-001** | Investigar liquidación al cambiar fase (incluye `STAGE_HANG` y avance de campaña). Ahora `pending()` aplica tarifa de fase actual a todo el tiempo acumulado | Regla original investigada; si no recuperable, decisión local explícita; tests de cambio de fase, cap, guardado y collect sin doble recompensa. |
| **P1 GXB2-SAVE-001** | Registrar schema/migraciones y restore sobre copias temporales; documentar dependencias externas | Partida antigua→actual, backup/restore, rollback y daño controlado; ninguna prueba modifica profile.sqlite3. |
| **P1 GXB2-FIDELITY-001** | Corpus de casos de combate/progresión/equipo. Incluir return de materiales, exskills, bonos y recetas | Informes reproducibles, comparación con fuentes originales y casos límite; no sustituir fórmulas por estimaciones. |
| **P1 GXB2-UI-QA-001** | Revisar flujo actual en navegador con base temporal y puertos distintos, incluida navegación anidada y audio | Capturas y registro por flujo, costos/persistencia/volver/resize; no usar Iniciar.command para QA porque detiene servidores por nombre. |
| **P2 GXB2-CATALOG-001** | Manifest de versiones/assets, registro autoritativo items/fuentes/sumideros y mapa mensajes operativos | Cada regla/recurso tiene origen/version/hash o incertidumbre; diferencias APK 1.5.686/catálogo 1.5.655/cache 1.5.410 explícitas. |
| **P2 GXB2-EXPAND-001** | Tras estabilizar lo anterior, elegir Exchange, misiones de Novato o Slots; investigar solo ese sistema primero | Reglas originales documentadas, API/UI/persistencia/costes/reset y test del ciclo; registrar handoff. |
| **Preservación GXB2-RECOVERY-001** | Mantener export anónimo; buscar snapshots adicionales solo si aparecen nuevas fuentes aportadas | Parser primero read-only, reporte sin credenciales; no inventar roster ni propiedad; import solo si IDs y conteos se pueden validar. |

## Discovery inbox / desconocidos

- **UNKNOWN-0001 — cadencia de botín original.** Source: `gxb2/campaign.py`, `DROP_INTERVAL=600`. Observed: decisión local, cliente no documenta intervalo del servidor. Research `[R]`, implementation `[M]`, Owner NONE. Next: recuperar evidencia o mantener sustitución identificada.
- **UNKNOWN-0002 — puntos por Advanced Capsule.** Source: `point_events.py`/`point_events.json`. Observed: 10 por tirada es supuesto local; premios van a Bolsa en vez de Mail. Research `[R]`, implementation `[M]`, Owner NONE.
- **DISCOVERY-0004 — periodo de puntos ausente.** Source: `web/events.js:pointEvent`, `point_events.add/snapshot`. Observed: cuenta atrás semanal sin reset backend; no campo periodo. Implementation `[P]`, Owner NONE. Task GXB2-EVENT-RESET-001.
- **DISCOVERY-0005 — tarifa idle retroactiva.** Source: `campaign.pending`, `Engine._dispatch/STAGE_HANG`. Observed: a t=100, cambiar fase 1→10 cambia EXP de jugador pendiente 100→120 sin pasar tiempo, según sonda en memoria. Original settlement `[?]`, Owner NONE. Task GXB2-IDLE-SETTLE-001.
- **DISCOVERY-0006 — home systems omitidos en listas antiguas.** Source: `home_systems.py`, `home-menus.js`, `test_home_systems.py`. Observed: operaciones locales de Servant/Libro/travel/Cosmos/contactos/mail; alcance parcial reflejado arriba. Owner NONE.
- **UNKNOWN-0003 — correspondencia de sistemas/versiones.** Source: tablas `starry_altar`, `travel_*`, `battlepass_*`, `pet_exskill`. Observed: catálogo y operaciones parciales no demuestran Stellar Altar/Galaxy Voyage/Ulticore completos. Research `[R]`, Owner NONE. Next: resolver nombres y relaciones con evidencia del cliente.

## Handoff breve

La auditoría termina con documentación integrada, evidencia automatizada y bloqueos liberados en [AI_WORKBOARD](AI_WORKBOARD.md). No hay cambio de gameplay ni tarea de implementación reclamada. La siguiente prioridad es **GXB2-TIME-001**, coordinada con reset de eventos y liquidación idle; reclamar antes de tocar backend. Para cualquier trabajo nuevo: checklist → workboard → este informe → código/fuente concreta → implementación → verificación → handoff. Preservar primero; registrar modificaciones aparte.


## GXB2-CLAUDE-WAVE-005 — 2026-09-29 (Claude)

| Sistema | Estado | Evidencia | Pendiente |
|---|---|---|---|
| UI de tamaño fijo | `[T]` | `web/frame.css`, `web/frame.js`; revisión visual de Inicio, Campaña, Chicas, Ficha, Eventos, Bolsa, Servants y Excursión | Revisión de todas las vistas antiguas; pantallas con `100dvh` heredado; comprobación táctil |
| Servants (UI + combate) | `[T][P]` | `web/servant.js/.css`, `tools/extract_servants.py`, `data/servants.json`, `Engine.battle_pet`, `runtime/battle_host.lua` (petA), `runtime/lua/app/models/ReportPetAttr.lua` (bytecode original); prueba manual: misma batalla derrota→victoria con Deerling | Ulticore/ex-level, Reborn, Training, FX de la habilidad del Servant |
| Excursión: mapa y edificios | `[T][P]` | `web/excursion.js/.css`, `tools/extract_excursion.py`, Spine `travel_main` 01–07 en coordenadas del prefab | Asignación de chicas a edificios en UI (backend existe), Training con nombres/atributos originales, market de edificios |
| Excursión: aventura Explore | `[T][M]` | `gxb2/explore.py`, `Engine.explore_action`, `tests/test_explore.py` (4); QA: evento Help Seeker → cofre → abrir con gemas; combate real contra enemigos de nivel 80 | Pesos/élite/subida son LOCAL-020…023; tienda de cofres (explore_mystery_shop), cambio de explorador, eventos de la historia |

53/53 pruebas (`python3 -m unittest discover -s tests`).


## GXB2-CLAUDE-WAVE-006 — 2026-09-29 (Claude)

| Sistema | Estado | Evidencia | Pendiente |
|---|---|---|---|
| Dates / relaciones | `[T]` | `gxb2/relations.py`, `web/dates.js/.css`, `tools/extract_relations.py`, `data/relations.json`, `tests/test_relations.py` (3); QA: regalo +20 con voz de reacción, 33 voces | Bonus de intimidad en HeroAttr, escenas de cita/Oath, marcos |
| Daily Tasks / Trophies | `[T][M]` | `gxb2/missions.py`, `web/missions.js/.css`, `tools/extract_missions.py`, `tests/test_missions.py` (3); QA: claim de trofeo con popup | Semanales, Alchemy/Internship/Hearts, reclamar todo |
| Tiendas | `[T][M]` | `gxb2/shops.py`, `web/shops.js/.css`, `tools/extract_shops.py` (+9 Spines de tenderas y 172 iconos), `tests/test_shops.py` (3); QA: mapa, Market (compra → Purchased), Sanctuary, Girls Store y Antique Store | Transfer (bloqueado), Skin Store, compra en cantidad, burbujas/voces de tenderas |
| Junior Varsity | `[T][M]` | `gxb2/arena.py`, `Engine.arena_action`, `web/arena.js/.css`, `tools/extract_arena.py`, `tests/test_arena.py` (4); QA: combate real → Victoria +27 y carta | Varsity 3v3, Elite League, defensa, animación de cartas |

66/66 pruebas (`python3 -m unittest discover -s tests`).


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

## House y Outfit — GXB2-HOUSE-DRESS-014 (ChatGPT, 29/09/2026)
`[R][T][P][M]` Café/Dorm y vestuario:297 muebles, tienda269 ofertas/13 series,425 estilos,276 modelos originales con capas y accesorios. Editor local con persistencia/cancelación, giro/recuperar, restricciones/coste/inventario/confort/dos pisos/chicas propias; armario con piezas propias y guardado. Outfit Store solo visual; gacha y pity, visitas, ingresos e interacciones House pendientes.9 tests específicos OK y QA normal temporal. Suite global no verde por Shrine paralelo y comparación temporal de Developer. [Pruebas, límites y handoff](validation/house-dress-2026-09-29/README.md).


### GXB2-CARDS-CAMPUS-015 — ChatGPT,29/09/2026
Campus elevado60px de lienzo; tarjetas compactas con marco original, nombre sobre retrato, emblemas según estrellas/facción y hover sin desplazamiento. QA visual9232 sobre partida temporal, filtros/detalle/galería e imágenes revisados, sintaxis JS válida. [Evidencia y límites](validation/cards-campus-2026-09-29/README.md). Incremento visual entregado; sistemas globales siguen parciales. Claims015 liberados. No cambios de backend ni guardados habituales.


### GXB2-CARD-CORNERS-016 — entregado, ChatGPT29/09/2026
Esquina de facción corregida con marco en9 secciones:22px de esquina para22px de icono, sin estirar textura completa. Dorado y avanzado verificados en QA temporal9232; assets/backend/saves intactos. [Evidencia](validation/card-corners-2026-09-29/README.md). Claim016 liberado.


## Recuperación original — tanda050, 2026-09-30

[R][P] Android auditado: 31 formaciones anónimas, 62 chicas sin identificar y preferencias; no contiene roster/inventario completo y no permite migración jugable. Herramientas de auditoría y lector de índice de respaldo iPad implementados, con 5 pruebas específicas aprobadas. El usuario conserva la app en iPad, pero falla por conexión. Próximo paso: obtener respaldo Finder y comprobar archivos de la app. Importación completa sigue pendiente; no se tocó la partida habitual. [Evidencia](validation/original-save-2026-09-30/README.md).


## Recuperación iOS — tanda051, 2026-09-30

[T][R][P] Exportación iMazing de iPhone japonés analizada sin modificar: 71 filas de formación, cuatro cuentas separadas, 45 selecciones de estilo y caché histórica de 24 conjuntos en la cuenta principal de la caché. Sin roster completo ni inventario actual; personaje especial de Guild Competition excluido de importación por ser modificable. Auditor de exportación implementado y 3 pruebas específicas OK. La migración completa continúa pendiente. Próxima fuente posible: exportación del iPad, sin asumir que contiene la cuenta completa. [Informe](validation/ios-save-2026-09-30/README.md).

## Eventos — tanda052, 2026-09-30

[T][P][M] Jigsaw (37) y Puppet Parade (189) jugables en Inicio → Eventos → Exclusives. Jigsaw conserva 24 ilustraciones, las 216 piezas originales, intercambio de dos posiciones por 1 energía, 50 compras progresivas y seis hitos. Puppet conserva 17 hitos y sus premios; las marionetas no se consumen al cobrar. Progreso persistente y premios protegidos contra doble cobro. LOCAL-070 sustituye el calendario/suministro del servidor: eventos permanentes, 3 energías y 40 marionetas diarias, premios directamente a la bolsa. Falta la presentación/animación completa y el calendario original. Suite completa: 303/303 OK; siete pruebas propias y QA visual con partida temporal. [Evidencia](validation/events-2026-09-30/README.md). Próximo foco: Firework Project, Winning Pair y calendario de eventos.

## Firework Project — tanda053, 2026-09-30

[T][P][M] Firework Project 196 jugable en Inicio → Eventos → Exclusives: fabricar ×1/×10, cuatro resultados ponderados (15/50/20/15), coste de 25 polvos, nivel por 100 polvos gastados, 21 canjes con niveles y límites originales. No confundir con Firework Display 274. Estado persistente; operaciones inválidas no gastan recursos. LOCAL-071: archivo permanente y 250 polvos por día local para sustituir fuentes del servidor. Faltan calendario, fuentes originales de polvo y animación Spine de fabricación. Siete pruebas específicas; suite completa 311/311 OK. [Evidencia](validation/firework-2026-09-30/README.md). Siguiente foco: Winning Pair y calendario de eventos.


## Pulido visual y tarjetas de skins — GXB2-POLISH-060, 2026-09-30

- [x] Graduate: encuadre por límites visibles de la ilustración (537 imágenes), estrellas originales, retratos disponibles sin apagado artificial y diálogo original.
- [x] Colección: equipar una skin cambia la tarjeta de esa copia; quitarla devuelve la tarjeta base. No altera otras copias de la misma chica. Galería prioriza 323 tarjetas originales de skins y señala ilustraciones pendientes.
- [x] Barras, pestañas y marcos: refinamiento de bordes, navegación inferior y paneles del gremio; entrada directa al territorio cuando ya existe gremio desbloqueado.
- [x] Menú: saldos sin solapamiento con Volver, navegación inferior dentro del lienzo y botones clonados de navegación operativos.
- [x] QA en partida de desarrollador separada: Alice 10★ equipar → recargar → quitar; otras copias conservan su tarjeta base. 6 pruebas de skins y 7 de promoción local, comprobación de orden/filtros Graduate y sintaxis correctas.
- [ ] Continuar revisión visual de Dorm, vestuario, eventos y demás pantallas usando referencias. El inventario de 4.311 referencias no equivale a revisión completa.

Evidencia y alcance: [validation/polish-2026-09-30/README.md](validation/polish-2026-09-30/README.md).


## Graduate — referencia de filtros y atributos, 2026-09-30

- [x] Filtros verticales con un emblema y número: amarillo 2–5, rojo 6–9 y naranja/dorado 10. Se conserva multiselección on/off y orden existente sin filtros.
- [x] Tres líneas: comparación real de atributos actual/después y límite de nivel, sin escribir en la partida. Ya no abre materiales ni lleva marcador de recetas listas.
- [x] Casilla Auto-seleccionar materiales de 5★ operativa, inicialmente apagada; revisión manual independiente debajo de la receta. Copias específicas y materiales de otras estrellas mantienen selección previa.
- [x] QA desarrollador separado: Sakura 6→7, off/on, preview Vida 43819→74865 y Ataque 5826→6836; diez pruebas de promoción/preview y pruebas JS correctas.
- Evidencia: validation/polish-2026-09-30/graduate-filters-reference.png y graduate-attributes.png.


## Graduate — ayuda visual y selección manual, 2026-09-30

- [x] «?» abre la guía original aportada por el usuario, con notas en español sobre filtros, atributos y materiales. Ventana cerrable con × o Escape y retorno de foco. Cabecera visible al desplazar la guía.
- [x] Las tarjetas de base/materiales abren el selector correspondiente. El selector excluye copias elegidas en otros huecos, bloqueadas como material e intercambio pendiente.
- [x] QA en partida desarrollador separada: Sakura 6→7; materiales 89,90,91,92 distintos, el 89 deja de aparecer en Material 2. Receta completa y botón habilitado, sin ejecutar Graduate.
- Evidencia: validation/polish-2026-09-30/graduate-help.png. Fuentes y guardados habituales intactos.


## Ajuste de referencia — ALL y filtro exclusivo, 2026-09-30

La instrucción nueva del usuario sustituye la multiselección anterior: ALL seleccionado por defecto, sólo un filtro de destino activo (2–10), elegir otro apaga el anterior. ALL recupera el orden general existente. La fila Revisar base y materiales 5/5 queda oculta: tocar una tarjeta abre su selector y Listo lo oculta de nuevo. QA navegador: 5→6 deja sólo 6 activo; ALL; selector false→true→false; consola sin errores. Evidencia graduate-all-clean.png. No se ejecutó Graduate. Servidor de prueba 9242 conservado porque el usuario lo está usando en modo desarrollador.

## GXB2-NAV-073

Chat: botón azul original lateral izquierdo; correo sólo receptor/adjuntos y borradores trasladados a Chat. Friend Boss en cuarta pestaña Co-op de Amigos, sin acceso independiente de Inicio. 18 pruebas relacionadas OK y QA visual temporal; ver NAVEGACION_CHAT_AMIGOS.md. Envío social sigue pendiente.

## GXB2-CAMPAIGN-074

Estados de botín/Collect, cinco chibis más grandes, dos entradas superiores y contadores de campaña ajustados a las referencias. Error de fort_finish corregido: premio de capítulo sólo tras última etapa. Suite366 OK y QA temporal; detalle en CAMPANA_ESTADOS_REFERENCIA.md. ProtectDoggy aún pendiente de minijuego.
