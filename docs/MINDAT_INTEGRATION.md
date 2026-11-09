# Mindat reference integration — isolated prototype

This branch adds an **optional**, **disabled-by-default** Cloudflare Worker to search Mindat geomaterial names for *manual research review*. It does NOT identify rocks from images, infer quarry provenance, import data into the CPC database, train AI, or process Mindat photographs.

## Legal/usage gate
Mindat's terms (effective 2026-08-21) require prior written authorization for AI/ML training, evaluation, testing, grounding and systematic AI knowledge uses. Its documented API carries CC BY-NC-SA 4.0 conditions; third-party photos require separate permission. Check whether a public-facing CPC application and proposed lookups are allowed *before enabling*. Sources:
- https://www.mindat.org/terms.php
- https://www.mindat.org/a/how_to_get_my_mindat_api_key
- https://api.mindat.org/v1/schema/redoc/

## Security and setup
1. Revoke and regenerate the Mindat token previously disclosed in chat.
2. Deploy `workers/mindat-reference.js` as an isolated Worker (do not change the existing CPC Worker or production app).
3. Configure encrypted Worker secrets `MINDAT_API_TOKEN` and `CPC_REFERENCE_ACCESS_TOKEN` in Cloudflare's dashboard. Do **not** paste them into GitHub, client-side JavaScript, Drive docs, or chat. Use a separate strong random CPC access token.
4. Keep `MINDAT_LOOKUP_ENABLED` unset or `false` until permissions are verified. Setting it to `true` enables authenticated requests, only when legal clearance is obtained.
5. GET `/health` reports configuration flags but never reveals tokens.
6. Once approved, test GET `/api/reference/mindat/search?q=quartz` with header `Authorization: Bearer <CPC_REFERENCE_ACCESS_TOKEN>`.

Security boundaries: server-side token only; access-controlled lookup; limited search size; no third-party photos; no bulk extraction; no persistence. Before opening this to app users, add proper user authentication and rate limiting. Never embed the CPC access token in publicly served web code.

## Future architecture
Keep first-party camera/stone classification separate from Mindat. Store direct links and provenance in the CPC evidence layer only under the terms of an approved license; do not silently treat mineral localities as historic quarry provenance.
