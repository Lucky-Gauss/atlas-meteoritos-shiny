# Verificación del navegador

Se utilizó el navegador integrado de Codex con el servidor local Shiny. Capturas reales en `output/screenshots`. Fecha de trabajo: 31 de octubre de 2026, Costa Rica.

## Casos comprobados

- Carga inicial con 45 716 registros, 32 186 ubicaciones, mediana 32,6 g y 466 etiquetas de clase.
- Filtro de caídas observadas con 1 107 registros y 1 096 ubicaciones.
- Búsqueda Allende con un registro. Su ventana muestra clase CV3, 2 000 000 g y año 1969.
- Allende combinado con hallazgo produce cero registros y un aviso explícito.
- Filtro sin ubicación conserva 13 530 registros para análisis.
- Desde 1900 sin años desconocidos produce 44 696 registros.
- Selección exacta L6 produce 8 285 registros. Existen variantes de clases con espacios al final que se conservan y se distinguen en el selector.
- La descarga CSV de L6 se completó desde el navegador. El archivo se volvió a leer y contiene 8 285 filas y únicamente la clase L6.
- La tabla se ordenó por nombre y se comprobó el cambio de las primeras filas.
- Restablecer filtros recupera el catálogo completo, incluidas las categorías múltiples.
- Se comprobó el dibujo del mapa agrupado, la ficha individual y la capa de concentración.
- El histograma alternó entre escala logarítmica y original.
- La evolución temporal alternó entre conteos anuales y por década.
- Las cajas alternaron entre condiciones y ocho clases. Los valores pequeños del eje se muestran en gramos decimales.
- Los cuatro gráficos renderizaron sin errores de JavaScript registrados.
- Se verificó una ventana móvil de 390 × 844. No hubo desbordamiento horizontal general y los filtros aparecieron plegados.

## Alcance y límites de esta revisión

La cámara de Plotly se accionó, pero no se confirmó el archivo PNG descargado en el navegador integrado. Se comprobó la descarga CSV. No se afirma una auditoría completa de accesibilidad, una prueba con lectores de pantalla o cobertura de todos los navegadores. Las modalidades de zoom temporal y todos los tamaños de pantalla no se probaron exhaustivamente.

Las 18 pruebas automáticas adicionales sobre datos reales se detallan en `pruebas_datos.md`.

La revisión de la versión pública se documentará por separado en `publicacion.md` cuando finalice su despliegue.
