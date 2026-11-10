"""Stage Warren printed page 12 in the provisional OCR review queue only.

Assistant-assisted image transcription is not named human source verification.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from scripts.stage_warren_ocr_review import COLLECTION, ROOT, SOURCE_URL, encode

NAME="warren-1910-births-p012-assistant-provisional.json"
PDF_SHA="59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6"


def prepare(path=ROOT/"data/vital-records"/NAME):
    path=Path(path)
    if path.name!=NAME:
        raise ValueError("Unrecognized page 12 intake file")
    data=json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema")!="cpc-warren-page12-assisted-transcription-v1"
        or data.get("collection_id")!=COLLECTION
        or data.get("source_pdf_sha256")!=PDF_SHA
        or data.get("printed_page")!=12 or data.get("pdf_index")!=15
        or data.get("review_state")!="assistant_visual_transcription_pending_named_review"):
        raise ValueError("Invalid collection, source or review state")
    raw=data.get("records")
    if not isinstance(raw,list) or len(raw)!=39:
        raise ValueError("Expected 39 printed source entries")
    digest=hashlib.sha256(encode(data)).hexdigest()
    rows=[]
    n_gs=0
    for i,r in enumerate(raw,1):
        ident=f"MA-WARREN-RICE1910-BIRTH-P012-{i:03d}"
        gs=r.get("printed_source_code")=="G.S.2."
        if gs:n_gs+=1
        if (r.get("id")!=ident
            or r.get("printed_page")!=12
            or r.get("review_status")!="requires_page_image_check"
            or r.get("record_level")!="ocr_candidate"
            or r.get("source_image_verified") is not False
            or r.get("event_type")!="birth"
            or r.get("proposed_person_id") is not None
            or r.get("proposed_burial_id") is not None
            or not isinstance(r.get("source_line_reading"),str)
            or not r["source_line_reading"].strip()
            or not isinstance(r.get("name_verbatim"),str)
            or not r["name_verbatim"].strip()
            or (gs and (r.get("original_source_class")!="gravestone"
                        or r.get("independent_from_pine_grove_photo") is not False))
            or (not gs and (r.get("printed_source_code") is not None
                            or r.get("original_source_class")!="town_book"))):
            raise ValueError("Provisional record invalid: "+ident)
        rows.append((
            ident,COLLECTION,NAME,digest,12,None,"birth",r["name_verbatim"],
            None,r["printed_source_code"],r["original_source_class"],0 if gs else None,
            SOURCE_URL,encode(r).decode("utf-8"),hashlib.sha256(encode(r)).hexdigest(),
            "requires_page_image_check",0
        ))
    if n_gs!=7 or data.get("counts")!={"candidate_entries":39,"gravestone_derived":7}:
        raise ValueError("Page 12 source lineage counts changed")
    return (NAME,digest,COLLECTION,39),rows


def stage(db,path=ROOT/"data/vital-records"/NAME):
    batch,rows=prepare(path)
    inserted=duplicates=0
    with db:
        if not db.execute("SELECT 1 FROM vital_record_collections WHERE id=?",(COLLECTION,)).fetchone():
            raise ValueError("Warren source catalog seed required")
        before=db.execute("SELECT batch_sha256,candidate_count FROM vital_ocr_review_batches WHERE batch_filename=?",(NAME,)).fetchone()
        if before and before!=(batch[1],39):
            raise ValueError("Page 12 batch source changed")
        if before is None:
            db.execute("INSERT INTO vital_ocr_review_batches(batch_filename,batch_sha256,collection_id,candidate_count) VALUES (?,?,?,?)",batch)
        for row in rows:
            prior=db.execute("SELECT record_sha256,source_batch_sha256 FROM vital_ocr_review_candidates WHERE id=?",(row[0],)).fetchone()
            if prior:
                if prior!=(row[14],row[3]):
                    raise ValueError("Page 12 candidate changed")
                duplicates+=1
                continue
            db.execute("""INSERT INTO vital_ocr_review_candidates
            (id,collection_id,source_batch,source_batch_sha256,printed_page,digital_image_sequence,
            event_type,name_verbatim,date_verbatim,printed_source_code,original_source_class,
            independently_corrob_gravestone,source_url,raw_record_json,record_sha256,
            review_status,source_image_verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",row)
            inserted+=1
    return {"inserted":inserted,"duplicate":duplicates,"total":len(rows)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database",type=Path)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    _batch,rows=prepare()
    if not a.apply:
        print(f"Validated {len(rows)} provisional page 12 candidates; DRY RUN.")
        return
    if not a.database or not a.database.is_file():
        p.error("--apply requires an existing migrated local SQLite --database")
    with sqlite3.connect(str(a.database)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        stats=stage(db)
    print(json.dumps(stats,sort_keys=True))

if __name__=="__main__":
    main()
