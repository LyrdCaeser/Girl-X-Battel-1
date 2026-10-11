# GxB2 Reborn — decisiones y sustituciones locales

Registro inicial: 2026-09-28, GXB2-DOC-AUDIT-001. Describe comportamiento **ya presente**; esta auditoría no introduce ni aprueba un nuevo balance. Volver a [LEEME](LEEME.md), [checklist](GXB2_MASTER_CHECKLIST.md), [estado y prioridades](ESTADO_PROYECTO.md) y [workboard](AI_WORKBOARD.md).

Las tablas y el motor recuperado se preservan como referencia. Una hipótesis del servidor no se convierte en regla original por tener un test local aprobado. `[M]` significa adaptación; falta una separación general configurable Original/Classic vs Reborn. Hasta entonces, cada sustitución debe estar identificada.

| ID | Decisión actual / fuente | Estado y fidelidad pendiente |
|---|---|---|
| LOCAL-001 | Perfil ficticio, web local y paquete inicial en `engine.new_state`; identidad `local-player-1` | `[M]` sustituyen servicios originales. APK/SDK no conectado; UI nueva usa assets originales. |
| LOCAL-002 | Idle: `campaign.DROP_INTERVAL=600` | `[M]` una tirada por caja cada diez minutos. Intervalo del servidor no recuperado; tick 5 s y cap 12 h tienen referencia cliente documentada. |
| LOCAL-003 | Capsule Points: diez puntos por avanzada, premios a Bolsa en `point_events.py` | `[M]` valor supuesto; entrega original por Mail según cliente investigado. Periodo semanal backend pendiente. |
| LOCAL-004 | `events.touch` registra un día al abrir Eventos/actuar; sin doble VIP | `[M]` reemplaza online_days del servidor y privilegios VIP ausentes. Fecha local; Quiz/Libro usan UTC. |
| LOCAL-005 | `events.js` rota cinco eventos archivados por pestaña semanalmente | `[M]` presentación local. No activa reglas ni reinicia estado de puntos. No es un scheduler funcional de eventos. |
| LOCAL-006 | BFF ×10 repite sorteo ID 9 en `engine.py` | `[M]` cliente solo documenta botón unitario. Costes/grupos se conservan según tabla. |
| LOCAL-007 | Treasure/crystal sortea por pesos en `equipment.pick` | `[M]` algoritmo de servidor no recuperado; costes y pesos vienen de datos extraídos. |
| LOCAL-008 | Contactos y borradores locales, mail de prueba solo DEV en `home_systems.py` | `[M]` no implementa peticiones a jugadores ni generación normal de rewards por correo. |
| LOCAL-009 | Fantasy Book sin temporada final, cuatro misiones y tiers gratuitos | `[M][P]` edición local; paid_award solo previsualizado. Límites de tienda persistentes, reset de temporada pendiente. |
| LOCAL-010 | Cosmos/Excursion en `home_systems.py` | `[M][P]` reglas reconstruidas desde tablas del cliente; no backend recuperado. Comparar costes, RNG, garantías, tasas y calendarios con evidencia original. |
| LOCAL-011 | DEV en SQLite independiente, recursos repuestos/nivel 400 en `Engine._load` | `[M]` herramienta de pruebas, no balance normal ni evidencia de progreso sostenible. |
| LOCAL-012 | Campaign seed derivada de battle_count; Quiz/Tests y adquisición usan aleatoriedad local | `[M]` combate repetible con semilla explícita; no demuestra origen/autoridad del RNG del servidor ni RNG global determinista. |

Al tomar una nueva decisión: anotar ID, fuente/version, regla original conocida, incertidumbre, alternativa local, archivos, responsable y pruebas. Si se cambia una regla de preservación, documentar cómo se conserva o recupera el modo original. Low-star endgame, VIP gratuito, recompensas antes pagadas y rebalance son objetivos pendientes, no logros actuales.


## Decisiones de GXB2-RECON-WAVE-001 — cierre 29/09/2026

| ID | Fuente/contrato original | Adaptación local y limitación |
|---|---|---|
|LOCAL-013 | ProphetReplace/Slot + partner_replace/dropbox | Exchange ponderado con misma rareza/facción y exclusión actual; backend original no recuperado. dropbox_id_2 pendiente; relación reiniciada a0 como sustitución de respuesta original. |
|LOCAL-014 | GambleWindow/Gamble + gamble/config/up/dropbox | Un premio ponderado por posición, luego sorteo entre posiciones no agotadas. Tablero persiste24h desde creación, first refresh gratis, paid no desplaza gratuidad, historial50. cool conservado sin simular. Probabilidad oficial y reset alineado pendientes. |
|LOCAL-015 | Eventos13/16/20 tienen rounds/umbrales pero calendario servidor ausente | Recurrencia semana ISO lunes 00:00 UTC; legacy preservado/vinculado en primera acción; archivo8 semanas; reloj atrás mantiene última semana. Premios directos siguen LOCAL-003. |
|LOCAL-016 | Idle tick5s/cap12h del cliente; liquidación servidor desconocida | Historial por fase y ticks completados; switch exacto pertenece a fase anterior. Mantiene fracciones; legado sin historia usa fase guardada. Cadencia600s sigue LOCAL-002. |
|LOCAL-017 | Login ya local, Quiz/Libro yaUTC | Engine aporta reloj inyectable; se preservan calendarios previos. Quiz rechaza reapertura de día pasado; no se afirma protección global ni calendario original. |

LOCAL-003 ya tiene periodo por LOCAL-015; LOCAL-005 sigue siendo solo archivo visual y no acredita scheduler integral. Todas las decisiones mantienen tablas originales intactas y están concentradas en módulos/reglas explícitos; selector general Original/Reborn sigue pendiente. Investigación detallada, hashes y siguientes acciones: [RESEARCH](validation/reconstruction-2026-09-28/RESEARCH.md).


## GXB2-SLOTS-LUCKY-004 — 2026-09-29

- **LOCAL-018 [M]: Lucky Store** usa shop_type3 y contratos originales; coste/límite/nivel/intervalos recuperados. El servidor local sortea ocho filas distintas ponderadas, mantiene ofertas vencidas hasta REFRESH, inicializa espera24h y reinicia el tiempo tras refresh pagado. limit_num de tabla no demuestra el algoritmo del servidor. Snapshot puro, transacción, persistencia y reloj hacia atrás probados. Solo tienda3 implementada.
- **LOCAL-019 [M]: presentación Slots** idle de dealers original; Skip por modalidad y bulk se guardan en localStorage (no en partida ni configuración Unity). Secuencia breve de luces local, no animación/audio íntegros del cliente. Probabilidades reflejan normalización Reborn sin cool; Records es historial local50. Contadores usan reloj monotónico con timestamp del servidor; no reabren una oferta por reloj local cambiado. Layout de Lucky dos columnas sobre fondo Slots, ShopWindow completo pendiente.

[Fuentes, evidencia y unknowns](validation/slots-lucky-2026-09-29/RESEARCH.md). Los recuentos47 anteriores son históricos;49 tests actuales no prueban fidelidad global.


## GXB2-CLAUDE-WAVE-005 — 2026-09-29 (Claude)

- **LOCAL-020 [M]: pesos de eventos de Explore.** `travel_event.value` suma exactamente 10000 entre los eventos no élite, así que se usa como peso del sorteo. El servidor original no está recuperado.
- **LOCAL-021 [M]: enemigo élite.** Sustituye el sorteo tras `travel_strong_enemy_condition[0]` (5) victorias comunes; vencerlo reinicia el contador.
- **LOCAL-022 [M]: calidad del cofre.** `reward_box_type` 2 tira dos veces el grado del cofre y se queda con el mayor; 0 entrega la dropbox del evento (Food Truck).
- **LOCAL-023 [M]: subida de nivel de Explore.** `update_box_limit "g#n"` se interpreta como cofres de grado g abiertos en el nivel actual; se reinicia al subir.
- **LOCAL-024 [M]: UI de tamaño fijo.** Un único lienzo de 480×853 (9:16) escalado con `transform`, en lugar de la resolución y el anclaje de Unity. Es presentación, no reglas.


## GXB2-CLAUDE-WAVE-006 — 2026-09-29 (Claude)

- **LOCAL-025 [M]: Daily Tasks y Trophies** (`gxb2/missions.py`). Los contadores diarios los llevaba el servidor: aquí se cuentan acciones locales (forja, Slots, cápsulas, recogida idle, quiz, Junior Varsity) y se reinician a medianoche local. Alchemy, Internship y Hearts siguen visibles pero no avanzan (no existen offline). La columna `coefficient` por nivel no se usa: premios base. Los trofeos se miden desde la partida y se reclaman en orden siguiendo `next_achieve_id`.
- **LOCAL-026 [M]: tiendas** (`gxb2/shops.py`). Los días terminan a medianoche local (el cliente usaba el día UTC del servidor). Los límites del Guild Store también se reinician a diario, y su refresh pagado (4#20000) los reinicia al momento. Transfer (tienda 2) no se reconstruye: todas sus filas son `0#0` porque el servidor generaba el inventario. **026a Dates:** `visit` entrega una sola vez `love_gift_initial`, y Compose convierte 44#10 en un regalo aleatorio entre 1000001 y 1000040 (el servidor original no está recuperado).
- **LOCAL-027 [M]: Junior Varsity** (`gxb2/arena.py`). El servidor hacía el emparejamiento, el rating y la clasificación. Aquí la puntuación es tipo Elo con K = `arena_score.coefficient` de la banda: al ganar sube K·(1−E) y al perder baja K·E, siempre al menos 1 punto y sin bajar de 0. La clasificación son 50 rivales: los 15 robots originales (900 + 30·i) y NPC persistentes con alineaciones de robots cuyo nivel escala con el del jugador. Se gana una de las 3 cartas tiradas. El premio diario por rango se reclama en la ventana. Al terminar la temporada de 15 días se entregan los premios de temporada y la puntuación vuelve a 1000. La defensa es la formación actual.


## GXB2-CLAUDE-WAVE-007 — 2026-09-29 (Claude)

- **LOCAL-028 [M]: Patrol** (`gxb2/patrol.py`). Del cliente se conservan: 600 fases, reservas de batallas, objetos, tienda, desbloqueo en la fase 92 de campaña, 5 chicas con la build fija, 1 chica por combate, HP/energía de ambos bandos, 15 rondas y tipo de combate DUNGEON (solo gana quien elimina a todos). Lo que decidía el servidor se sustituye así:
  - **Calendario:** ciclo de 4 días desde la medianoche local del 07/01/2019; abierta las primeras 48 h. Cada ventana nueva reinicia equipo, objetos y tienda, y conserva la mejor fase.
  - **Resultado de victoria:** `award_weight "a|b|c"` se reparte en el orden de las columnas siguientes de la tabla (cofre `dropbox_id`, objeto `drug`, mercader `trader`). Las cantidades del cofre salen del rango `id#min#max`, con distribución uniforme.
  - **Tienda del mercader:** fases 1-2 → tipo 1 (Primary), 3-4 → 2 (Medium), 5-6 → 3 (Senior).
  - **Auto Smash:** se empieza en la fase de mayor dificultad cuya casilla 50 se superó en rondas anteriores. Cada fase saltada tira un resultado de victoria normal: los cofres van a la bolsa y los objetos y ofertas se guardan.
  - **Enemigos:** conservan HP/energía mientras dura la misma fase; una fase nueva empieza al 100%.
  - **Sin Servant** en Patrol: la petición original solo lleva `partner_index`.
  - **Runtime:** `battle_host.lua` acepta `battle_type` y devuelve `end_status` (HP% y energía por posición). No cambia ninguna regla del motor.

- **LOCAL-029 [M]: House Exam** (`gxb2/house_exam.py`). Del cliente se conservan: tablas `school_practise_new2`, `school_practise_point_new2` y `school_practise_ticket_buy`, calendario de temporadas desde `school_practise_season1_start_time` (13 días de examen + 1 de resultados), variante de enemigos `(temporada−1) % 3 + 1`, la regla de que solo luchan chicas de la facción de la casa, los tickets y certificados con sus refrescos a las 00:00 UTC, las recompensas de primera vez que se guardan entre temporadas, la puntuación y el Raid. Sustituciones locales:
  - **Premio de temporada:** el original llegaba por correo; aquí se paga solo la primera vez que se abre el juego tras terminar la temporada (`last_award` lo muestra en la lista de casas). Las temporadas anteriores a la primera que vio la partida no se pagan.
  - **Marco de casa:** no se entrega, porque dependía de la clasificación del servidor.
  - **Admission Ticket:** se gasta al empezar el combate, se gane o se pierda (lo confirman las capturas 07 y 08).
  - **Formación:** se guarda una por casa (`formations`), como `readStorageFormation`. El Servant seleccionado entra en combate con el tipo de combate por defecto.


## Capsules/huevo — GXB2-CAPSULE-EGG-009,29/09/2026
Estado [P][M], alcance probado: gacha subido, huevo1.000→1 chica5★, puntos/excedente/guardado; BFF corregido a corazones11 y SUMMON15/16 (10/100), BAODI separado en12/SUMMON9.90/90 pruebas y20 JS válidos. Se preservan saldos; no se recalcula historia. VIP3 original documentado y omitido en Reborn según petición; FX/espacio pendientes. [Evidencias y handoff](validation/capsule-egg-2026-09-29/README.md), [cuatro referencias](docs/references/2026-09-29-c/README.md). Fuentes/saves usuales intactos; servidor habitual no detenido. Cargar el backend nuevo requiere reiniciarlo y recargar navegador.

- **LOCAL-030 [M]: animación de invocación** (`web/summon-anim.js`). Secuencia, Spines, animaciones y sonidos originales. Adaptaciones:
  - Además del gesto de deslizar hacia abajo sobre la máquina, hay un botón "Desliza hacia abajo" que hace lo mismo, para ratón y accesibilidad.
  - El nombre de la chica se muestra en HTML en lugar de las etiquetas que seguían los huesos `name`, `cv` y `zhiye` (en el Spine son texto de muestra y se ocultan).
  - No se reproduce la voz de bienvenida (`getStartDialog`) ni el efecto de estrellas `fx_ui_newgirl_gain_star`.
  - Las invocaciones que no tienen máquina (fragmentos y similares) van directas a la revelación, como `isSimple`.


- **LOCAL-031 [M]: Guild Lab** (GXB2-GUILD-LAB-010). Laboratorio personal persistente sin simular membresía remota. Datos, costes, requisitos, buff y devolución de tablas originales. Cada reset borra únicamente su grupo (1–5 básicos/10–14 avanzados); una cascada del servidor original no se ha recuperado. Las mejoras positivas se pasan al HeroAttr/BattleCreateReport original y se filtran allí por clase; no se inventan mejoras enemigas. No se regala moneda4 en partida normal; DEV la rellena. UI cotejada con captura y prefab, con pestañas explícitas,×10 adicional y confirmación local. FX/audio/cola de long-press pendientes. [Detalles](validation/guild-lab-2026-09-29/README.md).


### Lab: flechas de páginas — GXB2-GUILD-LAB-012,29/09/2026
Flecha derecha Básico→Avanzado, izquierda Avanzado→Básico y dos puntos inferiores reemplazan pestañas de texto. Sprites originales, centrado automático y clase conservados; QA de ida/vuelta correcta, sin gasto. Sigue pendiente transición original0.4s/FX; se conserva consulta de requisitos avanzados antes del desbloqueo. [Evidencia/relevo](validation/guild-lab-arrows-2026-09-29/README.md).

## GXB2-CLAUDE-WAVE-010 — 2026-09-29 (Claude)

- **LOCAL-031 [M]: Character Challenge** (`gxb2/hero_challenge.py`). Modos Normal y Puzzle con las tablas originales: chicas-monstruo prestadas, bendiciones como `god_skills`, Servants de nivel 90, Coupons (item 55) y la regla de muertes al perder. Sustituciones locales:
  - Cada elección ofrece **3 candidatos**: chicas ponderadas según la caja de la fase (sin repetir las que ya tienes), o bendiciones y Servants que aún no tienes.
  - `reward1` se paga una sola vez por fase.
  - **Ganar no gasta Coupon**; solo perder, como dice la ayuda.
  - Los modos Speed y Chess no se reconstruyen.
- **LOCAL-032 [M]: Sanctuary** (`gxb2/sanctuary.py`). Del original se conservan: fases y tipos, bendiciones (skills como `god_skills`; 13/14 son curaciones), HP persistente, tipo de combate TRIAL_NEW, jefe con premios por tramos de daño y banda de nivel, 1 reinicio diario no acumulable y el mapa con `new_trial_offset` e iconos originales. Sustituciones locales:
  - **Rivales Normal/Elite:** reflejo de tus 6 mejores chicas, con el nivel multiplicado por (0,6 + `power`).
  - **Bendiciones:** la Elite ofrece 3 de su lista y las Normal no dan ninguna.
  - **Santuario:** Volcano y Deep Sea se alternan cada lunes (UTC).
  - **Jefe:** se le puede atacar mientras te queden chicas; cada tramo se paga una vez por ronda.
  - **Barra del jefe en combate:** reparte el daño total proporcionalmente a la pérdida de HP por frame.
  - **Sin incluir:** la rueda de Chaos Crystals y el pase de Sanctuary.
- **Combate (todas las vistas):** la barra inferior es la **energía del Servant** (`BattleWindow.petBar_`: avatar del Servant + `frame.eps` pos 13) y se oculta si no llevas Servant; ya no es el progreso de rondas.


### Territorio del gremio y hover Lab — GXB2-GUILD-UI-013,29/09/2026
Mapa con cinco edificios/posiciones del prefab original, fuente, rótulos y comerciante yuanshu animada; canvas ajustado a densidad de pantalla. Corregida sustitución del transform de centrado de nodos/flechas por hover global. Merchant abre tienda Guild y vuelve al territorio. QA visual/navegación sin gasto y sintaxis JS correctas; ensayo físico de hover pendiente de confirmación manual. Guild global sigue parcial: actividades/membresía y FX ambientales pendientes. [Evidencia, fuentes y relevo](validation/guild-ui-2026-09-29/README.md). Sin cambios en backend ni saves habituales.

## GXB2-CLAUDE-WAVE-011 — 2026-09-29 (Claude)

- **LOCAL-033 [M]: Internship** (`gxb2/internship.py`). Del original se conservan: estrellas 1-7, requisito de estrellas y una chica por condición de facción o clase, duración, recompensa por caja, aceleración, cancelación, bloqueo, refresco a 10 gemas por encargo, pergaminos 24/25 con sus probabilidades y máximo de 200 encargos. Sustituciones locales:
  - **Encargos nuevos:** llegan a las 00:00 UTC; son 5 al día porque el VIP sigue en 0.
  - **Encargo generado:** cada uno recibe `need_num` condiciones y un nombre al azar de sus listas.
  - **Tarea diaria de Internship:** cuenta los encargos completados.
  - **Sin incluir:** el modo Multi-Intern y el reclamo en bloque.
- **LOCAL-034 [M]: Alchemy** (`gxb2/midas.py`, Midas v2). Del original: 1 reclamo gratis al día de `midas.gold_new[nivel]` y 5 compras con coste y multiplicador de `midas_buy_coin`. Sustituciones locales:
  - **Reinicio:** a las 00:00 UTC.
  - **Entrada:** se abre desde la píldora de oro de Inicio (en el original, desde el "+" del oro) y desde el Go de la tarea diaria.
  - **Tarea diaria de Alchemy:** cuenta cada uso.

## GXB2-CLAUDE-WAVE-012 — 2026-09-29 (Claude)

- **LOCAL-035 [M]: Old Campus Exploration** (`gxb2/old_campus.py`). Del original se conservan: temporadas de 13 + 1 días que alternan las tablas A y B, 10 niveles de 2-3 fases con apertura progresiva, un equipo por fase sin repetir chicas en el nivel, planes que se suman a la base 10, la puntuación actual que se reinicia al cambiar el equipo y la mejor que se conserva, el total y los premios de nivel y de puntuación. Sustituciones locales:
  - **Planes de cada temporada:** los elegía el servidor. Aquí se sortean con una semilla fija por temporada, respetando el número por puntos de `old_building_buff_lock_1..4` (Primary = 10 con 1,1,1,2,2,2,3,3,4,5, como la captura 05) y los desbloqueos de `old_building_buff_num` / `_num_2`.
  - **Sin reconstruir:** el nivel 11 (ranking de daño), los rankings y marcos, y la tienda de temporada.

## GXB2-CLAUDE-WAVE-013 — 2026-09-29 (Claude)

- **LOCAL-036 [M]: Echoes of Time** (`gxb2/echoes.py`). Del original se conservan:
  - los tiempos (Clockwork de 360 s, una carta cada 300 s, Time Essence de 600 s, Temporal Chips 10 máx. +1/1800 s);
  - los pesos de mazos y cartas, y el nivel de las cartas según la tecnología aprendida;
  - las subcartas de victoria y derrota, los grados por puntos y los Time Shards;
  - el árbol del Planetarium con requisitos, los 5 tipos de desbloqueo y los efectos;
  - las fases con premio de primera vez, los logros y el 85 % para abrir el siguiente mundo.

  Sustituciones locales:
  - **Atributos:** los Outfits no existen offline, así que los atributos negros salen solo del Planetarium. El boost verde es round(suma de niveles / 3).
  - **Cartas de Desafío:** se ganan si los tres atributos alcanzan la `base` de la carta. Las cartas de Outfit (tipos 10 y 11) no salen.
  - **Fases:** usan el motor original sin los efectos de atributos.
  - **Sin reconstruir:** Chica de Apoyo, cristales y ranking del Time Vortex (solo se guarda el mejor daño, para su logro).
  - **Desbloqueo:** fase 55 de la campaña (function 47).

## GXB2-CLAUDE-WAVE-014 — 2026-09-29 (Claude)

- **LOCAL-037 [M]: Santuario Tsuruga / Realm of Trials** (`gxb2/shrine.py`). Del original se conservan:
  - las temporadas de 12 + 2 días y las 15 invitaciones por temporada (más 5 compras de 10 gemas);
  - el desbloqueo con el piso 500 de Tests y una chica de 10★;
  - las 3 pruebas con sus 2 entornos por temporada;
  - las 15 fases: combate, recompensa, tienda, recuperación y jefe;
  - la dificultad 1-300, que aplica el propio motor original (`shrineId`), y los combates de 15 rondas (tipo 61);
  - la vida que se conserva entre fases y los 24 buffs como god skills (3 niveles);
  - los costes (180 / 90 / 180 al renunciar) y las 3 opciones de recuperación;
  - las fórmulas de misc para la dificultad desbloqueada y los puntos del jefe;
  - las tareas, los logros, las dos tiendas del Pond of Prayers y el prólogo con su historia.

  Sustituciones locales:
  - **Ranking:** no existe sin servidor. Al acabar la fase de desafío se da el premio del tramo según el total de la temporada (≥24000 → 201-500, …, cualquier prueba → 10001+), y lo mismo por prueba con la tercera parte.
  - **Grupo de enemigos:** el servidor elegía cuál de los grupos de cada fase aparece; aquí sale de un sorteo con semilla, igual que los buffs ofrecidos.
  - **Dificultad desbloqueada:** solo sube si la prueba deja puntos.
  - **Capítulos de la historia:** el capítulo N se abre tras N pruebas completadas.
  - **Sin reconstruir:** Tree of Chimes (sus logros quedan a 0), el Auto-Battle y el registro de combates.

## GXB2-HOUSE-DRESS-014 — sustituciones locales (29/09/2026)
House persiste localmente en profile.house_dress y usa items como inventario original. Inicialización concede una vez la dotación original al abrir, sin regalar sets Café. Guardado con transacción y revisión; colisión rectangular de huellas/apilado limitado con validación de soporte. Es una sustitución parcial, no equivalencia completa con HouseGrid/servidor. Confort/topes, ofertas/precios, piso200 y estilos gratuitos conservan tablas originales. Preview sincroniza las piezas Spine y separadores/puntos de accesorios originales; escena HTML sustituye Unity. Outfit Store conserva imagen y moneda258 pero desactiva tiradas hasta acreditar el algoritmo de probabilidad/soft pity; no usar pesos recuperados como prueba de un servidor idéntico. [Detalle](validation/house-dress-2026-09-29/README.md).

## GXB2-CLAUDE-WAVE-015 — 2026-09-29 (Claude)

- **LOCAL-038 [M]: Galaxy Voyage** (`gxb2/galaxy.py`). Del original se conservan:
  - las temporadas de 27 + 1 días y el desbloqueo (fase 156 y una chica de 10★);
  - los sistemas por temporada (4/4/6/6/6/8) y los 3 requisitos para abrir el siguiente;
  - la cuadrícula del mapa con el inicio abajo y el fin arriba, eventos de 1×1, 2×1, 2×2 y 3×3, y la exploración contigua ↑↓←→;
  - los tiempos por tipo y las rutas (6 + Voyage Team 2);
  - los cupones (10 al empezar, +10 al día, máximo 25), la vida persistente de enemigos normales y élite, y el Ruler de un solo intento debilitado 1 % por área desde el 30 % (máximo 40 %, enviado al motor como `galaxy_info`);
  - los buffs de los Mystery Planet;
  - los 3 Voyage Teams con la suma de (estrellas − 10);
  - System of Eternity con piratas de 72 h y el Galaxy Tyrant (1-20, empieza en 5);
  - las tareas, el Voyager Passport (fila gratuita) y las dos tiendas.

  Sustituciones locales:
  - **Mapa:** lo generaba el servidor. Aquí sale de un generador con semilla que sigue la tabla:
    - `line_events_num` áreas en las filas de inicio y fin;
    - las filas de élite solo con sus élites (actúan de muro);
    - cada evento en sus filas `area_id`, con su tamaño;
    - el resto, Blank Space o vacío, comprobando que el inicio y el fin quedan conectados.
  - **Rutas:** solo incluyen áreas explorables.
  - **Piratas:** usan las batallas de élite del sistema más alto abierto; hay 2 + (sistemas abiertos − 4) al día.
  - **Tyrant:** ganar un nivel paga también los inferiores que no se hayan cobrado.
  - **Textos de tareas que faltan:** 1009 se interpreta como Mystery Planets explorados y 1010 como el nivel más alto del Tyrant vencido.
  - **Passport:** la fila de pago no se vende.
  - **Ranking:** premio por tramos según los puntos de la temporada.
  - Ajuste con la captura 2026-09-29-h (System of Phantom):
    - las filas normales van completas, sin huecos;
    - solo tienen huecos la fila de inicio, la de fin y las de élite (confirmado);
    - el % de progreso usa la fórmula del cliente, `floor(x·100 + 0.1)`.

## GXB2-CLAUDE-WAVE-016 — 2026-09-29 (Claude)

- **LOCAL-039 [M]: Historia principal** (`gxb2/story.py`, `web/story.js`). Del original se conservan:
  - `main_plot_list` enlaza cada fase de campaña con "#antes#después": `pre` al empezar el combate (BattleWindow, `plotIds[2]`) y `post` tras la victoria (BattleController, `plotIds[3]`);
  - cada escena sigue la cadena de `next_id` con fondo, imagen de personaje, nombre ('*' = el jugador), diálogo, voces, música y ambiente (tabla `sound`), temblor y CG;
  - Memories: episodio → capítulo → sección. Se abre al superar su fase o con 2 Key of Memory (208) si la anterior está abierta.

  Sustituciones locales:
  - En campaña cada escena se ve solo la primera vez; se puede repetir en Memories.
  - De las variantes de diálogo "chico|chica" se usa la primera.
  - Las imágenes de personaje se escalan al 50 % en WebP. Todavía no se reproducen los efectos Spine de escena (`effect`), el movimiento de personajes (`position_move`) ni las apariciones y desapariciones animadas.

## GXB2-CLAUDE-WAVE-017 — 2026-09-29 (Claude)

- **LOCAL-040 [M]: Outfits** (`gxb2/dress.py`, `web/dress.js`). Del original se conservan:
  - las 288 piezas en 5 posiciones, con 1-2 estilos y un objeto por estrella (atributos base1/2/3, calidad 1-6);
  - la mejora con seda (260/261), fragmentos propios y fragmentos comunes por calidad (3999991-6);
  - los conjuntos, cuyas estrellas totales (5…30) activan el bonus especial sin tener que vestirlos;
  - las posiciones 1-3 no se pueden vaciar, y cuerpo y piernas pueden chocar;
  - Outfit Store y Outfit Sale (botones 258/259, cajas 50001/50003 y naranjas 50002/50004): 1,5 % de naranja, +400 de peso por tirada tras 50 fallos y garantizada a la 100; tirada gratis cada 24 h y 12 h; las piezas repetidas se convierten en sus fragmentos;
  - el chibi "Senpai" se compone como en SenpaiModel: 3 Spines (cabeza, cuerpo, piernas) repartidas en capas según sus ranuras `*_layer`, y sombrero y accesorio como imágenes en las ranuras del hueso con su offset, escala y rotación.

  Sustituciones locales:
  - **Atributos:** el servidor los sumaba. Aquí Courage/Charisma/Knowledge = suma de base1/2/3 de todas las piezas que tienes a su estrella, más el bonus por número de tiradas de la habilidad 1000101.
  - **Bonus especiales:** los que actúan sobre otros sistemas se muestran pero no se aplican.
  - **Outfit Sale:** siempre abierta.
  - **Fragmentos comunes:** se gastan automáticamente; el cliente dejaba elegirlos.
  - **Sin reconstruir:** logros de Outfits y DressShow.
- **LOCAL-036 actualizado:** Echoes of Time ya usa los atributos de los Outfits como atributos "negros" (más el Planetarium), como dice TIME_CLOISTER_HELP02.
- **Servidor HTTP:** backlog de 128 (antes 5). Las pantallas con muchas imágenes rechazaban conexiones, entre ellas a veces el CSS o `/api/state`.

## GXB2-CLAUDE-WAVE-018 — 2026-09-29 (Claude)

- **LOCAL-041 [M]: Skins de chicas** (`gxb2/skins.py`, `web/skins.js`). Del original se conservan:
  - la skin es un objeto (equip pos 7) que solo sirve a las chicas cuyo `partner.skin_ids` la incluye;
  - ponerla la pasa de la bolsa a `equipments[7]` y quitarla la devuelve; `show_skin` la muestra u oculta;
  - sus atributos (base1/base2) los aplica el HeroAttr original, y el informe de combate trae `skin_id`, así que la repetición dibuja el chibi de la skin;
  - el retrato grande es `partner_picture_<modelo>`, con su posición de `partner_picture`;
  - los puntos de colección salen de `collection.awards`, y los tramos HP/ATK de `collection_skin_effect`.

  Sustituciones locales:
  - Los tramos HP/ATK de la colección se muestran pero aún no se suman al combate.
  - "Method" es "Skin Shop" si se vende allí y "Exclusives" en el resto de casos.
  - Si una chica se consume como material, su skin vuelve a la bolsa.
- **LOCAL-042 [m]: Encabezado de House Exams sin servidor.** El botón Rank (`academy_assessment_rank_window2`) solo muestra un aviso, porque no hay ranking sin servidor. El botón Award y la estrella (`dress_show_buffs_detail_window` en el original) abren una ventana local con la temporada, el Exam Score, el récord y la recompensa del tramo actual.
- **LOCAL-043 [m]: Partida de desarrollador completa.** La partida dev añade una copia de cada chica de la guía (446) y repone equipo de prueba en cada carga, para revisar cualquier ficha (cósmicas incluidas) sin conseguirlas. La partida normal no cambia.
- **LOCAL-044 [M]: Limit-Break sin potenciales.** En esta versión local:
  - los nodos de potencial (`potentiality_choose_window`) se muestran bloqueados o desbloqueados según las estrellas, pero la elección de habilidad y su efecto en combate quedan pendientes;
  - Reverse (`potentiality_back_window`), Replace (`ten_star_exchange_window`) y Switch (`potentiality_switch_window`) muestran un aviso de "no disponible";
  - la ventana no muestra el bonus de HP/ATK del original, porque todavía no se ha localizado su tabla.
- **LOCAL-045 [M]: Reglas de Anima Gear que no están en el cliente.**
  - Las Anima Stones ganan un atributo extra nuevo en los niveles 5/10/15/20 (`soul_equip2_ex_buff_lvl`) mientras tengan menos de 4.
  - Los atributos extra del Artifact se tiran con `soul_equip1_ex_first_cost` y `soul_equip1_ex_cost` y se guardan o descartan.
  - El Ritual toma la estrella del dropbox de su nivel (`weight1` con Soul Token, `weight2` con Shiny Soul Token).
  - Los Plans (combinaciones guardadas) no están implementados.
- **LOCAL-046 [m]: Land of Souls.**
  - El progreso se conserva entre ciclos de 28 días; solo se renuevan los límites de la tienda.
  - Un combate perdido devuelve el ticket.
  - No hay ranking ni battle pass.
- **LOCAL-047 [m]: Reverse y Exchange.**
  - Reverse no devuelve el oro de subir nivel ni el cristal; sí la EXP al 65 %, las fiambreras de `bento_num` y el equipo.
  - En Exchange, la skin de la chica original vuelve a la Bolsa.
  - La intimidad pasa desde la copia con más intimidad.
- **LOCAL-048 [m]: Quick Formation.** Solo están las 3 alineaciones gratuitas (el precio en gemas de las siguientes no está en el cliente). Las chicas de una alineación no quedan protegidas contra usarse como material. El nombre se cambia con doble clic.
- **LOCAL-050 [M]: VIP por logros ("popularidad").** Idea de la usuaria (2026-09-29), implementada en `gxb2/vip.py` (2026-09-30). En local el VIP no viene de recargas: el VIP EXP se **deriva** del guardado (no se acumula aparte, así que no hay doble cobro y las partidas existentes lo reciben retroactivamente):
  - campaña: 12 por fase alcanzada (`max_stage`); nivel de jugador: 6 por nivel sobre 1; tareas diarias 10 y trofeos 25 (contador `missions.totals.popularity`); días jugados: 5; Laboratorio del gremio: 8 por nivel de tecnología.
  - Los umbrales y ventajas son la tabla `vip` original (`data/vip.json`, `tools/extract_vip.py`), sin reequilibrar. Con estos pesos, VIP 1 llega hacia la fase ~25, VIP 3 (Slots High Stakes, +30 % idle) hacia la fase ~110 y VIP 5 solo con campaña casi completa más tareas; VIP 6+ queda como meta muy larga. **Cifras a confirmar con la usuaria** (están juntas en `vip.WEIGHTS`).
  - Ventajas ya conectadas: bono `extra_output` en la recompensa idle (`campaign.pending`), Midas, Internship, Excursión y puertas de Slots/High Stakes (`state['vip']`/`vip_level` se rellenan al cargar). Pendientes: `partners_limit`, `quiz_buy_times`, `battle_speed`, `login_double`, regalos de VIP. La partida de desarrollo es VIP máximo.
  - La Recharge Task de Matching Pairs (LOCAL-055) mide el VIP EXP ganado durante el evento; las partidas con el contador provisional conservan su progreso (`two_love.vip_base`).
- **LOCAL-051 [m]: Beach Treasure Hunt.** Qué partes abre cada evento especial lo decidía el servidor; en local:
  - Water Ball abre las partes vecinas;
  - Hermit Crab recorre su fila;
  - Water Valve abre 4 partes al azar.
  El evento está siempre disponible, empieza con 10 palas y no se vende la Midsummer Invitation de pago.
- **LOCAL-052 [m]: Outfit Showcase.**
  - Un Slot puntúa el atributo de su fila (Courage / Charisma / Knowledge) de la pieza colocada.
  - Cada pieza se expone una sola vez por Booth.
  - Los Tags diarios se reclaman con Claim en la entrada; se acumulan hasta 7 días.
  - Los primeros Slots de cada fila, que no tienen condición, vienen abiertos.
  - La condición "Security Level" (Friend Team Boss, cooperativo) usa las fases de campaña ÷10.
  - No se vende la tienda de buffs (shop1).
- **LOCAL-053 [m]: Wish Capsule.** Las probabilidades del servidor no están en el cliente; se usan los `misc wish_gacha_*`:
  - la Wish Girl empieza con peso 100 de 1.000.000 y suma 100 cada 100 tiradas (×2 a ×5 de la ventana de ayuda);
  - desde la tirada 400 suma 220 más por tirada, y la 500 la garantiza;
  - conseguirla (por el deseo o del pool normal) reinicia el progreso; cambiar de chica no lo toca.
  El evento está siempre disponible y sus tiradas no cuentan para tareas diarias (como en el original).
- **LOCAL-054 [m]: Magic Card.** El servidor decidía qué da cada carta. En local:
  - al pulsar Start se sortea en qué giro sale la Ultimate Reward con los 25 pesos de `misc activity_ice_secret_weight` (pico en el giro 13); el resto de giros da una recompensa normal restante al azar;
  - Magician's Assistant usa contadores locales; no se muestran las misiones de sistemas inexistentes offline (Furniture, gemas gastadas, Elemental Orbs, Rudders); las de Space Radars cuentan los de Lost Space Zone;
  - "a battle in Magician's Assistant" (el jefe Backstage Prep, que no existe offline) cuenta cartas giradas;
  - el evento está siempre abierto, empieza con 150 Magic Wands y no se vende el Magic Gift Box de pago.
- **LOCAL-055 [m]: Matching Pairs.** Las Arrows of Love venían de la VIP EXP (recargas). Ahora salen del VIP por logros (LOCAL-050):
  - la Recharge Task cuenta el VIP EXP ganado durante el evento;
  - cada día que se abre el juego da 1 Arrow of Love;
  - el evento está siempre disponible y, al revelar las 16 cartas, se puede repartir de nuevo (vuelve el intento gratis).
- **LOCAL-056 [m]: Lost Space Zone.** El servidor generaba los tableros. En local:
  - una zona tiene las 55 cajas del grupo 1 y los eventos de `activity_lost_space_event`;
  - el portal sale en la exploración n.º `export_step` (23-33) y la Supply Coordinate en la n.º `treasure_step`, en las zonas `if_treasure`;
  - el contenido de un bloque se decide al explorarlo (el Hologram reserva una caja de valor, `show_icon`);
  - el Supply Stash tiene las 57 cajas del grupo 3 y su portal es el último bloque;
  - los 6 láseres son elegibles;
  - empieza con 30 radares y da 10 al día; el límite de compra (40) es diario; no se venden los Spaceship Supplies.
- **LOCAL-057 [M]: Reloj de juego monótono (2026-09-30).** Los reinicios diarios/semanales comparaban `día != día guardado`; con el reloj del sistema retrocediendo y avanzando se reiniciaban dos veces (tareas, límites, días jugados = fuente VIP `login`) y el check-in sumaba días pasados. Ahora `Engine.now()` devuelve el máximo instante visto, guardado en la tabla `clock` de la partida (sobrevive a reinicios); si el reloj del sistema va por detrás el juego espera (`clock_behind` en el snapshot). La partida de desarrollo sigue el reloj real para poder viajar en el tiempo en QA. `events.touch` y `missions.saved` además solo aceptan días posteriores. Contrapartida: un reloj adelantado por error avanza el juego hasta que el tiempo real lo alcance (se corrige borrando la fila de `clock` en una copia de la partida).
- **LOCAL-058 [M]: Día y semana según la hora de la máquina del jugador (2026-09-30, decidido con la usuaria).** El proyecto se jugará offline en todo el mundo, así que no hay "hora del servidor": todos los reinicios diarios acaban a la medianoche local y las semanas van de lunes 00:00 local a lunes (semanas ISO). Unificado en `gxb2/clock.py` (`day`, `week`, `week_end`, `week_index`, `week_start`); pasan a usarlo Midas, Internship, House Exam, Sanctuary (jefe alterno y reinicio), Quiz/Libro, Magic Card, puntos semanales de eventos, misiones, Excursión, arena, tiendas y check-in. Antes había mezcla de día local y UTC (en JST, UTC cambiaba a las 09:00). Las temporadas con inicio absoluto de las tablas (House Exam, Old Campus, Soul Land) no cambian. Al cambiar de zona horaria hacia el oeste el día puede repetirse una vez; el reloj monótono (LOCAL-057) impide que el tiempo retroceda. Los textos de la UI dicen "medianoche local".
- **LOCAL-059 [M]: Motor genérico de eventos (canje + misiones), 2026-09-30.** `gxb2/activity_kit.py` + `tools/extract_activity_kit.py` + `web/act-kit.js/.css` sirven 28 eventos del catálogo (Super/Skin/Antique Exchange, Kid's Store, Firework, Secret of Time, Celebration Party, Palace Vaults, Falling Stars, Trick or Treat, Jungle, Luvly's Journey, Goldfish, Fairytale, Lovely Date, Lucky Dips, Bizarre Adventures, To The Beach!, Game Console, Blind Box, Chime, Coffee Lab, Dream Castle, Dimensional Manor, Easter Egg Factory…). **Original:** filas de las tablas `activity_*_shop/_exchange` (coste, premio, límite por fila; 0 = ilimitado) y de las tablas de misiones (cantidad, premio, veces `limit`, textos). **Local:** (1) el emparejamiento evento↔tabla se dedujo de `xyd.ActivityID` y los títulos; no listados los que no se pudieron emparejar con seguridad (`unpaired` en el JSON); (2) el progreso de una misión es el aumento de nuestros contadores (`missions.totals`) desde que se abre el evento por primera vez, y el contador se deduce del texto (`COUNTERS`); las misiones de compra con dinero real, gastar gemas, una chica concreta, amigos, etc. salen como "No disponible en la versión local" y no se pueden reclamar; (3) la moneda del evento salía de su minijuego: mientras no exista, si las misiones del evento no la pagan se da un **suministro diario** de 1/10 del precio mediano (`SUPPLY_DAYS`) por día local; (4) diseño genérico, no el prefab de cada evento. Los eventos siguen sin calendario (siempre abiertos). Pendientes: Girls Exchange / 10-Star Exchange (selector de chica), eventos de las pestañas de pago, y los minijuegos que generan cada moneda.
- **LOCAL-060 [M]: Gremio v1 con miembros simulados (2026-09-30).** `gxb2/guild.py`, `tools/extract_guild.py`, `web/guild.js/.css`; entrada por el botón Gremio y por los edificios del territorio (Office, Cafeteria, Gym; Lab ya existía). **Original:** desbloqueo en la fase 32 (función 22), creación 500 gemas y nombre de 3 a 12 caracteres, cambio de nombre 1000 gemas, niveles/capacidad de `guild_exp`, firma diaria (50 Guild Coins + 30 EXP), Cafeteria desde el nivel 8 del gremio con Molino (`guild_mill`: donar oro sube el factor y los pedidos) y pedidos (`guild_order`: duración, premios × factor, mejora con gemas), Gym = Guild Boss (cadena 1-60, coste 0/0/40/80 gemas por combate y 16 h de enfriamiento, premios de combate y de victoria, EXP de gremio con tope diario). **Local:** el gremio es solo tuyo más miembros NPC que se unen uno al día hasta la capacidad, con nombre/nivel/poder deterministas por semilla, y que firman ~70 % de los días (+30 EXP cada uno); el combate contra el jefe usa tu formación y el motor original (un jefe = un combate tuyo, sin daño compartido); los pedidos nuevos se piden cada 12 h. **No reconstruido:** solicitudes/reclutamiento/chat/expulsar, jefe final (id 61+), Guild War/Playground, Merchant (`guild_trader` son packs de pago), ranking, registro de donantes.
- **LOCAL-061 [M]: Motor de sorteos con ficha (2026-09-30).** `gxb2/activity_draw.py`, `tools/extract_activity_draw.py`, pestaña "Juego" en `web/act-kit.js`: Goldfish Scooper 317, Seaside Fishing 245, Spin the Wheel 286, Easter Egg Factory 290, Childhood Memories 298, Lucky Dips 260, Jungle Exploration 234, Ring Toss 283. **Original:** ficha y coste (`misc activity_*_cost`), premios (tabla ponderada o dropboxes), stock por ronda de Spin the Wheel (`num`), pez dorado (`activity_fish_extra_pro`/10000), premios grandes 1 % y barra de garantía de Lucky Dips (100, +2 por sorteo), premios por hitos (`complete`/`point`), packs de fichas por gemas con su límite. **Local:** el contador de hitos suma 1 por sorteo (el servidor decidía cómo se contaba), cada hito se reclama una vez, se dan 10 sorteos de la primera ficha por día local, Easter Egg Factory usa sus dos fichas con sus dos dropboxes, Ring Toss elige entre 4 dropboxes por peso, Jungle solo reconstruye el área 1. **Sin hacer aún:** Jackpot/Lucky Draw (64/258, 3 rodillos), Blind Box, Pirate, Chime, Firework, Jigsaw, Cake/Coffee, Music Festival y los minijuegos con mecánica propia (pescar con reflejos, lanzar aros, etc.: aquí es un sorteo directo).
- **LOCAL-062 [M]: Jackpot of Fortune (evento 64), 2026-09-30.** `gxb2/jackpot.py`, `tools/extract_jackpot.py`, `web/jackpot.js/.css`, maquetada sobre la captura fb/3 y los sprites originales (`jackpot_machine`, cabezas, botones). **Original:** Energía (item 57): 15 al empezar, +1 cada 4 h hasta 20; girar cuesta apuesta × 5 (apuestas 1/2/5/10) y paga la combinación × apuesta (27 combinaciones con su peso; tres iguales 8/7/6, dos iguales 5/4/3, todas distintas nada) en Basic (moneda 58) o Super (moneda 305, se abre con 40 tiradas); la energía gastada en Super llena los 15 premios de progreso; conversión 58→305. La tienda de canje (`activity_jackpot_exchange`, 700 gemas por 35 de energía + ficha) la sirve `activity_kit`. **Local:** el servidor elegía la combinación (aquí un sorteo ponderado); el contador de tiradas para desbloquear Super es propio (1 por tirada); la Privilege Card de pago no se vende. Lucky Draw (258) es otro juego (`ActivityJackpotLottery`) y sigue sin hacer.
- **LOCAL-061 (ampliación) — Wish Upon a Chime (308):** las dos grullas (Jade 385 / Gilded 386) sacan de las dos listas del dropbox `activity_chime_dropbox` (tipo 1 / tipo 2) y cada 20 Gilded Cranes gastadas garantizan un Shard of Reflections (`ACTIVITY_CHIME_HELP`). Los Chimes (equipo con niveles, `chime.lua`, `chime_lv_cost`) **no** están reconstruidos: caen al bolsillo como objetos; por eso las misiones "Fantasy Dust/Talisman", "Charge your Chimes" y "Enchant or Ascend" siguen sin rastrear. Las misiones "Consume N Jade/Gilded Cranes" sí se cuentan (`spent:` en `activity_draw`).
- **LOCAL-063 [M]: Blind Box Frenzy (evento 338), 2026-09-30.** `gxb2/blind_box.py`, `tools/extract_blind_box.py`, `web/blind-box.js/.css`; reglas de `ACTIVITY_BLIND_BOX_HELP`, `ActivityBlindBox.lua` y `ActivityBlindBoxData.lua`, con la descripción y el cartel aportados por la usuaria (`docs/references/2026-09-30-user/01`). **Original:** 2 rondas; cada ronda tiene un Premio Gordo fijo y 4 niveles de recompensas a elegir (3, 3, 1 y 1; total 8); cada recompensa tiene `num` copias y `weight`; un cupón (item 438) abre 1 caja (×1) o 5 (×5) y cada caja sale entre las copias que quedan ponderando por peso × copias; la selección se puede cambiar hasta conseguir cualquier recompensa (ventana de confirmación); el Premio Gordo llega como mucho en la apertura 30 (`guarantee_time` 29); tras el gordo de la ronda 1 se puede pasar a la ronda 2 (lo que quedaba de la 1 se pierde); en la 2 se sigue abriendo tras el gordo. Rejilla 3×3 con las tablas de colores/posición del cliente. **Local:** los cupones venían del Blind Box Bonus y del Recharge Gift (de pago): aquí los pagan las misiones del evento (VIP EXP, motor genérico) y se dan `DAILY_COUPONS` = 3 por día local; el sorteo del servidor es aquí un sorteo ponderado.
- **LOCAL-064 [M]: Deep Sea Treasures (329) y Palace Vaults (330), 2026-09-30.** `gxb2/pirate.py`, `tools/extract_pirate.py`, `web/pirate.js/.css`, según las capturas de la usuaria (`docs/references/2026-09-30-user/05-07`). **Original:** cinco tierras (Sea Lord's Palace, The Beach, Coastal Waters, Open Sea, Abyssal Palace) con su dropbox (`activity_pirate_5_drop_awards`); un Raid cuesta 1 Voyager Compass (410), siempre paga 20 Pirate Coins (411) y saca una vez del dropbox de la tierra (los % de la ventana coinciden con las capturas); un cofre (5 tipos, 30/25/20/15/10 %; cada uno paga 30-120 monedas) cae con un 20 % y está garantizado tras 9 raids sin cofre (el 10.º); hasta 100 raids por vez; los cofres llenan la Collection Progress y cada uno que tengas paga su recompensa una vez (`activity_pirate_mission`). En Palace Vaults las bóvedas grandes se abren al gastar Pirate Coins (`activity_pirate_shop_awards.unlock`: 2500/5000/7500/12500/20000), aplicado en `activity_kit` (`UNLOCK_BY_SPENT`). **Local:** la historia de las islas (`activity_pirate_plot`, 348 líneas de diálogo) no está reconstruida y las cinco tierras están abiertas; las brújulas venían del Server Pack de pago: se reclama una vez el paquete gratis del cliente (`giftbag_free_awards`) y llegan 15 brújulas por día local. Los cofres se conservan como objetos de colección (no se abren).
- **LOCAL-065 [m]: Halloween Pumpkin Patch (150), 2026-09-30.** El servidor elegía qué calabaza abre cada corte; en local es una de las enteras al azar. Las dagas venían de Enroll Exam, el correo diario y packs; en local el evento empieza con 10, da 5 al día y el límite de compra (30) es diario. Siempre disponible.
- **LOCAL-066 [m]: Transfer / Altar, 2026-09-30.** `DECOMPOSE_PARTNERS` en `gxb2/engine.py`, con vista previa en `/api/altar/preview`. Cada chica devuelve:
  - lo que da el Altar (`Partner:getDecompose`);
  - el 70 % de las Grade Stones de sus grados (`grade_exp`);
  - el Awaken por debajo de 10★, al 70 %;
  - el 65 % de la EXP de nivel (`exp_partner.all_exp`).

  **Diferencias con el original:**
  - el Antique equipado vuelve entero a la mochila (no se convierte en materiales);
  - no se devuelve el origen de estrellas (Star Origin);
  - el límite diario de cinco chicas de 6★+ cuenta por día local.

  Las chicas bloqueadas, las Cosmos (grupo 7) y las que están en la formación se pueden quitar de ella; las bloqueadas y las Cosmos no se retiran.

- **LOCAL-067 [m]: Menú, Collection, Manga y orden de Girls, 2026-09-30.**
  - **Collection:** el servidor guardaba qué ids de `collection.lua` tenías. En local un id cuenta como conseguido si tienes su `item_id`:
    - Skins cuentan por `skins_info.collected`;
    - Furniture cuenta por el inventario del Dorm;
    - Antiques cuentan por `souls_info`.

    Los Collect Points son la suma de `123#n` de lo conseguido. La tienda de la colección no está reconstruida.
  - **Manga:** las páginas eran web. Se usan las de la carpeta de la usuaria. La pestaña Birthday es un añadido local para sus 62 mangas de cumpleaños.
  - **Menú:** Notice, Social, GM y Redeem necesitaban el servidor y solo muestran un aviso. Help abre el Game Assistant, Tips abre Mejoras e Image abre Wallpaper.
  - **Orden de Girls:** Power, ATK, Hp, Armor y Spd se calculan con base + crecimiento × (nivel − 1) de `girl-details`, sin equipo ni buffs. Like usa el afecto si existe.

- **LOCAL-068 [m]: Collection Store y Collect Points, 2026-09-30.**
  - El servidor guardaba qué ids de `collection.lua` tenías. En local cuentan si tienes el objeto:
    - skins: por `skins.collected`;
    - Antiques: en la bolsa o equipados;
    - atuendos: por las piezas de Outfit;
    - el resto: por la bolsa.
  - Los marcos y avatares comprados van a la bolsa. El perfil ya permitía elegir cualquiera del catálogo.
  - Las semanas siguen el reloj local (LOCAL-057).
  - **VIP:** 1 VIP EXP por Collect Point, añadido como fuente de LOCAL-050 a petición de la usuaria. El peso está en `vip.WEIGHTS['collection']`.
- **LOCAL-069 [M]: Arena 3v3 con rivales simulados, 2026-09-30.**
  - Los rivales son la escalera de Junior Varsity (LOCAL-027) con una puntuación 3v3 aparte. Cada rival lleva tres alineaciones de `arena_robot` (su robot y los 5 y 10 puestos siguientes), escaladas como los NPC.
  - La puntuación usa la regla Elo de Junior Varsity; un 2-0 cuenta ×1,25.
  - Temporadas de 15 días desde la primera visita.
  - No hay combates gratis: cada combate cuesta 3 tickets.
  - La defensa (tus equipos contra otros jugadores) no existe sin conexión.

- **LOCAL-070 [M]: Jigsaw y Puppet Parade, 2026-09-30.** Datos de cuatro tablas Lua (`activity_jigsaw_pic/buy/award`, `activity_puppet_award`), costes e item de `misc`. Jigsaw intercambia dos piezas cualesquiera, sin hueco: confirmado por `ActivityJigsaw.lua:setSelect/checkSwap` y `ActivityJigsawData.lua`. Energía inicial 1, coste 1 por intercambio, límite 50 compras progresivas. Puppet usa la cantidad actual de item 217, como `ActivityPuppet.lua:initMission`, sin consumir al cobrar. Local: archivo permanente sin fechas originales, suministro de 3 energías/40 marionetas por día local, sin volver a cobrar al retrasar el reloj. Reclamación explícita una vez y premio directo a la bolsa, sustituyendo el correo del servidor. Compras limitadas por vida del archivo, sin inventar un reset diario. Se conservan tableros y cobros al reiniciar. Faltan calendario, fuentes originales de moneda, maquetación/animación completa y rotación por temporada.

- **LOCAL-071 [M]: Firework Project 196, 2026-09-30.** Tablas `activity_bomb_make` y `activity_bomb_award`, misc `activity_bomb_make_cost=225#25`, `activity_bomb_make_lv=100`. `ActivityBombGachaWindow.lua` incrementa progreso por coste total, incluso si sale la devolución de polvo. Se usan los cuatro pesos originales; ×10 hace diez resultados independientes locales porque el servidor elegía la combinación. Tienda: desbloqueos por gasto total y límites originales, sin reset inventado. Archivo permanente, 250 polvos diarios locales en lugar de los drops de servidor; el reloj atrasado no concede otro suministro. Falta calendario, fuentes originales de polvo y animación Spine. Este evento es ActivityBomb (196); no usar reglas del posterior ActivityFirework (274).


- **LOCAL-072 [M]: Graduate para chicas nativas de 1–3★, 2026-09-30.** Ampliación solicitada por la usuaria: 50 chicas jugables, 390 recetas, hasta 10★ conservando table_id, nivel, formación y equipo de la base. No se aplica a monstruos. Cada paso consume una copia del mismo nombre con sus estrellas iniciales; de 3→4 y 4→5 también una chica de la misma facción con las estrellas previas; de 5→6 hasta 9→10 consume dos. Oro: 10.000 × (estrella destino − 1)². Caps de nivel 2–10★: 60/80/100/140/180/200/220/240/250. Recetas nativas existentes se mantienen.
  - Combate: se conservan habilidades nativas, sin inventar habilidades de despertar, EX o potenciales. El adaptador local multiplica HP/ATK/Armor por 1 + 0,25 × ascensos, redondeando hacia abajo, y recalcula Power. Velocidad y demás atributos no reciben este multiplicador. La serialización pasa awake=0 al código Lua original, que no tiene tablas de despertar para estas chicas; local_growth solo se aplica en el adaptador mantenido. El save sigue guardando los ascensos en awake.
  - UI: filtros 1→2 a 9→10, revisión manual de base y materiales, confirmación con nombres/niveles, retrato y receta en flujo, márgenes para la navegación, estados vacíos limpios. Materiales específicos exigen sus estrellas nativas para proteger copias ascendidas; bloqueadas e intercambio pendiente siguen excluidos. A 10★ muestra ruta terminada, sin controles de Limit-Break que no existen para ellas.
  - Balance propio local, pendiente de ajuste jugando; no se presenta como receta original ni se prometen 15★ para estas chicas.
- **LOCAL-073 [m]: Citas, Oath y Main Center, 2026-09-30.**
  - Date (DatesStoryWindow): el servidor llevaba las tareas de `partner_achievement`. En local se leen del guardado: nivel, intimidad, fondo de pantalla y forjas. Las tareas de «consumir objetos» se cobran al completar el paso.
  - Oath: el Marriage Certificate guarda `wedding_date`. Al casarse se entrega una sola vez la skin de boda de la chica (`partner_picture.is_wedding`), que el certificado muestra. El cliente no dice cómo se obtenía; la usuaria confirmó que se consigue al casarse.
  - Main Center (`travel_train_set`): chicas asignadas a los huecos de cada disciplina, que se abren según `travel_train_slot_limit`. Son solo visuales: el cliente no expone qué bonificación daban.
  - Explore: el detalle de cofres (tipsBtn) muestra `award1` al 100 % y las probabilidades de `dropbox_id1` por peso.
- **LOCAL-074 [m]: Discuss → Partner Data Station, 2026-09-30.**
  - Strategy y Lineup son datos del cliente: `direct`, `direct_array`, `direct_label` y sus textos.
  - Rank (el puesto de uso en Patrol, Junior Varsity, Tests y Guild Boss) lo calculaba el servidor con todos los jugadores. Se muestra «No Record».
  - Junior Varsity de Lineup y Field Test también dependían de otros jugadores o del servidor: no se incluyen.
  - Review (me gusta, etiquetas propias hasta 3 y comentarios de 12 a 400 caracteres) era un tablón en línea. Aquí son notas del jugador guardadas en `state.station[comment_id]`.
  - Solo se puede comentar si tienes a la chica, como en el original (PARTNER_COMMENT_LOCKED).
- **LOCAL-075 [m]: Producción del dormitorio (Comfort), 2026-09-30.**
  - HouseComfortWindow calcula en el cliente lo producido: `house_award` según el comfort, cada 5 s (`HANG_AWARD_TIME`), con un tope de 12 h (`hang_up_time_max`) desde el último Collect.
  - El servidor guardaba hang_time, hang_update_time y un registro de lo acumulado. Aquí son `house_dress.hang.at`, `upd` y `rec`. Al guardar la habitación o comprar muebles, lo acumulado con el comfort anterior se guarda antes del cambio.
  - Se omite el «−1 tick» que muestra el cliente.
- **LOCAL-076 [m]: Mejoras de la Showcase Store, 2026-09-30.**
  - `show_window_shop1`: cada compra añade una carga de 3 combates de su habilidad (700001…), hasta 4 activas y 8 compras por semana.
  - El servidor las aplicaba. Aquí cada carga activa entra en el combate como god skill y gasta un combate: Tests / Old Campus (15|39), Patrol (19) y House Exams (35), mediante `engine.show_mode` y `dress_show.battle_skills`.
  - Security Squad (32) es cooperativo en línea: sus mejoras se ven, pero no se venden.
- **LOCAL-077 [M]: Fantasy Book, 2026-09-30.** Datos: `battlepass_award`, `battlepass_mission`, `shop_battlepass`, `bp_lottery_*` y los textos BP_*.
  - La temporada la llevaba el servidor. Aquí dura 42 días desde la primera visita y luego empieza otra: se reinician las páginas, los premios reclamados, los límites de la tienda y las tareas Extra; las monedas se conservan.
  - El progreso de las tareas sale de `missions.record`: el contador de hoy para las diarias, y lo sumado desde el inicio de la semana o de la temporada para las demás.
  - Contadores nuevos: `arena_win`, `tavern5`, `tavern7`, `sanctuary` y `dorm_collect`.
  - Sin equivalente sin conexión, se quedan a 0: Hearts, Friend Boss, Seals y mejoras de antigüedades.
  - El Luxury Book y el Collector's Book eran compras con dinero real y no se venden (igual que la fila de pago del Passport). Se pueden comprar niveles con gemas (`cost_diamonds`, y `cost_dct_diamonds` en las 2 últimas semanas).
  - El sprite `icon_117` del cliente es un engranaje; las capturas muestran una hoja de otra versión.

## LOCAL-078 — Growth Diary offline

Premios/textos/capítulos son originales; progreso de servidor sustituido por métricas de save y contadores de acciones locales. Progreso persistente al guardar, sin inventar historial de acciones antiguas. Misiones con estrella: baseline en desbloqueo, por GROWTH_DIARY_TEXT09. Type15 reutilizado: resolver por registro 70/157. Requerir cuatro recompensas de misión antes de premio de capítulo, según GrowthDiary:checkCanAward. 39 objetivos no conectados visibles/bloqueados. UI adaptada con sprites originales, sin certificar prefab/animaciones. API HTTP; protocolo TCP del diario sigue pendiente. Ver GROWTH_DIARY.md.

## LOCAL-079 — Newbie Camp y ampliación Diary (2026-10-01)

Newbie Camp conserva 33 filas, premios y gates originales; amistad usa contactos locales. Chat/Elite League no se simulan. Racha por calendario local con actividad persistida, sin historia inventada. Presentación local compartida con Diary. Diary incorpora métricas de sistemas existentes; daño Guild Boss del informe local, antigüedades según star de EquipTable, retos por cadena next_id y examen por school_sort. Se conservan sólo logros demostrables y contadores nuevos desde integración. Seis objetivos Diary sin seguimiento. Véanse NEWBIE_CAMP.md y GROWTH_DIARY.md para límites/validación.

## LOCAL-080 — Friend Boss/Training/Ulticore/Practical Work (2026-10-01)

Friend Boss usa variante actual friend_boss_new, días locales y poder observado al abrir/consultar/luchar, sin apoyos/rankings ficticios. Training: días locales, distribución uniforme del multiplicador 0.8–1.2, recompensa de curso fijada al empezar, idle desde primera apertura. Ulticore se devuelve a 0 porque restore incluye apertura; monedas no devueltas. Practical Work: temporada local30d desde creación, daño de chicas y mail de premios; calendario/entrega inicial/protocolo originales pendientes. No traducir antiguas misiones Diary etapa10 a tablas actuales con ocho etapas. Detalles/evidencia y pruebas en SISTEMAS_PENDIENTES_RECONSTRUIDOS.md.
- **LOCAL-077 (ampliación): dos temporadas temáticas del Book, 2026-10-01.** El cliente trae dos pieles: «Restart the Engine!» (BattlePassSteam: Gearwheel 117, Screws 119, Mecha Core 120) y «Fantasy Book» (BattlePassSteamNew: Pages 223, Floral Stamp 221, Crystal Leaf 222).
  - Alternan por temporada: las impares son el Book y las pares el Engine.
  - Las tablas nombran las monedas del Book; en una temporada Engine se entregan y cobran sus equivalentes (`fantasy_book.tr`).
- **LOCAL-081 [m]: Hearts de amigos, 2026-10-01.** `gxb2/hearts.py`. Reglas originales: un Heart (objeto 11) enviado y uno reclamado por amigo al día, 30 reclamados al día como máximo y 1000 en posesión.
  - Sin servidor de amigos, los amigos son los contactos locales, y cada contacto tiene un Heart esperando cada día (en el original hacía falta que el amigo lo enviara).
  - «Recommended» ofrece a los rivales de Junior Varsity como contactos.
  - Enviar cuenta para la Daily Task y para la tarea del Book.
- **LOCAL-082 [M]: Calendario del juego, 2026-10-01.** `gxb2/game_calendar.py`. El servidor abría y cerraba cada evento limitado. Aquí el calendario es el local del jugador: semanas de lunes a domingo y meses desde el día 1.
  - Los eventos de canje y misiones del kit son semanales: 6 abiertos, cada uno dura 2 semanas y la mitad cambia cada lunes.
  - Los eventos con minijuego propio son mensuales: 4 abiertos, cada uno dura 2 meses y la mitad cambia el día 1.
  - El orden es un barajado fijo, así que el calendario es el mismo en cualquier máquina y se puede listar por adelantado.
  - Daily Login y el evento de 7 días siguen siempre abiertos. Un evento que se cierra conserva su progreso.
  - El calendario solo decide qué ofrece la ventana de Eventos; no bloquea las acciones en el backend.
- **LOCAL-083 [m]: Vida en el dormitorio, 2026-10-01.** HouseHero usa los mismos modelos Spine que el combate, con las animaciones `houseidle`, `walk`, `sit`, `lie` y `hurt`.
  - En el original el jugador arrastraba a la chica al mueble. Aquí las chicas deambulan solas (20 % se quedan, 25 % van a un mueble libre con `interact` 1 sit / 2 lie, el resto camina a una casilla libre) y reaccionan al toque.
  - La posición sentada usa `point_xy`; la tumbada se centra en el mueble, porque los offsets por modelo de `house_partner` no están extraídos.
- **LOCAL-084 [M]: Audio, efectos de combate y recursos bajo demanda, 2026-10-01.**
  - Audio (`tools/extract_audio.py`): todos los efectos y la música del cliente en MP3, con `sounds.json` (id de sonido → archivo y volumen, de `sound1/2`) y `skills.json` (habilidad → sonido).
  - Los sonidos de acción se asignan en una tabla central (`ACTION_SOUNDS` en `web/app.js`) por URL y acción, porque el cliente los disparaba ventana por ventana. La asignación es una aproximación propia con los sonidos originales.
  - Los sonidos de botón siguen `xyd.SoundID`: BUTTON 2006, BACKWARD 2007, CLOSED 2008 y TAB 2009, deducidos del nombre de clase del botón.
  - Jukebox y escenas animadas de portada son añadidos locales; se guardan por navegador (`gxb2-bgm`, `gxb2-scene`).
  - Efectos de combate (`tools/extract_battle_fx.py`): se usa el grupo base de `fx_hurt1-3` y `fx1`. No se reproducen las unidades invocadas (tipo 3) ni el vuelo de los proyectiles. `position` 1 se interpreta como «a los pies»; el resto, a media altura.
  - Rutas bajo demanda en `server.py`: `/assets/spine/<nombre>` (animaciones Misc), `/assets/sprite/<nombre>.png` y `/assets/bg/<nombre>.webp`. Leen de `~/Downloads/Decompiled` y guardan una copia en `web/assets/` la primera vez; sin esa carpeta, solo sirven lo ya guardado.
  - Catálogo de objetos completo (`tools/extract_items_all.py`): los objetos que no van en la Bolsa entran con `category` 0.
- **LOCAL-085 [M]: Bots (jugadores simulados), 2026-10-01.** `gxb2/bots.py`, `web/bots.js`. Petición de la usuaria: poner bots donde hacían falta otros jugadores.
  - Reparto: los 50 rivales persistentes de Junior Varsity. Todo es determinista (hash de bot, tema y día) y no se guarda nada: los bots nunca modifican la partida.
  - Rankings (`bots.rank`): cada bot avanza un poco cada día hasta su propio techo; el jugador entra con su valor real. Conectados: Land of Souls, Tsuruga (Message Board › Ranking) y Cafeteria (Rank). También hay uno de Tests, sin pantalla todavía.
  - Los rankings son solo informativos: los premios de temporada de Tsuruga siguen saliendo de la puntuación propia (LOCAL-037).
  - Student Files › Review: comentarios y «me gusta» de bots, con frases genéricas en inglés escritas para el proyecto (no son textos del juego).
  - Chat: los canales World, English, Servers y Recruit muestran una ventana rodante de mensajes de bots. Lo que escribe el jugador sigue siendo un borrador local; los bots no responden.
