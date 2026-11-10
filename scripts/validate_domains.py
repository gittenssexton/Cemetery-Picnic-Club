#!/usr/bin/env python3
"""Check CPC domain registry, ownership, terminology and pre-integration migrations.

Run: python3 scripts/validate_domains.py
Validates the declared migration plan but does not modify databases or other branches.
"""
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"architecture/domain-registry.json"
REQUIRED={"CEM","VIT","GEO","ICO","CAR","IMG","HIS","KIN","LOC","CON"}
IDENT=re.compile(r"^[a-z][a-z0-9_]*$")
REF=re.compile(r"^(CEM|VIT|GEO|ICO|CAR|IMG|HIS|KIN|LOC|CON):[a-z][a-z0-9_-]*:[A-Za-z0-9][A-Za-z0-9._-]*$")
MIGRATION=re.compile(r"^(\d{4})_[a-z][a-z0-9_]*\.sql$")


def check_registry(data):
    errors=[]
    codes=[d.get("code") for d in data.get("domains",[])]
    if len(codes)!=len(set(codes)):errors.append("duplicate domain code")
    if set(codes)!=REQUIRED:errors.append("domain code set differs from canonical set")
    prefixes=[d.get("prefix") for d in data.get("domains",[])]
    if len(set(prefixes))!=len(prefixes):errors.append("duplicate namespace prefix")
    for d in data.get("domains",[]):
        code=d.get("code","?")
        if not d.get("entities"):errors.append(f"{code}: no entities")
        if not d.get("terms"):errors.append(f"{code}: no terms")
        if not d.get("validation"):errors.append(f"{code}: missing validation rules")
        if not re.fullmatch(r"[a-z]{3}_",d.get("prefix","")):
            errors.append(f"{code}: invalid prefix")
        for name in d.get("terms",{}):
            if not IDENT.fullmatch(name):errors.append(f"{code}: invalid term {name}")
    shared=data.get("shared",{})
    if len(set(shared.get("canonical_entities",[])))!=len(shared.get("canonical_entities",[])):
        errors.append("duplicate canonical entity")
    mig=data.get("migrations",{})
    plan=mig.get("integration_plan",[])
    nums=[]
    for filename in plan:
        m=MIGRATION.fullmatch(filename)
        if not m:errors.append(f"invalid migration name: {filename}")
        else:nums.append(int(m.group(1)))
    if nums!=sorted(set(nums)):errors.append("integration plan has duplicate or unsorted migration numbers")
    return errors


def check_files(root=ROOT):
    errors=[]
    files=sorted((root/"db/migrations").glob("*.sql"))
    n={}
    for f in files:
        m=MIGRATION.fullmatch(f.name)
        if not m:errors.append(f"invalid existing migration filename: {f.name}");continue
        num=m.group(1)
        if num in n:errors.append(f"duplicate migration number: {n[num]}, {f.name}")
        n[num]=f.name
    return errors


def main():
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors=check_registry(data)+check_files()
    if errors:
        for e in errors:print("ERROR:",e,file=sys.stderr)
        return 1
    print(f"Valid registry: {len(data['domains'])} domains; unique local migrations; integration plan collision-free.")
    return 0


if __name__=="__main__":raise SystemExit(main())
