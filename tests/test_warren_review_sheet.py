"""Review worksheet must preserve candidate lineage and never fabricate approval."""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.export_warren_review_sheet import HEADERS, build_rows
from scripts.stage_warren_ocr_review import ROOT, FILES


class WarrenReviewSheetTests(unittest.TestCase):
    def test_all_101_entries_and_empty_attestation_fields(self):
        rows=build_rows([ROOT/"data/vital-records"/n for n in FILES])
        self.assertEqual(len(rows),101)
        self.assertEqual(len({x["candidate_id"] for x in rows}),101)
        self.assertEqual(sum(x["gs2_dependent"]=="YES" for x in rows),17)
        self.assertEqual(sum(bool(x["ocr_notes"]) for x in rows),16)
        for x in rows:
            for field in HEADERS[10:]:
                self.assertEqual(x[field],"",field)

    def test_csv_cli_no_overwrite_and_no_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"review.csv"
            cmd=[sys.executable,"-m","scripts.export_warren_review_sheet",
                 "--output",str(out)]
            first=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(first.returncode,0,first.stderr)
            with out.open(encoding="utf-8-sig",newline="") as source:
                rows=list(csv.DictReader(source))
            self.assertEqual(len(rows),75)
            self.assertFalse(any(x["review_decision"] for x in rows))
            second=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(second.returncode,0)
            self.assertIn("Refusing to overwrite",second.stderr)


if __name__=="__main__":
    unittest.main()
