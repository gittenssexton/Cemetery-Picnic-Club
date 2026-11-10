# Massachusetts bedrock geology — real dataset processing checkpoint

Date: 2026-11-10
Source: MassGIS Bedrock Lithology, original USGS Open-File Report 03-225 (Robinson and Kapo, 2003).

## Newly located input
The user-supplied complete shapefile is in the [Cemetery Picnic Club / bedlith folder](https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw). Original ".shp", ".dbf", ".shx", ".prj" and publisher metadata ".shp.xml" were read without modifying originals. Local materialization appended ".bin" to some binary names; local copies were renamed back to native shapefile extensions before processing.

## Actual processing results
- Real geometries loaded: **2,886 polygons**.
- Source coordinate system: **EPSG:26986**.
- Distinct original map symbol candidates: **322**. These are not 322 scientifically reviewed unit definitions.
- QA locations matched: **18 / 18**. All point assignments are provisional; several are towns' approximate centres.
- Location tests within 1,500 m of a mapped polygon boundary: **17 / 18**. This is a cautionary heuristic, not a statistical probability of wrong classification.
- **P01 Pine Grove Cemetery approximate centre:** original unit symbol **Ops**; **Sulfidic Schists** (source classification; broader class Metamorphic Rocks Undivi); map-geologic province **NH - Maine Sequence**; nominal point-to-polygon-edge distance **43.58 m**.

## Critical limitations
The source metadata estimates ~1.5 km spatial accuracy, much worse than P01's ~44 m polygon-edge proximity. **The specific bedrock under Pine Grove cannot be asserted confidently from this coordinate.** The 'Ops' symbol and rock-group attribute are a reproducible map query, *not* an independently verified formation assignment, observed outcrop, gravestone material or quarry origin. Bedrock map unit legend crosswalk to Zen et al. 1983 still requires human review.

## Deliverables
- 'massgis_bedlith_unreviewed_qa.json': full original values for 18 sample-point matches.
- 'massgis_18_location_review.csv': compact QA table with boundary flags.
- 'massgis_unit_symbols_unreviewed.csv': 322 source symbols and counts.
- 'massgis_source_manifest.json': file-level checksums and provenance.
- 'massgis_research_review.sqlite': temporary **unreviewed research database** (not production D1).
- 'build_review_package.py': deterministic packaging of the actual results.

## Next verification gates
Review P01 against original Zen 1983 legend, verify the cemetery centroid against authoritative surveyed coordinates, perform independent spatial alignment checks, review source license conditions, and test the D1 staging import. Do not deploy reviewed unit labels or assert stone provenance based on local geology. No additional GIS download or account connector is required for this Massachusetts step.