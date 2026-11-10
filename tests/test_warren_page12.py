"""Page 12 full-source intake must never assert reviewed people or burials."""
import sqlite3
import tempfile
import json
import unittest
from pathlib import Path

from scripts.stage_warren_ocr_review import ROOT, FILES, stage as stage_original
from scripts.stage_warren_page_omissions import stage as stage_omissions
from scripts.stage_warren_page12 import NAME, prepare, stage


class WarrenPage12Tests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for p in sorted((ROOT/"db/migrations").glob("*.sql")):
            self.db.executescript(p.read_text(encoding="utf-8"))
        self.db.executescript((ROOT/"db/seeds/0006_new_england_vital_catalog.sql").read_text(encoding="utf-8"))
        stage_original(self.db,[ROOT/"data/vital-records"/n for n in FILES])
        stage_omissions(self.db)
        self.addCleanup(self.db.close)

    def count(self,table):
        return self.db.execute("SELECT count(*) FROM "+table).fetchone()[0]

    def test_39_entries_7_gravestone_and_no_accepted_events(self):
        self.assertEqual(len(prepare()[1]),39)
        self.assertEqual(stage(self.db)["inserted"],39)
        self.assertEqual(self.count("vital_ocr_review_candidates"),140)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_ocr_review_candidates WHERE printed_page=12"
        ).fetchone()[0],39)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_ocr_review_candidates WHERE original_source_class='gravestone'"
        ).fetchone()[0],24)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(),[])
        for t in ("vital_record_entries","persons","burials","vital_ocr_page_reviews",
                  "vital_ocr_accepted_events","vital_entity_match_candidates"):
            self.assertEqual(self.count(t),0)

    def test_repeat_and_changed_candidate_hash_rejection(self):
        stage(self.db)
        self.assertEqual(stage(self.db),{"inserted":0,"duplicate":39,"total":39})
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/NAME
            data=json.loads((ROOT/"data/vital-records"/NAME).read_text(encoding="utf-8"))
            data["records"][0]["source_line_reading"]="altered"
            path.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"batch source changed"):
                stage(self.db,path)

    def test_falsified_scan_approval_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/NAME
            data=json.loads((ROOT/"data/vital-records"/NAME).read_text(encoding="utf-8"))
            data["records"][0]["source_image_verified"]=True
            path.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Provisional record invalid"):
                prepare(path)


if __name__=="__main__":
    unittest.main()
