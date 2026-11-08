# Cemetery Picnic Club

**Discover the stories. Understand the stones. Care for the places.**

Cemetery Picnic Club is a public-history discovery app and a community stewardship movement. It helps people document grave markers, explore the lives and families they commemorate, study the people and materials that made them, and support respectful care of burial grounds.

## The connected historical record

Every record is evidence-backed and may link to other records:

- **Burial place and grave marker:** cemetery, plot/location, photographs, inscriptions, condition and dated observations.
- **Person and family:** biographical information, relationships, historical records and associated markers.
- **Stone and material:** lithology, visual characteristics, possible quarry or source region.
- **Maker:** identified or proposed stonecarver, workshop, tools, carving techniques and stylistic comparisons.
- **Art and symbolism:** designs, faces, motifs, scripts, iconography and regional or chronological traditions.
- **Stewardship:** documented observations, permission-aware conservation guidance and volunteer opportunities.

**Important:** A grave marker, a burial, a person and a photograph are different objects; they must never be assumed to be one-to-one. A person may have multiple memorials, and a marker may commemorate several people.

## First visitor experience

1. Explore a cemetery on a map, or photograph a marker with permission and respectful conduct.
2. Capture the inscription and artwork through image analysis, retaining original photos.
3. Review possible name, dates, materials, iconography and maker, each with confidence and cited evidence.
4. Browse connections to family members, nearby memorials, comparable carvings, workshops and possible stone sources.
5. Submit corrections and condition observations for review.
6. Learn how to support cemetery stewardship through the appropriate owner or authority.

## Evidence policy

- Store source attribution, date, contributor, confidence level and review status for each claim.
- Distinguish **documented**, **strongly supported**, **tentative** and **unknown** conclusions.
- OCR/AI transcription and carver/quarry attribution are proposals until reviewed, not established facts.
- Preserve original images; store enhanced crops, transcriptions and interpretations separately.
- Support competing readings and hypotheses rather than overwriting historical uncertainty.
- Never infer identity, genealogy or provenance solely from visual similarity.

## Care, privacy and access

- Respect cemetery rules, religious practices, family wishes and applicable law.
- Do not encourage rubbing, chalking, chemicals, scraping, repairs or cleaning without qualified guidance and authorization.
- Keep sensitive recent-burial details and family contact information private by default; use opt-in messaging.
- Provide a process to request corrections, removal of sensitive content and access restrictions.
- Avoid exposing exact coordinates of vulnerable or sensitive sites when this might create harm.
- Design for accessible exploration, including people who cannot visit in person.

## Suggested technical architecture

- **Web app:** mobile-first progressive web app (PWA), map and camera workflow.
- **API:** Cloudflare Workers.
- **Structured records:** Cloudflare D1 (SQLite) or equivalent relational database.
- **Media:** Cloudflare R2 or equivalent object storage, with original-image retention.
- **Processing:** asynchronous queues for image analysis, transcription, similarity and moderation.
- **Search:** geographic, names, dates, iconography, stone type, carver and quarry.
- **Graph relationships:** versioned typed links between entities, with citations and confidence; begin in a relational schema before considering a specialized graph system.

This is an architecture proposal, not a statement that these services are provisioned.

## Delivery phases

1. **Foundation:** landing page, mission, design system, privacy and evidence policies, schema.
2. **Field catalog:** camera upload, geolocation, marker records, transcription review.
3. **Historical intelligence:** iconographic classification, stone material and carver hypotheses, evidence comparison.
4. **Connected histories:** genealogical source links, maker networks, quarry networks and cemetery exploration.
5. **Community care:** opt-in stewardship, condition reports, approved volunteer activities and local partnerships.

## Project locations

- GitHub: https://github.com/gittenssexton/Cemetery-Picnic-Club
- Google Drive: https://drive.google.com/drive/folders/10kQDrxfn097oa4XRGe7_ee44zR9bJ2OW
- Cloudflare Worker (provided deployment address; current operational status not verified): https://cemeterypicnicclub.gittens-sexton.workers.dev/

## Status

Initial project charter. No app features or production infrastructure are claimed to be implemented by this document.
