# CPC Camera v0.8 — Direct Google Drive per-file sync checkpoint
Date: 2026-11-10
Owner: camera workstream, `feature/field-camera-pilot`, draft PR #3
Preview: https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/

## Scope and actual implementation
Camera captures remain saved **locally in IndexedDB first**. Optional Google Drive upload now sends two individual files per camera record: `CPC-<record-id>-original.jpg` and `CPC-<record-id>-record.json`, not a ZIP. JSON contains original observation metadata and a Drive file ID linking the matching JPEG; private GPS and notes may be present. Do not share/upload these folders publicly.

`web/camera/drive-sync.js` adds browser Google Identity Services (GIS) token auth, limited Google OAuth `drive.file` scope, an app-created `Cemetery Picnic Club - Camera Uploads` Google Drive folder, per-record upload statuses (`pending`, `partial`, `uploaded`) in the local record, photo-first and JSON-second HTTP multipart uploads, and retry of incomplete records while the app is online, foregrounded and authorized. Tokens stay in memory; the nonsecret OAuth public client ID, enabled flag and folder ID persist in localStorage. No hardcoded credentials, tokens or refresh tokens are committed.

`web/camera/index.html` now has explicit Google Drive instructions, OAuth client-ID entry, Connect Google Drive, opt-in auto-upload and Upload pending records now, plus per-record Drive status. ZIP exports remain available as optional research archives. Local camera captures queue Drive upload only after their IndexedDB write succeeded. Changes after capture use transactional merged persistence to avoid overwriting sync markers.

`web/camera/sw.js` cache bumped to 0.8.0 and includes `drive-sync.js`.

`tests/test_camera_drive_sync.js` mocks Google sign-in, folder creation and two-file uploads and checks that a completed record is not reuploaded. CI workflow updated. Independent connector-JS mock assertions passed 8/8, and browser source parsed. Cloudflare Worker upload returned success, and published source readback verified module/UI/offline cache presence.

## Integration gates / limitations
1. The camera **has not yet been authorized to any Google account**. Requires a Google Cloud project with Drive API enabled, OAuth consent screen and Web application OAuth client ID. Add exact preview origin `https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev` to allowed JavaScript origins, then enter public client ID in camera and choose Connect.
2. Google OAuth login requires explicit user action. Access tokens expire. Browser-only code cannot guarantee authorization or upload while app is closed; reopening/reconnecting will resume pending work. A production backend with secure refresh-token handling would be required for truly unattended persistent synchronization.
3. `drive.file` permission intentionally creates its **own folder** in user's My Drive. It does not automatically gain access to the user's preexisting shared Cemetery Picnic Club project folder; integrating with that folder needs explicit picker-based access or other scoped authorization design.
4. Uploaded JSON is a **private research record** potentially containing GPS and notes, not the separately reviewed shareable/export record. Google account and folder permissions govern its security. No manual public sharing is performed.
5. Google OAuth origin verification, iPhone Safari authorization, actual Drive API upload/retry and physical-device behavior have not been field tested. JavaScript mocks do not prove real Google uploads.
6. Large-photo multipart uploads may time out on weak connections; a future upgrade should use Google Drive resumable upload sessions. Current code retries whole incomplete photo, and retains local original.
7. Existing camera preview and PR remain draft; main production/D1 not changed.

## Next QA
- Create OAuth web client and enable Drive API in Google Cloud; use exact preview origin. Authorize as a Google test user if OAuth consent is in Testing.
- Capture an overview/inscription and observe private JPEG and JSON files in `Cemetery Picnic Club - Camera Uploads` in the connected Drive.
- Disable cellular mid-upload, reconnect, and verify pending state and no duplicate completed records.
- Open JSON and verify photo ID, annotations, location privacy and absence of embedded image binary.
- Decide whether to route directly into an existing Cemetery Picnic Club folder via Google Picker in the next iteration, without requesting unrestricted Drive access.
- Reconcile central D1/R2 production integration separately; Google Drive is an interim archival destination, not the authoritative production database.
