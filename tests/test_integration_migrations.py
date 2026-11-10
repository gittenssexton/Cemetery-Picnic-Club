"""Verify integrated SQLite migrations with genuine foreign-key enforcement.

Run with: python3 -m unittest tests/test_integration_migrations.py -v
All data is synthetic, stays in memory, and never accesses Cloudflare D1.
"""
import sqlite3
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "db" / "migrations"
EXPECTED = [
    "0001_initial.sql",
    "0002_global_research_core.sql",
    "0003_stone_identification.sql",
    "0004_geological_map_core.sql",
    "0005_monument_analysis.sql",
    "0006_new_england_vital_records.sql",
    "0007_domain_evidence_links.sql",
    "0008_metadata_import_audit.sql",
    "0009_vital_ocr_review_queue.sql",
    "0010_vital_manual_review_evidence.sql",
]


def fresh_database():
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    for filename in EXPECTED:
        db.executescript((MIGRATIONS / filename).read_text(encoding="utf-8"))
    return db


class IntegrationMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = fresh_database()
        self.addCleanup(self.db.close)

    def test_all_ten_migrations_exist_in_order(self):
        self.assertEqual(sorted(p.name for p in MIGRATIONS.glob("*.sql")), EXPECTED)

    def test_fk_integrity_and_clean_start(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_no_duplicate_create_table_names_across_migrations(self):
        import re
        names = []
        for filename in EXPECTED:
            sql = (MIGRATIONS / filename).read_text(encoding="utf-8")
            names.extend(re.findall(
                r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][a-zA-Z_0-9]*)",
                sql, re.I
            ))
        duplicates = [n for n, count in Counter(names).items() if count > 1]
        self.assertEqual(duplicates, [], "CREATE TABLE names silently shadowed: " + str(duplicates))

    def test_two_different_motif_interpretation_entities(self):
        for table in ("motif_interpretations", "marker_motif_interpretation_candidates"):
            self.assertIsNotNone(self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone())
        columns = lambda t: {row[1] for row in self.db.execute("PRAGMA table_info(" + t + ")")}
        self.assertIn("interpretation_text", columns("motif_interpretations"))
        self.assertIn("marker_id", columns("marker_motif_interpretation_candidates"))

    def test_geology_source_only_is_not_material_attribution(self):
        self.db.execute(
            "INSERT INTO geology_map_sources(id,title,provider) VALUES(?,?,?)",
            ("map-synthetic", "Synthetic map", "test")
        )
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM geology_map_sources").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM stone_material_candidates").fetchone()[0], 0)

    def test_vital_collection_only_is_not_verified_person(self):
        self.db.execute("""INSERT INTO vital_record_collections
            (id,title,repository,state_code,canonical_url)
            VALUES ('collection-synthetic','Synthetic ledger','Test archive','MA','https://example.invalid/ledger')""")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM vital_record_collections").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM persons").fetchone()[0], 0)

    def test_local_field_draft_does_not_publish_image(self):
        self.db.execute(
            "INSERT INTO field_drafts(id,data_json) VALUES (?,?)",
            ("draft-synthetic", '{"synthetic":true}')
        )
        self.assertEqual(self.db.execute("SELECT sync_status FROM field_drafts").fetchone()[0], "local_only")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0], 0)

    def test_reject_invalid_foreign_key(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO geology_units(id,map_id,original_symbol) VALUES (?,?,?)",
                ("unit-synthetic", "missing-map", "X")
            )

    def test_candidate_link_deletion_preserves_original_records(self):
        self.db.execute("INSERT INTO cemeteries(id,name,town) VALUES ('cem-test','Test','Test')")
        self.db.execute("INSERT INTO markers(id,cemetery_id) VALUES ('marker-test','cem-test')")
        self.db.execute("""INSERT INTO images
            (id,marker_id,sha256,rights_basis,analysis_authorized,publish_authorized)
            VALUES ('img-test','marker-test','synthetic-sha','unknown',0,0)""")
        self.db.execute("""INSERT INTO material_types
            (id,display_name,geology_class,distinguishing_features)
            VALUES ('mat-test','Synthetic stone','unknown','Synthetic fixture')""")
        self.db.execute("""INSERT INTO stone_observations
            (id,marker_id,photograph_id,evidence_notes)
            VALUES ('obs-test','marker-test','img-test','Visual only')""")
        self.db.execute("""INSERT INTO stone_material_candidates
            (id,observation_id,material_id,confidence)
            VALUES ('candidate-test','obs-test','mat-test','possible')""")
        self.db.execute("DELETE FROM stone_material_candidates WHERE id='candidate-test'")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM stone_observations").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM markers").fetchone()[0], 1)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
