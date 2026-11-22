"""Build Markdown wiki and static HTML. Enforces fail-before-render lint gate."""
import html,json,pathlib,re,sys
from check import inspect
ROOT=pathlib.Path(__file__).resolve().parent.parent
errs,notes=inspect()
if errs:
    for e in errs:print('BUILD_BLOCKED',e)
    sys.exit(1)
data=json.loads((ROOT/'data/content.json').read_text('utf-8'))
pageids={p['id']:p for p in data['pages']}
sources={s['id']:s for s in data['sources']}
wiki=ROOT/'.wiki/wiki';wiki.mkdir(parents=True,exist_ok=True)
for p in data['pages']:
    lines=[f'# {p["title"]}','',p['subtitle'],'']
    for h,t in p['sections']:lines.extend([f'## {h}','',t,''])
    if p['example']:lines.extend(['## 教學案例','',p['example'],''])
    lines.extend(['## 原始資料',''])
    for id in p['sources']:lines.append(f'- [{id} · {sources[id]["title"]}]({sources[id]["url"]})')
    lines.extend(['','## 交叉連結',''])
    for id in p['related']:lines.append(f'- [{pageids[id]["title"]}]({id}.md)')
    (wiki/f'{p["id"]}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
idx=['# RAG 主題 LLM Wiki','',f'資料：{len(data["sources"])} 份；知識頁：{len(data["pages"])} 頁','']
idx += [f'- [{p["title"]}](wiki/{p["id"]}.md) — {p["subtitle"]}' for p in data['pages']]
idx+=['','## 原始來源','']
idx += [f'- [{s["id"]} · {s["title"]}]({s["url"]})' for s in data['sources']]
(ROOT/'.wiki/index.md').write_text('\n'.join(idx)+'\n',encoding='utf-8')
(ROOT/'.wiki/AGENTS.md').write_text('''# LLM Wiki project rules\n\n- Raw sources are immutable after ingest; if changed, re-run ingest and lint.\n- Source IDs S01..S06 must be preserved on all claims and lesson slides.\n- Wiki entries must include source citations and at least one related concept.\n- If citation or crosslink is broken, fail *before* HTML rendering.\n- Claims about lesson examples must explicitly say hypothetical.\n- Do not infer that a cited answer is necessarily true.\n- For new sources: ingest -> update wiki concept pages -> check -> render -> review.\n''',encoding='utf-8')
(ROOT/'.wiki/log.md').write_text('''# Maintenance log\n\n2026-11-23: 6 attributed source notes ingested. LLM-authored wiki synthesis generated as 10 connected entries.\n2026-11-23: Validation moved before HTML build; deliberate missing source ID test recorded in evidence/check_run.txt.\n2026-11-23: See evidence/check_run.txt for real command output and the limits of structural validation.\n''',encoding='utf-8')
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
for name in ('index','wiki','slides','workflow'):
    tpl=(ROOT/'templates'/f'{name}.tpl.html').read_text('utf-8')
    txt=tpl.replace('__DATA__',payload)
    if name=='workflow':
        ev=(ROOT/'evidence/check_run.txt').read_text('utf-8') if (ROOT/'evidence/check_run.txt').exists() else '尚未建立執行紀錄'
        txt=txt.replace('__EVIDENCE__',html.escape(ev))
    (ROOT/f'{name}.html').write_text(txt,encoding='utf-8')
    print('BUILD',name+'.html')
print('PASS BUILD_AFTER_LINT',*notes,sep=' | ')
