# Cemetery Picnic Club — independent Warren GQ-1358 plate review checkpoint

**Date:** 2026-11-10  
**Target:** Pine Grove Cemetery, Warren, MA  
**Status:** full-resolution bedrock plate **not obtained**. Source metadata and low-resolution whole-sheet image found; no valid independent formation assignment.

## What is directly verified

1. **USGS Geologic Quadrangle GQ-1358** is John S. Pomeroy's (1977) *Bedrock geologic map of the Warren quadrangle*, scale **1:24,000**, DOI: https://doi.org/10.3133/gq1358. The USGS publication describes a map plate with text. The indexed `https://pubs.usgs.gov/gq/1358/report.pdf` is only a jacket/standard-symbols report in the accessible text extraction; it does not yield a readable detailed geology plate for the cemetery.
2. **USGS Open-File Report 73-226** is an earlier *preliminary* Pomeroy bedrock map of the same Warren quadrangle; the official site lists a separate 1:24,000 plate: https://pubs.usgs.gov/publication/ofr73226 and https://pubs.usgs.gov/of/1973/0226/plate-1.pdf. The plate could be identified but not rendered/obtained in this session. **Do not substitute this superseded plate for the 1977 version without version labeling.**
3. An indexed, full-sheet **low-resolution photographic reproduction** of the GQ-1358 map confirms the document includes colorful geological units, legends, and cross-sections. Its resolution is insufficient to read the map unit, cemetery base map and exact contact near 207 Maple Street reliably. It must not be used to infer the bedrock at Pine Grove.
4. A separate, accessible **2018 USGS surficial materials map of Warren**, at 1:24,000, is https://pubs.usgs.gov/sim/3402/sim3402_quadrangle/063_Warren.pdf. Its mapped material descriptions rely on Pomeroy (1977) but cover **glacial and surface deposits, not the 1977 bedrock formations**. Therefore it cannot confirm a Partridge/Littleton bedrock boundary.

## Independent comparison attempted versus earlier MassGIS study

Our original user-supplied MassGIS BEDROCKLITHOLOGY_POLY shapefile includes 2,886 polygons, source CRS EPSG:26986. Two approximate *unsurveyed* cemetery point references, 80.5 m apart, both fall in `Ops` (Partridge Formation) in that generalized statewide map. The polygon boundary with `Dl` (Littleton Formation) lies approximately 44 m or 17 m away depending on the reference point. The source's quoted geographic positioning uncertainty is approximately 1.5 km, much larger than either separation. **The detailed GQ-1358 plate has NOT independently confirmed or contradicted these assignments.**

A newly created pair of [MassGIS source-data diagnostic maps](https://drive.google.com/drive/folders/1S02FCcz8uny9ac0PmyA6QQd-4S-l1_Of) visualizes the 500 m and 1.7 km neighborhoods without pretending to be the 1977 plate. The map does not include cemetery parcel boundaries or observed outcrops.

## New reproducible independent-review gate

`/scripts/geology/validate_warren_plate_gcps.py` accepts an **actual legible GQ-1358 full-sheet raster** and a hand-verified manifest of at least four map control points plus **two separate independent holdout points**. It projects geographic coordinates into Massachusetts EPSG:26986, fits affine map coordinates, and calculates measured internal residuals and independent holdout errors. It records the original plate's SHA-256. The engineering **100 m max holdout warning** is a local QC convention and is **not a claim of publication positional accuracy**. Even a passing result has only `candidate_alignment_manual_review` status; `site_geology_verified` stays `false`. The script neither decodes geological map colors nor writes D1 site context.

Five synthetic tests passed locally (good fit, large mismatch, point reuse, missing plate, wrong map source). Tests are unit tests, not map verification.

## Exact outstanding input / acquisition action

**Needed:** the **actual full-resolution 1977 GQ-1358 *bedrock map plate*** (not `report.pdf` jacket, not 1977 GQ-1357 *surficial* map, not earlier OFR 73-226). Official title page: https://pubs.usgs.gov/publication/gq1358 ; USGS Store listing (paper product 24438): https://store.usgs.gov/product/24438 . If the user can obtain a readable digital map scan, save it in `Cemetery Picnic Club/08_Geography_Maps_GIS/01_GIS_Survey_Data` named `USGS_GQ1358_Warren_1977_bedrock_full_plate_original.<extension>`, preserving the original file bytes. **No account connector is missing.** If only a paper version is accessible, a readable full-sheet scan can also serve as a preliminary source but still needs independent control-point alignment.

Once the full sheet is available: inspect native unit legend; locate Pine Grove using identifiable roads/topography and verified parcel address; record four or more accurate GCPs and distinct independent checks; run georeferencing QA; independently compare contact and source-unit label against MassGIS; record discrepancies explicitly. Avoid asserting exact bedrock or gravestone/quarry origin without additional evidence.

## Sources

- Pomeroy, J.S. (1977), USGS GQ-1358, DOI https://doi.org/10.3133/gq1358
- Pomeroy, J.S. (1973), USGS OFR 73-226, DOI https://doi.org/10.3133/ofr73226
- Stone, J.R., and DiGiacomo-Cohen, M.L. (2018), USGS SIM 3402 Warren quadrangle https://pubs.usgs.gov/sim/3402/sim3402_quadrangle/063_Warren.pdf
- MassGIS Bedrock Lithology https://www.mass.gov/info-details/massgis-data-bedrock-lithology