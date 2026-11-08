#!/usr/bin/env python3
"""Build a portable read-only JSON research catalog from the SQLite core.

Creates a local export; does not publish to a website or upload images.
python3 scripts/export_research_catalog.py --database local.db --output research.json
"""
import argparse, json, sqlite3
from pathlib import Path

TABLES={
    "works":("research_works","id,title,authors,published_year,work_type,journal,doi,url,full_text_status,rights_status,review_status"),
    "collections":("research_collections","id,institution,name,catalog_url,scope_note,metadata_license,image_license,access_status"),
    "motifs":("motifs","id,name,description"),
    "interpretations":("motif_interpretations","id,motif_id,interpretation_text,interpretation_type,tradition_id,scope_id,period_start_year,period_end_year,review_status"),
    "citations":("research_citations","id,work_id,locator,note"),
    "interpretation_citations":("interpretation_citations","interpretation_id,citation_id,evidence_role"),
    "maker_groups":("craftspeople","id,display_name,biography_note,home_region,date_range_text"),
    "research_tasks":("review_tasks","id,entity_type,entity_id,task_type,priority,state")
}

def export_catalog(connection):
    result={"format":"cpc-research-catalog-v1","description":"Unreviewed research metadata; not a verified stone identifier","data":{}}
    for key,(table,columns) in TABLES.items():
        cursor=connection.execute(f"SELECT {columns} FROM {table} ORDER BY 1")
        names=[col[0] for col in cursor.description]
        result["data"][key]=[dict(zip(names,row)) for row in cursor.fetchall()]
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    if not args.database.is_file(): p.error("Input database does not exist")
    db=sqlite3.connect(str(args.database))
    try: result=export_catalog(db)
    finally: db.close()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Exported {sum(len(x) for x in result['data'].values())} metadata rows to {args.output}")
if __name__=="__main__": main()
