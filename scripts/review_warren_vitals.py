"""Offline human-review attestation and controlled vital event acceptance.

No scan fetching, no OCR-based approvals, no D1 writes, and no person matching.
Call only with independently reviewed page evidence supplied by a real reviewer.
"""
import hashlib
import json
import re

COLLECTION = "ma-warren-1849-rice1910"
HEX64 = re.compile(r"^[a-f0-9]{64}$")
UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.][0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$")
SOURCE_CODE = "G.S.2."


def record_scan_review(db, *, candidate_id, reviewer_id, reviewed_at,
                       image_url, image_sequence, image_sha256,
                       verbatim_line, verified_name, verified_date=None,
                       verified_source_code=None, decision="needs_correction",
                       notes=""):
    """Append a human supplied attestation; does NOT itself approve an event."""
    if not all(isinstance(s,str) and s.strip() for s in
               (candidate_id,reviewer_id,reviewed_at,image_url,
                image_sha256,verbatim_line,verified_name)):
        raise ValueError("A reviewer, scan, checksum and exact line are mandatory")
    if len(reviewer_id.strip()) < 3 or not UTC.fullmatch(reviewed_at):
        raise ValueError("Reviewer's identity and ISO timestamp required")
    if not image_url.startswith("https://") or not HEX64.fullmatch(image_sha256):
        raise ValueError("Review requires a HTTPS scan URL and SHA-256")
    if type(image_sequence) is not int or image_sequence < 0:
        raise ValueError("Reviewed page image sequence must be an integer")
    if decision not in ("confirmed","needs_correction","rejected"):
        raise ValueError("Invalid review decision")
    row = db.execute("""SELECT printed_page,record_sha256,original_source_class,
                               printed_source_code
                        FROM vital_ocr_review_candidates WHERE id=?""",
                     (candidate_id,)).fetchone()
    if row is None:
        raise ValueError("No staged candidate")
    page,digest,source_class,code = row
    if source_class == "gravestone" and verified_source_code != SOURCE_CODE:
        raise ValueError("G.S.2 gravestone-derived provenance cannot be erased")
    if source_class != "gravestone" and verified_source_code == SOURCE_CODE:
        raise ValueError("Source code reclassification needs separate review workflow")
    # Use distinct review events; the candidate and its raw OCR are immutable.
    payload = [candidate_id,digest,reviewer_id,reviewed_at,image_url,image_sequence,
               image_sha256,page,verbatim_line,verified_name,verified_date,
               verified_source_code,decision,notes]
    review_id = "page-review-" + hashlib.sha256(
        json.dumps(payload,sort_keys=True,ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    db.execute("""INSERT INTO vital_ocr_page_reviews
        (id,candidate_id,candidate_record_sha256,reviewer_id,reviewed_at,
         image_url,image_sequence,image_sha256,printed_page,verbatim_line,
         verified_name,verified_date,verified_source_code,decision,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (review_id,*payload))
    return review_id


def accept_scan_reviewed_event(db, *, candidate_id, review_id, accepted_by):
    """Requires authorized collection and explicit scan-confirmed review.

    Creates one reviewed SOURCE ENTRY, never a CPC person, marker or burial.
    Leaves source record restricted pending separate publication authorization.
    """
    if not isinstance(accepted_by,str) or len(accepted_by.strip()) < 3:
        raise ValueError("Named accepting reviewer required")
    coll = db.execute("""SELECT ingestion_authorization,rights_status
                         FROM vital_record_collections WHERE id=?""",
                      (COLLECTION,)).fetchone()
    if coll != ("reviewed_source_entries","verified_public_domain"):
        raise ValueError("Collection still metadata-only or lacks reviewed rights")
    row = db.execute("""SELECT c.id,c.record_sha256,c.printed_page,
          c.original_source_class,r.candidate_record_sha256,r.printed_page,
          r.image_url,r.image_sequence,r.image_sha256,r.verbatim_line,r.verified_name,
          r.verified_date,r.verified_source_code,r.decision
          FROM vital_ocr_review_candidates c
          JOIN vital_ocr_page_reviews r ON c.id=r.candidate_id
          WHERE c.id=? AND r.id=?""",(candidate_id,review_id)).fetchone()
    if row is None:
        raise ValueError("Candidate and page-review evidence must be linked")
    (cid,original_hash,page,source_class,review_hash,review_page,image_url,
     seq,image_sha,verbatim,name,date,code,decision) = row
    if original_hash != review_hash or page != review_page or decision != "confirmed":
        raise ValueError("Source hash/page agreement and confirmed scan required")
    if source_class == "gravestone" and code != SOURCE_CODE:
        raise ValueError("Gravestone-derived lineage must be retained")
    if db.execute("SELECT 1 FROM vital_ocr_accepted_events WHERE candidate_id=?",
                  (candidate_id,)).fetchone():
        raise ValueError("Candidate already accepted; use a correction review")
    doc_id = "warren-rice1910-reviewed"
    page_id = f"{doc_id}-p{page:03d}-im{seq:04d}"
    entry_id = "vital-reviewed-" + cid
    # Transaction rollback is owned by caller via db context.
    existing_doc = db.execute("SELECT 1 FROM vital_source_documents WHERE id=?",
                              (doc_id,)).fetchone()
    if not existing_doc:
        db.execute("""INSERT INTO vital_source_documents
          (id,collection_id,volume_label,edition,source_url,original_format,
           transcription_source,transcription_rights,ocr_status,pagination_scheme)
          VALUES (?,?,?,?,?,?,?,?,?,?)""",
          (doc_id,COLLECTION,"1910 printed volume","Franklin P. Rice, 1910",
           "https://www.loc.gov/item/10008543/","printed_volume",
           "human_verified_page_scan","verified_public_domain",
           "selected_pages_reviewed","printed_page_and_image_sequence"))
    previous_page = db.execute("SELECT image_url,image_sequence FROM vital_source_page_refs WHERE id=?",
                               (page_id,)).fetchone()
    if previous_page and previous_page != (image_url,seq):
        raise ValueError("Conflicting image locator for existing page reference")
    if not previous_page:
        db.execute("""INSERT INTO vital_source_page_refs
          (id,document_id,printed_page,image_sequence,image_url,section_name,ocr_review_state)
          VALUES (?,?,?,?,?,'Births','reviewed')""",
          (page_id,doc_id,str(page),seq,image_url))
    db.execute("""INSERT INTO vital_record_entries
      (id,document_id,page_ref_id,local_entry_key,event_type,
       event_date_verbatim,primary_name_verbatim,entry_verbatim,
       printed_source_code,original_source_class,record_level,
       transcription_method,extraction_confidence,review_status,privacy_status)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (entry_id,doc_id,page_id,cid,"birth",date,name,verbatim,
       code,source_class,"compiled_transcription","human_page_scan_review",
       "verified_against_page","reviewed","restricted"))
    db.execute("""INSERT INTO vital_ocr_accepted_events
      (candidate_id,review_id,entry_id,accepted_by)
      VALUES (?,?,?,?)""",(candidate_id,review_id,entry_id,accepted_by))
    return entry_id
