"""Warren OCR review queue holds provisional evidence without accepted vital events."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.stage_warren_ocr_review import FILES, prepare, stage, ROOT


class WarrenOcrReviewTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for p in sorted((ROOT/"db/migrations").glob("*.sql")):
            self.db.executescript(p.read_text(encoding="utf-8"))
        self.db.executescript((ROOT/"db/seeds/0006_new_england_vital_catalog.sql").read_text(encoding="utf-8"))
        self.addCleanup(self.db.close)
        self.paths=[ROOT/"data/vital-records"/n for n in FILES]

    def count(self,table):
        return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_75_candidates_14_gravestone_unverified(self):
        for path in self.paths:
            batch, rows=prepare(path)
            self.assertEqual(len(rows),25)
        self.assertEqual(stage(self.db,self.paths),{"inserted":75,"duplicates":0,"candidate_count":75})
        self.assertEqual(self.count("vital_ocr_review_candidates"),75)
        self.assertEqual(self.count("vital_ocr_review_batches"),3)
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM vital_ocr_review_candidates WHERE original_source_class='gravestone'"
        ).fetchone()[0],14)
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM vital_ocr_review_candidates WHERE source_image_verified=1"
        ).fetchone()[0],0)
        for t in ("vital_record_entries","persons","burials","vital_entity_match_candidates",
                  "domain_evidence_links","images"):
            self.assertEqual(self.count(t),0,t)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_exact_repeat_does_not_duplicate(self):
        stage(self.db,self.paths)
        result=stage(self.db,self.paths)
        self.assertEqual((result["inserted"],result["duplicates"]),(0,75))
        self.assertEqual(self.count("vital_ocr_review_candidates"),75)

    def test_prevent_ocr_auto_approval_and_false_corrob(self):
        stage(self.db,self.paths)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""UPDATE vital_ocr_review_candidates SET
                review_status='scan_checked' WHERE id='MA-WARREN-RICE1910-BIRTH-P009-001'""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""UPDATE vital_ocr_review_candidates SET
                independently_corrob_gravestone=1 WHERE original_source_class='gravestone'""")

    def test_reject_changed_source_batch(self):
        stage(self.db,self.paths)
        with tempfile.TemporaryDirectory() as tmp:
            original=self.paths[0]
            changed=json.loads(original.read_text(encoding="utf-8"))
            changed["records"][0]["name_verbatim"]="Changed without scan review"
            renamed=Path(tmp)/original.name
            renamed.write_text(json.dumps(changed),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Batch differs"):
                stage(self.db,[renamed])
        self.assertEqual(self.count("vital_ocr_review_candidates"),75)

    def test_reject_falsified_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            original=self.paths[0]
            altered=json.loads(original.read_text(encoding="utf-8"))
            altered["records"][0]["source_image_verified"]=True
            target=Path(tmp)/original.name
            target.write_text(json.dumps(altered),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Scan verification"):
                prepare(target)

    def test_reject_gs2_independence(self):
        with tempfile.TemporaryDirectory() as tmp:
            original=self.paths[0]
            altered=json.loads(original.read_text(encoding="utf-8"))
            item=next(x for x in altered["records"] if x["original_source_class"]=="gravestone")
            item["independent_from_pine_grove_photo"]=True
            target=Path(tmp)/original.name
            target.write_text(json.dumps(altered),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"G.S.2"):
                prepare(target)


if __name__=="__main__":
    unittest.main()
