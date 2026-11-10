"""Validate CPC v1 domain exchange schemas with synthetic valid/invalid fixtures."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TYPES = {"GEO": "material_candidate", "VIT": "event", "IMG": "photo_original"}


def record(domain, record_type):
    return {
        "schema_version": "1.0.0",
        "domain": domain,
        "entity_ref": f"{domain}:{record_type}:synthetic-001",
        "record_type": record_type,
        "source_local_id": "synthetic-001",
        "source_ref": "HIS:work:synthetic-source",
        "evidence_locator": "test page 1",
        "confidence": "tentative",
        "review_status": "candidate",
        "observed_at": "2026-11-10T14:00:00Z",
        "independently_observed": False,
        "rights": {
            "access": "restricted",
            "analysis": "unknown",
            "publication": "prohibited"
        },
        "links": []
    }


class VersionedRecordContracts(unittest.TestCase):
    def test_valid_and_invalid_fixture_for_each_domain(self):
        for domain, typ in TYPES.items():
            with self.subTest(domain=domain):
                path = ROOT / "domains" / domain / "contracts/v1/record.schema.json"
                schema = json.loads(path.read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)
                checker = Draft202012Validator(schema, format_checker=FormatChecker())
                good = record(domain, typ)
                self.assertEqual(list(checker.iter_errors(good)), [])
                invalid = copy.deepcopy(good)
                invalid["entity_ref"] = "CEM:person:synthetic-001"
                self.assertTrue(list(checker.iter_errors(invalid)), "foreign domain namespace must fail")
                invalid = copy.deepcopy(good)
                invalid["rights"]["publication"] = "allowed_without_review"
                self.assertTrue(list(checker.iter_errors(invalid)), "invalid rights must fail")
                invalid = copy.deepcopy(good)
                invalid["observed_at"] = "not a timestamp"
                self.assertTrue(list(checker.iter_errors(invalid)), "invalid timestamp must fail")
                invalid = copy.deepcopy(good)
                invalid["links"] = [{"target_ref":"VIT:event:synthetic","relationship":"possible_match"}]
                self.assertTrue(list(checker.iter_errors(invalid)), "uncited link must fail")

    def test_cross_domain_links_are_cited_reviewable_candidates(self):
        path = ROOT / "domains/GEO/contracts/v1/record.schema.json"
        checker = Draft202012Validator(json.loads(path.read_text(encoding="utf-8")), format_checker=FormatChecker())
        candidate = record("GEO", "material_candidate")
        candidate["links"] = [{
            "target_ref": "IMG:photo_original:synthetic-002",
            "relationship": "visually_suggested_material",
            "evidence_ref": "HIS:work:synthetic-source",
            "review_status": "candidate"
        }]
        self.assertEqual(list(checker.iter_errors(candidate)), [])
        self.assertEqual(candidate["links"][0]["review_status"], "candidate")


if __name__ == "__main__":
    unittest.main()
