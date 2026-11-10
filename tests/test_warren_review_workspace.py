"""Offline review workspace is complete, local and incapable of approving entries."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_warren_review_workspace import build, candidates, image_payload, pdf_payload


class WarrenReviewWorkspaceTests(unittest.TestCase):
    def test_provisional_records_count_and_source_distinctions(self):
        rows=candidates()
        self.assertEqual(len(rows),140)
        self.assertEqual(len({x["id"] for x in rows}),140)
        self.assertEqual(
            {p:sum(x["printed_page"]==p for x in rows) for p in (9,10,11,12)},
            {9:26,10:35,11:40,12:39})
        self.assertEqual(sum(x["source_class"]=="gravestone" for x in rows),24)
        self.assertTrue(all(x["review_status"]=="requires_page_image_check" for x in rows))

    def test_workspace_exports_drafts_no_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"review.html"
            self.assertEqual(build(path),140)
            html=path.read_text(encoding="utf-8")
            self.assertIn("warren-review-proposals.json",html)
            self.assertIn("unsigned_draft_not_accepted",html)
            self.assertIn("private offline draft workspace",html)
            self.assertNotIn("vital_record_entries",html)
            self.assertNotIn("fetch(",html)
            self.assertNotIn("indexedDB",html)
            with self.assertRaises(FileExistsError):
                build(path)

    def test_incorrect_pdf_checksum_is_rejected_before_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=Path(tmp)/"wrong.pdf"
            fake.write_bytes(b"%PDF-1.4\\nnot the original book")
            with self.assertRaisesRegex(ValueError,"PDF checksum differs"):
                pdf_payload(fake)

    def test_scan_image_not_required_or_uploadable(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            self.assertEqual(image_payload(folder),{})
            (folder/"warren_scan_p12.png").write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"bounded PNG"):
                image_payload(folder)


if __name__=="__main__":
    unittest.main()
