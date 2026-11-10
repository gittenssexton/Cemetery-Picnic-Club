# CPC — Unified camera, stone identification and geology pilot (2026-11-10)

**Status:** branch integrated and GitHub automated tests GREEN; **not deployed to production**.

## Merge record
- Integration branch: `feature/camera-stone-geology-integration`
- Source branch 1: `feature/stone-camera-pilot` (Stone Camera field material guide, USGS/MassGIS data research, reference mapping, evidence gates).
- Source branch 2: `feature/field-camera-pilot` (guided mobile camera, GPS/cemetery candidate resolver, monument isolation and original-image preservation, private ZIP and reviewed public ZIP).
- [PR #6](https://github.com/gittenssexton/Cemetery-Picnic-Club/pull/6) **merged into integration branch**, not into main.
- [Draft PR #7](https://github.com/gittenssexton/Cemetery-Picnic-Club/pull/7) is the proposed future mainline review. It was deliberately **not merged**.
- Production website, database and Cloudflare deployment remain unchanged.

## Combined pilot: paths and data contract
- `/camera/` (`web/camera/index.html`) is the main field capture UI.
- `/stone-camera.html` remains the separate rule-based material guide, linked from the unified camera.
- Camera site-candidate selection (not GPS verification) can choose `cem-pine-grove-warren`. The user can click **Show site geology reference** to read the existing MassGIS context **offline**, without transmitting coordinates.
- Only an explicitly selected opt-in checkbox places `geology_context` into the **private** captured JSON record. All imported context is tagged `boundary_sensitive_unverified`, and material identity/quarry origin are *not inferred*.
- A public/shareable ZIP goes through an allowlist schema in `web/camera/export-privacy.js` and **does not include** `geology_context`, cemetery matching or GPS.
- A capture marked `reference_image_no_site_attribution` strips geological context as well as location/site identity.
- The approved static reference is **site-level** research for the approximate Pine Grove reference point, not a live point-in-polygon query for each photographed stone.
- No photos are uploaded automatically; private ZIPs are local exports.
- The legacy Stone Camera's live `/api/geology` (Macrostrat) HTTP lookup remains a separate **unverified endpoint/deployment dependency**. The new offline geological-reference panel does **not** depend on that endpoint.

## Migration conflict resolved
- `0004_geological_map_core.sql`: source maps, geological units and optional unreviewed site context.
- `0005_monument_analysis.sql`: monument observations and attribution candidate tables, renumbered from old duplicate `0004_monument_analysis.sql`.
- The original `motif_interpretations` table in `0002_global_research_core.sql` represents general interpretations of motifs. Renamed the monument-specific table to `marker_motif_interpretations` to avoid a column-incompatible collision.
- No verified `geology_site_context` or quarry assignments are added by reference seeds.

## Automated verification
On commit `f5bf47f1c70a303d68931f430b0b54ee4d46a8b1`, CI succeeded in **two independent GitHub Action runs** (runs #362, #363):
- [Successful CI run #362](https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42872759725)
- [Successful CI run #363](https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42872771234)

Checks included SQLite migration/seed integration, MassGIS synthetic vector tests with Python geospatial dependencies, GPS and cemetery resolver/relations, private/public ZIP privacy, guided capture, live on-device analysis, pixel contours, and geology-context contract. This is **automated repository validation**, not physical-device confirmation.

## Manual review gates before production
1. Deploy an isolated preview of `web/` with appropriate service-worker scope (do **not** overwrite production).
2. On iOS Safari and Android Chrome, verify camera permission, GPS/no-GPS/manual location, gallery capture, site selection, local geology explanation, guide link and export.
3. Inspect private ZIP JSON for explicit opt-in geology content, no inferred monument material/quarry, and preserved original image. Inspect public ZIP for absence of coordinates and geology; review any user-approved image/location cues.
4. Test the optional legacy `/api/geology` Macrostrat route if intended for release, or clearly mark it unavailable; this integration does not build that endpoint.
5. Review the detailed Warren GQ-1358 bedrock plate when available; keep Partridge/Littleton as provisional site-level reference until independent field/map QA.
6. Review schema deployment and apply migrations only after staging backup/rollback checks. No production D1 migration has run here.

**Decision:** ready for *combined pilot testing*; no claim of completed production deployment or confirmed geological unit at a grave.
