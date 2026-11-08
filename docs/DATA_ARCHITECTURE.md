# Cemetery Picnic Club — Connected Data and iPhone Capture v0.1

## Principle
Use one relational database with eight research areas and a shared evidence layer, not eight unrelated databases. This document is a proposal, not a deployed service.

## Research areas and records
- Historical: persons, names, dates, inscriptions, archival sources, biographies and events.
- Scientific: imagery analysis, transcription candidates, measurements, condition observations, uncertainty.
- Geological: lithology, geology maps, materials, quarries, provenance hypotheses.
- Craftsmanship: carvers, workshops, motifs, lettering, style, tool marks, attributions.
- Care: material-appropriate conservation guidance, condition, approved interventions and product guidance.
- Stewardship: commissions, member follows, approved volunteer projects and community gatherings.
- Family: sourced parent-child, spouse and other genealogical claims.
- Geography: cemeteries, sections, plots, marker coordinates, historical places, quarry and workshop locations.
- Evidence: sources, citations, claims, confidence, competing interpretations, reviewers, copyrights and revisions.

## Identity rules
Distinguish physical marker, burial, person and memorial. One marker may commemorate several people; a person may have multiple memorials; no marker automatically proves an interment.
Every important historical assertion is a cited claim, not an unsourced field. Every inferred relationship needs evidence and a confidence level.

## Suggested first SQL tables
cemeteries, markers, marker_locations, persons, marker_person_links, inscriptions, images, image_rights, sources, claims, external_references, condition_observations, sync_jobs.
Add burial, memorial, carver, workshop, motif, quarry, material, genealogy, care and membership tables when the first real datasets justify them.

## Important fields
- Marker: id, cemetery_id, section/plot, physical description, rough date, state.
- Image: id, marker_id, object_key, original_sha256, photographer, rights basis, usage scope, capture time, source link, review state.
- Location: latitude, longitude, accuracy meters, collection method, privacy precision, observation time.
- Inscription: literal transcription, uncertain character spans, review status, image region.
- Claim: subject, predicate, proposed value or target, evidence IDs, confidence, author, review status, competing assertion.
- Person: name variants, date range, sources, visibility and privacy state.
- Condition: observation time, description, photos, observer; treatment is a separate authorized action.

## iPhone field capture
Required: photograph and selected cemetery/marker; optional: wide context, close detail, raking-light angles, GPS (with accuracy and user permission), orientation where supported, notes and corrected inscription.
Preserve the original image; put OCR, crops, sharpened renditions, interpretations and annotations in distinct derivatives. Allow edits before publication.
Build an installable mobile-first PWA with camera input, geolocation, IndexedDB offline drafts, explicit upload queue/retries, HTTPS API and cloud photo storage.
Do not assume background synchronization reliably runs on iOS. Test permissions on physical iPhones. LiDAR is optional on compatible devices and may require a later native ARKit implementation; ordinary browser camera capture is the baseline.

## Proposed Cloudflare stack
- Workers with static assets for the app and API.
- D1 relational records for MVP.
- R2 for image originals and authorized derivatives.
- Queues for eventual OCR/image processing when necessary.
- Similarity/vector search is a later extension, not an initial requirement.
Nothing here represents provisioning or deployment.

## Image and sourcing rules
Link Find a Grave memorial IDs as external references. Do not systematically copy data or reuse photographs without necessary authorization. Prefer permitted volunteer photographs, cemetery ledgers, public archival records, geological surveys, published carver studies and authorized exports.
Material and carver recognition should remain tentative until corroborated. Show uncertain readings and record corrections. Store permission and copyright scope for each photo.

## Conservation and privacy
Record care observations separately from permitted work. No automatically authorized cleaning, chemicals, rubbing or repairs. Cemetery authority and preservation guidance determine interventions. Members may follow stones, not claim legal custody. Family messaging is opt-in and recent burial data has stronger privacy controls.

## Implementation order
1. D1 MVP schema and local migrations.
2. One cemetery and 30–50 properly sourced or synthetic test records.
3. iPhone camera form, GPS with accuracy, draft and offline queue.
4. Inscription review and historical candidate matching with sources.
5. Motif, maker, stone, geology and family relationship navigation.
6. Care, commissions, volunteer tasks, optional product guidance and social events.
