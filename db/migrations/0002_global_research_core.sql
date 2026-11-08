-- 0002: globally scoped linked research core; SQLite / Cloudflare D1
-- A global source, maker, motif or material does not need a cemetery.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS research_works(
 id TEXT PRIMARY KEY,
 title TEXT NOT NULL,
 authors TEXT,
 published_year INTEGER,
 work_type TEXT NOT NULL CHECK(work_type IN ('book','article','archive','government','dataset','web','report','other')),
 publisher TEXT,
 journal TEXT,
 volume TEXT,
 issue TEXT,
 pages TEXT,
 doi TEXT,
 isbn TEXT,
 url TEXT,
 full_text_status TEXT NOT NULL DEFAULT 'not_acquired' CHECK(full_text_status IN ('not_acquired','abstract_only','available_external','licensed_copy','public_domain_copy','reviewed')),
 rights_status TEXT NOT NULL DEFAULT 'unverified',
 review_status TEXT NOT NULL DEFAULT 'bibliography_only' CHECK(review_status IN ('bibliography_only','metadata_verified','partly_reviewed','fully_reviewed')),
 added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_collections(
 id TEXT PRIMARY KEY,
 institution TEXT NOT NULL,
 name TEXT NOT NULL,
 catalog_url TEXT,
 scope_note TEXT,
 metadata_license TEXT,
 image_license TEXT,
 access_status TEXT NOT NULL DEFAULT 'unknown',
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_collection_items(
 id TEXT PRIMARY KEY,
 collection_id TEXT NOT NULL REFERENCES research_collections(id),
 original_identifier TEXT,
 catalog_url TEXT,
 marker_id TEXT REFERENCES markers(id),
 work_id TEXT REFERENCES research_works(id),
 rights_status TEXT NOT NULL DEFAULT 'unknown',
 UNIQUE(collection_id,original_identifier)
);

CREATE TABLE IF NOT EXISTS cultural_traditions(
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 description TEXT,
 heritage_sensitivity TEXT NOT NULL DEFAULT 'standard'
);

CREATE TABLE IF NOT EXISTS geographic_scopes(
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 scope_type TEXT NOT NULL CHECK(scope_type IN ('global','continent','country','region','locality','historical','unknown')),
 modern_country_code TEXT,
 latitude REAL,
 longitude REAL,
 accuracy_m REAL,
 description TEXT,
 CHECK(latitude IS NULL OR latitude BETWEEN -90 AND 90),
 CHECK(longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

CREATE TABLE IF NOT EXISTS terminology(
 id TEXT PRIMARY KEY,
 entity_type TEXT NOT NULL,
 entity_id TEXT NOT NULL,
 term TEXT NOT NULL,
 language_tag TEXT,
 script_tag TEXT,
 is_primary INTEGER NOT NULL DEFAULT 0 CHECK(is_primary IN (0,1)),
 note TEXT
);

CREATE TABLE IF NOT EXISTS motif_interpretations(
 id TEXT PRIMARY KEY,
 motif_id TEXT NOT NULL REFERENCES motifs(id),
 interpretation_text TEXT NOT NULL,
 interpretation_type TEXT NOT NULL DEFAULT 'scholarly_hypothesis' CHECK(interpretation_type IN ('attested','scholarly_hypothesis','community_tradition','unknown')),
 tradition_id TEXT REFERENCES cultural_traditions(id),
 scope_id TEXT REFERENCES geographic_scopes(id),
 period_start_year INTEGER,
 period_end_year INTEGER,
 review_status TEXT NOT NULL DEFAULT 'unreviewed',
 CHECK(period_start_year IS NULL OR period_end_year IS NULL OR period_end_year >= period_start_year)
);

CREATE TABLE IF NOT EXISTS research_citations(
 id TEXT PRIMARY KEY,
 work_id TEXT NOT NULL REFERENCES research_works(id),
 locator TEXT,
 page_text TEXT,
 access_date TEXT,
 note TEXT,
 UNIQUE(work_id,locator)
);

CREATE TABLE IF NOT EXISTS interpretation_citations(
 interpretation_id TEXT NOT NULL REFERENCES motif_interpretations(id),
 citation_id TEXT NOT NULL REFERENCES research_citations(id),
 evidence_role TEXT NOT NULL DEFAULT 'supports' CHECK(evidence_role IN ('supports','questions','contradicts','background')),
 PRIMARY KEY(interpretation_id,citation_id,evidence_role)
);

CREATE TABLE IF NOT EXISTS comparative_features(
 id TEXT PRIMARY KEY,
 motif_id TEXT REFERENCES motifs(id),
 feature_kind TEXT NOT NULL CHECK(feature_kind IN ('face','wing','border','lettering','shape','signature','toolmark','material','other')),
 feature_description TEXT NOT NULL,
 source_work_id TEXT REFERENCES research_works(id)
);

CREATE TABLE IF NOT EXISTS maker_research_links(
 id TEXT PRIMARY KEY,
 craftsperson_id TEXT NOT NULL REFERENCES craftspeople(id),
 related_entity_type TEXT NOT NULL,
 related_entity_id TEXT NOT NULL,
 relation_type TEXT NOT NULL,
 work_id TEXT REFERENCES research_works(id),
 citation_locator TEXT,
 confidence TEXT NOT NULL DEFAULT 'tentative' CHECK(confidence IN ('documented','supported','tentative','unknown')),
 review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE IF NOT EXISTS research_work_geography(
 work_id TEXT NOT NULL REFERENCES research_works(id),
 scope_id TEXT NOT NULL REFERENCES geographic_scopes(id),
 coverage_note TEXT,
 PRIMARY KEY(work_id,scope_id)
);

CREATE TABLE IF NOT EXISTS review_tasks(
 id TEXT PRIMARY KEY,
 entity_type TEXT NOT NULL,
 entity_id TEXT NOT NULL,
 task_type TEXT NOT NULL,
 description TEXT,
 priority INTEGER NOT NULL DEFAULT 3 CHECK(priority BETWEEN 1 AND 5),
 state TEXT NOT NULL DEFAULT 'open' CHECK(state IN ('open','blocked','in_progress','done')),
 depends_on TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_works_title ON research_works(title);
CREATE INDEX IF NOT EXISTS idx_works_doi ON research_works(doi);
CREATE INDEX IF NOT EXISTS idx_interpretations_motif ON motif_interpretations(motif_id);
CREATE INDEX IF NOT EXISTS idx_citations_work ON research_citations(work_id);
CREATE INDEX IF NOT EXISTS idx_maker_research ON maker_research_links(craftsperson_id);
CREATE INDEX IF NOT EXISTS idx_tasks_state ON review_tasks(state,priority);
