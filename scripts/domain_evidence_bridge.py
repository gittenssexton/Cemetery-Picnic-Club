#!/usr/bin/env python3
"""Guarded, local-only canonical references and cited CPC evidence links.

The 0007 tables deliberately cannot carry polymorphic foreign keys to every
domain table. This module verifies the actual source row before registration
and the actual evidence source before linking. It never changes source rows,
creates identity matches, or escalates candidate review status.

CLI is deliberately absent. Call functions from reviewed integration code.
"""
import re
import sqlite3

REF = re.compile(r"^(CEM|VIT|GEO|ICO|CAR|IMG|HIS|KIN|LOC|CON):([a-z][a-z0-9_-]*):([A-Za-z0-9][A-Za-z0-9._-]*)$")
# Each explicit mapping is an already-existing source table with an 'id' PK.
# Keep this allowlist narrow until each domain's source-row semantics are reviewed.
OWNERS = {
    ("CEM", "marker"): "markers",
    ("CEM", "burial"): "burials",
    ("GEO", "geologic_map"): "geology_map_sources",
    ("GEO", "material_candidate"): "stone_material_candidates",
    ("VIT", "event"): "vital_record_entries",
    ("VIT", "collection"): "vital_record_collections",
    ("IMG", "photo_original"): "images",
    ("IMG", "field_draft"): "field_drafts",
    ("HIS", "work"): "research_works",
}
STATUS = {"candidate", "in_review", "rejected", "disputed"}
CONFIDENCE = {"unknown", "tentative", "supported", "documented"}


def parse_ref(entity_ref):
    match = REF.fullmatch(entity_ref) if isinstance(entity_ref, str) else None
    if not match:
        raise ValueError("Invalid canonical entity reference")
    domain, entity_type, source_id = match.groups()
    key = (domain, entity_type)
    if key not in OWNERS:
        raise ValueError("Unmapped domain entity; review adapter mapping before use")
    return domain, entity_type, source_id, OWNERS[key]


def register_reference(db, entity_ref, source_row_id):
    domain, typ, source_local_id, table = parse_ref(entity_ref)
    if not isinstance(source_row_id, str) or not source_row_id:
        raise ValueError("A real source row ID is required")
    if db.execute(f"SELECT 1 FROM {table} WHERE id=?", (source_row_id,)).fetchone() is None:
        raise ValueError("Underlying source row does not exist")
    existing = db.execute(
        "SELECT source_table,source_row_id FROM domain_entity_refs WHERE entity_ref=?",
        (entity_ref,)
    ).fetchone()
    if existing:
        if existing != (table, source_row_id):
            raise ValueError("Canonical reference already maps to a different source row")
        return entity_ref
    db.execute("""INSERT INTO domain_entity_refs
       (entity_ref,domain,entity_type,source_local_id,source_table,source_row_id)
       VALUES (?,?,?,?,?,?)""",
       (entity_ref,domain,typ,source_local_id,table,source_row_id))
    return entity_ref


def create_candidate_link(db, *, link_id, source_ref, target_ref, relation,
                          evidence_source_id, evidence_locator, evidence_note=None,
                          independently_observed=False, confidence="tentative"):
    if not all(isinstance(x, str) and x.strip()
               for x in (link_id, source_ref, target_ref, relation,
                         evidence_source_id, evidence_locator)):
        raise ValueError("Link ID, endpoints, relation and cited evidence are required")
    if source_ref == target_ref:
        raise ValueError("Self-links are invalid")
    if confidence not in CONFIDENCE:
        raise ValueError("Invalid confidence")
    if type(independently_observed) is not bool:
        raise ValueError("independently_observed must be boolean")
    # A source citation must exist in the core, not merely be a nonempty string.
    if db.execute("SELECT 1 FROM sources WHERE id=?", (evidence_source_id,)).fetchone() is None:
        raise ValueError("Evidence source is not registered")
    for ref in (source_ref, target_ref):
        domain, typ, _, table = parse_ref(ref)
        row = db.execute(
            "SELECT source_table,source_row_id FROM domain_entity_refs WHERE entity_ref=?",
            (ref,)
        ).fetchone()
        if row is None or row[0] != table:
            raise ValueError("Unregistered or mistyped canonical endpoint")
        if db.execute(f"SELECT 1 FROM {table} WHERE id=?", (row[1],)).fetchone() is None:
            raise ValueError("Endpoint source row was removed")
    # The bridge starts as restricted and reviewable, never pre-authorized for publication.
    db.execute("""INSERT INTO domain_evidence_links
       (id,source_entity_ref,target_entity_ref,relation,evidence_ref,
        evidence_locator,evidence_note,confidence,review_status,
        independently_observed,access_scope,publication_permission)
       VALUES (?,?,?,?,?,?,?,?,'candidate',?,'restricted','unknown')""",
       (link_id,source_ref,target_ref,relation,evidence_source_id,evidence_locator,
        evidence_note,confidence,int(independently_observed)))
    return link_id


def reject_candidate_link(db, link_id, reviewer, reviewed_at):
    if not all(isinstance(x, str) and x.strip() for x in (link_id, reviewer, reviewed_at)):
        raise ValueError("Explicit reviewer and date required")
    result = db.execute("""UPDATE domain_evidence_links
        SET review_status='rejected', reviewer=?, reviewed_at=?
        WHERE id=? AND review_status IN ('candidate','in_review','disputed')""",
        (reviewer, reviewed_at, link_id))
    if result.rowcount != 1:
        raise ValueError("Link missing or cannot be rejected in current state")
    # No source-row update/delete: rejected evidence stays visible for audit.


def list_links(db, entity_ref, *, public=False):
    """Read edges touching one canonical entity without exposing private evidence.

    Public results require source-level publication permission AND reviewed link.
    No raw evidence notes or citation locators are returned to the public view.
    Default is private/internal for approved application callers only.
    """
    parse_ref(entity_ref)
    base = """SELECT id,source_entity_ref,target_entity_ref,relation,evidence_ref,
                     evidence_locator,evidence_note,confidence,review_status,
                     access_scope,publication_permission
              FROM domain_evidence_links
              WHERE (source_entity_ref=? OR target_entity_ref=?)"""
    if public:
        base += """ AND review_status='reviewed'
                    AND access_scope='public'
                    AND publication_permission='permitted'"""
    rows = db.execute(base + " ORDER BY id", (entity_ref, entity_ref)).fetchall()
    keys = ("id","source_entity_ref","target_entity_ref","relation","evidence_ref",
            "evidence_locator","evidence_note","confidence","review_status",
            "access_scope","publication_permission")
    if public:
        # Even with a publishable link, source image/record and GPS rights must
        # be checked by the application before publishing an entity page.
        allowed = ("id","source_entity_ref","target_entity_ref","relation",
                   "confidence","review_status")
        return [{k:v for k,v in zip(keys,row) if k in allowed} for row in rows]
    return [dict(zip(keys,row)) for row in rows]
