"""Check ordered, repeatable CPC seeds on fully migrated, in-memory SQLite.

This test executes catalog metadata only; map-symbol crosswalks remain review-gated.
No live Cloudflare database access or third-party file retrieval.
"""
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [
    "0001_pine_grove_warren.sql",
    "0002_carver_motifs.sql",
    "0003_global_research_sources.sql",
    "0004_stone_materials.sql",
    "0005_geology_map_sources.sql",
]


class SeedOrderTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for path in sorted((ROOT / "db/migrations").glob("*.sql")):
            self.db.executescript(path.read_text(encoding="utf-8"))
        self.addCleanup(self.db.close)

    def seed_all(self):
        for name in SEEDS:
            self.db.executescript((ROOT / "db/seeds" / name).read_text(encoding="utf-8"))

    def snapshot(self):
        tables = [row[0] for row in self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )]
        return {name: self.db.execute('SELECT COUNT(*) FROM "' + name + '"').fetchone()[0]
                for name in tables}

    def test_seed_files_have_explicit_order(self):
        self.assertEqual(sorted(p.name for p in (ROOT / "db/seeds").glob("*.sql")), SEEDS)

    def test_all_seeds_load_after_full_schema_and_repeat_without_duplication(self):
        self.seed_all()
        original = self.snapshot()
        self.seed_all()
        self.assertEqual(original, self.snapshot())
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_geology_inventory_does_not_infer_gravestone_material_or_position(self):
        self.seed_all()
        self.assertGreater(self.db.execute("SELECT COUNT(*) FROM geology_map_sources").fetchone()[0], 0)
        for table in ("geology_site_context", "geology_unit_geometries",
                      "stone_material_candidates", "material_provenance_hypotheses",
                      "marker_positions", "burials"):
            self.assertEqual(self.db.execute('SELECT COUNT(*) FROM "' + table + '"').fetchone()[0], 0, table)

    def test_no_seed_adds_unlicensed_original_photographs(self):
        self.seed_all()
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM vital_record_entries").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
