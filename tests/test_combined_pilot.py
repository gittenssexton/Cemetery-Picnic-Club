"""Checks for the combined geology/field-camera/vital pilot interface."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def content(path): return (ROOT/path).read_text(encoding="utf-8")

class CombinedPilotTests(unittest.TestCase):
    def test_all_three_pilot_pages_exist(self):
        for path in ("web/camera/index.html","web/stone-camera.html","web/research/vital-records.html"):
            self.assertTrue((ROOT/path).is_file(),path)

    def test_camera_and_field_notebook_link_to_stone_pilot(self):
        self.assertIn('href="../stone-camera.html"',content("web/camera/index.html"))
        self.assertIn('href="./stone-camera.html"',content("web/index.html"))

    def test_stone_pilot_links_back_to_camera_and_records(self):
        page=content("web/stone-camera.html")
        self.assertIn('href="./camera/"',page)
        self.assertIn('href="./research/vital-records.html"',page)

    def test_geology_is_optional_and_not_identity_match(self):
        page=content("web/stone-camera.html")
        self.assertIn('id="lookupGeology"',page)
        self.assertIn('/api/geology?lat=',page)
        self.assertIn('does <strong>not</strong> establish the quarry',page)
        self.assertIn("No Mindat data",page)
        self.assertNotIn("MINDAT_API_TOKEN",page)
        self.assertNotIn("CPC_API_TOKEN",page)

    def test_vital_records_not_published(self):
        page=content("web/research/vital-records.html")
        self.assertIn("not been accepted as verified events",page)
        self.assertNotIn("/internal/warren-ocr-review",page)
        self.assertNotIn("fetch(",page)

if __name__=="__main__":
    unittest.main()
