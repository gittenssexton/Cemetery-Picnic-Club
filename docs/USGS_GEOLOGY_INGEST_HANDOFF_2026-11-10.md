# Cemetery Picnic Club — USGS geology ingestion & own-database handoff
**Date:** 2026-11-10  
**Scope:** Massachusetts first (Pine Grove / Warren pilot), New Hampshire second.  
**Branch:** `feature/stone-camera-pilot`  
**Production status:** Planning schema and inventory only; **no D1 migration run, no geologic tile service deployed, no unit attribution or automatic rock recognition claimed**.

## 1. Purpose
Create a source-verified, citation-aware **CPC geology reference database** that can show mapped bedrock and surficial geology, classify the material of a monument tentatively, and investigate **independently supported** historical quarry origins. Treat these as separate entities. Use USGS, Massachusetts and other documented reference sources, not Mindat material until written permission and terms allow it.

## 2. Source files — verified and organized
All three uploads were moved **without renaming, overwriting or modifying originals** into:

Cemetery Picnic Club / `08_Geography_Maps_GIS/01_GIS_Survey_Data`  
https://drive.google.com/drive/folders/1Jfu7hl2HrrTKtgYJKJ4jAhbzATvP-O7E

**USGS_ngm16357.zip** — [Drive](https://drive.google.com/file/d/1RcXdi8XiAjeCaTwzu8Tob6WzHLpcWbZz/view)
- USGS NGMDB *Bedrock geologic map of Massachusetts*, E-an Zen and colleagues, 1983, 1:250,000.
- Contains `USGS_ngm16357_1.tif` (**17,476 × 12,370 pixels**), `USGS_ngm16357_1.tif.aux.xml`, `USGS_ngm16357_1.tif.txt`, and `README.txt`.
- README identifies the USGS/AASG National Geologic Map Database download and citation. Auxiliary XML identifies `NAD_1927_Contiguous_USA_Albers` (EPSG:5069) and **four control points** for a first-order polynomial transformation.
- ZIP SHA-256: `a48efc79baef0d9a468e14773bd4c66c1b261bd0bec9ddf521b232f8fbff418f`.

**USGS_ngm16357_1.kmz** — [Drive](https://drive.google.com/file/d/170lDnGOw7NeDEJFkJGTrns26EQSDaQnF/view)
- `doc.kml`, a **10,000 × 10,000** overlay JPG, and branding/image assets; **not** geological vector polygons.
- KML bounds: N 42.8868011971, S 41.2273004221, E -69.9162474005, W -73.5082464435 (WGS84-style latitude/longitude).
- KMZ SHA-256: `e95b1fbb87d1d613cce8ddbc81011f7d114d839aecad2c58f38db1f3c3a0fd6c`.
- Overlay coverage is approximate and includes surrounding map labels/legend; do **not** assume each point can be assigned a map-unit solely by querying a JPG pixel.

**geo-nhx-250000-bmap-pg1-lyons1997.pdf** — [Drive](https://drive.google.com/file/d/1pt7_FWSXy7yvbcQzZQdIyIfiN5PWQ0d9/view)
- New Hampshire bedrock map and descriptive legend, 1:250,000 (Lyons et al., 1997 per filename; verify citation against the title sheet).
- Readable legend includes granites, diorites, gabbros, syenites and metamorphic rocks; extracted text is imperfect due to map typography. It is **not** yet a structured geological-unit file.

## 3. What is established versus not established
**Verified:** file identities, directory and embedded asset lists, TIFF/JPG pixel dimensions, Massachusetts scale/year/authors from README, KML footprint, 4 GCPs and projected CRS in the auxiliary file, ZIP/KMZ checksums, successful Drive moves.

**Unverified:** registration accuracy at known benchmarks, actual rock at Pine Grove, automatically mapped geological unit at any coordinate, geological unit polygons, exact NH bibliographic citation, any historical quarry provenance, photo-classifier accuracy, production D1 state.

The supplied map is an image; it needs an appropriately licensed **attributed vector bedrock dataset** or human-verified unit polygon digitization before reliable point-to-rock-type lookups can be offered from our own local DB.

## 4. Target data model and terminology
The new **`db/migrations/0004_geological_map_core.sql`** extends existing research, material, marker, photo and quarry tables (including `0003_stone_identification.sql`).

- `geology_map_sources` — publication, year, map scale, region, reference system, rights, provenance and QA state.
- `geology_map_assets` — original Drive ID, filename, checksum, file dimensions, image/raster/tiles status, source linkage.
- `geology_units` — reviewed map symbol, formation name, lithology, age, legend locator and review status.
- `geology_unit_geometries` — **only** sourced/verified GeoJSON geometry, geographic CRS, digitization provenance and reviewer.
- `geology_site_context` — field observation coordinate, optional mapped unit evidence, source and caveat, **never equivalent to marker provenance**.
- Existing `material_types`, `stone_material_candidates`, `material_provenance_hypotheses`, `quarries`, `sources`, `research_works` stay authoritative for marker analysis.

Do **not** enter the 1983 image color values as `geology_units`. Each assigned symbol must come from a map legend and reproducible polygon / valid authoritative geodata. Maintain `review_status`.

## 5. Extraction and processing workflow
1. **Freeze originals** in the Drive GIS Survey Data folder; cite Drive ID and checksum. All processing in separate generated folders, never overwrite.
2. **Extract the archive locally**; verify member names, zip integrity and checksums. Keep the TIFF and `.aux.xml` together.
3. **Check georeferencing** using GDAL `gdalinfo` / `gdalwarp` on the raster with its auxiliary file. Four GCPs are not proof of good accuracy. Inspect map corners/known intersections and residuals. Convert NAD27 Albers (EPSG:5069) to EPSG:3857 for map tiles or EPSG:4326 for geographic data. Do not confuse image-pixel coordinates with map coordinates.
4. **Make low-zoom tiles** (COG or XYZ tiles) after cropping sheet margins carefully, or retain full sheet as a separately labeled historical reference overlay. Publish lightweight derivatives through Cloudflare R2 / static assets, not a 37 MB ZIP in browser code.
5. **Search for an attributed authoritative vector dataset** of Massachusetts bedrock geologic units, ideally MassGIS with documented unit field and scale. Prefer this to manual tracing. Where no vectors exist, digitize polygons from the scanned map with reviewer QA, marking them derived and approximate.
6. **Enter legends** (symbol, lithologic description, formation/unit name, geological age) with page/legend locator and source ID. NH PDF typography requires manual confirmation.
7. **Validate** 15–30 sampled points including Warren, neighboring municipalities, sheet edges, river valleys and boundaries against independent maps. Record QA residuals and unresolved areas.
8. **Populate D1** map metadata, legend, vetted polygons and locally stored geographic unit references (separate rollout). Use immutable source IDs and record extraction version.
9. **Integrate** with the existing Stone Camera Pilot: show site geology next to tentative photo material, without implying that a gravestone uses nearby bedrock.
10. **Add historic quarries** through independent quarry and transportation records, cited and confidence-labeled, before suggesting likely procurement region.

## 6. Quality gates
- No production deployment before staging map QA.
- No records marked verified based solely on map color similarity or AI transcription.
- No geologic point lookup without provenance, map scale and uncertainty.
- No exact quarry attribution without quarry/archival evidence; gravestones often use transported materials.
- Keep photo original separate from interpretations, transformations and derivative images.
- Mindat source remains disabled pending permission, not required for this work.
- USGS-authored works are generally US federal public-domain, but examine third-party map elements and state contributions before redistribution and include full citation.

## 7. Delivery structure and responsibilities
**Drive originals:** `08_Geography_Maps_GIS/01_GIS_Survey_Data` (moved and verified).

**GitHub source code and planning on feature branch:**
- `data/geology-usgs-upload-inventory-2026-11-10.json` — detailed machine-readable inventory with checksums.
- `db/migrations/0004_geological_map_core.sql` — database schema; **not executed in production**.
- `docs/USGS_GEOLOGY_INGEST_HANDOFF_2026-11-10.md` — this handoff.
- `web/stone-camera.html` — existing photo + optional Macrostrat geological lookup preview.

**Future generated folders (create only once processing begins):**
`generated/geology/ma_zen1983/{warp,tiles,geounits,qa}/`;
`generated/geology/nh_lyons1997/{georef,legend,qa}/`.

## 8. First concrete build milestone
**MA phase 1:** a verified source catalog plus Massachusetts geology tiles and *one* trustworthy point query at Warren, with the exact map unit name, source legend symbol, source citation and resolution caveat. If only a raster is available, show the raster *without claiming automated lithology identification*. This is the point where CPC begins to own a reproducible, independently stored geological reference system.


## 9. Validated execution checkpoint (2026-11-10)
The initial plan above is preserved for provenance. The following supersedes its pending-status statements:

- **Originals processed, not just inventoried.** SHA-256 and CRC verification passed for the 37.6 MB ZIP and 8.7 MB KMZ. The 2.55 MB NH PDF SHA-256 was recorded. See [actual-file validation report](./USGS_GEOLOGY_VALIDATION_2026-11-10.md).
- **GCP fit and warp actually run.** Four EPSG:5069 control points; RMS fit 54.958 m; maximum LOOCV 366.322 m (neither is independently confirmed positional accuracy). Decimation-8 EPSG:3857 and EPSG:4326 reference TIFFs exist, and a Pine Grove reference crop was produced. All outputs stored in [processed GIS folder](https://drive.google.com/drive/folders/1S02FCcz8uny9ac0PmyA6QQd-4S-l1_Of); originals remain untouched.
- **Pipeline restored:** [raster processing script](../scripts/geology/ma_zen1983_pipeline.py), [five offline tests](../tests/test_geology_processing.py), [sample points](../data/geology/qa_sample_points_ma.csv), [MassGIS query script](../scripts/geology/query_massgis_bedlith.py), and [source-only D1 seed](../db/seeds/0005_geology_map_sources.sql) committed on feature branch. Five offline tests passed locally. No repository-wide test-suite claim.
- **Camera pilot adjusted:** Warren example now uses the approximate Pine Grove centroid and links to the separately labeled *unreviewed reference* raster. The existing Macrostrat API remains a live external lookup, not a locally verified D1 result.
- **Still blocked:** original MassGIS attributed bedrock polygons are not available to this execution environment, so P01 source unit, legend, independent alignment and 18 real point queries are **unverified**. No geologic unit or quarry is assigned to any gravestone, no XYZ tile service has been deployed, and no D1 production migration has run.

**Do not promote this reference imagery to vetted geological polygons or claim phase 1 is fully complete until the real feature query, map-symbol review, independent georeferencing QA, staging and review gates pass.**


## 10. Further execution — offline MassGIS polygons (2026-11-10)

The original ZIP/KMZ and raster processing remain verified per section 9. An independent, properly sourced polygon import is now implemented at `scripts/geology/ingest_bedlith_offline.py`, with tests `tests/test_bedlith_offline.py`. It accepts the **actual MassGIS bedrock-lithology shapefile ZIP** (or extracted `.shp` plus sidecars), tests ZIP integrity and paths, requires geographic CRS and expected fields, projects the 18 existing QA point coordinates and performs point-in-polygon membership. The result is a reproducible `massgis_bedlith_unreviewed_qa.json` with immutable source ID, input SHA-256, original `BEDROCK_1` labels, mapped lithology categories, approximate distance to polygon boundaries and explicit non-provenance cautions. It writes **no D1 production units or quarry attribution**.

**Local result:** 11 / 11 offline processing tests passed, including compressed ZIP and shapefile input tested on synthetic features. This does not constitute a successful real MassGIS source ingest. No real `bedlith.zip` was present in the three original Drive assets, and direct retrieval from the MassGIS/ArcGIS endpoints was inaccessible in this runtime. Consequently, P01 and the other 17 point-unit assignments remain unverified.

**Exact additional input required:** MassGIS `BEDROCKLITHOLOGY_POLY` shapefile ZIP from [the official MassGIS data page](https://www.mass.gov/info-details/massgis-data-bedrock-lithology). Place the original ZIP in `Cemetery Picnic Club/08_Geography_Maps_GIS/01_GIS_Survey_Data`; do not modify it or substitute the USGS raster ZIP. Then run:

```bash
python scripts/geology/ingest_bedlith_offline.py --vector /path/to/bedlith.zip --points data/geology/qa_sample_points_ma.csv --out generated/geology/bedlith
python -m unittest discover -s tests -p 'test_*geology*.py' -v
```

The second command is an optional broader test sweep; `test_bedlith_offline.py` should also be selected explicitly by filename. Check the symbol/legend and independent point-location quality before treating any imported record as reviewed. No new Google/Mindat credentials are required to obtain MassGIS open GIS data. An accessible official download is a data dependency, not an account permission dependency.


## 11. MassGIS official shapefile located and genuinely processed (2026-11-10)

**Important correction to section 10:** The user had already uploaded the complete MassGIS bedrock shapefile as **separate component files** under [Cemetery Picnic Club / bedlith](https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw), not as a ZIP. No further download or account connection is needed for Massachusetts. The `.shp`, `.shx`, `.dbf`, `.prj`, and `.shp.xml` were successfully recovered and read, without altering Drive originals.

**Actual-source results:** 2,886 polygons, EPSG:26986, 322 unique unreviewed symbols, and all 18 test locations matched one polygon. P01 approximate Pine Grove centroid maps to `Ops` and source classification `Sulfidic Schists`, but lies **43.58 m** from a polygon boundary. The source's own estimated ~1.5 km spatial positional accuracy makes this a boundary-sensitive result, not a verified outcrop or bedrock attribution for the cemetery. 17 of 18 test points fall within 1.5 km of a polygon edge, using a cautionary heuristic rather than a statistical confidence score. No geological result identifies gravestone stone or quarry provenance.

**Saved products:** [processed geology folder](https://drive.google.com/drive/folders/1S02FCcz8uny9ac0PmyA6QQd-4S-l1_Of) contains the complete unreviewed point-query JSON, 18-location review CSV, 322-symbol list, SHA-256 manifest, separate **nonproduction** SQLite research database, processing script, and [real-data validation report](./MASSGIS_REAL_DATA_IMPORT_REPORT_2026-11-10.md).

**Remaining work:** independently verify the Pine Grove coordinate and boundary against a detailed source; resolve the original Zen 1983 `Ops` legend; scrutinize unit naming and spatial error; import only reviewed sources to staged D1; then validate Stone Camera UI. Do not claim a verified cemetery lithology or production integration yet.


## 12. Publisher crosswalk and proximity audit (2026-11-10)

USGS Bulletin 1605-A and the published OFR 2006-1272 Massachusetts unit metadata independently establish **Ops = Partridge Formation (sulfidic mica schist)** and **Dl = Littleton Formation**. See [CPC's detailed boundary report](./PINE_GROVE_BOUNDARY_REVIEW_2026-11-10.md) and machine-readable [radius results](../data/geology/pine_grove_boundary_review.json).

At P01's approximate coordinates, original MassGIS polygons place the point inside `Ops` only **43.58 m** from `Dl`. Both polygon types intersect a 100-m radius. `Dlf` enters within 1,000 m and five distinct map symbols intersect within 1,500 m. Because MassGIS estimates **~1,500 m spatial accuracy**, actual bedrock at Pine Grove cannot be asserted from the mapped point. No quarry or gravestone material identification follows.

Added: reproducible [boundary review script](../scripts/geology/build_boundary_review.py), [two offline synthetic tests](../tests/test_boundary_review.py), and **nonproduction** [publisher-symbol SQL seed](../db/seeds/0006_ma_zen1983_symbol_crosswalk.sql). SQL was verified idempotent on temporary SQLite; two unit-definition rows carry `transcribed` status; no site-context rows. The Stone Camera pilot now shows the qualified source definitions alongside the historical source, without representing its optional live Macrostrat query as independent validation. Production D1 remains untouched.


## 13. Cemetery position cross-check and high-resolution map sources (2026-11-10)

Two separately published but **unsurveyed** Pine Grove coordinate references differ by **80.5 m**; the original MassGIS shapefile places both in `Ops` but only **43.6 m** and **17.1 m** from the polygon boundary, respectively. The source's ~1.5-km spatial accuracy still precludes a verified cemetery formation assignment. The Town of Warren identifies Pinegrove Cemetery at **207 Maple Street**; this is an authoritative address, not a bedrock observation. See [location sensitivity JSON](../data/geology/pine_grove_location_sensitivity.json) and [full analysis and source links](./PINE_GROVE_LOCATION_HIGH_RES_SOURCE_REVIEW_2026-11-10.md). Four local consistency tests pass; none substitutes for field/georeferencing validation.

Identified **USGS GQ-1358** (1977, Warren quadrangle 1:24,000 bedrock map) as the priority independent high-detail map; additionally catalogued **GQ-1357** (surficial) and **MF-541-D** (depth to bedrock) in [idempotent, metadata-only seed 0007](../db/seeds/0007_warren_quadrangle_local_sources.sql). The GQ-1358 plate has **not** been georeferenced or its Pine Grove legend interpreted. Tested seed insert twice locally with 3 inventory-only rows; production D1 remains unchanged.

**Stone Camera feature-branch corrections:** source-query status now current; Pine Grove context is shown only on its example selection; geolocation disclosure accurately states coordinates are sent to the CPC API/Macrostrat on an explicit lookup; changed coordinates invalidate prior geology and export; live Macrostrat results are distinguished from MassGIS reference. This is committed code, **not** a claim that the deployed site was tested or published.
