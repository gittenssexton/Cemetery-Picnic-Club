"""Validated staging of provisional Warren OCR birth readings, never canonical events.

The three research batches are selected samples, NOT complete scanned pages.
All entries remain unverified even if they contain structured dates.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "warren-1910-births-p009-batch01.json",
    "warren-1910-births-p010-batch02.json",
    "warren-1910-births-p011-batch03.json",
)
COLLECTION = "ma-warren-1849-rice1910"
SOURCE_URL = "https://www.loc.gov/item/10008543/"


def encode(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def prepare(path):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "cpc-warren-vital-extraction-batch-v1":
        raise ValueError("Wrong Warren source batch schema")
    if data.get("status") != "ocr_candidates_not_page_verified":
        raise ValueError("Batch must remain unverified")
    if path.name not in FILES:
        raise ValueError("Only approved Warren pilot batch names are allowed")
    page = int(data.get("page") or data.get("printed_page"))
    if page not in (9, 10, 11) or f"p{page:03d}" not in path.name:
        raise ValueError("Batch page and filename disagree")
    rows = data.get("records")
    if not isinstance(rows, list) or len(rows) != 25:
        raise ValueError("Expected exactly 25 selected candidate entries per batch")
    ids = set()
    result = []
    digest = hashlib.sha256(encode(data)).hexdigest()
    for record in rows:
        ident = record.get("id")
        source = record.get("source", {})
        code = record.get("printed_source_code")
        gs2 = isinstance(code, str) and code.replace(" ", "").upper().startswith("G.S.2")
        if (not isinstance(ident, str) or ident in ids or
            not ident.startswith(f"MA-WARREN-RICE1910-BIRTH-P{page:03d}-")):
            raise ValueError("Duplicate or unexpected provisional record identifier")
        ids.add(ident)
        if (record.get("record_level") != "ocr_candidate" or
            record.get("review_status") != "requires_page_image_check" or
            record.get("source_image_verified") is not False or
            source.get("digital_page_sequence") is not None):
            raise ValueError("Scan verification cannot be implied by OCR")
        if (source.get("collection") != COLLECTION or
            str(source.get("printed_page")) != str(page) or
            source.get("source_url") != SOURCE_URL or
            record.get("event_type") != "birth"):
            raise ValueError("Wrong source, page, or event type")
        if not isinstance(record.get("name_verbatim"), str) or not record["name_verbatim"].strip():
            raise ValueError("Source-preserved name is required")
        if gs2 and (record.get("original_source_class") != "gravestone" or
                    record.get("independent_from_pine_grove_photo") is not False or
                    record.get("evidence_lineage_status") != "gravestone_derived_not_independent"):
            raise ValueError("G.S.2 may not corroborate the underlying gravestone")
        if not gs2 and record.get("original_source_class") == "gravestone":
            raise ValueError("Gravestone record needs verified source-code lineage")
        independently = 0 if gs2 else None
        result.append((
            ident, COLLECTION, path.name, digest, page, None, "birth",
            record["name_verbatim"], record.get("event_date_verbatim"),
            code, record["original_source_class"], independently, SOURCE_URL,
            encode(record).decode("utf-8"), hashlib.sha256(encode(record)).hexdigest(),
            "requires_page_image_check", 0
        ))
    if sum(x[10] == "gravestone" for x in result) != data["counts"]["pine_grove_derived"]:
        raise ValueError("Reported G.S.2 count differs from actual batch")
    return (path.name, digest, COLLECTION, len(result)), result


def stage(db, paths):
    """Atomic import. Exact replays are harmless; a changed batch is rejected."""
    prepared = [prepare(p) for p in paths]
    flattened = [r for _, rows in prepared for r in rows]
    if len(set(r[0] for r in flattened)) != len(flattened):
        raise ValueError("Cross-batch candidate ID collision")
    inserted = 0
    duplicates = 0
    with db:
        if db.execute("SELECT 1 FROM vital_record_collections WHERE id=?", (COLLECTION,)).fetchone() is None:
            raise ValueError("Warren bibliographic collection must be present first")
        for batch, rows in prepared:
            old = db.execute("SELECT batch_sha256,candidate_count FROM vital_ocr_review_batches WHERE batch_filename=?",
                             (batch[0],)).fetchone()
            if old is not None and old != (batch[1],batch[3]):
                raise ValueError("Batch differs from previously staged source")
            if old is None:
                db.execute("""INSERT INTO vital_ocr_review_batches
                    (batch_filename,batch_sha256,collection_id,candidate_count)
                    VALUES (?,?,?,?)""",batch)
            for row in rows:
                old_row = db.execute(
                    "SELECT record_sha256,source_batch_sha256 FROM vital_ocr_review_candidates WHERE id=?",
                    (row[0],)).fetchone()
                if old_row is not None:
                    if old_row != (row[14], row[3]):
                        raise ValueError("Provisional record changed since initial staging")
                    duplicates += 1
                    continue
                db.execute("""INSERT INTO vital_ocr_review_candidates (
                    id,collection_id,source_batch,source_batch_sha256,printed_page,
                    digital_image_sequence,event_type,name_verbatim,date_verbatim,
                    printed_source_code,original_source_class,independently_corrob_gravestone,
                    source_url,raw_record_json,record_sha256,review_status,source_image_verified)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", row)
                inserted += 1
    return {"inserted":inserted,"duplicates":duplicates,"candidate_count":len(flattened)}


def main():
    import argparse
    import sqlite3
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    files=[ROOT/"data/vital-records"/n for n in FILES]
    batches=[prepare(f) for f in files]
    if not args.apply:
        print(f"Validated {sum(len(rows) for _,rows in batches)} provisional candidates; DRY RUN ONLY.")
        return
    if not args.database or not args.database.is_file():
        parser.error("--apply requires a pre-existing local SQLite --database")
    with sqlite3.connect(str(args.database)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        stats=stage(db,files)
    print(json.dumps(stats,sort_keys=True))


if __name__ == "__main__":
    main()
