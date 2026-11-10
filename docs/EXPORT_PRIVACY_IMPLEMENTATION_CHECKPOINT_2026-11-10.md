# Camera export privacy implementation checkpoint — 2026-11-10

**Owner:** Cemetery Picnic Club camera-development workstream (this conversation).
**Canonical:** GitHub PR #3, branch `feature/field-camera-pilot`.
**State:** Implemented in experimental preview, NOT merged to main, NOT deployed to production. Private/archive and shareable packages require iPhone and independent ZIP validation.

## Implemented camera work
- `web/camera/export-privacy.js`: independent allowlisted public record schema `CPC_SHAREABLE_RECORD_V1`. No copying of private record JSON; generates an unrelated public export ID. Rejects location-related keys and common pasted decimal coordinate pairs.
- `web/camera/index.html`: separate **Export private research ZIP** and **Create shareable ZIP** options; separate confirmation panel. All public fields and photograph OFF by default. Optional approved image is re-encoded from decoded photo pixels as a new JPEG, rather than exporting the original or GPS-tagged JPEG. Optional inscription, material/form and cemetery name require individual opt-in. Text/site/image can still reveal the location even without EXIF; the UI warns.
- Private ZIP retains the existing complete record and optional per-record geotagged JPEG (off by default); filename now ends `-private.zip`. Adds `CPC_PRIVATE_ARCHIVE_V1` labeling and `integrity-manifest.json` containing SHA-256, sizes and paths for the included files (excluding manifest itself). **Private archive has exact GPS in record.json; not safe to share.**
- `web/camera/sw.js`: version `cpc-field-camera-0.6.0`, precaches privacy helper.
- `tests/test_camera_export_privacy.js`: Node executable regression test for public allowlist and sensitive coordinate removal. **Authored, not yet executed in CI**.
- Cloudflare preview Worker `cemetery-picnic-camera-preview` updated and readback confirms the v0.6 UI, privacy helper and integrity manifest logic. Main production Workers untouched.

## Current validation
- Source-level inspections confirmed separate UI controls, explicit confirmation, no private record spreading in the public serializer, canvas JPEG re-encode for public photo, disabled public fields by default, GPS-preserving private archive and offline helper cache.
- Cloudflare Worker deployment returned success; source readback confirmed v0.6 changes.
- **Not yet validated:** actual iPhone Safari end-to-end downloads, generated ZIP inspection, byte-level image EXIF parser, browser storage and cache upgrade behavior, test run, cross-platform import or rights approval.
- No D1/R2 access controls or server upload endpoints added. No automatic publication or sync.

## Tasks before marking ready
1. Run `node tests/test_camera_export_privacy.js` and existing camera GPS/relationship test suites; fix failures.
2. Exercise actual private and shareable ZIPs with synthetic coordinates and image evidence; check all JSON, filenames, JPEG EXIF/XMP and original image hashes.
3. Physically capture and save both exports on iPhone; independently inspect ZIPs after downloading from Files.
4. Test old v0.1-v0.5 archive compatibility, no GPS/no camera, optional geotagged JPEG and refusal/cancel review flows.
5. Add rights/audience authorization with backend controls for any eventual published/private D1/R2 records.
6. Coordinate with domain-integration workstream on IMG/LOC/CEM contracts and migration collisions before merging.

## Coordination
The camera workstream owns `web/camera/`, camera export helper, and the camera privacy test. Main project owns overall access policy, D1/R2 integration and release review. Other agents should consume this checkpoint and PR #3 **before editing**; never assume Drive snapshot is current. Use GitHub commit/readback for progress across conversations.

**Preview:** https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/
**Handoff:** docs/CPC_CAMERA_PRIVATE_PUBLIC_EXPORT_HANDOFF_2026-11-10.md

## Validation continuation — camera sub-workstream, 2026-11-10

- Executed public allowlist helper dynamically against the committed source in a JavaScript tool runtime: **20/20 checks passed**, covering review requirement, removal of private marker ID, GPS coordinates, private notes and original reference, opt-ins and rejection of manually pasted decimal coordinate pairs.
- Exercised the **actual `packageZIP()` implementation** extracted from the committed camera HTML using a synthetic public JSON record and a four-byte mock JPEG payload. Parsed the two local entries and checked the ZIP central directory and that private test tokens were absent. **Passed**. This does **not** validate actual browser JPEG re-encoding, EXIF removal or iPhone downloads.
- Inspected a separate real historical v0.1 ZIP available in the development runtime with Python `zipfile.testzip()`: no CRC errors, but that archive predates v0.6 and includes a GPS-tagged JPEG. It is **not** a test of either new export profile.
- Committed `tests/test_camera_export_archive.js`, a Node regression that extracts the actual ZIP writer and checks synthetic public content; **not yet executed through GitHub CI**. `tests/test_camera_export_privacy.js` remains available.
- Device testing still required for actual private and shareable v0.6 exports, JPEG EXIF/XMP metadata audit, SHA-256 manifest verification, and iPhone Safari Files round-trip.
- **Ownership remains camera workstream; no production or D1 database change.**
