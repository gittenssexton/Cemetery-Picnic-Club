# Cemetery Picnic Club — Combined Public Pilot Preview (2026-11-10)

## Deployment
A separate Cloudflare Worker, `cpc-combined-pilot-preview`, was uploaded successfully with the contents of the `feature/domain-integration` branch at deployment time. Its public `workers.dev` subdomain was enabled:
https://cpc-combined-pilot-preview.gittens-sexton.workers.dev/

**This is not a production deployment** and is separate from the restricted `cpc-integration-staging` evidence Worker and the `cemetery-picnic-club-integration-staging` D1. No D1 bindings, data writes, secrets or Mindat token are present in the combined public pilot Worker.

## Pages
- `/` — field notebook links to all three research tools.
- `/camera/` — field camera; captures and exports photo originals/derivatives in local browser storage, no cloud photo upload.
- `/stone-camera.html` — non-invasive photo preview, human-selected traits, provisional material ranking and optional Macrostrat `/api/geology?lat=&lng=` lookup.
- `/research/vital-records.html` — source discovery and external archival search links for six New England states; **does not expose** staged Warren OCR candidates.
- `/stone-id.html` — baseline material field guide.

All pages and supporting camera scripts/manifests/icons/service workers are bundled into the isolated Worker, without a runtime dependency on raw GitHub content. Geology lookup is on-demand; coordinates go to Macrostrat through the Worker, with no storage code. No API is exposed for vital-record candidates or private evidence.

## Accuracy and limitations
- Photo selection is **not automated visual stone recognition**; materials are scored from human observations.
- Mapped geology at the phone site is **not** confirmation of gravestone material or quarry.
- The Pine Grove example and USGS/MassGIS historical symbols are reference context, not verified local rock at a specific grave.
- Mindat remains inactive and is not used.
- The external archive search submits only the visitor's typed query when they follow a link, not camera images or GPS.
- Phone camera capture, image original persistence, ZIP export and device GPS still require real iPhone/Android field acceptance.
- Cloudflare accepted the Worker upload and enabled its subdomain, but the public HTTP URL and Macrostrat round-trip **could not be independently loaded by the current external checker**. Mark runtime browser verification pending.
- This snapshot is manually uploaded. **Subsequent GitHub changes do not automatically publish.** Redeploy only after tests and explicit release control.

## Acceptance checklist
1. Load root, camera, stone identifier and research pages over HTTPS.
2. Confirm camera permission/no-permission flows, local drafts and export ZIP on phone; verify originals remain intact.
3. Open stone page, capture/select stone image; record traits, view ranked suggestions and export JSON.
4. Choose Warren example, run Macrostrat lookup; check result and error handling.
5. Confirm the public pilot has no D1, CPC_API_TOKEN, or Mindat access; do not disclose Warren OCR candidate records.
6. Record findings under this pilot and maintain PR #5 as draft pending full test evidence and production rollback plan.

## Branch integration
Committed `web/stone-camera.html` into `feature/domain-integration`, wired camera and main notebook to it, and introduced `tests/test_combined_pilot.py`. This is code-level pilot integration; **PR #5 has not been merged into main**.
