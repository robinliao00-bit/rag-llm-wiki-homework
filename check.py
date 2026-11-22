"""Source lineage and structure lint. Standard library only."""
import argparse, hashlib, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent

def inspect(path=None, expect_manifest=True):
    data=json.loads(pathlib.Path(path or ROOT/'data/content.json').read_text('utf-8'))
    errors=[]; notes=[]
    src=data.get('sources',[]); pages=data.get('pages',[]); slides=data.get('slides',[])
    sid={x['id'] for x in src}; pid={x['id'] for x in pages}
    def fail(msg): errors.append(msg)
    if len(src)<5: fail(f'SOURCE_MIN_5: found {len(src)}, expected >=5')
    if len(sid)!=len(src):fail('DUPLICATE_SOURCE_IDS')
    if len(pid)!=len(pages):fail('DUPLICATE_PAGE_IDS')
    if len({x['id'] for x in slides})!=len(slides):fail('DUPLICATE_SLIDE_IDS')
    manpath=ROOT/'.wiki/ingest_manifest.json'
    try: manifest=json.loads(manpath.read_text('utf-8')) if expect_manifest else None
    except FileNotFoundError: manifest=None;fail('NO_INGEST_MANIFEST: run python3 tools/ingest.py')
    if manifest is not None:
        ingested={x['id']:x for x in manifest['sources']}
        if len(ingested)<5:fail('INGESTED_SOURCE_MIN_5')
        if sid!=set(ingested):fail('INGEST_SOURCE_REGISTRY_MISMATCH')
    for s in src:
        f=ROOT/'raw'/f"{s['id']}.md"
        if not f.exists():fail(f'MISSING_RAW_SOURCE {s["id"]}');continue
        content=f.read_text('utf-8')
        for tag,value in [('id',s['id']),('url',s['url'])]:
            if f'{tag}: {value}' not in content:fail(f'RAW_METADATA_MISMATCH {s["id"]} {tag}')
        if not s['url'].startswith('https://'):fail(f'SOURCE_URL_INSECURE {s["id"]}')
        if len(content)<250:fail(f'SOURCE_NOTE_TOO_SHORT {s["id"]}')
        if manifest is not None:
            actual=hashlib.sha256(content.encode('utf-8')).hexdigest()
            if ingested.get(s['id'],{}).get('sha256')!=actual:fail(f'RAW_SOURCE_HASH_CHANGED {s["id"]}: re-ingest needed')
    for p in pages:
        if len(p.get('sections',[]))<2:fail(f'WIKI_TOO_THIN {p["id"]}')
        if not p['sources']:fail(f'WIKI_UNCITED {p["id"]}')
        for x in p['sources']:
            if x not in sid:fail(f'UNKNOWN_WIKI_SOURCE {p["id"]}: {x}')
        for x in p['related']:
            if x not in pid:fail(f'BROKEN_WIKI_CROSSLINK {p["id"]}: {x}')
    used_sources=set()
    for s in slides:
        if not s.get('wiki'):fail(f'SLIDE_NO_WIKI_LINEAGE {s["id"]}')
        if not s.get('sources'):fail(f'SLIDE_NO_SOURCES {s["id"]}')
        union=set()
        for p in s['wiki']:
            if p not in pid:fail(f'SLIDE_UNKNOWN_WIKI {s["id"]}: {p}')
            else:union.update(next(x for x in pages if x['id']==p)['sources'])
        for x in s['sources']:
            if x not in sid:fail(f'UNKNOWN_SLIDE_SOURCE {s["id"]}: {x}')
            elif x not in union:fail(f'SLIDE_SOURCE_NOT_LINKED_TO_WIKI {s["id"]}: {x}')
        if not s.get('points'):fail(f'SLIDE_EMPTY {s["id"]}')
        used_sources.update(s['sources'])
    if len(used_sources)<5:fail('SLIDE_USES_TOO_FEW_SOURCES')
    if len(pages)<5:fail('INSUFFICIENT_WIKI_PAGES')
    notes += [f'SOURCES={len(src)}',f'INGESTED={len(manifest["sources"]) if manifest else 0}',f'WIKI_PAGES={len(pages)}',f'SLIDES={len(slides)}',f'USED_SOURCES={len(used_sources)}']
    notes.append('STRUCTURE_ONLY: semantic faithfulness still needs human review')
    return errors,notes

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--data');args=pa.parse_args()
    errors,notes=inspect(args.data)
    for line in notes:print('INFO',line)
    if errors:
        for e in errors:print('FAIL',e)
        sys.exit(1)
    print('PASS SOURCE_LINEAGE_AND_STRUCTURE')
