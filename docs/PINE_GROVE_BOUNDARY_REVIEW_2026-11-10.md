# CPC — Pine Grove geology: publisher symbol crosswalk and boundary audit
Date: 2026-11-10 · Branch: `feature/stone-camera-pilot` · **Nonproduction review**

## Actual source and reproducibility
Data: user-supplied MassGIS `BEDROCKLITHOLOGY_POLY` shapefile in [Cemetery Picnic Club/bedlith](https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw), reprojected from EPSG:4326 reference coordinates to source EPSG:26986 before point and boundary distance computations. The `.shp` SHA-256 is `a2f5f8a10d4787afb9ee1d9cc1c3673ad7d23410faff8aed50aed1ec02b68d00`.

The site reference is an **approximate cemetery centroid**, 42.20909 N, 72.1966 W, not a surveyed grave, outcrop, or stone acquisition site.

## New publisher-supported label identification
- `Ops` = **Partridge Formation**, typical **sulfidic mica schist**, as defined for the map unit in USGS Bulletin 1605-A, p. A74 (1985), and USGS OFR 2006-1272 MA metadata. The MassGIS dataset's grouping `Sulfidic Schists` is consistent with this identification.
- `Dl` = **Littleton Formation** (Early Devonian), as named in USGS OFR 2006-1272 MA metadata and USGS Bulletin 1605-A. MassGIS groups it as `Pelitic Rocks`.
- These are documented **map symbol crosswalks**, not a new interpretation of the actual bedrock beneath a particular stone.

Sources:
- [USGS Bulletin 1605-A, Robinson and Luttrell discussion of Partridge and Littleton](https://ngmdb.usgs.gov/Geolex/resources/docs/USGS_B-1605-A_t.pdf)
- [USGS OFR 2006-1272 Massachusetts unit metadata](https://pubs.usgs.gov/of/2006/1272/documents/MAmetadata.htm)
- [MassGIS Bedrock Lithology technical description](https://www.mass.gov/info-details/massgis-data-bedrock-lithology)

## Actual nearby polygon intersection tests
| Radius around approximate centroid | Map units intersecting radius |
|---|---|
| 100 m | `Ops` (Partridge), `Dl` (Littleton) |
| 250 m | `Ops`, `Dl` |
| 500 m | `Ops`, `Dl` |
| 1,000 m | `Ops`, `Dl`, `Dlf` (Littleton subtype; interpretation needs detailed review) |
| 1,500 m | `Ops`, `Dl`, `Dlf`, `Dgd`, `gr` (last two require separate source-specific legend review) |

The point is inside `Ops` in the source polygons, **43.58 m** from the shared `Ops`–`Dl` boundary. The stated spatial accuracy of this generalized MassGIS layer is **approximately 1,500 m**, meaning the boundary distance is **not** an estimate of 44 m field accuracy. Five symbols nearby do **not** mean equal likelihood of each type beneath the point. The 1,500 m radius is an illustrative positional sensitivity envelope only.

## Decision
- **Verified:** Official publisher symbol definitions for `Ops` and `Dl`, source shapefile integrity/provenance, reproducible mapped geometry relations.
- **Unverified:** Exact cemetery centroid, independent geologic boundary alignment, bedrock exposure at the cemetery, rock of any gravestone, quarry origin.
- **Safe app wording:** “MassGIS historical map places this *approximate* coordinate in Partridge Formation (Ops), near Littleton Formation (Dl). Mapped boundary ≈44 m away; map positional uncertainty ≈1.5 km. Actual site geology requires review. This does not identify a memorial's stone.”
- **Safe database behavior:** Two symbol dictionary rows may be staged as `transcribed`, with publisher evidence; do **not** create any verified `geology_site_context` row for Pine Grove, any stone material inference, or quarry association. Production unchanged.

## Reproduction
Run `scripts/geology/build_boundary_review.py --shape path/to/BEDROCKLITHOLOGY_POLY.shp --out path/to/pine_grove_boundary_review.json`. Tests in `tests/test_boundary_review.py`. Local synthetic tests: 2/2 passed. The symbol seed SQL `db/seeds/0006_ma_zen1983_symbol_crosswalk.sql` was run twice in a temporary SQLite database and produced exactly two unique crosswalk rows.

## Remaining work
Review precise cemetery geolocation against a surveyed/local authority source, compare independent higher-resolution geology (where mapped), check georeferencing and boundaries on-site or from authoritative local studies. Only then approve staged D1 attribution. Do not treat the 1983 scan control-point fit as an independent check of the MassGIS vector.