"""Static safety checks for the isolated v0.5 field-camera pilot.

These do not substitute for actual iPhone/Safari camera, geolocation, ZIP or
service worker tests. No browser is launched or photo is acquired in CI.
"""
import re
import unittest
from pathlib import Path

CAMERA = Path(__file__).resolve().parents[1] / "web" / "camera"
ASSETS = ("README.md","index.html","discovery.js","exif.js",
          "silhouette.js","sw.js","manifest.webmanifest","icon.svg")


class CameraPackageTests(unittest.TestCase):
    def test_all_required_assets_staged(self):
        self.assertTrue(all((CAMERA / name).is_file() for name in ASSETS))

    def test_script_references_are_local(self):
        html = (CAMERA / "index.html").read_text(encoding="utf-8")
        urls = re.findall(r'<script[^>]*src=["\']([^"\']+)', html)
        self.assertEqual(set(urls), {"discovery.js","exif.js","silhouette.js"})
        self.assertTrue(all((CAMERA / url).is_file() for url in urls))

    def test_camera_has_no_implicit_network_upload(self):
        html = (CAMERA / "index.html").read_text(encoding="utf-8")
        self.assertIn("indexedDB.open(", html)
        self.assertIn("packageZIP(", html)
        # No direct upload transport is implemented by this pilot.
        self.assertNotIn("XMLHttpRequest(", html)
        self.assertNotIn("navigator.sendBeacon(", html)
        self.assertNotRegex(html, r"fetch\s*\(")

    def test_original_frame_and_geotagged_copy_are_separate(self):
        exif = (CAMERA / "exif.js").read_text(encoding="utf-8")
        self.assertIn("new Uint8Array(jpeg.length+exif.length)", exif)
        self.assertIn("root.CPCGeoTag={addGPS}", exif)
        html = (CAMERA / "index.html").read_text(encoding="utf-8")
        self.assertIn("_geotagged.jpg", html)
        self.assertIn("original", html.lower())

    def test_discovery_is_not_claimed_as_trained_recognition(self):
        script = (CAMERA / "discovery.js").read_text(encoding="utf-8")
        self.assertIn("NOT a trained", script)
        readme = (CAMERA / "README.md").read_text(encoding="utf-8")
        self.assertIn("not a verified monument plot coordinate", readme.lower())


if __name__ == "__main__":
    unittest.main()
