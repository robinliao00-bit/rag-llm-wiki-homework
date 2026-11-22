"""Ingest six curated, source-attributed notes into a local LLM-Wiki-style raw layer.
No external LLM API call here: synthesis and wiki content were authored with an LLM
in the discussion stage and stored in data/content.json.
"""
import hashlib, json, pathlib, shutil, datetime
ROOT=pathlib.Path(__file__).resolve().parent.parent
SRC=ROOT/'raw';DST=ROOT/'.wiki/raw';DST.mkdir(parents=True,exist_ok=True)
meta=json.loads((ROOT/'data/content.json').read_text('utf-8'))['sources']
entries=[]
for s in meta:
    original=SRC/f'{s["id"]}.md'
    if not original.exists():raise FileNotFoundError(original)
    b=original.read_bytes();shutil.copyfile(original,DST/original.name)
    entries.append({'id':s['id'],'title':s['title'],'url':s['url'],'file':f'raw/{original.name}','sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'status':'INGESTED_SOURCE_NOTE'})
result={'ingest_date':'2026-11-23','method':'curated paraphrased notes from independently linked public sources (not full-page scraping)','sources':entries}
(ROOT/'.wiki/ingest_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for e in entries:print('INGEST',e['id'],e['bytes'],'bytes',e['sha256'][:12])
print('TOTAL_INGESTED',len(entries))
