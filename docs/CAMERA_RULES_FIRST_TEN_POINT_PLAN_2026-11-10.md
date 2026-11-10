# CPC camera: rules-first field model — ten-point implementation plan

Date: 2026-11-10
Owner: Camera development workstream, feature/field-camera-pilot (draft PR #3)
Status: Implementation plan, not a claim these ten features are finished.
Goal: Make the camera guide documentation, capture reliable evidence, and deliver private/shareable records. Prefer deterministic algorithms and rules; call AI only as explicitly requested for unresolved ambiguity, with provenance and human review.

## Governing architecture
Inputs: camera frames, capture metadata, GPS with radius and age, cemetery polygons/points and site relations, reviewed markers and reference catalogs, user-entered observations.
Deterministic core: local image quality measures, capture state machine, GPS accuracy/containment resolver, contours and landmarks, image registration, OCR when available and independently validated, motif lookup, decision rules, contradiction engine, evidence serialization and export privacy checks.
Decision escalation: if conflicting signals cannot be resolved by better photos or explicit rules, offer user choices or optional AI-assisted *candidate* interpretation. AI never manufactures source facts or silently overwrites evidence. Camera can function with AI disabled and without network.

## Ten steps and acceptance
1. **One-monument session and state machine** (partially implemented: group ID). Add session roles `overview → select monument → front → inscription → crest/motifs → side/back/base/signature as needed → review → export`, resume/offline support, per-image `shot_type`, completion checklist and skip-with-reason. Acceptance: photos from one session never silently merge with a neighbor's monument.
2. **Overview camera and target selection** (not implemented). Prompt `Step back; include multiple markers and an identifying landmark`, capture wide frame, propose boxes around upright stone-like regions using conventional geometry/edges and optional on-device object detection model; no claim of semantic recognition. Tap one box or draw a rectangle manually; store crop/coordinate in the overview reference without modifying the original. Acceptance: selection also works with auto-proposals turned off.
3. **GPS cemetery / complex / sub-ground resolution** (code present, data incomplete). Run GPS candidate/accuracy/age checks against verified polygons and named/combined-ground relation graph; parent complexes and adjacent independent cemeteries are distinct. Never resolve to individual burial plot from phone accuracy alone. Acceptance: ambiguous GPS produces a list and `not confirmed`, never fabricated precise location.
4. **Real-time photo quality advisor** (not implemented). Local per-frame blur/focus score, glare/saturation, luminance and contrast, framing/occlusion, horizon/perspective and camera-motion checks using JS Canvas/OpenCV/WASM where available; adaptive thresholds calibrated against device types and material. Offer immediate actionable instruction; never discard originals or refuse needed evidence. Acceptance: tests include dark stones, glossy zinc, direct sun, trees and eroded inscriptions.
5. **Multi-view capture directions** (partially implemented shot modes). Ask for front/full shape, inscription, sculpture/symbol detail, side/back, base/foundry mark, and contextual photos. Only ask when needed based on seen evidence; if candidate cast zinc, specifically ask for joints, seams and foundry labels. Show required/optional/rejected/missing states. Acceptance: users can complete records when a back side is inaccessible and log the reason.
6. **Silhouette extraction and correction** (experimental heuristic + manual multipoint tracing present). Separate complete visible outline from clipped, damaged, vegetated and buried boundaries; correct arches/shoulders/finials with draggable points and stored mask provenance. Run proposal only when plausible; otherwise request manual selection. Acceptance: real held-out masks measured via IoU/boundary metrics; no contour claimed correct without review.
7. **Materials + historic craft classifier** (not yet in capture options). Introduce top-level `stone, cast metal, other manufactured, uncertain`; subtypes slate, schist, phyllite, granite, marble, sandstone, limestone, zinc/white bronze, cast iron, bronze etc. Compare textures, grain, seams, lettering relief, weathering and map context as independent evidence. Nearby bedrock NEVER proves quarry/material. Acceptance: records support multiple competing hypotheses and citations.
8. **Inscription, motif and maker evidence** (motif manual catalog present; automated identification not implemented). Image alignment, separate high-contrast derivative and OCR hypotheses with line-wise confidence; structured symbol feature annotations linked to the scanned guide and signed stone reference corpus; lettering/ornament features support workshop *candidates*, not maker facts. Acceptance: missing or worn letters stay uncertain; source-linked interpretations preserved.
9. **Contradiction / clarification engine** (not implemented). Rules compare names/dates from several views, material clues (e.g., apparent slate vs cast zinc), site identity, repeated markers, and candidate makers. Present concise reasons, exact conflicting claims, and one focused next-photo or clarification prompt. Keep all original claims and user decisions, never silently reconcile. Acceptance: synthetic contradictory cases lead to auditable warnings and safe `unresolved` status, no AI necessary.
10. **Evidence export, testing, integration** (v0.6 code present; device QA incomplete). Separate private archive (original pixels, GPS, analysis, full source provenance, integrity manifest) and reviewed shareable record (new public ID, redacted location, approved and metadata-free re-encoded image). Add actual ZIP/EXIF round-trip tests in CI, field test iPhone Safari, offline tests, coordinate leak audit and secure backend integration only after D1 migration/review and server authorization. Acceptance: two real ZIPs pass privacy and integrity checks, and zero private data reaches public sharing without explicit authorization.

## Implementation sequence
Release A: steps 1, 2, 4, 5 (minimum useful guided field capture, still works without auto-recognition).
Release B: steps 3, 6, 7 (GPS/site confidence, silhouette quality, material alternatives).
Release C: steps 8, 9, 10 (evidence comparison, contradiction prompts, end-to-end verified exports).

## Status observed from camera source this session
Present: GPS candidate panel and cemetery relationships, front/back/side/inscription/carving modes, field group IDs, experimental silhouette suggestion, full contour manual tracing, two export actions.
Not established in code: wide overview monument candidate picker, zinc/white bronze selector, blur/glare quality scoring, rules-based contradictions. Automatic semantics and quality thresholds are not certified.
Known blocker: phone-based test of v0.6 ZIP, EXIF scrub and private/public export. Do not merge to production until validated.

## Cross-workstream contracts
- Camera owns `web/camera`, field UX, capture state, local QA, annotations and export package construction.
- LOC/CEM owns validated site geography, complex membership, date-specific cemetery relationships. No invented boundaries or plot GPS.
- GEO owns materials/bedrock/quarry hypothesis data. Ground beneath cemetery is contextual only.
- ICO/CAR/HIS owns source-linked meaning, signed maker corpus, style and citations.
- Main integration owns shared D1/R2 permissions, migration numbering, public upload acceptance and final merge.
- Share progress via committed `docs/CAMERA_RULES_FIRST_IMPLEMENTATION_CHECKPOINT.md` and draft PR #3. GitHub is the canonical cross-conversation source; Drive may mirror. Chats do not message each other automatically.
