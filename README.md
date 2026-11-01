# Atlas de meteoritos

Aplicación interactiva en español con Shiny Core para Python, Plotly y Leaflet.

**Abrir la aplicación:** https://Lucky-Gauss.github.io/atlas-meteoritos-shiny/

Funciona directamente en el navegador mediante Shinylive. No requiere cuenta ni instalación. La primera apertura descarga Python y sus bibliotecas, por lo que puede tardar. Los filtros se procesan en el navegador del visitante.

## Contenido

- Mapa con agrupación y concentración por celdas de 5 grados.
- Histograma de masas con escala original y logarítmica.
- Evolución anual o por década, barras de clases y diagramas de caja.
- Filtros compartidos, indicadores, tabla ordenable y descarga CSV.
- Informe académico con capturas reales, datos originales, limpieza y pruebas.

Los 45 716 registros provienen del CSV oficial de NASA, descargado el 31 de octubre de 2026. Se conserva el original, con 10 columnas. La versión preparada tiene 15 columnas y conserva todas las filas. Se distinguen caídas observadas y hallazgos. El catálogo no es un censo de todos los impactos.

Fuente: https://data.nasa.gov/dataset/meteorite-landings

Archivo: https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv

La ficha actual de NASA no especifica licencia. Las licencias de bibliotecas y tipografía se conservan separadas. Natural Earth es de dominio público. No se atribuye una licencia global a los datos.

## Archivos y reproducción

`atlas-publicacion.zip` conserva la aplicación completa, los datos, recursos locales, documentación e informe. Se descomprime en la raíz y genera `app/`, `docs/` e `Informe_Atlas_Meteoritos.pdf`. El código principal también puede consultarse en `app/` dentro del repositorio.

Para generar la web desde el archivo descomprimido:

```text
python -m pip install shinylive==0.8.13
shinylive export app site
python -m http.server --directory site 8008
```

El workflow publica con GitHub Pages. Solo tiene lectura del contenido y los permisos de despliegue requeridos por Pages. No modifica el código ni crea contribuciones de estudiantes.

Este repositorio contiene un borrador independiente. No sustituye el trabajo colaborativo ni la evidencia de contribuciones del equipo. Integrantes, carnés, roles y fecha académica quedan pendientes de confirmar.
