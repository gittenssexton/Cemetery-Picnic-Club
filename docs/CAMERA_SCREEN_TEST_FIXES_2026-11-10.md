# CPC Camera screenshot stress test — 2026-11-10

Owner: camera workstream.
Preview: https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/
Status: Source fixes deployed to isolated preview; physical iPhone retest pending.

## Field input
User pointed the active iPhone camera at an image of several gravestones displayed on a separate screen. The captured overview showed a central curved-top marker, left and right markers, grass, an American flag, and display/UI borders. The earlier heuristic drew misplaced broad dotted boxes over grass/screen features. The camera overlay said "Processed reference" when the overview photo was actually shown unprocessed.

## Corrections
- `web/camera/guided-capture.js`: reject tiny connected edge clusters, wide screen-like contours and wide/horizontal high-contrast textures; cap automatic proposals at three, keep manual tap-selection always available. **Less false-positive risk, no verified object detector yet.**
- `web/camera/index.html`: correct "Original overview" status in overview photo review. Clarify that automatic boxes are visual candidates only.
- Add explicit **Test/reference image on another screen** checkbox; captures made in this mode do not attribute the phone's real-time GPS or cemetery candidates to the graves depicted on the screen. Store `capture_source='photograph_of_display_reference_test'` and `location_status='reference_image_no_site_attribution'`. Manual evidence/source selection stays separate.
- `tests/test_guided_capture.js`: added source/wiring/geometry regression for screen mode, label and candidate limit.
- `web/camera/sw.js`: invalidates old offline app shell under `cpc-field-camera-0.7.1`.
- Experimental preview Worker deployed; Cloudflare accepted the update and worker source contains revised UI, heuristics and cache marker.

## Important limits
- Current algorithm identifies **edge/contrast shapes**, not gravestones. Rectangular proposals can still be wrong. Video of a monitor is a harder input than native photos because perspective, moiré, glare and image borders introduce false edges. A real cemetery test remains necessary.
- Do not interpret green GPS badges as verification of a *depicted* site. Test mode prevents assignment during the capture but does not turn a photographed scene into georeferenced data.
- Do not claim OCR, carver identification, material classification or reliable stone segmentation. No model was trained in this change.
- JavaScript inline parser passed; nine targeted dynamic/static assertions passed. No physical Safari retest or CI run verified.
- Production, D1, public URLs and PR merge unchanged.

## Next QA
1. On iPhone, enable Test/reference image mode before capturing a screen; confirm stored JSON has null location and `reference_image_no_site_attribution`.
2. Use a single displayed gravestone first, then several; assess candidate boxes, tap selection and normalized coordinates.
3. At a real cemetery, capture an overview containing 3+ individual stones. Record false-positive/false-negative counts and lighting.
4. Compare the manual target rectangle to the yellow selected overlay; make sure it remains aligned after rotation.
5. Introduce labeled data and a proper silhouette/instance segmentation approach if the edge-only proposals remain unreliable; continue to require manual confirmation.
