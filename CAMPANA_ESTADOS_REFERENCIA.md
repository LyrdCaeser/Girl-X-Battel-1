# Campaña — tres estados de referencia

GXB2-CAMPAIGN-074, 2026-10-01.

Se restauran los dos accesos superiores originales: Protect the Doggy y recompensas de campaña. Los sprites proceden del cliente recuperado. El libro muestra Claim, punto rojo y dos premios cuando una recompensa se puede reclamar; en caso contrario indica las etapas que faltan hasta el final del capítulo. Su botón abre el premio real y usa el sistema de reclamación existente. Protect the Doggy identifica su ventana original; el minijuego sigue pendiente y su acceso informa de ello.

Chibis de patrulla más grandes (altura objetivo 190 frente a 118 unidades), centrados por sus límites visibles y repartidos en tres chicas y dos enemigos, tal como indica BattleHangUp.defaultMonsterMaxNum=2. Se usan los personajes y monstruos de la partida y del mapa; la selección de dos monstruos de la vista local es determinista. No se altera la formación de combate.

Montaña original de monedas: efecto Spine guajijiemian recuperado desde el esqueleto, atlas y canales RGB/Alpha originales. Niveles visuales después de media hora, tres horas y seis horas como CampaignWindow:addGoldEffect. Collect entrega los recursos y objetos reales y oculta la montaña; el punto rojo del regalo sigue el número real de tiradas pendientes, incluso antes de media hora. La vista de contadores conserva la economía ya calculada para etapas anteriores y añade sólo el ingreso nuevo. El snapshot incluye drop_seconds para respetar el resto del reloj de botín tras recoger, separado del reloj de ingreso, con el límite de doce horas.

Contadores superiores alineados, iconos originales, cifras abreviadas K/M y botón + sin desplazar el texto. El cristal verde de campaña es EXP de chicas (objeto9), no las gemas del objeto2; Inicio conserva las gemas. El formato corto se mantiene tras Collect y otras actualizaciones.

Corrección de premio anticipado: fort_finish es el número del último capítulo terminado, no una bandera. Antes se usaba su valor distinto de cero para dar por terminado fort_id al entrar en el siguiente capítulo. Ahora 13-8 conserva doce capítulos terminados y no habilita el premio del capítulo13 hasta 13-10. Las recompensas previamente reclamadas no se revocan.

Fuentes: CampaignWindow.lua (checkCampaignRedState, addGoldEffect), BattleHangUp.lua, CampaignAwardWindow.lua, AchievementTable.lua y tablas stage/achievement. Assets originales conservados; extractor tools/extract_campaign_scene.py permite regenerarlos.

QA aislada en validation/campaign-loot-2026-10-01: estado13-8, seis horas de botín preparadas para comprobar su montaña; Collect real, desaparición de la montaña y premios reales; preparación del escalón de capítulo13 para comprobar Reward after 2 Stages. Pruebas nuevas cubren ambos relojes/restos/límite y la frontera13-8/13-10. No se modifican partidas habituales.

Validación final: 366/366 pruebas generales aprobadas en 257,011 s, incluidas las dos pruebas nuevas de frontera de capítulo y relojes independientes. JS/diff válidos. QA visual final muestra los cinco chibis, montaña original visible, Collect real sin montaña y Reward after 2 Stages con dos iconos. Avisos HTTP históricos por conexión cerrada no fallan las pruebas.
