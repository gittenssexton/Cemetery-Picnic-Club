#!/usr/bin/env python3
"""Validate Warren OCR candidates and write an isolated, disposable SQLite staging DB.

No inserts into CPC's deployed database; no promotion to reviewed vital records.
Usage: python scripts/stage_warren_vitals.py --output /tmp/cpc_warren_staging.sqlite
"""
import argparse
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/vital-records").glob("warren-1910-births-p0*-batch*.json"))

def validate():
    entries = []
    errors = []
    for path in FILES:
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload["records"]
        count = payload.get("counts", {})
        if count.get("entries") != len(items):
            errors.append(f"{path.name}: declared count differs from records length")
        if sum(x["original_source_class"] == "gravestone" for x in items) != count.get("pine_grove_derived"):
            errors.append(f"{path.name}: declared G.S.2 count differs")
        for item in items:
            item["_batch_file"] = path.name
            entries.append(item)
    seen = set()
    for item in entries:
        identifier = item["id"]
        if identifier in seen:
            errors.append(f"{identifier}: duplicate ID")
        seen.add(identifier)
        if item["review_status"] != "requires_page_image_check" or item.get("source_image_verified") is not False:
            errors.append(f"{identifier}: must remain unverified until scan review")
        if item.get("record_level") != "ocr_candidate":
            errors.append(f"{identifier}: unexpected record level")
        if not item.get("source", {}).get("printed_page"):
            errors.append(f"{identifier}: missing printed page")
        if not item.get("name_verbatim"):
            errors.append(f"{identifier}: missing name")
        if item.get("event_date_iso") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["event_date_iso"]):
            errors.append(f"{identifier}: malformed ISO date")
        if item.get("original_source_class") == "gravestone":
            if (item.get("printed_source_code") or "").upper() != "G.S.2." or item.get("independent_from_pine_grove_photo") is not False:
                errors.append(f"{identifier}: incorrect Pine Grove evidence lineage")
        elif item.get("independent_from_pine_grove_photo") is not None:
            errors.append(f"{identifier}: falsely asserted independence for other records")
    return entries, errors

def stage(entries, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {output}")
    with sqlite3.connect(output) as conn:
        conn.executescript("""
          PRAGMA foreign_keys=ON;
          CREATE TABLE ocr_vital_candidates (
            id TEXT PRIMARY KEY,
            batch_filename TEXT NOT NULL,
            printed_page TEXT NOT NULL,
            event_type TEXT NOT NULL,
            name_candidate TEXT NOT NULL,
            date_candidate TEXT,
            date_iso_candidate TEXT,
            printed_source_code TEXT,
            source_class TEXT NOT NULL,
            evidence_lineage TEXT NOT NULL,
            scan_verified INTEGER NOT NULL DEFAULT 0 CHECK(scan_verified=0),
            review_status TEXT NOT NULL CHECK(review_status='requires_page_image_check'),
            source_url TEXT NOT NULL,
            raw_candidate_json TEXT NOT NULL
          );
          CREATE INDEX idx_candidates_name ON ocr_vital_candidates(name_candidate);
          CREATE INDEX idx_candidates_source ON ocr_vital_candidates(printed_page,source_class);
        """)
        conn.executemany(
          """INSERT INTO ocr_vital_candidates
             (id,batch_filename,printed_page,event_type,name_candidate,date_candidate,
              date_iso_candidate,printed_source_code,source_class,evidence_lineage,
              scan_verified,review_status,source_url,raw_candidate_json)
             VALUES(?,?,?,?,?,?,?,?,?,?,0,?,?,?)""",
          [(r["id"],r["_batch_file"],r["source"]["printed_page"],r["event_type"],
            r["name_verbatim"],r.get("event_date_verbatim"),r.get("event_date_iso"),
            r.get("printed_source_code"),r["original_source_class"],
            r["evidence_lineage_status"],r["review_status"],
            r["source"]["source_url"],json.dumps(r,ensure_ascii=False)) for r in entries]
        )
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        count = conn.execute("SELECT COUNT(*) FROM ocr_vital_candidates").fetchone()[0]
        gs2 = conn.execute("SELECT COUNT(*) FROM ocr_vital_candidates WHERE source_class='gravestone'").fetchone()[0]
        print(json.dumps({"database":str(output),"staging_candidates":count,"pine_grove_derived":gs2,"scan_verified":0},indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("/tmp/cpc_warren_staging.sqlite"))
    args=parser.parse_args()
    records,issues=validate()
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"Validation passed: {len(records)} OCR candidates across {len(FILES)} batches.")
    stage(records,args.output)
