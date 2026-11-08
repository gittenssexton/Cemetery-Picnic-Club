-- Cemetery Picnic Club — D1/SQLite schema, pilot v0.1
-- Design: marker != person != burial. Assertions are separate cited claims.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cemeteries (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  alternate_name TEXT,
  address TEXT,
  town TEXT NOT NULL,
  state TEXT,
  country TEXT DEFAULT 'US',
  latitude REAL CHECK(latitude BETWEEN -90 AND 90),
  longitude REAL CHECK(longitude BETWEEN -180 AND 180),
  centroid_accuracy_m REAL,
  governance TEXT,
  contact_public TEXT,
  public_access_notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS persons (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  name_variants_json TEXT NOT NULL DEFAULT '[]',
  birth_date_text TEXT,
  death_date_text TEXT,
  privacy_status TEXT NOT NULL DEFAULT 'public' CHECK(privacy_status IN ('public','restricted','private')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS markers (
  id TEXT PRIMARY KEY,
  cemetery_id TEXT NOT NULL REFERENCES cemeteries(id),
  section_name TEXT,
  plot_reference TEXT,
  marker_type TEXT DEFAULT 'unknown',
  physical_description TEXT,
  stone_material_hypothesis TEXT,
  verification_status TEXT NOT NULL DEFAULT 'research_candidate'
    CHECK(verification_status IN ('research_candidate','field_located','reviewed')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS burials (
  id TEXT PRIMARY KEY,
  cemetery_id TEXT NOT NULL REFERENCES cemeteries(id),
  person_id TEXT REFERENCES persons(id),
  plot_reference TEXT,
  verification_status TEXT NOT NULL DEFAULT 'unverified',
  note TEXT
);

CREATE TABLE IF NOT EXISTS marker_person_links (
  marker_id TEXT NOT NULL REFERENCES markers(id),
  person_id TEXT NOT NULL REFERENCES persons(id),
  relationship_type TEXT NOT NULL DEFAULT 'commemorates'
    CHECK(relationship_type IN ('commemorates','burial_asserted','names','associated')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (marker_id, person_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS marker_positions (
  id TEXT PRIMARY KEY,
  marker_id TEXT NOT NULL REFERENCES markers(id),
  latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
  longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
  accuracy_m REAL CHECK(accuracy_m >= 0),
  method TEXT NOT NULL CHECK(method IN ('iphone_gps','manual_map','survey','archive')),
  observed_at TEXT,
  visibility TEXT NOT NULL DEFAULT 'public' CHECK(visibility IN ('public','approximate','restricted')),
  UNIQUE(marker_id, observed_at, method)
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  url TEXT,
  citation TEXT,
  access_scope TEXT NOT NULL DEFAULT 'public'
    CHECK(access_scope IN ('public','internal','permission_required')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS claims (
  id TEXT PRIMARY KEY,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  value_text TEXT,
  object_type TEXT,
  object_id TEXT,
  confidence TEXT NOT NULL DEFAULT 'tentative'
    CHECK(confidence IN ('documented','supported','tentative','unknown')),
  review_status TEXT NOT NULL DEFAULT 'unreviewed'
    CHECK(review_status IN ('unreviewed','in_review','reviewed','disputed','rejected')),
  method TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(value_text IS NOT NULL OR object_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS claim_evidence (
  claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id),
  page_or_locator TEXT,
  excerpt_or_note TEXT,
  PRIMARY KEY(claim_id, source_id, page_or_locator)
);

CREATE TABLE IF NOT EXISTS images (
  id TEXT PRIMARY KEY,
  marker_id TEXT REFERENCES markers(id),
  object_key TEXT,
  file_name TEXT,
  sha256 TEXT,
  photographer TEXT,
  rights_holder TEXT,
  rights_basis TEXT NOT NULL DEFAULT 'unknown'
    CHECK(rights_basis IN ('own_photo','explicit_permission','licensed','public_domain','unknown')),
  analysis_authorized INTEGER NOT NULL DEFAULT 0 CHECK(analysis_authorized IN (0,1)),
  publish_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publish_authorized IN (0,1)),
  capture_type TEXT NOT NULL DEFAULT 'front'
    CHECK(capture_type IN ('front','context','detail','angled','back','other')),
  captured_at TEXT,
  source_url TEXT,
  uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inscriptions (
  id TEXT PRIMARY KEY,
  marker_id TEXT NOT NULL REFERENCES markers(id),
  image_id TEXT REFERENCES images(id),
  kind TEXT NOT NULL DEFAULT 'face' CHECK(kind IN ('face','back','edge','signature_excerpt','other')),
  transcription TEXT NOT NULL,
  uncertain_spans_json TEXT NOT NULL DEFAULT '[]',
  review_status TEXT NOT NULL DEFAULT 'unreviewed',
  source_id TEXT REFERENCES sources(id),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS craftspeople (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  alternate_names_json TEXT NOT NULL DEFAULT '[]',
  biography_note TEXT,
  home_region TEXT,
  date_range_text TEXT
);

CREATE TABLE IF NOT EXISTS quarries (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT,
  geology TEXT,
  latitude REAL,
  longitude REAL,
  status TEXT DEFAULT 'unverified'
);

CREATE TABLE IF NOT EXISTS motifs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE IF NOT EXISTS marker_motifs (
  marker_id TEXT NOT NULL REFERENCES markers(id),
  motif_id TEXT NOT NULL REFERENCES motifs(id),
  confidence TEXT NOT NULL DEFAULT 'tentative',
  source_id TEXT REFERENCES sources(id),
  PRIMARY KEY(marker_id, motif_id)
);

CREATE TABLE IF NOT EXISTS external_references (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  external_url TEXT NOT NULL,
  external_id TEXT,
  note TEXT,
  UNIQUE(provider, external_url)
);

CREATE TABLE IF NOT EXISTS condition_observations (
  id TEXT PRIMARY KEY,
  marker_id TEXT NOT NULL REFERENCES markers(id),
  observed_at TEXT NOT NULL,
  observation TEXT NOT NULL,
  image_id TEXT REFERENCES images(id),
  is_diagnosis INTEGER NOT NULL DEFAULT 0 CHECK(is_diagnosis IN (0,1)),
  care_authorized INTEGER NOT NULL DEFAULT 0 CHECK(care_authorized IN (0,1))
);

CREATE TABLE IF NOT EXISTS field_drafts (
  id TEXT PRIMARY KEY,
  cemetery_id TEXT REFERENCES cemeteries(id),
  marker_id TEXT REFERENCES markers(id),
  data_json TEXT NOT NULL,
  sync_status TEXT NOT NULL DEFAULT 'local_only',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_markers_cemetery ON markers(cemetery_id);
CREATE INDEX IF NOT EXISTS idx_markers_status ON markers(verification_status);
CREATE INDEX IF NOT EXISTS idx_persons_display_name ON persons(display_name);
CREATE INDEX IF NOT EXISTS idx_marker_person_person ON marker_person_links(person_id);
CREATE INDEX IF NOT EXISTS idx_claims_subject ON claims(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_claim_evidence_source ON claim_evidence(source_id);
CREATE INDEX IF NOT EXISTS idx_inscriptions_marker ON inscriptions(marker_id);
CREATE INDEX IF NOT EXISTS idx_positions_marker ON marker_positions(marker_id);
CREATE INDEX IF NOT EXISTS idx_external_ref_entity ON external_references(entity_type,entity_id);
