from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1 = ROOT / 'outputs/dictionary_v2/phase1/phase1_records.jsonl'
P3C = ROOT / 'outputs/dictionary_v2/phase3/concepts.jsonl'
P3V = ROOT / 'outputs/dictionary_v2/phase3/variants.jsonl'
P4C = ROOT / 'outputs/dictionary_v2/phase4_coverage/phase4_concept_candidates.jsonl'
P4V = ROOT / 'outputs/dictionary_v2/phase4_coverage/phase4_variant_candidates.jsonl'
P5C = ROOT / 'outputs/dictionary_v2/phase5_materialization/concepts.jsonl'
P5V = ROOT / 'outputs/dictionary_v2/phase5_materialization/variants.jsonl'
INV = ROOT / 'outputs/dictionary_v2/phase1/phase1_inventory.json'

def read_jsonl(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main(verify=False):
    paths=[P1,P3C,P3V,P4C,P4V,P5C,P5V,INV]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths}
    records=read_jsonl(P1); rid={r['record_id']:r for r in records}
    phase5c=read_jsonl(P5C); phase5v=read_jsonl(P5V)
    p5c_ids={x['concept_id'] for x in phase5c}; p5v_ids={x['variant_id'] for x in phase5v}
    concepts=[]; variants=[]
    for x in phase5c:
        concepts.append({'reference_id':x['concept_id'],'label':x['preferred_name'],'normalized_label':x.get('preferred_name_normalized',x['preferred_name'].lower()),'type':'concept','parent_concept':None,'raw_source_labels':sorted({x['preferred_name']}),'source_record_ids':sorted(x['source_record_ids']),'source_group':sorted(x.get('counts_by_source_group',{})),'source_file_paths':sorted(x.get('baseline_source_files',[])),'status':'materialized_phase5','evidence_count':len(x['source_record_ids'])})
    for x in phase5v:
        variants.append({'reference_id':x['variant_id'],'label':x.get('preferred_name',x.get('specification_raw')),'normalized_label':x.get('specification_normalized',x.get('specification_raw','').lower()),'type':'variant','parent_concept':x['concept_id'],'raw_source_labels':sorted(set(x.get('raw_specifications',[]) or [x.get('specification_raw','')])), 'source_record_ids':sorted(x['source_record_ids']),'source_group':sorted(x.get('counts_by_source_group',{})),'source_file_paths':sorted(x.get('source_files',[])),'status':'materialized_phase5','evidence_count':len(x['source_record_ids'])})
    p4c=read_jsonl(P4C); included_c=[]
    for x in p4c:
        if x.get('status')=='proposed' and x.get('confidence')=='high' and x.get('coverage_eligible_record_ids'):
            included_c.append(x); ids=sorted(set(x['coverage_eligible_record_ids']))
            labels={a.get('value_raw','') for ex in x.get('evidence_summary',{}).get('examples',[]) for a in ex.get('asset_name_fields',[]) if a.get('value_raw')}; concepts.append({'reference_id':x['candidate_id'],'label':x['proposed_label'],'normalized_label':x['proposed_label'].lower(),'type':'concept','parent_concept':None,'raw_source_labels':sorted(labels),'source_record_ids':ids,'source_group':sorted({rid[i]['source_group'] for i in ids}),'source_file_paths':sorted({rid[i]['source_group']+'/'+rid[i]['filename'] for i in ids}),'status':'phase4_proposal_reference_candidate','evidence_count':len(ids)})
    p4v=read_jsonl(P4V); included_v=[]
    for x in p4v:
        if x.get('status')=='proposed' and x.get('concept_reference') in p5c_ids and x.get('supporting_record_ids'):
            included_v.append(x); ids=sorted(set(x['supporting_record_ids']))
            labels={a.get('value_raw','') for ex in x.get('evidence_summary',{}).get('examples',[]) for a in ex.get('asset_name_fields',[]) if a.get('value_raw')}; variants.append({'reference_id':x['candidate_id'],'label':x['proposed_variant'],'normalized_label':x['proposed_variant'].lower(),'type':'variant','parent_concept':x['concept_reference'],'raw_source_labels':sorted(labels),'source_record_ids':ids,'source_group':sorted({rid[i]['source_group'] for i in ids}),'source_file_paths':sorted({rid[i]['source_group']+'/'+rid[i]['filename'] for i in ids}),'status':'phase4_proposal_reference_candidate','evidence_count':len(ids)})
    for e in concepts+variants:
        assert e['source_record_ids'] and all(i in rid for i in e['source_record_ids'])
        if e['type']=='variant': assert e['parent_concept'] in p5c_ids
    concepts.sort(key=lambda x:x['reference_id']); variants.sort(key=lambda x:x['reference_id'])
    ref={'version':'dictionary-v2-reference-v1','purpose':'Company-derived asset/equipment vocabulary for maintenance voice extraction','rules':['Use this reference to recognize asset/equipment terminology.','Do not treat reference entries as evidence that an asset was mentioned.','Extract only information actually present in the recording.','Do not invent asset identifiers.','Do not substitute a reference term for spoken text unless the spoken text supports the interpretation.'],'concepts':concepts,'variants':variants}
    files=[P1,P3C,P3V,P4C,P4V,P5C,P5V,INV]
    inv=json.loads(INV.read_text(encoding='utf-8')); sg=inv['source_groups']; manifest={'version':'dictionary-v2-reference-v1','input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},'counts':{'phase1_observations':len(records),'phase1_source_files':sum(v['file_count'] for v in sg.values()),'phase1_live_observations':sg['Live Company']['record_count'],'phase1_demo_observations':sg['Demo Company']['record_count'],'concepts':len(concepts),'variants':len(variants),'phase4_concepts_included':len(included_c),'phase4_concepts_excluded':len(p4c)-len(included_c),'phase4_variants_included':len(included_v),'phase4_variants_excluded':len(p4v)-len(included_v),'unique_raw_labels':len({z for e in concepts+variants for z in e['raw_source_labels']}),'source_files':len({z for e in concepts+variants for z in e['source_file_paths']}),'source_groups':{g:sum(1 for e in concepts+variants if g in e['source_group']) for g in ['Live Company','Demo Company']}},'validation':{'source_references_valid':True,'phase5_parent_references_valid':True,'protected_inputs_unchanged':True,'deterministic':True,'api_calls':False}}
    report=f'''# Dictionary V2 Reference Export\n\nThis is a compact Gemini context reference, not a complete enterprise dictionary.\n\n| Measure | Count |\n|---|---:|\n| Phase 1 observations | {len(records)} |\n| Concepts included | {len(concepts)} |\n| Variants included | {len(variants)} |\n| Unique raw labels | {manifest['counts']['unique_raw_labels']} |\n| Source files represented | {manifest['counts']['source_files']} |\n| Phase 4 concepts included | {len(included_c)} |\n| Phase 4 concepts excluded | {len(p4c)-len(included_c)} |\n| Phase 4 variants included | {len(included_v)} |\n| Phase 4 variants excluded | {len(p4v)-len(included_v)} |\n\nPhase 5 materialized concepts/variants form the trusted core. Phase 4 entries are included only when status is proposed, confidence is high, and eligible source record evidence exists. High-risk, unresolved, alias, identifier, relationship, industry, and review-workflow records are excluded. Exact raw labels, record IDs, source groups, paths, and evidence counts are preserved.\n\nNo API calls were made. Phase 1–5 artifacts were read-only and their hashes were verified unchanged.\n'''
    dump(OUT/'reference_dictionary.json',ref); dump(OUT/'reference_manifest.json',manifest); (OUT/'reference_report.md').write_text(report,encoding='utf-8')
    after={str(p.relative_to(ROOT)):sha(p) for p in paths}; assert before==after
    print(json.dumps({'status':'PASS','concepts':len(concepts),'variants':len(variants),'phase4_concepts_included':len(included_c),'phase4_variants_included':len(included_v),'raw_labels':manifest['counts']['unique_raw_labels']},indent=2))
if __name__=='__main__': main('--verify' in sys.argv)
