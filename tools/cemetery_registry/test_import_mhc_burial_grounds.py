"""Offline fixture tests for the public MHC cemetery candidate importer."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).with_name("import_mhc_burial_grounds.py")
spec = importlib.util.spec_from_file_location("import_mhc_burial_grounds", MODULE)
mhc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mhc)


def feature(source_id, lat, lon, typ="Burial Ground"):
    return {
        "attributes": {
            "OBJECTID": int(source_id),
            "MHCN": "WAR." + source_id,
            "TYPE": typ,
            "COMMON_NAM": "Historic Burial Ground",
            "TOWN_NAME": "Warren"
        },
        "geometry": {"x": lon, "y": lat}
    }


class TestMHC(unittest.TestCase):
    def test_center_candidate_preserves_source(self):
        pages = [{"payload": {"features": [feature("1", 42.20909, -72.19660)]}}]
        candidates, rejected = mhc.candidates_from_pages(pages)
        self.assertEqual((len(candidates), rejected), (1, 0))
        self.assertEqual(candidates[0]["source_id"], "WAR.1")
        self.assertEqual(candidates[0]["review_status"], "unreviewed")
        self.assertIsNone(candidates[0]["canonical_cemetery_id"])

    def test_out_of_radius_excluded(self):
        pages = [{"payload": {"features": [feature("2", 42.9, -72.19660)]}}]
        self.assertEqual(mhc.candidates_from_pages(pages)[0], [])

    def test_non_burial_ground_excluded(self):
        pages = [{"payload": {"features": [feature("3", 42.20909, -72.19660, "Building")]}}]
        self.assertEqual(mhc.candidates_from_pages(pages)[0], [])

    def test_missing_coordinates_rejected(self):
        pages = [{"payload": {"features": [{"attributes": {
            "TYPE": "Burial Ground", "MHCN": "WAR.4"}, "geometry": {}}]}}]
        self.assertEqual(mhc.candidates_from_pages(pages)[1], 1)

    def test_page_size_validation(self):
        with self.assertRaises(ValueError):
            mhc.acquire(2001)


if __name__ == "__main__":
    unittest.main()
