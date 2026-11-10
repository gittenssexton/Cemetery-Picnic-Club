#!/usr/bin/env python3
"""Reproducible nonproduction proximity review for mapped Massachusetts bedrock.

No coordinates or geologic boundaries are treated as surveyed on-site truth.
Requires geopandas, pyproj, shapely. Source polygons retain original map symbols.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import geopandas as gpd
from shapely.geometry import Point

RADII = [100, 250, 500, 1000, 1500]
MASSGIS = "https://www.mass.gov/info-details/massgis-data-bedrock-lithology"
USGS_SYMBOLS = "https://pubs.usgs.gov/of/2006/1272/documents/MAmetadata.htm"
USGS_BULLETIN = "https://ngmdb.usgs.gov/Geolex/resources/docs/USGS_B-1605-A_t.pdf"


def review(shp: Path, lat: float, lon: float):
    layer = gpd.read_file(shp)
    if layer.crs is None:
        raise ValueError("Source projection missing")
    for c in ["BEDROCK_1", "ROCK_GPB"]:
        if c not in layer:
            raise ValueError(f"Missing source attribute {c}")
    pt = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(layer.crs).iloc[0]
    matches = layer[layer.geometry.covers(pt)]
    if len(matches) != 1:
        raise ValueError(f"Expected one polygon covering reference point, found {len(matches)}")
    summaries = []
    for r in RADII:
        sub = layer[layer.geometry.intersects(pt.buffer(r))].copy()
        recs = []
        for _, row in sub.iterrows():
            recs.append({"symbol": str(row["BEDROCK_1"]), "lithogeochemical_group": str(row["ROCK_GPB"]),
                         "distance_to_boundary_m": round(float(row.geometry.boundary.distance(pt)), 2),
                         "reference_point_inside": bool(row.geometry.covers(pt))})
        recs.sort(key=lambda x: (x["distance_to_boundary_m"], x["symbol"]))
        summaries.append({"radius_m":r,"nearby_polygons":recs})
    return {
        "schema":"cpc-pine-grove-neighborhood-review-v1", "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_title":"MassGIS Bedrock Lithology, derived from USGS OFR 03-225",
        "source_url": MASSGIS,
        "source_shape_sha256":hashlib.sha256(shp.read_bytes()).hexdigest(),
        "source_crs":str(layer.crs), "number_of_polygons":len(layer),
        "site_reference":{"label":"Pine Grove Cemetery approximate centroid (not surveyed)","latitude":lat,"longitude":lon},
        "map_point_symbol":str(matches.iloc[0]["BEDROCK_1"]),
        "reviewed_symbol_dictionary":{
            "Ops":{"formation":"Partridge Formation", "unit_description":"typical sulfidic mica schist",
                   "symbol_evidence": [USGS_SYMBOLS, USGS_BULLETIN], "symbol_review":"publisher_cross_reference_verified"},
            "Dl":{"formation":"Littleton Formation", "unit_description":"pelitic metamorphic rock (source's lithogeochemical label)",
                  "symbol_evidence":[USGS_SYMBOLS, USGS_BULLETIN],"symbol_review":"publisher_cross_reference_verified"}
        },
        "spatial_accuracy_caveat":"Published estimated positional accuracy ~1500 m, vastly exceeding the polygon-boundary distance. Radii indicate polygon intersections, not probabilities or actual outcrops.",
        "site_assignment_status":"boundary_sensitive_unverified",
        "marker_material_or_quarry":"unknown; never derived from this map",
        "neighborhood":summaries
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--shape',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--latitude',type=float,default=42.20909)
    a.add_argument('--longitude',type=float,default=-72.1966)
    args=a.parse_args()
    obj=review(args.shape,args.latitude,args.longitude)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'point_symbol':obj['map_point_symbol'],'radii':[(x['radius_m'],[r['symbol'] for r in x['nearby_polygons']]) for x in obj['neighborhood']]},indent=2))
if __name__=='__main__':main()