import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.evaluator import evaluate,PARAMETERS
from src.report_generator import _build_summary
R=Path(__file__).resolve().parents[3]; O=R/'outputs/dictionary_v2/experiment_direct_gemini_combined'
def L(p): return json.loads(Path(p).read_text(encoding='utf-8'))
gt=L(R/'outputs/ground_truth/ground_truth_final.json'); pred=L(O/'predictions.json'); s=_build_summary(evaluate({n:gt[n] for n in pred},{},pred)); (O/'evaluation_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); d=s['overall']['direct_gemini']; lines=['# Combined V1 + V2 Evaluation','',f"Overall accuracy: {d['accuracy_percent']}%",'']+[f"- {p}: {s['per_parameter'][p]['direct_gemini']['accuracy_percent']}%" for p in PARAMETERS]+['','Counts:','```json',json.dumps(d['counts'],indent=2),'```']; (O/'evaluation_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
paths=[('Baseline',R/'outputs/evaluation/evaluation_summary.json'),('V1',R/'outputs/dictionary_v1/evaluation_50/dictionary_v1_evaluation_summary_50.json'),('Full V2',R/'outputs/dictionary_v2/evaluation_direct_gemini/evaluation_summary.json'),('Compact V2',R/'outputs/dictionary_v2/experiment_direct_gemini_compact/evaluation_summary.json'),('Combined',O/'evaluation_summary.json')]; ss=[(n,L(p)) for n,p in paths]; lines=['# Five-pipeline comparison','','| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval |','|---|---:|---:|---:|---:|---:|---:|']
for n,x in ss: lines.append('| '+n+' | '+' | '.join([str(x['overall']['direct_gemini']['accuracy_percent'])+'%']+[str(x['per_parameter'][p]['direct_gemini']['accuracy_percent'])+'%' for p in PARAMETERS])+' |')
for n,x in ss[:-1]: lines.append(f"\nCombined vs {n}: {d['accuracy_percent']-x['overall']['direct_gemini']['accuracy_percent']:+.2f} percentage points")
lines += ['','Combined judgment counts:','```json',json.dumps(d['counts'],indent=2),'```']
(O/'combined_v1_v2_direct_gemini_comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); print(d['accuracy_percent'],{p:s['per_parameter'][p]['direct_gemini']['accuracy_percent'] for p in PARAMETERS})
