# Atlas de meteoritos

Borrador local preparado el 31 de octubre de 2026 como referencia para Programación para Estadística II. No sustituye el trabajo colaborativo del equipo ni constituye una entrega académica definitiva.

## Objetivo y justificación

Explorar un catálogo histórico de meteoritos con una aplicación Shiny para Python que conecte geografía, masa, clasificación y tiempo. La combinación de variables numéricas y categóricas permite trabajar estadística descriptiva, distribuciones asimétricas, valores faltantes y programación reactiva sobre datos reales.

La base tiene 45 716 filas y 10 columnas originales. Supera el mínimo académico de 500 registros. El borrador conserva todas las filas, incluidos los 75 registros de tipo Relict, sin imputar valores ni inventar ubicaciones.

## Preguntas y vistas

1. ¿Dónde se concentran los registros con ubicación utilizable? El mapa agrupado y la vista de concentración muestran patrones de documentación.
2. ¿Cómo se distribuye la masa y cómo cambia entre condiciones o clasificaciones? El histograma y los diagramas de caja permiten estudiar asimetría y dispersión.
3. ¿Cómo varían los registros según el año consignado? La evolución temporal permite explorar intervalos y períodos.
4. ¿Qué clasificaciones son más frecuentes? El gráfico de barras permite comparar los conteos por clase.

Los indicadores y conclusiones del explorador corresponden a la selección de filtros vigente. Los resultados de este documento se calculan sobre el conjunto completo preparado.

## Fuente real

- Creador original: The Meteoritical Society.
- Publicación: NASA Open Data Portal, Meteorite Landings.
- Ficha oficial: https://data.nasa.gov/dataset/meteorite-landings
- Archivo oficial: https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv
- Solicitud exacta: https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv?download=20261031
- Descarga: 31 de octubre de 2026, referencia horaria America/Costa_Rica.
- Licencia: la ficha indica License not specified. El acceso público no permite atribuir una licencia abierta específica.
- Procedencia completa, dimensiones, hash SHA-256 y referencias en `data/provenance.json`.

La descripción del portal conserva referencias a una versión anterior con 34 513 filas. Para este borrador se usan las dimensiones medidas en el CSV descargado. Es una copia histórica y no un seguimiento actualizado de meteoritos.

El fondo cartográfico local procede de Natural Earth, versión 5.1.2, a escala 1:110 millones. Es de dominio público y se usa para orientación, sin asignar países a los registros. La URL exacta y el hash de la geometría se conservan en la sección `cartography` de `data/provenance.json`.

## Preparación y decisiones

| Revisión | Conteo | Decisión |
| --- | ---: | --- |
| Filas conservadas | 45 716 | Mantener el universo completo |
| Masas ausentes | 131 | Omitir únicamente en análisis de masa |
| Masas iguales a cero | 19 | Mantener, excluir de logaritmos |
| Masas negativas | 0 | No requiere exclusión |
| Años ausentes | 291 | Omitir en la evolución temporal |
| Año anómalo 2101 | 1 | Conservar, marcar y excluir de la serie temporal |
| Coordenadas incompletas | 7 315 | Mantener en análisis no geográficos |
| Coordenadas 0, 0 | 6 214 | Excluir del mapa por ubicación sospechosa |
| Coordenadas fuera del rango terrestre | 1 | Meridiani Planum, hallazgo en Marte |
| Registros cartografiables | 32 186 | Usar en mapa terrestre |
| Filas completas duplicadas | 0 | No eliminar registros |
| Identificadores duplicados | 0 | No eliminar registros |

Meridiani Planum se mantiene en los análisis generales del catálogo. Su longitud de 354,47333 no se transforma en una ubicación terrestre. El origen marciano está documentado en https://www.lpi.usra.edu/meteor/metbull.php?code=32789 y https://ntrs.nasa.gov/citations/20100003417.

El procedimiento está separado de la interfaz en `scripts/prepare_data.py`. El archivo original se conserva en `data/raw` y el preparado en `data/processed`. Las banderas de calidad determinan la elegibilidad por vista, sin atribuir una calidad perfecta a los registros restantes.

## Resultados del conjunto completo

- Hallazgos: 44 609 registros, un 97,58 %. Caídas observadas: 1 107 registros, un 2,42 %.
- Registros cartografiables: 32 186, un 70,40 % del catálogo. De ellos, 22 099 tienen latitud inferior a 60° S, un 68,66 %. Es una descripción por latitud, sin asignación de país.
- Mediana entre las 45 585 masas no negativas disponibles: 32,6 g. La media de esas masas es 13 278,08 g.
- Entre las 45 566 masas estrictamente positivas, la mediana es 32,695 g y la media es 13 283,62 g. Esta es la población usada en las comparaciones logarítmicas del informe.
- Entre masas positivas, la mediana de caídas observadas es 2 800 g y la de hallazgos es 30,54 g. La diferencia es descriptiva y no permite inferir causalidad.
- Hoba tiene la masa máxima consignada, 60 000 000 g.
- Se registran 466 etiquetas de clasificación. L6 es la más frecuente, con 8 285 registros, un 18,12 % del catálogo.
- Los 45 424 años elegibles abarcan de 860 a 2013. La década de 2000 a 2009 reúne el mayor número de registros, 17 757.

Las cifras pueden recalcularse desde el CSV. El redondeo empleado en el informe tiene fines de presentación y no altera la copia de los datos.

## Interpretación y limitaciones

Fell corresponde a caída observada y Found a hallazgo posterior. El año consignado representa caída o hallazgo según la condición, no una fecha de impacto conocida para todos los registros.

La distribución espacial está condicionada por búsqueda, conservación, acceso y documentación. Los conteos no miden tasas globales de caída y no sirven por sí solos para estimar riesgo. El predominio de hallazgos también limita comparaciones directas entre condiciones.

Las masas muy grandes influyen en la media. La mediana, los cuartiles y la escala logarítmica aportan información complementaria. Los ceros son válidos como valores registrados, pero no admiten una transformación logarítmica.

El catálogo es histórico, incluye un hallazgo marciano y no constituye un registro exhaustivo de impactos terrestres. No se imputan países, no se realizan pruebas causales y no se atribuye aleatoriedad a la muestra.

## Correspondencia académica y pendientes

El borrador propone Shiny Core para Python, datos públicos con más de 500 filas, cuatro preguntas de análisis, varias formas de visualización, filtros reactivos, documentación y un informe PDF con capturas reales.

Quedan por completar por el equipo sus nombres, carnés, grupo, docente, roles y contribuciones reales. La guía solicita evidencia de Git y colaboración. Este borrador independiente no inicializa Git y no inventa commits, ramas, aportes ni capturas de colaboración.

La guía académica imprime la fecha 23/11/2025. Debe confirmarse con el docente su aplicación al ciclo de 2026 antes de planificar una entrega.

La verificación de la aplicación se documenta aparte. Una captura real demuestra una pantalla observada, pero no acredita por sí sola que todas las interacciones hayan sido probadas.
