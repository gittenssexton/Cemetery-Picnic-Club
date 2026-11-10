"""Combined camera/geology migration contract. No production D1 mutation."""
from pathlib import Path
import re
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / 'db' / 'migrations'

class IntegratedMigrationContractTests(unittest.TestCase):
    def test_migration_numbers_are_unique(self):
        paths = sorted(MIGRATIONS.glob('*.sql'))
        self.assertGreaterEqual(len(paths), 4)
        ids = []
        for path in paths:
            match = re.match(r'^(\d{4})_', path.name)
            self.assertIsNotNone(match, f'Unversioned migration: {path.name}')
            ids.append(int(match.group(1)))
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate numbered migrations in unified pilot')
        self.assertEqual(ids, sorted(ids))

    def test_both_domains_create_in_one_database(self):
        db = sqlite3.connect(':memory:')
        try:
            db.execute('PRAGMA foreign_keys=ON')
            for path in sorted(MIGRATIONS.glob('*.sql')):
                db.executescript(path.read_text(encoding='utf-8'))
            names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            for table in ('markers','geology_map_sources','geology_units','geology_site_context',
                          'marker_form_observations','carving_feature_observations',
                          'lettering_style_observations'):
                self.assertIn(table,names)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
        finally:
            db.close()

    def test_reviewed_geology_seeds_do_not_assign_gravestones(self):
        db = sqlite3.connect(':memory:')
        try:
            db.execute('PRAGMA foreign_keys=ON')
            for path in sorted(MIGRATIONS.glob('*.sql')):
                db.executescript(path.read_text(encoding='utf-8'))
            for name in ('0005_geology_map_sources.sql','0006_ma_zen1983_symbol_crosswalk.sql',
                         '0007_warren_quadrangle_local_sources.sql'):
                db.executescript((ROOT/'db'/'seeds'/name).read_text(encoding='utf-8'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM geology_site_context').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM geology_units').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM geology_map_sources').fetchone()[0],9)
        finally:
            db.close()

if __name__=='__main__':
    unittest.main()
