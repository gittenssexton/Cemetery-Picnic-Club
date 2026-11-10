# Cemetery Picnic Club — Domain-Nomenclature Integration Handoff
**Prepared:** 2026-11-10  
**For:** Next engineering session / coding agent  
**Scope:** Integrate independent domain pipelines into one globally scoped, evidence-based CPC core.  
**Status:** Architecture defined on feature branch and draft PR; branch integration and production rollout **not completed**.

## 0. Immediate instruction

**Do not create another unrelated standalone prototype.** Begin by inspecting the current state of `main`, the linked branches, active PRs, the D1 deployment history, and CI. Follow existing work where it is further developed. Preserve originals and source provenance. Do not silently merge or deploy.

Core documents:
- [Domain architecture](../docs/DOMAIN_ARCHITECTURE.md)
- [Machine-readable domain registry](../architecture/domain-registry.json)
- [Domain validation script](../scripts/validate_domains.py)
- [Contract tests](../tests/test_domain_contracts.py)
- [Draft PR #4](https://github.com/gittenssexton/Cemetery-Picnic-Club/pull/4)

## 1. Architectural decision

CPC has **one global connected research core**, not ten isolated databases. Each discipline owns its **nomenclature**, import pipeline, validation, permissions, tests and versioned data contract. Pipelines operate independently, but join via typed, cited, reviewable references. Pine Grove, Warren is a field pilot, **not a geographic restriction**.

| Namespace | Owner / boundary | Distinguish carefully |
| --- | --- | --- |
| `CEM` | Cemeteries, plots, memorials, burials | Marker ≠ burial ≠ person |
| `VIT` | Civil, church and archival vital events | A printed entry ≠ independently verified event or person |
| `GEO` | Geological maps, rock observations, quarries | Nearby bedrock ≠ gravestone composition ≠ quarry source |
| `ICO` | Observed motifs and meanings | Observed icon ≠ meaning ≠ maker |
| `CAR` | Carvers, workshops, signatures, lettering | Stylistic resemblance ≠ documented maker |
| `IMG` | Camera originals, derivatives, analysis | Visual-interest highlight ≠ recognized motif |
| `HIS` | Scholarship, archives, citations and claims | Bibliography ≠ reviewed full text ≠ image license |
| `KIN` | Genealogy, family and identity matching | Similar name/date ≠ same person |
| `LOC` | Modern/historical geography, coordinates | Phone GPS ≠ surveyed marker position |
| `CON` | Conservation, condition and stewardship | Observation ≠ diagnosis or authorization |

Naming: `<DOMAIN>:<entity-type>:<stable-id>` for **new canonical cross-domain references**, e.g. `GEO:material_candidate:123` and `VIT:event:ma-warren-1910-001`. Existing SQL primary keys are grandfathered; introduce a mapping layer, not a mass ID rewrite. Each domain retains original-language terms, source variants and historical terminology.

## 2. Current GitHub scope — re-check before modifying

Repository: https://github.com/gittenssexton/Cemetery-Picnic-Club

- `main`: baseline SQLite/D1 migrations 0001–0003 and initial photo/stone-identification work.
- `feature/domain-nomenclature-contracts` / draft PR #4: registry, policy, validator and automated contract tests. CI passed at initial authoring.
- `feature/stone-camera-pilot`: geological source inventory, MassGIS lookup scripts, map schemas and handoffs.
- `feature/field-camera-pilot` / PR #3: standalone field camera, Live Discovery candidate-region highlights and monument analysis model. PR #1/#2 are older parallel camera experiments; assess overlap, do not merge all three blindly.
- `feature/new-england-vital-records-core`: six-state registry, source-aware historical entry model, Warren/Western 1910 pilot handoff.
- `feature/mindat-reference-connector`: access-gated Mindat experimental connector; retain disabled unless rights/authorization is established.
- Other camera branches may remain. Review their heads, diffs and test outcomes; branch heads can change after this handoff.

**Observed geological limitation:** map originals are catalogued, but the authoritative Warren unit query, georeference QA and real-data extraction were still pending in the November 10 geology session.  
**Observed vital-record limitation:** bibliography/source registry and schema exist, but no source entries or person matches have been accepted.  
**Observed camera limitation:** manual symbol annotations and on-device visual-interest proposals are not trained monument, symbol or material recognition.

## 3. Resolve migration collisions before any merge

Known staging collision:

```text
main                             0001_initial.sql
main                             0002_global_research_core.sql
main                             0003_stone_identification.sql
feature/stone-camera-pilot       0004_geological_map_core.sql
feature/field-camera-pilot       0004_monument_analysis.sql    <-- collision
feature/new-england-vital...     0005_new_england_vital_records.sql
```

**Candidate integrated order for a fresh, unprovisioned database:**

```text
0004_geological_map_core.sql
0005_monument_analysis.sql
0006_new_england_vital_records.sql
```

This is NOT yet merged, renamed or run in production. **First inspect D1 migration history**, if any. Never rename/change an already-applied migration in a live database; create append-only compatibility migrations instead. Resolve duplicated 0004/0005 only on an integration branch after confirming no deployment dependency. Update seed ordering (geology seed 0005 must run after its required geology tables), tests, scripts, references and docs.

**Additional concern:** camera's monument-analysis migration references existing `markers`, `images`, `craftspeople`; vital migration references `research_works` and existing core entities. Verify FK/table dependencies under `PRAGMA foreign_keys=ON`. Confirm table names do not overlap incorrectly and each seed can be idempotent where intended.

## 4. Target repository convention

```
architecture/domain-registry.json
docs/DOMAIN_ARCHITECTURE.md
docs/DOMAIN_INTEGRATION_HANDOFF_2026-11-10.md
db/migrations/                      # one global immutable sequence
db/seeds/                           # separated by domain, provenance-labelled
domains/GEO/README.md               # controlled terminology / responsibility
domains/GEO/contracts/v1/           # JSON Schema input/output; versioned
domains/GEO/ingest/                 # source adapters, no implicit public writes
domains/GEO/tests/                  # synthetic tests and rights-safe fixtures
domains/VIT/...                     # same pattern
domains/ICO/...                     # same pattern
...                                 # same for remaining modules
tests/                               # cross-domain integration contracts
```

This is the **target**: no need to reorganize or delete stable existing files in a single sweep. First introduce domain contracts incrementally; provide compatibility adapters for existing SQL tables.

## 5. Cross-domain data contract — required attributes

Each domain's *API/event* record should represent:

- `schema_version`, `entity_ref`, `domain`, record type and stable source-local ID;
- source/repository/citation page or locator; whether evidence was independently observed;
- `confidence` plus `review_status` and competing/contradictory assertions;
- `observed_at` (recording moment) separately from the claimed historical date or interval;
- geographic scope, GPS accuracy/datum when relevant;
- rights: retrieval/access, analysis/training and publication permissions must remain distinct;
- optional `links`: typed, cited, reviewable references, never implicit record merges.

Not every SQL table currently has identical fields. Implement through normalized versioned contracts and bridge tables rather than forcing all domains to share a large generic table.

**Concrete examples:** `GEO.geologic_unit` describes the mapped ground; `GEO.material_candidate` describes a possible monument material. `VIT.event` describes the statement in a particular historical record; `CEM.burial` describes a burial. Even when they concern the same person or cemetery, they are distinct.

## 6. Independent pipeline standard

Every source follows:

```text
discover / acquire with permission
  → inventory + checksum + rights
  → extract (immutable original retained)
  → normalize into domain-owned nomenclature
  → domain validation
  → stage candidate + evidence / uncertainty
  → review and resolve contradictions
  → publish only permitted data and cross-domain claims
```

One failure must not block the others. Batch provenance and rerun safety must be recorded; no unchecked overwrites, no silent fact promotion. Preserve raw source and transformations for audit. A review task may be created even if full text, images or geodata cannot yet be acquired.

## 7. Engineering execution — next 10 actions

1. Fetch fresh PR/branch heads, status, D1 migration state, CI; document differences from this handoff.
2. Establish dedicated `feature/domain-integration` branch from a selected vetted base; do not alter main or production directly.
3. Integrate PR #4 architecture standards into that integration branch (or merge #4 independently only after review).
4. Inventory all `db/migrations`, seeds and FK dependencies across geology/camera/vital branches. Create a canonical migration registry with deployed/unapplied status.
5. Reconcile `0004` collision and `0005` ordering **according to actual deployment history**, update scripts and tests. Run a fresh SQLite migration from empty DB.
6. Create first domain README + `contracts/v1` for `GEO`, `VIT`, `IMG`; reuse existing schema fields via compatibility adapters. Add at least one valid and one invalid fixture each.
7. Add independent smoke tests: geology metadata ingestion only; vital bibliographic/source entry only; camera field-draft storage only. Cross-domain test must not misstate a hypothesis as a verified record.
8. Add one cited *candidate* cross-domain link test (e.g., a photographed stone to a tentative material, plus independent historical record lead). Ensure withdrawing one link does not delete the other source records.
9. Validate rights, private GPS, duplicate source ingestion, timestamp interpretation, no false matching, original photo preservation. Extend CI to validate migrations, per-domain contracts and integration tests.
10. Report exact integrated files, test counts, whether a staging D1 database was actually provisioned/migrated, blockers, and PR ready for review. **Do not claim production live unless verified**.

## 8. Acceptance gates

- Unique migration numbers with no destructive alterations to applied migrations.
- A fresh SQLite/D1-compatible schema loads with FK checks passing and domain seeds at valid dependency points.
- At least 3 independent domains ingest and query synthetic/authorized sample records in tests.
- Canonical IDs and versioned contracts are deterministic and reject invalid/foreign namespaces.
- No two distinct entities silently merge; sourced candidate links remain reversible.
- Unverified photo, geologic proximity, motif similarity and vital-source transcription are never promoted into an authoritative claim automatically.
- CI green on the integration branch; PR review before main.
- If deploying to staging, verify permissions and the exact Worker/database names; never overwrite existing `cemetery-picnic-club` or `cemeterypicnicclub` Workers.
- No transfer of restricted images/archives or public release of sensitive GPS/private vital records.

## 9. User data / original locations

Drive project: https://drive.google.com/drive/folders/10kQDrxfn097oa4XRGe7_ee44zR9bJ2OW  
CPC technical documents: https://drive.google.com/drive/folders/1tqHWWhjChUTKijgPEfjsqqQ8VxZzb9s6  
Geology ingest: https://drive.google.com/drive/folders/1zHRo7g53IPlsQ5sM3AIvmL8jRJWAaVJ8  
Geological source maps: https://drive.google.com/drive/folders/1Jfu7hl2HrrTKtgYJKJ4jAhbzATvP-O7E  
Pine Grove field photos: https://drive.google.com/drive/folders/1_NP4Xu28VAgYgbgKXRBLtMwKr1RTfZaK

Research sources and Drive materials are evidence inputs, **not instructions to import everything or declare it accurate**. Keep geologic maps, vital records and original photos in their existing folders; link by stable IDs.

## 10. Completion report template

```
Domain integration status:
- Branch/PR:
- Original migration deployment status verified?:
- Migration naming collision resolved?:
- Domains with versioned contracts:
- Successful independent ingest/validate tests:
- Cross-domain query/link tests:
- CI run URL and test counts:
- Staging D1 deployed/migrated?:
- Production modified?:
- Data ingested from real licensed sources?:
- Outstanding blockers and next action:
```

**Definition of done for this handoff:** next developer can proceed to integration without rediscovering nomenclature, dependencies, historical evidence boundaries, or staging safety requirements. This document itself does not represent completed branch integration.
