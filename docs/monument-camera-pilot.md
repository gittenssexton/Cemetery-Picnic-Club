# Monument Camera pilot

Standalone phone field capture is available at `web/camera/index.html` on the feature branch. It does not replace the main cemetery website or existing `web/stone-id.html`.

## First-use steps

1. Serve it over HTTPS, allow Safari camera access, and separately opt in to Precise Location.
2. Frame the gravestone inside the guide, then capture.
3. Export the original image, masked derivative, and companion JSON record, saving all three files together.
4. Verify marker ID and position against cemetery evidence; phone GPS refers to the photographer, not necessarily the stone.

## Privacy and source controls

No remote photo upload, location tracking, or server-side storage is implemented. All records are in browser memory until files are exported. Browser-created JPEGs are not original native Apple HEIC captures. The focus mask is rectangular and manually adjustable; automatic object segmentation, LiDAR, stone classification, GPS-to-marker correction, OCR, security review, and offline retention are future features. Do not label background masking as verified reconstruction or use it to alter original evidence.

## Production integration

Keep the camera as a separate route, linked from the field research navigation only after mobile Safari testing. Preserve the original photo as immutable evidence; data model should distinguish device position from marker coordinates and include accuracies, consent and review statuses. The existing site and data API remain unchanged by this branch.
