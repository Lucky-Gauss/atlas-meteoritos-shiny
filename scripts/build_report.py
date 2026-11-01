"""Genera el informe académico a partir de los datos preparados y capturas reales."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from html import escape
from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SCREENSHOTS = OUT / "screenshots"
NAVY = colors.HexColor("#101e34")
TEAL = colors.HexColor("#167b78")
INK = colors.HexColor("#223249")
MUTED = colors.HexColor("#57697b")
PALE = colors.HexColor("#edf5f6")
RULE = colors.HexColor("#d8e3e8")
W, H = A4
CONTENT_W = W - 40 * mm


def fmt(value, digits=0):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return "sin dato"
    return f"{value:,.{digits}f}".replace(",", "\u2009").replace(".", ",")


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def truth(value):
    return str(value).lower() in {"true", "1", "1.0"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_records():
    candidates = sorted((ROOT / "data" / "processed").glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("Falta el CSV preparado. Ejecute scripts/prepare_data.py")
    with candidates[0].open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def register_fonts():
    fonts = Path("C:/Windows/Fonts")
    regular = fonts / "arial.ttf"
    bold = fonts / "arialbd.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Atlas", str(regular)))
        pdfmetrics.registerFont(TTFont("AtlasBold", str(bold)))
        pdfmetrics.registerFontFamily("Atlas", normal="Atlas", bold="AtlasBold", italic="Atlas", boldItalic="AtlasBold")
        return "Atlas", "AtlasBold"
    return "Helvetica", "Helvetica-Bold"


FONT, BOLD = register_fonts()
STYLES = {
    "body": ParagraphStyle("body", fontName=FONT, fontSize=10.1, leading=15.2, textColor=INK, spaceAfter=9),
    "small": ParagraphStyle("small", fontName=FONT, fontSize=8.5, leading=12.5, textColor=MUTED, spaceAfter=7),
    "caption": ParagraphStyle("caption", fontName=FONT, fontSize=8.2, leading=11.5, textColor=MUTED, spaceBefore=6, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=25, leading=29, textColor=NAVY, spaceAfter=16),
    "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=13, leading=17, textColor=TEAL, spaceBefore=11, spaceAfter=7),
    "eyebrow": ParagraphStyle("eyebrow", fontName=BOLD, fontSize=8.5, leading=12, textColor=TEAL, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName=FONT, fontSize=8.6, leading=12, textColor=INK),
    "th": ParagraphStyle("th", fontName=BOLD, fontSize=8.4, leading=11.5, textColor=colors.white),
    "quote": ParagraphStyle("quote", fontName=BOLD, fontSize=12, leading=17, textColor=TEAL, spaceAfter=12),
}


def p(text, style="body"):
    return Paragraph(text, STYLES[style])


def heading(number_, title, subtitle):
    return [p(f"{number_:02d} / ATLAS DE METEORITOS", "eyebrow"), p(title, "h1"), p(subtitle)]


def table(headers, rows, widths):
    converted = [[p(escape(str(h)), "th") for h in headers]]
    converted += [[p(escape(str(cell)), "cell") for cell in row] for row in rows]
    result = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, RULE),
    ]))
    return result


def screenshot(name, caption, max_height=86 * mm, crop=None):
    path = SCREENSHOTS / name
    if not path.exists():
        alternatives = [path.with_suffix(".jpg"), path.with_suffix(".jpeg")]
        path = next((candidate for candidate in alternatives if candidate.exists()), path)
    if not path.exists():
        raise FileNotFoundError(f"Falta la captura real {path}")
    with PILImage.open(path) as im:
        if crop is not None:
            bounds = tuple(round(value * (im.width if i % 2 == 0 else im.height)) for i, value in enumerate(crop))
            im = im.crop(bounds)
        width, height = im.size
        buffer = BytesIO()
        im.save(buffer, format="PNG")
        buffer.seek(0)
    scale = min(CONTENT_W / width, max_height / height)
    image = Image(buffer, width=width * scale, height=height * scale)
    image.hAlign = "LEFT"
    return [image, p(caption, "caption")]


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 8 * mm, W, 8 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(RULE)
    canvas.line(20 * mm, 17 * mm, W - 20 * mm, 17 * mm)
    canvas.setFont(FONT, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 12 * mm, "ATLAS DE METEORITOS  /  Borrador local  /  31.10.2026")
    canvas.drawRightString(W - 20 * mm, 12 * mm, f"{doc.page:02d}")
    canvas.restoreState()


class Orbit(Flowable):
    def __init__(self, width, height=55 * mm):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.width, self.height, 12, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#27425b"))
        cx, cy = self.width * 0.74, self.height * 0.50
        for radius in [23, 43, 63]:
            c.ellipse(cx - radius, cy - radius * 0.50, cx + radius, cy + radius * 0.50, stroke=1, fill=0)
        c.setFillColor(colors.HexColor("#55ddcf"))
        c.circle(cx + 34, cy + 14, 4, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#ffbc75"))
        c.circle(cx - 56, cy + 14, 2.7, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(BOLD, 13)
        c.drawString(18, self.height - 31, "Una historia escrita")
        c.drawString(18, self.height - 50, "en fragmentos")
        c.setFillColor(colors.HexColor("#b6c7d8"))
        c.setFont(FONT, 8.5)
        c.drawString(18, 23, "GEOGRAFÍA  /  MASA  /  TIEMPO  /  CLASIFICACIÓN")


def main():
    records = load_records()
    provenance = read_json(ROOT / "data" / "provenance.json")
    n = len(records)
    masses = [number(r.get("mass_g")) for r in records]
    known_mass = [m for m in masses if m is not None]
    positive = [m for m in known_mass if m > 0]
    counts = Counter(r["fall"] for r in records)
    classes = Counter(r["recclass"] for r in records)
    valid_map = [r for r in records if truth(r.get("map_valid"))]
    valid_year = [int(float(r["year"])) for r in records if truth(r.get("year_valid")) and number(r.get("year")) is not None]
    decades = Counter((y // 10) * 10 for y in valid_year)
    zeros = sum(m == 0 for m in known_mass)
    missing_year = sum(number(r.get("year")) is None for r in records)
    invalid_year = sum(number(r.get("year")) is not None and not truth(r.get("year_valid")) for r in records)
    missing_coords = sum(number(r.get("lat")) is None or number(r.get("lon")) is None for r in records)
    zero_coords = sum(number(r.get("lat")) == 0 and number(r.get("lon")) == 0 for r in records)
    out_coords = sum(number(r.get("lat")) is not None and number(r.get("lon")) is not None and (abs(number(r["lat"])) > 90 or abs(number(r["lon"])) > 180) for r in records)
    max_record = max((r for r in records if number(r.get("mass_g")) is not None), key=lambda r: float(r["mass_g"]))
    group_medians = {g: statistics.median([float(r["mass_g"]) for r in records if r["fall"] == g and number(r.get("mass_g")) is not None and float(r["mass_g"]) > 0]) for g in ["Fell", "Found"]}
    top_class, top_count = classes.most_common(1)[0]
    top_decade, decade_count = decades.most_common(1)[0]
    antarctic = sum(float(r["lat"]) < -60 for r in valid_map)

    story = []
    story += [Spacer(1, 5 * mm), p("PROGRAMACIÓN PARA ESTADÍSTICA II  /  PROYECTO DE REFERENCIA", "eyebrow"),
              p("Atlas de<br/>meteoritos", "h1"),
              p("Exploración interactiva de un catálogo público con Shiny para Python", "quote"),
              Spacer(1, 3 * mm), Orbit(CONTENT_W, 45 * mm), Spacer(1, 7 * mm)]
    story += [p("Alcance del documento", "h2"),
              p(f"Este borrador local acompaña una aplicación para explorar <b>{fmt(n)} registros</b> de Meteorite Landings. Integra ubicación, masa, clasificación y año de catálogo como referencia de diseño, análisis y programación para el proyecto del equipo."),
              p("El catálogo describe meteoritos documentados. No es un censo de todos los impactos del planeta ni una muestra aleatoria de los meteoritos que llegan a la Tierra."),
              table(["Estado", "Detalle"], [["Integrantes y carnés", "Pendientes de completar por el equipo"], ["Docente, grupo y roles", "Pendientes de confirmar"], ["Repositorio y contribuciones", "No se generan evidencias de Git en este borrador"]], [40 * mm, CONTENT_W - 40 * mm]),
              Spacer(1, 4 * mm), p("El trabajo permanece separado del repositorio del equipo. Las conclusiones numéricas de este informe describen el conjunto completo preparado, no una selección temporal del explorador.", "small"), PageBreak()]

    story += heading(1, "Preguntas y fuente", "Un catálogo que permite conectar estadística descriptiva, cartografía y desarrollo reactivo.")
    story += [p("Justificación", "h2"), p("Meteorite Landings combina variables numéricas, temporales y categóricas, con suficiente tamaño para discutir distribuciones asimétricas, valores faltantes y sesgos de observación. La aplicación facilita contrastar patrones y reconocer los límites de una base histórica de registros."),
              table(["Pregunta", "Vista que la responde"], [["¿Dónde se concentran los registros con ubicación utilizable?", "Mapa con agrupación de puntos y vista de concentración"], ["¿Cómo se distribuye la masa y cómo cambia entre condiciones o clases?", "Histograma y diagramas de caja"], ["¿Cómo varían los registros según el año consignado?", "Serie temporal con zoom y selección de períodos"], ["¿Qué clasificaciones son más frecuentes?", "Barras de clases con conteos y comparación interactiva"]], [98 * mm, CONTENT_W - 98 * mm]),
              p("Fuente y trazabilidad", "h2"),
              p("Fuente original: <b>The Meteoritical Society</b>. NASA publica la ficha <i>Meteorite Landings</i>. El tipo de nombre <i>Relict</i> señala objetos originalmente meteoríticos muy alterados por meteorización. Esos registros se conservan."),
              p('<link href="https://data.nasa.gov/dataset/meteorite-landings" color="#167b78">Ficha oficial de NASA: data.nasa.gov/dataset/meteorite-landings</link>', "small"),
              p(f"Se descargó el CSV oficial de NASA el <b>{provenance['download_date']}</b>. Contiene <b>{fmt(provenance['rows'])} filas y {provenance['columns']} columnas</b>. La ficha describe también una versión anterior de 34 513 filas, distinta del archivo utilizado.", "small"),
              p(f"Archivo exacto: <link href=\"{provenance['file_url']}\" color=\"#167b78\">{provenance['file_url']}</link>", "small"),
              p("La consulta de descarga añadió <b>?download=20261031</b>. La ficha indica <b>License not specified</b>, por lo que no se presupone una licencia abierta específica. La solicitud exacta y el hash SHA-256 están en <b>data/provenance.json</b>.", "small"),
              p("Definiciones que cambian la interpretación", "h2"),
              p("<b>Caída observada (Fell)</b> identifica meteoritos cuya caída fue observada. <b>Hallazgo (Found)</b> identifica recuperaciones posteriores. El año de catálogo puede corresponder a la caída o al hallazgo según la condición. No debe interpretarse como el año de impacto conocido de todos los registros."), PageBreak()]

    story += heading(2, "Preparación y calidad", "Se conservan las filas originales y se evalúa la elegibilidad de cada variable según la vista.")
    quality_rows = [
        ["Filas del conjunto preparado", fmt(n), "Se mantiene el universo de registros"],
        ["Masa ausente", fmt(n - len(known_mass)), "Excluida de cálculos de masa"],
        ["Masa igual a cero", fmt(zeros), "Se conserva, se omite en logaritmos"],
        ["Año ausente", fmt(missing_year), "Sin posición en la evolución temporal"],
        ["Año marcado como anómalo", fmt(invalid_year), "Se conserva, se omite del análisis temporal"],
        ["Coordenadas incompletas", fmt(missing_coords), "Se excluyen solo del mapa"],
        ["Par de coordenadas 0, 0", fmt(zero_coords), "Ubicación no confiable para cartografía"],
        ["Coordenadas fuera de rango terrestre", fmt(out_coords), "Meridiani Planum, hallazgo en Marte"],
        ["Registros elegibles para el mapa", fmt(len(valid_map)), "Disponibles con los filtros generales"],
        ["Filas completas o ID duplicados", "0", "No se elimina ningún registro"],
    ]
    story += [table(["Revisión", "Registros", "Tratamiento"], quality_rows, [65 * mm, 26 * mm, CONTENT_W - 91 * mm]),
              Spacer(1, 5 * mm), p("Reglas de conservación", "h2"),
              p("No se imputan masas, años ni coordenadas y no hay masas negativas. El año 2101 se marca como anómalo. <b>Meridiani Planum</b> es un hallazgo en Marte cuya longitud queda fuera del rango terrestre. Se conserva en los análisis del catálogo y se excluye del mapa terrestre, sin corregir sus coordenadas."),
              p("Los filtros especifican cómo tratar los valores faltantes. El tamaño de la selección general puede diferir del número representado en una vista cuando esta requiere una variable utilizable. Los gráficos y sus notas deben indicar esas exclusiones."),
              p("El procedimiento reproducible y las comprobaciones se detallan en <b>scripts/prepare_data.py</b> y <b>docs/calidad_datos.md</b>. El origen marciano se verifica en la <link href=\"https://www.lpi.usra.edu/meteor/metbull.php?code=32789\" color=\"#167b78\">ficha de Meridiani Planum del Meteoritical Bulletin</link>. Las banderas de calidad no garantizan ausencia de otros errores.", "small"),
              p("Las masas se expresan en gramos. Los ceros no tienen logaritmo definido y se excluyen solo de las representaciones logarítmicas.", "small"), PageBreak()]

    story += heading(3, "Geografía documentada", "La distribución de registros refleja búsqueda, conservación y documentación además de procesos naturales.")
    story += screenshot("desktop.png", "Figura 1. Detalle de la captura real del explorador. El mapa muestra los 32 186 registros con coordenadas utilizables del conjunto completo. La imagen original se conserva en output/screenshots.", 92 * mm, crop=(0.215, 0.395, 0.987, 0.825))
    story += [p("Resultados del conjunto completo", "h2"), p(f"Hay <b>{fmt(len(valid_map))} registros cartografiables</b>, un {fmt(100 * len(valid_map) / n, 1)} % del catálogo preparado. De ellos, {fmt(antarctic)} presentan latitud inferior a 60° S, lo que equivale al {fmt(100 * antarctic / len(valid_map), 1)} % de los registros cartografiables. Esta es una descripción por coordenadas, no una asignación de país."),
              p(f"Los hallazgos suman <b>{fmt(counts['Found'])}</b> registros ({fmt(100 * counts['Found'] / n, 1)} %), frente a <b>{fmt(counts['Fell'])}</b> caídas observadas ({fmt(100 * counts['Fell'] / n, 1)} %). Las condiciones representan mecanismos de documentación distintos."),
              p("Interpretación", "h2"), p("Una concentración visible no prueba una mayor tasa de impactos. Las campañas de búsqueda, la preservación en ciertos ambientes y el acceso a los lugares condicionan qué fragmentos entran al catálogo. El agrupamiento de puntos mejora la navegación, pero no modifica los conteos del conjunto."),
              p("La navegación y el zoom del mapa sirven para explorar posiciones. Las ventanas emergentes conservan nombre, masa, clase, condición y año de catálogo, con las ausencias identificadas en español. El fondo cartográfico local procede de <b>Natural Earth, versión 5.1.2, escala 1:110 millones</b>, de dominio público. Se usa para orientación, sin asignar países a los meteoritos.", "small"), PageBreak()]

    story += heading(4, "Masas y clasificaciones", "La amplitud de las masas exige separar la forma de la distribución de sus valores extremos.")
    story += screenshot("analysis.png", "Figura 2. Detalle de la captura real del análisis. Histograma logarítmico y barras por clasificación para el conjunto completo. Los colores distinguen la condición del registro.", 78 * mm, crop=(0.215, 0.295, 0.987, 0.51))
    story += [p("Resultados del conjunto completo", "h2"),
              p(f"Entre las {fmt(len(positive))} masas positivas, la mediana es <b>{fmt(statistics.median(positive), 2)} g</b> y la media es <b>{fmt(statistics.mean(positive), 2)} g</b>. La diferencia es compatible con una distribución muy asimétrica, influida por los registros de mayor masa."),
              p(f"El valor máximo corresponde a <b>{escape(max_record['name'])}</b>, con <b>{fmt(float(max_record['mass_g']))} g</b>. Entre masas positivas, la mediana de caídas observadas es {fmt(group_medians['Fell'], 2)} g y la de hallazgos es {fmt(group_medians['Found'], 2)} g. Estas diferencias son descriptivas y no demuestran un efecto causal de la condición."),
              p(f"La etiqueta de clasificación más frecuente es <b>{escape(top_class)}</b>, con {fmt(top_count)} registros, un {fmt(100 * top_count / n, 1)} % del catálogo. El ranking de clases muestra las categorías más frecuentes y mantiene el denominador del conjunto seleccionado."),
              p("Lectura de los gráficos", "h2"), p("El histograma representa frecuencias en intervalos de masa. La escala original facilita interpretar gramos y la logarítmica revela la distribución de los registros pequeños. Los diagramas de caja resumen mediana y dispersión. Una clasificación poco frecuente puede ofrecer estimaciones inestables, por lo que conviene revisar su tamaño muestral."), PageBreak()]

    story += heading(5, "Tiempo y exploración", "La cronología se interpreta como historia del registro, no como una serie global de impactos.")
    story += [p(f"Los {fmt(len(valid_year))} registros con año elegible abarcan de <b>{min(valid_year)}</b> a <b>{max(valid_year)}</b>. La década con más registros es <b>{top_decade}-{top_decade + 9}</b>, con {fmt(decade_count)} registros. La cobertura y la frecuencia cambian con los procedimientos de búsqueda y documentación."),
              p("La serie temporal permite ampliar intervalos y consultar sus conteos. La selección de período en los filtros generales actualiza las vistas. La interacción local de zoom cambia el detalle visible del gráfico y no debe confundirse con una nueva selección global."),
              p("Exploración tabular", "h2")]
    story += screenshot("table.png", "Figura 3. Detalle de la captura real del catálogo con sus primeras filas. La búsqueda y el ordenamiento permiten inspeccionar registros antes de exportar la selección.", 80 * mm, crop=(0.215, 0.4, 0.987, 0.735))
    story += [p("Conclusiones preliminares", "h2"), p("El conjunto permite estudiar cómo se documentan los meteoritos y comparar sus características medidas. Los hallazgos dominan el catálogo, la masa presenta gran asimetría y algunas clasificaciones reúnen una proporción importante de registros. La concentración espacial y temporal no puede convertirse directamente en riesgo o probabilidad de impacto."),
              p("La aplicación favorece una lectura crítica al mantener visibles las unidades, las condiciones de registro y las exclusiones por calidad. Las conclusiones generales de este informe deben diferenciarse de los indicadores reactivos que describen cada selección.", "small"), PageBreak()]

    story += heading(6, "Reproducción y pendientes", "Un borrador local para revisar y adaptar antes de la entrega académica del equipo.")
    story += [p("Organización técnica", "h2"),
              p("La aplicación usa Shiny Core para Python. Los gráficos se construyen con Plotly y comparten una identidad visual con el mapa, las tarjetas y la tabla. Los datos se leen desde una copia local, separada del procedimiento de descarga y preparación."),
              table(["Recurso", "Finalidad"], [["README.md", "Instalación, inicio y estructura en Windows"], ["data/raw y data/processed", "Original conservado y versión preparada"], ["data/provenance.json", "Fuente, archivo, fecha, dimensiones y hash"], ["scripts/prepare_data.py", "Preparación reproducible de los datos"], ["scripts/build_report.py", "Generación de este informe con datos y capturas"], ["docs/calidad_datos.md", "Decisiones de limpieza y sus conteos"]], [66 * mm, CONTENT_W - 66 * mm]),
              p("Verificación", "h2"),
              p("Se comprobaron en navegador la carga inicial, búsqueda de Allende y su ventana, filtros de condición, año, clase y ubicación, selecciones vacías, ordenamiento de tabla, concentración y cambios de escala, agrupación temporal y cajas. El CSV descargado para L6 se validó con 8 285 filas. Pasaron 18 pruebas automatizadas."),
              p("El detalle se conserva en <b>docs/verificacion_navegador.md</b>. Las capturas son reales. Este informe no afirma que se hayan probado todas las modalidades de zoom o todos los dispositivos.", "small"),
              p("Pendientes académicos", "h2"),
              p("Completar los nombres, carnés, grupo, docente, roles y contribuciones reales de los integrantes. El documento académico solicita trabajo colaborativo y evidencias de Git. Este borrador no crea esas evidencias ni sustituye las contribuciones del equipo. La fecha impresa en las instrucciones es 23/11/2025 y debe confirmarse con el docente para el ciclo de 2026."),
              p("Limitaciones", "h2"), p("El catálogo es histórico y su disponibilidad pública no garantiza actualización ni exhaustividad. Existen registros sin variables útiles y ubicaciones que requieren exclusión cartográfica. No se estiman riesgos de impacto, tasas globales ni relaciones causales. Las condiciones de uso publicadas se transcriben en la procedencia sin atribuir una licencia que la fuente no declare."),
              Spacer(1, 1)]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "Informe_Atlas_Meteoritos.pdf"
    document = BaseDocTemplate(str(path), pagesize=A4, title="Atlas de meteoritos - Borrador local", author="Borrador académico sin autoría asignada", leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=24 * mm)
    frame = Frame(20 * mm, 24 * mm, CONTENT_W, H - 44 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates(PageTemplate(id="Atlas", frames=frame, onPage=on_page))
    document.build(story)
    print('Informe listo en output/Informe_Atlas_Meteoritos.pdf')


if __name__ == "__main__":
    main()
