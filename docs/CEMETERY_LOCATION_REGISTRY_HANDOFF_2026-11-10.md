# Cemetery Picnic Club — Cemetery Location Registry Handoff

**Date:** 2026-11-10  
**Owner:** LOC/CEM cemetery-geodata workstream, distinct from camera implementation  
**Status:** Data architecture and runnable import scaffold created; **regional inventory not yet harvested or completeness-audited**  
**Canonical location:** `gittenssexton/Cemetery-Picnic-Club`, `docs/CEMETERY_LOCATION_REGISTRY_HANDOFF_2026-11-10.md`

## 1. Geographic scope

**Zone A:** a 25-statute-mile (40,233.6-meter) straight-line radius around the Pine Grove Cemetery approximate reference point **42.20909, −72.19660**, Warren, Massachusetts. This point comes from the project Pine Grove dossier and is **not** a surveyed boundary or grave location.

**Zone B:** a **3-mile corridor on each side** of the actual sourced Massachusetts Route 9 centerline continuing to Amherst, including areas outside Zone A. The union of the zones is the desired extent, with each candidate tagged with the zone(s) it belongs to. Obtain a verified current Route 9 polyline from OpenStreetMap or public road centerlines; do not invent a route from Pine Grove to Route 9 or approximate by a straight line. The import code intentionally omits Zone B until a Route 9 LineString is supplied.

Record active cemeteries, church burial grounds, family plots, historic/abandoned grounds, separate named sections, alternate names, and complex memberships. **All** requires a coverage audit with individual town inventories; no single map is exhaustive.

## 2. Reusable datasets / rights

1. **OpenStreetMap**: extract `landuse=cemetery` and `amenity=grave_yard` points, ways and relations using Overpass. Retain OSM IDs/tags and applicable ODbL attribution/share-alike obligations: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
2. **Massachusetts Historical Commission inventory**: MACRIS/MassGIS points and areas include burial grounds, but also non-cemetery historic resources. Inspect the layer schema and filter to burial-ground records rather than treating all features as cemeteries. https://www.mass.gov/info-details/massgis-data-mhc-historic-inventory and https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/MHC_Inventory_GDB/FeatureServer
3. **MassGIS open-space polygons**: includes *some* cemeteries only where recognized as open-space resources, not a complete list. https://www.mass.gov/info-details/massgis-data-protected-and-recreational-openspace ; public-domain state data credit: `MassGIS (Bureau of Geographic Information), Commonwealth of Massachusetts EOTSS`.
4. **Town cemetery commissions, assessors, historical societies, historic mapping**, and sourced municipal survey geometry to cross-check omissions, old burial grounds, names and borders.
5. **Google Maps** only for permitted human-in-the-loop comparison; do **not** scrape Google cemetery names, coordinates or polygons into CPC. Google Maps Platform places/geocoding policies restrict bulk extraction/caching and derivative geodatabases: https://developers.google.com/maps/documentation/places/web-service/policies

## 3. What has been built

- `tools/cemetery_registry/overpass_warren_amherst.ql`: Overpass query retrieves OSM candidates from the Pine Grove circle and an intentionally generous Route 9 vicinity bounding box. Bounding-box inclusion is **not** itself corridor membership.
- `tools/cemetery_registry/import_osm_cemeteries.py`: reads a previously downloaded Overpass JSON response and optionally a reviewed `route9_warren_amherst.geojson` LineString/MultiLineString; selects candidate locations within Zone A or within 3 miles of the supplied route; removes duplicate source IDs; preserves OSM source URLs, alternate names, provenance, zone flags and geometry quality; emits `CPC_CEMETERY_CANDIDATES_V1` JSON.
- For OSM ways, a properly closed ring is retained as `osm_polygon_unreviewed`; a relation without assembled rings stays **point-only**, not a fabricated polygon. All candidates are unreviewed. No automatic proof of a cemetery, merged complex or grave coordinates.
- `tools/cemetery_registry/test_import_osm_cemeteries.py` contains 5 local tests which passed against synthetic fixtures on 2026-11-10.

After a proper external download:

```bash
python tools/cemetery_registry/import_osm_cemeteries.py \
  --osm-json incoming/warren_amherst_overpass.json \
  --route9-geojson incoming/route9_warren_amherst_reviewed.geojson \
  --output data/cemetery_registry/warren_amherst_candidates.json
python -m unittest discover -s tools/cemetery_registry -p 'test_*.py' -v
```

Without the route file, the script returns **only** Zone A matches and marks `route_geometry_provided=false`.

## 4. Historic and combined cemetery identity

One canonical record per confirmed cemetery/ground, with alternate names and separately sourced geometry versions. Maintain distinct types `cemetery`, `cemetery_complex`, `historical_ground`, `cemetery_section` and `cemetery_alias`. Distinguish two adjacent cemeteries from two names for one cemetery, and a parent complex from its historic child grounds. Use **source-reviewed, dated relations** such as `part_of_complex`, `contains_historical_ground`, `administratively_managed_with`, `shares_entrance_with`, `adjacent_to`, `renamed_to`, `merged_into_at_date`, and `possible_duplicate_of`. Names, proximity, shared roads or boundary touching **do not prove merger**.

Keep the imported OSM source identity and a review mapping to canonical cemetery IDs. Never merge duplicated point/area entries automatically by a simplistic distance rule. Never assign a private grave photo to an individual burial plot from phone GPS alone.

## 5. Camera contract

The geodata workstream publishes reviewed, versioned, read-only cemetery entities/geometry, aliases, relations and source licenses. The camera's existing `cemetery-resolver.js` can then compare phone GPS and uncertainty with boundaries or point-only locations. Camera display must distinguish:

- `within_reviewed_boundary` (likely location, but user confirmation still required),
- `near_unverified_point` (closest known cemetery, not proof user is inside),
- `multiple_nearby_sites` or `complex_child_unresolved` (show candidates separately),
- `outside_coverage`, `stale_gps`, and `no_gps` (show unknown, invite correction).

Keep raw coordinates private by default, respect screenshot/reference mode, and record exact location-source provenance and catalog version. A user-selected site is not independent verification. An unresolved site must be saved without inventing a name.

## 6. Ten-step execution backlog

1. Acquire licensed OSM data for the 25-mile radius; save immutable dated raw download and request metadata.
2. Source a correctly connected Route 9 centerline to Amherst and complete the corridor extraction.
3. Import MassGIS/MHC burial grounds, retaining source IDs and feature types; audit duplicate and distinct identities.
4. Review town-by-town cemetery lists (including unnamed and abandoned grounds) to discover omitted sites.
5. Check polygon outlines, point-only centroids, CRS and stated precision; do not upgrade OSM outlines to surveyed.
6. Preserve historic names, family plots and combined-site relations with documentary citations and effective dates.
7. Reconcile duplicated map features into reviewed canonical identities without losing raw provenance.
8. Publish reviewed versioned GeoJSON/JSON/SQLite snapshots with license ledger, separate from private individual burial data.
9. Integration-test the camera in several municipalities, including areas around Warren, Ware, Belchertown, and Amherst; test GPS uncertainty, multiple candidates and offline mode.
10. Report counts, coverage gaps, tests and artifacts to the main project; only then approve a camera registry snapshot and later production database migration.

## 7. Owners and reporting protocol

**Geodata workstream owns** `tools/cemetery_registry/`, `data/cemetery_registry/`, source licenses, geometry, aliases and combined-ground research. It writes `docs/CEMETERY_LOCATION_REGISTRY_CHECKPOINT_YYYY-MM-DD.md` after each batch with counts, original-source IDs, geographic coverage, gaps and test outcomes.

**Camera workstream owns** `web/camera/` (GPS UI, local position matching, offline cache, imaging and exports); it consumes **reviewed** snapshots from LOC/CEM only. Do not independently edit these camera files from a new conversation.

**Main Cemetery Picnic Club integration owns** migration-number reconciliation, production D1/R2 schema/permissions and merge/release approval. GitHub documents are the cross-conversation handoff; Drive copies are snapshots, not live two-way chat synchronization.

## 8. Honest implementation status

The existing camera site registry has only **one** Pine Grove approximate point. The OSM import scaffold and its 5 synthetic unit tests were created and run, but the first attempted direct Overpass retrieval failed due to unavailable network DNS in the execution environment. Therefore **no newly downloaded regional cemetery inventory or comprehensive cemetery count is claimed**, and the Route 9 polyline is outstanding. No production service, main site or D1 database has changed.
