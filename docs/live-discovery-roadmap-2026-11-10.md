# Live Discovery development roadmap — 2026-11-10

## Built and available in the separate preview Worker
- Camera access, GPS permission and accuracy, photograph and derivative capture, original/full-frame photo ZIP export.
- Four-point manual stone isolation and enhanced reading derivative.
- Illustrated cemetery-symbol reference list, user-positioned meaning annotations exported into record.json.
- **v0.4**: on-device candidate region stability: edge-density features at 160x200 every 1200 ms; 2-scan persistence threshold; exponential center smoothing (0.72 previous/0.28 new); maximum 2 missed scans and 3 display circles. **These are NOT motif or monument detections.**
- This code lives on the feature branch and a separate preview Cloudflare Worker. No D1/R2 production rollout.

## Highest-value engineering sequence
1. **Real monument segmentation**. Collect varied annotated photographs (not just one stone) including slate tablets, marble, dark granite, rounded tops, shoulders and irregular silhouettes; trace actual polygon masks. Add silhouette proposals with user correction and confidence. Compare mask quality on held-out stones (IoU and edge error), check foliage/neighbors.
2. **Symbol and motif bounding boxes**. Use licensed/own source photos and the supplied Nov. 8 scanned symbol guide as text/interpretation seeds. A scanned illustration is a reference, not proof that a model recognizes a weathered real carving. Crop and label images: skull/wings/cherub/urn/willow/rosette/hourglass/etc with independent reviewer. Evaluate precision, recall, abstention and false positives on previously unseen grave markers.
3. **Inscriptions and lettering**. Separate text recognition from letterform style embeddings (serifs, relative width, spacing, terminals, capital shape, punctuation and line layout). Preserve uncertain readings; use several photos rather than hallucinating eroded glyphs.
4. **Carver/workshop similarity**. Compare geometry, carving and lettering with signed and documented reference stones, then validate against documented reference sets. Unknown style must remain a legitimate result. Avoid assuming a stylistic match identifies an individual.
5. **Material and provenance**. Integrate visual texture/layering and material candidate data from 0003 with quarry catalogs and geological maps. Photo appearance cannot confirm a quarry. Publish alternative hypotheses and source links.
6. **Secure persistence**. D1 for marker, person, inscription, claim and image metadata; R2 for originals and derivatives; authentication and owner-consent policies before any community photo upload.
7. **Field UX**. Adjustable sampling / battery mode, stable/paused overlays, tap-to-inspect with provenance, offline fallback, a field-test checklist and device performance metrics.

## Field test prerequisites and acceptance checks
- iPhone Safari camera prompt, location prompt, GPS accuracy and fresh timestamp visible.
- Yellow regions persist across successive frames when the phone stays still; do not claim semantic identification.
- User can mark motif using the symbol guide; source document/page retained.
- Full frame ZIP, all processed copies and record.json, EXIF GPS on geotagged JPEG.
- Switch camera on/off, leave/reenter page, interrupt camera, and test disabled GPS.
- Test on multiple real stones with competing background objects (grass/trees/other stones) and varied lighting.
- Compare original image pixels against geotagged JPEG image pixels.

## Research handling
The illustrative symbol guide belongs to the user's collection; cite it as `Scan Nov 8, 2026 at 7.00 PM.pdf`, pages 3–7, in interpretations. Symbols can have multiple meanings conditioned by culture, place, period and whether they are purely decorative. Preserve all unmodified originals; do not fill missing lettering or source facts.

## Release protection
Never silently replace `cemetery-picnic-club` or `cemeterypicnicclub` Cloudflare Workers. Use `cemetery-picnic-camera-preview` for experimental build. Keep PR as draft until tested and reviewed.
