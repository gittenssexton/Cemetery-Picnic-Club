# CPC Drive scan: stone identification + camera integration — 2026-11-10

## Scope and current read status
Scanned the project root and relevant descendants: technical, Soule/carver, iconography, stone/geology, science, Pine Grove field photographs, directory maps/database, and two newly uploaded GIS bundles. Read the latest integration handoff, regional Soule research, USGS ingestion session, photo manifests and two sometimes-conflicting Daniel Combs field reports. Did not visually classify every new photograph or independently validate map polygon geometry.

## 1. New field photograph batch
`02_Pine_Grove_Warren_Pilot/03_Field_Research/02_Gravestone_Photos_IMG_5287-5295` contains **9 JPEGs**. Manifest tags 5287 and 5294 as context, seven other images as individual stone candidates. Specific labels (Bliss, Thomas, Rebekah, winged death's head) are **provisional descriptions** and need visual and inscription review. This is a much better initial variety test than the initial eight-photo set, which depicts one monument. Never imply nine verified unique stones without deduplication.

## 2. Material ambiguity is a feature requirement
The two source reports for the Combs candidate conflict:
- `Field Observation 001` suggests slate or fine-grained phyllite/schist.
- `Field Record 001` says the raised lettering, panel repetition and uniform finish could instead indicate cast zinc (“white bronze”). It is explicitly unverified.
The camera must expose **stone / metal / manufactured / unknown** as top-level hypotheses; preserve multiple candidate materials and contradictory evidence, with `cannot_determine` default. Capture photos of seams, reverse, base, foundry signatures and shallow side-lit relief. Never pretend regional bedrock confirms monument composition.

## 3. GIS and source materials
New `bedlith.zip` and expanded `bedlith/` contain a full shapefile set `BEDROCKLITHOLOGY_POLY.{shp,shx,dbf,prj}` plus XML metadata. Regional mapping is USGS Robinson/Kapo 2003 OFR 03-225 with ~1.5 km stated accuracy. The `outlin/` `outlina1` and `outlinp1` shapefile family requires dataset identification before use; do **not** treat them as automatically extracted gravestone contours. The full GIS point-in-polygon query for Warren remains unrun according to `USGS_GEOLOGY_INGEST_SESSION_2026-11-10.md`; source metadata and smoke tests are not a validated local result.
Safe camera idea: geologic context as optional informational panel; no auto-accept material/quarry matches.

## 4. Iconography, carving, handwriting
- Scanned Nov 8 symbol guide supplies illustrations and attributed meanings; preserve citation page and possibility of ornamental-only use.
- `Research Update 02` identifies Soule family, signed-carver references and distinction between a style match and proven maker. The document cites Kelly/Williams signed-stone index and Soule exemplars; copyright and signature readings must be verified.
- Capture a front-wide, tympanum/crown close-up, lettering close-up, back/side/base and contextual framing. Associate all with one marker; classify individual images by angle.
- Compare signature, letter shape, relief depth, symmetric borders and recurring crown geometry; do not attribute by iconography alone.

## 5. Existing cemetery database (separate from camera)
The map/database directory now contains SQLite, HTML map, ZIP and CSV reports. The latest session reports **322 provisional directory entries** extracted partially from 3 of 8 directory photos, **zero verified grave coordinates**. Do not autojoin phone GPS or provisional directory names to specific burial plots. Map coordinates need survey or verified geometry.

## 6. Integration blockers and dependencies
The November 10 domain handoff says one research core and separate CEM/VIT/GEO/ICO/CAR/IMG/HIS/KIN/LOC/CON evidence modules. Existing feature branches have **colliding migration 0004 identifiers** (geology vs monument analysis) and vital records 0005. Nothing should be merged into main or deployed to production until D1 migration history and dependencies are checked and collision resolved on the dedicated integration branch. Camera preview may continue independently.

## 7. Camera improvement work queue
1. Add capture-type presets: front, crest, inscription, symbol, side/base, context, signature.
2. Extend material choices to zinc/cast metal, granite, sandstone, slate, marble, schist/phyllite, unknown, with multi-candidate evidence and no auto-verified status.
3. Improve contour UI: user-correctable multi-point outline, reject colored shadows/adjacent stones, classify occluded/broken contour portions distinctly.
4. Add **photo set grouping** by one marker ID and require permission to publish/train from originals.
5. Add photographic QA: blur, glare and low-contrast warning; no aggressive digital modifications to master original.
6. Read and annotate iconography regions; show the catalog's meaning only after human selection or model inference with confidence.
7. Record inscription uncertainty per span; preserve letterform images for later signed-workshop comparison.
8. Provide *optional* GIS contextual source and explicit uncertainty; no quarry match from map alone.
9. Add geolocation-age and accuracy thresholds; manual coordinates labeled independently, no silent map joins.
10. Integrate with global domain contracts and D1/R2 only after migration, rights, access and CI checks.

## Source pointers
- Root: https://drive.google.com/drive/folders/10kQDrxfn097oa4XRGe7_ee44zR9bJ2OW
- New field photographs: https://drive.google.com/drive/folders/1fwntCgamZPCDtF4bT3WsTCQ3mC51de0q
- Main GIS: https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw
- New domain handoff: https://docs.google.com/document/d/19wiVbe-DKjADiSpi1ogSuZBbz6MQ7nvbiYVxd6XCctM/edit
- USGS geology handoff: https://drive.google.com/drive/folders/1zHRo7g53IPlsQ5sM3AIvmL8jRJWAaVJ8
- Draft camera PR: https://github.com/gittenssexton/Cemetery-Picnic-Club/pull/3

**This is a source-based review and integration plan; no new AI training or classification was performed in this scan.**
