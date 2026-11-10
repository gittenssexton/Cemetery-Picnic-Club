# CPC domain integration status — 2026-11-10

## Scope and safety
Integration branch: `feature/domain-integration` forked from `feature/domain-nomenclature-contracts` (draft PR #4).
No production Worker, D1 database, `main` or original source files modified by this integration work.

## Verified branch inventory
- `main`: `0001_initial.sql`, `0002_global_research_core.sql`, `0003_stone_identification.sql`.
- `feature/stone-camera-pilot`: `0004_geological_map_core.sql`.
- `feature/field-camera-pilot`: `0004_monument_analysis.sql` (collides by number).
- `feature/new-england-vital-records-core`: geology `0004`, vital `0005_new_england_vital_records.sql`.
- `feature/domain-nomenclature-contracts`: domain registry, validator, tests and handoff.

## Staged migration sequence (integration branch only)
1. `0001_initial.sql` — inherited
2. `0002_global_research_core.sql` — inherited
3. `0003_stone_identification.sql` — inherited
4. `0004_geological_map_core.sql` — copied from geology feature branch
5. `0005_monument_analysis.sql` — copied from field-camera feature branch; number changed on this unmerged integration copy only
6. `0006_new_england_vital_records.sql` — copied from vital feature branch; number changed on this unmerged integration copy only

The geology migration references `markers`; camera references `markers`, `images`, `inscriptions`, `motifs`, `claims`, `sources`, and `craftspeople`; vital references `research_works`, `sources`, `persons`, and `markers`. These must be present in the inherited baseline before migrations run.

## Outstanding gates
- **D1 migration ledger not verified**. Do not run this numbering plan against a previously provisioned database until actual `d1_migrations` and deployment history are inspected. If earlier migrations were applied, use append-only compatibility migrations instead of rewriting history.
- **Fresh SQLite/D1 FK test not yet executed**: run migrations on an empty database with `PRAGMA foreign_keys=ON` and `PRAGMA foreign_key_check`; verify schema objects.
- Review geology seed numbering and scripts; ensure every seed is applied only after required tables exist, and is idempotent where intended.
- Inspect and selectively integrate camera UI and ingest code; do not combine overlapping PR #1/#2/#3 camera implementations blindly.
- Add domain v1 JSON schemas for GEO, VIT, IMG, valid/invalid fixtures and independent ingestion smoke tests, then linked candidate tests.
- Verify rights, private GPS redaction, immutable original photos and reversible candidate links.
- CI and staging D1 status are **not verified**; production unchanged by this work.

## Acceptance
Do not merge to main or deploy until live migration history and all schema, contract, ingestion and rights gates pass. The migration files here are **staged candidates**, not proof of successful D1 deployment.


## 2026-11-10 verification addendum (supersedes stale test gates above)
- CI executed the complete SQLite migration suite in memory with foreign keys enabled; see `tests/test_domain_integration.py` and `tests/test_integration_migrations.py`.
- GEO/VIT/IMG versioned record JSON Schemas are present at `domains/{GEO,VIT,IMG}/contracts/v1/record.schema.json`. Timestamp format validation is explicitly constrained.
- Independent, synthetic geology catalog, vital source and image/field draft tests verify no automatic identity or material attribution. Candidate withdrawal preserves source records.
- Verified green integration workflow on commit `f8ab874ee116e1b7e3d06086f0b905692e14eadd`: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42842111929
- Cloudflare connection inspection found only one D1 database, `cartoveyra-research-staging`, in the currently connected account. No Cemetery Picnic Club D1 database was listed; a CPC migration ledger therefore could not be inspected there. This does **not** prove no CPC D1 exists in another account.
- Remaining: production account identification and D1 ledger if applicable; deployment of isolated CPC staging database; live source acquisition and licenses; phone Safari field-camera tests; end-to-end geologic unit extraction and vital entry review. No staging D1 migration or production deployment performed by this session.

## Session continuation: validated integration work
- Resolved a **second** schema collision: `0002_global_research_core.sql` and the camera migration both defined `motif_interpretations` with incompatible columns. Camera-specific table is now `marker_motif_interpretation_candidates`; earlier scholarly table remains unchanged.
- Added GEO, VIT and IMG v1 JSON Schema contracts, ownership READMEs, and contract tests rejecting wrong namespace, invalid rights, malformed dates and uncited links.
- Added in-memory migration and domain-ingestion smoke tests, candidate withdrawal preservation and SQLite FK/integrity checks.
- GitHub Actions successfully completed **45 tests** in run https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42842111929 . This verifies a fresh SQLite integration, **not** Cloudflare D1 deployment history or staging D1 migration.
- No production changes or real-data bulk ingest. Domain adapters, source-specific authorized ingestion and staged D1 remain future work.

## Cloudflare D1 live inventory — read-only check, 2026-11-10
- Inspected the connected Cloudflare account via the read-only List D1 Databases API.
- The account exposed **one** D1 database: `cartoveyra-research-staging`, unrelated to CPC.
- **No CPC-named D1 database was listed in this connected account.** This does not prove no database exists in another account/environment or that no earlier deployment occurred.
- No D1 SQL executed and no D1 resource created, modified or deleted.
- Gate: establish which intended CPC staging/production database and Cloudflare account should be used before any migration execution. Do not point CPC migrations at CARTOVEYRA.

## Session continuation — seeds and ingestion adapters
- Imported `db/seeds/0005_geology_map_sources.sql` from the geology branch. The catalog is metadata only; it creates no automatic material or quarry provenance claims.
- The additional `0006_ma_zen1983_symbol_crosswalk.sql` remains out of the default sequence pending source-level review and deliberate release; the existing seed sequence stays 0001–0005.
- New `tests/test_seed_integration.py` checks all seeds against the integrated fresh schema, repeatable reruns and absence of fabricated positions, material links, burials and photo records.
- Added `scripts/ingest_domain_metadata.py`: dry-run unless explicit `--apply --database` to an existing **local SQLite** file. Only GEO map-source catalog entries, VIT collection entries and IMG local drafts are supported. All other record types fail closed. No D1 connection, image bytes, person reconciliation, markers or historical claims.
- Added metadata-adapter tests for allowable imports, duplicate safety, rights/namespace rejection and separation of evidence sources.
- GitHub Actions: **53 tests passed** at https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42843687450 . The first staging/production database migration and real-source extraction remain unperformed.


## 2026-11-10 isolated Cloudflare D1 staging execution
- **Created** a NEW unbound Cloudflare D1 database: `cemetery-picnic-club-integration-staging` (UUID `ad4a436d-048c-47a6-bd00-8cf1b9632f6b`). Existing `cartoveyra-research-staging` is unrelated and untouched.
- Applied migrations `0001` through `0006` successfully using the Cloudflare D1 API and then the new append-only `0007_domain_evidence_links.sql`. This is **staging only**; none of the production Workers or `main` was deployed or migrated.
- Added `cpc_staging_schema_ledger` as a dedicated integration-stage ledger, containing the seven filenames and their checked GitHub blob SHAs. It is not Wrangler's `d1_migrations` table and should not be passed off as one.
- D1 `PRAGMA foreign_keys` returned 1; `PRAGMA foreign_key_check` returned zero violations. Cloudflare denied `PRAGMA integrity_check` with SQLITE_AUTH; local SQLite test covers integrity check, but remote integrity check is **not** claimed.
- Remote synthetic sample created marker, photo, geology source, canonical refs and a typed, cited candidate link; checked candidate state, set link to rejected, and removed synthetic records. After cleanup: `domain_evidence_links=0`, `domain_entity_refs=0`, `images=0`, `vital_record_entries=0`, `geology_map_sources=0`. No real records imported.
- The integration-branch v7 migration adds explicit `domain_entity_refs` and `domain_evidence_links` tables; links require two registered canonical refs, evidence reference + locator, status and separate rights. Existing domain tables remain distinct. Registry-to-underlying-row existence must be checked by adapters, since a generic bridge table cannot enforce dynamic foreign keys to arbitrary domain tables.
- CI for seven migration coverage and evidence-link tests passed: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42843864025
- **Remaining gates:** real-source ingestion with reviewed permissions and source provenance, adapter validation of source-row existence and duplicate imports, field camera Safari tests, accurate geologic map extraction, vital records manual review, staging Worker integration, and review of PR #5 before any production merge. Avoid deploying unapproved image content, GPS details, and private vital records.


## Source-row adapter hardening
- Added `scripts/domain_ref_adapter.py`: allowlisted CEM/GEO/VIT/IMG entity mappings, validates the source-owned table row exists before registering a canonical reference, rejects invalid/unknown entity types, and creates only unreviewed candidate links with publication permission unknown.
- Added `tests/test_domain_ref_adapter.py` covering missing source row, invalid ID, duplicate-safe reference registration, citation requirement, candidate rejection/removal, original image preservation, and no implicit publishing.
- GitHub Actions succeeded at commit `50a60dc65a1f3978ba7979fb97579864674337c0`: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42844288760
- This Python adapter is a tested integration/library interface, not yet a deployed Worker API. No real-source imports or app sync are claimed.

## Further integration — evidence bridge runtime guards
- The branch already contained `0007_domain_evidence_links.sql`. A schema-only canonical reference does not guarantee the polymorphic underlying record exists, so `scripts/domain_evidence_bridge.py` now checks allowed domain/table ownership and the actual source row before registering a canonical ref.
- Candidate links require an existing `sources` citation and nonblank locator, valid registered endpoints, and remain restricted/unpublished by default. No automatic person merge or geology attribution.
- Rejection preserves the reviewed link, original image/source record, and historical entry. A read-only public view includes only explicitly reviewed, publicly permitted links and omits raw citation notes and locators. **Page-level photo/record/GPS permissions still need separate application checks.**
- The new `tests/test_evidence_bridge.py` includes missing-row, invented-citation, mistaken namespace, duplicate mapping, rejection-retention and privacy/redaction cases.
- Verified successful GitHub Actions run: **64 tests passing**, https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42844481860 .
- No CPC staging D1 was created; no production change. Next: integrate the reviewed application API with these guards and separately verify a dedicated CPC staging DB and field-camera capture behavior.


## 2026-11-10 continuation: staging geological inventory and importer hardening
- **Live staging:** `cemetery-picnic-club-integration-staging` (D1 UUID `ad4a436d-048c-47a6-bd00-8cf1b9632f6b`) has seven migrations, verified separately from any production database. Earlier notes above saying staging D1 does not exist are historical and superseded.
- Applied `db/seeds/0005_geology_map_sources.sql` to the staging D1 database. Current inventory: **6 geology map metadata records; 3 archived asset references**. Records are descriptive bibliography/archive references, not verified geologic units.
- Applied seed a second time as an idempotency check: **0 additional rows**. Added a staging-only `cpc_staging_seed_ledger` entry recording seed filename, GitHub blob SHA `0b437aa94a7549bb8813331e8331afc10b0ccd41`, branch, and metadata-only scope.
- Remote D1 post-seed checks: `geology_units=0`, `stone_material_candidates=0`, `marker_positions=0`, `vital_record_entries=0`, and `PRAGMA foreign_key_check` returned no violations. No person/marker/geolocation matching was performed.
- Updated `scripts/ingest_domain_metadata.py` to reject inconsistent `domain:record_type:source_local_id` canonical references and reject nonempty `links` rather than silently discarding citations. Added corresponding tests in `tests/test_metadata_intake.py`.
- CI green at https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42845116553 . Some intermediate commits failed while a separate evidence-bridge public-visibility test was being tightened; the cited passing run is the checked integration state.
- Pending: obtain/verify real geologic unit geometries and point-query response; review source acquisition/redistribution rights; source-aware vital collection review; image capture UI integration and Safari field testing. **Production, main, and original images unchanged.**

## Continuation — privacy-gated links and isolated camera package (2026-11-10)
- The public evidence-link view now checks publication authorization of **both actual source rows** and the access scope of the **cited source**, not just the link's publication flag. IMG original images require explicit publish permission; VIT entries must be public historical and reviewed. Unknown/unsupported entity types fail closed. Camera field drafts never become public edges.
- Added regression tests for restricted citations, restricted vital records, unpublished images, and unreleased camera drafts. Internal read access still requires caller authorization at the application layer; this helper alone does not implement authentication.
- Staged the field-camera v0.5 package from `feature/field-camera-pilot` into `web/camera/` (8 files). It remains browser-local via IndexedDB and ZIP export; no CPC server-side photo sync or database writes have been wired. Older parallel camera PRs were **not** merged. It is not linked from the primary UI or deployed from this integration branch.
- Added static camera package checks, including existence of local JS dependencies and absence of direct upload paths. **These tests do not substitute for iPhone Safari field tests, actual camera/GPS validation, original-byte comparison, ZIP inspection, or accessibility review.**
- GitHub CI verified **73 passing tests** on `feature/domain-integration`: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42845500292 .
- Outstanding deployment gate: Cloudflare account inventory showed no CPC D1 database; do not run integration migrations against CartoVeyra's database. Staging D1, mobile field validation, and live licensed evidence ingestion remain unresolved.


## Source metadata-to-evidence integration safeguard
- The local metadata adapter now rejects inconsistent `entity_ref` / `source_local_id` pairs and nonempty cross-domain links it cannot process instead of silently discarding them.
- The adapter now writes the **source-local ID** as the source table primary key; the canonical `DOMAIN:type:local-id` lives in `domain_entity_refs`. This fixes incompatibility with the already implemented evidence bridge.
- New integration tests run GEO/VIT metadata intake, register canonical endpoints, create a cited candidate link and verify that no person, claim or automatic match is manufactured. A full remote metadata-import API is still not deployed.
- The geological source catalog is present in staging (six maps, three archived asset references) and is repeatable without duplicates. Map symbols/geometry remain unreviewed.
- Production files, public Worker, original camera photos and main branch are unchanged by this session.

## Verified continuation — D1 reconciliation and camera export review

- Read-only Cloudflare D1 inspection of `cemetery-picnic-club-integration-staging` confirms migration ledger entries for **0001–0007**. Each recorded GitHub blob SHA matches the current integration-branch migration file. The database is **staging only**.
- Staging seed ledger shows `0005_geology_map_sources.sql` applied with provenance and metadata-only scope; no accepted image, vital-event, or cross-domain-link records in the inspected staging database. `PRAGMA foreign_key_check` returned no violations. CARTOVEYRA's separate D1 was not modified.
- Added `tests/test_camera_exif.mjs` and a GitHub Actions step executing the actual EXIF GPS encoder for four coordinate fixtures; each verifies DMS coordinates and original JPEG byte preservation.
- Added `scripts/validate_camera_export.py` and synthetic `tests/test_camera_export_zip.py`: validate exported `record.json`, camera version, original JPEG presence/hash, ZIP path safety, duplicate members, coordinate-status consistency, and restricted reporting. **No file upload, database import, automatic person attribution or public GPS access occurs.**
- GitHub Actions validated **87 Python tests plus the JavaScript EXIF test**: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42846751437
- Added `docs/CAMERA_FIELD_ACCEPTANCE.md` to specify the physical iPhone Safari, camera, GPS, original image, region proposal and ZIP export conditions that remain unverified.
- Still blocked for release: physical iPhone/Safari field evidence, source rights and geologic/vital review, authenticated application API, production migration/deployment approval. Draft PR #5 remains unmerged.


## Continuation — audited import ledger and six-state vital source inventory
- New migration `0008_metadata_import_audit.sql` is applied to isolated Cloudflare D1 `cemetery-picnic-club-integration-staging` and recorded in `cpc_staging_schema_ledger` with GitHub blob SHA `3e0ca6419eebdc3536134081732348741f417cec`. D1 `PRAGMA foreign_key_check` showed no violations and there were **zero** audited JSON imports at verification. This avoids mislabeling SQL seeds as audited JSON imports.
- Added transactional local `scripts/ingest_audited_metadata.py`, testing exact replay, duplicate conflicts, changed-source drift, rights checks, all-or-nothing rollback and zero implicit person/marker/material attribution. Its CLI is dry-run by default; it does not connect to D1.
- Source registry copied from `feature/new-england-vital-records-core` to `data/vital-records/new-england-source-registry.json`. Added `db/seeds/0006_new_england_vital_catalog.sql` with MA/CT/RI/NH/VT/ME state jurisdiction metadata, Warren (Western) alias and LOC Warren 1910 source bibliography. No actual event transcription accepted.
- Applied vital catalog seed to isolated D1; first pass inserted **six state jurisdictions, one Warren town, one historical collection**, and repeated pass inserted zero records. Seed ledger stores blob SHA `3fd34b29626d1ad28587ce5681b2c34d776e016b`. Query verified six states, one collection, zero accepted vital entries, zero persons, zero match candidates, and no FK violations.
- Provisional 75 Warren birth OCR candidates in the separate vital branch still lack page-image QA; do **not** import them as verified events or independent evidence. `G.S.2` is gravestone-derived; no circular corroboration.
- Verified CI after the SQL and seed integration: **88 Python tests passed** in https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42846991792 (additional camera Node checks are run by workflow separately).
- `docs/METADATA_IMPORT_AUDIT.md` provides exact local usage and identifies outstanding authentication, rights, and scanned-page review gates. PR #5 remains draft; no production Worker or main-branch rollout.

## Additional staging inspection and authenticated API scaffold
- Live, read-only staging D1 reconciliation now verifies **eight** migrations (0001–0008) against GitHub blob SHAs; `PRAGMA foreign_key_check` returned an empty result. Staging currently contains six geological source catalog entries and no images, vital entries or cross-domain links.
- Added camera ZIP review validation with `scripts/validate_camera_export.py` and synthetic rejection cases: path traversal, duplicates, mismatched record IDs, malformed GPS state, missing original frame and unsupported versions. Report intentionally excludes precise GPS values. Validation does **not** import or publish records.
- Added the `server/cpc-integration-staging.mjs` **undeployed** Worker scaffold: bearer-token-gated, parameterized, bounded read-only D1 link query with no mutations or uploads. A separate non-sensitive liveness endpoint exists; the private endpoint is not a public search API. See `docs/STAGING_EVIDENCE_API.md` for required bindings and review gates.
- GitHub CI verified **88 Python tests, Node EXIF test, and Node Worker authorization test** at https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42847336855 .
- Remaining blockers: human iPhone Safari test, authorized image and source ingestion review, secret/access configuration, secured staging Worker deployment and end-to-end API tests, production migration review and release approval. Nothing from this branch has been merged to main.

## Camera ZIP provenance tightening and concurrent OCR migration (2026-11-10)
- Hardened `scripts/validate_camera_export.py` to reject conflicts between `location_status` and the coordinate `source` (`device_gps` vs `manual`), invalid reported GPS accuracy, or a `_geotagged.jpg` file inside an explicitly unlocated export. Added regression coverage in `tests/test_camera_export_zip.py`.
- The repository now contains `0009_vital_ocr_review_queue.sql`, introduced by concurrent OCR queue development. Tests that assumed exactly eight migrations initially failed, and were revised by that workstream. Verified subsequent GitHub CI: **93 Python tests plus Node EXIF and staging-API checks passing**, https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42855780199 .
- **Important: source-branch migration count and applied staging count differ.** Read-only D1 inspection still shows only 0001–0008 applied; 0009 is not in the inspected staging ledger. Do not mark 0009 as applied, deploy it silently, or merge the branch before its D1 staging validation and OCR privacy/rights review.
- `PRAGMA foreign_key_check` on the current staging database remains clean. Staging still has zero image, accepted vital-entry and cross-domain-link records at inspection. No production or main change from this refinement.


## Continuation — 75 provisional Warren OCR candidates safely staged
- Added `0009_vital_ocr_review_queue.sql` on the integration branch and applied to isolated CPC D1 staging. Recorded migration blob SHA `5ccd4b83d3125dca5f92e592d9d36d8e16c56995` in `cpc_staging_schema_ledger`, now **nine migrations**. The queue remains physically separate from accepted `vital_record_entries`.
- Copied 3 original Warren 1910 birth OCR candidate JSON batches from `feature/new-england-vital-records-core` without changing source readings: printed pages 9, 10, 11, each with 25 **selected** (not page-complete) entries.
- Added `scripts/stage_warren_ocr_review.py`, a dry-run-by-default local staging adapter that requires exact collection/page IDs, unverified scan status, original text, G.S.2 dependency and source hashes; changed batches are rejected.
- Added `tests/test_warren_ocr_review.py` verifying the 75-candidate/14-G.S.2 totals, duplicate-safe replays, correction hashes, no automatic scan approval, no invented independent gravestone evidence, and no accepted events/persons.
- Staged **75 distinct OCR candidates** in the actual isolated Cloudflare D1 `vital_ocr_review_candidates` table, retaining raw JSON, per-record hash and batch hash. Batch hashes: p009 `a5fc5936d403d0c08eb48da1f086a69ea8acfda5a5860860b772b08d9cb65fb6`, p010 `e58d46a5df8932dfbf71bff19b849cb835d473ba7b5afe5c98eeb18d8856d9fa`, p011 `b20f790362ef1842012dae5781a1a977bd1102463ced2ae04a877d96f8af9bc2`.
- Post-import D1 queries: 75 unique candidate IDs, 14 gravestone-derived with no independent corroboration, 0 image-checked, 0 accepted vital events, 0 persons, 0 burials, 0 identity matches, 0 FK violations.
- Page QA priorities, including uncertain initials, OCR years, parent spellings and corrected BARNUM names, recorded in `docs/WARREN_OCR_REVIEW_PRIORITIES_2026-11-10.md`. There are 13 candidates with OCR notes and 11 without an exact ISO date; original printed pages still need manual image verification.
- Integration test CI: **99 Python tests passed** on commit `30beb319b7e73776a86e72abc0e90c9418080a62` (run https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42855955529). No production rollout.

## Staging 0009 reconciliation and API hardening — 2026-11-10
- Verified that `vital_ocr_review_candidates` and `vital_ocr_review_batches` existed on the isolated staging D1 but the migration ledger had no 0009 entry. Reviewed table columns, defaults and indexes against `0009_vital_ocr_review_queue.sql`. Re-executed its idempotent `CREATE TABLE/INDEX IF NOT EXISTS` statements without altering existing data and inserted a staging ledger entry with exact GitHub blob SHA `5ccd4b83d3125dca5f92e592d9d36d8e16c56995`.
- Afterward the staging ledger contains 0001–0009 and `PRAGMA foreign_key_check` returned no violations. **Caveat:** the D1 API blocked direct inspection of complete `sqlite_master.sql` definitions, so this is a migration/column/index reconciliation, not a full bit-for-bit DDL proof.
- Read-only OCR QA: **75 candidate rows in three 25-record batches**; all `requires_page_image_check`, all with `source_image_verified=0`. Sixty-one have `town_book` source lineage and fourteen have `gravestone` lineage. The latter remain explicitly uncorroborated. `vital_record_entries` remained empty.
- The staging Worker scaffold now requires `CPC_ENVIRONMENT=staging`, a matching `CPC_ALLOWED_HOST`, bearer secret and a non-browser request for internal evidence lookups. It remains **undeployed**; the optional `/health` endpoint is liveness only. This does not replace Cloudflare Access, credential rotation, upstream authorization or a penetration test.
- Tests: **99 Python tests** and both Node checks passed in https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42856686814 . No production deployment or main merge.


## Continuation — manual scan review and guarded acceptance (2026-11-10)
- Added `0010_vital_manual_review_evidence.sql` to `feature/domain-integration`; applied it to **isolated** D1 `cemetery-picnic-club-integration-staging` and recorded blob SHA `7f5e7d8e99376e26026d45f804a6120c5f3ce805` in `cpc_staging_schema_ledger`. **10 migrations applied**. Cloudflare `PRAGMA foreign_key_check` returned no violations.
- Schema adds append-only `vital_ocr_page_reviews` (reviewer identity, time, exact line, scanned image URL/sequence/SHA, corrected reading, decision) and `vital_ocr_accepted_events` (traceable accepted source event). Append-only triggers prevent update/deletion of review and acceptance lineage.
- `scripts/review_warren_vitals.py` provides an offline human-attestation entry and explicitly rights-gated source-event acceptance. Acceptance requires a `confirmed` scan review and matching original candidate hash/page, plus deliberate collection rights/ingestion approval. Any accepted source entry remains `restricted` and creates **no** person, burial, marker, relationship, or identity match. The currently staged Warren collection is **metadata_only** and does not permit acceptance.
- Added six `tests/test_warren_scan_acceptance.py` cases covering the rights gate, source event separation, rejected/uncertain review, G.S.2 lineage, append-only evidence and invalid scan locator fields. Corrected a UTC timestamp regex bug discovered by first CI run. Verified **105 Python tests passed** on https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42858161345 .
- Expanded the undeployed `server/cpc-integration-staging.mjs` with `GET /internal/warren-ocr-review?page=9|10|11`, an authenticated, read-only, parameterized internal queue endpoint with no raw source JSON or approval/mutation path. Node tests verify authentication and invalid-query rejection. **Worker has not been deployed**.
- Verified isolated D1 after migration: `vital_ocr_review_candidates=75`, `vital_ocr_page_reviews=0`, `vital_ocr_accepted_events=0`, `vital_record_entries=0`, `persons=0`. No scanned-page verification has occurred. Production, `main`, original photos and Cartoveyra D1 remain untouched.
- Outstanding: original-image review of pages 9–11, correction of incomplete OCR page samples, rights/source checks and named human review, authenticated staging Worker deployment/security testing, physical iPhone/Safari and camera ZIP validation, geological unit extraction/QA, and separate authorization for any public historical search.
