"""SQLite/D1 pilot schema smoke tests. Run: python -m unittest discover -s tests -v"""
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = (ROOT / "db/migrations/0001_initial.sql").read_text(encoding="utf-8")
GLOBAL_SCHEMA = (ROOT / "db/migrations/0002_global_research_core.sql").read_text(encoding="utf-8")
SEED = (ROOT / "db/seeds/0001_pine_grove_warren.sql").read_text(encoding="utf-8")
MOTIFS = (ROOT / "db/seeds/0002_carver_motifs.sql").read_text(encoding="utf-8")
GLOBAL_SEED = (ROOT / "db/seeds/0003_global_research_sources.sql").read_text(encoding="utf-8")


class PineGroveDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA)
        self.db.executescript(GLOBAL_SCHEMA)
        self.db.executescript(SEED)
        self.db.executescript(MOTIFS)
        self.db.executescript(GLOBAL_SEED)

    def tearDown(self):
        self.db.close()

    def count(self, table):
        return self.db.execute("SELECT count(*) FROM " + table).fetchone()[0]

    def test_pilot_site_and_research_candidates(self):
        self.assertEqual(self.count("cemeteries"), 1)
        self.assertEqual(self.count("markers"), 2)
        self.assertEqual(self.count("persons"), 2)
        self.assertEqual(self.count("sources"), 4)
        self.assertEqual(self.count("claim_evidence"), 5)
        self.assertEqual(self.count("marker_positions"), 0)
        self.assertEqual(self.count("images"), 0)
        self.assertEqual(self.count("burials"), 0)
        statuses = self.db.execute("SELECT DISTINCT verification_status FROM markers").fetchall()
        self.assertEqual(statuses, [("research_candidate",)])

    def test_maker_claims_are_sourced_and_not_equated(self):
        rows = self.db.execute(
            "SELECT c.id,c.object_id,e.source_id FROM claims c "
            "JOIN claim_evidence e ON e.claim_id=c.id "
            "WHERE c.predicate='attributed_carver' ORDER BY c.id"
        ).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0][1], rows[1][1])
        self.assertTrue(all(r[2] == "src-carvers-draft" for r in rows))

    def test_idempotent_seed(self):
        self.db.executescript(SEED)
        self.db.executescript(MOTIFS)
        self.db.executescript(GLOBAL_SEED)
        self.assertEqual(self.count("markers"), 2)
        self.assertEqual(self.count("claim_evidence"), 5)

    def test_rights_cannot_be_unknown_but_published(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO images(id,rights_basis,publish_authorized) VALUES (?,?,?)",
                ("bad-publish","unknown",1),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO images(id,rights_basis,analysis_authorized) VALUES (?,?,?)",
                ("bad-analysis","unknown",1),
            )

    def test_comparative_motif_vocabulary_does_not_auto_attribute(self):
        self.assertEqual(self.count("motifs"), 19)
        self.assertEqual(self.count("marker_motifs"), 0)
        self.assertEqual(self.count("craftspeople"), 7)
        self.assertEqual(self.count("marker_positions"), 0)

    def test_marker_can_commemorate_multiple_persons(self):
        self.db.execute("INSERT INTO persons(id,display_name) VALUES (?,?)",("p-test","Second Person"))
        self.db.execute(
            "INSERT INTO marker_person_links(marker_id,person_id,relationship_type) VALUES (?,?,?)",
            ("marker-jemima-lincoln","p-test","commemorates"),
        )
        count = self.db.execute(
            "SELECT COUNT(*) FROM marker_person_links WHERE marker_id=?",
            ("marker-jemima-lincoln",),
        ).fetchone()[0]
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
