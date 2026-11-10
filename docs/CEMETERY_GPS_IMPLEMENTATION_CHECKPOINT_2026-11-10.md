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
- `tests/test_cemetery_gps_resolver.js`: synthetic geometry and point-only policy assertions. A direct JavaScript execution of this test source passed 14 assertions on 2026-11-10; embedded camera script syntax parsed successfully.

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
