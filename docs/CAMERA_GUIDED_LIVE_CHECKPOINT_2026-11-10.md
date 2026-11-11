# CPC Camera v0.7 — guided sequence and live analysis checkpoint
Date: 2026-11-10
Owner: Camera workstream, `feature/field-camera-pilot` (draft PR #3)
Preview: https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/

## Implemented
1. `web/camera/guided-capture.js`: deterministic capture order; overview frame first; coarse edge-density candidate regions; normalized manual target box coordinates and geometry helpers.
2. `web/camera/index.html`: added **Distance view** mode, tap-to-select target on captured overview, selected-monument highlighting, manual target rectangle width/height, Next guided photograph, skip-with-reason and monument group ID persisted per photograph. Subsequent shots: full front, inscription, carving, side, back. Captures retain original full camera frames and separately generated derivatives.
3. `web/camera/live-analysis.js`: lightweight local image analysis; candidate horizontal text-like bands, brightness/contrast/glare statistics, non-diagnostic image advice, and adaptive brightness/contrast settings.
4. `web/camera/discovery.js`: during the **active** camera view, continuously sample frames on-device, display possible monument rectangles in overview mode (mint), text-like regions (blue), persistent carving/surface detail proposals (gold). Toggle each separately. Preview-only brightness/contrast auto-enhancement is on by default, without changing captured originals or the exported original image. Fixed live manual symbol-mark pointer-events gating.
5. `web/camera/sw.js`: cache version `cpc-field-camera-0.7.0` includes `guided-capture.js` and `live-analysis.js`.
6. `tests/test_guided_capture.js` and `tests/test_camera_live_analysis.js` added to CI workflow; CI completion not confirmed.

## Verification
- All updated JavaScript sources and inline camera JS parsed successfully in the available JS runtime.
- Executed nine direct assertions against the analysis module, covering dark and bright synthetic frames, absence of fabricated text regions, input validation, active-mode controls, and preservation of source camera pixels.
- Guided state/geometry exercised in JS tool runtime; one initially failing letterbox test was a mistaken coordinate choice, corrected in the committed regression source. Node/GitHub CI execution remains unverified.
- Cloudflare preview Worker update returned success and source readback confirmed guided controls, live module, text-like highlighting, original/photo exports, and new offline cache.
- No real device, GPS or iPhone Safari camera/ZIP test performed, and no production Worker/database changes.

## Important truth and safety boundaries
- All detections are **visual proposals**, not validated classification of gravestones, lettering, symbols, specific materials, quarries or carvers. The user taps the actual stone; the system does not auto-assign an identity.
- Contrast enhancement is display-only, applied to video via CSS filter; full-frame captured originals are not enhanced or overwritten.
- Experimental proposals can be misleading in vegetation, fences, other stones, shadows or reflective materials. Manual selection always available.
- Selection is attached to photographed overview and grouped subsequent photos, not a GPS plot survey.
- Material contradiction engine is deferred: user reprioritized this camera session to overview selection and live visual proposals.

## Next gates
1. Physical Safari video + GPS test, especially landscape orientation and UI touch targets.
2. Review actual candidate shapes and text-like lines on varied grave markers; tune thresholds / add proper annotated model only after collecting rights-cleared photographs.
3. Test whether the manual overview selection stays aligned with a real photo when portrait/landscape changes.
4. Test next-step and skip-reason persistence across app restarts and ensure each archived record has a clear group ID.
5. Inspect actual v0.7 private/shareable ZIPs for raw metadata and coordinate leaks before any release.
6. Keep camera PR draft; share this checkpoint with main integration workstream rather than changing `main`.
