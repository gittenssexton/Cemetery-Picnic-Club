"""Page-complete Warren 1910 pilot remains provisional, cited, repeatable."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.stage_warren_ocr_review import FILES, ROOT, stage as stage_initial
from scripts.stage_warren_page_omissions import FILENAME, prepare, stage as stage_omissions


class WarrenOmissionTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for path in sorted((ROOT/"db/migrations").glob("*.sql")):
            self.db.executescript(path.read_text(encoding="utf-8"))
        self.db.executescript((ROOT/"db/seeds/0006_new_england_vital_catalog.sql").read_text(encoding="utf-8"))
        self.paths=[ROOT/"data/vital-records"/x for x in FILES]
        stage_initial(self.db,self.paths)
        self.addCleanup(self.db.close)

    def count(self,table):
        return self.db.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]

    def test_complete_page_candidate_coverage_not_identity(self):
        batch,rows=prepare(ROOT/"data/vital-records"/FILENAME)
        self.assertEqual(len(rows),26)
        self.assertEqual(stage_omissions(self.db)["inserted"],26)
        self.assertEqual(self.count("vital_ocr_review_candidates"),101)
        self.assertEqual(self.count("vital_ocr_review_batches"),4)
        by_page=dict(self.db.execute(
            "SELECT printed_page,count(*) FROM vital_ocr_review_candidates GROUP BY printed_page"))
        self.assertEqual(by_page,{9:26,10:35,11:40})
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_ocr_review_candidates WHERE original_source_class='gravestone'"
        ).fetchone()[0],17)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_ocr_review_candidates WHERE source_image_verified=1"
        ).fetchone()[0],0)
        for table in ("vital_ocr_page_reviews","vital_ocr_accepted_events",
                      "vital_record_entries","persons","burials","vital_entity_match_candidates"):
            self.assertEqual(self.count(table),0,table)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_exact_replay_preserves_all_original_records(self):
        stage_omissions(self.db)
        self.assertEqual(stage_omissions(self.db),{"inserted":0,"duplicate":26,"candidate_count":26})
        self.assertEqual(self.count("vital_ocr_review_candidates"),101)

    def test_conflicting_omission_aborts_before_write(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/FILENAME
            original=json.loads((ROOT/"data/vital-records"/FILENAME).read_text(encoding="utf-8"))
            original["records"][4]["review_status"]="scan_checked"
            path.write_text(json.dumps(original),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"provenance"):
                stage_omissions(self.db,path)
            self.assertEqual(self.count("vital_ocr_review_candidates"),75)

    def test_gs2_cannot_become_independent_claim(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/FILENAME
            original=json.loads((ROOT/"data/vital-records"/FILENAME).read_text(encoding="utf-8"))
            rec=next(x for x in original["records"] if x["original_source_class"]=="gravestone")
            rec["independent_from_pine_grove_photo"]=True
            path.write_text(json.dumps(original),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"G.S.2"):
                prepare(path)

    def test_duplicate_source_ids_and_original_ids_cannot_collide(self):
        batch,rows=prepare(ROOT/"data/vital-records"/FILENAME)
        initial={r[0] for f in self.paths for r in __import__(
            "scripts.stage_warren_ocr_review",fromlist=["prepare"]).prepare(f)[1]}
        self.assertFalse(initial.intersection({r[0] for r in rows}))
        self.assertEqual(len({r[0] for r in rows}),26)


if __name__=="__main__":
    unittest.main()
