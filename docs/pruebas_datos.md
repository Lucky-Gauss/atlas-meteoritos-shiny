# Evidencia de pruebas de datos y filtros

Pruebas realizadas el 31 de octubre de 2026 sobre la copia real del CSV de NASA conservada en el borrador. Esta evidencia corresponde a pruebas automáticas del procesamiento y de los filtros. No sustituye la inspección de las interacciones en el navegador.

## Preparación

Se ejecutó `scripts/prepare_data.py` y se verificó que conserva las 45 716 filas y los identificadores originales. Se contrastaron el SHA-256 del original, las sumas de clases, las sumas por año y las banderas de elegibilidad.

- SHA-256 del CSV: `5b4c6a3596f177b3fe8b722e8a7e5f98f05628fe2167ec3bd007acdeb77036b5`.
- Ubicaciones utilizables: 32 186.
- Años válidos: 45 424.
- Masas no negativas disponibles: 45 585.
- Masas positivas disponibles: 45 566.
- Geometrías del fondo Natural Earth: 177.
- Meridiani Planum queda fuera del mapa terrestre.
- El año original 2101 de Northwest Africa 7701 se conserva con bandera temporal falsa.

## Filtros y exportación

Se ejecutaron **18 pruebas de unittest y todas pasaron**. La corrida registrada tardó 0,594 segundos en la ejecución de las pruebas, sin contar el arranque de Python. Se utilizó el entorno local `.venv` con pandas 3.1.0.

Comando desde la carpeta del borrador en PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_filters.py" -v
```

| Caso verificado | Resultado comprobado |
| --- | --- |
| Selección predeterminada | 45 716 registros, incluidas 131 masas ausentes y 291 años ausentes |
| Ubicación utilizable | 32 186 registros, con 1 096 caídas observadas y 31 090 hallazgos |
| Sin ubicación utilizable | 13 530 registros conservados para exploración no geográfica |
| Búsqueda por nombre | Allende se encuentra sin distinguir mayúsculas y con espacios externos |
| Símbolos de expresiones regulares | La búsqueda de `[` se interpreta literalmente, sin error |
| Condición | 1 107 caídas observadas o 44 609 hallazgos. Ninguna condición produce selección vacía |
| Intersección de clase y condición | L6 tiene 8 285 registros y L6 con caída observada tiene 262 |
| Selección contradictoria | Allende con condición hallazgo produce cero registros |
| Masa conocida | 45 585 registros, incluidos 19 ceros |
| Solo masas positivas | 45 566 registros |
| Ceros y ausentes | Son opciones independientes. Rango 0 a 0 permite aislar 19 ceros o 131 ausentes |
| Límites numéricos | El rango de masa 21 a 21 incluye 50 registros y sus extremos |
| Años conocidos | Excluir ausentes y anómalos produce 45 424 registros |
| Año anómalo | Se conserva 2101 cuando se incluyen años ausentes o anómalos |
| Período moderno | 1900 a 2013 contiene 44 696 registros con año válido o 44 988 al incluir años desconocidos |
| Año exacto | 2003 contiene 3 323 registros con año válido |
| Rangos invertidos | Tanto masa como año producen selección vacía, incluso si se incluyen desconocidos |
| Exportación | Diez columnas en español con unidades y banderas, coordenadas originales y clases con comas correctamente serializadas |
| Exportación vacía | Conserva la cabecera de diez columnas |

Se identificó y corrigió durante el desarrollo que un rango invertido podía conservar registros con valores desconocidos. La versión probada devuelve un conjunto vacío para ese caso. Las pruebas usan conteos del archivo real y ejemplos con significado, sin fabricar datos ni duplicar la lógica de filtrado.

La serialización CSV se comprobó con el registro Meridiani Planum, cuya clase contiene una coma y cuya masa está ausente. La longitud original 354,47333 permanece en la descarga con ubicación utilizable falsa. La prueba no convierte esa longitud en una coordenada terrestre.

## Alcance

Estas pruebas comprueban `atlas/filtering.py`, la estructura de exportación y la consistencia del archivo preparado. La descarga HTTP desde el navegador, el dibujo del mapa, las ventanas emergentes, la adaptación móvil y los controles de Plotly requieren una revisión independiente en la aplicación activa. No se declaran probados aquí.
