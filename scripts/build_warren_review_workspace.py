"""Build a LOCAL, self-contained source-scan review workspace for Warren.

This exports a draft review JSON; it does not record a signed attestation,
write to staging, grant rights, or accept historical persons/burials.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path

from scripts.stage_warren_ocr_review import ROOT, FILES, prepare as original
from scripts.stage_warren_page_omissions import prepare as omissions
from scripts.stage_warren_page12 import prepare as page12


def candidates():
    rows=[]
    for name in FILES:
        _, batch=original(ROOT/"data/vital-records"/name)
        rows.extend(batch)
    rows.extend(omissions()[1])
    rows.extend(page12()[1])
    if len(rows)!=140 or len({r[0] for r in rows})!=140:
        raise ValueError("Expected 140 unique provisional source candidates")
    output=[]
    for r in rows:
        record=json.loads(r[13])
        output.append({
          "id":r[0],"printed_page":r[4],"candidate_sha256":r[14],
          "ocr_name":r[7],"ocr_date":r[8] or "",
          "code":r[9] or "", "source_class":r[10],
          "line":record.get("source_line_reading") or "",
          "notes":record.get("notes") or "",
          "source_batch":r[2],
          "review_status":"requires_page_image_check"
        })
    return sorted(output,key=lambda x:(x["printed_page"],x["id"]))


def image_payload(directory):
    out={}
    if directory is None:return out
    for page in (9,10,11,12):
        path=directory/f"warren_scan_p{page:02d}.png"
        if not path.is_file():
            continue
        data=path.read_bytes()
        if len(data)>12_000_000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
            raise ValueError("Source scan is not a bounded PNG: "+str(path))
        out[str(page)]={
            "data":"data:image/png;base64,"+base64.b64encode(data).decode("ascii"),
            "sha256":hashlib.sha256(data).hexdigest()
        }
    return out


HTML_TOP = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Warren printed births — review drafts</title>
<style>
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,Arial;background:#f4f3ef;color:#24302d}
header{background:#172f2a;color:white;padding:14px 22px}h1{font-size:21px;margin:0}header p{margin:3px 0}
main{display:grid;grid-template-columns:minmax(360px,48%) minmax(370px,52%);height:calc(100dvh - 105px)}
section{min-width:0;overflow:auto;padding:16px}section+section{border-left:1px solid #bbb}
#scan{display:block;max-width:100%;margin:auto;background:white;box-shadow:0 1px 10px #bbb}
label{display:block;margin:8px 0 3px;font-weight:600}input,select,textarea,button{font:inherit}
input,select,textarea{width:100%;padding:9px;border:1px solid #a2aca7;border-radius:5px;background:#fff}
textarea{min-height:80px}button{border:0;border-radius:6px;padding:9px 12px;cursor:pointer;background:#234f41;color:white}
button:disabled{opacity:.45;cursor:default}.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.card{background:white;padding:14px;border:1px solid #ddd;border-radius:9px}.muted{color:#52615d}
.warning{background:#fff6db;color:#594214;padding:9px 12px;border-radius:7px;margin-bottom:12px}
code{overflow-wrap:anywhere}.meta{display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media(max-width:870px){main{display:block;height:auto}section{overflow:visible}section+section{border-left:0;border-top:1px solid #aaa}#scan{max-height:90vh}}
</style></head><body>
<header><h1>Warren Vital Records | Local source review</h1>
<p>140 provisional entries • printed pp. 9–12 • private offline draft workspace • no approvals or database writes</p></header>
<main><section><div class="toolbar"><label for="page">Printed page</label>
<select id="page" style="width:auto"><option>9</option><option>10</option><option>11</option><option>12</option></select>
<span id="scan-info"></span></div><img id="scan" alt="Historical book page (when locally embedded)">
<p class="muted">The book was printed in 1910. Read the original line, not just OCR. Blank dates and G.S.2 gravestone citations must stay explicit.</p></section>
<section><div class="warning"><strong>Drafts only:</strong> This page does not produce signed human verification, approve data, create people, or publish images. Export proposed readings for a separate controlled review.</div>
<div class="toolbar"><label for="candidate">Candidate</label><select id="candidate" style="flex:1;min-width:200px"></select></div>
<div class="card"><div id="details"></div>
<label for="reading">Proposed exact printed line</label><textarea id="reading" placeholder="Transcribe the full line, including brackets and source suffix."></textarea>
<div class="meta"><div><label for="name">Proposed name as printed</label><input id="name"></div>
<div><label for="date">Proposed date as printed</label><input id="date"></div></div>
<label for="decision">Draft outcome</label><select id="decision"><option value="">Not reviewed</option>
<option value="propose_confirm">Looks consistent — request human signoff</option>
<option value="propose_correction">Correction proposed — request human signoff</option>
<option value="needs_more_evidence">Uncertain — hold</option></select>
<label for="notes">Evidence notes / uncertainty</label><textarea id="notes"></textarea>
<div class="toolbar"><button id="keep">Save draft locally in this session</button><button id="export">Export review drafts as JSON</button></div>
<p class="muted" id="counts"></p></div></section></main>
<script id="payload" type="application/json">"""
HTML_BOTTOM = """</script><script>
'use strict';
const data=JSON.parse(document.getElementById('payload').textContent);
const draft=new Map(); const el=id=>document.getElementById(id);
let selected='';
function escapeText(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function refreshPage(){
 const p=Number(el('page').value);
 const img=data.scans[String(p)];
 el('scan').src=img?img.data:'';
 el('scan').style.display=img?'block':'none';
 el('scan-info').textContent=img?'Embedded local scan • SHA-256 '+img.sha256.slice(0,14)+'…':'Source scan not embedded; supply a local scan image to generator';
 const items=data.rows.filter(x=>x.printed_page===p);
 el('candidate').replaceChildren();
 for(const x of items){const o=document.createElement('option');o.value=x.id;
 o.textContent=x.id.split('-').slice(-2).join('-')+' • '+x.ocr_name;el('candidate').appendChild(o);}
 selected='';choose();
}
function choose(){
 const id=el('candidate').value;const r=data.rows.find(x=>x.id===id);if(!r)return;selected=id;
 el('details').innerHTML='<strong>'+escapeText(r.ocr_name)+'</strong> • '+escapeText(r.ocr_date)
   +'<p><small><code>'+escapeText(r.id)+'</code></small></p>'
   +'<p>Original class: <strong>'+escapeText(r.source_class)+'</strong> • Source code: '
   +escapeText(r.code||'none printed')+'</p>'
   +'<p class="muted">Source row checksum: <code>'+escapeText(r.candidate_sha256)+'</code></p>'
   +(r.notes?'<p>'+escapeText(r.notes)+'</p>':'');
 const d=draft.get(id)||{};
 el('reading').value=d.reading??r.line;
 el('name').value=d.name??r.ocr_name;
 el('date').value=d.date??r.ocr_date;
 el('decision').value=d.decision??'';
 el('notes').value=d.notes??'';
 counts();
}
function save(){
 if(!selected)return;
 const r=data.rows.find(x=>x.id===selected);
 draft.set(selected,{candidate_id:selected,printed_page:r.printed_page,source_record_sha256:r.candidate_sha256,
  reading:el('reading').value,name:el('name').value,date:el('date').value,
  decision:el('decision').value,notes:el('notes').value,
  review_status:'unsigned_draft_not_accepted'});
 counts();
}
function counts(){el('counts').textContent=draft.size+' of 140 draft entries saved in this browser session (not to server).';}
el('page').addEventListener('change',()=>{save();refreshPage()});
el('candidate').addEventListener('change',()=>{save();choose()});
el('keep').addEventListener('click',save);
el('export').addEventListener('click',()=>{
 save();
 const payload={schema:'cpc-warren-human-review-drafts-v1',status:'unsigned_draft_not_accepted',
    source:'Warren 1910 printed births pp. 9-12',entries:Array.from(draft.values())};
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob);const a=document.createElement('a');
 a.href=url;a.download='warren-review-proposals.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
refreshPage();
</script></body></html>"""


def build(output, scans=None):
    rows=candidates()
    payload=json.dumps({"rows":rows,"scans":image_payload(scans)},ensure_ascii=False,
                       separators=(",",":")).replace("<","\\u003c")
    if output.exists():
        raise FileExistsError("Refusing to overwrite existing review drafts HTML")
    output.write_text(HTML_TOP+payload+HTML_BOTTOM,encoding="utf-8")
    return len(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--scan-dir",type=Path,help="Private folder with warren_scan_p09.png ... p12.png")
    args=parser.parse_args()
    n=build(args.output,args.scan_dir)
    print(f"Created private offline draft review workspace for {n} provisional entries.")

if __name__=="__main__":
    main()
