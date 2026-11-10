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
