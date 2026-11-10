# Cemetery Location Registry — Checkpoint 2026-11-10

## Scope and branch
Branch: `feature/camera-stone-geology-integration`.
Location registry only. Camera production files and D1/R2 remain unchanged.

## Verified changes
- Restored nonempty `tools/cemetery_registry/import_osm_cemeteries.py`, `overpass_warren_amherst.ql`, and `test_import_osm_cemeteries.py` from `feature/field-camera-pilot`. Those three files had been empty in this branch despite the handoff claiming they existed.
- Added `tools/cemetery_registry/import_mhc_burial_grounds.py`: public MHC Inventory Points FeatureServer layer 0, `TYPE = 'Burial Ground'`, paginated JSON acquisition and SHA-256 per response, preserved raw pages and normalized **unreviewed Zone A** candidates.
- Added `tools/cemetery_registry/test_import_mhc_burial_grounds.py` with five synthetic fixture tests; **tests added, not executed in this session**.
- Verified official MassGIS documentation updated June 4, 2026 confirms public MHC point/area layers, `TYPE` values, unique `MHCN` and `COMMON_NAM`. Official FeatureServer service confirms layer 0 is points and layer 1 areas. The code currently imports **points only**.

## How to run on a network-enabled workstation
```bash
python -m unittest discover -s tools/cemetery_registry -p 'test_*.py' -v
python tools/cemetery_registry/import_mhc_burial_grounds.py \
  --raw-output incoming/mhc_burial_grounds_raw_2026-11-10.json \
  --output data/cemetery_registry/mhc_zone_a_candidates.json
```

MHC source:
https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/MHC_Inventory_GDB/FeatureServer

Documentation:
https://www.mass.gov/info-details/massgis-data-mhc-historic-inventory

Raw source responses are intended as provenance snapshots; re-check source reuse conditions before distributing a combined derivative dataset. Preserve MassGIS/MHC credit.

## Outstanding blockers and honest counts
- Verified newly downloaded MHC features: **0**. Network DNS access to the ArcGIS endpoint failed in the working runtime. The source service is public, but execution of the script on a network-enabled runner is still required.
- Verified newly downloaded OSM features: **0**. Existing Overpass acquisition also has not succeeded in this runtime.
- Verified Route 9 segments: **0**. Zone B remains unassessed; do not substitute a guessed line.
- Reviewed canonical cemetery records approved for camera registry from this workstream: **0**.
- No executed test result for the newly added MHC fixture tests is claimed.

## Next actions
1. Run the tests on a network-enabled checkout; correct failures before data ingest.
2. Execute both source imports, preserve dated raw responses, publish candidate counts and source identifiers.
3. Obtain connected, reviewed Route 9 centerline and apply the three-mile corridor. Zone A and Zone B membership must be independently recorded.
4. Import public MHC area features as separate unreviewed geometry; do not represent their boundaries as surveyed.
5. Cross-check municipal burial ground lists town by town; reconcile duplicate candidates into canonical IDs through manual evidence review.
6. Only after review: produce versioned GeoJSON/SQLite publication and exercise camera resolver integration with GPS ambiguity and offline scenarios.

## Safety and data discipline
Do not ingest excluded archaeological resources, private grave-level GPS, or third-party Google Maps-derived location records. Do not auto-merge same-name or neighboring sites. A historical inventory point is not a surveyed grave or property boundary.
