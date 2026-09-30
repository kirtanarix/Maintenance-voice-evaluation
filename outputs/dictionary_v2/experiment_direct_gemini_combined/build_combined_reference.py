import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
V1=ROOT/'inputs/dictionary/India_Cement_Industry_and_Generic_Maintenance_Dictionary_v1.0.json'; V2=ROOT/'outputs/dictionary_v2/reference/reference_dictionary.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\s+',' ',str(s).strip().casefold())
def main():
 OUT.mkdir(parents=True,exist_ok=True); a=json.loads(V1.read_text(encoding='utf-8')); b=json.loads(V2.read_text(encoding='utf-8')); entries={}
 def add(label,src,kind='term'):
  if not isinstance(label,str) or not label.strip() or len(label)>180: return
  n=norm(label); e=entries.setdefault(n,{'label':label.strip(),'normalized_label':n,'type':kind,'sources':[]}); e['sources']=sorted(set(e['sources'])|{src})
 def walk(x):
  if isinstance(x,list):
   for v in x: walk(v)
  elif isinstance(x,dict):
   for k,v in x.items():
    if k=='common_hindi_hinglish_variants' and isinstance(v,dict):
     for key,vals in v.items(): add(key,'V1'); walk(vals)
    else: walk(v)
  elif isinstance(x,str): add(x,'V1')
 walk(a.get('categories',{}))
 for item in b.get('concepts',[]): add(item.get('label'),'V2','concept')
 for item in b.get('variants',[]): add(item.get('label'),'V2','variant')
 final=[{'label':e['label'],'normalized_label':e['normalized_label'],'type':e['type']} for e in sorted(entries.values(),key=lambda x:(x['normalized_label'],x['label']))]
 out={'version':'dictionary-v1-v2-combined-v1','purpose':'Unified contextual maintenance vocabulary','rules':['Contextual vocabulary only; reference membership is not evidence.','Extract only information explicitly supported by audio.'],'entries':final}
 cp=OUT/'combined_reference.json'; cp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 counts={'v1_source_terms':sum('V1' in x['sources'] for x in entries.values()),'v2_source_entries':len(b.get('concepts',[]))+len(b.get('variants',[])),'unified_entries':len(final),'v1_only':sum(x['sources']==['V1'] for x in entries.values()),'v2_only':sum(x['sources']==['V2'] for x in entries.values()),'both':sum(len(x['sources'])==2 for x in entries.values())}
 chars=len(json.dumps(out,ensure_ascii=False,separators=(',',':'))); audit={'source_v1':str(V1),'source_v1_sha256':sha(V1),'source_v2':str(V2),'source_v2_sha256':sha(V2),'combined_sha256':sha(cp),'counts':counts,'serialized_characters':chars,'file_bytes':cp.stat().st_size,'estimated_tokens_chars_div_4':round(chars/4),'api_calls_made':False,'deduplication':'casefolded whitespace-normalized labels'}
 (OUT/'combined_reference_manifest.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (OUT/'combined_reference_report.md').write_text('# Combined V1 + V2 Reference\n\n'+json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
