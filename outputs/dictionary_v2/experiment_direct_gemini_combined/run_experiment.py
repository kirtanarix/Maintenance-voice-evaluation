from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.config import GEMINI_MODEL,load_gemini_settings
from src.direct_extractor import DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent; REF=OUT/'combined_reference.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((ROOT/'outputs/dictionary_v1/50_recordings/manifest.json').read_text(encoding='utf-8')); names=m['recording_ids']; files=[ROOT/'audio_backup'/n for n in names]; gt=json.loads((ROOT/'outputs/ground_truth/ground_truth_final.json').read_text(encoding='utf-8')); ref=json.loads(REF.read_text(encoding='utf-8')); assert len(names)==50 and all(p.is_file() for p in files) and all(n in gt for n in names)
 context='\nUse this unified V1+V2 reference only as contextual vocabulary. Reference membership is not evidence. Extract only audio-supported facts. Do not invent identifiers, substitute identifiers, add unsupported components, or split composite assets unless audio supports it. Preserve spoken identifiers/specifications.\n<combined_reference_json>\n'+json.dumps(ref,ensure_ascii=False,separators=(',',':'))+'\n</combined_reference_json>\n'; results={}; failures=[]; (OUT/'prompts').mkdir(exist_ok=True); manifest={'experiment_version':'dictionary-v1-v2-combined-direct-gemini-v1','gemini_model':GEMINI_MODEL,'recording_ids':names,'audio_sha256':{n:sha(ROOT/'audio_backup'/n) for n in names},'combined_reference_sha256':sha(REF),'ground_truth_sha256':sha(ROOT/'outputs/ground_truth/ground_truth_final.json'),'v1_reference_sha256':'416b5bded94001359807ff290af8836a7a893dfb1167d09a127756ddf49029eb','v2_reference_sha256':'ddbe7b2130e8aca3f588daf7b5fae0eb80411648f9abae6d4d66eacc4842204c','success_count':0,'failure_count':0,'proxy_variables_removed_for_process':True,'prompt_version':'direct_extractor_combined_context_v1'}; (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8'); client=GeminiAudioClient(load_gemini_settings())
 for i,p in enumerate(files,1):
  print(f'[{i}/50] {p.name}',flush=True); system=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION+context; (OUT/'prompts'/f'{p.name}.json').write_text(json.dumps({'recording_filename':p.name,'audio_sha256':sha(p),'combined_reference_sha256':sha(REF),'system_instruction':system,'user_prompt':'Listen to the attached maintenance voice recording and return the five-field JSON extraction.','model':GEMINI_MODEL},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  try:
   r=client.extract_from_audio_file(p,system_instruction=system,user_prompt='Listen to the attached maintenance voice recording and return the five-field JSON extraction.'); payload=r.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload); results[p.name]=payload; (OUT/'predictions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' success',flush=True)
  except Exception as e: failures.append({'filename':p.name,'error':f'{type(e).__name__}: {e}'}); (OUT/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' failure',flush=True)
  manifest['success_count']=len(results); manifest['failure_count']=len(failures); (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 if not failures: (OUT/'failures.json').write_text('[]\n',encoding='utf-8')
 if failures: raise SystemExit(1)
if __name__=='__main__': main()
