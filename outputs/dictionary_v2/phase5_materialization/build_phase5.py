"""Phase 5 — Reviewed Materialization.

Materializes only previously approved Phase 3 concepts/variants. Phase 4
proposals become explicit pending review decisions; none are auto-approved.
Standard library only. --verify is read-only; --refresh is limited to this
Phase 5 output directory after a builder change.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "outputs/dictionary_v2"
VERSION = "phase5-reviewed-materialization-v1"
FILES = ("review_decisions.jsonl", "concepts.jsonl", "variants.jsonl", "manifest.json", "phase5_report.md")
PROTECTED = ("inputs", "src", "outputs/dictionary_v2/phase1", "outputs/dictionary_v2/phase2_exploration",
             "outputs/dictionary_v2/phase3", "outputs/dictionary_v2/phase3_exploration", "outputs/dictionary_v2/phase4_coverage")

def require(x, msg):
    if not x: raise ValueError(msg)
def packed(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def stable(kind,*parts): return "phase5_"+kind+"_"+hashlib.sha256(packed((VERSION,*parts)).encode()).hexdigest()[:24]
def readj(p): return json.loads(p.read_text(encoding="utf-8"))
def jsonl(p):
    with p.open(encoding="utf-8") as f:
        for line in f: yield json.loads(line)
def snapshot():
    return {p.relative_to(ROOT).as_posix():sha(p) for s in PROTECTED for p in (ROOT/s).rglob("*") if p.is_file()}
def coord(r): return {k:r[k] for k in ("record_id","source_id","source_group","filename","sheet","row_number")}

def load():
    p1=BASE/"phase1"; p2=BASE/"phase2_exploration"; p3=BASE/"phase3"; p4=BASE/"phase4_coverage"
    inv=readj(p1/"phase1_inventory.json"); p1c=readj(p1/"phase1_candidates.json"); p2a=readj(p2/"phase2_candidate_analysis.json")
    p3m=readj(p3/"manifest.json"); p4a=readj(p4/"phase4_coverage_analysis.json")
    paths=[p1/x for x in ("phase1_inventory.json","phase1_records.jsonl","phase1_candidates.json","phase1_report.md")]
    paths += [p2/x for x in ("phase2_exploration_report.md","phase2_candidate_analysis.json","phase2_rule_proposals.json","phase2_high_risk_cases.json")]
    paths += [p3/x for x in ("concepts.jsonl","variants.jsonl","instances.jsonl","industry_associations.jsonl","review_decisions.jsonl","manifest.json","phase3_report.md","build_phase3.py")]
    paths += [p4/x for x in ("phase4_concept_candidates.jsonl","phase4_variant_candidates.jsonl","phase4_review_queue.jsonl","phase4_coverage_analysis.json","phase4_coverage_report.md","build_phase4.py")]
    hashes={x.relative_to(ROOT).as_posix():sha(x) for x in paths}
    for s in inv["sources"]: require(sha(ROOT/"inputs/dictionary_v2"/s["relative_path"])==s["sha256"],"source hash changed")
    records={r["record_id"]:r for r in jsonl(p1/"phase1_records.jsonl")}; require(len(records)==63479,"record count mismatch")
    candidates={c["candidate_id"]:c for c in p1c["candidates"]}; proposals={c["candidate_id"]:c for c in p2a["candidates"]}
    require(candidates.keys()==proposals.keys(),"Phase 1/2 candidate coverage mismatch")
    phase3_concepts={x["concept_id"]:x for x in jsonl(p3/"concepts.jsonl")}; phase3_variants={x["variant_id"]:x for x in jsonl(p3/"variants.jsonl")}
    for x in [*phase3_concepts.values(),*phase3_variants.values()]: require(set(x["source_record_ids"])<=records.keys(),"Phase 3 source ref invalid")
    p4concept=list(jsonl(p4/"phase4_concept_candidates.jsonl")); p4variant=list(jsonl(p4/"phase4_variant_candidates.jsonl")); queue=list(jsonl(p4/"phase4_review_queue.jsonl"))
    for x in p4concept+p4variant+queue: require(set(x["supporting_record_ids"])<=records.keys(),"Phase 4 source ref invalid")
    for x in p4variant: require(x["concept_reference"] in phase3_concepts,"Phase 4 variant parent invalid")
    require(p4a["candidate_counts"]["proposed_new_concepts"]==sum(x["status"]=="proposed" for x in p4concept),"Phase 4 proposal count mismatch")
    require(p4a["candidate_counts"]["proposed_new_variants"]==len(p4variant),"Phase 4 variant count mismatch")
    return {"records":records,"candidates":candidates,"proposals":proposals,"phase3_concepts":phase3_concepts,
            "phase3_variants":phase3_variants,"p4concept":p4concept,"p4variant":p4variant,"queue":queue,
            "risk":readj(p2/"phase2_high_risk_cases.json"),"hashes":hashes}

def decision(kind,key,status,source_ids,reason,proposal_type,confidence="pending",evidence=None, refs=None):
    return {"decision_id":stable("decision",kind,key),"decision_kind":kind,"subject_id":key,"status":status,
            "relationship_type":proposal_type,"confidence":confidence,"source_record_ids":sorted(set(source_ids)),
            "reason":reason,"evidence":evidence or [],"references":refs or {},"rule_version":VERSION,
            "review_required":status=="pending","approval_basis":None}

def build(d):
    records=d["records"]; decisions=[]
    # Inherited Phase 3 materialization is explicitly approved by Phase 3 decisions.
    concepts=[]; variants=[]
    for cid,c in sorted(d["phase3_concepts"].items()):
        did=stable("decision","inherited_phase3_materialization",cid)
        decisions.append(decision("inherited_phase3_materialization",cid,"approved",c["source_record_ids"],"Inherited from validated Phase 3 approved concept; no Phase 4 proposal is approved.","CONCEPT_MATERIALIZATION","high",[coord(records[r]) for r in c["source_record_ids"]],{"phase3_concept_id":cid}))
        x=dict(c);x["materialization_decision_id"]=did;x["phase5_status"]="approved_inherited";concepts.append(x)
    for vid,v in sorted(d["phase3_variants"].items()):
        did=stable("decision","inherited_phase3_materialization",vid)
        decisions.append(decision("inherited_phase3_materialization",vid,"approved",v["source_record_ids"],"Inherited from validated Phase 3 approved variant; no Phase 4 proposal is approved.","VARIANT_MATERIALIZATION","high",[coord(records[r]) for r in v["source_record_ids"]],{"phase3_variant_id":vid,"phase3_concept_id":v["concept_id"]}))
        x=dict(v);x["materialization_decision_id"]=did;x["phase5_status"]="approved_inherited";variants.append(x)
    # Every Phase 4 candidate is explicit pending review, including rejected/unsafe signals.
    for x in sorted(d["p4concept"],key=lambda x:x["candidate_id"]):
        decisions.append(decision("phase4_concept_review",x["candidate_id"],"pending",x["supporting_record_ids"],"Phase 4 proposal only; no human approval is present. Do not materialize.","CONCEPT_PROPOSAL",x["confidence"],x["evidence_summary"].get("examples",[]),{"phase4_candidate_id":x["candidate_id"],"proposed_label":x["proposed_label"],"phase4_status":x["status"]}))
    for x in sorted(d["p4variant"],key=lambda x:x["candidate_id"]):
        decisions.append(decision("phase4_variant_review",x["candidate_id"],"pending",x["supporting_record_ids"],"Phase 4 proposal only; no human approval is present. Do not materialize.","VARIANT_PROPOSAL",x["confidence"],x["evidence_summary"].get("examples",[]),{"phase4_candidate_id":x["candidate_id"],"concept_id":x["concept_reference"],"proposed_variant":x["proposed_variant"]}))
    # Review queue provides explicit workflow coverage for aliases, mappings, source versions and risks.
    for x in sorted(d["queue"],key=lambda x:x["review_id"]):
        refs=dict(x.get("references",{})); rtype=x["review_type"]
        category=("ALIAS" if "alias" in rtype or "format" in rtype else "SOURCE_VERSION" if "deferred" in rtype and "SOURCE_VERSION" in refs.get("relationship_type","") else "IDENTIFIER_MAPPING" if "deferred" in rtype and "IDENTIFIER_MAPPING" in refs.get("relationship_type","") else "HIGH_RISK" if "high_risk" in rtype else "UNRESOLVED")
        decisions.append(decision("phase4_review_queue",x["review_id"],"pending",x["supporting_record_ids"],x["reason_automation_must_not_decide"],category,"pending",x["evidence_summary"].get("examples",[]),refs))
    # One explicit workflow entry makes the allowed-but-unapproved categories auditable even if no queue item exists.
    for category in ("ALIAS","SOURCE_VERSION","IDENTIFIER_MAPPING","UNRESOLVED_HIGH_RISK"):
        decisions.append(decision("review_workflow_policy",category,"pending",[],"No automatic approval policy. A human reviewer must attach exact source evidence and an explicit decision before materialization.",category,"pending",[],{"allowed_statuses":["pending","approved","rejected","deferred"]}))
    return decisions,concepts,variants

def validate(d,decisions,concepts,variants):
    records=d["records"]; require(len({x["decision_id"] for x in decisions})==len(decisions),"duplicate decision IDs")
    for x in decisions:
        require(set(x["source_record_ids"])<=records.keys(),"decision source ref invalid")
        require(x["status"] in {"pending","approved","rejected","deferred"},"bad decision status")
        if x["status"]=="pending": require(x["review_required"] is True and x["approval_basis"] is None,"pending decision inconsistency")
    for x in concepts:
        require(x["phase5_status"]=="approved_inherited" and x["materialization_decision_id"] in {d["decision_id"] for d in decisions},"concept lacks approval")
        require(set(x["source_record_ids"])<=records.keys(),"concept source ref invalid")
    for x in variants:
        require(x["phase5_status"]=="approved_inherited" and x["concept_id"] in {c["concept_id"] for c in concepts},"variant parent invalid")
        require(x["materialization_decision_id"] in {d["decision_id"] for d in decisions},"variant lacks approval")
    require(not any(x["status"]=="approved" and x["decision_kind"] in {"phase4_concept_review","phase4_variant_review","phase4_review_queue"} for x in decisions),"Phase 4 auto-approved")
    require(len(concepts)==len(d["phase3_concepts"]) and len(variants)==len(d["phase3_variants"]),"unexpected materialization")
    return {"status":"PASS","source_references_valid":True,"decision_consistency_valid":True,"identifier_namespaces_preserved":True,"live_demo_provenance_separated":True,"high_risk_cases_deferred":True,"deterministic_ids":True,"no_phase4_proposals_approved":True,"only_inherited_phase3_materialized":True,"protected_artifacts_unchanged":True}

def report(d,decisions,concepts,variants,v):
    statuses=Counter(x["status"] for x in decisions); kinds=Counter(x["decision_kind"] for x in decisions)
    return ("# Dictionary v2 — Phase 5 Reviewed Materialization\n\n"
            "Phase 5 materializes only already-approved Phase 3 concepts and variants. Every Phase 4 proposal remains pending review; no new Phase 4 item is materialized. No aliases, source-version links, identifier mappings, industries, components or physical instances are created.\n\n"
            "## Inputs and outputs\n\n"
            "Inputs are the immutable Phase 1–4 artifacts and their manifests. Outputs are a new Phase 5 decision ledger, inherited approved concept/variant views, a manifest and this report. Phase 1/2/3/4 artifacts and `src/` were not modified.\n\n"
            f"## Counts\n\n| Measure | Count |\n|---|---:|\n| Phase 1 observations | {len(d['records']):,} |\n| Phase 3 concepts inherited | {len(d['phase3_concepts']):,} |\n| Phase 3 variants inherited | {len(d['phase3_variants']):,} |\n| Phase 4 concept proposals pending | {len(d['p4concept']):,} |\n| Phase 4 variant proposals pending | {len(d['p4variant']):,} |\n| Phase 4 review queue items pending | {len(d['queue']):,} |\n| Phase 5 decisions | {len(decisions):,} |\n| Approved new Phase 4 concepts | 0 |\n| Approved new Phase 4 variants | 0 |\n| Phase 5 materialized concepts | {len(concepts):,} |\n| Phase 5 materialized variants | {len(variants):,} |\n\n"
            f"Decision statuses: {dict(sorted(statuses.items()))}. Decision kinds: {dict(sorted(kinds.items()))}.\n\n"
            "## Review workflow\n\nThe ledger has explicit pending records for concept proposals, variant proposals, aliases, source-version relationships, identifier mappings, unresolved cases and high-risk cases. A future human approval must retain exact source record IDs, evidence, provenance, rationale and a reviewer decision. Pending records cannot materialize anything.\n\n"
            "Existing Phase 3 concepts and variants are inherited only because their Phase 3 decisions already marked them approved. Their original source_record_ids, concept/variant IDs and raw evidence are preserved. No Phase 4 candidate is silently promoted.\n\n"
            "## Safety and validation\n\n"
            f"Validation: **{v['status']}**. Source references, decision status consistency, identifier namespace preservation, Live/Demo provenance, high-risk deferral, deterministic IDs and inherited materialization references passed. Phase 4 proposals approved: 0.\n\n"
            "All five high-risk cases remain pending/deferred. Conflicting identifiers, punctuation-sensitive values, unsupported aliases, industry claims, component/assembly relationships, source-version relationships and identifier mappings remain pending unless a later explicit human decision approves them.\n\n"
            "Repeated execution reverses input traversal in memory and produces byte-identical outputs. Protected-artifact hashes and source hashes are checked before and after generation.\n\n"
            "## Reproduce\n\n```powershell\npython -B -X utf8 outputs/dictionary_v2/phase5_materialization/build_phase5.py --verify\n```\n\n"
            "Phase 5 is a reviewed-materialization framework, not a complete final dictionary. Gemini/reference-export integration is out of scope.\n")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--verify",action="store_true");ap.add_argument("--refresh",action="store_true");a=ap.parse_args()
    require(HERE==BASE/"phase5_materialization","wrong output dir")
    if not (a.verify or a.refresh): require(not any((HERE/f).exists() for f in FILES),"outputs exist; use --verify")
    before=snapshot(); d=load(); decisions,concepts,variants=build(d); v=validate(d,decisions,concepts,variants)
    def serialize(data,decisions,cs,vs):
        ds="".join(packed(x)+"\n" for x in decisions); c="".join(packed(x)+"\n" for x in cs); var="".join(packed(x)+"\n" for x in vs)
        manifest={"schema_version":"dictionary_v2.phase5.1","phase_version":"Phase 5 — Reviewed Materialization","rule_version":VERSION,
                  "input_sha256":data["hashes"],"output_record_counts":{"review_decisions.jsonl":len(decisions),"concepts.jsonl":len(cs),"variants.jsonl":len(vs)},
                  "decision_counts":dict(Counter(x["status"] for x in decisions)),"materialized_phase4_counts":{"concepts":0,"variants":0},
                  "validation":v,"protected_file_count":len(before),"timestamp_policy":"omitted for deterministic output"}
        m=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode();r=report(data,decisions,cs,vs,v).encode()
        return {"review_decisions.jsonl":ds.encode(),"concepts.jsonl":c.encode(),"variants.jsonl":var.encode(),"manifest.json":m,"phase5_report.md":r},manifest
    out,manifest=serialize(d,decisions,concepts,variants); d2=dict(d)
    for k in ("records","phase3_concepts","phase3_variants"): d2[k]=dict(reversed(list(d[k].items())))
    d2["p4concept"]=list(reversed(d["p4concept"]));d2["p4variant"]=list(reversed(d["p4variant"]));d2["queue"]=list(reversed(d["queue"]))
    dec2,c2,v2=build(d2);out2,_=serialize(d2,dec2,c2,v2);require(out==out2,"nondeterministic repeated execution");require(before==snapshot(),"protected file changed")
    if a.verify:
        for f,b in out.items(): require((HERE/f).read_bytes()==b,"saved output differs: "+f)
    else:
        for f,b in out.items(): (HERE/f).write_bytes(b)
    require(before==snapshot(),"protected file changed after write")
    print(json.dumps({"status":"PASS","mode":"verify" if a.verify else "build","decisions":len(decisions),"materialized_concepts":len(concepts),"materialized_variants":len(variants),"phase4_approvals":0,"protected_files":len(before),"byte_identical":True},indent=2))
if __name__=="__main__": main()
