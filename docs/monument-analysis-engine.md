# Monument analysis engine — evidence model v0.1

This is the **data and research foundation**, not a claim that AI inference is already running in the camera. Do not display tentative interpretations as facts.

## Workflow after a camera capture
1. Preserve the source photo unaltered and attach GPS observation + accuracy; link derivatives.
2. Detect or manually trace the silhouette; record crest, shoulders, edges, finials, proportions and dimensions **only if measured or calibrated**.
3. Inspect material features (grain, foliation, bedding, crystals, fossils, weathering). Classify likely material with competing alternatives; never infer a quarry solely from color.
4. Detect and label motifs, separating **visual observation** from historical interpretation. Multiple meanings by region, community and time may coexist.
5. Extract inscription transcription with uncertain spans; record lettering geometry, distinctive letters and punctuation **independently** of the inscription text.
6. Characterize carved relief and tool marks; avoid fictional inferences about hand tools from compressed imagery.
7. Compare against **documented** stones and signed examples; rank silhouette, lettering, relief, borders, motif construction, material, chronology and geographic plausibility.
8. Store alternative carver/workshop candidates with supporting and contradictory evidence; route for human review. A maker's name should be considered documented only with appropriate primary or scholarly evidence.
9. Estimate geological provenance only with regional geology, known quarry history, transport routes and, where available, authorized scientific tests; photograph-only quarry claims remain hypothetical.

## Data model
- `marker_form_observations`: shape and geometric observations.
- `carving_feature_observations`: artistic execution and signatures.
- `lettering_style_observations`: comparative 'carver handwriting', including distinctive glyphs.
- `motif_interpretations`: observed symbol vs cited meaning.
- `carver_attribution_candidates`: reviewer-controlled attributions with alternatives.
- `marker_similarity_evidence`: explicit pairwise observations; **a numeric match is not proof**.
- Existing `stone_observations`, `stone_material_candidates`, `material_provenance_hypotheses` (migration 0003) handle geology.

## Evidence standards
- Documented source / signed marker > archival linkage > consistent close stylistic comparison > broad iconographic resemblance.
- Distinguish carver, lettering specialist, workshop, apprentice, and shared pattern book.
- Negative evidence and damaged surfaces are important; do not invent invisible tool marks or letters.
- Preserve source IDs, image IDs, reviewer, and uncertainty for each observation.

## Starter references (interpretation is always geographically and historically contingent)
- Boston city government, *Iconography of Gravestones at Burying Grounds*: https://www.boston.gov/departments/parks-and-recreation/iconography-gravestones-burying-grounds
- Association for Gravestone Studies, *Identifying Major Stone Types*: https://www.gravestonestudies.org/component/content/article/88-preservationconservation/100-preservation-and-conservation-2
- US National Park Service, *Materials and Monuments*: https://www.nps.gov/articles/000/cemetery-preservation-course-materials-and-monuments.htm
- Connecticut State Historic Preservation Office cemetery research bibliography: https://portal.ct.gov/-/media/DECD/Historic-Preservation/01_Programs_Services/Hurricane-Sandy/Cemeteries/RESEARCHING-CONNECTICUT-CEMETERIESFINAL_APRIL2019.pdf

## Next engineering slices
- Add image region annotations to capture front/back/detail photo evidence for each observation.
- Implement on-device image region proposal with trace/edit controls, initially manual review.
- Run OCR/vision inference only with permission; persist raw candidate labels and error states separately.
- Train/test stone style matching against signed and reliably attributed records, report false-match rates.
- Add D1/R2 bindings only after access control and photo-publication policy is implemented.
