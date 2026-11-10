"""Synthetic safe-import checks for Field Camera ZIP bundles."""
import copy
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("camera_zip", ROOT / "scripts/validate_camera_export.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
ID = "CPC-2026-11-10T15-35-00-000Z"
ORIGINAL = bytes([255,216,255,217])


def record():
    return {"id":ID,"schema_version":"0.5","photo":{
        "format":"image/jpeg","width":1200,"height":800,"original_is_full_frame":True},
        "location":None,"location_status":"location_missing"}


class CameraZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "camera.zip"

    def write(self, rec=None, extra=None):
        rec = record() if rec is None else rec
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_STORED) as z:
            z.writestr(ID + "/record.json", json.dumps(rec))
            z.writestr(ID + "/" + ID + "_original.jpg", ORIGINAL)
            for key,value in (extra or {}).items():
                z.writestr(key, value)

    def test_valid_export_is_only_validated_never_imported(self):
        self.write()
        out=validator.validate_camera_zip(self.path)
        self.assertEqual(out["review_status"],"unreviewed")
        self.assertFalse(out["published"])
        self.assertFalse(out["imported"])
        self.assertEqual(out["member_count"],2)
        self.assertEqual(out["original_bytes"],len(ORIGINAL))

    def test_valid_location_flag_without_revealing_coordinates(self):
        r=record()
        r["location"]={"latitude":42.20909,"longitude":-72.1966,
                       "source":"device_gps","accuracy_m":12}
        r["location_status"]="device_gps_observed"
        self.write(r)
        report=validator.validate_camera_zip(self.path)
        self.assertTrue(report["has_gps_metadata"])
        self.assertNotIn("latitude",report)
        self.assertNotIn("longitude",report)
        self.assertNotIn("location",report)

    def test_forged_unlocated_record_rejected(self):
        r=record()
        r["location"]={"latitude":42,"longitude":-72}
        self.write(r)
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)

    def test_invalid_coordinates_rejected(self):
        r=record()
        r["location_status"]="device_gps_observed"
        r["location"]={"latitude":99,"longitude":-72}
        self.write(r)
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)

    def test_unexpected_path_rejected(self):
        self.write(extra={"../escape.txt":"unsafe"})
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)

    def test_unexpected_attachment_rejected(self):
        self.write(extra={ID + "/private.txt":"unsafe"})
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)

    def test_invalid_camera_version_rejected(self):
        r=record()
        r["schema_version"]="2.0"
        self.write(r)
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)

    def test_duplicate_member_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.write(extra={ID + "/record.json":"{}"})
        with self.assertRaises(ValueError):
            validator.validate_camera_zip(self.path)


if __name__=="__main__":
    unittest.main()
