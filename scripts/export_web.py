"""Prepara y exporta el atlas a Shinylive sin incluir el entorno de desarrollo."""
from pathlib import Path
import shutil
import subprocess
import zipfile
import io
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
    classic = PUBLIC / 'clasico-app'
    classic.mkdir(parents=True, exist_ok=True)
    archive = subprocess.check_output(['git', 'archive', '--format=zip',
        'cc5642bc9890928b605a7714abd6c16b99d5d3a6', 'app.py', 'atlas', 'www', 'data', 'docs'], cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        bundle.extractall(classic)
    _export.export(classic, SITE / 'clasico')
    for folder, label, target in [(SITE, 'Abrir versión clásica', './clasico/'),
                                   (SITE / 'clasico', 'Abrir expedición ilustrada', '../')]:
        index = folder / 'index.html'
        html = index.read_text(encoding='utf-8')
        html = html.replace('<title>Shiny App</title>', '<title>Atlas de meteoritos</title>')
        html = html.replace('<html lang="en">', '<html lang="es">')
        html = html.replace('</body>', f'<a href="{target}" style="position:fixed;bottom:12px;right:18px;z-index:9999;background:#ffcf79;color:#352658;padding:9px 16px;border-radius:24px;font:13px sans-serif;text-decoration:none">{label}</a></body>')
        index.write_text(html, encoding='utf-8')
    print('Exportacion de ambas versiones lista en publicacion/site')

if __name__ == '__main__':
    prepare()
