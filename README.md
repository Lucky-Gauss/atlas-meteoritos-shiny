# Atlas de meteoritos

Borrador universitario independiente y funcional en **Shiny Core para Python**. Tema espacial oscuro, mapa Leaflet, gráficos Plotly y datos reales de NASA.

## Abrir y compartir en internet

**[Abrir el Atlas de meteoritos](https://lucky-gauss.github.io/atlas-meteoritos-shiny/)**

[Repositorio público y código](https://github.com/Lucky-Gauss/atlas-meteoritos-shiny). La publicación utiliza Shinylive en GitHub Pages. Cada visitante ejecuta Python dentro de su navegador, sin instalar programas y sin depender de esta computadora. La primera carga necesita descargar el motor y las bibliotecas, por lo que puede demorar más que las visitas posteriores.

La copia local y los comandos siguientes siguen disponibles para desarrollo y uso sin conexión después de preparar el entorno.

## Guardar cambios y actualizar la web

Esta carpeta está conectada al repositorio público mediante Git. Desde una terminal en esta carpeta:

```powershell
git status
git add .
git commit -m "Describir el cambio"
git push
```

Cada envío a `main` inicia GitHub Actions, que construye y publica el sitio. Guardar un archivo o sincronizar OneDrive no publica cambios. Revisá `git status` antes de guardar una versión. El entorno `.venv`, la caché y los archivos temporales quedan excluidos mediante `.gitignore`.

Si editaste el repositorio desde otra computadora o desde GitHub, traé esos cambios con `git pull --ff-only` antes de empezar a trabajar. Si Git informa cambios locales o conflictos, resolvelos antes de continuar.

## Ejecutar la copia local en Windows

El entorno `.venv` ya está preparado en esta carpeta. Abrí PowerShell en la carpeta del borrador y ejecutá:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iniciar_Atlas.ps1
```

Después abrí **http://127.0.0.1:8765**. Mantené esa consola abierta. Para detener la aplicación, presioná `Ctrl+C`.

También podés iniciarla directamente, sin ejecutar un script de PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m shiny run --host 127.0.0.1 --port 8765 app.py
```

Si el puerto está ocupado porque el atlas ya está abierto, usá la sesión existente. Para ejecutar otra instancia:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iniciar_Atlas.ps1 -Puerto 8766
```

Abrí entonces http://127.0.0.1:8766. La dirección `127.0.0.1` limita el acceso a esta computadora.

## Preparar en otra computadora

Probado en Windows con Python 3.14.7. Usá Python 3.14 de 64 bits y verificá que el comando `python --version` funciona. No copies `.venv` entre computadoras. Los entornos virtuales contienen rutas absolutas y se deben crear nuevamente.

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe scripts\prepare_data.py
& .\.venv\Scripts\python.exe -m shiny run --host 127.0.0.1 --port 8765 app.py
```

El equivalente de los tres primeros comandos está en `Preparar_Entorno.ps1`. Solo la instalación inicial necesita internet. Los datos, mapas, tipografía, Leaflet, Plotly y su traducción se conservan dentro de la carpeta.

## Explorar

- **Explorar** muestra el mapa protagonista. Los círculos agrupados indican cuántos registros contienen. Al hacer clic se acerca el mapa o se muestran los primeros nombres si comparten ubicación. Los puntos individuales usan color por condición y tamaño logarítmico por masa. Su ficha muestra nombre, clase, masa, año y coordenadas.
- **Concentración** cuenta registros en celdas de 5° × 5°. La intensidad tiene escala logarítmica. No es densidad por km² y las celdas tienen distintas superficies sobre la Tierra.
- **Análisis** contiene histograma de masas, barras de las 12 clases más frecuentes, evolución anual o por década y cajas de masas por condición o por ocho clases frecuentes.
- **Catálogo** permite ordenar columnas. La búsqueda por nombre está en los filtros generales. El botón CSV descarga toda la selección, con unidades en los encabezados, coordenadas originales y banderas de calidad.
- **Los datos** explica procedencia, limpieza, preguntas, conclusiones generales y límites.

Todos los filtros generales se combinan por intersección. Ninguna condición seleccionada produce cero filas. Ninguna clase seleccionada significa todas las clases. Los años ausentes o anómalos y las masas ausentes se incluyen inicialmente y tienen casillas independientes. El rango de masas es inclusivo. Los ceros se incluyen solo si la casilla está activa y la mínima es cero. Un rango invertido produce una selección vacía con aviso.

**Los controles de zoom y leyenda de Plotly son locales a cada gráfico.** No modifican el mapa, indicadores, tabla ni CSV. El doble clic recupera el zoom. La cámara en la barra de cada gráfico exporta una imagen PNG. El selector inferior de la evolución temporal cambia el período visible. Los cambios de filtros generales regeneran los gráficos. No hay selecciones gráficas ocultas que filtren otras vistas.

En pantallas pequeñas los filtros se pliegan en un panel desplegable. Se respetan las preferencias de movimiento reducido del sistema y existen focos visibles para navegación con teclado. La tabla ofrece una alternativa textual al mapa y a los gráficos.

## Fuente y resultados

Archivo oficial: [Meteorite_Landings.csv](https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv).

Fuente: [NASA Open Data Portal](https://data.nasa.gov/dataset/meteorite-landings), datos de The Meteoritical Society. Descargado el **31 de octubre de 2026**, fecha de Costa Rica. Contiene **45 716 filas y 10 columnas**. El preparado conserva todas las filas y agrega banderas, con 15 columnas.

La ficha actual de NASA indica licencia no especificada. No se presupone una licencia abierta concreta. `data/provenance.json` guarda las URLs exactas de solicitud, hashes SHA-256, condiciones disponibles y referencias del diccionario y del mapa Natural Earth.

El catálogo es una copia histórica con años plausibles de 860 a 2013. No es un registro completo de los impactos del planeta. Hay 44 609 hallazgos y 1 107 caídas observadas. La mediana de las masas conocidas, incluidos los ceros, es 32,6 g. Hay 32 186 ubicaciones utilizables y 13 530 registros que permanecen disponibles fuera del mapa.

Se excluyen del mapa las coordenadas ausentes, fuera de rango y el par sospechoso 0, 0. **Meridiani Planum fue hallado en Marte**. Se conserva con sus coordenadas originales y no se coloca artificialmente en la Tierra. El año 2101 se marca como anómalo. Los años ausentes o anómalos no entran en las series temporales. Las masas cero no se convierten a logaritmos.

El año de un hallazgo no es una fecha conocida de impacto. Las concentraciones pueden reflejar búsqueda, conservación y documentación. La mediana de masa no representa el tamaño de todos los meteoritos que llegan a la Tierra. Las masas de las cajas se restringen a valores positivos y se calculan sin muestreo.

## Estructura

```text
app.py                      Interfaz y servidor reactivo
atlas/filtering.py          Filtros y exportación compartidos
atlas/charts.py             Figuras y estadísticas Plotly
www/atlas.css               Identidad visual y adaptación móvil
www/atlas.js                Mapa, navegación y puente con Plotly
www/vendor/                 Bibliotecas, tipografía y cartografía locales
data/raw/                   Archivo y diccionario originales
data/processed/             CSV preparado con banderas
data/provenance.json        Procedencia, licencia y hashes
data/summary.json           Auditoría y resultados completos
scripts/prepare_data.py     Preparación reproducible con biblioteca estándar
scripts/fetch_assets.py     Descarga opcional de recursos visuales
scripts/build_report.py     Generación del informe PDF
tests/test_filters.py       Pruebas sobre datos reales
docs/                       Método, resumen académico y verificación
output/                     Informe, capturas y evidencia de exportación
```

## Reproducir análisis y verificación

Desde esta carpeta:

```powershell
& .\.venv\Scripts\python.exe scripts\prepare_data.py
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe scripts\build_report.py
```

El último comando utiliza las capturas reales conservadas en `output/screenshots`. No las fabrica. El PDF es `output/Informe_Atlas_Meteoritos.pdf`. Las capturas corresponden a una sesión de prueba y pueden mostrar una selección diferente de la sesión actual.

`prepare_data.py` normalmente lee el CSV local. Su opción `--download` solicita una nueva copia de la fuente y cambia el archivo de trabajo, por lo que conviene conservar la copia histórica antes de utilizarla. La app nunca vuelve a descargar los datos al iniciar. `fetch_assets.py` es opcional y no se necesita para usar la entrega.

Las pruebas automáticas y el recorrido manual del navegador se documentan en `docs/pruebas_datos.md` y `docs/verificacion_navegador.md`.

## Pendientes académicos

Este borrador no sustituye la entrega colaborativa. Faltan integrantes, carnés, roles, contribuciones y evidencia real de uso de Git. La guía consultada imprime una fecha de entrega 23/11/2025 que debe confirmarse con el docente para el ciclo 2026. No se inventaron esos datos ni se modificó el repositorio del equipo.

## Dos experiencias disponibles

- [Expedición ilustrada](https://lucky-gauss.github.io/atlas-meteoritos-shiny/)
- [Atlas clásico](https://lucky-gauss.github.io/atlas-meteoritos-shiny/clasico/)

El rediseño, los recursos originales y la verificación están documentados en `docs/rediseno.md`. La versión clásica se conserva desde un commit fijo. El exportador necesita el historial de Git para reconstruir ambas versiones.
