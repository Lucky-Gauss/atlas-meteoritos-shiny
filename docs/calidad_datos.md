# Fuente, preparación y límites de interpretación

Este documento describe la copia local descargada el 31 de octubre de 2026, en la zona horaria de Costa Rica. Las cifras siguientes corresponden al catálogo completo y no a una selección de la aplicación.

## Procedencia verificada

- Publicador: NASA Open Data Portal.
- Fuente original acreditada por NASA: The Meteoritical Society.
- Ficha: https://data.nasa.gov/dataset/meteorite-landings
- CSV oficial: https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv
- Solicitud efectiva de descarga: https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv?download=20261031
- Verificación independiente del enlace oficial en otro catálogo federal: https://catalog.data.gov/dataset/meteorite-landings
- Diccionario oficial conservado: `data/raw/MD_columns.json`, obtenido de https://data.nasa.gov/docs/legacy/meteorite_landings/MD_columns.json?download=20261031

El parámetro de descarga evita una redirección firmada antigua en caché. El recurso es el CSV oficial alojado por NASA. No se utilizó un espejo de terceros ni se generaron registros. El archivo original se conserva sin modificaciones. `data/provenance.json` contiene el tamaño, la huella SHA-256, las dimensiones y las referencias exactas.

La ficha actual indica **License not specified** y acceso público. Por ello no se declara CC0 ni una licencia de redistribución que NASA no especifica en esa ficha. La atribución se mantiene y cualquier publicación futura debe revisar las condiciones aplicables. La licencia de una réplica no se transfiere automáticamente al archivo descargado.

La descripción del catálogo menciona una versión anterior con 34 513 meteoritos. La copia descargada tiene **45 716 filas y 10 columnas**. Las dimensiones se calcularon directamente. El rango de años plausibles es 860 a 2013, por lo que es una instantánea histórica. La fecha de actualización de la ficha no demuestra que se hayan agregado observaciones nuevas.

## Variables y unidades

| Variable de origen | Interpretación utilizada |
| --- | --- |
| name | Nombre del meteorito |
| id | Identificador en el catálogo, conservado como texto |
| nametype | Valid o Relict, conservado sin excluir los relictos |
| recclass | Clasificación original. Existen 466 etiquetas distintas |
| mass (g) | Masa registrada en gramos. No representa por sí sola la masa original del objeto antes de atravesar la atmósfera |
| fall | Fell significa caída observada. Found significa hallazgo posterior sin caída observada |
| year | Año de caída para Fell o año del hallazgo para Found. No se interpreta el hallazgo como fecha del impacto |
| reclat, reclong | Coordenadas registradas, sujetas a validación antes de situarlas en el mapa terrestre |
| GeoLocation | Par redundante de coordenadas conservado en el original |

El diccionario oficial confirma la unidad gramos. La distinción del año y la condición también puede consultarse en la descripción de la copia distribuida bajo la cuenta NASA en https://www.kaggle.com/nasa/meteorite-landings/data. Para Meridiani Planum, el Meteoritical Bulletin distingue explícitamente año de hallazgo, condición y planeta.

## Auditoría y decisiones de limpieza

| Revisión | Registros afectados | Decisión |
| --- | ---: | --- |
| Masas ausentes | 131 | Conservar la fila. Excluir solo de cálculos o gráficas que requieren masa |
| Masas iguales a cero | 19 | Conservar en escala original. Excluir de escala logarítmica y explicitarlo |
| Masas negativas | 0 | No hay correcciones |
| Años ausentes | 291 | Conservar en catálogo. Excluir de la serie temporal |
| Año posterior a 2026 | 1 | Conservar 2101 como valor original. Marcar no elegible para tiempo, sin sustituir por 2010 ni otro valor supuesto |
| Pares de coordenadas ausentes | 7 315 | Conservar para análisis no geográficos |
| Pares de coordenadas 0,0 | 6 214 | Considerarlos ubicación no confiable y excluir solo del mapa. No afirmar que todos son errores demostrados |
| Coordenadas fuera de rango terrestre | 1 | No proyectar en la Tierra ni normalizar la longitud |
| Filas completas duplicadas | 0 | No se eliminan filas |
| Identificadores duplicados | 0 | No se eliminan identificadores |
| Nombres duplicados | 0 | No se combinan registros |
| Filas eliminadas | 0 | Las 45 716 filas permanecen en el preparado |
| Valores imputados | 0 | Los ausentes siguen ausentes |

La anomalía temporal es **Northwest Africa 7701**, con año 2101. La fuente descargada se conserva tal como está. La validación fija un corte de 2026 para que la reproducción del borrador mantenga el mismo criterio.

El registro **Meridiani Planum**, identificador 32789 y longitud 354,47333, corresponde a un meteorito hallado en **Marte** en 2005. No es una coordenada terrestre que deba corregirse sumando o restando 360 grados. Se mantiene en el catálogo histórico y fuera del mapa terrestre. Su inclusión en los conteos generales debe recordarse al interpretar el alcance del archivo. Fuentes de verificación: https://www.lpi.usra.edu/meteor/metbull.php?code=32789 y https://ntrs.nasa.gov/citations/20100003417

Los 75 registros Relict se conservan. La descripción de NASA identifica esta etiqueta con objetos muy alterados por meteorización. No se mezclan categorías, no se adivinan países y no se modifican clasificaciones.

## Universo disponible para cada vista

- Catálogo y comparaciones de clase o condición: 45 716 filas antes de aplicar filtros.
- Mapa terrestre: 32 186 filas con coordenadas elegibles, el 70,40 % del catálogo.
- Serie temporal: 45 424 filas con año válido.
- Estadísticas de masa no negativa y escala original: 45 585 filas.
- Distribución logarítmica y comparaciones que requieren logaritmos: 45 566 filas con masa positiva.

Los filtros generales actúan antes de las condiciones de elegibilidad de cada visualización. Por eso el número de puntos en el mapa puede ser inferior al número de filas seleccionadas. La exclusión geográfica no elimina la información de clase, nombre, masa o condición. La opción de incluir datos ausentes en filtros debe conservar ese criterio de manera visible.

## Preguntas y resultados descriptivos

1. **¿Dónde están documentados los meteoritos y cómo cambia el patrón entre hallazgos y caídas observadas?** El mapa utiliza los 32 186 registros ubicables. Hay 31 090 hallazgos y 1 096 caídas observadas con coordenadas elegibles. La concentración refleja también búsqueda, conservación y documentación, por lo que no estima tasas de impactos.
2. **¿Cómo se distribuye la masa registrada?** La mediana de las 45 585 masas no negativas es 32,6 g y el intervalo intercuartílico va de 7,2 a 202,6 g. El máximo es 60 000 000 g, correspondiente a Hoba. La media es aproximadamente 13 278,08 g. La asimetría justifica explorar la escala logarítmica, que separa órdenes de magnitud sin incluir los ceros.
3. **¿Cómo cambia la cantidad de registros a través del tiempo?** La mayor frecuencia anual del archivo es 2003, con 3 323 registros. Las fechas son años de hallazgo o caída según la condición. El resultado no permite afirmar que ese año tuvo más impactos.
4. **¿Qué clases aparecen más y cómo se comparan sus masas?** Hay 466 etiquetas de clasificación. L6 aparece 8 285 veces, H5 aparece 7 142 veces y L5 aparece 4 796 veces. Se conserva la etiqueta original y la gráfica puede limitarse a las más frecuentes, indicando el alcance.
5. **¿Difieren las masas registradas entre las dos condiciones?** Entre las masas no negativas, la mediana de las caídas observadas es 2 800 g, con 1 075 registros, y la mediana de los hallazgos es 30,5 g, con 44 510 registros. Es una asociación descriptiva de esta muestra histórica, no un efecto causal ni una comparación de todos los objetos que llegan a la Tierra.

En todo el catálogo, 44 609 registros son hallazgos, el 97,58 %, y 1 107 son caídas observadas, el 2,42 %. Estos resultados generales no deben presentarse como resultados de cualquier selección. `data/summary.json` permite reproducir cada cifra.

## Cartografía y límites generales

El fondo del mapa es Natural Earth a escala 1:110 millones, versión 5.1.2, almacenado en `www/vendor/world.geojson`. URL exacta: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_admin_0_countries.geojson

Natural Earth declara sus datos cartográficos de dominio público en https://www.naturalearthdata.com/about/terms-of-use/. El fondo sirve únicamente como orientación. No se hace una unión espacial para asignar países a los meteoritos ni se calculan estadísticas nacionales. Los límites representados no expresan una postura sobre disputas territoriales.

La proyección geográfica permite conservar los registros cercanos a los polos. Una agrupación visual por celdas de pantalla expresa conteos de registros, no densidades por kilómetro cuadrado. La comparación de áreas requiere considerar la distorsión y el esfuerzo de búsqueda. El archivo tampoco garantiza que cada fila equivalga a un impacto independiente.

Los datos no son un censo exhaustivo de todos los impactos. Hay sesgos de localización, acceso, preservación, campañas de búsqueda y documentación. La ausencia de coordenadas puede ser sistemática y la muestra geográfica disponible no representa necesariamente el resto del catálogo. Los extremos de masa son valores registrados, no errores que deban borrarse automáticamente.

## Reproducción

Ejecutar `python scripts/prepare_data.py` dentro de la carpeta del borrador regenera el preparado, la auditoría y el resumen a partir del original local. No requiere bibliotecas externas ni conexión. Agregar `--download` solicita explícitamente una nueva copia oficial y actualiza la procedencia. La aplicación no invoca esa descarga al iniciar.

Los campos `map_valid`, `year_valid`, `mass_positive` y `mass_nonnegative` son banderas de elegibilidad. `coordinate_issue` y `year_issue` explican las exclusiones. Ninguna de estas banderas cambia el valor original conservado.
