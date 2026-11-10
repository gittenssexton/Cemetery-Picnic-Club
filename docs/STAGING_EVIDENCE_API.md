# CPC internal evidence API — staging-only contract

Source: `server/cpc-integration-staging.mjs`.

This Worker has **not** been deployed by this integration branch. Its purpose is to expose authenticated, read-only candidate-link retrieval for engineering review. It is not a public cemetery search API.

Required bindings for a future isolated staging deployment:
- D1 binding `CPC_DB` pointing **only** to `cemetery-picnic-club-integration-staging`.
- Secret `CPC_API_TOKEN` stored with Cloudflare secrets management; minimum 32 characters. Never add tokens to Git or client-side code.
- Environment variable `CPC_ENVIRONMENT=staging` (mandatory; absent or any other value disables internal queries).
- Environment variable `CPC_ALLOWED_HOST` set to the exact staging Worker hostname (mandatory; a production or alternate hostname disables internal queries).
- A staging-only Worker name distinct from `cemetery-picnic-club`, `cemeterypicnicclub`, or CARTOVEYRA.

Routes:
- `GET /health`: liveness only, no database readiness claim and no content.
- `GET /internal/evidence-links?entity_ref=DOMAIN:type:id`: bearer-authenticated, parameterized SQL, returns up to 100 matching evidence links. **Contains internal citations/notes and must never be embedded directly in a public page.**
- `GET /internal/warren-ocr-review?page=9|10|11&status=requires_page_image_check`: bearer-authenticated, read-only, parameterized internal review queue. Status also supports `in_review`, `rejected`, `scan_checked`. At most 25 records/page; returns name as transcribed, original source classification, printed source code, checksum and review flag but **not** raw source JSON, private annotations, scans, or any public people/marker search. Response explicitly marks page coverage incomplete and requires review. It does **not** accept or approve candidates.
- Every other method or route is rejected. No uploads, publishing, record merges or writes. Browser `Origin` requests are rejected; the endpoint is only for approved server-side review clients.

Security gates before deployment:
1. Verify Cloudflare account, D1 binding ID, secret, and absence of any public route that can access private records.
2. Apply least-privilege Cloudflare service access; authorize users upstream rather than distributing one shared bearer token to browser clients.
3. Enable request authentication rate limits, audit logging with sensitive parameters redacted, explicit CORS policy and rotation plan.
4. Confirm disabled caching, restricted location metadata, and source-level rights checks. The helper's internal endpoint is not the public evidence release gate.
5. Test separately from production, validate field-camera exports and authorized real data, then review API responses for leaks.

Automated Node tests cover missing/wrong token, missing D1 binding, invalid references, SQL parameterization, method restrictions and expected read-only response. They do **not** establish a production-grade authentication system.

## Warren review-to-source-event gate (offline)

`scripts/review_warren_vitals.py` provides two Python helpers for an operator-controlled local SQLite workflow: `record_scan_review` records a named reviewer's exact line reading, HTTPS page locator, image sequence and image SHA-256; `accept_scan_reviewed_event` requires that confirmed review, the original candidate checksum, and a collection explicitly marked as `reviewed_source_entries` with `verified_public_domain` rights. It writes a **restricted** source event and an immutable acceptance lineage. No person, family, marker, burial, public rights grant or other identity assertion is made. No bulk accept, automated scan verification, public review endpoint or D1 promotion route is implemented.

The connected staging database's Warren collection remains `metadata_only`; there are **zero** `vital_ocr_page_reviews`, **zero** `vital_ocr_accepted_events`, and **zero** accepted `vital_record_entries` at the post-migration check. Historical OCR batch names and dates must not be described as verified.

## Actual Cloudflare setup check — 2026-11-10

The separate `cpc-integration-staging` Worker script was uploaded and automatically deployed as an isolated Cloudflare Worker. It is **not publicly reachable**: its `workers.dev` subdomain and preview URLs are both disabled.

Read-back of the actual Cloudflare Worker settings confirmed:
- `CPC_DB`: D1 binding `ad4a436d-048c-47a6-bd00-8cf1b9632f6b` (`cemetery-picnic-club-integration-staging`, **not** CARTOVEYRA).
- `CPC_ENVIRONMENT`: `staging`.
- `CPC_ALLOWED_HOST`: `cpc-integration-staging.gittens-sexton.workers.dev`.
- `CPC_API_TOKEN`: **not installed**. The attempted secret-write operation was blocked, so no token was created; do not assert otherwise.

**Remaining operator step:** In Cloudflare Dashboard → Workers & Pages → `cpc-integration-staging` → Settings → Variables and Secrets, add a securely generated, unique `CPC_API_TOKEN` as a **Secret** (at least 32 characters), never as plaintext or in GitHub. Prefer Cloudflare Access service authentication and credential rotation for internal callers. Only after secrets and access policies are verified should the operator enable the staging subdomain, execute unauthenticated/authenticated smoke tests and document the results. Do not use this service as a public API or grant browser clients the bearer token.

The Worker upload is not a production website deployment. Production workers, CARTOVEYRA resources, and `main` were not modified by this setup.
