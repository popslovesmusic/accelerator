"""Idempotent registration of inducted intake into non-canonical research memory."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "departments/analysis_intake/chat_captures"
QUEUE = ROOT / "departments/analysis_intake/induction_queue/queue_registry.json"
REGISTRY = ROOT / "registry/induction_registry.json"
RESEARCH = ROOT / "departments/research"
REPORTS = RESEARCH / "reports"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def first_text(value, default=""):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("statement") or value.get("definition") or value.get("meaning") or default
    return default


def register(ids: list[str], apply: bool) -> dict:
    queue_entries = read(QUEUE).get("entries", [])
    induction_entries = read(REGISTRY).get("entries", [])
    queue_by_id = {e.get("proposal_id"): e for e in queue_entries}
    registry_by_id = {e.get("induction_id"): e for e in induction_entries}
    report = {"run_id": "RIT_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), "records": [], "overall_status": "PASS"}

    for packet_id in sorted(ids):
        source = CAPTURES / f"{packet_id}.json"
        if not source.is_file():
            report["records"].append({"packet_id": packet_id, "status": "RESEARCH_BLOCKED_VISIBLE", "blocker": "MISSING_SOURCE_CAPTURE"})
            report["overall_status"] = "FAIL_CLOSED"
            continue
        capture = read(source)
        q = queue_by_id.get(packet_id, {})
        reg = registry_by_id.get(packet_id, {})
        source_hash = digest(source)
        expected_hash = q.get("source_sha256")
        if expected_hash and expected_hash.upper() != source_hash:
            report["records"].append({"packet_id": packet_id, "status": "RESEARCH_BLOCKED_VISIBLE", "blocker": "SOURCE_HASH_CONFLICT"})
            report["overall_status"] = "FAIL_CLOSED"
            continue
        partial = bool(q.get("blockers")) or capture.get("status") == "PRESERVED_PARTIAL"
        research_id = f"RR_{packet_id}"
        status = "RESEARCH_BLOCKED_VISIBLE" if partial else "RESEARCH_REGISTERED"
        concepts = []
        entities = capture.get("foundational_entities") or capture.get("core_definitions") or capture.get("provisional_formalization") or {}
        if isinstance(entities, dict):
            for label in sorted(entities):
                concept_id = f"CONCEPT_{packet_id}_{label.upper().replace('-', '_')}"
                concepts.append(concept_id)
                write_json(RESEARCH / "concepts" / f"{concept_id}.json", {
                    "concept_id": concept_id, "preferred_label": label, "aliases": [],
                    "source_packet_ids": [packet_id], "first_contact_source": str(source.relative_to(ROOT)).replace('\\', '/'),
                    "first_seen_at": capture.get("capture_timestamp_utc"), "status": "PROVISIONAL_UNREVIEWED",
                    "definition_candidates": [first_text(entities[label], "")], "related_concepts": [], "open_questions": capture.get("formalization_obligations", [])
                })
        derivation_id = f"DERIVATION_{packet_id}"
        derivation_text = capture.get("primary_mechanism", {}).get("sequence") or capture.get("provisional_formalization", {}).get("expanded_chain") or capture.get("candidate_statement", {}).get("compact") or " -> ".join(capture.get("calculus_cycle", []))
        derivations = []
        if derivation_text:
            derivations = [derivation_id]
            write_json(RESEARCH / "derivations" / f"{derivation_id}.json", {
                "derivation_id": derivation_id, "source_packet_ids": [packet_id], "parent_concepts": concepts,
                "derived_concepts": concepts, "derivation_text": derivation_text, "assumptions": capture.get("interpretive_constraints", []),
                "dependencies": capture.get("formalization_obligations", []), "claim_ceiling": capture.get("claim_ceiling", "PROVISIONAL"),
                "review_status": "NOT_REVIEWED", "status": "UNASSESSED_DERIVATION", "source_trace": {"path": str(source.relative_to(ROOT)).replace('\\', '/'), "sha256": source_hash}
            })
        open_questions = capture.get("formalization_obligations") or capture.get("obligation_updates", {}).get("remaining_open", []) or capture.get("remaining_open", []) or capture.get("open_research", [])
        dependencies = capture.get("dependency_effects") or capture.get("dependencies") or []
        record = {
            "record_type": "research_record", "research_record_id": research_id,
            "queue_entry_id": q.get("queue_entry_id"), "proposal_id": packet_id,
            "source_path": str(source.relative_to(ROOT)).replace('\\', '/'), "source_sha256": source_hash,
            "source_timestamp": capture.get("capture_timestamp_utc"), "source_channel": capture.get("source_channel"),
            "capture_mode": capture.get("capture_type"), "preservation_status": q.get("preservation_status", "PRESERVED_LITERAL"),
            "induction_status": "INDUCTED", "research_status": status, "review_status": q.get("review_status", "NOT_REVIEWED"),
            "promotion_status": q.get("promotion_status", "HOLD_C1"), "canonicality": q.get("canonicality", "NON_CANONICAL_CANDIDATE"),
            "claim_ceiling": capture.get("claim_ceiling", reg.get("claim_ceiling", "PROVISIONAL")), "concepts": concepts,
            "candidate_definitions": capture.get("candidate_statement", {}), "derivations": derivations,
            "dependencies": dependencies, "open_questions": open_questions, "ambiguities": capture.get("ambiguities", []),
            "risks": capture.get("risks", []), "applications": capture.get("applications", []), "parent_links": [], "child_links": [],
            "aliases": [], "source_trace": {"capture_path": str(source.relative_to(ROOT)).replace('\\', '/'), "sha256": source_hash, "immutable": True},
            "created_at": capture.get("capture_timestamp_utc"), "updated_at": datetime.now(timezone.utc).isoformat(),
            "blockers": q.get("blockers", []) if partial else []
        }
        if apply:
            write_json(RESEARCH / "records" / f"{research_id}.json", record)
            write_json(RESEARCH / "dependencies" / f"{research_id}.json", {"research_record_id": research_id, "dependencies": dependencies, "source_trace": record["source_trace"]})
            write_json(RESEARCH / "open_questions" / f"{research_id}.json", {"research_record_id": research_id, "open_questions": open_questions, "source_trace": record["source_trace"]})
        report["records"].append({"packet_id": packet_id, "research_record_id": research_id, "status": status, "concept_count": len(concepts), "derivation_count": len(derivations), "source_sha256": source_hash})
    if apply:
        index = {"index_id": "RESEARCH_INDEX_001", "schema_version": "1.0.0", "records": report["records"], "authority": "Non-canonical research memory; source captures remain authoritative."}
        write_json(RESEARCH / "indexes" / "research_index.json", index)
        write_json(REPORTS / f"research_intake_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--fail-closed", action="store_true")
    args = parser.parse_args()
    ids = ["RT_ASYM_OBSERVATION_ORIENTATION_EXCLUSION_INDUCTION_20260728_001", "RT_BOUNDARY_ORIENTATION_ASYM_INDUCTION_20260728_001", "RT_ASYM_SYMBOL_TYPE_RECONCILIATION_20260728_001", "RT_INDUCTION_MTO_OTM_CALCULUS_001"]
    result = register(ids, args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 2 if result["overall_status"] == "FAIL_CLOSED" and args.fail_closed else 0


if __name__ == "__main__":
    raise SystemExit(main())
