-- Cemetery Picnic Club | 0006 New England historical vital-record core
-- Stage only. Requires earlier migrations. Designed for SQLite / Cloudflare D1.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS vital_jurisdictions (
 id TEXT PRIMARY KEY,
 jurisdiction_type TEXT NOT NULL CHECK (jurisdiction_type IN ('state','county','town','city','parish','other')),
 name TEXT NOT NULL,
 state_code TEXT NOT NULL CHECK (state_code IN ('MA','CT','RI','NH','VT','ME')),
 parent_id TEXT REFERENCES vital_jurisdictions(id),
 valid_from_year INTEGER,
 valid_to_year INTEGER,
 alternate_names_json TEXT NOT NULL DEFAULT '[]',
 note TEXT
);

CREATE TABLE IF NOT EXISTS vital_record_collections (
 id TEXT PRIMARY KEY,
 title TEXT NOT NULL,
 repository TEXT NOT NULL,
 record_start_year INTEGER,
 record_end_year INTEGER,
 state_code TEXT NOT NULL CHECK (state_code IN ('MA','CT','RI','NH','VT','ME')),
 jurisdiction_id TEXT REFERENCES vital_jurisdictions(id),
 canonical_url TEXT NOT NULL,
 catalog_identifier TEXT,
 publication_year INTEGER,
 original_record_type TEXT NOT NULL DEFAULT 'mixed',
 rights_status TEXT NOT NULL DEFAULT 'unverified',
 access_method TEXT NOT NULL DEFAULT 'manual_review',
 ingestion_authorization TEXT NOT NULL DEFAULT 'needs_review',
 citation_template TEXT,
 notes TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vital_source_documents (
 id TEXT PRIMARY KEY,
 collection_id TEXT NOT NULL REFERENCES vital_record_collections(id),
 source_work_id TEXT REFERENCES research_works(id),
 source_id TEXT REFERENCES sources(id),
 volume_label TEXT,
 edition TEXT,
 source_url TEXT NOT NULL,
 external_identifier TEXT,
 original_format TEXT,
 checksum_sha256 TEXT,
 transcription_source TEXT,
 transcription_rights TEXT NOT NULL DEFAULT 'unverified',
 ocr_status TEXT NOT NULL DEFAULT 'not_started',
 pagination_scheme TEXT,
 page_offset_note TEXT,
 acquired_at TEXT,
 UNIQUE(collection_id,source_url)
);

CREATE TABLE IF NOT EXISTS vital_source_page_refs (
 id TEXT PRIMARY KEY,
 document_id TEXT NOT NULL REFERENCES vital_source_documents(id),
 printed_page TEXT,
 image_sequence INTEGER,
 image_url TEXT,
 section_name TEXT,
 ocr_text_checksum TEXT,
 ocr_review_state TEXT NOT NULL DEFAULT 'unreviewed',
 UNIQUE(document_id,printed_page,image_sequence)
);

CREATE TABLE IF NOT EXISTS vital_record_entries (
 id TEXT PRIMARY KEY,
 document_id TEXT NOT NULL REFERENCES vital_source_documents(id),
 page_ref_id TEXT REFERENCES vital_source_page_refs(id),
 local_entry_key TEXT NOT NULL,
 event_type TEXT NOT NULL CHECK(event_type IN ('birth','baptism','marriage','marriage_intention','death','burial','other')),
 jurisdiction_id TEXT REFERENCES vital_jurisdictions(id),
 event_date_verbatim TEXT,
 event_date_iso TEXT,
 event_date_precision TEXT NOT NULL DEFAULT 'unknown'
   CHECK(event_date_precision IN ('day','month','year','range','circa','unknown')),
 event_place_verbatim TEXT,
 primary_name_verbatim TEXT NOT NULL,
 entry_verbatim TEXT NOT NULL,
 entry_normalized_summary TEXT,
 printed_source_code TEXT,
 original_source_class TEXT NOT NULL DEFAULT 'unknown'
   CHECK(original_source_class IN ('town_book','church_register','gravestone','family_record','compiled_secondary','other','unknown')),
 record_level TEXT NOT NULL DEFAULT 'compiled_transcription'
   CHECK(record_level IN ('original','compiled_transcription','index','ocr_candidate')),
 transcription_method TEXT NOT NULL DEFAULT 'manual',
 extraction_confidence TEXT NOT NULL DEFAULT 'unreviewed'
   CHECK(extraction_confidence IN ('unreviewed','uncertain','reviewed','verified_against_page')),
 review_status TEXT NOT NULL DEFAULT 'unreviewed',
 privacy_status TEXT NOT NULL DEFAULT 'public_historical'
   CHECK(privacy_status IN ('public_historical','restricted','private')),
 recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(document_id,local_entry_key)
);

CREATE TABLE IF NOT EXISTS vital_entry_participants (
 id TEXT PRIMARY KEY,
 entry_id TEXT NOT NULL REFERENCES vital_record_entries(id),
 role TEXT NOT NULL CHECK(role IN ('subject','spouse','parent','child','witness','informant','other')),
 name_verbatim TEXT NOT NULL,
 person_id TEXT REFERENCES persons(id),
 relationship_note TEXT,
 match_status TEXT NOT NULL DEFAULT 'not_linked'
   CHECK(match_status IN ('not_linked','candidate','reviewed_link','rejected')),
 evidence_notes TEXT
);

CREATE TABLE IF NOT EXISTS vital_entry_source_codes (
 document_id TEXT NOT NULL REFERENCES vital_source_documents(id),
 code TEXT NOT NULL,
 meaning TEXT NOT NULL,
 evidence_class TEXT NOT NULL DEFAULT 'unknown'
   CHECK(evidence_class IN ('gravestone','town_book','church_register','family_record','other','unknown')),
 citation_locator TEXT,
 reviewer TEXT,
 PRIMARY KEY(document_id,code)
);

CREATE TABLE IF NOT EXISTS vital_entity_match_candidates (
 id TEXT PRIMARY KEY,
 entry_id TEXT NOT NULL REFERENCES vital_record_entries(id),
 person_id TEXT REFERENCES persons(id),
 marker_id TEXT REFERENCES markers(id),
 match_kind TEXT NOT NULL CHECK(match_kind IN ('person','marker','burial','same_event')),
 candidate_score REAL,
 score_model TEXT,
 supporting_factors_json TEXT NOT NULL DEFAULT '[]',
 contradictory_factors_json TEXT NOT NULL DEFAULT '[]',
 independent_source_count INTEGER NOT NULL DEFAULT 0 CHECK(independent_source_count>=0),
 review_status TEXT NOT NULL DEFAULT 'candidate'
   CHECK(review_status IN ('candidate','accepted','rejected','needs_more_evidence')),
 reviewer TEXT,
 reviewed_at TEXT,
 notes TEXT,
 CHECK(person_id IS NOT NULL OR marker_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS vital_ingestion_runs (
 id TEXT PRIMARY KEY,
 document_id TEXT NOT NULL REFERENCES vital_source_documents(id),
 pipeline_version TEXT NOT NULL,
 started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 finished_at TEXT,
 page_first INTEGER,
 page_last INTEGER,
 entries_extracted INTEGER NOT NULL DEFAULT 0,
 entries_verified INTEGER NOT NULL DEFAULT 0,
 duplicate_count INTEGER NOT NULL DEFAULT 0,
 error_count INTEGER NOT NULL DEFAULT 0,
 log_summary TEXT,
 status TEXT NOT NULL DEFAULT 'in_progress'
);

CREATE INDEX IF NOT EXISTS idx_vital_collection_state ON vital_record_collections(state_code,record_start_year);
CREATE INDEX IF NOT EXISTS idx_vital_event_type_date ON vital_record_entries(event_type,event_date_iso);
CREATE INDEX IF NOT EXISTS idx_vital_name ON vital_record_entries(primary_name_verbatim);
CREATE INDEX IF NOT EXISTS idx_vital_entries_doc ON vital_record_entries(document_id);
CREATE INDEX IF NOT EXISTS idx_vital_participant_name ON vital_entry_participants(name_verbatim);
CREATE INDEX IF NOT EXISTS idx_vital_participant_person ON vital_entry_participants(person_id);
CREATE INDEX IF NOT EXISTS idx_vital_match_entry ON vital_entity_match_candidates(entry_id,review_status);
