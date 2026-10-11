# Rutas reconstruidas — actualización29/09/2026

- Campus → Enroll → **Exchange** ahora ejecuta propuesta, guardar y descartar; el estado se conserva al reabrir.
- Campus → **Slots** ahora abre máquina Normal/High Stakes operativa, refresh e historial; Evento Slot Points → Slot Machine enlaza esa misma máquina.
- Chicas → detalle → **Bloquear/Desbloquear** conecta LOCK_PARTNER y protege materiales.
- Lucky Store y otras tiendas/ventanas archivadas siguen pendientes. Abrir una ruta archivada no acredita su operación.

Estado/evidencia/límites en [ESTADO_PROYECTO](ESTADO_PROYECTO.md), [VALIDACION](VALIDACION.md) y [RESEARCH](validation/reconstruction-2026-09-28/RESEARCH.md). Las descripciones antiguas siguientes se conservan como referencia visual; los pendientes concretos de Exchange/Slots se sustituyen por este encabezado.

---

> **Corrección de estado — 28/09/2026:** este mapa conserva la navegación/historial original. Para alcance actual consultar [ESTADO_PROYECTO](ESTADO_PROYECTO.md), [LEEME](LEEME.md) y [checklist](GXB2_MASTER_CHECKLIST.md). Las entradas visuales de la tabla no constituyen pruebas de lógica/persistencia completa.
>
> **Avances posteriores:** Campus → Enroll tiene tiradas locales de fragmentos/Portfolios; Exchange sigue pendiente. Chica → Gear y Bolsa → Forge tienen operaciones de equipo/forja/tesoro/antigüedad. Perfil permite nombre/firma/avatar/marco. Eventos incluye login/7 días/puntos parciales; Slots sigue pendiente. Servant, Libro, Excursion y Cosmos tienen operaciones locales parciales; Amigos son contactos/borradores y Correo tiene adjuntos locales con correo de prueba solo DEV. Guild, ligas PvP, Date/Dorm, Memories y demás archivos visuales no pasan a completos por estos avances. Servant aún no afecta al combate. Ver evidencias y tareas en la matriz.

# Mapa de menús reconstruidos

Las rutas de navegación se trazaron en el cliente Lua de la copia local del juego (`~/Downloads/Decomp files/lua/app/windows/`). Los gráficos provienen de `unity/Assets/hotres/atlases` y `unity/Assets/hotres/textures`. Los archivos fuente no se modificaron; `tools/extract_menu_assets.py` genera las copias usadas por la web.

| Entrada | Ventana original | Pantallas locales | Estado |
|---|---|---|---|
| Inicio → Campus | `MainWindow.lua` → `SchoolChooseWindow.lua` | Study, Life, Graduate | Graduate funciona con la partida local; el resto tiene navegación visual. |
| Study → Shopping Street | `SchoolChooseWindow.lua` → `ShopMapWindow.lua` | Mapa con tienda de chicas, skins, mercado, intercambio y artefactos | Edificios originales, entradas navegables. Compras pendientes. |
| Study → Transfer, Slots, Intern, Enroll | `SchoolChooseWindow.lua` | Altares, máquinas, encargos y facciones | Ventanas visuales; acciones pendientes. |
| Life → Date, Dorm, Outfit, Outfit Store, Outfit Showcase, Costume Wardrobe | `SchoolChooseWindow.lua` | Rutas respectivas; Dorm enlaza tienda y visitas, Date enlaza historias | Fondos y elementos visuales originales donde se encontraron. Simulación pendiente. |
| Inicio → League → Battle | `MainWindow.lua` → `BattleChooseWindow.lua` | Tests, Daily Quiz, Sanctuary, Echoes of Time, Practice | Tests y Daily Quiz tienen combate local y progreso persistente. Sanctuary, Echoes of Time y Practice conservan navegación visual. |
| Inicio → League → League | `BattleChooseWindow.lua` | Arena, Team Arena, Cross-server Arena | Entradas visuales; clasificación en red pendiente. |
| Barra inferior → Gremio | `MainWindow.lua` → `GuildJoinWindow.lua` o `GuildTerritoryWindow.lua` | Buscar, crear y territorio; dentro: sala, comedor, gimnasio, guerra, laboratorio y tienda | Mapa e iconos originales; membresía y transacciones pendientes. |
| Barra inferior → Menú | `MainWindow.lua` → `SettingUpWindow.lua` | Recuerdos, colección, avisos, ayuda, mejoras, cómic, fondos y logros | Iconos originales; la colección enlaza la galería local. |
| Iconos laterales de Inicio | `MainWindow.lua` y componentes de la portada | Correo, eventos, tesoro, amigos, libro, Servant y excursión | Entradas visuales para continuar la restauración. |

La interfaz muestra una nota dentro de cada pantalla cuando su lógica aún no existe. Los botones de regreso y la barra inferior permiten volver a las secciones que ya funcionan. El grafo concreto está en `menuRoutes` de `web/app.js`; los recursos copiados están en `web/assets/menus/`.

Tests usa `tower.lua` (2.000 pisos), `TowerMap.lua` y `TowerWindow.lua`. Muestra el piso actual y los siguientes nueve; la ficha de cada piso enseña enemigos, poder y premios cuando están disponibles. El motor recuperado contiene combates de los primeros 1.500 pisos; los restantes quedan marcados como pendientes. Cada intento real consume una ficha, una victoria abre el piso siguiente y entrega la recompensa una vez; se recupera una ficha cada 30 minutos hasta diez. La práctica no modifica la partida. Los gráficos de puertas, cofres y ficha provienen de `~/Downloads/Decompiled/Sprites (atlases, cut)/`; los tres fondos de piso vienen de `textures/scenes_web` de la decompilación anterior. El script para reproducir la extracción está en `tools/extract_tower.py`.
