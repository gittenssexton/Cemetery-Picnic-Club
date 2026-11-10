"""Stage the 26 image-assisted page omissions as UNVERIFIED source candidates.

No source claims are accepted. No person, burial or identity matching occurs.
Every source row is immutable under exact-replay hash checks.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from scripts.stage_warren_ocr_review import COLLECTION, ROOT, SOURCE_URL, encode

FILENAME = "warren-1910-page-omissions-2026-11-10.json"
PDF_SHA = "59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6"
PAGE_COUNTS = {9: 1, 10: 10, 11: 15}
PAGE_RENDER_SHA = {
    9:"86a4367f3425a5b24ab4f85ea120dda8fb825380477b774e6faffb94adf9f848",
    10:"8dda636648e75444ecd1fa63fbdc71c2ad2c0315dd10e78a71b40c84739ca18d",
    11:"775780404ee21ec22635ed5d64679b8db1a3e6012fc35567272fcd8a0e7cdbe2",
}


def prepare(path):
    path = Path(path)
    if path.name != FILENAME:
        raise ValueError("Only the recorded 2026 Warren omissions batch may be staged")
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema") != "cpc-warren-omitted-ocr-candidate-batch-v1"
        or data.get("collection") != COLLECTION
        or data.get("source_pdf_sha256") != PDF_SHA
        or data.get("review_status") != "assistant_page_scan_transcription_pending_human_review"):
        raise ValueError("Source PDF / provisional batch schema does not match")
    records = data.get("records")
    if not isinstance(records, list) or len(records) != 26:
        raise ValueError("Expected exactly 26 omitted provisional entries")
    digest = hashlib.sha256(encode(data)).hexdigest()
    counts = {page:0 for page in PAGE_COUNTS}
    seen=set()
    rows=[]
    for r in records:
        page = r.get("printed_page")
        if type(page) is not int or page not in PAGE_COUNTS:
            raise ValueError("Unapproved printed page")
        counts[page] += 1
        suffix = f"P{page:03d}-OM{counts[page]:03d}"
        ident = f"MA-WARREN-RICE1910-BIRTH-{suffix}"
        if r.get("id") != ident or ident in seen:
            raise ValueError("Omission identifier/order mismatch")
        seen.add(ident)
        code = r.get("printed_source_code")
        gravestone = code == "G.S.2."
        if (r.get("record_level") != "ocr_candidate"
            or r.get("review_status") != "requires_page_image_check"
            or r.get("source_image_verified") is not False
            or r.get("pdf_index") != page + 3
            or r.get("source_page_image_sha256") != PAGE_RENDER_SHA[page]
            or r.get("event_type") != "birth"
            or not isinstance(r.get("source_line_reading"),str)
            or not r["source_line_reading"].strip()
            or not isinstance(r.get("name_verbatim"),str)
            or not r["name_verbatim"].strip()):
            raise ValueError("Missing immutable source/scan provenance")
        if ((gravestone and (r.get("original_source_class") != "gravestone"
                             or r.get("independent_from_pine_grove_photo") is not False))
            or (not gravestone and (r.get("original_source_class") != "town_book"
                                    or r.get("independent_from_pine_grove_photo") is not None))):
            raise ValueError("Invalid G.S.2 source lineage")
        rows.append((
            ident, COLLECTION, FILENAME, digest, page, None, "birth",
            r["name_verbatim"], r.get("event_date_verbatim"), code,
            r["original_source_class"], 0 if gravestone else None, SOURCE_URL,
            encode(r).decode("utf-8"), hashlib.sha256(encode(r)).hexdigest(),
            "requires_page_image_check", 0
        ))
    if counts != PAGE_COUNTS:
        raise ValueError("Page counts do not match the audited omissions")
    return (FILENAME,digest,COLLECTION,len(rows)),rows


def stage(db,path=ROOT/"data/vital-records"/FILENAME):
    batch,rows=prepare(path)
    added=replayed=0
    with db:
        if not db.execute(
            "SELECT 1 FROM vital_record_collections WHERE id=?", (COLLECTION,)
        ).fetchone():
            raise ValueError("Warren catalog seed required before staging omissions")
        prior=db.execute(
            "SELECT batch_sha256,candidate_count FROM vital_ocr_review_batches "
            "WHERE batch_filename=?",(batch[0],)
        ).fetchone()
        if prior and prior!=(batch[1],batch[3]):
            raise ValueError("Omissions batch differs from recorded import")
        if not prior:
            db.execute(
                "INSERT INTO vital_ocr_review_batches "
                "(batch_filename,batch_sha256,collection_id,candidate_count) VALUES (?,?,?,?)",
                batch
            )
        for row in rows:
            prior=db.execute(
                "SELECT record_sha256,source_batch_sha256 FROM vital_ocr_review_candidates WHERE id=?",
                (row[0],)
            ).fetchone()
            if prior:
                if prior!=(row[14],row[3]):
                    raise ValueError("Conflicting candidate reimport")
                replayed+=1
            else:
                db.execute(
                    "INSERT INTO vital_ocr_review_candidates "
                    "(id,collection_id,source_batch,source_batch_sha256,printed_page,"
                    " digital_image_sequence,event_type,name_verbatim,date_verbatim,"
                    " printed_source_code,original_source_class,independently_corrob_gravestone,"
                    " source_url,raw_record_json,record_sha256,review_status,source_image_verified) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",row
                )
                added+=1
    return {"inserted":added,"duplicate":replayed,"candidate_count":len(rows)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--database",type=Path)
    args=parser.parse_args()
    batch,rows=prepare(ROOT/"data/vital-records"/FILENAME)
    if not args.apply:
        print(f"Validated {len(rows)} unverified source omissions; DRY RUN ONLY.")
        return
    if not args.database or not args.database.is_file():
        parser.error("--apply requires an existing, migrated local SQLite --database")
    with sqlite3.connect(str(args.database)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        result=stage(db)
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
