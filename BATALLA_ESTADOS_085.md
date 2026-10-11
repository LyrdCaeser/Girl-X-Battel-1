# Battle 2-8: jefe y estados · 085

Los datos originales identifican 2-8 como stage20/battle100020: cinco enemigos (stands 1,2,3,4,6), incluido Blowie (monster44, partner52002), jefe situado entre dos posiciones. La prueba usa seis aliadas y los cinco enemigos originales; se cargaron once modelos.

La reproducción aplicaba a todos los jefes la escala sin normalizar y el anclaje inferior de Sanctuary. Ahora la posición inferior especial solo se aplica cuando el informe contiene boss_bar; los jefes de batallas normales conservan su posición de formación, centrada entre huecos cuando corresponde, y una escala acotada a 330 unidades de alto. Su barra de vida vuelve a estar visible y alineada.

Se extrajeron 144 iconos originales para 158 estados desde buff y buff_text_en_en. Debajo de la vida aparecen hasta cuatro iconos, con contador de acumulaciones y nombre en inglés al pasar el cursor. La reproducción sigue BattleWindow/BaseFighter: buffOn 0/1 añade, 2 activa sin duplicar, 3/4 retira un estado del mismo nombre y signo. Se limpian al morir. Los estados sin icono original siguen sin inventar símbolos.

Validación: prueba de ciclo de estados (altas, activaciones, bajas, signo, acumulaciones); JS y diff; comprobación de todos los archivos de iconos. QA con informe del motor original 2-8: once modelos, sin errores de consola, quemadura y curación continua visibles con texturas cargadas. El servidor temporal de QA añadió una pausa visual después del frame8 para inspección; no cambió la simulación original ni la partida del usuario. Se cerró al terminar.

Archivos: web/battle-animation.js, web/app.js, web/style.css, web/assets/spine/battle-status.json, web/assets/spine/status-icons; extractor tools/extract_battle_status.py y prueba tests/test_battle_status.js. No se cambió la economía ni el motor de batalla.
