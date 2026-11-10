#!/usr/bin/env python3
"""Acquire MHC public Burial Ground points as unreviewed CPC source candidates.

No archaeological/non-public records, no guessed cemetery polygons, and no
automatic merging with OSM records. Requires network access when run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

SERVICE = ("https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/"
           "services/MHC_Inventory_GDB/FeatureServer/0/query")
PINE_GROVE = (42.20909, -72.19660)
RADIUS_M = 25 * 1609.344
EARTH_M = 6371008.8


def haversine_m(lat1, lon1, lat2, lon2):
    a = math.sin(math.radians(lat2 - lat1) / 2) ** 2
    a += (math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
          * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_M * math.asin(min(1, math.sqrt(a)))


def request_json(params):
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "User-Agent": "CemeteryPicnicClub-registry-research/0.1",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=75) as response:
        raw = response.read()
    parsed = json.loads(raw)
    if "error" in parsed:
        raise RuntimeError(f"ArcGIS returned error: {parsed['error']}")
    return parsed, hashlib.sha256(raw).hexdigest()


def acquire(page_size=1000):
    """Page over public burial ground points; return raw pages and hashes."""
    if page_size < 1 or page_size > 2000:
        raise ValueError("page_size must be between 1 and 2000")
    # Approximate *overinclusive* bounding envelope for the radius.
    # Final Zone A membership is tested geodesically below.
    where = "TYPE = 'Burial Ground'"
    envelope = "-72.75,41.83,-71.64,42.59"
    base = {
        "f": "json", "where": where, "geometry": envelope,
        "geometryType": "esriGeometryEnvelope", "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects", "outSR": 4326,
        "outFields": "MHCN,TYPE,COMMON_NAM,TOWN_NAME,ADDRESS,DEMOLISHED,OBJECTID",
        "returnGeometry": "true", "orderByFields": "OBJECTID ASC",
    }
    pages, seen = [], set()
    offset = 0
    while True:
        payload, digest = request_json({
            **base, "resultOffset": offset, "resultRecordCount": page_size
        })
        features = payload.get("features", [])
        if not isinstance(features, list):
            raise ValueError("Missing features array in ArcGIS response")
        pages.append({"offset": offset, "sha256": digest, "payload": payload})
        if not features:
            break
        for feature in features:
            key = feature.get("attributes", {}).get("OBJECTID")
            if key is None or key in seen:
                raise ValueError("Missing or repeated OBJECTID during pagination")
            seen.add(key)
        offset += len(features)
        if not payload.get("exceededTransferLimit", False) and len(features) < page_size:
            break
        if len(pages) > 10000:
            raise RuntimeError("Unexpected excessive pagination")
    return pages


def candidates_from_pages(pages):
    candidates, rejected = [], 0
    for page in pages:
        for f in page["payload"].get("features", []):
            a, g = f.get("attributes") or {}, f.get("geometry") or {}
            if a.get("TYPE") != "Burial Ground":
                continue
            lat, lon = g.get("y"), g.get("x")
            if not isinstance(lat, (float, int)) or not isinstance(lon, (float, int)):
                rejected += 1
                continue
            if not -90 <= lat <= 90 or not -180 <= lon <= 180:
                rejected += 1
                continue
            if haversine_m(PINE_GROVE[0], PINE_GROVE[1], lat, lon) > RADIUS_M:
                continue
            source_id = a.get("MHCN")
            if not source_id:
                rejected += 1
                continue
            candidates.append({
                "source": "MA_MHC_MACRIS_PUBLIC_INVENTORY",
                "source_id": source_id,
                "source_url": "https://mhc-macris.net/",
                "type": "historical_burial_ground_candidate",
                "name": a.get("COMMON_NAM"),
                "town": a.get("TOWN_NAME"),
                "address": a.get("ADDRESS"),
                "demolished_source_flag": a.get("DEMOLISHED"),
                "latitude": lat,
                "longitude": lon,
                "geometry_quality": "mhc_inventory_point_unreviewed",
                "zone_a": True,
                "zone_b": None,
                "zone_b_unassessed_reason": "reviewed Route 9 centerline not provided",
                "review_status": "unreviewed",
                "canonical_cemetery_id": None,
            })
    candidates.sort(key=lambda x: str(x["source_id"]))
    return candidates, rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=1000)
    args = parser.parse_args()
    pages = acquire(args.page_size)
    candidates, rejected = candidates_from_pages(pages)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    raw = {
        "source": SERVICE, "retrieved_utc": stamp, "pages": pages,
        "license_review_required": True,
    }
    result = {
        "schema": "CPC_MHC_BURIAL_GROUND_CANDIDATES_V1",
        "retrieved_utc": stamp, "source": SERVICE,
        "coverage": "Zone A only: 25-mile circle around approximate Pine Grove point",
        "route_geometry_provided": False,
        "review_status": "unreviewed",
        "count": len(candidates), "rejected_missing_geometry_or_id": rejected,
        "candidates": candidates,
    }
    for path, data in [(args.raw_output, raw), (args.output, result)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"MHC candidates in Zone A: {len(candidates)}; rejected: {rejected}")


if __name__ == "__main__":
    main()
