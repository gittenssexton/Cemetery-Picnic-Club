-- 0003 Stone / marker material identification, global controlled vocabulary.
-- Material identification is a hypothesis derived from evidence, never a photo-only fact.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS material_types (
 id TEXT PRIMARY KEY,
 display_name TEXT NOT NULL UNIQUE,
 geology_class TEXT NOT NULL CHECK(geology_class IN ('igneous','sedimentary','metamorphic','metal','manufactured','organic','unknown')),
 distinguishing_features TEXT NOT NULL,
 known_ambiguities TEXT,
 source_work_id TEXT REFERENCES research_works(id)
);

CREATE TABLE IF NOT EXISTS stone_observations (
 id TEXT PRIMARY KEY,
 marker_id TEXT REFERENCES markers(id),
 photograph_id TEXT REFERENCES images(id),
 recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 observer_name TEXT,
 color_description TEXT,
 surface_texture TEXT CHECK(surface_texture IN ('smooth','granular','crystalline','powdery','mixed','unknown') OR surface_texture IS NULL),
 visible_crystals TEXT CHECK(visible_crystals IN ('yes','no','uncertain') OR visible_crystals IS NULL),
 grain_pattern TEXT CHECK(grain_pattern IN ('interlocking','sand_grains','fine_uniform','unknown') OR grain_pattern IS NULL),
 layering TEXT CHECK(layering IN ('flat_planes','banded','none_visible','uncertain') OR layering IS NULL),
 fossils TEXT CHECK(fossils IN ('yes','no','uncertain') OR fossils IS NULL),
 weathering TEXT,
 evidence_notes TEXT,
 capture_method TEXT NOT NULL DEFAULT 'visual',
 invasive_test_performed INTEGER NOT NULL DEFAULT 0 CHECK(invasive_test_performed IN (0,1)),
 review_status TEXT NOT NULL DEFAULT 'unreviewed',
 CHECK(marker_id IS NOT NULL OR photograph_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS stone_material_candidates (
 id TEXT PRIMARY KEY,
 observation_id TEXT NOT NULL REFERENCES stone_observations(id),
 material_id TEXT NOT NULL REFERENCES material_types(id),
 confidence TEXT NOT NULL CHECK(confidence IN ('possible','probable','verified')),
 supporting_features TEXT,
 contradicting_features TEXT,
 evidence_source_id TEXT REFERENCES sources(id),
 reviewer TEXT,
 reviewed_at TEXT,
 CHECK(confidence <> 'verified' OR reviewer IS NOT NULL),
 UNIQUE(observation_id, material_id)
);

CREATE TABLE IF NOT EXISTS material_reference_sources (
 material_id TEXT NOT NULL REFERENCES material_types(id),
 work_id TEXT NOT NULL REFERENCES research_works(id),
 locator TEXT,
 evidence_note TEXT,
 PRIMARY KEY(material_id,work_id)
);

CREATE TABLE IF NOT EXISTS material_provenance_hypotheses (
 id TEXT PRIMARY KEY,
 marker_id TEXT NOT NULL REFERENCES markers(id),
 quarry_id TEXT REFERENCES quarries(id),
 claim_text TEXT NOT NULL,
 source_id TEXT REFERENCES sources(id),
 confidence TEXT NOT NULL DEFAULT 'possible' CHECK(confidence IN ('possible','probable','verified')),
 review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE INDEX IF NOT EXISTS idx_observation_marker ON stone_observations(marker_id);
CREATE INDEX IF NOT EXISTS idx_candidate_observation ON stone_material_candidates(observation_id);
CREATE INDEX IF NOT EXISTS idx_material_provenance_marker ON material_provenance_hypotheses(marker_id);
