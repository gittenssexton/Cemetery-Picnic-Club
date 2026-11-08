"""Research-core invariants and bibliography importer checks."""
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cpc_importer", ROOT / "scripts/import_bibliography.py")
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

def init_db():
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    for path in ("db/migrations/0001_initial.sql",
                 "db/migrations/0002_global_research_core.sql",
                 "db/seeds/0001_pine_grove_warren.sql",
                 "db/seeds/0002_carver_motifs.sql",
                 "db/seeds/0003_global_research_sources.sql"):
        db.executescript((ROOT / path).read_text(encoding="utf-8"))
    return db

class ResearchCoreTests(unittest.TestCase):
    def setUp(self):
        self.db = init_db()

    def tearDown(self):
        self.db.close()

    def test_nonlocal_sources_and_collections_not_attached_to_cemeteries(self):
        self.assertEqual(self.db.execute("SELECT count(*) FROM research_works").fetchone()[0], 7)
        self.assertEqual(self.db.execute("SELECT count(*) FROM research_collections").fetchone()[0], 2)
        self.db.execute("INSERT INTO geographic_scopes(id,name,scope_type) VALUES ('global-test','Southern Africa','region')")
        self.db.execute("INSERT INTO research_work_geography(work_id,scope_id) VALUES (?,?)",
                        ("work-forbes-1927","global-test"))
        self.assertEqual(self.db.execute("SELECT count(*) FROM cemeteries").fetchone()[0], 1)

    def test_interpretations_have_distinct_citations(self):
        self.assertEqual(self.db.execute("SELECT count(*) FROM motif_interpretations").fetchone()[0], 4)
        missing = self.db.execute("""SELECT i.id FROM motif_interpretations i
            LEFT JOIN interpretation_citations e ON e.interpretation_id=i.id
            WHERE e.citation_id IS NULL""").fetchall()
        self.assertEqual(missing, [])
        self.db.execute("""INSERT INTO motif_interpretations
            (id,motif_id,interpretation_text,scope_id)
            VALUES ('competing','motif-winged-cherub','Alternate interpretation','scope-global')""")
        self.assertEqual(self.db.execute("""SELECT count(*) FROM motif_interpretations
            WHERE motif_id='motif-winged-cherub'""").fetchone()[0], 2)

    def test_no_auto_link_from_motif_to_marker_or_maker(self):
        self.assertEqual(self.db.execute("SELECT count(*) FROM marker_motifs").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT count(*) FROM maker_research_links").fetchone()[0], 0)

    def test_seed_repeatable(self):
        src=(ROOT/"db/seeds/0003_global_research_sources.sql").read_text(encoding="utf-8")
        self.db.executescript(src)
        self.assertEqual(self.db.execute("SELECT count(*) FROM research_works").fetchone()[0], 7)

    def test_invalid_date_range_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""INSERT INTO motif_interpretations
            (id,motif_id,interpretation_text,period_start_year,period_end_year)
            VALUES ('bad','motif-urn','Bad dates',1900,1700)""")

    def test_importer_template_validates(self):
        rows,errors=importer.load(ROOT/"data/templates/research_works_example.csv")
        self.assertEqual(errors,[])
        self.assertEqual(len(rows),1)

    def test_importer_rejects_duplicates_and_bad_rights_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"x.csv"
            header=",".join(importer.FIELDS)
            values=["duplicate","A source","","2000","article","","","","","","","","http://example.org/a","not_acquired","unknown","bibliography_only"]
            path.write_text(header+"\n"+",".join(values)+"\n"+",".join(values)+"\n",encoding="utf-8")
            _,errors=importer.load(path)
            self.assertTrue(any("duplicate id" in e for e in errors))
            self.assertTrue(any("HTTPS" in e for e in errors))

    def test_importer_inserts_only_on_explicit_call(self):
        rows,errors=importer.load(ROOT/"data/templates/research_works_example.csv")
        self.assertFalse(errors)
        before=self.db.execute("SELECT count(*) FROM research_works").fetchone()[0]
        importer.import_rows(self.db,rows)
        self.assertEqual(self.db.execute("SELECT count(*) FROM research_works").fetchone()[0],before+1)
        with self.assertRaises(sqlite3.IntegrityError):
            importer.import_rows(self.db,rows)

    def test_cross_cemetery_relation_not_confused_with_identity(self):
        self.db.execute("""INSERT INTO cemeteries(id,name,town,state) VALUES
            ('test-remote','Synthetic test cemetery','Test Town','VT')""")
        self.db.execute("""INSERT INTO markers(id,cemetery_id) VALUES
            ('test-marker','test-remote')""")
        self.db.execute("""INSERT INTO marker_motifs(marker_id,motif_id,confidence) VALUES
            ('test-marker','motif-winged-cherub','tentative')""")
        self.assertEqual(self.db.execute("""SELECT c.id FROM cemeteries c
            JOIN markers m ON m.cemetery_id=c.id
            JOIN marker_motifs mm ON mm.marker_id=m.id
            WHERE mm.motif_id='motif-winged-cherub'""").fetchall(),[("test-remote",)])
        self.assertEqual(self.db.execute("SELECT count(*) FROM marker_person_links WHERE marker_id='test-marker'").fetchone()[0],0)

if __name__=="__main__":
    unittest.main()
