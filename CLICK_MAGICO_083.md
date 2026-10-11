# Círculo mágico de clic · 083

Recuperado el efecto original fx_dianji desde los assets de Unity, con su atlas y transparencia original. WindowManager:initClick/playClickAction confirma texiao02 para controles y texiao01 para el fondo.

La interfaz reproduce el efecto en la posición del clic o toque, y en el centro del control para activaciones de teclado. Tamaño proporcional al lienzo del juego. Capa sin interacción, por encima de ventanas mediante popover; no bloquea botones ni cambia el foco. Un renderer reutilizado, con actualización solo durante el efecto; se oculta al terminar o al ocultar la pestaña. Los clics consecutivos reinician la animación, como en el cliente original. Respeta movimiento reducido acortando el efecto.

Archivos: web/hero-glow.js, web/hero-glow.css, web/assets/spine/fx_dianji. Extracción reproducible: tools/extract_click_effect.py. No requiere cambios de servidor ni de partida.

Validación: sintaxis JavaScript y Python, diff sin errores; QA visual de texiao02 en Menu y texiao01 en Campaign, navegación conservada y efecto oculto al terminar. Captura GxB2-Click-Magic-083.png en outputs del chat.
