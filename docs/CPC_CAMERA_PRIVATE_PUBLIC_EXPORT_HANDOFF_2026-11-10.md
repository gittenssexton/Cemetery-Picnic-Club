# Cemetery Picnic Club — Camera Private Archive / Shareable Export Handoff

**Date:** 2026-11-10  
**Status:** Engineering handoff; **not implemented or deployed**  
**Owner / integration authority:** Main Cemetery Picnic Club project and its domain-integration workstream  
**Canonical working copy:** `docs/CPC_CAMERA_PRIVATE_PUBLIC_EXPORT_HANDOFF_2026-11-10.md` in `gittenssexton/Cemetery-Picnic-Club`  
**Reference:** Draft camera PR #3 (`feature/field-camera-pilot`); domain architecture PR #4 (`feature/domain-nomenclature-contracts`); `docs/CEMETERY_GPS_IMPLEMENTATION_CHECKPOINT_2026-11-10.md`

## A. Routing decision and coordination protocol

Implement the export separation **within the current camera branch and shared IMG/LOC/CEM contracts**, not as a new independent application, database, or competing camera prototype. The current camera workstream owns capture UI and ZIP generation; the main/integration workstream owns shared rights policy, D1/R2 access control, contract harmonization, and final merge. This handoff is the acceptance contract between those workstreams.

**No automatic chat-to-chat messaging exists.** The two conversations can coordinate using repo files/PR comments and the mirrored Drive handoff; each session must re-read the latest GitHub version and associated `IMPLEMENTATION_STATUS` section before touching the same files. This isn't a push notification or a live connection between conversations. Avoid simultaneous edits to `web/camera/index.html`. Keep one named owner per change, and write exact commit hashes, tests, and deployment IDs when reporting progress.

**Status update protocol**
1. Read current main, PR #3, PR #4 and the export handoff; recheck actual D1 migration history before DB changes.
2. Update the **status section at end of this document** or create a dated `docs/EXPORT_PRIVACY_IMPLEMENTATION_CHECKPOINT_YYYY-MM-DD.md` in the same repo/branch. Record owner, branch, commit SHA, changed files, tests, warnings, current deployment and pending work.
3. Link the checkpoint in the relevant PR description or comment; duplicate a human-readable snapshot to `Cemetery Picnic Club/11_App_Database_Technical` in Drive if useful. **GitHub is source of truth; Drive is a snapshot, not an automatically synchronized workspace.**
4. Before accepting work done in the other conversation, read back commits/checkpoint. Do not assume a new note means changes are in the camera preview or production.

## B. Current verified baseline as of handoff creation

- Field camera draft PR #3 exists, is open/draft; repo `feature/field-camera-pilot` contains `web/camera/index.html` and on-device cemetery candidate resolver.
- `exportCurrent()` builds **one ZIP** containing `record.json`, the original full-frame camera JPEG, processed isolated JPEG, transparent cutout PNG and **optionally** an EXIF GPS JPEG.
- GPS EXIF is **unchecked by default**. This **does not** make the ZIP safe to share: `record.json` includes GPS, GPS observation/candidate matches and potentially named cemeteries/plot information.
- Privacy annotation calls current ZIP a `private_archive`. No sanitized share ZIP is implemented or validated yet.
- Source-level camera/GPS/relationship tests were reported passing in the camera checkpoint, but no physical iPhone, actual ZIP round-trip or sharing safety audit was verified.
- Historic named grounds may be mapped as relationships without assuming merger. A cemetery selected by a user is not proof of a surveyed grave location.

## C. Two distinct export products

### 1. Private research archive (`CPC_PRIVATE_ARCHIVE_V1`)
**Use:** owner's research, approved stewardship, archival ingestion. **Default destination is private**; never implicitly upload or publish.

Contents:
- Unmodified captured original image bytes from the browser frame; exact photo capture evidence and original file provenance where available. If later importing native Photos/HEIC, preserve original file and embedded metadata as received.
- All derived photographs/masks and transformation recipes, including source-image linkage, processing algorithms/settings, coordinates for contours and image-region annotations.
- Full, unrounded GPS observation (`lat/lon`, accuracy meters, timestamp, fix age, GPS provider, manual-vs-device), along with distinct **cemetery candidate vs user selection vs verified assignment**.
- Full historical claim/evidence provenance, material/carver/motif hypotheses, source rights and review status, original capture timestamp, source IDs and immutable record ID.
- Explicit `sensitivity: "restricted"`, `archive_kind: "private"`, `contains_precise_location: true/false`, and a visible warning before saving/transmitting; embedding GPS EXIF remains a separate opt-in, and its absence must never imply the JSON is redacted.
- Integrity manifest with size and SHA-256 for each file, schema version and export tool version. No silent rewriting of source data.

**Access:** encrypted at rest when persisted to a server and role-gated for reads; no public URL to the archive; user explicitly controls sync/upload. Private ZIP is still sensitive even if locally saved to Files; do not promise ZIP encryption where none exists.

### 2. Shareable record (`CPC_SHAREABLE_RECORD_V1`)
**Use:** intentionally shared visual/history summary (classroom, historical society, public contribution) with privacy controls.

**Default: coordinate-redacted, conservative**. Construct with a **positive allowlist from scratch**; do not clone `record.json` and then delete a few known GPS fields. Default public content:
- New non-reversible, random public export ID (do not expose raw database/private record ID, original basename, EXIF device IDs or crosswalk keys).
- User-approved image derivatives generated from decoded image pixels with a metadata-free export. **Do not include original image, geotagged image, unaltered HEIC, thumbnails carrying EXIF, or `.zip` inside ZIP**. Image transformations must not invent letters/carvings.
- User-approved inscription reading, monument form, motif observations, broad material candidates, dated citation URLs/locators and explicit `provisional`/`review_status`. No automatic human/plot matches.
- `site_display`: default `hidden`; optionally allow user-reviewed broad geography or named cemetery after an explicit review screen (because names, lot numbers, maps and contextual photos can re-identify exact places). Avoid automatically carrying over GPS candidate results or historical-complex graph.
- Optional category-level region (e.g. state) only if explicitly approved and not derived from an unsafe precise-site inference. **No arbitrary coordinate rounding or jitter**: these still permit reidentification.
- A public provenance summary with **non-sensitive** source title/URI only; never internal Drive share tokens, unpublished document text, precise private source coordinates or private file paths.

Strictly exclude by default anywhere in the ZIP, JSON, binary metadata, exported filenames, or previews:
`latitude`, `longitude`, `accuracy_m`, `horizontal_accuracy_m`, `altitude`, GPS EXIF/XMP/IPTC location, raw GPS fix, provider/timestamps of sensitive location observation, geofence polygon, device identifiers, plot coordinates, plot number, private record UUID, cemetery candidate distances, nearby-cemetery shortlist, restricted notes, and original image bytes.

**Do not promise anonymous photos:** visible signs, inscriptions, nearby buildings, distinctive monument features, image content and any approved cemetery name can reveal the place. Provide a human review step and warning before sharing. A public export can't reliably remove all visual location cues automatically.

**Explicit exception / authorized precise sharing** is **not** the ordinary public mode. Add a separate reviewed release profile with permission records, declared purpose, data fields disclosed, recipient/audience, consent and expiry/withdrawal policy, a user acknowledgment and domain access validation. Never use a single “share” checkbox to expose raw coordinates. If not implemented, leave precise-location sharing disabled.

## D. Export interface and data contracts

UI controls: `Export private research ZIP` and `Create shareable ZIP`; separate button labels and visual descriptions. For public ZIP, require a confirmation/review sheet covering images, visible text, site name, map/location, note fields, citations and declared audience. Default all potentially identifying fields off. If private archive GPS included, warn that `record.json` contains exact coordinates even if geotagged JPEG is unchecked.

**Example sanitized public structure** (illustrative, NOT existing data):
```json
{
  "schema_version": "CPC_SHAREABLE_RECORD_V1",
  "public_export_id": "random-nonlinkable-id",
  "privacy": {"profile": "public_redacted", "precise_location_included": false, "reviewed_by_user": true},
  "monument": {"form": "tablet", "inscription_status": "provisional"},
  "observations": {"motifs": [], "material_candidates": []},
  "site_display": null,
  "sources": [],
  "assets": [{"file": "image_01.jpg", "kind": "derived_redacted_visual", "rights_reviewed": true}]
}
```

The public schema must not contain original `location_observation`, `location_observation_id`, `cemetery_match`, `cemetery_assignment` or private per-capture hashes that allow correlation; never trust `strip.export_privacy` labels as proof a ZIP is safe.

Function-level structure: `exportPrivateArchive(record,settings)`, `buildShareableRecord(record,reviewedAllowlist)`, `encodePublicImage(originalDecodedPixels)`, `verifyExportPackage(zip,profile)`. Use centralized shared privacy policy helpers (IMG/LOC/CEM) instead of duplicating redaction logic in the UI and backend. Treat ZIP entry paths and filenames as untrusted data; block traversal and nested archive bypass.

## E. Acceptance tests / threat-model gates

- **Unit snapshots:** inputs containing exact coordinates in every nested GPS/cemetery/EXIF field, opaque IDs, notes, image filenames, `location_observation`, `location_status`, `cemetery_candidate_catalog_version`, candidate results, manually entered GPS, complex/child relations and source citations.
- **Byte-level ZIP scan:** open actual exported ZIP, inspect all entries recursively as applicable, parse JSON, inspect JPEG EXIF, TIFF/PNG chunks and optional XMP/IPTC; prove private-only coordinates/IDs are absent from public files/metadata/filenames. Scan for known test coordinate tokens and original image hashes, while recognizing those scans are not sufficient by themselves.
- **Image integrity:** private ZIP original SHA-256 equals captured source bytes; public image is newly encoded with no metadata; check pixels are visually usable and processing is cited.
- **Negative flows:** no GPS, stale GPS, very accurate GPS, manually entered coordinates, GPS EXIF off/on, nearby overlapping or combined cemeteries, hidden cemetery name, restricted research notes, historic/modern site name conflicts.
- **Sharing control:** public redaction defaults; explicit reviewed opt-in for named cemetery; change review selections produces correct new ZIP; no public archive URL generated from private data; review canceled = nothing shared.
- **Round-trip:** iPhone Safari ZIP saved into Files, re-imported/read on desktop; older v0.1–v0.5 private export formats still recognized without backfilling missing provenance.
- **Client/server:** backend rejects public upload of private ZIP, unauthorized access, unsafe paths and unapproved precise-release fields; storage/cache and logs don't leak private GPS; per-user authorization enforced server-side.
- **CI required:** tests run against actual generated archives, not just static string assertions; report failures/coverage and at least one manual iPhone test before calling implementation complete.

## F. Dependencies and non-goals

- `web/camera/index.html`, `exif.js`, ZIP writer, any new export helper and `tests/test_camera_gps_contract.js` (camera PR #3); global domain registry/validation (PR #4).
- One shared research core: IMG handles images/export rights, LOC handles GPS sensitivity, CEM handles site identity, HIS handles source publicability. No silent ID merges or cross-domain promotion.
- Resolve competing SQL migration 0004/0005 numbering and actual D1 migration history before adding DB tables. **Do not provision D1/R2 or touch the main Workers from this handoff alone.**
- Keep Cloudflare `cemetery-picnic-camera-preview` experimental and separate from the main Worker.
- No machine vision recognition, no ability to scrub location cues from the visible scene, no automatic determination that a cemetery's legal/research data can be published.

## G. Work order — main workstream and camera sub-workstream

1. Main workstream: choose implementation owner/branch and annotate this handoff; inspect current PR #3 changes to avoid duplicate code.
2. Camera workstream: extract ZIP builder and privacy profiles into testable pure helpers; add first unit tests for public allowlist.
3. Camera workstream: separate UI actions, review flow, and two distinct schemas/filenames.
4. Camera workstream: metadata-free public derivative JPEG and privacy audit of image / JSON / path contents.
5. Shared contracts: define authorized fields, rights, retention/deletion and coordinate-access policy for sync, D1/R2 and future public API.
6. QA: generate actual test ZIPs with fake/private GPS and nested sensitive data; inspect EXIF/JSON and ZIP entries; run iPhone Files roundtrip.
7. Integration: main workstream review and resolve migration / access control dependencies; merge only after review and confirmed test results.
8. Status reporting: write dated checkpoint (owner, SHA, exact changed files, tests, deployment). Keep original Drive handoff and any updated revision linked.

## H. Implementation status (append dated entries; do not replace history)

**2026-11-10 — handoff authored.** Both export contracts defined. Existing camera produces only private ZIP; optional GPS EXIF is unchecked by default but coordinates remain in private JSON. Shareable coordinate-redacted ZIP **not implemented**, no new test results, no Worker deployment or schema change by this handoff. Main conversation must adopt the handoff before simultaneous code editing begins.
