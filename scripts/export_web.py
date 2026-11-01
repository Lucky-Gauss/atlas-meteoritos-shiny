"""Prepara y exporta el atlas a Shinylive sin incluir el entorno de desarrollo."""
from pathlib import Path
import shutil
import shinylive
from shinylive import _assets, _export

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'publicacion'
APP = PUBLIC / 'app'
SITE = PUBLIC / 'site'

def prepare():
    APP.mkdir(parents=True, exist_ok=True)
    text = (ROOT / 'app.py').read_text(encoding='utf-8-sig')
    text = text.replace('BORRADOR LOCAL', 'ATLAS INTERACTIVO')
    text = text.replace('Borrador universitario local', 'Borrador universitario')
    (APP / 'app.py').write_text(text, encoding='utf-8')
    for directory in ['atlas', 'www', 'data', 'docs']:
        shutil.copytree(ROOT / directory, APP / directory, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    # La caché de publicación también permanece dentro del borrador.
    _assets.shinylive_cache_dir = lambda: str(ROOT / '.sl')
    _assets.ensure_shinylive_assets()
    _export.export(APP, SITE)
    (SITE / '.nojekyll').touch()
    print('Exportacion lista en publicacion/site')

if __name__ == '__main__':
    prepare()
