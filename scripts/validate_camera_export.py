#!/usr/bin/env python3
"""Validate Field Camera 0.5 ZIPs without importing or exposing precise GPS."""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBER = 80 * 1024 * 1024
RECORD_ID = re.compile(r"^CPC-[0-9]{4}-[0-9]{2}-[0-9]{2}T[A-Za-z0-9-]+$")
SUFFIXES = ("_original.jpg", "_isolated.jpg", "_geotagged.jpg", "_cutout.png")
LOCATIONS = {"location_missing", "device_gps_observed", "manual_unverified"}


def validate_camera_zip(path):
    with zipfile.ZipFile(path) as archive:
        files = archive.infolist()
        names = [f.filename for f in files]
        if not 2 <= len(files) <= 12 or len(names) != len(set(names)):
            raise ValueError("Invalid number of files or duplicate names")
        if sum(f.file_size for f in files) > 150 * 1024 * 1024:
            raise ValueError("Excessive uncompressed archive size")
        for f in files:
            p = PurePosixPath(f.filename)
            if (f.is_dir() or p.is_absolute() or len(p.parts) != 2 or ".." in p.parts
                    or "\\" in f.filename or f.flag_bits & 1 or f.file_size > MAX_MEMBER):
                raise ValueError("Unsafe archive member")
        entries = [f for f in files if f.filename.endswith("/record.json")]
        if len(entries) != 1 or entries[0].file_size > 2 * 1024 * 1024:
            raise ValueError("Expected exactly one bounded record.json")
        record = json.loads(archive.read(entries[0]))
        if not isinstance(record, dict):
            raise ValueError("Invalid metadata object")
        rid = record.get("id")
        if not isinstance(rid, str) or not RECORD_ID.fullmatch(rid):
            raise ValueError("Invalid record ID")
        if record.get("schema_version") != "0.5":
            raise ValueError("Unsupported camera schema")
        photo = record.get("photo")
        if (not isinstance(photo, dict) or photo.get("format") != "image/jpeg"
            or photo.get("original_is_full_frame") is not True
            or type(photo.get("width")) is not int or photo["width"] <= 0
            or type(photo.get("height")) is not int or photo["height"] <= 0):
            raise ValueError("Missing original-frame provenance")
        status = record.get("location_status")
        if status not in LOCATIONS:
            raise ValueError("Invalid location status")
        location = record.get("location")
        if status == "location_missing" and location is not None:
            raise ValueError("Unlocated record unexpectedly includes GPS")
        if status != "location_missing":
            if not isinstance(location, dict):
                raise ValueError("Missing coordinate metadata")
            lat, lon = location.get("latitude"), location.get("longitude")
            if (type(lat) not in (int,float) or type(lon) not in (int,float)
                or not (-90 <= lat <= 90 and -180 <= lon <= 180)):
                raise ValueError("Invalid GPS coordinates")
        root = rid + "/" + rid
        original_name = root + "_original.jpg"
        allowed = {rid + "/record.json"} | {root + s for s in SUFFIXES}
        if original_name not in names or not set(names).issubset(allowed):
            raise ValueError("Missing original or unexpected archive path")
        if archive.testzip() is not None:
            raise ValueError("Archive CRC failure")
        original = archive.read(original_name)
        if len(original) < 4 or original[:2] != bytes([255,216]) or original[-2:] != bytes([255,217]):
            raise ValueError("Invalid original JPEG signature")
        for name in names:
            if name.endswith(".jpg"):
                content = archive.read(name)
                if len(content) < 4 or content[:2] != bytes([255,216]) or content[-2:] != bytes([255,217]):
                    raise ValueError("Invalid derivative JPEG signature")
        return {"record_id":rid,"schema_version":"0.5",
                "original_sha256":hashlib.sha256(original).hexdigest(),
                "original_bytes":len(original),"member_count":len(files),
                "has_gps_metadata":location is not None,
                "location_status":status,"review_status":"unreviewed",
                "published":False,"imported":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("camera_zip",type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(validate_camera_zip(args.camera_zip),sort_keys=True,indent=2))
        return 0
    except (OSError,zipfile.BadZipFile,ValueError,KeyError,TypeError) as exc:
        print("Invalid camera archive:",exc,file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
