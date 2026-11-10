"""Metadata intake remains local, explicit and free of identity/material claims."""
import importlib.util
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("metadata", ROOT / "scripts/ingest_domain_metadata.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


def record(domain, typ, attributes=None):
    return {
        "schema_version": "1.0.0",
        "entity_ref": f"{domain}:{typ}:fixture-001",
        "domain": domain, "record_type": typ, "source_local_id": "fixture-001",
        "source_ref": "HIS:work:fixture", "evidence_locator": "page 1",
        "confidence": "tentative", "review_status": "candidate",
        "observed_at": "2026-11-10T15:00:00Z",
        "rights": {"access": "restricted", "analysis": "unknown", "publication": "prohibited"},
        "links": [], "attributes": attributes or {}
    }


class MetadataAdapterTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for p in sorted((ROOT / "db/migrations").glob("*.sql")):
            self.db.executescript(p.read_text(encoding="utf-8"))
        self.addCleanup(self.db.close)

    def test_independent_metadata_intake_with_no_claim_promotion(self):
        fixtures = [
            record("GEO", "geologic_map", {"title": "Synthetic map", "provider": "Fixture"}),
            record("VIT", "collection", {"title": "Synthetic collection",
                "repository": "Fixture archive", "state_code": "MA", "canonical_url": "https://example.invalid"}),
            record("IMG", "field_draft")
        ]
        operations = metadata.plan(fixtures)
        metadata.insert(self.db, operations)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM geology_map_sources").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM vital_record_collections").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT sync_status FROM field_drafts").fetchone()[0], "local_only")
        for table in ("persons", "burials", "markers", "stone_material_candidates", "images",
                      "vital_record_entries", "claims"):
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0], 0)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_duplicate_import_rolls_back_as_one_transaction(self):
        original = record("GEO", "geologic_map", {"title": "Synthetic map", "provider": "Fixture"})
        operations = metadata.plan([original])
        metadata.insert(self.db, operations)
        with self.assertRaises(sqlite3.IntegrityError):
            metadata.insert(self.db, operations)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM geology_map_sources").fetchone()[0], 1)

    def test_reject_unpermitted_domain_and_extra_attributes(self):
        with self.assertRaises(ValueError):
            metadata.plan([record("IMG", "photo_original")])
        with self.assertRaises(ValueError):
            metadata.plan([record("GEO", "geologic_map",
                {"title": "X", "provider": "Y", "marker_id": "auto-matched"})])
        with self.assertRaises(ValueError):
            metadata.plan([record("VIT", "collection",
                {"title": "X", "repository": "Y", "state_code": "NY",
                 "canonical_url": "https://example.invalid"})])

    def test_reject_mismatched_source_id_and_unprocessed_links(self):
        good = record("GEO", "geologic_map", {"title": "Fixture map", "provider": "Fixture"})
        incorrect = dict(good, source_local_id="different-source-id")
        with self.assertRaisesRegex(ValueError, "canonical reference"):
            metadata.plan([incorrect])
        unsupported_link = dict(good, links=[{
            "target_ref": "IMG:photo_original:fixture-001",
            "relationship": "source_suggests",
            "evidence_ref": "HIS:work:fixture",
            "review_status": "candidate"
        }])
        with self.assertRaisesRegex(ValueError, "evidence bridge"):
            metadata.plan([unsupported_link])
        self.assertEqual(self.db.execute("SELECT count(*) FROM geology_map_sources").fetchone()[0], 0)

    def test_reject_invalid_rights_and_duplicate_refs_before_write(self):
        good = record("IMG", "field_draft")
        bad = dict(good)
        bad["rights"] = dict(good["rights"], publication="unreviewed_license")
        with self.assertRaises(ValueError):
            metadata.plan([bad])
        with self.assertRaises(ValueError):
            metadata.plan([good, good])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM field_drafts").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
