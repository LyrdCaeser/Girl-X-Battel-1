# Campaign: oro y ventana · 084

El montón animado de monedas se amplió con margen de recorte para que sus píxeles visibles alcancen ambos bordes de Campaign, manteniendo la proporción original y las plantas delante.

La ventana Auto-Battle abierta al pulsar las chicas caía en document.body porque Campaign no es un section directo de game-root. Ahora el fallback usa el marco del juego. Las ventanas comunes miden sus unidades respecto a su overlay y limitan su tamaño al 94% del contenedor; los huecos de formación también se ajustan al ancho del juego.

Validación: sintaxis de los dos JS modificados y diff; QA visual de oro hasta ambos bordes y Auto-Battle dentro del juego (ventana 475 px frente a marco de 505 px). Apertura y cierre comprobados, sin guardar cambios de equipo ni reclamar recursos.
