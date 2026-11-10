#!/usr/bin/env python3
"""Query authoritative MassGIS bedrock polygons at CPC QA points.

Produces UNREVIEWED observations; never assigns quarry provenance or claims
site stone matches locally mapped bedrock. Standard library only.
"""
import argparse
import csv
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

SERVICE = "https://services.arcgis.com/2gdL2gxYNFY2TOUb/ArcGIS/rest/services/bedlith/FeatureServer/0/query"
SOURCE = "usgs-ofr-03-225-ne-lithology"
FIELDS = "BEDROCK_1,BEDROCK_2,LITHO_CODE,LITH_MOD,ROCK_GPA,ROCK_GPB,G_PROVINCE"
CAVEAT = "Generalized regional bedrock (~1.5 km spatial accuracy); not monument stone or quarry provenance."

def query_point(lat, lon, service=SERVICE, opener=urllib.request.urlopen):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Coordinates outside decimal-degree range")
    payload = {"f": "json", "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryPoint", "inSR": 4326, "spatialRel": "esriSpatialRelIntersects",
        "outFields": FIELDS, "returnGeometry": "false", "outSR": 4326}
    request = urllib.request.Request(service + "?" + urllib.parse.urlencode(payload),
        headers={"User-Agent": "CPC-geology-QA/1.0", "Accept": "application/json"})
    with opener(request, timeout=30) as response:
        data = json.load(response)
    if "error" in data:
        raise RuntimeError("ArcGIS error: " + str(data["error"]))
    features = data.get("features")
    if not isinstance(features, list):
        raise RuntimeError("Unexpected ArcGIS response: features absent")
    return [f.get("attributes", {}) for f in features]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--points", type=pathlib.Path, default=pathlib.Path("data/geology/qa_sample_points_ma.csv"))
    p.add_argument("--out", type=pathlib.Path, default=pathlib.Path("generated/geology/bedlith_point_qa.json"))
    p.add_argument("--service", default=SERVICE, help="Verified ArcGIS layer endpoint for QA")
    a = p.parse_args()
    if not a.service.startswith("https://"):
        p.error("Only HTTPS services are allowed")
    with a.points.open(newline="", encoding="utf-8") as f:
        points = list(csv.DictReader(f))
    if not points:
        p.error("No points")
    rows = []
    for point in points:
        lat, lon = float(point["latitude"]), float(point["longitude"])
        row = {"point_id": point["point_id"], "place": point["place"],
               "latitude": lat, "longitude": lon,
               "location_basis": point["location_basis"], "source_id": SOURCE,
               "service": a.service, "status": "unreviewed",
               "spatial_accuracy_note": "~1.5 km (MassGIS metadata)",
               "caveat": CAVEAT}
        try:
            matches = query_point(lat, lon, service=a.service)
            row.update(matches=matches, query_status="ok" if matches else "no_feature")
        except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
            row.update(matches=[], query_status="error", error=str(exc))
        rows.append(row)
        time.sleep(0.15)
    output = {"schema": "cpc-bedlith-point-qa-v1", "source": SOURCE,
              "source_url": "https://www.mass.gov/info-details/massgis-data-bedrock-lithology",
              "qa_status": "unreviewed", "points": rows}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {a.out}: {sum(r['query_status']=='ok' for r in rows)}/{len(rows)} point responses; manual legend review required")
    if any(r["query_status"] == "error" for r in rows):
        raise SystemExit("Some lookups failed; see output and retry before review")

if __name__ == "__main__":
    main()
