# Formación de batalla y rótulos en inglés — 087

Todas las batallas comparten las posiciones de app.js. La formación completa baja 200 unidades en el lienzo de 1080×1920, aproximadamente el 10,4% de la altura, conservando sus posiciones relativas. Los modelos, barras de vida y efectos de estado usan los mismos anclajes; los efectos de habilidad ligados a cada chica siguen su nueva posición. La formación queda entre Round y el HUD inferior del Servant. Se conserva el tratamiento especial del jefe de Sanctuary.

Se añadieron los rótulos originales battle_result_text01_en_en (VICTORY) y battle_result_text02_en_en (DEFEAT) al resultado compartido, junto con la animación y los controles existentes. Los archivos son copias exactas de los assets recuperados; el código original BattleWinWindow.lua y BattleFailWindow.lua confirma la selección por idioma. No se usan versiones de otros idiomas.

Verificación visual con informe original de Campaign 2-8 (seis aliadas y cinco enemigas) en una partida QA independiente: formación centrada y espacio libre bajo Round y sobre controles. Se insertó una pausa exclusivamente en el informe QA para capturar la disposición. Ventanas de victoria y derrota previsualizadas con datos de ejemplo, sin conceder recompensas a la partida. DEFEAT carga con ancho original 512 px y los botones quedan dentro de la ventana; VICTORY y recompensas se ven completos. Sintaxis y revisión de espacios pasaron. Ambos assets responden 200 image/png en el servidor principal 59074.

Capturas: GxB2-Battle-Centered-087.png, GxB2-Victory-English-087.png y GxB2-Defeat-English-087.png en outputs del chat. Servidor QA 59087 detenido al acabar. Servidor principal activo con la partida existente; las verificaciones no la modificaron.
