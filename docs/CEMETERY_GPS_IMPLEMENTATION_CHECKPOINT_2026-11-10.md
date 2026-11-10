# CPC GPS Cemetery Identification — Implementation checkpoint
Date: 2026-11-10
Branch: `feature/field-camera-pilot`
Status: GPS candidate matching integrated in the browser field camera; **not deployed to production; no surveyed cemetery boundaries**.

## Implemented
- `web/camera/cemetery-resolver.js`: WGS84 GPS candidate matcher with metric distance to polygon segments, polygon holes, multipolygons, stale-fix classification, alternative candidates, point-only discovery, accuracy-circle overlap and conservative confidence.
- `web/camera/cemetery-sites.js`: explicit point-only Pine Grove candidate from the Pine Grove dossier at latitude 42.20909, longitude -72.19660; source ID and approximate-centroid limitation preserved. No fabricated St. Paul or South Warren locations.
- `web/camera/index.html`: no longer preselects Pine Grove; live candidate results display by GPS reading; user can pick a catalog candidate or leave unknown. Selection **does not** mean verified cemetery assignment.
- Field `record.json` now includes `location_observation_id`, full candidate result, `cemetery_assignment` (with explicit `unverified` state), and registry version. GPS candidates are recomputed immediately before record creation. Existing export code serializes these fields.
- `web/camera/sw.js`: resolver and registry cached offline with cache version bump.
- `tests/test_cemetery_gps_resolver.js`: synthetic geometry and point-only policy assertions. A direct JavaScript execution of this test source passed 23 assertions on 2026-11-10; embedded camera script syntax parsed successfully.

## Outstanding / blockers before production
1. iPhone Safari physical GPS and camera permission test, including airplane/offline mode and GPS-denied export.
2. Test ZIP `record.json` against legacy v0.1–v0.5 imports; verify EXIF GPS and privacy presentation in exported photo variants.
3. Source/review municipal or surveyed cemetery polygons for actual within-boundary verification. Pine Grove remains **approximate centroid only**.
4. Verify St. Paul and South Warren coordinates independently before adding them to the point registry; historic Forefathers Ground remains uncertain.
5. Validate combined-complex hierarchy against real documented geometry and all containment/crossing permutations; currently this is a conservative general-purpose candidate matcher, not a complete relationship graph.
6. Reconcile D1 migration numbering with other branches and actual deployed migration history before database writes.
7. Run privacy/security and operational staging review; keep preview Worker independent of production.

## Evidence policy
Never present a camera GPS point as a surveyed burial plot. User-selected cemetery does not verify a marker or person, point-only centroid is not a boundary, and distinct grounds are not merged by name or proximity.

## Follow-up hardening (same date)
- Fixed a real point-to-segment distance bug found by the synthetic tests.
- Parent complexes no longer imply resolution of an unidentified child ground: `complex_child_unresolved` with `parent_complex_ids` and `unresolved_child` is returned.
- Multiple plausible child cemeteries sharing a parent remain `multiple_candidates`; the parent relation never merges them.
- A stale GPS fix now receives an explicit camera warning and a distinct captured-record status; manually typed positions display as unverified entries rather than surveyed facts.
- Starting the next monument clears the previously selected cemetery, preventing accidental carryover across records.
- Checked JavaScript syntax and executed 23 resolver assertions with a lightweight JS harness; this does not replace physical-device field testing, privacy review or full build CI.

## QA note
The existing static preview deployment was not updated as part of these commits; production is untouched.

## GPS accuracy and evidence hardening (2026-11-10, further session)
- Reject malformed or non-closed polygon rings and invalid GeoJSON coordinate points rather than accepting an untrustworthy boundary.
- A boundary marked `verified_boundary` must also have a nonempty source ID to count as verified.
- A separate point-only cemetery name falling within the GPS accuracy radius can block exclusive attribution to a polygon-defined site; no point can alone prove boundary containment.
- Added tests for missing boundary provenance, malformed geometry, MultiPolygon containment, and conflicting point candidates.
- New camera records include UUID observation/record IDs, device position observations with fix age, accuracy, provider, timestamps, explicit `restricted_by_default` visibility, and the statement that phone position is not a grave survey.
- Preserved free-text cemetery provenance independently from user selection; exported silhouette mask metadata now reflects whether a manual contour or initial rectangle was used.
- Added static camera integration and privacy guard assertions (`tests/test_camera_gps_contract.js`).
- **Executed:** 30 geometry resolver assertions + 21 camera contract assertions = **51 passing source-level assertions** in a JavaScript test harness; browser camera/ZIP field QA not yet done.

## Remaining release blockers
- Review physical iPhone camera/GPS/ZIP samples, confirm EXIF behavior and no coordinate leakage to publicly reachable endpoints.
- Obtain defensible real source polygons; current Pine Grove data are still point-only.
- Inspect D1 production migrations before schema additions; no deployment/migration conducted.
- Verify complex hierarchy, historical names, effective dates, map rights and source licensing before import.
