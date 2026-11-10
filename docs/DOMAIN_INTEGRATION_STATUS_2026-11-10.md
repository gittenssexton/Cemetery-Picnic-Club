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
