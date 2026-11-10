-- CPC 0010: manual page-image reviews and guarded source-event acceptance.
-- Existing 75 provisional OCR rows are not promoted by this migration.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS vital_ocr_page_reviews (
  id TEXT PRIMARY KEY,
  candidate_id TEXT NOT NULL REFERENCES vital_ocr_review_candidates(id) ON DELETE RESTRICT,
  candidate_record_sha256 TEXT NOT NULL CHECK(length(candidate_record_sha256)=64),
  reviewer_id TEXT NOT NULL CHECK(length(trim(reviewer_id))>=3),
  reviewed_at TEXT NOT NULL CHECK(length(trim(reviewed_at))>=20),
  image_url TEXT NOT NULL CHECK(length(trim(image_url))>12),
  image_sequence INTEGER NOT NULL CHECK(image_sequence>=0),
  image_sha256 TEXT NOT NULL CHECK(length(image_sha256)=64),
  printed_page INTEGER NOT NULL CHECK(printed_page>0),
  verbatim_line TEXT NOT NULL CHECK(length(trim(verbatim_line))>0),
  verified_name TEXT NOT NULL CHECK(length(trim(verified_name))>0),
  verified_date TEXT,
  verified_source_code TEXT,
  decision TEXT NOT NULL CHECK(decision IN ('confirmed','needs_correction','rejected')),
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(candidate_id,reviewer_id,image_sha256,decision)
);
CREATE INDEX IF NOT EXISTS idx_vital_page_reviews_candidate
  ON vital_ocr_page_reviews(candidate_id,reviewed_at);
CREATE TABLE IF NOT EXISTS vital_ocr_accepted_events (
  candidate_id TEXT PRIMARY KEY REFERENCES vital_ocr_review_candidates(id) ON DELETE RESTRICT,
  review_id TEXT NOT NULL UNIQUE REFERENCES vital_ocr_page_reviews(id) ON DELETE RESTRICT,
  entry_id TEXT NOT NULL UNIQUE REFERENCES vital_record_entries(id) ON DELETE RESTRICT,
  accepted_by TEXT NOT NULL CHECK(length(trim(accepted_by))>=3),
  accepted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Preserve the review evidence and accepted-event lineage even if callers
-- accidentally execute UPDATE or DELETE. Corrections are new review events.
CREATE TRIGGER IF NOT EXISTS vital_page_review_no_update
  BEFORE UPDATE ON vital_ocr_page_reviews BEGIN SELECT RAISE(ABORT, 'review evidence is append only'); END;
CREATE TRIGGER IF NOT EXISTS vital_page_review_no_delete
  BEFORE DELETE ON vital_ocr_page_reviews BEGIN SELECT RAISE(ABORT, 'review evidence is append only'); END;
CREATE TRIGGER IF NOT EXISTS vital_event_acceptance_no_update
  BEFORE UPDATE ON vital_ocr_accepted_events BEGIN SELECT RAISE(ABORT, 'acceptance lineage is append only'); END;
CREATE TRIGGER IF NOT EXISTS vital_event_acceptance_no_delete
  BEFORE DELETE ON vital_ocr_accepted_events BEGIN SELECT RAISE(ABORT, 'acceptance lineage is append only'); END;
