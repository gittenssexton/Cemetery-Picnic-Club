# Camera Real-Photo Pattern Casebook — 2026-11-10
Scope: 27 connected Drive images reviewed (8 original HEIC field views, 9 gravestone JPEGs, 10 directory/map JPEGs). No original bytes copied into this public repository. Inscription identities and materials remain unverified.

## Grouped test evidence
- IMG 5263–5266: Four photographs of the SAME memorial with raised or molded name/age panels and a lower verse. Cropped name appears DANIEL GOULDS, while older Drive documents variously say Daniel Combs or Goulds. Preserve as a conflict and do not automatically link person records. Born March 2, 1799 and Lived 85 years and retired to his rest visually supported. Death date not verified. Zinc white-bronze material plausible, not established.
- IMG 5267–5270: close views of lower base/side of this memorial. IMG 5269/5270 register well. Suspected base maker mark cannot be read with confidence. Horizontal patterns may be seams/tooling/weathering rather than geological bedding.
- IMG 5287–5289: adjacent, overlapping incised-script stones and variable pale surface growth. Need distinguish inscription strokes from ornament, adjoining stone boundaries and growth.
- IMG 5290: wide scene with grass and buildings; important negative case for non-monument contours.
- IMG 5291: very weathered scalloped stone, surface growth obscures inscriptions.
- IMG 5292–5293: alternate views of same dark rounded tablet, partially weathered lettering.
- IMG 5294: face-style carved top, side lozenge/diamond motif borders, weathered multilayer text.
- IMG 5295: second, distinct ornamented tablet with face, radial/fan carving, scrolls and faint text. Do not claim specific iconography without supporting evidence.
- Directory photos 01–04, 07–10: printed names and lot columns, glare and perspective. Keep as separate registry OCR task.
- Maps 05–06: St Paul and Pine Grove plot maps with veteran symbols. They do not provide a precise GPS location for the field memorial.

## Quantitative matching
At matched 750x1000 pixel scale, ORB+RANSAC registration of IMG 5263 against 5264, 5265, 5266 yielded 874/916 (95%), 864/901 (96%), 793/815 (97%) inliers, with median reprojection errors 0.92, 0.89, 1.05 pixels. This supports 2D plane registration, NOT measured 3D letter relief.
IMG 5269/5270: 468/491 matches retained as homography inliers (~95%), median 1.28 px. IMG 5267/5268 insufficient match confidence: only 5 inliers of 9 candidate correspondences.
libheif successfully decoded original HEIC. Older FFmpeg and ImageMagick paths initially produced incorrect black output and must not be used for quality scoring on this sample.

## Required future work
Build a real-stone benchmark distinguishing raised lettering, incised inscriptions, lichen/soil/grass false edges, unstable contours, illustrated symbols, and printed boards. Keep source photo and crop provenance. Measure character error rate and abstention rate. Do not call synthetic 5x7 STONE test real-gravestone accuracy.
Use 2D image alignment first, then acquire sufficiently separated views to test actual depth-aware carved-stroke inference. LiDAR by itself is too coarse to claim accurate shallow lettering relief.
Photo ownership/publication and third-party training rights are not documented; preserve private originals in the connected Drive and do not publish image bytes.