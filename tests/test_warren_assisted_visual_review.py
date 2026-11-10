"""Assisted scan readings are auditable leads, never fabricated human approvals."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/vital-records"


class WarrenAssistedVisualReviewTests(unittest.TestCase):
    def test_visual_findings_have_matching_candidates_and_pdf_provenance(self):
        record=json.loads((DATA/"warren-1910-assisted-visual-review-2026-11-10.json").read_text(encoding="utf-8"))
        self.assertEqual(record["schema"],"cpc-warren-assisted-visual-check-v1")
        self.assertEqual(record["review_status"],"proposed_correction_pending_named_human_review")
        self.assertFalse(record["source_record_changes"])
        self.assertEqual(record["accepted_vital_events"],0)
        self.assertEqual(len(record["findings"]),13)
        self.assertEqual(len({x["candidate_id"] for x in record["findings"]}),13)
        pdf=record["source_pdf"]
        self.assertEqual(len(pdf["sha256"]),64)
        self.assertEqual(pdf["pages"]["9"]["pdf_index"],12)
        self.assertEqual(pdf["pages"]["10"]["pdf_index"],13)
        self.assertEqual(pdf["pages"]["11"]["pdf_index"],14)
        self.assertTrue(all(len(v["render_sha256"])==64 for v in pdf["pages"].values()))
        source={}
        for page in (9,10,11):
            batch=DATA/f"warren-1910-births-p{page:03d}-batch{page-8:02d}.json"
            original=json.loads(batch.read_text(encoding="utf-8"))
            for candidate in original["records"]:
                source[candidate["id"]]=(page,candidate)
                self.assertIs(candidate["source_image_verified"],False)
                self.assertEqual(candidate["review_status"],"requires_page_image_check")
        for finding in record["findings"]:
            ident=finding["candidate_id"]
            self.assertIn(ident,source)
            self.assertEqual(finding["printed_page"],source[ident][0])
            self.assertEqual(finding["review_status"],"assisted_visual_read_pending_human_signoff")
            self.assertTrue(finding["visual_reading"])
            self.assertNotIn("human_reviewer_id",finding)
            self.assertNotIn("accepted_entry_id",finding)

    def test_gravestone_dependency_unchanged_in_original_batches(self):
        code_count=0
        for page in (9,10,11):
            batch=json.loads((DATA/f"warren-1910-births-p{page:03d}-batch{page-8:02d}.json").read_text(encoding="utf-8"))
            for x in batch["records"]:
                if x["original_source_class"]=="gravestone":
                    code_count+=1
                    self.assertIs(x["independent_from_pine_grove_photo"],False)
        self.assertEqual(code_count,14)


if __name__=="__main__":
    unittest.main()
