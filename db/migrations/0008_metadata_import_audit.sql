-- 0008: source-aware metadata import audit (append-only provenance)
-- No source data or publication status is altered by this migration.
PRAGMA foreign_keys=ON;

CREATE TABLE metadata_import_batches (
  batch_id TEXT PRIMARY KEY,
  batch_sha256 TEXT NOT NULL CHECK(length(batch_sha256)=64),
  record_count INTEGER NOT NULL CHECK(record_count>=0),
  inserted_count INTEGER NOT NULL CHECK(inserted_count>=0),
  duplicate_count INTEGER NOT NULL CHECK(duplicate_count>=0),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(inserted_count+duplicate_count=record_count)
);

CREATE TABLE metadata_import_records (
  entity_ref TEXT PRIMARY KEY,
  domain TEXT NOT NULL CHECK(domain IN ('GEO','VIT','IMG')),
  record_type TEXT NOT NULL,
  source_local_id TEXT NOT NULL,
  source_ref TEXT NOT NULL CHECK(length(trim(source_ref))>0),
  evidence_locator TEXT NOT NULL CHECK(length(trim(evidence_locator))>0),
  record_sha256 TEXT NOT NULL CHECK(length(record_sha256)=64),
  rights_json TEXT NOT NULL CHECK(json_valid(rights_json)),
  review_status TEXT NOT NULL DEFAULT 'candidate'
    CHECK(review_status IN ('candidate','unreviewed','in_review','reviewed','rejected','disputed')),
  batch_id TEXT NOT NULL REFERENCES metadata_import_batches(batch_id),
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(entity_ref=domain || ':' || record_type || ':' || source_local_id)
);

CREATE INDEX idx_metadata_import_source ON metadata_import_records(source_ref);
CREATE INDEX idx_metadata_import_batch ON metadata_import_records(batch_id);
