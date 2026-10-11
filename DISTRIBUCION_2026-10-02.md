# Distribución — 2 de octubre de 2026

Paquete completo del proyecto para macOS y Windows, con los datos, recursos gráficos, animaciones, voces y motores de combate incluidos. Sigue las instrucciones de README.md para instalar Python e iniciar el juego. El primer inicio crea una partida nueva.

Esta actualización reúne los cambios posteriores a la distribución del 30 de septiembre:

- Tablas originales recuperadas, Growth Diary, Newbie Camp y sistemas de entrenamiento y Friend Boss.
- Navegación de chat y amigos; ajustes visuales de Campaign, selección de piso y botín, Internship, Dorm y Trophies.
- Guías ilustradas en los botones de ayuda correspondientes.
- Iconos cuadrados de chicas y shards, estrellas según rango, ilustraciones originales, brillo y marcos de avatar.
- Textos de interfaz en inglés y catálogo para una futura localización.
- Efecto mágico al pulsar, indicadores de efectos de estado y disposición corregida de las batallas.
- Tests con pisos del colegio, chibis, vista de enemigos y recompensas, y KEEP OUT en los pisos superados.
- Batallas a pantalla completa, formación centrada entre Round y los controles del Servant, y rótulos originales VICTORY/DEFEAT en inglés.

Los sistemas online y la reconstrucción completa del juego siguen teniendo límites documentados en ESTADO_PROYECTO.md y los informes de cada sistema. Esta distribución no recupera una cuenta de los antiguos servidores.

El ZIP se genera desde el mismo commit que se sube a GitHub, con una carpeta principal GxB2-local. No incluye .git, partidas, exportaciones personales, pruebas, referencias locales ni archivos temporales. Conserva los permisos de los ejecutables de runtime. No necesitas las fuentes originales de Downloads para jugar.

## Verificación de esta entrega

- 374 pruebas automatizadas aprobadas en macOS.
- 71 archivos JavaScript revisados sin errores de sintaxis.
- 6.108/6.108 voces incluidas.
- 36.697 archivos previstos en el paquete; sin partidas ni archivos temporales.
- Revisiones visuales de Campaign, Tests y resultados de batalla documentadas en los informes recientes.

Los lanzadores y LuaJIT de Windows se incluyen. La comprobación Windows anterior está enlazada en README.md; no se ha realizado una revisión visual de esta actualización en Windows.
