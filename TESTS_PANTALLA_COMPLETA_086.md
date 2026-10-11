# Tests y BattleWindow — 086

Reconstruida la pantalla de Tests con los fondos tower_bg00/01/02, puerta abierta original, placa del piso, chibis Spine animados y controles superiores. La lista abre en el piso actual y permite consultar los nueve próximos pisos. El aviso de recompensa muestra el próximo múltiplo de cinco con las cantidades de las tablas recuperadas.

La ventana de cada piso presenta poder, seis avatares de enemigos con nivel, premios y Fight. Los pisos futuros permiten consultar pero no combatir. Los pisos superados muestran el asset original tower_icon02 (KEEP OUT), ocultan al enemigo y deshabilitan el combate. El servidor rechaza también repetir pisos superados con practice=True. Record reproduce el último informe de esta sesión sin gastar fichas ni volver a ejecutar el combate. Los rankings online siguen sin estar disponibles en esta versión local.

Todas las batallas que usan el visor de eventos ocupan el marco completo de 480×853, igual que la campaña. Se ocultan cabecera, narración, premios y navegación externos; Continue del resultado vuelve al modo de origen. La pantalla de carga se usa también al combatir en Tests y su barra preserva los extremos mediante nueve cortes.

Verificación: nivel 413 con poder 2,118,286, seis Ennmaya nivel 266, oro 210K y 210 Lunch Boxes; piso 414 Locked; pisos 411/412 KEEP OUT; combate y repetición del 413 a pantalla completa. Capturas en los outputs del chat. Prueba test_tower_practice_progress_rewards_and_ticket_recharge pasó, incluyendo rechazo de repeat practice tras victoria. Sintaxis de app.js/campaign-ui.js y revisión de espacios pasaron.

Las pruebas visuales usaron una copia independiente de la partida en validation/tests-086/preview.sqlite3 con avance 412. La partida del servidor 59074 no fue modificada por las pruebas. Servidor principal reiniciado para cargar el bloqueo del backend. Servidor temporal 59086 detenido al finalizar.
