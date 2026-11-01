"""Pruebas de contrato con la copia real de NASA descargada para el borrador."""

import csv
import io
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from atlas.filtering import export_frame, select_records


class RealDataFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(ROOT / "data/processed/meteorites.csv")

    def select(self, **overrides):
        options = {
            "years": (860, 2013),
            "mass_range": (0, 60_000_000),
            "conditions": ("Found", "Fell"),
        }
        options.update(overrides)
        return select_records(self.data, **options)

    def test_default_preserves_entire_snapshot_and_missing_values(self):
        result = self.select()
        self.assertEqual(len(result), 45_716)
        self.assertEqual(result.mass_g.isna().sum(), 131)
        self.assertEqual(result.year.isna().sum(), 291)
        self.assertEqual(result.lat.isna().sum(), 7_315)

    def test_map_selection_preserves_every_eligible_coordinate(self):
        result = self.select(geography="valid")
        self.assertEqual(len(result), 32_186)
        self.assertEqual(result.fall.eq("Fell").sum(), 1_096)
        self.assertEqual(result.fall.eq("Found").sum(), 31_090)
        self.assertFalse(result.name.eq("Meridiani Planum").any())
        self.assertFalse((result.lat.eq(0) & result.lon.eq(0)).any())

    def test_unusable_location_remains_available_as_a_selection(self):
        result = self.select(geography="missing")
        self.assertEqual(len(result), 13_530)
        self.assertTrue(result.name.eq("Meridiani Planum").any())
        self.assertEqual(result.lat.isna().sum(), 7_315)

    def test_name_search_is_case_insensitive_and_trims_spaces(self):
        result = self.select(query="  aLlEnDe  ")
        self.assertEqual(result.name.tolist(), ["Allende"])
        self.assertEqual(int(result.iloc[0].id), 2278)
        self.assertEqual(result.iloc[0].mass_g, 2_000_000)
        self.assertEqual(result.iloc[0].year, 1969)

    def test_name_search_treats_regex_characters_as_literal_text(self):
        self.assertTrue(self.select(query="[").empty)

    def test_condition_selections_have_known_totals(self):
        self.assertEqual(len(self.select(conditions=("Fell",))), 1_107)
        self.assertEqual(len(self.select(conditions=("Found",))), 44_609)
        self.assertTrue(self.select(conditions=()).empty)
        self.assertTrue(self.select(conditions=("Inexistente",)).empty)

    def test_class_filter_combines_with_condition(self):
        self.assertEqual(len(self.select(classes=("L6",))), 8_285)
        self.assertEqual(len(self.select(classes=("L6", "H5"))), 15_427)
        self.assertEqual(len(self.select(classes=("L6",), conditions=("Fell",))), 262)
        self.assertTrue(self.select(classes=("Clase inexistente",)).empty)

    def test_name_and_condition_intersection_can_be_empty(self):
        self.assertTrue(self.select(query="Allende", conditions=("Found",)).empty)

    def test_mass_missing_and_zero_are_independent_choices(self):
        known = self.select(include_unknown_mass=False)
        positive = self.select(include_unknown_mass=False, include_zero=False)
        without_zero = self.select(include_zero=False)
        self.assertEqual(len(known), 45_585)
        self.assertEqual(known.mass_g.eq(0).sum(), 19)
        self.assertEqual(len(positive), 45_566)
        self.assertTrue(positive.mass_g.gt(0).all())
        self.assertEqual(len(without_zero), 45_697)
        self.assertEqual(without_zero.mass_g.isna().sum(), 131)

    def test_zero_only_range_and_empty_numeric_selection(self):
        zero_only = self.select(mass_range=(0, 0), include_unknown_mass=False)
        self.assertEqual(len(zero_only), 19)
        self.assertIn("Gove", zero_only.name.tolist())
        self.assertTrue(self.select(mass_range=(0, 0), include_unknown_mass=False, include_zero=False).empty)

    def test_unknown_mass_remains_visible_when_explicitly_included(self):
        result = self.select(mass_range=(0, 0), include_zero=False)
        self.assertEqual(len(result), 131)
        self.assertTrue(result.mass_g.isna().all())

    def test_mass_range_boundaries_are_inclusive(self):
        result = self.select(mass_range=(21, 21), include_unknown_mass=False)
        self.assertEqual(len(result), 50)
        self.assertIn("Aachen", result.name.tolist())
        self.assertEqual(len(self.select(query="Allende", mass_range=(2_000_000, 2_000_000), include_unknown_mass=False)), 1)

    def test_year_missing_and_anomaly_can_be_excluded(self):
        result = self.select(include_unknown_year=False)
        self.assertEqual(len(result), 45_424)
        self.assertFalse(result.year.isna().any())
        self.assertFalse(result.name.eq("Northwest Africa 7701").any())
        anomaly = self.select(query="Northwest Africa 7701")
        self.assertEqual(len(anomaly), 1)
        self.assertEqual(anomaly.iloc[0].year, 2101)
        self.assertFalse(anomaly.iloc[0].year_valid)

    def test_year_period_respects_explicit_unknown_toggle(self):
        self.assertEqual(len(self.select(years=(1900, 2013), include_unknown_year=False)), 44_696)
        self.assertEqual(len(self.select(years=(1900, 2013))), 44_988)
        self.assertEqual(len(self.select(years=(2003, 2003), include_unknown_year=False)), 3_323)

    def test_inverted_mass_range_returns_empty_even_with_unknowns(self):
        self.assertTrue(self.select(mass_range=(100, 10)).empty)

    def test_inverted_year_range_returns_empty_even_with_unknowns(self):
        self.assertTrue(self.select(years=(2000, 1900)).empty)

    def test_export_has_spanish_units_quality_flags_and_original_coordinates(self):
        frame = export_frame(self.select(query="Meridiani Planum"))
        expected = ["Nombre", "Identificador", "Clase", "Condición", "Año del catálogo", "Masa (g)",
                    "Latitud original", "Longitud original", "Ubicación utilizable", "Año utilizable"]
        self.assertEqual(frame.columns.tolist(), expected)
        rows = list(csv.DictReader(io.StringIO(frame.to_csv(index=False))))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Nombre"], "Meridiani Planum")
        self.assertEqual(rows[0]["Clase"], "Iron, IAB complex")
        self.assertEqual(rows[0]["Condición"], "Hallazgo")
        self.assertEqual(rows[0]["Masa (g)"], "")
        self.assertAlmostEqual(float(rows[0]["Longitud original"]), 354.47333)
        self.assertEqual(rows[0]["Ubicación utilizable"], "False")

    def test_empty_export_retains_the_download_schema(self):
        exported = export_frame(self.select(query="Nombre que no existe en el catálogo"))
        self.assertTrue(exported.empty)
        self.assertEqual(len(exported.columns), 10)
        self.assertEqual(len(exported.to_csv(index=False).splitlines()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
