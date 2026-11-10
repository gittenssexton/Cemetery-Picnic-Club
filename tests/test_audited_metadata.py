"""Transactional import evidence ledger tests (only synthetic SQLite)."""
import copy
import sqlite3
import unittest
from pathlib import Path

from scripts.ingest_audited_metadata import apply_audited

ROOT = Path(__file__).resolve().parents[1]


def fixture(domain="GEO", typ="geologic_map", source_id="fixture-a"):
    attrs = ({"title": "Synthetic map", "provider": "Test source"} if domain=="GEO"
             else {"title": "Test vital collection", "repository": "Test archive",
                   "state_code": "MA", "canonical_url": "https://example.invalid/source"})
    return {
        "schema_version":"1.0.0", "entity_ref":f"{domain}:{typ}:{source_id}",
        "domain":domain, "record_type":typ, "source_local_id":source_id,
        "source_ref":"HIS:work:synthetic", "evidence_locator":"test inventory p. 1",
        "confidence":"tentative", "review_status":"candidate",
        "observed_at":"2026-11-10T15:00:00Z",
        "rights":{"access":"restricted","analysis":"unknown","publication":"prohibited"},
        "links":[], "attributes":attrs
    }


class AuditedMetadataTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for f in sorted((ROOT/"db/migrations").glob("*.sql")):
            self.db.executescript(f.read_text(encoding="utf-8"))
        self.addCleanup(self.db.close)

    def count(self, table):
        return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_audited_replay_does_not_duplicate_or_change_records(self):
        records = [fixture(), fixture("VIT","collection","fixture-b")]
        first = apply_audited(self.db, records)
        self.assertEqual((first["inserted"], first["duplicates"]), (2,0))
        second = apply_audited(self.db, records)
        self.assertEqual((second["inserted"], second["duplicates"]), (0,2))
        self.assertEqual(self.count("metadata_import_records"),2)
        self.assertEqual(self.count("metadata_import_batches"),1)
        self.assertEqual(self.count("geology_map_sources"),1)
        self.assertEqual(self.count("vital_record_collections"),1)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_modified_payload_rejected_without_overwriting(self):
        original = fixture()
        apply_audited(self.db, [original])
        altered = copy.deepcopy(original)
        altered["rights"]["publication"] = "permitted"
        with self.assertRaisesRegex(ValueError,"Conflicting reimport"):
            apply_audited(self.db,[altered])
        self.assertEqual(self.count("metadata_import_batches"),1)
        self.assertEqual(self.count("geology_map_sources"),1)
        self.assertIn("prohibited",self.db.execute(
            "SELECT rights_json FROM metadata_import_records").fetchone()[0])

    def test_manual_source_drift_is_rejected(self):
        original=fixture()
        apply_audited(self.db,[original])
        self.db.execute("UPDATE geology_map_sources SET title='Altered' WHERE id='fixture-a'")
        with self.assertRaisesRegex(ValueError,"modified source row"):
            apply_audited(self.db,[original])

    def test_conflicting_batch_rolls_back_first_insert(self):
        earlier=fixture(source_id="fixture-existing")
        apply_audited(self.db,[earlier])
        conflict=copy.deepcopy(earlier)
        conflict["attributes"]["title"]="Changed title"
        with self.assertRaisesRegex(ValueError,"Conflicting reimport"):
            apply_audited(self.db,[fixture(source_id="fixture-new"),conflict])
        self.assertEqual(self.count("geology_map_sources"),1)
        self.assertEqual(self.count("metadata_import_records"),1)
        self.assertEqual(self.count("metadata_import_batches"),1)

    def test_untracked_existing_row_requires_review(self):
        self.db.execute("""INSERT INTO geology_map_sources(id,title,provider)
            VALUES ('fixture-a','Existing','Imported elsewhere')""")
        with self.assertRaisesRegex(ValueError,"no matching audit record"):
            apply_audited(self.db,[fixture()])
        self.assertEqual(self.count("metadata_import_records"),0)

    def test_no_person_image_or_material_promotion(self):
        apply_audited(self.db,[fixture()])
        for t in ("persons","images","markers","claims","stone_material_candidates",
                  "vital_record_entries","domain_evidence_links"):
            self.assertEqual(self.count(t),0,t)


if __name__=="__main__":
    unittest.main()
