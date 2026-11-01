"""Atlas de meteoritos. Aplicación local con Shiny Core y gráficos Plotly."""
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go
# La importación explícita permite que Shinylive detecte Plotly al exportar.
from shiny import App, reactive, render, ui, req

from atlas.filtering import select_records, export_frame
from atlas.charts import mass_histogram, timeline, class_bars, mass_boxes

ROOT = Path(__file__).parent
DATA = pd.read_csv(ROOT / 'data/processed/meteorites.csv')
for flag in ['map_valid', 'year_valid']:
    if DATA[flag].dtype != bool:
        DATA[flag] = DATA[flag].astype(str).str.lower().eq('true')
CLASSES = sorted(DATA['recclass'].dropna().unique())
CLASS_LABELS = {value: value if value == value.strip() else value.strip() + ' · espacio final'
                for value in CLASSES}
YEAR_MIN = int(DATA.loc[DATA.year_valid, 'year'].min())
YEAR_MAX = int(DATA.loc[DATA.year_valid, 'year'].max())
MASS_MAX = float(DATA.mass_g.max())


def number(value, digits=0):
    if pd.isna(value):
        return 'Sin datos'
    return f'{value:,.{digits}f}'.replace(',', ' ').replace('.', ',')


def eyebrow(text):
    return ui.div(text, class_='eyebrow')


def chart_panel(tag, title, explanation, chart_id, controls=None, wide=False):
    return ui.tags.section(
        ui.div(ui.div(eyebrow(tag), ui.h3(title)), controls, class_='panel-heading'),
        ui.p(explanation, class_='panel-intro'),
        ui.div(id=chart_id, class_='plot', role='img', **{'aria-label': title}),
        class_='panel chart-panel' + (' wide' if wide else ''),
    )


app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.meta(name='viewport', content='width=device-width, initial-scale=1'),
        ui.tags.link(rel='stylesheet', href='vendor/leaflet.css'),
        ui.tags.link(rel='stylesheet', href='atlas.css'),
        ui.tags.script(src='vendor/leaflet.js', defer=True),
        ui.tags.script(src='vendor/plotly.min.js', defer=True),
        ui.tags.script(src='vendor/plotly-locale-es.js', defer=True),
        ui.tags.script(src='atlas.js', defer=True),
    ),
    ui.tags.a('Saltar al contenido', href='#main-content', class_='skip-link'),
    ui.tags.header(
        ui.div(ui.span('✦', class_='brand-icon', **{'aria-hidden': 'true'}),
               ui.div(ui.strong('ATLAS'), ui.span('DE METEORITOS')), class_='brand'),
        ui.tags.nav(
            *[ui.tags.button(label, type='button', class_='nav-item' + (' active' if i == 0 else ''),
                             **{'data-page': page, 'aria-pressed': 'true' if i == 0 else 'false'})
              for i, (page, label) in enumerate([('explorer', 'Explorar'), ('analysis', 'Análisis'),
                                                ('catalogue', 'Catálogo'), ('about', 'Los datos')])],
            **{'aria-label': 'Navegación principal'}),
        ui.div(ui.span(class_='status-dot'), 'ATLAS INTERACTIVO', class_='local-badge'),
        class_='topbar',
    ),
    ui.div(
        ui.tags.aside(
            ui.tags.details(
                ui.tags.summary('Filtros de exploración', class_='filter-title'),
                ui.div(
                    ui.p('Una selección, todas las vistas.', class_='muted small'),
                    ui.input_text('search', 'Buscar meteorito', placeholder='Nombre, por ejemplo Allende'),
                    ui.input_slider('years', 'Año del catálogo', min=YEAR_MIN, max=YEAR_MAX,
                                    value=(YEAR_MIN, YEAR_MAX), sep='', step=1),
                    ui.div(ui.input_action_button('all_years', 'Todo'),
                           ui.input_action_button('modern', 'Desde 1900'), class_='preset-row'),
                    ui.input_checkbox('unknown_year', 'Incluir año ausente o anómalo', True),
                    ui.div('CONDICIÓN DEL REGISTRO', class_='filter-section'),
                    ui.input_checkbox_group('condition', None,
                        choices={'Found': 'Hallazgo', 'Fell': 'Caída observada'}, selected=['Found', 'Fell']),
                    ui.div('MASA EN GRAMOS', class_='filter-section'),
                    ui.div(ui.input_numeric('mass_min', 'Mínima', value=0, min=0, max=MASS_MAX),
                           ui.input_numeric('mass_max', 'Máxima', value=MASS_MAX, min=0, max=MASS_MAX),
                           class_='mass-inputs'),
                    ui.input_checkbox('unknown_mass', 'Incluir masa no informada', True),
                    ui.input_checkbox('zero_mass', 'Incluir masa registrada como cero', True),
                    ui.input_selectize('classes', 'Clasificación', choices=CLASS_LABELS, multiple=True,
                                       options={'placeholder': 'Todas las clases', 'plugins': ['remove_button']}),
                    ui.input_select('geography', 'Disponibilidad de ubicación',
                                    {'all': 'Todos los registros', 'valid': 'Ubicación utilizable',
                                     'missing': 'Sin ubicación utilizable'}),
                    ui.input_action_button('reset', '↺  Restablecer filtros', class_='reset-btn'),
                    ui.p('Los valores desconocidos se conservan cuando sus casillas están activas.', class_='small muted'),
                    class_='filter-body'),
                open=True),
            ui.div(ui.span('01 / ARCHIVO TERRESTRE'),
                   ui.p('Fragmentos del espacio.\nHistorias conservadas en la Tierra.'), class_='sidebar-foot'),
            class_='sidebar'),
        ui.tags.main(
            ui.div(ui.div(eyebrow('EXPLORACIÓN · CIENCIA · DESCUBRIMIENTO'),
                         ui.h1('Un universo de', ui.br(), ui.span('huellas en la Tierra.')),
                         ui.p('Explorá los meteoritos del catálogo de NASA y descubrí las historias que cuentan su masa, su ubicación y su registro.', class_='hero-description')),
                   ui.div(ui.div(class_='orbit orbit-one'), ui.div(class_='orbit orbit-two'),
                          ui.div(class_='planet'), ui.span('45 716', class_='orbit-count'),
                          ui.span('REGISTROS · MUCHAS HISTORIAS', class_='orbit-label'),
                          class_='hero-art', **{'aria-hidden': 'true'}), class_='hero'),
            ui.output_ui('metrics'),
            ui.div(ui.div(ui.span(class_='selection-dot'), ui.output_text('selection_text', inline=True)),
                   ui.div('Actualizando vistas…', id='busy-label', role='status'),
                   class_='selection-bar', **{'aria-live': 'polite'}),
            ui.output_ui('filter_warning'),
            ui.tags.section(
                ui.tags.section(
                    ui.div(ui.div(eyebrow('01 / GEOGRAFÍA DEL CATÁLOGO'), ui.h2('Cada punto, una historia.')),
                           ui.input_radio_buttons('map_mode', None,
                               {'points': 'Meteoritos', 'concentration': 'Concentración'}, inline=True),
                           class_='panel-heading'),
                    ui.div(ui.span('●', class_='teal'), ' Hallazgo', ui.span('●', class_='amber'), ' Caída observada',
                           ui.span('El tamaño individual representa la masa en escala logarítmica.', class_='legend-note'),
                           class_='map-legend'),
                    ui.div(ui.div(id='atlas-map', role='region', **{'aria-label': 'Mapa mundial de registros de meteoritos'}),
                           ui.div('Preparando el atlas…', id='map-empty', class_='map-empty'),
                           class_='map-wrap'),
                    ui.div(ui.output_text('map_note'), ui.tags.button('↗ Vista mundial', id='world-view', type='button'), class_='map-footer'),
                    class_='panel map-panel'),
                ui.div(
                    ui.tags.article(eyebrow('LEER EL MAPA'), ui.h3('Un mapa de registros, no de impactos.'),
                               ui.p('Las concentraciones reflejan también dónde se busca, se conserva y se documenta. La ausencia de puntos no implica ausencia de meteoritos.'), class_='insight-card'),
                    ui.tags.article(eyebrow('TU SELECCIÓN'), ui.output_ui('selection_insight'), class_='insight-card accent'),
                    class_='insights'),
                id='page-explorer', class_='atlas-page active'),
            ui.tags.section(
                ui.div(eyebrow('02 / PATRONES Y CONTRASTES'), ui.h2('Mirar más allá del punto.'),
                       ui.p('Cada gráfico responde una pregunta distinta. Zoom y leyendas solo modifican su propia vista. Los filtros de la izquierda actualizan todo el atlas.'), class_='section-intro'),
                ui.div(
                    chart_panel('DISTRIBUCIÓN', '¿Cuánto pesan los meteoritos?',
                                'Frecuencia por intervalo de masa. La escala logarítmica permite comparar órdenes de magnitud y excluye masas cero o ausentes.',
                                'mass-chart', ui.input_radio_buttons('mass_scale', None, {'log': 'Logarítmica', 'linear': 'Original'}, inline=True)),
                    chart_panel('COMPOSICIÓN', '¿Qué clases predominan?',
                                'Las 12 clases más frecuentes de la selección, separadas por condición. Las demás clases siguen incluidas en las otras vistas.', 'classes-chart'),
                    chart_panel('REGISTRO TEMPORAL', '¿Cómo cambia el catálogo en el tiempo?',
                                'El año corresponde a la caída observada o al hallazgo según la condición. No representa necesariamente el año del impacto. Arrastrá para acercar y usá el selector inferior.',
                                'time-chart', ui.input_radio_buttons('time_bin', None, {'decade': 'Por década', 'year': 'Por año'}, inline=True), wide=True),
                    chart_panel('VARIABILIDAD', '¿Cómo se comparan las masas?',
                                'Cajas con mediana y 50 % central. Bigotes hasta 1,5 rangos intercuartílicos, calculados en gramos. Eje logarítmico, solo masas positivas. Los atípicos se cuentan al pasar el cursor.',
                                'boxes-chart', ui.input_radio_buttons('box_group', None, {'fall': 'Por condición', 'recclass': 'Por clase'}, inline=True), wide=True),
                    class_='charts-grid'),
                id='page-analysis', class_='atlas-page'),
            ui.tags.section(
                ui.div(ui.div(eyebrow('03 / ARCHIVO EXPLORABLE'), ui.h2('Las historias, registro a registro.'),
                              ui.p('Buscá nombres con el filtro general. Ordená las columnas con sus encabezados. El CSV contiene todos los registros de la selección y las banderas de calidad.')),
                       ui.download_button('download_csv', '↓ Descargar CSV', class_='download-btn'), class_='section-intro table-heading'),
                ui.div(ui.output_data_frame('catalogue'), class_='panel table-panel'),
                id='page-catalogue', class_='atlas-page'),
            ui.tags.section(
                ui.div(eyebrow('04 / FUENTES Y CRITERIO'), ui.h2('La ciencia empieza por los datos.'),
                       ui.p('Un catálogo histórico y público para practicar análisis exploratorio, programación reactiva y lectura crítica de evidencia.'), class_='section-intro'),
                ui.output_ui('about_data'), id='page-about', class_='atlas-page'),
            ui.tags.footer(ui.span('ATLAS DE METEORITOS'), ui.span('NASA · The Meteoritical Society'),
                           ui.span('Borrador universitario · 2026'), class_='footer'),
            id='main-content'),
        class_='app-shell'),
    title='Atlas de meteoritos', lang='es',
)


def server(input, output, session):
    @reactive.calc
    def selected():
        low = input.mass_min() if input.mass_min() is not None else 0
        high = input.mass_max() if input.mass_max() is not None else MASS_MAX
        return select_records(DATA, input.years(), (low, high), input.condition(),
                              input.classes(), input.search(), input.unknown_year(),
                              input.unknown_mass(), input.zero_mass(), input.geography())

    @reactive.effect
    @reactive.event(input.reset)
    def reset():
        ui.update_text('search', value='')
        ui.update_slider('years', value=(YEAR_MIN, YEAR_MAX))
        ui.update_checkbox_group('condition', selected=['Found', 'Fell'])
        ui.update_numeric('mass_min', value=0)
        ui.update_numeric('mass_max', value=MASS_MAX)
        ui.update_selectize('classes', selected=[])
        ui.update_select('geography', selected='all')
        for key in ['unknown_year', 'unknown_mass', 'zero_mass']:
            ui.update_checkbox(key, value=True)
        ui.update_radio_buttons('mass_scale', selected='log')
        ui.update_radio_buttons('time_bin', selected='decade')
        ui.update_radio_buttons('box_group', selected='fall')
        ui.update_radio_buttons('map_mode', selected='points')

    @reactive.effect
    @reactive.event(input.modern)
    def modern():
        ui.update_slider('years', value=(1900, YEAR_MAX))

    @reactive.effect
    @reactive.event(input.all_years)
    def all_years():
        ui.update_slider('years', value=(YEAR_MIN, YEAR_MAX))

    @render.ui
    def metrics():
        df = selected()
        values = [
            ('REGISTROS SELECCIONADOS', number(len(df)), f'de {number(len(DATA))} en el archivo', '01'),
            ('UBICACIONES UTILIZABLES', number(df.map_valid.sum()), 'coordenadas válidas y distintas de 0, 0', '02'),
            ('MASA MEDIANA', number(df.mass_g.median(), 1) + ' g' if df.mass_g.notna().any() else 'Sin datos', 'masa conocida, incluidos los ceros', '03'),
            ('CLASES REPRESENTADAS', number(df.recclass.nunique()), 'clasificación del catálogo original', '04'),
        ]
        return ui.div(*[ui.tags.article(ui.div(ui.span(label), ui.span(index), class_='metric-label'),
                                    ui.strong(value), ui.p(note), class_='metric')
                        for label, value, note, index in values], class_='metrics')

    @render.text
    def selection_text():
        df = selected()
        return f'{number(len(df))} registros · {number(len(df) / len(DATA) * 100, 1)} % del catálogo'

    @render.ui
    def filter_warning():
        if (input.mass_min() or 0) > (input.mass_max() if input.mass_max() is not None else MASS_MAX):
            return ui.div('La masa mínima supera la máxima. Corregí el rango para volver a explorar.', class_='empty-banner', role='alert')
        if selected().empty:
            return ui.div('No hay registros con esta combinación. Ampliá los filtros o usá Restablecer filtros.', class_='empty-banner', role='status')

    @render.text
    def map_note():
        df = selected()
        return f'{number(df.map_valid.sum())} registros en el mapa · {number((~df.map_valid).sum())} sin ubicación utilizable. Agrupación visual al cambiar el zoom.'

    @render.ui
    def selection_insight():
        df = selected()
        if df.empty:
            return ui.TagList(ui.h3('Una nueva búsqueda.'), ui.p('Ampliá la selección para descubrir más registros.'))
        observed = df.fall.eq('Fell').sum()
        return ui.TagList(ui.h3(f'{number(observed / len(df) * 100, 1)} % con caída observada.'),
                         ui.p(f'{number(observed)} caídas observadas y {number(df.fall.eq("Found").sum())} hallazgos. La condición distingue una observación de la caída de un descubrimiento posterior.'))

    @reactive.effect
    async def update_map():
        req(input.client_ready())
        df = selected().loc[lambda x: x.map_valid, ['name', 'recclass', 'mass_g', 'fall', 'year', 'lat', 'lon']]
        rows = json.loads(df.to_json(orient='values', double_precision=6))
        await session.send_custom_message('atlas-map', {'rows': rows, 'mode': input.map_mode()})

    @reactive.effect
    async def update_charts():
        req(input.client_ready())
        df = selected()
        figures = {
            'mass-chart': mass_histogram(df, input.mass_scale()),
            'classes-chart': class_bars(df),
            'time-chart': timeline(df, input.time_bin()),
            'boxes-chart': mass_boxes(df, input.box_group()),
        }
        await session.send_custom_message('atlas-charts', {
            key: json.loads(fig.to_json()) for key, fig in figures.items()
        })

    @render.data_frame
    def catalogue():
        frame = export_frame(selected())
        frame['Año del catálogo'] = frame['Año del catálogo'].astype('Int64')
        for column in ['Ubicación utilizable', 'Año utilizable']:
            frame[column] = frame[column].map({True: 'Sí', False: 'No'})
        return render.DataGrid(frame, height='560px', width='100%', filters=False, summary=False)

    @render.download(filename='atlas_meteoritos_seleccion.csv', media_type='text/csv;charset=utf-8')
    def download_csv():
        yield '\ufeff' + export_frame(selected()).to_csv(index=False)

    @render.ui
    def about_data():
        quality_path = ROOT / 'docs/calidad_datos.md'
        quality = quality_path.read_text(encoding='utf-8') if quality_path.exists() else 'Consultá la documentación local en la carpeta docs.'
        return ui.TagList(
            ui.div(
                ui.tags.article(eyebrow('FUENTE ORIGINAL'), ui.h3('Meteorite Landings'),
                           ui.p('Catálogo de The Meteoritical Society difundido por NASA. Copia local descargada el 31 de octubre de 2026, con 45 716 filas y 10 columnas originales.'),
                           ui.tags.a('Consultar el catálogo de NASA ↗', href='https://data.nasa.gov/dataset/meteorite-landings', target='_blank', rel='noopener'),
                           ui.p('Acceso público. El portal de NASA no especifica una licencia. No se atribuye una licencia de reutilización no declarada.'), class_='insight-card'),
                ui.tags.article(eyebrow('RESULTADOS GENERALES'), ui.h3('Un archivo dominado por hallazgos.'),
                           ui.p(f'En el archivo completo, {number(DATA.fall.eq("Found").mean()*100, 1)} % son hallazgos. La masa mediana es {number(DATA.mass_g.median(), 1)} g y la mayor masa registrada alcanza {number(DATA.mass_g.max()/1000000, 0)} toneladas.'),
                           ui.p('Estos resultados describen el archivo completo. Los indicadores superiores y la sección Análisis describen la selección activa.'), class_='insight-card'), class_='insights'),
            ui.tags.article(eyebrow('PREGUNTAS DE EXPLORACIÓN'), ui.h3('Cuatro formas de interrogar el archivo.'),
                       ui.tags.ol(ui.tags.li('¿Cómo se distribuyen espacialmente los registros con ubicación utilizable?'),
                                  ui.tags.li('¿Cómo se distribuyen las masas y cómo varían por condición o clase?'),
                                  ui.tags.li('¿Cómo cambian los registros de caída y hallazgo a través del tiempo?'),
                                  ui.tags.li('¿Cuáles son las clasificaciones más frecuentes?')), class_='panel prose'),
            ui.tags.article(ui.markdown(quality), class_='panel prose'),
            ui.tags.article(ui.h3('Alcance académico'),
                       ui.p('Borrador local e independiente en Shiny para Python. Quedan pendientes los nombres, carnés, roles y contribuciones del equipo, la evidencia real de trabajo con Git y la fecha de entrega confirmada por el docente.'),
                       ui.p('La aplicación inicia desde archivos locales. La cartografía Natural Earth se usa solo como referencia visual y no asigna países a los meteoritos.'), class_='panel prose'),
        )


app = App(app_ui, server, static_assets=ROOT / 'www')

