# Pendientes de implementar — GxB2 Reborn (30/09/2026)

> **Corrección de estado, tanda049:** la [sección 40 del checklist](GXB2_MASTER_CHECKLIST.md#40-actualización-de-cobertura--2026-09-30) prevalece sobre esta hoja de ruta cuando se contradicen. Ya existe copia SQLite en caliente y restauración a ruta nueva (`tools/save_archive.py`), así como Gremio v1, Dorm/editor, Manga y Tree of Chimes; **siguen pendientes** migraciones, import original, Guild War/social, calendario de eventos y muchos modos exclusivos. Las cifras «10 de 322» y la tabla inferior se calcularon antes de las tandas 038–048, por lo que no son una cuenta actual de cobertura.

> Hoja de ruta hecha por Claude a partir de `data/events.json` (322 actividades del catálogo), `INVENTARIO_CLIENTE.md` (**desactualizado**: aún marca como pendientes Quick Formation, Outfit Showcase, Game Assistant…), el workboard y `web/events.js` (`WORKING`). Cifras aproximadas; no acreditan fidelidad de lo ya hecho. Estado fino en [ESTADO_PROYECTO](ESTADO_PROYECTO.md).

## 1. Eventos — 10 de 322 con juego propio + 28 con motor genérico (canje/misiones) + 8 sorteos (actualizado 30/09)
> Tras la tanda 037: motor de canje/misiones (`activity_kit`, 28 eventos), sorteos con ficha (`activity_draw`, 8 eventos) y Gremio v1 (Office/Cafeteria/Gym). Lo que sigue en las tablas de abajo es lo que aún falta.

Operativos: Daily Login (1), 7-Day (116), Capsule Points (13), Enroll Exam (16), Slot Points (20), Beach Treasure Hunt / Midsummer / Ocean Coin (309-312), Wish Capsule (140), Magic Card (134), Matching Pairs (331), Lost Space (292).

| Familia | ≈ nº | Ejemplos (id) | Qué hace falta |
|---|---|---|---|
| **De pago (packs, pases, fondos, recarga)** | 95 | Monthly Pass 6, First Recharge 164, Level Pack 8, Value Pack 12… | **Decisión de diseño**: omitir, o convertir en recompensas de juego (LOCAL-050 ya da VIP por logros). No implementar como compra. |
| **Canje / tiendas de evento** | ~12 | Girls Exchange 26, 10-Star Exchange 48, Super Exchange 183, Skin Exchange 232, Reward Exchange 163, Antique Limited Exchange 244 | Un motor genérico `activity_shop` (límites, monedas) cubre casi todo. **Mejor relación esfuerzo/valor.** |
| **Firmas / calendarios** | ~6 | Moon Festival 47, New Year 172, Advent Calendar 257, 6th Anniv. Sign In 307 | Reutilizar `events.py` (check-in) con tablas propias. Fácil. |
| **Misiones de evento / pases** | ~12 | Exclusive Task 23, Practical Work 32/246, Intern Event 21, League Ace 22, Graduate & Awake 25, Limited Missions 193, Secret Sanctuary 109, Sanctuary Pass 289, Soul Pass 337 | Los contadores de `missions` ya existen; falta el contenedor y sus premios. |
| **Modos con combate/exploración** | ~8 | Old Campus Exploration 155, Explore the Campus 126, Ancient City Battle 198, Dimensional Manor/Challenge 300/301, Entrance Exam 120/314, Story Challenge 240, Fairytale Land 141, Servant Challenge 186 | Reutilizan motores ya hechos (Old Campus, Hero Challenge, Servants). |
| **Minijuegos únicos** | ~55 | Jigsaw 37, Winning Heart 52/84, Lucky Pair 125, Ring Toss 283, Goldfish Scooper 317, Cake Decoration 306, Blind Box 338/340, Spin the Wheel 286, Potion Brewing 249, Bottles Adrift 191, Easter Egg Factory 290, Fireworks 196/274, Jackpot/Lucky Draw/Dips 64/258/260/273, Seaside Fishing 245, Treasure Hut 323, Deep Sea 329, Bubble 344, Catch an Astral 346, Game Console Fixer 325, Bonnie's To-Do 326… | Uno por uno: tabla `activity_*` + prefab. Suelen ser variantes de "tablero + recurso" (ya hay 5 hechas como plantilla). |
| **Temporada (Halloween, Navidad, Verano, Aniversarios, San Valentín)** | ~35 | 86, 150, 248-250, 332-334; 171, 270-272, 348; 42, 61, 230-233; 131, 182, 127; 185, 313 | Muchas son re-skins de las familias anteriores: primero el motor, luego los datos. |
| **Novato** | 12 | 7-Day Mission 156, Program Study 204/218, Online Rewards 113, Guidance 114 | `beginner_quest`, `NewbieCamp`; ligado al tutorial. |
| **Requieren gremio/red** | ~5 | Guild Championship 328, Friend/Community | Esperan a las sustituciones NPC. |

**Infraestructura de eventos que falta:** calendario con inicio/fin y rotación automática (hoy todos los "WORKING" están siempre abiertos y la rotación de archivados es solo JS), estado persistente por evento, archivo/repetición de eventos viejos, correo de recompensas, cierre y limpieza. (Checklist §20.)

## 2. Sistemas que no existen o son parciales
| Área | Estado | Falta |
|---|---|---|
| **Gremio** | Solo Laboratorio | Crear/unirse, oficina y firma diaria, EXP/nivel, jefe, comedor/pedidos, gimnasio, parque, guerra, tienda, ranking → NPC (§14). |
| **PvP** | Solo Junior Varsity | Varsity 3v3, Elite/Ultimate League (ArenaAllServer*, FairArena, ArenaTeam, House Battle), temporadas y ranking simulados, NPC persistentes (§13). |
| **Social** | Contactos y correo básicos | Amigos y solicitudes, **Friend Boss**, Security Squad, chat, comentarios de chicas, Community; NPC amigos (§24). |
| **Dorm / My Room** | Solo Outfit de casa | Muebles, comodidad, colocar chicas, `house_*` (11 tablas) (§21). |
| **Servants** | Hecho lo básico | Ulticore/ex-level, Reborn, **PetTraining**, PetSlot, visor en repetición. |
| **Libro / Fantasy Book, Battle Pass** | Sin hacer (botón "Libro") | `battlepass_*` (5 tablas), misiones y tienda. |
| **Cómic/Manga, Growth Diary, Background, Elite Assembly, Data Station** | Sin hacer | Modelos completos del cliente con tablas sin leer. |
| **VIP** | Nivel/EXP y bono idle | `partners_limit`, `quiz_buy_times`, `battle_speed`, `login_double`; ventana VIP original y regalos (de pago → sustituir). |
| **Cosmos/Galaxy tardío, Tests > piso 1500** | Parcial | Pisos restantes; sistemas cósmicos conectados. |
| **Tiendas** | Shopping Street, Lucky | Skin Store, Collection Store, Event Stores, tiendas de liga/gremio. |
| **Combate** | Motor original ejecutado | Corpus de pruebas de habilidades/atributos, pools (GXB2-FIDELITY-001). |

## 3. Infraestructura y preservación (P0/P1 del ESTADO)
1. **GXB2-SAVE-001** copia SQLite y restauración a ruta nueva probadas; faltan migraciones, restauración desde la interfaz e import de progreso real (M12).
2. **Tiempo:** hecho reloj monótono (LOCAL-057) y día/semana locales (LOCAL-058); falta calendario de eventos, liquidación idle al cambiar de fase (IDLE-SETTLE-001), aviso en pantalla si el reloj va por detrás.
3. **Tutorial / flujo de novato**, ajustes (idioma, audio, FPS), localización (solo ES/EN parcial), inventario de audio y voces, tabla autoritativa de ítems/monedas.
4. **Import del save original** (M12) y **empaquetado portable para todo el mundo** (M14): instalador, sin rutas de `~/Downloads`, extractores documentados.
5. `INVENTARIO_CLIENTE.md`: regenerar con el mapa `LOCAL` de `build_client_inventory.py` actualizado.

## 4. Orden que recomiendo
1. **Motor genérico de canje** (`activity_shop`) → desbloquea ~12 eventos de una vez.
2. **Calendario de eventos** (inicio/fin, rotación, archivo) + decisión sobre los ~95 de pago.
3. **Misiones/pases de evento** y **firmas** (reutilizan contadores y check-in).
4. **Gremio NPC** (§14) y **Varsity/Elite NPC** (§13): son los sistemas grandes sin ninguna base.
5. Minijuegos por lotes de estacionalidad (Halloween → Navidad → Verano → Aniversarios).
6. SAVE-001 antes de tocar el import real; en paralelo, tutorial y empaquetado.
