"""Warren source-event acceptance is explicit, scan-cited, and non-identifying."""
import sqlite3
import unittest
from pathlib import Path

from scripts.stage_warren_ocr_review import FILES, ROOT, stage
from scripts.review_warren_vitals import record_scan_review, accept_scan_reviewed_event


class ScanAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for p in sorted((ROOT/"db/migrations").glob("*.sql")):
            self.db.executescript(p.read_text(encoding="utf-8"))
        self.db.executescript((ROOT/"db/seeds/0006_new_england_vital_catalog.sql").read_text(encoding="utf-8"))
        stage(self.db,[ROOT/"data/vital-records"/FILES[0]])
        self.addCleanup(self.db.close)
        self.candidate="MA-WARREN-RICE1910-BIRTH-P009-001"
        self.gravestone="MA-WARREN-RICE1910-BIRTH-P009-007"

    def review(self,candidate=None,decision="confirmed",code=None):
        return record_scan_review(
            self.db,candidate_id=candidate or self.candidate,reviewer_id="fixture-reviewer",
            reviewed_at="2026-11-10T16:00:00Z",image_url="https://example.invalid/scan-test.jpg",
            image_sequence=17,image_sha256="a"*64,
            verbatim_line="Synthetic verified source line for tests only",
            verified_name="Example Fixture",verified_date="1785-10-11",
            verified_source_code=code,decision=decision,
            notes="test fixture not a real page review")

    def grant_fixture_rights(self):
        self.db.execute("""UPDATE vital_record_collections
            SET ingestion_authorization='reviewed_source_entries',
                rights_status='verified_public_domain'
            WHERE id='ma-warren-1849-rice1910'""")

    def counts(self):
        return tuple(self.db.execute(
            "SELECT (SELECT count(*) FROM vital_record_entries),"
            " (SELECT count(*) FROM persons),(SELECT count(*) FROM burials),"
            " (SELECT count(*) FROM vital_entity_match_candidates)").fetchone())

    def test_no_source_event_without_explicit_rights_and_review(self):
        review=self.review()
        self.assertEqual(self.counts(),(0,0,0,0))
        with self.assertRaisesRegex(ValueError,"metadata-only"):
            with self.db:
                accept_scan_reviewed_event(self.db,candidate_id=self.candidate,
                                           review_id=review,accepted_by="editor-fixture")
        self.grant_fixture_rights()
        with self.assertRaisesRegex(ValueError,"Candidate and page-review"):
            with self.db:
                accept_scan_reviewed_event(self.db,candidate_id=self.gravestone,
                                           review_id=review,accepted_by="editor-fixture")
        self.assertEqual(self.counts(),(0,0,0,0))

    def test_reviewed_source_entry_separate_from_person_and_burial(self):
        review=self.review()
        self.grant_fixture_rights()
        with self.db:
            entry=accept_scan_reviewed_event(self.db,candidate_id=self.candidate,
                review_id=review,accepted_by="editor-fixture")
        self.assertEqual(self.counts(),(1,0,0,0))
        self.assertEqual(self.db.execute("""SELECT privacy_status,extraction_confidence,
            entry_verbatim FROM vital_record_entries WHERE id=?""",(entry,)).fetchone(),
            ("restricted","verified_against_page","Synthetic verified source line for tests only"))
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(),[])
        with self.assertRaises(ValueError):
            with self.db:
                accept_scan_reviewed_event(self.db,candidate_id=self.candidate,
                    review_id=review,accepted_by="editor-fixture")

    def test_rejected_or_incomplete_review_never_promoted(self):
        review=self.review(decision="needs_correction")
        self.grant_fixture_rights()
        with self.assertRaisesRegex(ValueError,"confirmed scan"):
            with self.db:
                accept_scan_reviewed_event(self.db,candidate_id=self.candidate,
                    review_id=review,accepted_by="editor-fixture")
        self.assertEqual(self.counts(),(0,0,0,0))
        with self.assertRaises(ValueError):
            self.review(candidate=self.gravestone,code=None)

    def test_gs2_provenance_remains_gravestone_and_not_independent(self):
        review=self.review(candidate=self.gravestone,code="G.S.2.")
        self.grant_fixture_rights()
        with self.db:
            entry=accept_scan_reviewed_event(self.db,candidate_id=self.gravestone,
                 review_id=review,accepted_by="editor-fixture")
        self.assertEqual(self.db.execute(
            "SELECT original_source_class,printed_source_code,privacy_status "
            "FROM vital_record_entries WHERE id=?",(entry,)).fetchone(),
            ("gravestone","G.S.2.","restricted"))
        self.assertEqual(self.counts(),(1,0,0,0))

    def test_review_evidence_is_append_only(self):
        review=self.review()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE vital_ocr_page_reviews SET verified_name='edited' WHERE id=?",(review,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM vital_ocr_page_reviews WHERE id=?",(review,))
        self.assertEqual(self.db.execute("SELECT count(*) FROM vital_ocr_page_reviews").fetchone()[0],1)

    def test_invalid_scan_checksum_and_sequence_rejected(self):
        with self.assertRaises(ValueError):
            record_scan_review(self.db,candidate_id=self.candidate,reviewer_id="fixture-reviewer",
                reviewed_at="2026-11-10T16:00:00Z",image_url="https://example.invalid/a.jpg",
                image_sequence=-1,image_sha256="invalid",verbatim_line="test",
                verified_name="Test")


if __name__=="__main__":
    unittest.main()
