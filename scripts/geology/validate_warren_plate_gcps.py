#!/usr/bin/env python3
"""Preflight independent georegistration of the USGS GQ-1358 Warren map plate.

Coordinates are supplied by a human reviewing legible map graticules and control
features; never inferred from a map thumbnail. This tool DOES NOT identify any
rock unit and DOES NOT publish site geologic claims or create D1 records.

Input JSON example:
{"source": "USGS GQ-1358 1977", "plate_path":"/path/to/legible_full_plate.tif",
 "gcps":[{"pixel_x":100,"pixel_y":100,"longitude":-72.25,"latitude":42.25}, ...],
 "holdouts":[{"pixel_x":900,"pixel_y":900,"longitude":-72.125,"latitude":42.125}, ...]}

The holdouts must be distinct, independently selected checks; never reuse the
registration points. RMS and max error measure alignment to *chosen control*,
not the absolute accuracy of the historical published geology.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from pyproj import Transformer

MAX_ACCEPTABLE_HOLDOUT_M=100.0  # pilot engineering warning limit, NOT survey precision

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def check_plate(manifest):
    """Return report; strict failure for malformed or non-independent controls."""
    if manifest.get('source') != 'USGS GQ-1358 1977':
        raise ValueError('source must explicitly identify 1977 GQ-1358; no source substitution')
    path=Path(manifest['plate_path'])
    if not path.is_file():raise FileNotFoundError(f'Full-resolution map plate absent: {path}')
    gcps=manifest.get('gcps',[])
    holdouts=manifest.get('holdouts',[])
    if len(gcps)<4 or len(holdouts)<2:
        raise ValueError('At least four GCPs and two separate independent holdouts required')
    px_seen=set()
    for data in gcps+holdouts:
        arr=[data.get(k) for k in ('pixel_x','pixel_y','longitude','latitude')]
        if any(not isinstance(v,(float,int)) or isinstance(v,bool) or not math.isfinite(v) for v in arr):
            raise ValueError('All pixel and geographic coordinates must be finite numbers')
        a,b,lon,lat=arr
        if a<0 or b<0 or not(-180<=lon<=180 and -90<=lat<=90):
            raise ValueError('Coordinates out of bounds')
        xy=(a,b)
        if xy in px_seen:raise ValueError('GCP and holdout pixels must be distinct')
        px_seen.add(xy)
    # Projection consistent with official MassGIS polygons already ingested (EPSG:26986).
    proj=Transformer.from_crs('EPSG:4326','EPSG:26986',always_xy=True)
    def array(data):
        px=np.array([[1,r['pixel_x'],r['pixel_y']] for r in data],dtype=float)
        eastnorth=np.array([proj.transform(r['longitude'],r['latitude']) for r in data],dtype=float)
        return px,eastnorth
    X,Y=array(gcps)
    if np.linalg.matrix_rank(X)<3:raise ValueError('GCPs degenerate/collinear')
    coeff=np.linalg.lstsq(X,Y,rcond=None)[0]
    Xh,Yh=array(holdouts)
    train=np.linalg.norm(X@coeff-Y,axis=1)
    checks=np.linalg.norm(Xh@coeff-Yh,axis=1)
    train_rms=float(np.sqrt(np.mean(train*train)))
    check_rms=float(np.sqrt(np.mean(checks*checks)))
    check_max=float(np.max(checks))
    status='candidate_alignment_manual_review' if check_max<=MAX_ACCEPTABLE_HOLDOUT_M else 'failed_alignment_qa'
    return {
        'schema':'cpc-gq1358-georeference-preflight-v1',
        'source':'USGS GQ-1358 (Pomeroy, 1977), bedrock map plate',
        'plate_sha256':sha256(path), 'gcp_count':len(gcps),
        'independent_check_count':len(holdouts), 'registration_rms_m':round(train_rms,3),
        'independent_check_rms_m':round(check_rms,3),
        'independent_check_max_m':round(check_max,3),
        'engineering_warning_threshold_m':MAX_ACCEPTABLE_HOLDOUT_M,
        'status':status,
        'candidate_affine_pixel_to_epsg26986':coeff.T.tolist(),
        'interpretation_status':'no_geology_interpreted',
        'site_geology_verified':False,
        'quarry_origin_verified':False,
        'caveat':'No independently checked formation boundary or lithology can be inferred from an affine check alone. Location and field data remain necessary.'
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    report=check_plate(json.loads(args.manifest.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','gcp_count','independent_check_count','independent_check_max_m')},indent=2))
    if report['status']=='failed_alignment_qa':raise SystemExit(2)
if __name__=='__main__':main()