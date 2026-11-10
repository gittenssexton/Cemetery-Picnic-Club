# CPC Field Camera acceptance checklist

**State:** Not yet physically verified on an iPhone. This file is a field acceptance protocol, not a claim that device tests passed.

## Before field work
Use the isolated camera build from `feature/domain-integration/web/camera/` on an HTTPS preview separate from production. Never point it at the CARTOVEYRA database. Field records stay in local IndexedDB until the operator explicitly exports them. Back up exports promptly.

## Required device scenarios
1. iPhone Safari, HTTPS, rear camera permission: verify capture, orientation and dimensions.
2. Precise location allowed: record GPS fix, uncertainty and date; distinguish **phone** position from surveyed plot coordinates.
3. Precise location denied or unavailable: confirm explicit no-GPS capture works; no fabricated coordinates in export.
4. Manual coordinates: verify they are identified as manually entered and remain unverified unless backed by surveying.
5. Full-frame original: hash the original JPEG inside the ZIP and compare to the captured browser JPEG; derivatives must differ only as intended. The camera records browser-created JPEG frames, not a native Apple HEIC file.
6. Stone contour proposal: test at least three **different markers** in diffuse light, shadows and clutter; review every outline against the original. Reject contamination rather than accepting uncertain segmentation.
7. A gravestone with illegible inscription: ensure it does not generate fabricated names or dates.
8. ZIP export: run `python3 scripts/validate_camera_export.py path/to/CPC-export.zip`, inspect archive integrity and independently verify EXIF GPS on the geotagged **copy**.
9. Local storage: reload Safari, resume prior record, export, then test deletion only after confirming external backup.
10. Privacy: deny publication rights, verify restricted GPS and other metadata never appear on public routes; no automatic upload.

## Acceptance conditions
- No duplicate, missing or altered original images in exports.
- Coordinates remain labeled by origin and uncertainty; missing GPS remains missing.
- Region proposals are explicitly experimental; no unreviewed attribution or recognition.
- No third-party copyrighted archive images used without permission.
- Results documented with device/iOS/Safari version, representative test identifiers, photos retained privately, failure cases and reviewer.
- Do not merge, deploy or turn on a public evidence API solely on the strength of unit tests.

## Completed automated checks
- Python ZIP validation covers duplicate/unsafe entries, metadata/version consistency, original JPEG signature, location-state validity and privacy-preserving audit summary.
- Node test executes the EXIF appender for four coordinate examples and checks original JPEG bytes are not mutated.
- These checks are **not equivalent** to device testing, ZIP review of real captures, or authorization of data publication.
