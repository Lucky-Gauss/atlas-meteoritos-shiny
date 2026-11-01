"""Escenas vectoriales originales del museo, independientes de los datos."""
from pathlib import Path
from shiny import ui

ART = Path(__file__).resolve().parents[1] / 'www' / 'illustrations'


def scene(name, class_name=''):
    return ui.div(ui.HTML((ART / f'{name}.svg').read_text(encoding='utf-8')),
                  class_='illustration ' + class_name, **{'aria-hidden': 'true'})


def chapter(name, kicker, title, text):
    return ui.div(scene(name), ui.div(ui.div(kicker, class_='eyebrow'),
                  ui.h2(title), ui.p(text)), class_='chapter chapter-' + name)
