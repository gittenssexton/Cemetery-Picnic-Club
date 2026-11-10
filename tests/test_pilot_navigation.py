"""Pilot integration safety / navigation smoke checks (no live credentials required)."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PilotNavigationTests(unittest.TestCase):
    def test_notebook_links_to_camera_and_archival_research(self):
        page=(ROOT/"web/index.html").read_text(encoding="utf-8")
        self.assertIn('href="./camera/"',page)
        self.assertIn('href="./research/vital-records.html"',page)

    def test_camera_links_to_research_without_bearer_token(self):
        page=(ROOT/"web/camera/index.html").read_text(encoding="utf-8")
        self.assertIn('href="../research/vital-records.html"',page)
        self.assertIn("No camera record is automatically uploaded or linked.",page)
        self.assertNotIn("CPC_API_TOKEN",page)

    def test_research_only_opens_optional_archive_searches(self):
        page=(ROOT/"web/research/vital-records.html").read_text(encoding="utf-8")
        self.assertIn("https://www.loc.gov/search/?q=",page)
        self.assertIn("https://www.digitalcommonwealth.org/search?",page)
        self.assertNotIn("/internal/warren-ocr-review",page)
        self.assertNotIn("CPC_API_TOKEN",page)
        self.assertNotIn("fetch(",page)
        self.assertIn("not been accepted as verified events",page)

    def test_internal_staging_api_remains_server_only(self):
        api=(ROOT/"server/cpc-integration-staging.mjs").read_text(encoding="utf-8")
        self.assertIn("browser_origin_denied",api)
        self.assertIn("environment_not_authorized",api)
        self.assertIn("CPC_API_TOKEN",api)

if __name__=="__main__":
    unittest.main()
