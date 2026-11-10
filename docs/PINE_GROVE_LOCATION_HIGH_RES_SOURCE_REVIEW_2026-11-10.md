# Cemetery Picnic Club — Pine Grove position sensitivity and higher-detail USGS sources
Date: 2026-11-10 · Branch: `feature/stone-camera-pilot` · Research/staging only

## Evidence actually computed against uploaded shapefile
Source: MassGIS `BEDROCKLITHOLOGY_POLY.shp`, SHA-256 `a2f5f8a10d4787afb9ee1d9cc1c3673ad7d23410faff8aed50aed1ec02b68d00`; source CRS EPSG:26986. This is the uploaded original, not a re-created geology map.

Two published **unsurveyed cemetery-location references**, both checked against the same source polygons:

| Reference | Latitude | Longitude | Polygon | Proximity to polygon boundary |
| --- | ---: | ---: | --- | ---: |
| OpenStreetMap/Mapcarta cemetery-center reference | 42.2090900 | -72.1966000 | Ops, Partridge | 43.6 m |
| GNIS-derived reference on third-party cemetery listing | 42.2098066 | -72.1967443 | Ops, Partridge | 17.1 m |

The reference points differ by 80.5 m in projected map coordinates. They **are not surveyed control points**. Both polygon queries reproduce `Ops`, but neither confirms real on-site bedrock, because the polygon position is mapped only to approximately 1.5 km accuracy. `Dl` (Littleton) is adjacent. See [machine-readable source-stamped result](../data/geology/pine_grove_location_sensitivity.json); four consistency tests pass, and none is a scientific ground-truth test.

Sources for reference locations:
- https://mapcarta.com/22240244 (OSM way 29915659; centroid used as the original CPC pilot seed)
- https://www.anyplaceamerica.com/directory/ma/worcester-county-25027/cemeteries/pine-grove-cemetery-602368/ (GNIS-derived coordinate; independent listing, not independent survey)
- Town of Warren's 2024 Cemetery Department report identifies Pinegrove Cemetery as **207 Maple Street** and maintained at 25 acres: https://www.warren-ma.gov/sites/g/files/vyhlif3996/f/news/s50981_warren_tr.pdf. Address/property identity is authoritative; it does not provide an independently surveyed geologic point.

## Higher-detail local maps found, but NOT interpreted
The existing MassGIS dataset is based on generalized mapping. More relevant published sources for subsequent independent review:

1. **USGS GQ-1358, Pomeroy (1977)**, *Bedrock geologic map of the Warren quadrangle*. Scale **1:24,000**. DOI https://doi.org/10.3133/gq1358 ; PDF https://pubs.usgs.gov/gq/1358/report.pdf . Priority source for checking the Partridge–Littleton location. A publication record and digital PDF are indexed, but the plate's actual symbol at Pine Grove has **not been read or georeferenced** in this session.
2. **USGS GQ-1357, Pomeroy (1977)**, *Surficial geologic map of the Warren quadrangle*. Scale **1:24,000**. DOI https://doi.org/10.3133/gq1357 . Surface deposits, not a formation-level bedrock identification.
3. **USGS MF-541-D, Londquist and Pomeroy (1974)**, *Map showing depth to bedrock, Warren quadrangle*. Scale **1:24,000**. DOI https://doi.org/10.3133/mf541D . Relevant to whether bedrock is covered, but cannot identify a gravestone stone or quarry.

The metadata-only, idempotent SQL catalog seed is `db/seeds/0007_warren_quadrangle_local_sources.sql`; tested twice against a temporary SQLite schema (three source rows, all `inventory_only`). This is not a production D1 deployment.

## App hygiene fixes made on feature branch
- Removed outdated claim that MassGIS had not been queried; 18 sample queries were completed on real polygons.
- Pine Grove-specific historical geometry appears only when its *example coordinate* is selected, not automatically for arbitrary GPS inputs.
- Disclosed that clicking the live geology lookup transmits user-entered coordinates to the app's `/api/geology` endpoint and Macrostrat; a promise of no server logging is **not** warranted.
- New coordinate input clears stale geology and hides an earlier comparison/export until rerun; a live lookup result carries `sourceType: live_macrostrat_not_MassGIS`.
- Exporting the Pine Grove example supplies **unverified reference geology separately** from any live Macrostrat data; no quarry provenance inference.

## Acceptance gates not yet met
- Need actual view of the full GQ-1358 plate and its legend and an independent georeferencing/field check.
- Cemetery parcel boundary/survey must be checked before a definitive on-site geological claim.
- No production database migration, hosted feature map or end-to-end deployed camera verification occurred.
- Do not assign Partridge Formation, Littleton Formation, or any quarry origin to a specific headstone.