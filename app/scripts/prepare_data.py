"""Prepara el CSV conservando todas las filas y documenta elegibilidad por vista."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/Meteorite_Landings.csv"
CSV_URL = "https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv"
DOWNLOAD_URL = CSV_URL + "?download=20261031"
PORTAL_URL = "https://data.nasa.gov/dataset/meteorite-landings"
YEAR_CUTOFF = 2026


def number(value):
    """Convierte vacíos en ausentes sin imputar valores."""
    if value is None or not str(value).strip():
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except ValueError:
        return None


def median(values):
    return statistics.median(values) if values else None


def quantile(values, p):
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * p
    low = math.floor(position)
    high = math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def download():
    """La descarga es explícita y nunca se ejecuta al iniciar Shiny."""
    RAW.parent.mkdir(parents=True, exist_ok=True)
    downloaded = datetime.now(timezone(timedelta(hours=-6)))
    request_url = CSV_URL + "?download=" + downloaded.strftime("%Y%m%d%H%M%S")
    request = Request(request_url, headers={"User-Agent": "AtlasMeteoritos/1.0"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    if not content.startswith(b"name,id,"):
        raise ValueError("La respuesta no tiene la cabecera esperada del conjunto NASA")
    RAW.write_bytes(content)
    provenance_path = ROOT / "data/provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.exists() else {}
    provenance.update({"download_date": downloaded.date().isoformat(), "download_request_url": request_url})
    write_json(provenance_path, provenance)


def prepare():
    with RAW.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        original_fields = list(reader.fieldnames or [])
        source_rows = list(reader)
    required = {"name", "id", "nametype", "recclass", "mass (g)", "fall", "year", "reclat", "reclong"}
    if not required.issubset(original_fields):
        raise ValueError("Cambió el esquema del archivo original. Revisá la preparación")

    rows = []
    for source in source_rows:
        mass = number(source["mass (g)"])
        year_number = number(source["year"])
        year = int(year_number) if year_number is not None and year_number.is_integer() else None
        lat, lon = number(source["reclat"]), number(source["reclong"])
        if lat is None or lon is None:
            coordinate_issue = "Coordenadas ausentes"
        elif not (-90 <= lat <= 90 and -180 <= lon <= 180):
            coordinate_issue = "Coordenadas fuera de rango"
        elif lat == 0 and lon == 0:
            coordinate_issue = "Par 0,0 sin ubicación confiable"
        else:
            coordinate_issue = ""
        if year is None:
            year_issue = "Año ausente"
        elif not 1 <= year <= YEAR_CUTOFF:
            year_issue = "Año fuera del período posible"
        else:
            year_issue = ""
        rows.append({
            "name": source["name"], "id": source["id"],
            "nametype": source["nametype"], "recclass": source["recclass"],
            "mass_g": mass, "fall": source["fall"], "year": year,
            "lat": lat, "lon": lon, "map_valid": not coordinate_issue,
            "year_valid": not year_issue, "mass_positive": mass is not None and mass > 0,
            "mass_nonnegative": mass is not None and mass >= 0,
            "coordinate_issue": coordinate_issue, "year_issue": year_issue,
        })

    prepared = ROOT / "data/processed/meteorites.csv"
    prepared.parent.mkdir(parents=True, exist_ok=True)
    with prepared.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    masses = [r["mass_g"] for r in rows if r["mass_nonnegative"]]
    positive = [r["mass_g"] for r in rows if r["mass_positive"]]
    valid_years = [r["year"] for r in rows if r["year_valid"]]
    classes = Counter(r["recclass"] for r in rows)
    conditions = Counter(r["fall"] for r in rows)
    quality = {
        "missing_by_original_column": {key: sum(not r[key].strip() for r in source_rows) for key in original_fields},
        "duplicate_complete_rows": len(source_rows) - len({tuple(r.values()) for r in source_rows}),
        "duplicate_ids": len(source_rows) - len({r["id"] for r in source_rows}),
        "duplicate_names": len(source_rows) - len({r["name"] for r in source_rows}),
        "missing_mass": sum(r["mass_g"] is None for r in rows),
        "zero_mass": sum(r["mass_g"] == 0 for r in rows),
        "negative_mass": sum(r["mass_g"] is not None and r["mass_g"] < 0 for r in rows),
        "missing_year": sum(r["year"] is None for r in rows),
        "anomalous_year": sum(r["year"] is not None and not r["year_valid"] for r in rows),
        "missing_coordinates": sum(r["coordinate_issue"] == "Coordenadas ausentes" for r in rows),
        "zero_zero_coordinates": sum(r["lat"] == 0 and r["lon"] == 0 for r in rows),
        "out_of_range_coordinates": sum(r["coordinate_issue"] == "Coordenadas fuera de rango" for r in rows),
        "map_eligible": sum(r["map_valid"] for r in rows),
        "year_eligible": len(valid_years),
        "positive_mass_eligible": len(positive),
        "nonnegative_mass_eligible": len(masses),
        "removed_rows": 0,
        "imputed_values": 0,
    }
    by_condition = {}
    for condition in sorted(conditions):
        subset = [r for r in rows if r["fall"] == condition]
        values = [r["mass_g"] for r in subset if r["mass_nonnegative"]]
        by_condition[condition] = {
            "count": len(subset), "percent": len(subset) / len(rows) * 100,
            "mass_n": len(values), "median_mass_g": median(values),
            "q1_mass_g": quantile(values, .25), "q3_mass_g": quantile(values, .75),
            "map_n": sum(r["map_valid"] for r in subset),
        }
    summary = {
        "rows": len(rows), "original_columns": len(original_fields),
        "prepared_columns": len(rows[0]), "class_count": len(classes),
        "conditions": dict(conditions), "nametypes": dict(Counter(r["nametype"] for r in rows)),
        "year_min": min(valid_years), "year_max": max(valid_years),
        "year_cutoff": YEAR_CUTOFF, "mass_min_g": min(masses),
        "mass_min_positive_g": min(positive), "mass_max_g": max(masses),
        "mass_median_g": median(masses), "mass_q1_g": quantile(masses, .25),
        "mass_q3_g": quantile(masses, .75), "mass_mean_g": statistics.mean(masses),
        "mass_positive_median_g": median(positive), "mass_total_g": sum(masses),
        "quality": quality, "by_condition": by_condition,
        "top_classes": [{"class": k, "count": v, "percent": v / len(rows) * 100} for k,v in classes.most_common(15)],
        "class_counts": dict(classes.most_common()),
        "year_counts": [{"year": y, "count": n} for y,n in sorted(Counter(valid_years).items())],
        "year_condition_counts": [
            {"year": y, "fall": fall, "count": count}
            for (y,fall),count in sorted(Counter((r["year"],r["fall"]) for r in rows if r["year_valid"]).items())
        ],
        "largest": sorted((r for r in rows if r["mass_nonnegative"]), key=lambda r:r["mass_g"], reverse=True)[:5],
        "anomalous_year_rows": [r for r in rows if r["year"] is not None and not r["year_valid"]],
        "out_of_range_coordinate_rows": [r for r in rows if r["coordinate_issue"] == "Coordenadas fuera de rango"],
    }
    write_json(ROOT / "data/summary.json", summary)
    provenance_path = ROOT / "data/provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.exists() else {}
    provenance.update({
        "title": "Meteorite Landings", "original_creator": "The Meteoritical Society",
        "publisher": "NASA Open Data Portal", "dataset_identifier": "gh4g-9sfh",
        "landing_page": PORTAL_URL,
        "catalog_verification_url": "https://catalog.data.gov/dataset/meteorite-landings",
        "file_url": CSV_URL, "download_request_url": provenance.get("download_request_url", DOWNLOAD_URL),
        "download_date": provenance.get("download_date", "2026-10-31"),
        "download_timezone": "America/Costa_Rica", "source_type": "CSV oficial alojado por NASA, sin espejo",
        "raw_file": "data/raw/Meteorite_Landings.csv", "raw_bytes": RAW.stat().st_size,
        "sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "rows": len(source_rows), "columns": len(original_fields), "original_column_names": original_fields,
        "license": "La ficha de NASA consultada indica License not specified. El acceso es público, pero no se presume una licencia abierta específica.",
        "license_url": PORTAL_URL,
        "reuse_note": "Conservar la atribución a The Meteoritical Society y NASA. Revisar las condiciones de uso antes de redistribuir o publicar el proyecto.",
        "historical_snapshot": "Es una copia histórica. Los años plausibles contenidos van de 860 a 2013. La fecha de actualización del catálogo no equivale a actualización de las observaciones.",
        "year_definition": "Año de la caída observada para Fell o del hallazgo para Found. Para Found no es una fecha de impacto.",
        "year_definition_reference": "https://www.kaggle.com/datasets/nasa/meteorite-landings",
        "legacy_note": "El catálogo conserva descripciones de una versión antigua de 34 513 meteoritos. Las dimensiones informadas aquí se calcularon sobre el CSV descargado.",
        "preparation": "scripts/prepare_data.py", "year_cutoff": YEAR_CUTOFF,
    })
    write_json(provenance_path, provenance)
    print(json.dumps({"rows":len(rows),"columns":len(original_fields),"quality":quality,"mass_median_g":median(masses),"by_condition":by_condition}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepara la copia local de Meteorite Landings")
    parser.add_argument("--download", action="store_true", help="Descargar nuevamente el CSV oficial antes de preparar")
    args = parser.parse_args()
    if args.download:
        download()
    prepare()
