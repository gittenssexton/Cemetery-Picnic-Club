# Cemetery Picnic Club — GPS Cemetery and Combined Grounds Identification Handoff

**Prepared:** 2026-11-10  
**Status:** Engineering specification / evidence policy, not a deployed locator  
**Scope:** Global CPC core; initial field evaluation in Warren, Massachusetts and then New England  
**Domains:** LOC (geolocation), CEM (cemeteries, named grounds, sections), IMG (camera observations), HIS (sourced claims), with KIN/VIT only after separate identity review.

## 1. Goal

From camera GPS and map evidence, identify which cemetery or historically named burial ground a user is likely within; discover neighboring known cemeteries; handle several named cemeteries inside a combined complex, shared property, historic division or connected grounds. The engine must **never** silently collapse different cemetery identities, assign an exact plot from approximate GPS, or treat a nearest centroid as a surveyed boundary.

### Essential example
A site may be a single modern operational cemetery containing an older burial ground with its own historical name, or several distinct cemeteries sharing a driveway or a modern map label. The UI should display both the parent complex and the possible sub-ground, with independent citations and confidence. Multiple cemeteries next door remain separate even when their footprints touch; a shared name is not enough to merge them. The existing Pine Grove and St. Paul *map photos* are separate source maps; this project has NOT established they are physically joined or administratively combined.

## 2. Grounded project inputs (Drive/GitHub, 2026-11-10)

- Project dossier, `docs/PINE_GROVE_DOSSIER.md` on `main`: Pine Grove Cemetery, 207 Maple Street, Warren; approximate **site centroid** `42.20909, -72.19660`. This is explicitly **not** a marker position, ground polygon, or surveyed edge. The historic Founders section near Maple Street needs municipal verification. The dossier lists an unresolved acreage discrepancy (approximately 15 vs 25 acres).
- `02_Pine_Grove_Warren_Pilot/01_Cemetery_Records_Maps/02_Cemetery_Directory_and_Plot_Map_Photos`: photographs of **Pine Grove** and **St. Paul** plan drawings. The Pine Grove plan mentions **Forefathers Ground** in the map/geolocation evidence policy, but its geometry and administrative/historic status remain unverified. St. Paul anchors A–F are approximate **image coordinates**, not longitude/latitude.
- `03_Searchable_Cemetery_Database_2026-11-10/geolocation_evidence_policy.csv`: `SITE_UNCONFIRMED`, `SECTION_UNCONFIRMED`, `LOT_NUMBER_ONLY`, `ST_PAUl_MAP`, `PINE_GROVE_MAP`. No directory rows can be projected into a named cemetery without site corroboration; cemetery + section + lot is the minimum composite key when verified.
- `README_Database_Limits_and_Next_Steps.md` and `SESSION_PROGRESS_REPORT.md`: **322 provisional** directory entries from three partially read board photos, **0 verified** grave coordinates; names, lots and maps not automatically joined.
- User photo batches `IMG_5263–5270` and `IMG_5287–5295`: photographs are candidate monument evidence, NOT reliable cemetery assignments by filename alone. The Combs candidate's site remains unconfirmed.
- `docs/DOMAIN_INTEGRATION_HANDOFF_2026-11-10.md`: one global core with distinct CEM/LOC namespaces; feature-branch SQL migration number collisions are unresolved. Do **not** add an uncoordinated `0004` or deploy schema without checking actual D1 migration history.
- Illustrated guide `Scan Nov 8, 2026 at 7.00 PM.pdf`: contains a page on South Warren Cemetery, but this does not locate any photographed marker there.

These sources establish mapped **names and pilot documents**, not a trustworthy georeferenced national cemetery database.

## 3. Distinct identity concepts

| Concept | Definition | Example behavior |
| --- | --- | --- |
| `cemetery` | Administratively or historically recognized burial site | Own canonical ID, aliases, ownership and boundaries |
| `cemetery_complex` | Operational/physical grouping containing multiple sites or named grounds | Display parent plus children; do not overwrite child records |
| `historical_ground` | Named older ground, sometimes inside a larger cemetery | Preserve time scope and original name; relationship to parent can be disputed |
| `cemetery_section` | Section/area under a cemetery's authority | Scoped section and plot identifiers; no global section A |
| `burial_plot` | Specific plot reference and (if available) geometry | Cannot be resolved from GPS alone |
| `cemetery_alias` | Alternate or historic name of the SAME identified entity | Alias is not a second physical cemetery |
| `adjacent_cemetery` | Different cemetery with touching or nearby boundary | Separate records, optionally shared access |
| `shared_facility` | Common entrance, office, parking, road or management | Relationship only; not evidence of one cemetery |
| `cemetery_successor` | Site absorbed, renamed or administratively reorganized | Effective dates and documentary sources; historic records remain intact |

**Relationships** are typed, directional, independently cited, and effective-date aware: `part_of_complex`, `contains_historical_ground`, `administratively_managed_with`, `shares_entrance_with`, `adjacent_to`, `renamed_to`, `merged_into_at_date`, `overlaps_disputed_boundary`, `separate_from`, `possible_duplicate_of`. Never use one unconditional `same_as` edge for proximity alone.

A `combined` cemetery means an evidenced administrative or historic complex, **not** automatically two names close together. A user may need to choose among several member grounds within the complex.

## 4. Source hierarchy and coverage

Use **local authoritative geometry first**, with original source and map edition:

1. Municipality/cemetery commission GIS or surveyed parcel/section maps with explicit cemetery attribution, currentness, scale, georeferencing method and permissions.
2. State/local GIS cemetery site features or legal/planning records and dated preservation inventories.
3. OpenStreetMap cemetery `landuse=cemetery` / burial-ground polygons, religious/operational tags and relation memberships; preserve OSM attribution, ODbL obligations and freshness. Map features may be incomplete or misclassified.
4. Historical maps, burial registers, town histories, cemetery directories and image-plane plans; link to modern coordinates only after explicit georeferencing with control points and quality measurements.
5. Geocoded names/addresses or **approximate centroids** as discovery candidates only.

Possible future U.S. cemetery candidate sets include GNIS place names and state historic resource registries; assess current coverage, licensing, accuracy and availability before importing. No provider should be treated as universally complete. Start with an inventory of known sites plus `geometry_status`, not fabricated polygons.

Every geometry needs `source_id`, `feature_id`, `source_date`, `retrieved_at`, `geometry_type`, `geometry_status`, `accuracy_m`/error if defensible, coordinate reference system, and revision. Polygons with unverified boundaries must display as uncertain.

## 5. Location-matching algorithm

Input: `lat`, `lon` WGS84, `horizontal_accuracy_m` (from platform), `observed_at`, `fix_age_s`, `provider`, optional visual sign text / user-selected cemetery; optional prior GPS fixes. Never substitute the user location inferred from IP for device GPS.

**Step A: Validate GPS.** Check finite coordinates, valid ranges, permission and timestamps. Distinguish no permission, no fix, stale fix, low accuracy, and manually specified location. GPS accuracy is an estimated error radius, not proof the monument lies at the coordinate center.

**Step B: Gather candidate features.** Search all sourced cemetery polygons intersecting or within a configurable search radius around the *accuracy circle*; also gather nearby point-only cemetery centroids as discovery candidates. Include containment/complex/adjacency relationships and temporal aliases. Do not filter out a competing cemetery simply because its centroid is farther away.

**Step C: Evaluate geometry.** For each boundary, test: location point within polygon, minimum point-to-boundary distance, whether GPS accuracy circle intersects polygon, and whether several boundaries intersect that circle. Use a locally appropriate metric projection/geodesic distance; never compare raw degree differences as meters. Respect incomplete polygon provenance.

**Step D: Classify, don't overclaim.** Suggested statuses:
- `within_verified_boundary`: point inside a well-sourced boundary, GPS uncertainty sufficiently small relative to boundaries, no conflicting nearby site.
- `possible_within`: accuracy circle intersects site/complex or polygon itself is approximate.
- `multiple_candidates`: at least two distinct sites/grounds could contain the GPS circle, including members of a complex.
- `nearby_only`: only point features or distant site polygons; user may not be in any cemetery.
- `unknown`: no defensible candidates.
- `manually_selected_unverified`: user picked a name, not authoritative evidence of position.

**Step E: Show hierarchy.** Display `Complex › Cemetery › Historic ground › Section` when verified. When only a parent is known, show parent and `sub-ground uncertain`. When two overlapping candidates exist, show both and ask the user to confirm against entrance signage or a map. Never infer a person or burial plot during this decision.

**Step F: Confirm.** Prefer user confirmation, georeferenced entrance signage, municipal map/plot ledger or surveyed parcel boundaries. Persist observation and candidate list, not merely a string name. GPS points near roads or footpaths may require a repeat fix from within the site.

**Step G: Record provenance.** Store all candidates, reasons, geometry vintage, user override and future review history. A later better map must not silently change historical capture records; create a revised assignment linked to the original observation.

### Recommended decision rule for combined sites
If GPS lies inside a documented parent complex but intersects multiple child cemetery boundaries or no child geometry exists, return **parent complex + unresolved child**. If child footprint verified and accuracy circle falls safely within only one child, suggest that child. If polygons disagree, return `multiple_candidates` and log a mapping issue.

## 6. Proposed data model — integrate only after schema reconciliation

New/extended entities (names conceptual; adapt to existing D1 tables):

- `cemetery_entities`: existing `cemeteries` table as stable canonical sites plus `entity_kind`, operational state, date range, rights/review.
- `cemetery_names`: entity ID, variant, language, name status, valid-from/to, source, never merge by name alone.
- `cemetery_geometries`: entity ID, GeoJSON boundary/point, coordinate system, quality, source, date, validity, review. Store large polygon geometries as R2/GeoJSON with spatial lookup index as appropriate; not blindly as giant D1 JSON rows.
- `cemetery_relationships`: subject, predicate, object, from/to dates, confidence, source ID, reviewer. Prevent cycles of `part_of_complex` and avoid implicit transitive identity.
- `location_observations`: GPS values plus accuracy, timestamp, method, device measurement notes and privacy.
- `cemetery_match_candidates`: observation, candidate cemetery, geometry evidence, distances, reason codes, match status, rank, review state. Candidate scores are not calibrated probabilities unless tested.
- `cemetery_assignments`: observation/photo/marker, selected entity, assignment method (`survey`, `documentary`, `user_confirmed`, `gps_candidate`), verification state, source and reviewer. A GPS candidate must not be a `verified` assignment.
- `section_map_links`: named child section, source map, pixel-to-ground transform, residual error, source-lot key and uncertainty.

New cross-domain `CEM:cemetery:<id>` / `LOC:observation:<id>` references should conform to the nomenclature contract; preserve existing legacy IDs with a mapping table. Unknown/mixed ownership is valid and never silently defaulted.

## 7. Camera UX (iPhone first)

Top of live camera, just below GPS accuracy:

> **Possible site:** Pine Grove Cemetery · position estimated ±[device-reported accuracy] m  
> **Map status:** approximate center only — **not enough to verify boundary**  
> [Confirm site] [See nearby cemeteries] [Not here / choose another]

A combined site displays:

> **Within:** [Parent cemetery complex]  
> **Which ground?** [historic ground A] · [cemetery B] · [unknown]

UI should draw a GPS accuracy circle, distinct boundary styles for verified vs approximate mapping, and a visible map legend. Avoid showing detailed private grave positions or silently publishing captured location. Allow offline caching of bounded site metadata, maps, and linked names with last-updated dates. If GPS quality worsens or stale fix persists, show uncertainty; do not keep a previous green 'verified' status.

**Capture/export fields:** preserve raw GPS and its metadata, selected cemetery entity ID, parent complex ID if supported, candidate list with match reasons, location observation ID, reviewer/selection source, map citation and version. Continue preserving original JPEG separately from derivative and embedded EXIF GPS. A user-selected cemetery is *not* a burial/person identification.

## 8. Explicit pilot examples / do-not-merge cases

1. **Pine Grove, Warren:** Its current dossier provides a likely center and a municipal address. We do *not* have an approved surveyed boundary. Even if a camera GPS point is near the dossier centroid, return `nearby_only` or `possible_within`, not a verified site or plot.
2. **Pine Grove map's Forefathers Ground:** It's a named area in a photographed plan; confirm its exact name, legal or historic status, and geometry before deciding whether it is an internal historical ground or a section. Do not create a definite independent cemetery without evidence.
3. **St. Paul map:** Sections A–F exist as **image-plane** approximate anchors, not georeferenced shapes. Do not place GPS pins in them or combine St. Paul with Pine Grove merely because both appear in the Drive project.
4. **South Warren:** A source PDF page identifies South Warren Cemetery, not a specific photographed memorial. Treat as a separate known named-site candidate pending sourced geolocation and boundary work.
5. **Mixed directory boards:** Printed section/lot identifiers and provisional names cannot be assigned to Pine Grove or St. Paul until the board's cemetery attribution is verified. Name/lot-only joins are prohibited.
6. **Merged cemetery example (synthetic):** One present-day complex contains separate earlier churchyard and municipal grounds. Engine returns parent and two candidate child grounds if GPS uncertainty overlaps their division; no auto-merge of burial records.
7. **Contiguous cemeteries example (synthetic):** Two independent cemeteries share a fence or common entrance. Both appear as separate candidates if GPS accuracy circle crosses boundary; shared access does not imply one cemetery.

## 9. Test and acceptance gates

Synthetic geometry tests (do not use invented shapes as real-world site records):

- Point well within one authoritative polygon: one provisional site suggestion, with verified-boundary condition only when accuracy is adequate and no competing candidate.
- Two polygons sharing an edge: accuracy circle crosses both → `multiple_candidates`.
- Parent complex encloses two child sites: parent recognized, child unresolved unless clearly inside one child.
- Polygon with hole (non-cemetery interior): inside hole must not count as inside cemetery.
- Point near centroid but outside all polygon footprints: never assign verified cemetery.
- Unknown boundary / point-only site: `nearby_only`, not `within_verified_boundary`.
- Stale GPS, accuracy > boundary separation, manual coordinates: downgrade, preserve uncertainty.
- Same cemetery with alternate/historic names: one canonical entity, multiple names, no duplicate site.
- Same name for two distinct cemeteries in different towns: two entities, no name-based merge.
- Shared entrance or management only: no auto-merging.
- Historic merger effective date: present-day complex link does not erase historic site identity.
- Directory section and plot overlap: person-to-plot match remains blocked without documented cemetery + section + lot + verified map reference.
- Offline and fresh-map conflict: flag stale geometry and ask for confirmation, do not silently migrate assignments.
- Privacy tests: restricted photo/GPS cannot be exposed by unauthenticated map endpoints.

Production gate: verify D1 migration history; reconcile colliding feature migrations, complete tests and staging review, secure geospatial sources and publication rights. Keep `cemetery-picnic-camera-preview` isolated from main Workers until approved.

## 10. Execution checklist for the next engineering session

1. Inventory all existing cemetery entities, aliases, mapped sources and section references in main, Drive and staged branches.
2. Introduce a candidate source registry (municipal GIS, OSM, historic map images), licensing and geographic accuracy fields.
3. Build reusable point/accuracy-circle vs polygon resolver including nested, overlapping and holes cases.
4. Add cemetery complex / related-ground graph with typed links, time scope and cycle checks.
5. Add confidence and no-match outcomes, with cited reasons and human override.
6. Stage Pine Grove **point-only** candidate with exact source and centroid limitation; leave boundary null pending validation.
7. Stage St. Paul and South Warren names as source-linked candidates without inventing GPS polygons.
8. Build camera candidate selector UI + nearby maps + selected-complex/child display.
9. Preserve raw fixes and candidate list in ZIP `record.json`; validate against old v0.1–v0.5 exports.
10. Run synthetic geometry and privacy tests; seek municipal GIS boundary and historic-ground status before any production GPS-based site verification.

## 11. Source links from user's project

- Project Drive: https://drive.google.com/drive/folders/10kQDrxfn097oa4XRGe7_ee44zR9bJ2OW
- Pine Grove dossier: https://github.com/gittenssexton/Cemetery-Picnic-Club/blob/main/docs/PINE_GROVE_DOSSIER.md
- Source map photos: https://drive.google.com/drive/folders/1HyESdE1XKJCpjXro9_wqZBt3wtzTxcMW
- Existing map directory and geolocation policy: https://drive.google.com/drive/folders/1mklf1zSNC5ehTqAmsokAwb5BUNFDd-y4
- Domain handoff: https://docs.google.com/document/d/19wiVbe-DKjADiSpi1ogSuZBbz6MQ7nvbiYVxd6XCctM/edit
- Camera draft PR: https://github.com/gittenssexton/Cemetery-Picnic-Club/pull/3

**Final rule:** A GPS fix is an observation; a map is a sourced assertion; a cemetery match is a reviewable hypothesis. A cemetery complex is a relationship among entities, not an excuse to collapse distinct burial grounds or historical names.
