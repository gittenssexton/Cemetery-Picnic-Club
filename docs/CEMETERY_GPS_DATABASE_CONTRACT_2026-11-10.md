# CPC GPS & Cemetery Relationship Database Contract — pre-migration draft
**Date:** 2026-11-10
**Status:** Staged design only; do NOT execute until D1 migrations have been reconciled.

## Existing deployment constraints
The feature branches have overlapping numbered migrations. Before assigning any new number, compare `db/migrations` on main and all active branches, deployed `d1_migrations` / Cloudflare D1 history, and previously applied schema. Do not run a speculative `0004` migration. The current browser pilot persists records in IndexedDB and ZIP; **it does not save to D1**.

## Relational identity and evidence rules
- Canonical cemetery entity IDs are permanent; a renamed or merged entity retains its historical identity.
- Distinguish `cemetery`, `cemetery_complex`, `historical_ground`, and `cemetery_section`.
- Named grounds and aliases are not interchangeable. Do not merge entities by proximity, name similarity, shared entrance or administration.
- Each geometry is independently versioned with source, source/validity dates, quality, CRS and rights metadata. A centroid is not a verified boundary; camera GPS is not a surveyed grave location.
- Relations carry `subject_id`, `predicate`, `object_id`, `source_id`, `review_status`, `valid_from`, `valid_to`, and reviewer. Validated parent links may produce a hierarchy, but identity remains separate.
- Reviewed relation graph must prevent cycles in containment. Unreviewed/disputed relations never establish hierarchy.
- Location observations preserve WGS84 fix, device accuracy, fix timestamp, method, visibility and capture time.
- Match candidates persist **all** results, not just a chosen site; include geometry revision/source, reason codes and historical resolver/catalog versions.
- Assignments must preserve selection method and verification status, review trail, supersession and original observation. Never upgrade a `gps_candidate` or `user_selected_unverified` to `verified` automatically.
- Sensitive GPS coordinates must be access controlled in the database/API. A string label `restricted_by_default` in a ZIP is **not** backend access control.
- The photo or plot cannot inherit a site identity just because its coordinates are near a cemetery centroid.

## Proposed schema entities (names pending reconciliation)
`cemetery_entity_names`, `cemetery_geometry_versions`, `cemetery_entity_relationships`,
`location_observations`, `cemetery_match_candidates`, `cemetery_assignments`,
`cemetery_assignment_reviews`, `cemetery_section_map_links`.

All foreign keys should reference existing `cemeteries` or a reconciled entity table and `sources`, without rewriting legacy marker/person IDs. Store imported polygon payloads with explicit geospatial index strategy and a separate review process.

## Acceptance gates
1. Audit current D1 migration version inventory and collisions.
2. Stage SQL under a *new noncolliding migration number only after reconciliation*.
3. Add SQLite/D1 foreign-key, check-constraint and rollback tests.
4. Verify 2026 pilot references against municipal records before adding site polygons or historical ground links.
5. Prove role-based restrictions for public endpoints, and avoid public EXIF coordinates by default.
6. Test import/export round-trips for old camera records and new candidate/relationship JSON.
7. Complete Safari/iPhone offline, stale-GPS, permissions and camera ZIP validation.
8. Obtain review approval before merging or deploying production.

## Current code
- `web/camera/cemetery-resolver.js`: geodesic / local metric cemetery candidate matching.
- `web/camera/cemetery-relations.js`: sourced effective-dated relation validation and hierarchy.
- `web/camera/cemetery-sites.js`: source-backed Pine Grove centroid only and **no verified relations**.
- `web/camera/index.html`: user selection explicitly unverified; capture snapshot with match candidates and relation evidence.
- `tests/test_cemetery_gps_resolver.js`, `tests/test_cemetery_relations.js`, `tests/test_camera_gps_contract.js`.

**Scope warning:** The relationship module is a pure JavaScript data validation layer. It is not yet a persistent relationship database or comprehensive historical source registry.
