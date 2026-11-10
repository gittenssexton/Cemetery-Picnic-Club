# USGS geology ingestion — reconciliation and current execution status
Date: 2026-11-10
Project: Cemetery Picnic Club / feature/stone-camera-pilot

## Audit outcome
The Drive session record (USGS_GEOLOGY_INGEST_SESSION_2026-11-10.md) claims that a pipeline, source seed, 18-point CSV and 12 tests were created and that 33 tests passed. However, a direct GitHub read on this branch on 2026-11-10 found the described `scripts/geology/ma_zen1983_pipeline.py`, `db/seeds/0005_geology_map_sources.sql`, and `data/geology/qa_sample_points_ma.csv` absent. Do not treat the reported 33 passing tests as independently confirmed against the current remote branch.

## Changes actually committed in this recovery session
- `data/geology/qa_sample_points_ma.csv`: 18 actual QA sampling coordinates from the Drive tracker, explicitly marked approximate where applicable.
- `scripts/geology/query_massgis_bedlith.py`: standard-library-only ArcGIS feature-service point query; preserves raw attributes and caveats; writes unreviewed JSON and reports per-point failures.
- `db/seeds/0005_geology_map_sources.sql`: six metadata-only map source rows and three original asset references, with provenance and immutable IDs.

## Validated scientific/data design
- MassGIS Bedrock Lithology provides generalized Massachusetts bedrock polygons and an original `BEDROCK_1` symbol from the source map; estimated spatial accuracy 1.5 km. Citation: https://www.mass.gov/info-details/massgis-data-bedrock-lithology
- `BEDROCK_1` is NOT a reviewed formation name and `LITHO_CODE` is NOT an independent identification of any grave marker.
- The PDF, TIFF, KMZ are originals; do not overwrite.
- The existing `db/migrations/0004_geological_map_core.sql` defines schema only and has not been applied to production.
- Existing Stone Camera queries Macrostrat optionally, not the locally reviewed CPC unit catalog.

## Commands for reproducible phase-1 checkpoint
1. Run migration 0004 and seed 0005 in a temporary/local SQLite database; do not apply to production.
2. With normal network access, run:
   `python3 scripts/geology/query_massgis_bedlith.py`
   Inspect `generated/geology/bedlith_point_qa.json` and all 18 responses.
3. Reconcile `P01` with the Zen 1983 original map and published legend. Review map boundary uncertainty. Require reviewer name, date and legend locator before `geology_units` or `geology_site_context` is elevated to verified.
4. Retrieve original ZIP/KMZ from Drive, independently recompute SHA-256, inspect all ZIP members and georeferencing control-point residuals; only then warp and tile the scan. Do not infer that 4 GCPs imply accuracy.
5. Test staged local unit lookup in Stone Camera and preserve caveat: mapped bedrock does not identify marker material/quarry.

## Blockers
- Live ArcGIS query endpoint inaccessible from present execution environment; no P01 map unit can be honestly reported.
- The reported raster extraction/warping pipeline and associated 12 tests were not found on the inspected branch; restore from source if available or rebuild/test.
- No verified geological units, shapes, legends, tiles, quarry origins, or D1 deployment have been produced here.

## Quality gate
Keep production unchanged. Do not silently claim ingestion is complete. The milestone requires a reproducible observed P01 point response, crosschecked published map symbol and legend, spatial caveat, and reviewer signoff.
