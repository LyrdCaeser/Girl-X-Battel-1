# Brillo y marcos originales — 081

Recuperados los efectos Spine shiziui_touxiang y shiziui_touxiang_tianyi desde los archivos Unity, con sus canales alfa originales. HeroIcon.lua activa el brillo desde 10 estrellas: texiao01 para 10, texiao02 para superiores y texiao03 como resplandor; Cosmos usa la variante tianyi. Los rangos menores conservan el marco hero_frame, los superiores usan hero_frame2.

Aplicado a fragmentos, ilustraciones originales de la colección y avatares cuadrados comunes y tarjetas de resultados de invocación. Se conservan nombres, nivel, facción y estrellas. Chicas y Galería mantienen sus ilustraciones y sus marcos de carta; los avatares usan sus marcos cuadrados. Los efectos se dibujan desde un solo renderizador compartido y únicamente en iconos visibles, sin crear un contexto WebGL por cada chica; los iconos retirados se liberan.

Validación: sintaxis JavaScript, compilación Python y diff correctos. Revisados visualmente colección y Shards, con rangos altos y bajos; sin errores de consola. Servidor 59074 actualizado conservando las partidas. Se requiere recargar las pestañas abiertas para cargar el nuevo módulo. No se ha reiniciado ningún otro servidor.

Avatar del jugador: recuperados 19 efectos originales de marco (item.avatar_frame_effect). Se muestran en Inicio, Perfil y vista previa según el marco seleccionado. La textura estática se oculta mientras aparece su marco animado, como PlayerIcon.lua. Comprobada vista previa de 8041 sin aplicar cambios al perfil.
