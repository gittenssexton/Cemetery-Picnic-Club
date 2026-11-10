# Cemetery Picnic Club — Field Camera pilot

Standalone, mobile-first field camera under `web/camera/`, separate from the existing landing page and stone identification app.

## Pilot capabilities
- Request camera and high-accuracy location permission over HTTPS; display reported accuracy.
- Require a location attempt before capturing, with explicit no-GPS/manual-coordinate paths.
- Live rectangular focus guide; manually refine four corners after capture for a clean derivative image.
- Save original captured JPEG separately from processed derivatives and preserve provenance.
- Store field records locally in IndexedDB and export per-record ZIP archives including JSON and original/isolated images; geotagged exported JPEG when coordinates exist.
- No cloud upload or automated monument segmentation/recognition yet.

## Test
Deploy the contents of `web/` to a secure origin. Open `/camera/` in Safari on an iPhone; allow camera and precise location, capture and export a test record, and inspect the ZIP. Browser storage is **not** a permanent backup—export after each record.

The live Cloudflare sandbox preview is a separate Worker: `cemetery-picnic-camera-preview`. This branch does not modify the existing `cemetery-picnic-club` Worker or its main website.

## Limitations
Position is the phone's GPS position, not a verified monument plot coordinate; depth/AI segmentation and true object silhouettes are future work. Camera output is a browser JPEG, not the original Apple Camera app HEIC. Some permissions and features vary by browser. Keep original and derivative files distinct, avoid inventing inscriptions, and do not publish precise locations for sensitive sites without review.
