# Campaña e Internship — 077

## Campaña
El suelo original no está invertido: campaign_select_bg.png contiene plantas y tierra, sin conexiones de etapas. Las conexiones son piezas independientes del prefab CampaignWindow; la colocación anterior de esas piezas no llegaba a las etapas. Ahora una ruta continua dibujada detrás de los hexágonos conecta sus centros, alternando las dos alturas y con esquinas redondeadas.

Se recuperó el canal alfa del suelo original: recorte (12,164,1012,858), PNG RGBA de 1000×694. Así las plantas aparecen delante del oro sin huecos negros. La montaña animada Spine ocupa 750 unidades, el ancho completo del diseño. La escena continúa hasta la fila de recursos; Fight, libro y regalo bajan 33 unidades. Se elimina la barra vertical de campaña ajustando la composición al marco.

La cápsula de recursos (sprite original 60×36) conserva los extremos con nueve cortes: 12/18/12/18. Collect conserva su marco original de 65×65 con cortes de 19. No se estiran completos los bordes.

## Internship
Barras de progreso, bandas de estrellas y botones conservan sus extremos originales mediante nueve cortes. Las etiquetas de progreso se superponen al fondo para evitar que el borde las recorte.

Se recupera btnRefresh al final de los siete filtros de estrellas. Fuente: tavern_window/content/choosePart/btnContent/btnRefresh, posición x287, sprite switch_btn, 52×53. TavernWindow.lua initChoosePart/getRefreshCost confirma refresco pagado. El botón abre una vista previa del número de encargos y coste; aplicar llama a la acción refresh existente. No afecta los encargos bloqueados, en curso o terminados. Coste original pub_mission_refresh_cost: 2#10 (10 gemas por encargo). Se retira el acceso escondido dentro de Use; Use queda para pergaminos.

## Validación
Ocho pruebas existentes de Internship pasan, incluida conservación de encargos bloqueados y cobro del refresco. JavaScript y extractor Python válidos; git diff --check limpio. Revisadas visualmente campaña, bordes de Internship y ventana Refresh: seis encargos elegibles, 60 gemas, un encargo en curso protegido. Se canceló la vista previa sin gastar gemas ni renovar encargos del usuario. No se modificaron guardados ni otros servidores.

Paquete incremental: requiere la reconstrucción previa hasta 076; no incluye base de datos ni instalador completo. Servicio de revisión existente: http://localhost:59074/.
