# Cemetery Picnic Club — USGS geology actual-file validation
Date: 2026-11-10. Phase: Massachusetts reference raster / New Hampshire document intake.

## Originals independently verified today
- `USGS_ngm16357.zip` — 37,644,226 bytes; SHA-256 `a48efc79baef0d9a468e14773bd4c66c1b261bd0bec9ddf521b232f8fbff418f`; CRC OK; required TIFF, `.aux.xml`, `.tif.txt`, README all present.
- `USGS_ngm16357_1.kmz` — 8,664,436 bytes; SHA-256 `e95b1fbb87d1d613cce8ddbc81011f7d114d839aecad2c58f38db1f3c3a0fd6c`; CRC OK; contains ground-overlay JPG and `doc.kml`, **no unit polygons**.
- `geo-nhx-250000-bmap-pg1-lyons1997.pdf` — 2,552,473 bytes; SHA-256 `d32949df18b7428b66247c20d6c2c57c8f19cffb2588a4985ef276ca155624aa`; one map-sheet PDF page; top edge reads 'BEDROCK GEOLOGIC MAP OF NEW HAMPSHIRE SHEET 1 OF 2'. Bibliographic author/year still require title-sheet or publication cross-check, since this uploaded page itself does not expose all title details.

## Massachusetts raster workflow actually run
- Original raster dimensions: 17,476 by 12,370 pixels, RGB, TIFF.
- Four GCPs sourced from the GeoTIFF's own auxiliary XML, EPSG:5069 (NAD27 / Conus Albers).
- First-order least-squares GCP fit RMS: 54.958 metres, maximum in-sample residual: 71.732 metres.
- Leave-one-out GCP errors: 311.137, 366.322, 168.424, 183.378 metres (max 366.322 m). This is NOT an externally calibrated absolute map-registration error.
- Actually produced decimation-8 EPSG:3857 and EPSG:4326 GeoTIFF reference rasters, not geology unit polygons.
- Visually inspected EPSG:3857 preview: legible whole historical map, margins/legend retained; *not* suitable to use directly as clipped terrain layer or to attribute map units by sampled pixel color.
- The Warren P01 approximate cemetery centroid (42.20909 N, 72.19660 W) was plotted on an explicitly unreviewed crop. No geological unit or quarry has been determined at the cemetery coordinate.
- Five offline pipeline tests passed (ZIP members, integrity, non-destructive extraction, traversal block, conflicts). No claim that whole-repository test suite passed.

## What is not done
- Exact P01 map unit is NOT verified. A real attributed MassGIS BEDROCK_1 symbol at that point still requires a successful real point query and comparison against Zen 1983 legend.
- No MassGIS bedlith polygons downloaded into CPC; no complete New England map database and no history of quarry/transport established.
- No Google Cloudflare D1 production migration, material inference, geologic site-to-stone assertion, or live map deployment.
- No standalone XYZ tile set published to R2 because scanned sheet boundaries and registration still need cartographic QA and the original margins should not overlay the map.

## Next reproducible steps
1. Run `python scripts/geology/query_massgis_bedlith.py` from a network-enabled machine, record all 18 point results, and independently check the Warren symbol against the original legend, map boundaries, and alternate source.
2. Obtain and process USGS OFR 2006-1272 integrated digital geology (including map units/age), and NH DS 215; extend to CT, RI, VT, and ME with official vector sources, citing separately.
3. Have a geologic-data reviewer sign off before moving `geology_units`, `geology_site_context` or polygons from unreviewed to verified.
4. Stage D1 import and camera site-geology display with non-provenance caveats; deploy only after tests and staging maps pass.

## Sources
Zen et al. (1983), USGS *Bedrock geologic map of Massachusetts*, doi:10.3133/70046713; MassGIS Bedrock Lithology: https://www.mass.gov/info-details/massgis-data-bedrock-lithology (~1.5 km estimated accuracy); Bennett et al. (2006), USGS DS 215, doi:10.3133/ds215.