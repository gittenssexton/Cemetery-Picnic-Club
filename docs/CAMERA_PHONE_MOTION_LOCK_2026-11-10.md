# Camera v0.9.4 — Phone motion-assisted gravestone locking
Date: 2026-11-10
Branch: feature/field-camera-pilot
Preview: https://cemetery-picnic-camera-preview.gittens-sexton.workers.dev/

## Shipped
- `motion-lock.js`: optional on-device access to phone DeviceOrientation and DeviceMotion sensor readings, with one-tap permission control, no credentials, sensor data kept ephemeral, and no raw sensor trail uploaded.
- Angular wraparound correctly handled for orientation axes (359° → 1° = 2°, not 358°); classify steady, moving or rapid rotation by short rolling readings. Missing/stale sensor readings fall back to `unknown`.
- `pixel-contours.js`: contour tracking uses stricter multi-frame matching during motion; 2 frames steady, 3 moving, 4 rapid. No synthetic shifted contours.
- `discovery.js`: greenlighting internal letter/carving interpretations pauses during rapid phone rotation; UI reports camera motion and visual lock status. Camera-only tracking operates without sensor permission.
- Camera interface: `Enable phone motion assist` button requests platform permission from an explicit user gesture. Offline service worker bumped to v0.9.4.
- Synthetic checks of permission, wraparound, steady/moving/rapid states and stricter visual persistence; source JS parsed, Cloudflare deploy and readback verified.

## What this does NOT do
The gyroscope by itself does not yield distance, scale, stone thickness, world pose, a 3D model or perspective-correct image projection. The current module increases tracking confidence through motion-aware frame validation, not true motion-compensated AR tracking. That requires calibrated camera intrinsics, visual keypoints/homography, perhaps LiDAR or ARKit/ARCore via an eligible native or AR-capable integration, and validation against real stones.

## Next checks in a cemetery
1. On compatible iPhone, press Enable phone motion assist and grant permission.
2. Hold the phone steady on one stone, then pan slowly, then rotate abruptly; compare outline persistence and whether yellow pseudo-letter fills pause during fast motion.
3. Repeat denying permission and on devices with no sensors; camera-only path must work.
4. Check that simply moving the phone sideways with little rotation can still cause drift; inertial orientation alone cannot measure translation.
5. Use several stones at different distances, angles, and partial occlusion, with no names or 3D geometry asserted until visual confirmation.

Reference: https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static
