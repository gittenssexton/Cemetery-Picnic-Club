# Cemetery Picnic Club — live pixel-contour correction checkpoint
Date: 2026-11-10
Workstream: camera (feature/field-camera-pilot, draft PR #3)
Preview: https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/

## User observation
Perfect circles and rectangular highlight proposals hop around the active camera and fail to follow photographed gravestone silhouettes. Stabilizing these arbitrary shapes does not make them credible contours.

## Changes committed
- `web/camera/pixel-contours.js`: low-resolution, on-device connected-component pixel segmentation targeting moderately gray/neutral surfaces, rejecting green vegetation, tiny components, frame-edge components, overly wide/low-filled regions. Uses horizontal scan-line boundaries to create many-point curved polygons, **not squares or circles**. Tracks candidates using bounding-box IoU; only shows a contour after two matching frames; hides on missing matches, resets on stop.
- `web/camera/discovery.js`: removed automatically drawn rectangle outline and floating gold circles; draws actual polygon curves in mint, text-like lines as blue underlines. Interior texture regions are still counted but do not get misleading circular markers. Live image enhancement remains display-only.
- `web/camera/index.html`: overview review uses pixel contour polygons instead of rectangular auto-proposals; keeps editable manually selected yellow target **box** distinctly labeled as manual selection, not as detected silhouette.
- `web/camera/sw.js`: updated offline cache to `cpc-field-camera-0.7.2`; precaches contour engine.
- `tests/test_camera_pixel_contours.js`: added deterministic curved synthetic monument, stability and overlay-regression assertions, wired into existing GitHub Actions workflow.

## Verification and honesty
- JavaScript syntax passed for all three edited camera source modules in the available JS runtime.
- Synthetic 160x200 RGB example with a gray rounded-top monument against green grass yielded a 138-point curved contour, with different x values at the crown vs sides. Tracker held it off on the first detection, displayed after the second, hid it on a missing scan. This is **not** a real cemetery segmentation accuracy test.
- Cloudflare preview Worker deployed; source readback shows pixel-contour module, UI integration, cache v0.7.2 and preserved export components.
- No physical device or measured cemetery field accuracy yet; GitHub CI final result not verified.

## Limitations
- The current grayscale/chroma rule is deliberately narrow. It can miss dark or highly colored stone, zinc, light marble, shadowed monuments or vegetation-covered edges. It may still trace non-stones with similar color. It performs no semantic material, carver or inscription identification.
- Automatic contours are **provisional**. Tap-selection and manual silhouette tracing remain available. The yellow selected target rectangle is an **editable target marker**, not a stone outline.
- Real validation needs human-reviewed contours across many distinct stones/backgrounds and rigorous false-positive analysis. A later segmenter may require color/texture feature engineering or an on-device trained model; do not equate a shape-fitting algorithm with an authenticated grave identity.
- Production and global database remain unchanged.

## Next steps
1. Retest same screen photograph; record whether shapes actually follow stone edges or vanish when uncertain.
2. Capture and review at least 10 independent real monument photos with various stone colors, lighting, and complex backgrounds.
3. Add manual foreground/background taps and edge correction where automatic separation fails.
4. Measure contour IoU against reviewed masks; avoid pushing an apparently confident incorrect contour.
5. Preserve camera-source rights and private/public export policies.
