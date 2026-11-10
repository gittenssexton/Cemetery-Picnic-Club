-- 0004: Geological source catalog and independently reviewed map units.
-- SQLite / Cloudflare D1. Migration only; no production DB changes.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS geology_map_sources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  authors TEXT,
  year INTEGER,
  publisher TEXT,
  scale_denominator INTEGER,
  region TEXT,
  source_url TEXT,
  provider TEXT NOT NULL,
  rights_note TEXT,
  citation_text TEXT,
  source_datum TEXT,
  coordinate_system TEXT,
  geometry_status TEXT NOT NULL DEFAULT 'raster_only'
    CHECK(geometry_status IN ('raster_only','candidate_vector','verified_vector','unknown')),
  validation_status TEXT NOT NULL DEFAULT 'inventory_only'
    CHECK(validation_status IN ('inventory_only','georef_review','georef_validated','unit_review','ready')),
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS geology_map_assets (
  id TEXT PRIMARY KEY,
  map_id TEXT NOT NULL REFERENCES geology_map_sources(id),
  original_filename TEXT NOT NULL,
  drive_file_id TEXT,
  format TEXT NOT NULL,
  sha256 TEXT,
  byte_size INTEGER,
  width_px INTEGER,
  height_px INTEGER,
  geographic_bounds_json TEXT,
  storage_key TEXT,
  reference_only INTEGER NOT NULL DEFAULT 1 CHECK(reference_only IN (0,1)),
  role TEXT NOT NULL CHECK(role IN ('original_archive','georef_raster','google_earth_overlay','published_pdf','tiles','other')),
  status TEXT NOT NULL DEFAULT 'unprocessed'
    CHECK(status IN ('unprocessed','validated','reprojected','tiled','quarantined')),
  UNIQUE(map_id,original_filename)
);

CREATE TABLE IF NOT EXISTS geology_units (
  id TEXT PRIMARY KEY,
  map_id TEXT NOT NULL REFERENCES geology_map_sources(id),
  original_symbol TEXT NOT NULL,
  formal_name TEXT,
  lithology TEXT,
  geologic_age TEXT,
  description TEXT,
  legend_locator TEXT,
  interpretation_status TEXT NOT NULL DEFAULT 'unreviewed'
    CHECK(interpretation_status IN ('unreviewed','transcribed','verified','rejected')),
  reviewer TEXT,
  reviewed_at TEXT,
  UNIQUE(map_id,original_symbol)
);

CREATE TABLE IF NOT EXISTS geology_unit_geometries (
  id TEXT PRIMARY KEY,
  unit_id TEXT NOT NULL REFERENCES geology_units(id),
  geometry_geojson TEXT NOT NULL,
  geometry_crs TEXT NOT NULL DEFAULT 'EPSG:4326',
  geometric_source TEXT NOT NULL,
  review_status TEXT NOT NULL DEFAULT 'unreviewed',
  reviewer TEXT,
  simplification_tolerance_m REAL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS geology_site_context (
  id TEXT PRIMARY KEY,
  marker_id TEXT REFERENCES markers(id),
  query_lat REAL NOT NULL CHECK(query_lat BETWEEN -90 AND 90),
  query_lng REAL NOT NULL CHECK(query_lng BETWEEN -180 AND 180),
  location_accuracy_m REAL,
  map_id TEXT REFERENCES geology_map_sources(id),
  unit_id TEXT REFERENCES geology_units(id),
  provider_response_json TEXT,
  query_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  context_type TEXT NOT NULL DEFAULT 'local_bedrock'
    CHECK(context_type IN ('local_bedrock','surficial','historical_quarry_reference')),
  attribution TEXT,
  review_status TEXT NOT NULL DEFAULT 'unreviewed',
  caveat TEXT NOT NULL DEFAULT 'Mapped site geology does not establish monument stone quarry provenance'
);

CREATE INDEX IF NOT EXISTS idx_geo_units_map ON geology_units(map_id);
CREATE INDEX IF NOT EXISTS idx_geo_assets_map ON geology_map_assets(map_id);
CREATE INDEX IF NOT EXISTS idx_geo_context_marker ON geology_site_context(marker_id);
