import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.evaluator import evaluate, PARAMETERS
from src.report_generator import _build_summary
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
gt=json.loads((ROOT/'outputs/ground_truth/ground_truth_final.json').read_text(encoding='utf-8')); pred=json.loads((ROOT/'outputs/dictionary_v2/experiment_direct_gemini/predictions.json').read_text(encoding='utf-8')); base=json.loads((ROOT/'outputs/evaluation/evaluation_summary.json').read_text(encoding='utf-8')); v1=json.loads((ROOT/'outputs/dictionary_v1/evaluation_50/dictionary_v1_evaluation_summary_50.json').read_text(encoding='utf-8'))
assert len(pred)==50 and set(pred)==set(base['recordings'][0].keys()) if False else len(pred)==50
summary=_build_summary(evaluate({n:gt[n] for n in pred}, {}, pred)); (OUT/'evaluation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Dictionary V2 Direct Gemini Evaluation','','| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval intent |','|---|---:|---:|---:|---:|---:|---:|']
def row(name,s): return '| '+name+' | '+str(s['overall']['direct_gemini']['accuracy_percent'])+'% | '+' | '.join(str(s['per_parameter'][p]['direct_gemini']['accuracy_percent'])+'%' for p in PARAMETERS)+' |'
lines.append(row('Dictionary V2',summary)); lines += ['','Scoring uses the unchanged `src/evaluator.py` and existing ground truth. Correct includes EXACT_MATCH, SEMANTIC_MATCH, and CORRECT_NULL.']
(OUT/'evaluation_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
sv=summary['overall']['direct_gemini']; sb=base['overall']['direct_gemini']; s1=v1['overall']['direct_gemini']; sbp=base['per_parameter_accuracy_percent']; s1p=v1['per_parameter_accuracy_percent']; v2p={p:summary['per_parameter'][p]['direct_gemini'] for p in PARAMETERS}; lines=['# Baseline vs Dictionary V1 vs Dictionary V2 â€” Direct Gemini','','| Pipeline | Overall accuracy | Assets | Quantities | Hours | Dates | Approval intent |','|---|---:|---:|---:|---:|---:|---:|']
def r(name,s,source):
 vals=v2p if source=='v2' else (sbp if source=='base' else s1p); return '| '+name+' | '+str(s['accuracy_percent'])+'% | '+' | '.join(str(vals[p] if isinstance(vals[p],(int,float)) else (vals[p].get('direct_gemini', vals[p].get('accuracy_percent')) if isinstance(vals[p],dict) else vals[p]))+'%' for p in PARAMETERS)+' |'
lines += [r('Baseline',sb,'base'),r('Dictionary V1',s1,'v1'),r('Dictionary V2',sv,'v2'),'','| Change | Overall percentage points |','|---|---:|',f"| V1 â†’ V2 | {round(100*(sv['correct']/sv['total']-s1['correct']/s1['total']),2):+.2f} |",f"| Baseline â†’ V2 | {round(100*(sv['correct']/sv['total']-sb['correct']/sb['total']),2):+.2f} |",'','Counts (V2): '+json.dumps(sv['counts'],ensure_ascii=False),'','V2 evaluation uses the unchanged evaluator and ground truth; no baseline or Dictionary V1 rerun was performed.']
(ROOT/'outputs/dictionary_v2/dictionary_v2_direct_gemini_comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'overall':sv,'per_parameter':{p:summary['per_parameter'][p]['direct_gemini'] for p in PARAMETERS}},indent=2))


