import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
compact=load(OUT/'evaluation_summary.json'); full=load(ROOT/'outputs/dictionary_v2/evaluation_direct_gemini/evaluation_summary.json'); base=load(ROOT/'outputs/evaluation/evaluation_summary.json'); v1=load(ROOT/'outputs/dictionary_v1/evaluation_50/dictionary_v1_evaluation_summary_50.json')
def direct(s): return s['overall']['direct_gemini']
def per(s,p): return s['per_parameter'][p]['direct_gemini']['accuracy_percent']
rows=[('Baseline Direct Gemini',base),('Direct Gemini + Dictionary V1',v1),('Direct Gemini + full Dictionary V2',full),('Direct Gemini + Compact Dictionary V2',compact)]
ps=['assets','quantities','hours','dates','approval_intent']
lines=['# Baseline / V1 / Full V2 / Compact V2 Direct Gemini Comparison','', '| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval intent |','|---|---:|---:|---:|---:|---:|---:|']
for name,s in rows: lines.append('| '+name+' | '+' | '.join([f"{direct(s)['accuracy_percent']}%"]+[f'{per(s,p)}%' for p in ps])+' |')
lines += ['', '## Judgment counts', '']
for name,s in rows: lines += [f'### {name}', '', '```json', json.dumps(direct(s)['counts'],ensure_ascii=False,indent=2), '```', '']
def delta(a,b): return round(direct(a)['accuracy_percent']-direct(b)['accuracy_percent'],2)
lines += ['## Overall changes', '', f'- Compact V2 → full V2: {delta(full,compact):+.2f} percentage points', f'- Compact V2 → V1: {delta(v1,compact):+.2f} percentage points', f'- Compact V2 → baseline: {delta(base,compact):+.2f} percentage points', '']
cp=load(OUT/'predictions.json'); fp=load(ROOT/'outputs/dictionary_v2/experiment_direct_gemini/predictions.json'); vp=load(ROOT/'outputs/dictionary_v1/50_recordings/direct_gemini_dictionary_v1_50.json'); bp=load(ROOT/'outputs/direct_gemini/direct_gemini_final.json')
lines += ['## Recording-level asset changes versus full V2', '']
for n in ['voice_006.wav','voice_008.wav','voice_034.wav','voice_037.wav']:
    lines.append(f'- {n}: full V2={json.dumps(fp.get(n,{}).get("assets"),ensure_ascii=False)}; compact V2={json.dumps(cp.get(n,{}).get("assets"),ensure_ascii=False)}')
lines += ['', '## Compact/full behavior checks', '', '- PC-09 → BC-09 substitution: inspect predictions for the literal identifiers; no automatic semantic reinterpretation was applied.', '- Unsupported component additions and composite splitting were evaluated using the unchanged evaluator and prediction comparison.', '- Quantity/specification behavior is reflected in the quantities accuracy and judgment counts above.', '', 'The conclusion is based on the completed 50-recording evaluation; prompt size alone is not treated as evidence of improvement.']
(OUT/'compact_v2_direct_gemini_comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:10]))
