#!/usr/bin/env python3
"""CPC domain metadata intake: dry-run by default; local SQLite only with --apply.

Accepts a JSON array of versioned GEO/VIT/IMG records. Intentionally supports
only GEO map-source metadata, VIT collection metadata, and IMG local field drafts.
Never imports photos, person matches, marker geolocation, or historical claims.
"""
import argparse
import json
import sqlite3
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = {
    ("GEO", "geologic_map"): ("geology_map_sources", ("id", "title", "provider"),
                              ("title", "provider")),
    ("VIT", "collection"): ("vital_record_collections",
                            ("id", "title", "repository", "state_code", "canonical_url"),
                            ("title", "repository", "state_code", "canonical_url")),
    ("IMG", "field_draft"): ("field_drafts", ("id", "data_json", "sync_status"), ()),
}
STATE_CODES = {"MA", "CT", "RI", "NH", "VT", "ME"}


def plan(records):
    if not isinstance(records, list):
        raise ValueError("Input must be an array of records")
    operations = []
    seen = set()
    for n, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"record {n}: expected object")
        domain, typ = record.get("domain"), record.get("record_type")
        key = (domain, typ)
        if key not in MAPPINGS:
            raise ValueError(f"record {n}: ingestion not authorized for {key}")
        schema_path = ROOT / "domains" / domain / "contracts/v1/record.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
        if errors:
            raise ValueError(f"record {n}: invalid domain contract: {errors[0].message}")
        expected_ref = f"{domain}:{typ}:{record.get('source_local_id', '')}"
        if record["entity_ref"] != expected_ref:
            raise ValueError(f"record {n}: canonical reference does not match domain, type and source-local ID")
        # This intake intentionally imports metadata records only. A supplied link
        # must not be silently dropped, because that loses evidence/provenance.
        if record.get("links"):
            raise ValueError(f"record {n}: cross-domain links require the reviewed evidence bridge")
        attributes = record.get("attributes") or {}
        if not isinstance(attributes, dict):
            raise ValueError(f"record {n}: attributes must be an object")
        table, columns, required = MAPPINGS[key]
        if any(k not in attributes or not isinstance(attributes[k], str)
               or not attributes[k].strip() for k in required):
            raise ValueError(f"record {n}: missing or invalid required metadata")
        if set(attributes) - set(required):
            raise ValueError(f"record {n}: unsupported attributes: {sorted(set(attributes)-set(required))}")
        if key == ("VIT", "collection") and attributes["state_code"] not in STATE_CODES:
            raise ValueError(f"record {n}: invalid New England state code")
        if record["entity_ref"] in seen:
            raise ValueError(f"record {n}: duplicate canonical entity_ref")
        seen.add(record["entity_ref"])
        # Source-owned tables keep their local primary keys. The full
        # <domain>:<type>:<id> reference belongs in domain_entity_refs,
        # registered only after the underlying row has been inserted.
        id_value = record["source_local_id"]
        if key == ("IMG", "field_draft"):
            # Keep source and rights metadata; no cloud sync or photo file ingestion.
            values = (id_value, json.dumps(record, sort_keys=True), "local_only")
        else:
            values = (id_value, *(attributes[k].strip() for k in required))
        operations.append((table, columns, values))
    return operations


def insert(connection, operations):
    # Strict table/column allowlists, fixed SQL identifiers, parameterized values.
    with connection:
        for table, columns, values in operations:
            placeholders = ",".join("?" for _ in values)
            query = "INSERT INTO " + table + " (" + ",".join(columns) + ") VALUES (" + placeholders + ")"
            connection.execute(query, values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--database", type=Path)
    args = parser.parse_args()
    if args.apply and (not args.database or not args.database.is_file()):
        parser.error("--apply requires an existing local SQLite --database")
    try:
        operations = plan(json.loads(args.json_file.read_text(encoding="utf-8")))
        if args.apply:
            with sqlite3.connect(str(args.database)) as db:
                db.execute("PRAGMA foreign_keys=ON")
                insert(db, operations)
            print(f"Imported {len(operations)} local metadata records; no photos or claims.")
        else:
            print(f"Validated {len(operations)} records; DRY RUN ONLY.")
    except (OSError, ValueError, json.JSONDecodeError, sqlite3.Error) as error:
        parser.exit(1, f"Metadata intake failed: {error}\n")


if __name__ == "__main__":
    main()
