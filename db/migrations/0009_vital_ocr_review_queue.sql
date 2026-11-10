-- Provisional Warren OCR queue. NOT a verified vital record, person, or burial table.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS vital_ocr_review_candidates (
  id TEXT PRIMARY KEY,
  collection_id TEXT NOT NULL REFERENCES vital_record_collections(id),
  source_batch TEXT NOT NULL,
  source_batch_sha256 TEXT NOT NULL CHECK(length(source_batch_sha256)=64),
  printed_page INTEGER NOT NULL CHECK(printed_page>0),
  digital_image_sequence INTEGER,
  event_type TEXT NOT NULL CHECK(event_type IN ('birth','death','marriage','intention','baptism','burial','other')),
  name_verbatim TEXT NOT NULL CHECK(length(trim(name_verbatim))>0),
  date_verbatim TEXT,
  printed_source_code TEXT,
  original_source_class TEXT NOT NULL CHECK(original_source_class IN ('town_book','gravestone','church','other','unknown')),
  independently_corrob_gravestone INTEGER CHECK(independently_corrob_gravestone IN (0,1)),
  source_url TEXT NOT NULL CHECK(length(trim(source_url))>0),
  raw_record_json TEXT NOT NULL CHECK(json_valid(raw_record_json)),
  record_sha256 TEXT NOT NULL CHECK(length(record_sha256)=64),
  review_status TEXT NOT NULL DEFAULT 'requires_page_image_check'
     CHECK(review_status IN ('requires_page_image_check','in_review','rejected','scan_checked')),
  source_image_verified INTEGER NOT NULL DEFAULT 0 CHECK(source_image_verified IN (0,1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(review_status <> 'scan_checked' OR source_image_verified=1),
  CHECK(original_source_class <> 'gravestone' OR independently_corrob_gravestone=0),
  CHECK(source_image_verified=0 OR digital_image_sequence IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS idx_vital_ocr_page_review
  ON vital_ocr_review_candidates(collection_id,printed_page,review_status);
CREATE INDEX IF NOT EXISTS idx_vital_ocr_lineage
  ON vital_ocr_review_candidates(original_source_class,printed_source_code);
CREATE TABLE IF NOT EXISTS vital_ocr_review_batches (
  batch_filename TEXT PRIMARY KEY,
  batch_sha256 TEXT NOT NULL CHECK(length(batch_sha256)=64),
  collection_id TEXT NOT NULL REFERENCES vital_record_collections(id),
  candidate_count INTEGER NOT NULL CHECK(candidate_count>=0),
  source_image_checked INTEGER NOT NULL DEFAULT 0 CHECK(source_image_checked IN (0,1)),
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
