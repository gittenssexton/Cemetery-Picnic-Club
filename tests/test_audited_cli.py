"""Execute the documented audited-import CLI against an isolated local database."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def example():
    return [{
        "schema_version": "1.0.0",
        "entity_ref": "GEO:geologic_map:cli-synthetic-map",
        "domain": "GEO",
        "record_type": "geologic_map",
        "source_local_id": "cli-synthetic-map",
        "source_ref": "HIS:work:synthetic",
        "evidence_locator": "fixture inventory p. 1",
        "confidence": "tentative",
        "review_status": "candidate",
        "observed_at": "2026-11-10T15:00:00Z",
        "rights": {
            "access": "restricted",
            "analysis": "unknown",
            "publication": "prohibited"
        },
        "links": [],
        "attributes": {"title": "CLI synthetic fixture", "provider": "Unit Test"}
    }]


class AuditedCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "input.json"
        self.database = Path(self.tmp.name) / "local.sqlite"
        self.path.write_text(json.dumps(example()), encoding="utf-8")
        with sqlite3.connect(str(self.database)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            for p in sorted((ROOT / "db/migrations").glob("*.sql")):
                db.executescript(p.read_text(encoding="utf-8"))

    def call(self, *extra):
        return subprocess.run(
            [sys.executable, "-m", "scripts.ingest_audited_metadata",
             str(self.path), *extra],
            cwd=ROOT, capture_output=True, text=True, check=False
        )

    def test_dry_run_then_apply_then_replay(self):
        dry = self.call()
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn("DRY RUN ONLY", dry.stdout)
        with sqlite3.connect(str(self.database)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM geology_map_sources").fetchone()[0], 0)

        first = self.call("--apply", "--database", str(self.database))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn('"inserted": 1', first.stdout)

        replay = self.call("--apply", "--database", str(self.database))
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertIn('"duplicates": 1', replay.stdout)
        with sqlite3.connect(str(self.database)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM geology_map_sources").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM metadata_import_records").fetchone()[0], 1)
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_reject_missing_database_and_changed_metadata(self):
        self.assertNotEqual(self.call("--apply").returncode, 0)
        first = self.call("--apply", "--database", str(self.database))
        self.assertEqual(first.returncode, 0, first.stderr)
        altered = example()
        altered[0]["attributes"]["title"] = "Altered without review"
        self.path.write_text(json.dumps(altered), encoding="utf-8")
        conflict = self.call("--apply", "--database", str(self.database))
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("Conflicting reimport", conflict.stderr)
        with sqlite3.connect(str(self.database)) as db:
            self.assertEqual(db.execute("SELECT title FROM geology_map_sources").fetchone()[0],
                             "CLI synthetic fixture")


if __name__ == "__main__":
    unittest.main()
