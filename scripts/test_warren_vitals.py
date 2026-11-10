#!/usr/bin/env python3
"""Offline regression checks for the Warren OCR candidate staging pipeline.

Execute from a full repository checkout:
    python -m unittest discover -s scripts -p 'test_warren_vitals.py' -v
"""
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "stage_warren_vitals.py"
spec = importlib.util.spec_from_file_location("stage_warren_vitals", MODULE)
stage_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage_module)

class WarrenStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.errors = stage_module.validate()

    def test_batch_counts_and_unique_ids(self):
        self.assertEqual(len(self.records), 75)
        self.assertEqual(len({r["id"] for r in self.records}), 75)
        self.assertEqual(len(self.errors), 0)

    def test_gravestone_lineage_is_not_double_counted(self):
        gs2 = [r for r in self.records if r["original_source_class"]=="gravestone"]
        self.assertEqual(len(gs2), 14)
        self.assertTrue(all(r.get("independent_from_pine_grove_photo") is False for r in gs2))
        others = [r for r in self.records if r["original_source_class"]!="gravestone"]
        self.assertTrue(all(r.get("independent_from_pine_grove_photo") is None for r in others))

    def test_all_rows_are_not_visually_verified(self):
        self.assertTrue(all(r["review_status"]=="requires_page_image_check" for r in self.records))
        self.assertTrue(all(r.get("source_image_verified") is False for r in self.records))

    def test_corrected_surname_has_audit_trail(self):
        path=ROOT / "data/vital-records/warren-1910-births-p011-batch03.json"
        data=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(sum(r["name_verbatim"].startswith("BARNUM ") for r in data["records"]),4)
        self.assertFalse(any(r["name_verbatim"].startswith("BARWUM ") for r in data["records"]))
        self.assertTrue(any(c.get("previous_reading")=="BARWUM" for c in data.get("ocr_corrections",[])))

    def test_sqlite_staging_and_no_production_tables(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"warren-staging.sqlite"
            stage_module.stage(self.records,out)
            with sqlite3.connect(out) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                self.assertEqual(db.execute("SELECT count(*) FROM ocr_vital_candidates").fetchone()[0],75)
                self.assertEqual(db.execute("SELECT count(*) FROM ocr_vital_candidates WHERE source_class='gravestone'").fetchone()[0],14)
                self.assertEqual(db.execute("SELECT count(*) FROM ocr_vital_candidates WHERE scan_verified <> 0").fetchone()[0],0)
                self.assertEqual(db.execute("SELECT count(*) FROM sqlite_master WHERE name='persons' OR name='vital_record_entries'").fetchone()[0],0)

    def test_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"existing.sqlite"
            out.write_text("do not overwrite")
            with self.assertRaises(SystemExit):
                stage_module.stage(self.records,out)
            self.assertEqual(out.read_text(),"do not overwrite")

if __name__ == "__main__":
    unittest.main()
