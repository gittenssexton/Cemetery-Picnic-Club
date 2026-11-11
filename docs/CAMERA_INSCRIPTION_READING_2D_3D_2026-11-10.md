# CPC Camera — inscription reading priority: 2D and 3D
Date: 2026-11-10
Status: v0.9.8 exploratory 2D reading and planar orientation handling deployed to field preview. Genuine 3D relief reading NOT yet implemented.
Product scope: gravestones and engraved monument surfaces photographed outdoors.

## Required behavior
- The operator taps the stone or inscription to direct investigation.
- Retain the original full-resolution photo and its metadata.
- Persist user-reviewed readings separately from machine candidates. Never infer a person's identity from a low-confidence reading.
- Inscriptions and relief are the primary goal, not just drawing contours.

## What v0.9.8 actually provides
1. `inscription-reader.js` with deterministic 5×7 templates for A-Z and 0-9, grayscale and Otsu threshold, polarity search, rows/columns segmentation and candidate glyph matching. Only accepted when score >=.86 and margin >=.035; uncertain shapes are '?'.
2. Two review buttons: **Attempt 2D reading** on selected monument bounds and **Read straightened stone face** using an assumed four-corner planar face. The latter uses `reading-geometry.js` projective correction and is **not** a measured 3D model or engraving depth.
3. Store bounded `reading_attempts` locally with source method, timestamp, candidate scores, unverified status. Do not overwrite `monument`, `notes`, `originalBlob` or user attribution.
4. A blank low-contrast synthetic image produces no guessed transcription. Synthetic pixel-font 'STONE' reads as 'STONE'.
5. Source scripts and photo review handlers parse and are deployed with offline cache v0.9.8. No real gravestone reading accuracy validated.

## First production-scale 2D reading pathway
- Crop to a polygon or inscription row selected by user; preserve original and source coordinates.
- Improve segmentation for actual gravestone incisions and serif fonts: adaptive threshold/local contrast, text baselines, connected-letter separation, broken glyph joins, edge topology, depth-related shadow gradients.
- Support multiline inscriptions, dates, ligatures, varying typefaces, reversed strokes, broken/weathered letters.
- Create a manually reviewable transcript with character-level alternatives, unknown markers, source crops, scores, and editable corrections.
- Compare against cemetery vital/burial registries only *after* reliable textual candidates; keep source/provenance.
- Field benchmark with consented reference images: measure character error rate, word error rate, percent correctly abstained, mistaken identity rate, drift, processing time.

## 3D / relief-reading pathway (not yet done)
- Record several still photos of the same stone face from distinct, safe viewpoints, using a shared monument group ID and per-image orientation/GPS only where appropriate.
- Establish verified visual correspondences across images; estimate camera pose/perspective geometry with calibrated camera parameters (if available).
- Use geometry to align and compare persistent grooves versus moving sunlight/tree shadows. Differential photometric/reflectance analysis may help where illumination changes and images are well registered.
- Where native phone hardware and permissions allow, use device depth/LiDAR only for macro stone-face plane estimation and tracking, not for millimeter-scale inscription groove reading. A web-only preview cannot assume ARKit LiDAR access.
- Do not interpret shading as depth in a single photograph. Treat estimated relief as provisional with uncertainty.
- Derive 2D character candidates from several aligned views and retain disagreements; don't synthesize missing letters.

## Outdoor requirements
- Diffuse, raking and dappled light all have distinct value; contrast processing must preserve original shading evidence.
- Lichen, algae, rust, moss, mildew, darkened marble and natural stone color are potential obstructions, not identified organisms from color alone.
- Never suggest cleaning, rubbing, chalking or otherwise altering historic markers.

## Go/no-go for actual field recognition
- User can focus on one inscription area and see proposed characters with uncertainty, then confirm or correct them.
- Real-stone tests demonstrate useful accuracy across slate, marble, granite, limestone and sandstone under variable light.
- 3D-based assertions require verified multi-view or measured depth evidence; perspective rectification alone does not qualify.
