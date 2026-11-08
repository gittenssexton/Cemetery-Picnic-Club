# Cemetery Picnic Club — Single-Cemetery Pilot

Status: pilot design; no cemetery selected, memorial imported, image copied, or partnership confirmed.

## Primary outcome

Deliver an unusually capable gravestone identifier and research connector before adding the community and commerce layers.

## First cemetery acceptance criteria

- Permission and practical access for photography and field documentation.
- Identifiable cemetery authority or commission contact.
- A manageable test cohort (suggested 30–50 markers) spanning different periods, materials and conservation states.
- Existing grave records available through permission, open records or volunteer-owned exports.
- At least a few potentially related families, motifs or carving workshops for testing connections.
- Willing volunteers and a review workflow.

## Research data pipeline

1. Record cemetery identity, boundary, responsible authority, access rules and public contact.
2. Record any Find a Grave cemetery URL and memorial IDs as outbound references (not a bulk scrape).
3. Obtain original photographs, licensed images, or explicit contributor permissions; retain source, photographer, license/permission date and original image hashes.
4. Collect public cemetery ledgers and other permitted primary-source records.
5. Create distinct entries for marker, grave/burial, person, image, maker, workshop, material, quarry, location, claim, citation and care observation.
6. Generate tentative AI readings or visual comparisons only on images that may be used for this purpose.
7. Human-review transcriptions, names, dates and attributed connections.
8. Publish with evidence/confidence labels, revision history and correction requests.

## Find a Grave and reuse

Ancestry terms (which include Find a Grave) limit copying, systematic gathering, republishing, and use of content for AI model development or training. Do not automate extraction or use Find a Grave content for AI training absent appropriate written authorization. Find a Grave advises direct permission from contributors for photos. A user can export the contributions they themselves added to a cemetery through Account Settings > Data and Privacy.

References:
- https://www.ancestry.com/c/legal/termsandconditions-en
- https://www.ancestry.com/c/legal/community-guidelines-en
- https://support.findagrave.com/hc/en-us/articles/53933391181843-Questions-about-Photos
- https://support.findagrave.com/hc/en-us/articles/53933374591891-Questions-about-Cemeteries

## Initial record fields

### Cemetery
id, official_name, alternate_names, region, approximate_boundary, governing_body, authority_contact_public, visiting_rules, permissions, findagrave_url

### Marker
id, cemetery_id, plot_id, geo_location, stone_type_hypothesis, condition, inscription_literal, inscription_reviewed, period_estimate, motif_tags, original_photos, visibility_status

### Person
id, names_and_variants, date_ranges, biography, privacy_status

### Link
id, subject_type/id, predicate, object_type/id, evidence_refs, confidence, reviewer, updated_at

### Image
id, marker_id, object_key, photographer, copyright_owner, rights_basis, permission_reference, captured_at, published_at, hash, analysis_allowed

### Historical claim
id, subject, claim_type, claim_value, evidence_refs, confidence, reviewer, contested_status, correction_history

### Stewardship report
id, marker_id, observed_at, visible_condition, photos, proposed_action, authority_approval_status, reviewer

## Identification UX v1

Camera / upload -> detect marker -> propose inscription transcription -> permit user correction -> compare within selected cemetery -> return candidate match(es) and reasons -> view historical record and verified links -> submit field observation.

Uncertain output is never silently converted into a fact. No image recognition model is trained on external platform images without authorization.

## Phase order

1. Working identification, transcription and record matching in one cemetery.
2. Material/iconography/carver hypotheses and genealogy-source connections.
3. Evidence-quality reviewer tools; public discovery map.
4. Cemetery commissions and volunteer stewardship; approved maintenance documentation.
5. Optional product links and local gatherings, governed by separate care and event rules.

## Stewardship rules

- Members may follow a marker and record its condition without implying legal custody or care rights.
- Any physical cleaning or maintenance requires approval from the responsible cemetery authority and a material-specific safe method.
- No bleach, acids, wire brushes, pressure washing, stone rubbing, scraping, or undocumented repairs.
- Product recommendations must be tied to the type/condition of stone, trained guidance, and approval.
- Gatherings and meals occur only where allowed; religious activities, burials, visiting families and cultural customs take precedence.
- Family contact is opt-in only; no automatic outreach using personal data.

Conservation references:
- https://www.nps.gov/articles/000/cemetery-preservation-course-overview.htm
- https://home.nps.gov/articles/000/cemetery-preservation-course-cleaning-grave-markers.htm
