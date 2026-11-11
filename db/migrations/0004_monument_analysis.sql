-- 0004: Monument form, iconography, lettering and workshop attribution
-- Run after 0001-0003. Observations are not attributions.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS marker_form_observations (
 id TEXT PRIMARY KEY, marker_id TEXT NOT NULL REFERENCES markers(id),
 image_id TEXT REFERENCES images(id), observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 form_type TEXT NOT NULL DEFAULT 'unknown' CHECK(form_type IN ('tablet','headstone','footstone','obelisk','ledger','box_tomb','cross','column','other','unknown')),
 silhouette TEXT NOT NULL DEFAULT 'unknown' CHECK(silhouette IN ('round','segmental_arch','ogee','stepped','shouldered','pediment','rectangular','irregular','other','unknown')),
 crown_description TEXT, finial_description TEXT, border_description TEXT,
 height_mm REAL CHECK(height_mm>0), width_mm REAL CHECK(width_mm>0), thickness_mm REAL CHECK(thickness_mm>0),
 dimensions_method TEXT CHECK(dimensions_method IN ('measured','photogrammetric_estimate','unknown')),
 edge_condition TEXT, symmetry_notes TEXT, evidence_note TEXT, review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE IF NOT EXISTS carving_feature_observations (
 id TEXT PRIMARY KEY, marker_id TEXT NOT NULL REFERENCES markers(id),
 image_id TEXT REFERENCES images(id), observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 region TEXT NOT NULL CHECK(region IN ('tympanum','shoulder','border','body','base','reverse','side','other')),
 technique TEXT CHECK(technique IN ('incised','low_relief','high_relief','intaglio','pierced','mixed','unknown')),
 tool_mark_description TEXT, relief_description TEXT, execution_notes TEXT,
 signature_text TEXT, signature_reading_status TEXT CHECK(signature_reading_status IN ('visible','uncertain','none_seen')),
 production_quality_notes TEXT, evidence_note TEXT, review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE IF NOT EXISTS lettering_style_observations (
 id TEXT PRIMARY KEY, marker_id TEXT NOT NULL REFERENCES markers(id), image_id TEXT REFERENCES images(id),
 observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, region TEXT,
 letter_family TEXT CHECK(letter_family IN ('roman','italic','blackletter','script','sans_serif','mixed','unknown')),
 incised_or_relief TEXT CHECK(incised_or_relief IN ('incised','raised','mixed','unknown')),
 serif_description TEXT, stroke_terminals TEXT, letter_width_notes TEXT,
 letter_spacing_notes TEXT, line_spacing_notes TEXT, baseline_notes TEXT,
 distinctive_glyphs_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(distinctive_glyphs_json)),
 punctuation_notes TEXT, spelling_notes TEXT, hand_consistency_notes TEXT,
 reviewed_transcription_id TEXT REFERENCES inscriptions(id),
 evidence_note TEXT, review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE IF NOT EXISTS motif_interpretations (
 id TEXT PRIMARY KEY, marker_id TEXT NOT NULL REFERENCES markers(id),
 motif_id TEXT REFERENCES motifs(id), image_id TEXT REFERENCES images(id),
 location_on_marker TEXT, visual_description TEXT NOT NULL,
 proposed_meaning TEXT, cultural_context TEXT, date_range_context TEXT,
 regional_context TEXT, alternative_interpretations_json TEXT NOT NULL DEFAULT '[]'
 CHECK(json_valid(alternative_interpretations_json)),
 claim_id TEXT REFERENCES claims(id), source_id TEXT REFERENCES sources(id),
 confidence TEXT NOT NULL DEFAULT 'unknown' CHECK(confidence IN ('documented','supported','tentative','unknown')),
 review_status TEXT NOT NULL DEFAULT 'unreviewed'
);

-- Candidate matches are suggestions only; sourced historical claims belong in claims/claim_evidence.
CREATE TABLE IF NOT EXISTS carver_attribution_candidates (
 id TEXT PRIMARY KEY, marker_id TEXT NOT NULL REFERENCES markers(id),
 craftsperson_id TEXT REFERENCES craftspeople(id), workshop_label TEXT,
 attribution_level TEXT NOT NULL CHECK(attribution_level IN ('same_hand_candidate','workshop_candidate','stylistic_tradition','documentary_attribution')),
 status TEXT NOT NULL DEFAULT 'candidate' CHECK(status IN ('candidate','under_review','supported','rejected')),
 rationale TEXT NOT NULL, supporting_features_json TEXT NOT NULL DEFAULT '[]'
 CHECK(json_valid(supporting_features_json)),
 contradicting_features_json TEXT NOT NULL DEFAULT '[]'
 CHECK(json_valid(contradicting_features_json)),
 source_id TEXT REFERENCES sources(id), comparison_marker_id TEXT REFERENCES markers(id),
 reviewed_by TEXT, reviewed_at TEXT,
 CHECK(craftsperson_id IS NOT NULL OR workshop_label IS NOT NULL),
 CHECK(comparison_marker_id IS NULL OR comparison_marker_id<>marker_id),
 CHECK(status <> 'supported' OR reviewed_by IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS marker_similarity_evidence (
 id TEXT PRIMARY KEY, marker_a_id TEXT NOT NULL REFERENCES markers(id),
 marker_b_id TEXT NOT NULL REFERENCES markers(id),
 feature_domain TEXT NOT NULL CHECK(feature_domain IN ('silhouette','lettering','iconography','technique','material','geography','overall')),
 method TEXT NOT NULL, score REAL CHECK(score BETWEEN 0 AND 1),
 qualitative_note TEXT NOT NULL, source_image_a TEXT REFERENCES images(id),
 source_image_b TEXT REFERENCES images(id), reviewer TEXT,
 CHECK(marker_a_id<>marker_b_id)
);

CREATE INDEX IF NOT EXISTS idx_form_marker ON marker_form_observations(marker_id);
CREATE INDEX IF NOT EXISTS idx_carving_marker ON carving_feature_observations(marker_id);
CREATE INDEX IF NOT EXISTS idx_lettering_marker ON lettering_style_observations(marker_id);
CREATE INDEX IF NOT EXISTS idx_motif_marker ON motif_interpretations(marker_id);
CREATE INDEX IF NOT EXISTS idx_carver_marker ON carver_attribution_candidates(marker_id);
CREATE INDEX IF NOT EXISTS idx_similarity_marker_a ON marker_similarity_evidence(marker_a_id);
