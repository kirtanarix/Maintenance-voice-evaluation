from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.config import PROJECT_ROOT,GEMINI_MODEL,load_gemini_settings
from src.direct_extractor import extract_from_audio,DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction

OUT=Path(__file__).resolve().parent; REF=PROJECT_ROOT/'outputs/dictionary_v2/reference/reference_dictionary.json'; GT=PROJECT_ROOT/'outputs/ground_truth/ground_truth_final.json'; BASE=PROJECT_ROOT/'outputs/dictionary_v1/50_recordings/manifest.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads(BASE.read_text(encoding='utf-8')); names=m['recording_ids']; files=[PROJECT_ROOT/'audio_backup'/n for n in names]; assert len(names)==50 and all(p.is_file() and p.stat().st_size for p in files); ref=json.loads(REF.read_text(encoding='utf-8')); assert set(ref)=={'version','purpose','rules','concepts','variants'}
 gt=json.loads(GT.read_text(encoding='utf-8')); assert all(n in gt for n in names); context='\nYou are given a company-derived asset/equipment reference. Use it only as contextual vocabulary. Do not treat reference membership as evidence that an asset was mentioned. Extract only information explicitly present in the audio. Do not invent identifiers or substitute unrelated entries.\n<company_asset_reference_json>\n'+json.dumps(ref,ensure_ascii=False,separators=(',',':'))+'\n</company_asset_reference_json>\n'; out=OUT; out.mkdir(exist_ok=True); manifest={'experiment_version':'dictionary-v2-direct-gemini-v1','gemini_model':GEMINI_MODEL,'recording_ids':names,'audio_sha256':{n:sha(PROJECT_ROOT/'audio_backup'/n) for n in names},'reference_sha256':sha(REF),'ground_truth_sha256':sha(GT),'prompt_version':'direct_extractor_plus_company_reference_v1','success_count':0,'failure_count':0}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); client=GeminiAudioClient(load_gemini_settings()); results={}; failures=[]
 for i,p in enumerate(files,1):
  print(f'[{i}/50] {p.name}',flush=True)
  try:
   audit=out/'prompts'/f'{p.name}.json'; audit.parent.mkdir(parents=True,exist_ok=True); system=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION+context; audit.write_text(json.dumps({'system_instruction':system,'user_prompt':'Listen to the attached maintenance voice recording. Internally interpret the spoken content in English, then return the five-field JSON extraction.','audio_path':str(p),'audio_sha256':sha(p)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); result=extract_from_audio(client,p) if False else client.extract_from_audio_file(p,system_instruction=system,user_prompt='Listen to the attached maintenance voice recording. Internally interpret the spoken content in English, then return the five-field JSON extraction.'); payload=result.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload); results[p.name]=payload; (out/'predictions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' success',flush=True)
  except Exception as e: failures.append({'filename':p.name,'error':f'{type(e).__name__}: {e}'}); (out/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' failure',flush=True)
 manifest['success_count']=len(results); manifest['failure_count']=len(failures); (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); assert not failures, failures
if __name__=='__main__': main()
