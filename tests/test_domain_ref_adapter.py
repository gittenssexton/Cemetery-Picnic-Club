"""Canonical reference adapter tests: source existence and candidate-only links."""
import sqlite3
import unittest
from pathlib import Path
from scripts.domain_ref_adapter import register_existing, link_candidate

ROOT = Path(__file__).resolve().parents[1]

class CanonicalReferenceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for f in sorted((ROOT / "db/migrations").glob("*.sql")):
            self.db.executescript(f.read_text(encoding="utf-8"))
        self.db.execute("INSERT INTO cemeteries(id,name,town) VALUES ('fixture-c','Synthetic','Test')")
        self.db.execute("INSERT INTO markers(id,cemetery_id) VALUES ('fixture-m','fixture-c')")
        self.db.execute("""INSERT INTO images
            (id,marker_id,file_name,rights_basis,analysis_authorized,publish_authorized)
            VALUES ('fixture-i','fixture-m','original.jpg','unknown',0,0)""")
        self.addCleanup(self.db.close)

    def test_register_source_rows_not_guesses(self):
        with self.assertRaises(ValueError):
            register_existing(self.db, "VIT", "event", "missing")
        with self.assertRaises(ValueError):
            register_existing(self.db, "BAD", "person", "fixture-m")
        with self.assertRaises(ValueError):
            register_existing(self.db, "CEM", "marker", "fixture;DROP")
        ref = register_existing(self.db, "CEM", "marker", "fixture-m")
        self.assertEqual(ref, "CEM:marker:fixture-m")
        register_existing(self.db, "CEM", "marker", "fixture-m")
        self.assertEqual(self.db.execute("SELECT count(*) FROM domain_entity_refs").fetchone()[0], 1)

    def test_link_is_cited_reversible_and_does_not_publish(self):
        marker = register_existing(self.db, "CEM", "marker", "fixture-m")
        photo = register_existing(self.db, "IMG", "photo_original", "fixture-i")
        with self.assertRaises(ValueError):
            link_candidate(self.db, "uncited", marker, photo, "photo_of", "", "page 1")
        link_candidate(self.db, "fixture-link", marker, photo, "photo_of",
                       "HIS:work:synthetic", "test image 1")
        self.assertEqual(self.db.execute("""SELECT review_status,publication_permission
            FROM domain_evidence_links WHERE id='fixture-link'""").fetchone(),
                         ("candidate", "unknown"))
        self.db.execute("UPDATE domain_evidence_links SET review_status='rejected' WHERE id='fixture-link'")
        self.db.execute("DELETE FROM domain_evidence_links WHERE id='fixture-link'")
        self.assertEqual(self.db.execute("SELECT count(*) FROM images").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT publish_authorized FROM images").fetchone()[0], 0)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

if __name__ == "__main__":
    unittest.main()
