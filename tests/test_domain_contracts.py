"""Contract checks for discipline-specific CPC vocabularies and migrations."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("domain_validator",ROOT/"scripts/validate_domains.py")
validator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class DomainContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads((ROOT/"architecture/domain-registry.json").read_text(encoding="utf-8"))

    def test_domain_registry_valid(self):
        self.assertEqual(validator.check_registry(self.registry),[])

    def test_local_migration_versions_unique(self):
        self.assertEqual(validator.check_files(ROOT),[])

    def test_reject_duplicate_domain(self):
        bad=json.loads(json.dumps(self.registry))
        bad["domains"].append(dict(bad["domains"][0]))
        self.assertTrue(any("duplicate domain" in s for s in validator.check_registry(bad)))

    def test_reject_migration_collision_in_plan(self):
        bad=json.loads(json.dumps(self.registry))
        bad["migrations"]["integration_plan"]=["0004_geological_map_core.sql","0004_monument_analysis.sql"]
        self.assertTrue(any("duplicate" in s for s in validator.check_registry(bad)))

    def test_distinct_vital_event_and_burial(self):
        d={x["code"]:x for x in self.registry["domains"]}
        self.assertIn("event",d["VIT"]["entities"])
        self.assertIn("burial",d["CEM"]["entities"])
        self.assertNotEqual(d["VIT"]["terms"]["event"],d["CEM"]["terms"]["burial"])

    def test_distinct_geology_context_from_monument_material(self):
        d={x["code"]:x for x in self.registry["domains"]}
        self.assertIn("geologic_unit",d["GEO"]["terms"])
        self.assertIn("material_candidate",d["GEO"]["terms"])
        self.assertNotEqual(d["GEO"]["terms"]["geologic_unit"],d["GEO"]["terms"]["material_candidate"])

    def test_canonical_ref_format(self):
        self.assertIsNotNone(validator.REF.fullmatch("GEO:material_candidate:slate-123"))
        self.assertIsNone(validator.REF.fullmatch("slate-123"))
        self.assertIsNone(validator.REF.fullmatch("BAD:material:slate"))

if __name__=="__main__":unittest.main()
