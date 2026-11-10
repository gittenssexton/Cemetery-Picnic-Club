#!/usr/bin/env python3
"""CPC cemetery registry v0.1: ingest a saved OSM Overpass JSON response.

This produces candidates, not reviewed cemetery identities or surveyed boundaries.
Source geometry is never promoted to verified by this script. Google Maps data is
not an input. Route 9 geometry must come from a separate appropriately licensed
GeoJSON route line and is not guessed.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

PINE_GROVE_LAT, PINE_GROVE_LON = 42.20909, -72.19660  # approximate source centroid
RADIUS_M = 25 * 1609.344
CORRIDOR_M = 3 * 1609.344
EARTH_M = 6371008.8


def distance_m(lat1, lon1, lat2, lon2):
    a1, a2 = math.radians(lat1), math.radians(lat2)
    da = a2-a1
    dl = math.radians(lon2-lon1)
    a = math.sin(da/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dl/2)**2
    return 2*EARTH_M*math.asin(min(1, math.sqrt(a)))


def distance_to_route_m(lat, lon, route):
    if not route:
        return math.inf
    ref = math.radians(lat)
    x0 = EARTH_M*math.radians(lon)*math.cos(ref)
    y0 = EARTH_M*math.radians(lat)
    best = math.inf
    for line in route:
        for a,b in zip(line, line[1:]):
            ax,ay=EARTH_M*math.radians(a[0])*math.cos(ref), EARTH_M*math.radians(a[1])
            bx,by=EARTH_M*math.radians(b[0])*math.cos(ref), EARTH_M*math.radians(b[1])
            dx,dy=bx-ax,by-ay
            t=max(0,min(1,((x0-ax)*dx+(y0-ay)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
            best=min(best, math.hypot(x0-(ax+t*dx), y0-(ay+t*dy)))
    return best


def route_lines(geojson):
    if geojson is None:
        return []
    if geojson.get('type')=='FeatureCollection':
        parts=[f.get('geometry') for f in geojson.get('features', [])]
    elif geojson.get('type')=='Feature':
        parts=[geojson.get('geometry')]
    else:
        parts=[geojson]
    lines=[]
    for geometry in parts:
        if not geometry:continue
        kind=geometry.get('type'); coordinates=geometry.get('coordinates', [])
        if kind=='LineString': lines.append(coordinates)
        elif kind=='MultiLineString': lines.extend(coordinates)
    return [line for line in lines if len(line)>=2]


def valid_ring(ring):
    return (len(ring)>=4 and ring[0]==ring[-1] and
            all(len(p)>=2 and math.isfinite(p[0]) and math.isfinite(p[1]) and
                -180<=p[0]<=180 and -90<=p[1]<=90 for p in ring))


def centroid(element):
    if element.get('type')=='node':
        return element.get('lat'),element.get('lon')
    if element.get('center'):
        return element['center'].get('lat'),element['center'].get('lon')
    geom=element.get('geometry') or []
    if geom:
        return sum(p['lat'] for p in geom)/len(geom),sum(p['lon'] for p in geom)/len(geom)
    return None,None


def candidate(element, routes):
    tags=element.get('tags') or {}
    if tags.get('landuse')!='cemetery' and tags.get('amenity')!='grave_yard':
        return None
    lat,lon=centroid(element)
    if lat is None or lon is None or not(-90<=lat<=90 and -180<=lon<=180):
        return None
    radius=distance_m(PINE_GROVE_LAT,PINE_GROVE_LON,lat,lon)
    route=distance_to_route_m(lat,lon,routes)
    zones=[]
    if radius<=RADIUS_M:zones.append('pine_grove_25mi_radius')
    if route<=CORRIDOR_M:zones.append('route9_3mi_corridor')
    if not zones:return None
    source_type=element.get('type')
    geometry={'type':'Point','coordinates':[lon,lat]}
    status='mapped_point_or_centroid_unverified'
    if source_type=='way':
        coords=[[p['lon'],p['lat']] for p in element.get('geometry', [])]
        if valid_ring(coords):
            geometry={'type':'Polygon','coordinates':[coords]}
            status='osm_polygon_unreviewed'
    # Relation multipolygon member rings require correct assembly; never guess.
    osm_id=f"osm:{source_type}:{element.get('id')}"
    return {'id':osm_id,'name':tags.get('name') or None,
      'alternate_names':[v for key,v in tags.items() if key in ('alt_name','old_name','official_name','name:en') and v and v!=tags.get('name')],
      'entity_kind':'cemetery_candidate','geometry':geometry,'geometry_status':status,
      'reference_position':[lon,lat],'zones':zones,
      'distance_from_pine_grove_m':round(radius),
      'distance_to_route9_m':round(route) if math.isfinite(route) else None,
      'osm_tags':{k:v for k,v in tags.items() if k in ('name','landuse','amenity','religion','denomination','operator','start_date','historic','wikidata','website')},
      'source_id':osm_id,'source_url':f'https://www.openstreetmap.org/{source_type}/{element.get("id")}',
      'review_status':'unreviewed','verified_cemetery':False,
      'combined_complex_id':None,'relationship_review_status':'not_evaluated'}


def build(osm,route=None):
    lines=route_lines(route)
    records={}
    for element in osm.get('elements', []):
        if element.get('type') not in ('node','way','relation'):continue
        result=candidate(element, lines)
        if result:records[result['id']]=result
    return {'schema_version':'CPC_CEMETERY_CANDIDATES_V1',
      'scope':{'pine_grove_center_lat':PINE_GROVE_LAT,'pine_grove_center_lon':PINE_GROVE_LON,
               'radius_m':RADIUS_M,'route9_corridor_m':CORRIDOR_M,
               'route_geometry_provided':bool(lines)},
      'evidence_warning':'Unreviewed OSM candidate locations. Not a comprehensive cemetery inventory, surveyed boundaries, combined-ground assignments or grave coordinates.',
      'source':'OpenStreetMap contributors; ODbL; attribution and share-alike obligations apply',
      'count':len(records),'entities':sorted(records.values(),key=lambda r:(r['name'] or '',r['id']))}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--osm-json',type=Path,required=True)
    p.add_argument('--route9-geojson',type=Path,help='OSM-derived verified LineString/MultiLineString corridor path; do not use road guesses')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=build(json.loads(a.osm_json.read_text()),json.loads(a.route9_geojson.read_text()) if a.route9_geojson else None)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(f"Wrote {out['count']} unreviewed cemetery candidates to {a.output}")

if __name__=='__main__':main()