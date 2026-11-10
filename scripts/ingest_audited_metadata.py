"""Audited, idempotent LOCAL metadata import for CPC staging preparation.

No remote D1 connection or background import. Call only after validated migrations.
Existing legacy rows are never adopted or overwritten silently.
"""
import hashlib
import json
import sqlite3

from scripts.ingest_domain_metadata import plan


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def apply_audited(db, records):
    """All-or-nothing validated ingest with source/rights audit and duplicate detection."""
    operations = plan(records)
    batch_sha = hashlib.sha256(canonical_bytes(records)).hexdigest()
    batch_id = "metadata-" + batch_sha
    # Plan checked the fixed set of target tables and column names.
    # Ensure the audit tables are present BEFORE writing source rows.
    db.execute("SELECT 1 FROM metadata_import_batches LIMIT 1")
    db.execute("SELECT 1 FROM metadata_import_records LIMIT 1")
    inserted = duplicate = 0
    with db:
        for record, (table, columns, values) in zip(records, operations):
            ref = record["entity_ref"]
            digest = hashlib.sha256(canonical_bytes(record)).hexdigest()
            current = db.execute(
                "SELECT record_sha256 FROM metadata_import_records WHERE entity_ref=?",
                (ref,)
            ).fetchone()
            source = db.execute(
                "SELECT " + ",".join(columns) + " FROM " + table + " WHERE id=?",
                (record["source_local_id"],)
            ).fetchone()
            if current:
                if current[0] != digest or source != values:
                    raise ValueError("Conflicting reimport or modified source row: " + ref)
                duplicate += 1
                continue
            if source is not None:
                raise ValueError("Existing source row has no matching audit record: " + ref)
            # Source rows first; rollback includes all rows and ledger if later work fails.
            placeholders = ",".join("?" for _ in values)
            db.execute(
                "INSERT INTO " + table + " (" + ",".join(columns) + ") VALUES (" +
                placeholders + ")", values)
            inserted += 1
        # The batch ledger is written before its dependent audit records.
        prior = db.execute(
            "SELECT batch_sha256,record_count FROM metadata_import_batches WHERE batch_id=?",
            (batch_id,)
        ).fetchone()
        if prior is None:
            db.execute(
                """INSERT INTO metadata_import_batches
                (batch_id,batch_sha256,record_count,inserted_count,duplicate_count)
                VALUES (?,?,?,?,?)""",
                (batch_id,batch_sha,len(records),inserted,duplicate)
            )
        elif prior != (batch_sha, len(records)):
            raise ValueError("Batch digest mismatch")
        for record in records:
            ref = record["entity_ref"]
            if db.execute("SELECT 1 FROM metadata_import_records WHERE entity_ref=?", (ref,)).fetchone():
                continue
            db.execute(
                """INSERT INTO metadata_import_records
                (entity_ref,domain,record_type,source_local_id,source_ref,
                 evidence_locator,record_sha256,rights_json,review_status,batch_id)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (ref, record["domain"], record["record_type"], record["source_local_id"],
                 record["source_ref"], record["evidence_locator"],
                 hashlib.sha256(canonical_bytes(record)).hexdigest(),
                 canonical_bytes(record["rights"]).decode("utf-8"),
                 record["review_status"], batch_id)
            )
    return {"batch_id": batch_id, "inserted": inserted, "duplicates": duplicate}


def main():
    """Offline CLI: dry-run by default, explicit local database required to write."""
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--apply", action="store_true",
                        help="Write validated metadata into an existing local SQLite file")
    parser.add_argument("--database", type=Path)
    args = parser.parse_args()
    if args.apply and (not args.database or not args.database.is_file()):
        parser.error("--apply requires an existing local SQLite --database")
    try:
        records = json.loads(args.json_file.read_text(encoding="utf-8"))
        validated = plan(records)
        if not args.apply:
            print(f"Validated {len(validated)} records; DRY RUN ONLY.")
            return
        with sqlite3.connect(str(args.database)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            result = apply_audited(db, records)
        print("Audited metadata import complete: " + json.dumps(result, sort_keys=True))
    except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        parser.exit(1, f"Audited import failed: {exc}\\n")


if __name__ == "__main__":
    main()
