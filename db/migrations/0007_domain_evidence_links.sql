-- 0007: Explicit, reversible cross-domain references. No implicit entity merge.
-- Canonical refs wrap existing legacy IDs; source domain tables retain ownership.
-- Applied only to isolated integration staging until reviewed.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS domain_entity_refs (
  entity_ref TEXT PRIMARY KEY,
  domain TEXT NOT NULL CHECK(domain IN ('CEM','VIT','GEO','ICO','CAR','IMG','HIS','KIN','LOC','CON')),
  entity_type TEXT NOT NULL CHECK(length(entity_type)>0 AND entity_type NOT LIKE '%:%'),
  source_local_id TEXT NOT NULL CHECK(length(source_local_id)>0 AND source_local_id NOT LIKE '%:%'),
  source_table TEXT NOT NULL CHECK(length(source_table)>0),
  source_row_id TEXT NOT NULL CHECK(length(source_row_id)>0),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(entity_ref=domain || ':' || entity_type || ':' || source_local_id),
  UNIQUE(domain,entity_type,source_local_id),
  UNIQUE(domain,source_table,source_row_id,entity_type)
);

CREATE TABLE IF NOT EXISTS domain_evidence_links (
  id TEXT PRIMARY KEY,
  source_entity_ref TEXT NOT NULL REFERENCES domain_entity_refs(entity_ref) ON DELETE RESTRICT,
  target_entity_ref TEXT NOT NULL REFERENCES domain_entity_refs(entity_ref) ON DELETE RESTRICT,
  relation TEXT NOT NULL CHECK(length(trim(relation))>0),
  evidence_ref TEXT NOT NULL CHECK(length(trim(evidence_ref))>0),
  evidence_locator TEXT NOT NULL CHECK(length(trim(evidence_locator))>0),
  evidence_note TEXT,
  confidence TEXT NOT NULL DEFAULT 'tentative'
    CHECK(confidence IN ('unknown','tentative','supported','documented')),
  review_status TEXT NOT NULL DEFAULT 'candidate'
    CHECK(review_status IN ('candidate','in_review','reviewed','rejected','disputed')),
  independently_observed INTEGER NOT NULL DEFAULT 0 CHECK(independently_observed IN (0,1)),
  access_scope TEXT NOT NULL DEFAULT 'restricted'
    CHECK(access_scope IN ('public','restricted','permission_required','unknown')),
  analysis_permission TEXT NOT NULL DEFAULT 'unknown'
    CHECK(analysis_permission IN ('permitted','prohibited','unknown')),
  publication_permission TEXT NOT NULL DEFAULT 'unknown'
    CHECK(publication_permission IN ('permitted','prohibited','unknown')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TEXT,
  reviewer TEXT,
  CHECK(source_entity_ref<>target_entity_ref),
  CHECK(review_status<>'reviewed' OR (reviewer IS NOT NULL AND reviewed_at IS NOT NULL)),
  CHECK(publication_permission<>'permitted' OR access_scope='public')
);

CREATE INDEX IF NOT EXISTS idx_domain_links_source ON domain_evidence_links(source_entity_ref,review_status);
CREATE INDEX IF NOT EXISTS idx_domain_links_target ON domain_evidence_links(target_entity_ref,review_status);
CREATE INDEX IF NOT EXISTS idx_domain_links_evidence ON domain_evidence_links(evidence_ref);
