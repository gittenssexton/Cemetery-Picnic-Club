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
- Every other method or route is rejected. No uploads, publishing, record merges or writes. Browser `Origin` requests are rejected; the endpoint is only for approved server-side review clients.

Security gates before deployment:
1. Verify Cloudflare account, D1 binding ID, secret, and absence of any public route that can access private records.
2. Apply least-privilege Cloudflare service access; authorize users upstream rather than distributing one shared bearer token to browser clients.
3. Enable request authentication rate limits, audit logging with sensitive parameters redacted, explicit CORS policy and rotation plan.
4. Confirm disabled caching, restricted location metadata, and source-level rights checks. The helper's internal endpoint is not the public evidence release gate.
5. Test separately from production, validate field-camera exports and authorized real data, then review API responses for leaks.

Automated Node tests cover missing/wrong token, missing D1 binding, invalid references, SQL parameterization, method restrictions and expected read-only response. They do **not** establish a production-grade authentication system.
