# Rediseño: expedición Miga

La aplicación conserva Shiny, los 45 716 registros y las reglas estadísticas. La portada tiene una Tierra ilustrada, meteoritos facetados y Miga, una sonda original. Las secciones combinan violeta, crema, esmeralda y coral. Las ilustraciones son conceptuales y no sustituyen la cartografía ni representan masas a escala.

Referencias consultadas: https://shop-us.kurzgesagt.org/collections/posters y su colección Universe Infographic Poster. Se observó la galería oficial en el navegador. Se tomaron como orientación las formas planas, las escenas en capas y los contrastes de escala. No se copiaron recursos ni se visualizaron videos.

## Archivos

- `app.py` integra portada, escenas, panel de filtros y resumen de filtros activos.
- `atlas/illustrations.py` carga SVG locales reutilizables.
- `scripts/build_illustrations.py` genera las cinco escenas originales de `www/illustrations/`.
- `www/atlas.css` define colores, tipografía, componentes y adaptación de pantalla.
- `www/museum.js` controla filtros, teclado, pausa, visibilidad de animaciones y trayectoria al desplazarse.
- `atlas/charts.py` cambia únicamente la presentación visual de las figuras.
- `www/atlas.js` conserva el mapa y adapta los colores y transiciones.

Las animaciones se ejecutan en el navegador. Se pausan fuera de pantalla, admiten un control de pausa y respetan movimiento reducido. Se usa IntersectionObserver, sin nuevas dependencias. El informe académico anterior se conserva como referencia.

## Verificación

El 1 de noviembre de 2026 pasaron las 18 pruebas estadísticas. El SHA-256 del archivo original permanece idéntico. Se verificaron en navegador las cuatro secciones, Allende con un registro, combinación vacía, restablecimiento, 13 530 registros sin ubicación, mapa agrupado, concentración con 495 celdas, zoom, ficha Allende, escalas del histograma, cajas por clase, frecuencia de clases, serie anual y zoom de Plotly. Se comprobó ordenamiento ascendente y descendente de nombres.

Se accionó la descarga CSV en el navegador. Además, se leyó el endpoint de descarga de esa sesión y se verificaron 13 530 filas de la selección sin ubicación, todas con bandera falsa. No se confirmó el archivo guardado automáticamente por el navegador ni la descarga PNG.

Se inspeccionaron ventanas de 390, 820, 1280, 1440 y 1920 píxeles. No se detectó desbordamiento horizontal general en las medidas comprobadas. Escape cierra los filtros y restaura el foco. La pausa manual funciona. No se realizó una auditoría de lector de pantalla ni se cambió la preferencia de movimiento del sistema operativo. Se corrigió un error de concatenación de funciones JavaScript y se comprobó una recarga sin errores de consola.

Capturas reales en `output/rediseno/`: portada, móvil, tablet, análisis, catálogo, metodología y ficha. No son maquetas.

## Ejecutar y publicar

Usar `Iniciar_Atlas.ps1 -Puerto 8767` desde PowerShell en la carpeta del proyecto. Las dependencias existentes son suficientes. Para regenerar SVG, ejecutar `python scripts/build_illustrations.py`.

Se publican dos versiones. La expedición ilustrada vive en la raíz y la versión clásica en `/clasico/`. El exportador recupera la clásica del commit `cc5642bc9890928b605a7714abd6c16b99d5d3a6`, sin modificar el historial. Cada versión tiene un enlace a la otra. Las futuras modificaciones de la raíz no alteran la copia clásica. El usuario autorizó expresamente commit y push del rediseño y pidió mantener ambos enlaces.
