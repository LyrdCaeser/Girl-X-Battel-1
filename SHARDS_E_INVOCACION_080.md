# Shards e invocaciones — 080

Los fragmentos usan el rango del partner objetivo, incluida la evolución inicial de la configuración de invocación, en lugar de la calidad del objeto. Ghost Doll conserva 5, 6, 9 o 10 estrellas según su variante. Las tarjetas de resultado muestran el rango completo; los efectos animados mantienen las estrellas originales del cliente.

El revelado espera la carga de la imagen antes de iniciar el efecto, resuelve variantes mediante su personaje base y usa el avatar cuadrado cuando no hay ilustración completa. La escala utiliza show_scale_special y la posición vertical sigue la fórmula original 150 − partner_picture_xy.y. Esto corrige ilustraciones ausentes o fuera de encuadre.

La configuración awaken_lv se aplica al personaje adquirido: la Doll de nueve estrellas nace con la evolución original de tres niveles sobre su base de seis. Se corrigió también el coste de Shards, que multiplicaba por diez incluso al invocar una sola vez.

La entrada antigua 55001 (瓦拉斯基) carece tanto de ilustración como de avatar entre los recursos recuperados. Se conserva su dato original, sin inventar una imagen. No se migran retroactivamente personajes obtenidos antes de esta corrección.

Validación: 6 pruebas de cápsula (incluida regresión para Dolls 5/6/9/10 y coste), 15 de backend y modo desarrollador; todas pasan. Los 647 rangos de avatares coinciden con partner.max_star. JavaScript, extractores Python y diff validados. En una partida temporal separada se verificaron visualmente Ghost Doll, resultado 9★ y Sakura completa; se guardaron capturas. Servidor de revisión 59074 reiniciado conservando su base de datos.
