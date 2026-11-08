#!/usr/bin/env python3
"""Validate and optionally import licensed bibliographic metadata into SQLite/D1 compatible DB.

Usage:
  python3 scripts/import_bibliography.py data/templates/research_works_example.csv --check
  python3 scripts/import_bibliography.py input.csv --database research.db --apply

No web scraping, full-text acquisition, photo fetching, or claims about reading sources.
The default is a dry-run; --apply explicitly writes accepted rows. D1 production sync is
separate and not performed here.
"""
import argparse
import csv
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ("id","title","authors","published_year","work_type","publisher","journal",
          "volume","issue","pages","doi","isbn","url","full_text_status",
          "rights_status","review_status")
WORK_TYPES = {"book","article","archive","government","dataset","web","report","other"}
TEXT_STATUS = {"not_acquired","abstract_only","available_external","licensed_copy","public_domain_copy","reviewed"}
REVIEW_STATUS = {"bibliography_only","metadata_verified","partly_reviewed","fully_reviewed"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,127}$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$",re.IGNORECASE)


def validate(row, number):
    errors=[]
    for field in ("id","title","work_type"):
        if not row.get(field,"").strip(): errors.append(f"row {number}: missing {field}")
    if row.get("id") and not ID_PATTERN.fullmatch(row["id"]):
        errors.append(f"row {number}: invalid stable id")
    if row.get("work_type") and row["work_type"] not in WORK_TYPES:
        errors.append(f"row {number}: invalid work_type")
    if row.get("full_text_status") not in TEXT_STATUS:
        errors.append(f"row {number}: invalid full_text_status")
    if row.get("review_status") not in REVIEW_STATUS:
        errors.append(f"row {number}: invalid review_status")
    year=row.get("published_year","").strip()
    if year and (not year.lstrip("-").isdigit() or not -5000<=int(year)<=2100):
        errors.append(f"row {number}: invalid year")
    if row.get("doi") and not DOI_PATTERN.fullmatch(row["doi"].replace("https://doi.org/","")):
        errors.append(f"row {number}: invalid DOI")
    url=row.get("url","").strip()
    if url:
        u=urlparse(url)
        if u.scheme!="https" or not u.netloc:
            errors.append(f"row {number}: URL must be HTTPS with a domain")
    return errors


def load(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames: raise ValueError("Missing CSV header")
        missing=set(FIELDS)-set(reader.fieldnames)
        if missing: raise ValueError("Missing header fields: "+", ".join(sorted(missing)))
        rows=[]; errors=[]; seen=set(); dois=set()
        for index,raw in enumerate(reader,start=2):
            row={field:(raw.get(field) or "").strip() for field in FIELDS}
            errors.extend(validate(row,index))
            if row["id"] in seen: errors.append(f"row {index}: duplicate id {row['id']}")
            seen.add(row["id"])
            doi=row["doi"].lower().replace("https://doi.org/","")
            if doi:
                if doi in dois: errors.append(f"row {index}: duplicate DOI {doi}")
                dois.add(doi)
            rows.append(row)
    return rows,errors


def import_rows(connection, rows):
    sql=("INSERT INTO research_works ("+",".join(FIELDS)+") VALUES ("+
         ",".join("?" for _ in FIELDS)+")")
    # Fail on duplicates already in the DB. This prevents unreviewed overwrites.
    connection.executemany(sql,[[int(r[f]) if f=="published_year" and r[f] else (r[f] or None)
                                 for f in FIELDS] for r in rows])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv",type=Path)
    parser.add_argument("--check",action="store_true",help="Validate only (default)")
    parser.add_argument("--database",type=Path,help="Existing SQLite DB with global core migration")
    parser.add_argument("--apply",action="store_true",help="Explicitly insert into database")
    args=parser.parse_args()
    if args.apply and (args.check or not args.database):
        parser.error("--apply requires --database and cannot be combined with --check")
    if args.apply and not args.database.is_file():
        parser.error("Database file must already exist; migrations are not run implicitly")
    try: rows,errors=load(args.csv)
    except (ValueError,OSError,csv.Error) as e:
        print("CSV ERROR:",e,file=sys.stderr);return 2
    if errors:
        for e in errors: print(e,file=sys.stderr)
        return 1
    print(f"Validated {len(rows)} bibliography records; zero photographs or full text retrieved.")
    if args.apply:
        try:
            con=sqlite3.connect(str(args.database))
            con.execute("PRAGMA foreign_keys=ON")
            with con: import_rows(con,rows)
            con.close()
        except sqlite3.Error as e:
            print("IMPORT FAILED:",e,file=sys.stderr);return 1
        print(f"Inserted {len(rows)} bibliographic records into local SQLite.")
    else:
        print("Dry run only; use --apply --database PATH for explicit import.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
