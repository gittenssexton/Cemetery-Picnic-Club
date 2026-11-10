# Regional geological maps — live pilot (2026-11-10)

This feature is staged on Cloudflare **cpc-stone-camera-preview**, not on the main Cemetery Picnic Club application.

## What is implemented
- Stone Camera Pilot offers optional browser GPS or manually entered decimal-degree coordinates.
- Explicit button queries `GET /api/geology?lat=...&lng=...` on its own Cloudflare Worker, which requests Macrostrat stable API v2 `/geologic_units/map`.
- Returned unit name, rock type, geologic age and original map source ID are displayed when supplied; calls are on-demand and no GPS/photo uploads are stored.
- A map link opens the Macrostrat geological map to inspect adjoining units.
- Macrostrat CC BY 4.0 acknowledgement and links to Massachusetts bedrock and surficial maps are in the UI.
- The JSON observation export includes the consulted geological map evidence, marked separately from tentative stone identification.

## Limits and follow-up checks
- Cloudflare confirmed the Worker code upload and enabled workers.dev address, but the complete third-party Macrostrat request and returned data have **not been independently validated** in a live browser.
- The 'Warren, Massachusetts example' coordinates are illustrative, **not** verified Pine Grove grave-marker coordinates.
- Bedrock below a cemetery is not evidence that a commercial or historical gravestone originated there.
- Massachusetts generalized bedrock data has ~1.5 km estimated spatial accuracy. Check 1:24,000 surficial map before interpreting local glacial surface deposits.
- No automatic image classification yet; users still describe rock features.
- No Mindat access; it remains disabled pending permission.

## Sources
- https://macrostrat.org/api/v2/geologic_units/map (stable v2 endpoint)
- https://dev.macrostrat.org/docs/data-services
- https://www.mass.gov/info-details/massgis-data-bedrock-lithology
- https://www.mass.gov/info-details/massgis-data-usgs-124000-surficial-geology
