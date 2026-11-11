# Cemetery Iconography Reference and Recognition Contract — 2026-11-11
Status: v0.9.9 field-preview integration. Do not treat source-derived meanings as verified identifications.

## Primary source examined
User-supplied nine-page photographic scan, `Scan Nov 8, 2026 at 7.00 PM.pdf`, Drive file ID `1TDwejroxzYUY2-C8hzGaoHa9FCxtMUMo`.
The PDF is image-only: review of rendered pages 3–7 is required. Printed page 10 appears on PDF page 7.
Page 7 Geometric and Ornamental illustrations: Pinwheel, Rosette, Scallops, Diamonds, Stars, Scrolls. Monuments and Architecture: Urn, Broken Column, Obelisk.
Page 3/4: Time, Faith and the Afterlife motifs, including Scythe, Hourglass, Winged Hourglass, Inverted Torch, Crown, Book/Bible, Hand Pointing Upward, Clasped Hands, Lamb.
Page 5: Vines, Ivy, Leaves, Branches, Palm Branches, Wheat, Oak Leaves and Acorns, Weeping Willow, Tree of Life, Broken/Cut Tree.
Page 6: Anchor, Heart, Gate/Door, Flowers, Flower cut by Scythe, Rose, Rosebud, Fleur-de-lis, Grapes.
Pages 8–9 are research resources, not symbol illustration templates.

## Guide interpretation constraints
Source says a pinwheel can represent motion, eternity or the sun but may be ornament alone. Rosette is described with sun, life and renewal. Scallops/diamonds are chiefly ornamental. Urn is associated with mourning/remembrance and commonly paired with willow. These are historical guide descriptions, NOT proof of a maker's intent on a particular monument.
Do not conflate a circle with an identified pinwheel. Do not conflate a circular radial pattern with verified iconography or a person's identity.

## Code added
`web/camera/iconography.js` includes 37 source-grounded entries with pattern morphology text, group, source Drive ID and scanned PDF page number.
`CPCIconography.classifyCircularRegion()` tests observed circular candidate regions for spatial angular structure and a possible winding/straight-radial family. When evidence is insufficient, it abstains. If evidence exists, it gives unverified pinwheel/rosette alternatives, not a confirmed symbol.
Live camera integration operates on tracked possible circular surface-feature regions, not on a global free-floating icon detector. It reports candidate counts and guide source in `liveIconographyStatus` and stores provisional proposals in camera evidence snapshots.
Existing manual `Mark a symbol` review catalog remains available for the broader 37 motifs; all other guide entries are indexed visually/descriptively but do NOT yet have automated image classifiers.
`tests/test_camera_iconography.js` includes reference-category coverage, blank-image abstention, synthetic winding versus straight radial tests. The synthetic test passed in the connector JavaScript runtime; actual CI completion and real historical marker accuracy remain unverified.
Offline camera SW v0.9.9 and Cloudflare preview worker deployed; published source readback checked.

## Next work
1. Add photographed guide icon templates through a restricted rights-aware research corpus rather than copying copyrighted scan artwork into the public app.
2. Add actual-stone crops of manually confirmed rosettes, pinwheels, urns, scrolls and flowers with citation and counterexamples. Include mimics: lichen patches, fractures, tree shadows and painted areas.
3. Benchmark confusion matrix, false positives, abstention accuracy, geometric shape stability and device runtime against real photos. Do not call radial source candidates recognized before field validation.
4. Expand geometric detectors for scallop chains, diamond chains, pointed stars and scroll-spirals; urns require vessel/lid/foot geometry and contextual panel evidence.
5. Link each image-pattern hypothesis to a searchable motif record and its documented source page without automatically asserting any historical meaning.

Source remains in user Drive; photo/guide bytes are not replicated in the public GitHub branch.