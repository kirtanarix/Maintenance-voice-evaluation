import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.evaluator import evaluate, PARAMETERS
from src.report_generator import _build_summary
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
gt=json.loads((ROOT/'outputs/ground_truth/ground_truth_final.json').read_text(encoding='utf-8'))
pred=json.loads((OUT/'predictions.json').read_text(encoding='utf-8'))
assert len(pred)==50
summary=_build_summary(evaluate({n:gt[n] for n in pred}, {}, pred))
(OUT/'evaluation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def metric(p): return summary['per_parameter'][p]['direct_gemini']['accuracy_percent']
lines=['# Compact Dictionary V2 Direct Gemini Evaluation','','Scored with unchanged `src/evaluator.py` and existing ground truth.','',f"Overall accuracy: {summary['overall']['direct_gemini']['accuracy_percent']}%",'']
for p in PARAMETERS: lines.append(f"- {p}: {metric(p)}%")
lines += ['', 'Judgment counts:', '```json', json.dumps(summary['overall']['direct_gemini']['counts'],ensure_ascii=False,indent=2), '```']
(OUT/'evaluation_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
