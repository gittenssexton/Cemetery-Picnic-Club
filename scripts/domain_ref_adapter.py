"""Canonical CPC reference adapter for already-existing source-owned SQL rows.

No network access, no automatic person matching, and no publishing rights granted.
The caller supplies an open SQLite connection with all migrations applied.
"""
import re

SOURCE_TABLES = {
    ("CEM", "marker"): "markers",
    ("CEM", "burial"): "burials",
    ("GEO", "geologic_map"): "geology_map_sources",
    ("GEO", "unit"): "geology_units",
    ("GEO", "material_candidate"): "stone_material_candidates",
    ("VIT", "event"): "vital_record_entries",
    ("VIT", "collection"): "vital_record_collections",
    ("IMG", "photo_original"): "images",
    ("IMG", "field_draft"): "field_drafts",
}
PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def register_existing(db, domain, entity_type, source_id):
    """Register an existing row only; never create a placeholder source record."""
    table = SOURCE_TABLES.get((domain, entity_type))
    if table is None:
        raise ValueError("Unregistered domain/entity mapping")
    if not isinstance(source_id, str) or not PART.fullmatch(source_id):
        raise ValueError("Invalid source-local ID")
    if db.execute(f"SELECT 1 FROM {table} WHERE id=?", (source_id,)).fetchone() is None:
        raise ValueError("Source row does not exist")
    entity_ref = f"{domain}:{entity_type}:{source_id}"
    db.execute(
        """INSERT OR IGNORE INTO domain_entity_refs
        (entity_ref,domain,entity_type,source_local_id,source_table,source_row_id)
        VALUES (?,?,?,?,?,?)""",
        (entity_ref, domain, entity_type, source_id, table, source_id)
    )
    return entity_ref


def link_candidate(db, link_id, source_ref, target_ref, relation,
                   evidence_ref, evidence_locator, evidence_note=None):
    """Create reviewable link; identity, attribution and publication never auto-approved."""
    for value in (link_id, source_ref, target_ref, relation, evidence_ref, evidence_locator):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Link requires nonempty ID, refs, relation and cited evidence")
    if not PART.fullmatch(link_id):
        raise ValueError("Invalid link ID")
    if source_ref == target_ref:
        raise ValueError("A candidate must link distinct entities")
    for ref in (source_ref, target_ref):
        if db.execute("SELECT 1 FROM domain_entity_refs WHERE entity_ref=?", (ref,)).fetchone() is None:
            raise ValueError("Unregistered canonical reference")
    db.execute(
        """INSERT INTO domain_evidence_links
        (id,source_entity_ref,target_entity_ref,relation,evidence_ref,
         evidence_locator,evidence_note,review_status,publication_permission)
        VALUES (?,?,?,?,?,?,?,'candidate','unknown')""",
        (link_id, source_ref, target_ref, relation, evidence_ref,
         evidence_locator, evidence_note)
    )
    return link_id
