# Friend Boss, Servant Training, Ulticore y Practical Work — 01/10/2026

Botón **Training & Bosses** en Inicio, con pestañas Friend Boss / Training / Practical Work. Training también se abre desde Servant. Reinicia el servidor habitual para cargar el código nuevo. No se modificaron las partidas habituales durante la implementación; la validación utiliza bases temporales.

## Friend Boss actual

Se usa `friend_boss_new` (12 dificultades), tal como carga `FriendBossTable.lua`, junto con `Friend.lua`, `FriendWindow.lua`, `FriendBossBattleFormationWindow.lua`, `FriendBossSwitchBossLevelWindow.lua` y `FRIEND_ASSISTANT_HELP`. No se confunde con la tabla antigua `friend_boss`, que describe búsquedas y energía diferentes.

- Player Lv36. Equipo y Servant propios; motor Lua original, BattleType FRIEND_BOSS=7.
- Una victoria diaria. Derrota no consume la victoria del día ni concede premios. Reintentos permitidos.
- Umbrales originales por poder combinado de las seis chicas más fuertes; dificultad observada nueva pendiente hasta el día siguiente. El poder se observa al consultar/abrir/luchar con Friend Boss. No se reconstruyen poderes históricos no guardados.
- Dropbox originales por dificultad, una vez por victoria. Tres victorias propias en una dificultad permiten saltar el combate de esa dificultad, consumiendo la victoria diaria.
- Sin amigas ficticias, Girl on Duty, rankings de apoyo ni premios sociales simulados.
- HTTP `/api/friend-boss/action`; mensajes actuales GET_FRIEND_BOSS_INFO y FRIEND_BOSS_FIGHT. Informe del combate normalizado y mochila push validados antes de guardar.

## Servant Training y Ulticore

Fuentes: Pet.lua/PetTraining.lua/PetSlot.lua, PetTrainingWindow/Detail/Lesson/SelectBoss, PetEvolutionWindow, PetDetailWindow y sus tablas/misc originales.

- Training tras un Servant Lv120. Diez niveles de sala y diez muñecos; 15 cursos, tres posiciones, 1–3 Servants por curso, sin compartirlos entre cursos. Servant ocupado en curso no ataca al muñeco.
- Puntuación original: **nivel ×5 + Ulticore ×20 + suma de auras ×2**. Daño entre 0,8× y 1,2×, con distribución uniforme local explícita porque el cliente no expone la distribución del servidor.
- Tres desafíos y dos energías por Servant al día. Dos compras adicionales, 80/120 gemas, restauran una energía al Servant elegido y una oportunidad global. Cada ataque incrementa el contador persistente del diario.
- HP retenidos entre ataques; el muñeco revive al morir. Se conserva el exceso de daño, incluido más de un renacimiento si procede. Premio final **sustituye** al premio normal en el ataque que mata, como indica PET_TRAINING_HELP. Cambiar de muñeco reinicia sus HP.
- Cursos con duración/puertas originales por nivel de sala; bonificación por suma de niveles. La recompensa queda fijada al comenzar, adaptación local documentada para evitar ambigüedad al mejorar Servants durante el curso. Cancelar libera Servants sin premio; reclamar exige temporizador vencido y vacía la posición una sola vez.
- Entrenamiento automático por ciclos de 600 segundos, tope y multiplicadores originales por niveles totales. Primera apertura inicia el reloj; no se regala acumulación previa no demostrable. Cobrar reinicia el reloj.
- Ulticore Lv120: coste de desbloqueo original, mejoras hasta Lv100 para los nueve Servants, 900 filas de costes/efectos. Se pasa `ex_lv` al ReportPet original del combate.
- Reset devuelve los materiales acumulados de la fila `restore`, excluye monedas y vuelve a Ulticore 0. La fila incluye el coste de apertura. Auras por encima del límite base 30 bajan a 30 y devuelven sus Spirit Cookies, sin monedas. Límite adicional de auras por tramo de Ulticore, según PetPasSkill:getCurMaxLev, hasta 50.
- HTTP `/api/pet-training/action`; ocho mensajes PET_TRAINING_* actuales y ACTIVE/UPGRADE/RESET_PET_EXLEVEL. La solicitud extendida pet_ids no se simula: el cliente observado envía un Servant por ataque.

## Practical Work / World Boss

Fuentes: ActivityWorldBossData.lua, ActivityWorldBoss.lua, ActivityWorldBossWindow.lua, ActivityBossTable.lua, ACTIVITY_WORLD_BOSS_HELP y `activity_boss`.

Tres proyectos, **ocho jefes por proyecto** (24 filas). Cadena next_id, HP, dropbox y premios finales originales. Cada combate usa un Practical Map (28); compra 50 gemas por mapa y límite original. Motor Lua BattleType WORLD_BOSS=13, con HP restantes pasados como porcentaje al combate. El daño acumulado usa sólo las posiciones de chicas 1–6; Servant no reduce el HP del proyecto. Premio final por correo original y adjuntos únicos, sin sustituirlo por una entrega inmediata.

LOCAL-080: evento disponible desde el menú local; temporada fija de 30 días anclada a la creación de la partida porque el calendario de actividad del servidor no está disponible. HP absoluto conservado por proyecto; entrada al motor por porcentajes enteros, como el formato local existente. El stock inicial de mapas se mantiene; no se reconstruyen regalos históricos de apertura. `activity_boss_open_award` se preserva en los datos, sin inferir una entrega original del servidor.

**Discrepancia sin resolver:** las misiones antiguas de Growth Diary 116/130/160 dicen etapas 1-10/2-10/3-10; el cliente recuperado sólo contiene etapas 1–8. No hay una correspondencia demostrada que permita reclamar esas misiones. No se reemplaza 10 por 8 ni Practical Work por Soul Land.

## Diario y pendientes

**157/160** misiones con seguimiento. Se incorporan 99 Friend Boss, 153 Training Dummy y 156 Ulticore. Sólo 116/130/160 quedan sin métrica. Chat y Elite League de Newbie Camp siguen pendientes, además de apoyo social de Friend Boss y calendario/protocolo original de Practical Work.

## Validación

**364 tests generales aprobados**, incluidos diez tests nuevos: límites diarios/energía/compras, derrota/reintento/victoria, desbloqueo al siguiente día, skip, cursos exclusivos/tiempo/cancelación, idle, costes/reset/aura caps, correo, temporadas, concurrencia y rollback del protocolo. Se actualizaron dos expectativas de tests anteriores para reflejar las tres misiones ahora conectadas; no se eliminó ninguna prueba.

Verificación nativa en DB temporal: Friend Boss victoria con motor original y mensaje FRIEND_BOSS_FIGHT codificado (dos paquetes); Practical Work produjo daño positivo y descontó exactamente ese daño de HP. JavaScript sintácticamente válido. QA web en `validation/remaining-2026-10-01/qa.sqlite3`: navegar, desbloquear Ulticore, atacar (HP3600→2932, energía2→1, desafíos3→2), recargar y verificar persistencia; presentación revisada y barras/paneles sin rótulos comprimidos. Completar cursos/idle por tiempo se verifica en tests con reloj controlado. No se adelantó el reloj de partidas habituales.
