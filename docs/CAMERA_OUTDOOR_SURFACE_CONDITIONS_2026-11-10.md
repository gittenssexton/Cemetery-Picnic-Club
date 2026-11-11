# Camera v0.9.2 — Outdoor light, stone weathering, and colored-surface diagnostics
Date: 2026-11-10
Status: experimental field pilot; Cloudflare preview deployed; not production

## Why
Outdoor monument photography has variable lighting: diffuse overcast light, bright sun, raking light that makes relief legible, tree shade and dappled shadows. Gravestones also carry lichen, algae, moss, fungal films, pigments, stains, crusts, mineral deposits, wet sheen, erosion and many types of stone texture. The phone cannot infer causes or species from RGB appearance alone.

## Implemented
- `web/camera/surface-conditions.js`: deterministic 4×4 local illumination grid and bounded statistics for stone region (or full scene when none selected); mean light, tile light range and variation, clipped highlights/shadows, nearly neutral bright reflection candidates, green color areas, warm-colored patches, grayscale edge energy.
- Heuristic flags with explicitly unverified terminology; no claims of biological taxon, wetness, material type or surface erosion.
- Non-destructive display-only brightness/contrast suggestions, bounded to roughly 0.9–1.17 brightness and 0.95–1.11 contrast. Existing saved original camera JPEG is never edited.
- `web/camera/discovery.js`: runs surface analysis on visible/locked candidate region, shows strongest field photo advice and visible flags, uses stone-region preview correction when toggled, snapshots diagnostic results in camera capture evidence. Fallback assesses scene when no stone candidate.
- `web/camera/index.html`: plain-language surface observation field during live preview.
- `tests/test_camera_surface_conditions.js` and CI hook: synthetic cases for uniform stone, uneven shade, green chromatic area, clipped reflection; source parse checks.
- Camera service worker cache bumped to `cpc-field-camera-0.9.2`; Cloudflare deployment and readback verified.

## Interpretation boundary
Color alone cannot distinguish lichen, algae, moss, mildew, mold, paint, reflected foliage, naturally tinted stone or mineral accretions. Dark coloration alone does not prove wetness; a polished stone may reflect light similarly to wet stone. A single shaded frame cannot identify persistent damage. Current module should be a conservative photographic diagnostic and repeat-shot adviser, not automated conservation reporting.

## Next field validation
1. Capture same stone under direct sun, dappled shade, overcast, low raking light, and after rainfall when safe.
2. Record regions that contain verified biological growth versus painted/rust/mineral stains and naturally colored stone, with expert confirmation when available.
3. Compare single-frame false positives, lighting variability and feature-lock drift; record examples before tuning thresholds.
4. Use multiple aligned images to differentiate persistent surface structure from passing shadows only after image stabilization is reliable.
5. Consider optional local-region contrast and multi-angle photometric imaging later, with preservation of originals and explicit provenance.
6. Never direct users to scrub, chemically treat, scrape or clean historic stones on the basis of machine image flags.

## External reading (research guidance, not training data)
- NPS cemetery preservation — https://www.nps.gov/articles/000/cemetery-preservation-course-cleaning-grave-markers.htm
- Discovering England's Burial Spaces photography guidance — https://www.debs.ac.uk/photography.html
- UCL gravestone weathering — https://www.ucl.ac.uk/mathematical-physical-sciences/earth-sciences/outreach/public-engagement/geology-london/st-pancras-gardens/gravestone-weathering
- Historic survey photo guidance — https://spadeandthegrave.com/2020/09/26/photography-of-gravestones-for-a-historic-survey-a-how-to-guide/

## Limitations
No actual field performance measurements from the new module yet. Heuristic pixel thresholds are preliminary. Exact dampness, biological identity, damage type and inscription reading cannot be established by this module. Some colored/background cues may be misleading because a candidate contour is not a perfect stone mask. Phone permissions and Google Drive OAuth remain separate deployment/testing issues.
