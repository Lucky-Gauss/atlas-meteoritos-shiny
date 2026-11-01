"""Guarda bibliotecas públicas en el borrador para funcionar sin conexión."""
from pathlib import Path
from urllib.request import urlopen
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'www' / 'vendor'
ASSETS = {
    'leaflet.js': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'leaflet.css': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'leaflet-LICENSE.txt': 'https://unpkg.com/leaflet@1.9.4/LICENSE',
    'plotly-locale-es.js': 'https://cdn.plot.ly/plotly-locale-es-latest.js',
    'space-grotesk.woff2': 'https://unpkg.com/@fontsource-variable/space-grotesk/files/space-grotesk-latin-wght-normal.woff2',
    'space-grotesk-LICENSE.txt': 'https://unpkg.com/@fontsource-variable/space-grotesk/LICENSE',
}

if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    for name, url in ASSETS.items():
        path = DEST / name
        if not path.exists():
            try:
                with urlopen(url, timeout=45) as response:
                    path.write_bytes(response.read())
                print(name, path.stat().st_size)
            except Exception as exc:
                print(name, str(exc))
    from plotly.offline import get_plotlyjs
    (DEST / 'plotly.min.js').write_text(get_plotlyjs(), encoding='utf-8')
    (DEST / 'sources.json').write_text(json.dumps(ASSETS, indent=2), encoding='utf-8')
