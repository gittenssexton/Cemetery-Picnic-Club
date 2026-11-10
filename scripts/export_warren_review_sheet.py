"""Generate the 140-row reviewer worksheet from provisional Warren source batches.

Read-only; never converts provisional records into verified records.
Use this CSV beside legitimate original page images during manual QA.
"""
import argparse
import csv
from pathlib import Path

from scripts.stage_warren_ocr_review import FILES, ROOT, prepare
from scripts.stage_warren_page_omissions import FILENAME as OMISSIONS, prepare as prepare_omissions
from scripts.stage_warren_page12 import prepare as prepare_page12

HEADERS = (
    "candidate_id", "printed_page", "source_collection", "name_ocr",
    "date_ocr", "source_code_ocr", "source_class_ocr", "gs2_dependent",
    "ocr_notes", "candidate_sha256",
    "verified_image_url", "verified_image_sequence", "verified_image_sha256",
    "reviewer_id", "reviewed_at", "exact_printed_line",
    "name_confirmed", "date_confirmed", "source_code_confirmed",
    "review_decision", "reviewer_notes"
)


def build_rows(paths):
    result=[]
    seen=set()
    for path in paths:
        batch, records = prepare(path)
        for row in records:
            (ident, collection, _name, _batch_sha, page, _seq, _event,
             name, date, code, source_class, independent, _url,
             raw, record_sha, _status, _verified) = row
            if ident in seen:
                raise ValueError("Duplicate candidate identifier")
            seen.add(ident)
            import json
            record = json.loads(raw)
            result.append({
                "candidate_id":ident,
                "printed_page":page,
                "source_collection":collection,
                "name_ocr":name,
                "date_ocr":date or "",
                "source_code_ocr":code or "",
                "source_class_ocr":source_class,
                "gs2_dependent":"YES" if source_class=="gravestone" else "NOT ESTABLISHED",
                "ocr_notes":record.get("notes") or "",
                "candidate_sha256":record_sha,
                # Human verification cells deliberately blank.
                **{field:"" for field in HEADERS[10:]}
            })
    # Reconcile the 26 omitted page entries without rewriting the first 75.
    _batch, omitted = prepare_omissions(ROOT/"data/vital-records"/OMISSIONS)
    for row in omitted:
        (ident, collection, _name, _batch_sha, page, _seq, _event,
         name, date, code, source_class, _independent, _url,
         raw, record_sha, _status, _verified) = row
        if ident in seen:
            raise ValueError("Duplicate candidate identifier")
        seen.add(ident)
        import json
        record=json.loads(raw)
        result.append({
            "candidate_id":ident,
            "printed_page":page,
            "source_collection":collection,
            "name_ocr":name,
            "date_ocr":date or "",
            "source_code_ocr":code or "",
            "source_class_ocr":source_class,
            "gs2_dependent":"YES" if source_class=="gravestone" else "NOT ESTABLISHED",
            "ocr_notes":record.get("notes") or "",
            "candidate_sha256":record_sha,
            **{field:"" for field in HEADERS[10:]}
        })
    _batch, page12_rows=prepare_page12()
    for row in page12_rows:
        (ident, collection, _batch_name, _batch_sha, page, _seq, _event,
         name, date, code, source_class, _independent, _url,
         raw, record_sha, _status, _verified)=row
        if ident in seen:
            raise ValueError("Duplicate candidate identifier")
        seen.add(ident)
        import json
        record=json.loads(raw)
        result.append({
            "candidate_id":ident,"printed_page":page,"source_collection":collection,
            "name_ocr":name,"date_ocr":date or "", "source_code_ocr":code or "",
            "source_class_ocr":source_class,
            "gs2_dependent":"YES" if source_class=="gravestone" else "NOT ESTABLISHED",
            "ocr_notes":record.get("source_line_reading") or "",
            "candidate_sha256":record_sha,
            **{field:"" for field in HEADERS[10:]}
        })
    return sorted(result,key=lambda x:(x["printed_page"],x["candidate_id"]))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    paths=[ROOT/"data/vital-records"/name for name in FILES]
    rows=build_rows(paths)
    if args.output.exists():
        parser.error("Refusing to overwrite an existing review worksheet")
    with args.output.open("w",newline="",encoding="utf-8-sig") as handle:
        writer=csv.DictWriter(handle,fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} UNVERIFIED review rows; no approvals recorded.")


if __name__=="__main__":
    main()
