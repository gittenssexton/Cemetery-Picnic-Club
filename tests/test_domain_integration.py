"""Fresh migration and independent-domain smoke tests (SQLite-compatible D1 schema).

Runs entirely in memory; never touches Cloudflare or production.
"""
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DomainIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        files = sorted((ROOT / "db/migrations").glob("*.sql"))
        self.assertEqual([p.name[:4] for p in files],
                         ["0001", "0002", "0003", "0004", "0005", "0006"])
        for file in files:
            with self.subTest(migration=file.name):
                self.db.executescript(file.read_text(encoding="utf-8"))
        self.assertEqual(self.db.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def tearDown(self):
        self.db.close()

    def test_fresh_migrations_foreign_keys_clean(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        tables = {r[0] for r in self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"geology_map_sources", "marker_form_observations",
                         "vital_record_entries", "images"}.issubset(tables))

    def test_geology_catalog_independent_of_marker_material(self):
        self.db.execute("""INSERT INTO geology_map_sources
            (id,title,provider,geometry_status,validation_status)
            VALUES ('map-a','Synthetic test map','fixture','raster_only','inventory_only')""")
        self.assertEqual(self.db.execute(
            "SELECT validation_status FROM geology_map_sources WHERE id='map-a'"
        ).fetchone()[0], "inventory_only")
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM stone_material_candidates").fetchone()[0], 0)

    def test_vital_source_entry_not_automatically_a_person(self):
        self.db.execute("""INSERT INTO vital_record_collections
            (id,title,repository,state_code,canonical_url)
            VALUES ('collection-a','Synthetic collection','Fixture repository','MA','https://example.org/fixture')""")
        self.db.execute("""INSERT INTO vital_source_documents
            (id,collection_id,source_url)
            VALUES ('doc-a','collection-a','https://example.org/fixture/page')""")
        self.db.execute("""INSERT INTO vital_record_entries
            (id,document_id,local_entry_key,event_type,primary_name_verbatim,entry_verbatim)
            VALUES ('entry-a','doc-a','1','death','Example, Ann','Synthetic entry')""")
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_record_entries").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT count(*) FROM persons").fetchone()[0], 0)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM vital_entity_match_candidates").fetchone()[0], 0)

    def test_image_original_separate_from_field_draft(self):
        self.db.execute("""INSERT INTO images
            (id,file_name,sha256,rights_basis,analysis_authorized,publish_authorized)
            VALUES ('image-a','original.jpg','synthetic-checksum','unknown',0,0)""")
        self.db.execute("""INSERT INTO field_drafts(id,data_json)
            VALUES ('draft-a','{"image_ref":"IMG:photo_original:image-a","status":"unreviewed"}')""")
        self.assertEqual(self.db.execute(
            "SELECT file_name,analysis_authorized,publish_authorized FROM images"
        ).fetchone(), ("original.jpg", 0, 0))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE images SET publish_authorized=1 WHERE id='image-a'")

    def test_candidate_material_and_withdrawal_preserve_sources(self):
        self.db.execute("INSERT INTO cemeteries(id,name,town) VALUES ('c','Test','Test')")
        self.db.execute("INSERT INTO markers(id,cemetery_id) VALUES ('m','c')")
        self.db.execute("""INSERT INTO stone_observations
            (id,marker_id,evidence_notes) VALUES ('observation-a','m','Synthetic observation')""")
        self.db.execute("""INSERT INTO material_types
            (id,display_name,geology_class,distinguishing_features)
            VALUES ('slate','Synthetic slate','metamorphic','Test features')""")
        self.db.execute("""INSERT INTO stone_material_candidates
            (id,observation_id,material_id,confidence)
            VALUES ('candidate-a','observation-a','slate','possible')""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE stone_material_candidates SET confidence='verified' WHERE id='candidate-a'")
        self.db.execute("DELETE FROM stone_material_candidates WHERE id='candidate-a'")
        self.assertEqual(self.db.execute("SELECT count(*) FROM stone_observations").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT count(*) FROM markers").fetchone()[0], 1)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_reject_missing_foreign_key_and_invalid_geocoordinate(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""INSERT INTO vital_source_documents
                (id,collection_id,source_url) VALUES ('orphan','missing','https://example.org')""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""INSERT INTO geology_site_context (id,query_lat,query_lng)
                VALUES ('outside',91,0)""")


if __name__ == "__main__":
    unittest.main()
