"""Stone material identification data tests and non-invasive identification safeguards."""
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parent.parent
FILES=[
"db/migrations/0001_initial.sql",
"db/migrations/0002_global_research_core.sql",
"db/migrations/0003_stone_identification.sql",
"db/seeds/0001_pine_grove_warren.sql",
"db/seeds/0002_carver_motifs.sql",
"db/seeds/0003_global_research_sources.sql",
"db/seeds/0004_stone_materials.sql"
]

class StoneIdTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(":memory:")
  self.db.execute("PRAGMA foreign_keys=ON")
  for file in FILES:self.db.executescript((ROOT/file).read_text(encoding="utf-8"))
 def tearDown(self):self.db.close()
 def test_reference_materials_have_no_marker_claims(self):
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM material_types").fetchone()[0],10)
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM stone_material_candidates").fetchone()[0],0)
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM material_reference_sources").fetchone()[0],10)
 def test_an_observation_is_not_a_verified_identification(self):
  self.db.execute("INSERT INTO stone_observations(id,marker_id,visible_crystals,grain_pattern) VALUES ('obs1','marker-jemima-lincoln','no','fine_uniform')")
  self.db.execute("INSERT INTO stone_material_candidates(id,observation_id,material_id,confidence) VALUES ('c1','obs1','material-slate','possible')")
  with self.assertRaises(sqlite3.IntegrityError):
   self.db.execute("INSERT INTO stone_material_candidates(id,observation_id,material_id,confidence) VALUES ('c2','obs1','material-marble','verified')")
  self.db.execute("INSERT INTO stone_material_candidates(id,observation_id,material_id,confidence,reviewer) VALUES ('c3','obs1','material-marble','verified','Qualified reviewer')")
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM stone_material_candidates WHERE observation_id='obs1'").fetchone()[0],2)
 def test_markers_need_no_material_identification(self):
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM markers").fetchone()[0],2)
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM stone_observations").fetchone()[0],0)
 def test_candidate_rejects_invalid_confidence(self):
  self.db.execute("INSERT INTO stone_observations(id,marker_id) VALUES('obs2','marker-martha-glezen')")
  with self.assertRaises(sqlite3.IntegrityError):
   self.db.execute("INSERT INTO stone_material_candidates(id,observation_id,material_id,confidence) VALUES('bad','obs2','material-slate','certain_by_photo')")
 def test_seed_is_idempotent(self):
  self.db.executescript((ROOT/"db/seeds/0004_stone_materials.sql").read_text(encoding="utf-8"))
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM material_types").fetchone()[0],10)

if __name__=="__main__":unittest.main()
