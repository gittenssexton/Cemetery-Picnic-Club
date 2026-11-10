#!/usr/bin/env python3
"""CPC: reproducible processing of the USGS Zen 1983 original raster.

This is a georeferenced *reference sheet* including margins and map legend;
it is not an attributed geology polygon dataset. Never infer units from pixels.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

EXPECTED_SHA = {
    'USGS_ngm16357.zip': 'a48efc79baef0d9a468e14773bd4c66c1b261bd0bec9ddf521b232f8fbff418f',
    'USGS_ngm16357_1.kmz': 'e95b1fbb87d1d613cce8ddbc81011f7d114d839aecad2c58f38db1f3c3a0fd6c',
}
EXPECTED_MEMBERS = {'USGS_ngm16357_1.tif', 'USGS_ngm16357_1.tif.aux.xml',
                    'USGS_ngm16357_1.tif.txt', 'README.txt'}
DEFAULT_OUT = Path('generated/geology/ma_zen1983')


def file_hash(p):
    h = hashlib.sha256()
    with open(p, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify(zip_path, kmz_path=None):
    for p in filter(None, (zip_path, kmz_path)):
        p = Path(p)
        assert p.is_file(), f'Missing {p}'
        digest = file_hash(p)
        if p.name in EXPECTED_SHA and digest != EXPECTED_SHA[p.name]:
            raise ValueError(f'Checksum mismatch: {p}: {digest}')
        with zipfile.ZipFile(p) as z:
            bad = z.testzip()
            if bad:
                raise ValueError(f'CRC error in {bad}')
            members = {n for n in z.namelist() if not n.endswith('/')}
            if p.suffix.lower() == '.zip' and not EXPECTED_MEMBERS <= members:
                raise ValueError(f'Archive missing expected members: {EXPECTED_MEMBERS - members}')
            if p.suffix.lower() == '.kmz' and 'doc.kml' not in members:
                raise ValueError('KMZ has no doc.kml')
        print(f'VERIFIED {p.name} bytes={p.stat().st_size} sha256={digest}')


def extract(zip_path, destination):
    verify(zip_path)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            p = Path(member.filename)
            if p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
                raise ValueError(f'Unsafe archive path: {member.filename}')
            target = destination / p
            if target.exists():
                with z.open(member) as src, target.open('rb') as existing:
                    h1=hashlib.sha256(src.read()).digest();h2=hashlib.sha256(existing.read()).digest()
                    if h1 != h2:
                        raise FileExistsError(f'Existing conflicting file: {target}')
                continue
            with z.open(member) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    print('Extracted originals into', destination)


def inspect_gcp(raster_path):
    import numpy as np
    import rasterio
    with rasterio.open(raster_path) as src:
        gcps, crs = src.gcps
        if len(gcps) < 4 or crs is None:
            raise ValueError('Missing at least 4 authoritative GCPs and projection')
        if crs.to_epsg() != 5069:
            raise ValueError(f'Unexpected GCP CRS: {crs}')
        x = np.array([[1, p.col, p.row] for p in gcps], dtype=float)
        y = np.array([[p.x, p.y] for p in gcps], dtype=float)
        fit = np.linalg.lstsq(x, y, rcond=None)[0]
        residual = np.linalg.norm(x @ fit - y, axis=1)
        leave_one_out = []
        for i in range(len(gcps)):
            xa = np.delete(x, i, axis=0)
            if np.linalg.matrix_rank(xa) < 3:
                leave_one_out.append(None)
                continue
            coeff = np.linalg.lstsq(xa, np.delete(y, i, axis=0), rcond=None)[0]
            leave_one_out.append(float(np.linalg.norm(x[i] @ coeff - y[i])))
        return {'raster_width': src.width, 'raster_height': src.height,
                'gcp_crs': str(crs), 'gcp_count': len(gcps),
                'fit_rms_m': float(np.sqrt(np.mean(residual ** 2))),
                'fit_max_m': float(residual.max()),
                'leave_one_out_m': leave_one_out,
                'leave_one_out_max_m': max(x for x in leave_one_out if x is not None),
                'quality_note': 'This is an internal GCP fit, NOT an independently validated geolocation accuracy estimate.'}


def warp(raster_path, out_dir, decimate=8):
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from affine import Affine
    if not 1 <= decimate <= 64:
        raise ValueError('decimate must be within 1-64')
    qa = inspect_gcp(raster_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with rasterio.open(raster_path) as src:
        gcps, crs = src.gcps
        for out_crs, name in [('EPSG:3857', 'epsg3857'), ('EPSG:4326', 'epsg4326')]:
            transform, width, height = calculate_default_transform(crs, out_crs, src.width, src.height, gcps=gcps)
            width = math.ceil(width / decimate); height = math.ceil(height / decimate)
            transform = transform * Affine.scale(decimate, decimate)
            dst_path = out_dir / f'ma_zen1983_{name}_d{decimate}.tif'
            with rasterio.open(dst_path, 'w', driver='GTiff', width=width, height=height,
                count=src.count, dtype=src.dtypes[0], transform=transform, crs=out_crs,
                compress='deflate', tiled=True, blockxsize=256, blockysize=256,
                nodata=0) as dst:
                for band in range(1, src.count + 1):
                    reproject(source=rasterio.band(src, band), destination=rasterio.band(dst, band),
                              gcps=gcps, src_crs=crs, dst_transform=transform,
                              dst_crs=out_crs, dst_nodata=0, resampling=Resampling.bilinear,
                              num_threads=2, init_dest_nodata=True)
            results.append(str(dst_path))
    return {'outputs': results, 'gcp_qa': qa, 'decimate': decimate,
            'status': 'reference_raster_only_not_unit_polygons'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('verify','extract','georef-qa','warp'))
    p.add_argument('--zip', default='USGS_ngm16357.zip')
    p.add_argument('--kmz')
    p.add_argument('--out', type=Path, default=DEFAULT_OUT)
    p.add_argument('--raster', type=Path)
    p.add_argument('--decimate', type=int, default=8)
    args=p.parse_args()
    raster=args.raster or args.out/'extracted/USGS_ngm16357_1.tif'
    if args.command=='verify': verify(args.zip,args.kmz)
    elif args.command=='extract': extract(args.zip,args.out/'extracted')
    elif args.command=='georef-qa':
        report=inspect_gcp(raster)
        (args.out/'qa').mkdir(parents=True,exist_ok=True)
        (args.out/'qa/gcp_report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
    elif args.command=='warp':
        report=warp(raster,args.out/'warp',args.decimate)
        (args.out/'qa').mkdir(parents=True,exist_ok=True)
        (args.out/'qa/warp_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))

if __name__ == '__main__': main()