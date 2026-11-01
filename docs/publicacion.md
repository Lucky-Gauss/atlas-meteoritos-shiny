# Publicación del Atlas de meteoritos

Aplicación: https://lucky-gauss.github.io/atlas-meteoritos-shiny/

Repositorio público independiente: https://github.com/Lucky-Gauss/atlas-meteoritos-shiny

Informe: https://lucky-gauss.github.io/atlas-meteoritos-shiny/Informe_Atlas_Meteoritos.pdf

## Funcionamiento

Se utiliza GitHub Pages y Shinylive. Python se ejecuta en el navegador del visitante con WebAssembly. No se requiere cuenta, instalación ni mantener encendida la computadora de desarrollo. La primera apertura descarga el motor de Python, las bibliotecas y los datos. Esa carga puede demorar según la conexión y el dispositivo.

El sitio utiliza la copia histórica de NASA incluida en el proyecto. Los filtros se procesan en cada navegador y no alteran el archivo original ni las selecciones de otros visitantes. La aplicación no contiene credenciales.

El despliegue se construye con shinylive 0.8.13. Su entorno web utiliza las versiones disponibles para Pyodide, que pueden diferir de las del entorno de Windows. La versión exportada se probó localmente antes de publicarla, incluyendo carga completa, búsqueda Allende, restablecimiento y generación de los cuatro gráficos.

## Evidencia del despliegue

GitHub Actions completó correctamente la construcción y publicación en esta ejecución:

https://github.com/Lucky-Gauss/atlas-meteoritos-shiny/actions/runs/41269155453

Commit del paquete publicado: `97c542d6087fc63ba48a0043985f3c85b154d79c`.

La publicación inicial utilizó un paquete ZIP. Ahora el repositorio conserva directamente el código en la raíz, los datos, los recursos y el informe. La carpeta local está conectada mediante Git. El workflow ejecuta `scripts/export_web.py` y publica su resultado. Los permisos se limitan a lectura del contenido y despliegue de Pages.

## Comprobación del sitio público

El 1 de noviembre de 2026 se abrió el enlace HTTPS público en el navegador integrado, sin iniciar sesión en GitHub. Se comprobó la carga de 45 716 registros, 32 186 ubicaciones y mediana de 32,6 g. El mapa agrupado se dibujó y se guardó una captura real en `output/screenshots/public.jpg`.

La búsqueda Allende produjo un registro y una masa de 2 000 000 g. Se abrió Análisis y aparecieron los cuatro gráficos con controles de Plotly. Al excluir las caídas observadas, la combinación produjo cero registros y el mensaje correspondiente. Restablecer recuperó los 45 716 registros. El PDF público respondió HTTP 200 con tipo `application/pdf`.

El motor web emitió un aviso de obsolescencia de `render.download`. La aplicación continuó funcionando. La descarga CSV fue comprobada en el servidor local, pero no se repitió en el sitio público. La descarga PNG no se confirmó. La revisión de dispositivos pequeños y las 18 pruebas de datos corresponden a la versión local y se documentan por separado.

## Mantenimiento

Editar los archivos de esta carpeta, guardar una versión con `git add .` y `git commit`, y enviarla con `git push`. Cada envío a `main` vuelve a construir y publicar. Ya no es necesario subir un ZIP. GitHub Pages sirve la última ejecución que termina correctamente.

La autorización posterior de publicar este borrador reemplaza la restricción inicial de mantenerlo local. El repositorio del equipo no fue modificado. El informe académico sigue siendo un borrador con los datos personales y evidencias de contribuciones pendientes de confirmar.
