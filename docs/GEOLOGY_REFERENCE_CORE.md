# CPC Geological Reference Core — Stage 1 (2026-11-10)

The independent stone camera pilot remains a photo preview + human-guided material comparison. **It does not yet identify rock types from image pixels.** No external API or photos are bundled. This stage records vetted source entry points and provenance policies.

## First reference sources

- **USGS:** Public-domain agency-authored data/reports, with attribution. Inspect each specimen photograph for third-party copyright before reuse. https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted
- **MassGIS Bedrock Lithology:** Polygon data for Massachusetts grouped by lithogeochemical rock class. Its coarse compilation is suitable for **regional context only**; estimated spatial accuracy ~1.5 km. https://www.mass.gov/info-details/massgis-data-bedrock-lithology
- **Massachusetts Geological Survey:** Bedrock geologic map, contextual historical geology. https://www.umass.edu/geological-survey/resources/bedrock-geologic-map-massachusetts
- **Macrostrat:** Public geological API under CC BY 4.0. Suitable to query a map unit at a user-provided location once request paths and attribution are tested. https://dev.macrostrat.org/docs/data-services
- **USGS MRDS:** Historical mine/deposit record reference; *not* proof of gravestone sourcing. https://www.usgs.gov/publications/mineral-resources-data-system-mrds

## Evidence rules

- Three separate claims: photographed marker material; geology at *observation site*; possible *historical quarry origin*. Never infer one from another.
- Never infer a quarry from current GPS alone; traded stone may travel hundreds or thousands of miles.
- Image recognition must run independently from Mindat until relevant written permission is granted.
- Label hypotheses; record source URL, dataset version, rights, review state, confidence methodology.
- Record GPS precision; avoid public coordinates of vulnerable or sensitive grave sites.
- External geology APIs are not part of this initial offline-friendly prototype.

## Next implementation

1. Assemble a small vetted photo library of granite, marble, slate, brownstone/sandstone, limestone, gneiss, schist and manufactured markers using photos we own or independently verified rights.
2. Link user-observed traits to the source registry and research record.
3. Validate the camera UI on iPhone and Android; then create a separate Cloudflare preview deployment.
4. Add independent pixel-based classifier and measure performance on labeled photos; abstain when ambiguous.
5. Add location-based Macrostrat lookup with provenance and attribution, clearly separating observation geology from candidate quarry.
6. Attach independently verified historic quarry records to material source candidates.
7. Keep Mindat disabled until approval.

Source registry: `data/geology-reference-sources.json`.
