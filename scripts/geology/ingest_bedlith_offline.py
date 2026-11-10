#!/usr/bin/env python3
"""CPC Massachusetts bedrock: source-preserving, *unreviewed* offline ingest.

Input is the authoritative MassGIS BEDROCKLITHOLOGY_POLY shapefile ZIP (or
shapefile directory), not the Zen 1983 raster. Output is JSON suitable for
manual review and *never* represents quarry provenance or reviewed units.

Usage:
 python scripts/geology/ingest_bedlith_offline.py --vector bedlith.zip \
    --points data/geology/qa_sample_points_ma.csv --out generated/geology/bedlith
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

SOURCE_ID = 'usgs-ofr-03-225-ne-lithology'
SOURCE_URL = 'https://www.mass.gov/info-details/massgis-data-bedrock-lithology'
CAVEAT = ('Mapped bedrock is generalized (MassGIS estimated 1.5 km positional accuracy); '
          'it does not identify the material or quarry of a monument.')
FIELDS = ('BEDROCK_1','BEDROCK_2','LITHO_CODE','LITH_MOD','ROCK_GPA','ROCK_GPB','G_PROVINCE')


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def open_vector(path):
    """Return Fiona collection; reject missing shapefile sidecars and CRS."""
    import fiona
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == '.zip':
        with ZipFile(path) as z:
            names = z.namelist()
            if z.testzip() is not None:
                raise ValueError('Corrupt archive member')
            if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):
                raise ValueError('Unsafe archive path')
            files = [n for n in names if n.lower().endswith('.shp')]
            if len(files) != 1:
                raise ValueError(f'Expected exactly one shapefile in ZIP; found {len(files)}')
            stem = files[0][:-4].lower()
            for ext in ('.shp', '.shx', '.dbf', '.prj'):
                if stem + ext not in [n.lower() for n in names]:
                    raise ValueError(f'Missing required shapefile file {stem+ext}')
        uri = f'zip://{path.resolve()}'
    elif path.suffix.lower() == '.shp':
        uri = str(path)
    else:
        raise ValueError('Supply .zip or .shp with sidecars')
    return fiona.open(uri)


def analyze(vector, points):
    from shapely.geometry import Point, shape
    from shapely.ops import transform
    from pyproj import CRS, Transformer

    with open_vector(vector) as data:
        if not data.crs:
            raise ValueError('Vector data has no CRS')
        crs = CRS.from_user_input(data.crs)
        transformer = Transformer.from_crs('EPSG:4326', crs, always_xy=True)
        # Distances calculated in meters from WGS84 using UTM Zone 18N
        meters_transformer = Transformer.from_crs(crs, 'EPSG:32618', always_xy=True)
        fieldnames = set(data.schema['properties'])
        missing = {'BEDROCK_1','ROCK_GPA'} - fieldnames
        if missing:
            raise ValueError(f'Missing expected MassGIS fields: {sorted(missing)}')
        features = []
        symbols = Counter()
        for obj in data:
            props = dict(obj['properties'])
            geom = shape(obj['geometry']) if obj['geometry'] else None
            if geom is None or geom.is_empty:
                continue
            attrs = {key: props.get(key) for key in FIELDS if key in props}
            sym = attrs.get('BEDROCK_1')
            if sym:
                symbols[str(sym).strip()] += 1
            features.append((geom, attrs, transform(meters_transformer.transform, geom)))
    observations = []
    for p in points:
        lat, lon = float(p['latitude']), float(p['longitude'])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f'Invalid coordinate: {p}')
        x,y = transformer.transform(lon,lat)
        site = Point(x,y)
        site_m = transform(meters_transformer.transform,site)
        matches = []
        distances = []
        for geom, attrs, geom_m in features:
            if geom.intersects(site):
                matches.append(attrs)
                distances.append(round(geom_m.boundary.distance(site_m), 2))
        record = {
            'point_id':p['point_id'], 'place':p['place'],
            'latitude':lat, 'longitude':lon, 'location_basis':p['location_basis'],
            'status':'unreviewed', 'attribution':'massgis_bedrock_polygon',
            'source_id':SOURCE_ID,'source_url':SOURCE_URL,
            'matches':matches, 'boundary_distance_m':distances,
            'query_status':'ok' if matches else 'no_intersection', 'caveat':CAVEAT,
            'manual_review_required':True,
        }
        observations.append(record)
    return {
        'schema':'cpc-massgis-bedlith-ingest-v1',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'source_id':SOURCE_ID,'source_url':SOURCE_URL,
        'input_file':Path(vector).name,'input_sha256':sha256(vector),
        'crs_input':crs.to_string(), 'point_count':len(observations),
        'feature_count':len(features),
        'qa_points':observations,
        'unit_symbol_candidates':[
           {'symbol':name,'polygon_count':number,'status':'unreviewed','legend_locator':None}
           for name,number in sorted(symbols.items())
        ],
        'caveat':CAVEAT,
        'production_ready':False,
        'review_requirements':['Independent origin and licensing review','Verify map symbol against Zen 1983 legend',
            'Check polygons around boundaries and census location uncertainty','Review geologic unit definitions'],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vector',required=True,type=Path)
    ap.add_argument('--points',default='data/geology/qa_sample_points_ma.csv',type=Path)
    ap.add_argument('--out',default='generated/geology/bedlith',type=Path)
    args=ap.parse_args()
    with args.points.open(newline='',encoding='utf8') as f:
        points=list(csv.DictReader(f))
    if not points:
        ap.error('No QA points')
    result=analyze(args.vector,points)
    args.out.mkdir(parents=True,exist_ok=True)
    dst=args.out/'massgis_bedlith_unreviewed_qa.json'
    dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(f'Wrote {dst}; {len(result["qa_points"])} points; '
          f'{sum(bool(p["matches"]) for p in result["qa_points"])} with intersections; UNREVIEWED')

if __name__ == '__main__':
    main()