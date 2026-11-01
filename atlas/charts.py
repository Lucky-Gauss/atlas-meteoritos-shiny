"""Gráficos del atlas con estadísticas completas y una identidad visual común.

Cada función recibe la selección global, calcula sus propios registros elegibles
y devuelve una figura Plotly. Los cambios de zoom o leyenda son locales al gráfico.

Referencias de implementación:
https://plotly.com/python/box-plots/
https://plotly.com/python/reference/box/
https://plotly.com/python/range-slider/
"""

from __future__ import annotations

import math
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go


BG = "#fffaf0"
TEXT = "#302747"
MUTED = "#655971"
GRID = "#e7dfe7"
COLORS = {"Found": "#157f73", "Fell": "#c45a36"}
LABELS = {"Found": "Hallazgo", "Fell": "Caída observada"}


def _fmt(value: float, digits: int = 2) -> str:
    """Formatea cantidades con coma decimal y espacio de millares."""
    if not np.isfinite(value):
        return "Sin dato"
    if value == int(value):
        return f"{int(value):,}".replace(",", " ")
    if abs(value) < 0.01 and value != 0:
        return f"{value:.4g}".replace(".", ",")
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def _base(height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color=TEXT),
        colorway=list(COLORS.values()),
        height=height,
        margin=dict(l=62, r=22, t=40, b=56),
        hoverlabel=dict(bgcolor="#fff3d8", bordercolor="#ad8fbd", font_color=TEXT, font_size=13),
        legend=dict(
            orientation="h",
            x=0,
            y=1.14,
            xanchor="left",
            yanchor="top",
            font=dict(size=11, color=MUTED),
            bgcolor="rgba(0,0,0,0)",
            groupclick="togglegroup",
        ),
        separators=", ",
        hovermode="closest",
        dragmode="zoom",
        transition_duration=0,
    )
    fig.update_xaxes(
        gridcolor=GRID,
        zeroline=False,
        linecolor=GRID,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        linecolor=GRID,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
        automargin=True,
    )
    return fig


def _empty(message: str, height: int = 360) -> go.Figure:
    fig = _base(height)
    fig.add_annotation(
        x=0.5,
        y=0.52,
        xref="paper",
        yref="paper",
        text=message,
        showarrow=False,
        align="center",
        font=dict(size=15, color=MUTED),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(meta={"eligible": 0})
    return fig


def _mass_values(df: pd.DataFrame, positive: bool) -> pd.DataFrame:
    values = pd.to_numeric(df["mass_g"], errors="coerce")
    eligible = np.isfinite(values) & (values.gt(0) if positive else values.ge(0))
    result = df.loc[eligible].copy()
    result["mass_g"] = values.loc[eligible].astype(float)
    return result


def mass_histogram(df: pd.DataFrame, scale: str = "log") -> go.Figure:
    """Cuenta todas las masas elegibles en intervalos comunes a las condiciones.

    En modo log, el eje se expresa en gramos, con distancias de log10. En modo
    original se conservan también los ceros. Los intervalos finales incluyen
    su límite superior, igual que numpy.histogram.
    """
    is_log = scale in {"log", "logarithmic", "log10"}
    subset = _mass_values(df, positive=is_log)
    if subset.empty:
        return _empty("No hay masas positivas para esta selección" if is_log else "No hay masas disponibles para esta selección")
    raw = subset["mass_g"].to_numpy()
    values = np.log10(raw) if is_log else raw
    low, high = float(values.min()), float(values.max())
    if low == high:
        span = 0.25 if is_log else max(abs(low) * 0.1, 0.5)
        edges = np.array([low - span, high + span])
        if not is_log and low == 0:
            edges = np.array([0.0, 1.0])
    else:
        bins = min(44, max(12, int(math.sqrt(len(subset)))))
        edges = np.linspace(low, high, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    widths = np.diff(edges) * 0.96
    original_edges = np.power(10.0, edges) if is_log else edges
    intervals = [f"{_fmt(a)} a {_fmt(b)} g" for a, b in zip(original_edges[:-1], original_edges[1:])]
    fig = _base()
    known = [condition for condition in LABELS if condition in subset["fall"].values]
    for condition in known:
        group = subset.loc[subset["fall"].eq(condition), "mass_g"].to_numpy()
        group_values = np.log10(group) if is_log else group
        counts, _ = np.histogram(group_values, bins=edges)
        details = [[interval, _fmt(int(n)), f"{100 * n / len(subset):.2f}".replace(".", ",")] for interval, n in zip(intervals, counts)]
        fig.add_bar(
            x=centers.tolist(),
            y=counts.tolist(),
            width=widths.tolist(),
            name=LABELS[condition],
            marker_color=COLORS[condition],
            marker_line_width=0,
            customdata=details,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + LABELS[condition]
                + ": %{customdata[1]} registros<br>"
                "%{customdata[2]} % de las masas elegibles<extra></extra>"
            ),
        )
    fig.update_layout(barmode="stack", bargap=0.04, meta={"eligible": len(subset), "excluded": len(df) - len(subset), "scale": "log" if is_log else "linear"})
    if is_log:
        tick_values = list(range(math.ceil(low), math.floor(high) + 1))
        if len(tick_values) > 8:
            tick_values = tick_values[::2]
        if len(tick_values) < 2:
            tick_values = [low, high] if low != high else [low]
        fig.update_xaxes(title="Masa (g) · escala logarítmica", tickmode="array", tickvals=tick_values, ticktext=[_fmt(10 ** value) for value in tick_values])
    else:
        fig.update_xaxes(title="Masa (g) · escala original", tickformat="~s")
    fig.update_yaxes(title="Número de registros", rangemode="tozero", tickformat="~s")
    return fig


def timeline(df: pd.DataFrame, period: str = "decade") -> go.Figure:
    """Cuenta registros por año o década, conservando los intervalos sin registros."""
    valid = df["year_valid"].fillna(False).astype(bool)
    subset = df.loc[valid & pd.to_numeric(df["year"], errors="coerce").notna()].copy()
    if subset.empty:
        return _empty("No hay años válidos para esta selección", 390)
    step = 1 if period in {"year", "annual", "año"} else 10
    subset["period"] = (pd.to_numeric(subset["year"]).astype(int) // step) * step
    lower, upper = int(subset["period"].min()), int(subset["period"].max())
    periods = np.arange(lower, upper + step, step)
    fig = _base(390)
    for condition in LABELS:
        group = subset.loc[subset["fall"].eq(condition)]
        if group.empty:
            continue
        counts = group.groupby("period").size().reindex(periods, fill_value=0)
        details = [[str(int(year)) if step == 1 else f"{int(year)}–{int(year + 9)}", _fmt(int(count))] for year, count in counts.items()]
        fig.add_scatter(
            x=periods.tolist(),
            y=counts.tolist(),
            name=LABELS[condition],
            mode="lines",
            line=dict(color=COLORS[condition], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(85,221,207,0.12)" if condition == "Found" else "rgba(255,188,117,0.09)",
            customdata=details,
            hovertemplate="<b>%{customdata[0]}</b><br>" + LABELS[condition] + ": %{customdata[1]} registros<extra></extra>",
        )
    fig.update_xaxes(
        title="Año consignado" if step == 1 else "Década del año consignado",
        tickformat="d",
        range=[lower - step / 2, upper + step / 2],
        rangeslider=dict(visible=True, thickness=0.14, bgcolor="#eee2f0", bordercolor=GRID, borderwidth=1),
    )
    fig.update_yaxes(title="Número de registros", rangemode="tozero", tickformat="~s", fixedrange=False)
    fig.update_layout(hovermode="x unified", meta={"eligible": len(subset), "excluded": len(df) - len(subset), "period": "year" if step == 1 else "decade"})
    return fig


def class_bars(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """Ordena las clases más frecuentes y desglosa su condición de registro."""
    if df.empty:
        return _empty("No hay clases para esta selección", 400)
    subset = df.copy()
    subset["recclass"] = subset["recclass"].fillna("Sin clasificación")
    totals = subset["recclass"].value_counts().head(max(1, int(top_n)))
    classes = totals.index.tolist()[::-1]
    fig = _base(max(360, min(500, 130 + 25 * len(classes))))
    for condition in LABELS:
        group = subset.loc[subset["fall"].eq(condition)]
        if group.empty:
            continue
        counts = group["recclass"].value_counts().reindex(classes, fill_value=0)
        custom = [[escape(str(name)), _fmt(int(count)), f"{100 * count / len(subset):.2f}".replace(".", ","), _fmt(int(totals.loc[name]))] for name, count in counts.items()]
        fig.add_bar(
            x=counts.tolist(),
            y=classes,
            orientation="h",
            name=LABELS[condition],
            marker=dict(color=COLORS[condition], line_width=0),
            customdata=custom,
            hovertemplate=(
                "<b>Clase %{customdata[0]}</b><br>"
                + LABELS[condition]
                + ": %{customdata[1]} registros<br>"
                "%{customdata[2]} % de la selección global<br>"
                "Total de esta clase: %{customdata[3]}<extra></extra>"
            ),
        )
    fig.update_layout(
        barmode="stack",
        bargap=0.29,
        meta={"eligible": len(subset), "represented": int(totals.sum()), "top_n": len(classes)},
    )
    fig.update_xaxes(title="Número de registros", rangemode="tozero", tickformat="~s")
    fig.update_yaxes(title=None, type="category", categoryorder="array", categoryarray=classes, showgrid=False)
    return fig


def mass_boxes(df: pd.DataFrame, group: str = "fall", top_n: int = 8) -> go.Figure:
    """Compara masas positivas mediante cuartiles y bigotes exactos.

    Los cuartiles usan interpolación lineal. Los bigotes terminan en los datos
    más extremos dentro de 1,5 veces el rango intercuartílico en gramos. Los
    valores atípicos participan del resumen, pero no se dibujan individualmente.
    """
    subset = _mass_values(df, positive=True)
    if subset.empty:
        return _empty("No hay masas positivas para comparar", 390)
    by_class = group in {"recclass", "class", "clase"}
    key = "recclass" if by_class else "fall"
    subset[key] = subset[key].fillna("Sin clasificación" if by_class else "Sin condición")
    categories = subset[key].value_counts().head(max(1, int(top_n))).index.tolist() if by_class else [item for item in LABELS if item in subset[key].values]
    fig = _base(390)
    for category in categories:
        values = subset.loc[subset[key].eq(category), "mass_g"].to_numpy()
        q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75], method="linear")
        iqr = q3 - q1
        inner = values[(values >= q1 - 1.5 * iqr) & (values <= q3 + 1.5 * iqr)]
        lower, upper = float(inner.min()), float(inner.max())
        outliers = int(np.sum((values < lower) | (values > upper)))
        label = str(category) if by_class else LABELS[category]
        color = "#77539c" if by_class else COLORS[category]
        summary = (
            f"<b>{escape(label)}</b><br>"
            f"Registros con masa positiva: {_fmt(len(values))}<br>"
            f"Cuartil inferior (25 %): {_fmt(q1)} g<br>"
            f"Mediana: {_fmt(median)} g<br>"
            f"Cuartil superior (75 %): {_fmt(q3)} g<br>"
            f"Bigotes: {_fmt(lower)} a {_fmt(upper)} g<br>"
            f"Atípicos no dibujados: {_fmt(outliers)}"
        )
        fig.add_trace(go.Box(
            x=[label],
            q1=[float(q1)],
            median=[float(median)],
            q3=[float(q3)],
            lowerfence=[lower],
            upperfence=[upper],
            name=label,
            line=dict(color=color, width=2),
            fillcolor="rgba(119,83,156,0.18)" if by_class else ("rgba(21,127,115,0.18)" if color == COLORS["Found"] else "rgba(196,90,54,0.18)"),
            width=0.48,
            boxpoints=False,
            showlegend=False,
            hovertemplate=summary + "<extra></extra>",
        ))
        fig.add_scatter(
            x=[label],
            y=[float(median)],
            mode="markers",
            marker=dict(color=color, size=7, symbol="diamond", line=dict(color=BG, width=1)),
            showlegend=False,
            hovertemplate=summary + "<extra></extra>",
        )
    fig.update_xaxes(title=None, showgrid=False, type="category", categoryorder="array", categoryarray=[str(item) if by_class else LABELS[item] for item in categories])
    fig.update_yaxes(title="Masa (g) · escala logarítmica", type="log", tickformat="~s")
    fig.update_layout(meta={"eligible": len(subset), "represented": int(subset[key].isin(categories).sum()), "excluded": len(df) - len(subset), "group": key})
    return fig
