"""Deterministic, fail-closed synchronization of induction state into research notes.

The registry and immutable captures remain authoritative.  This script creates a
derived representation ledger and a generated notes section; it never changes
review, promotion, or scientific content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "governance/live/induction_queue.json"
INDUCTIONS = ROOT / "registry/induction_registry.json"
INTAKE = ROOT / "departments/analysis_intake/induction_queue/queue_registry.json"
CAPTURE_DIR = ROOT / "departments/analysis_intake/chat_captures"
NOTES = ROOT / "docs/textbook/mono_process_textbook_complete.md"
LEDGER = ROOT / "governance/live/representation_ledger.json"
REPORT_DIR = ROOT / "departments/analysis/crawl_reports"
START = "<!-- BEGIN AUTO-SYNCHRONIZED GOVERNED RESEARCH STATE -->"
END = "<!-- END AUTO-SYNCHRONIZED GOVERNED RESEARCH STATE -->"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    if path.resolve() == NOTES.resolve() and path.is_file():
        text = path.read_text(encoding="utf-8")
        if START in text and END in text:
            text = text[:text.index(START)] + text[text.index(END) + len(END):]
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_hash(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def canonical_id(record: dict) -> str | None:
    return record.get("induction_id") or record.get("proposal_id")


def source_record(*records: dict) -> dict:
    candidates = []
    for record in records:
        if not record:
            continue
        candidates += [record.get("source_path"), record.get("source_artifact"), record.get("capture_path"), record.get("linked_governance_patch")]
        candidates += record.get("source_artifacts", []) or []
    candidates = [x for x in candidates if x]
    for path in candidates:
        p = ROOT / path
        if p.is_file():
            return {"path": str(path).replace("\\", "/"), "exists": True, "hash": sha256(p)}
    return {"path": str(candidates[0]).replace("\\", "/") if candidates else None, "exists": False, "hash": None}


def discover_preserved_captures() -> list[dict]:
    """Discover receipt-backed immutable captures before queue induction."""
    receipts = []
    for path in sorted(CAPTURE_DIR.glob("*.json"), key=lambda item: item.name.lower()):
        try:
            record = load(path)
        except (OSError, json.JSONDecodeError):
            continue
        preserved = record.get("preserved_path") or record.get("capture_path")
        if preserved and (record.get("source_sha256") or record.get("preserved_sha256")):
            receipts.append((path, record, str(preserved).replace("\\", "/")))
    captures = []
    for receipt_path, receipt, preserved in receipts:
        capture_path = ROOT / preserved
        if not capture_path.is_file():
            continue
        capture_status = receipt.get("preservation_status") or receipt.get("capture_status")
        if capture_status not in {"PRESERVED_LITERAL", "PRESERVED_PROVISIONAL", "APPENDED_WITH_PARENT_IMMUTABLE", "INDUCTED"}:
            continue
        capture_hash = sha256(capture_path)
        registered_hash = (receipt.get("preserved_sha256") or receipt.get("source_sha256") or "").lower()
        if registered_hash and registered_hash != capture_hash.lower():
            captures.append({"receipt_path": str(receipt_path.relative_to(ROOT)).replace("\\", "/"), "capture_path": preserved, "hash_conflict": {"registered": registered_hash, "actual": capture_hash}})
            continue
        capture_id = receipt.get("capture_id") or receipt.get("induction_id") or f"CAPTURE_{stable_hash({'path': preserved, 'sha256': capture_hash})[:20]}"
        captures.append({
            "capture_id": capture_id,
            "capture_path": preserved,
            "receipt_path": str(receipt_path.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": capture_hash.upper(),
            "capture_status": capture_status,
            "review_status": receipt.get("review_status", "NOT_REVIEWED"),
            "promotion_status": receipt.get("promotion_status", "HOLD_C1"),
            "induction_status": receipt.get("induction_status", "NOT_QUEUED"),
            "title": Path(preserved).stem,
        })
    return captures


def collect() -> tuple[list[dict], list[dict]]:
    queue = load(QUEUE).get("queue", [])
    induction = load(INDUCTIONS).get("entries", [])
    intake = load(INTAKE).get("entries", [])
    preserved = discover_preserved_captures()
    by_id: dict[str, dict] = {}
    conflicts: list[dict] = []
    for capture in preserved:
        cid = capture.get("capture_id")
        item = by_id.setdefault(cid, {"induction_id": cid, "sources": {}, "queue": None, "registry": None, "intake": None, "capture": capture})
        item["capture"] = capture
        if capture.get("hash_conflict"):
            conflicts.append({"type": "CAPTURE_HASH_CONFLICT", "induction_id": cid, **capture["hash_conflict"]})
    for origin, records in (("global_queue", queue), ("induction_registry", induction), ("intake", intake)):
        for record in records:
            cid = canonical_id(record)
            if not cid:
                conflicts.append({"type": "MISSING_INDUCTION_ID", "origin": origin, "record": record})
                continue
            item = by_id.setdefault(cid, {"induction_id": cid, "sources": {}, "queue": None, "registry": None, "intake": None, "capture": None})
            target_key = {"global_queue": "queue", "induction_registry": "registry", "intake": "intake"}[origin]
            item[target_key] = record
    entries: list[dict] = []
    for cid in sorted(by_id):
        item = by_id[cid]
        q = item.get("queue") or {}
        r = item.get("registry") or {}
        i = item.get("intake") or {}
        c = item.get("capture") or {}
        src = source_record(c, q, i, r)
        statuses = {
            "queue_status": q.get("status", "NOT_PRESENT"),
            "registry_status": r.get("status", "NOT_BOUND"),
            "review_status": c.get("review_status", q.get("review_status", i.get("review_status", r.get("review_status", "NOT_RECORDED")))),
            "promotion_status": c.get("promotion_status", q.get("promotion_status", i.get("promotion_status", r.get("promotion_status", "NOT_RECORDED")))),
            "capture_status": c.get("capture_status", i.get("preservation_status", q.get("preservation_status", "NOT_RECORDED"))),
            "induction_status": c.get("induction_status", q.get("induction_status", r.get("induction_status", "NOT_QUEUED"))),
        }
        if q and not r:
            section = "NOTES_QUEUED"
        elif statuses["review_status"] in {"NOT_REVIEWED", "PARTIAL"}:
            section = "NOTES_UNDER_REVIEW"
        elif statuses["registry_status"] in {"EXCLUDED_FROZEN", "REJECTED"} or statuses["queue_status"] in {"excluded_frozen", "rejected"}:
            section = "NOTES_ARCHIVED"
        elif statuses["promotion_status"] in {"HOLD_C1", "UNQUEUED_FOR_PROMOTION"}:
            section = "NOTES_OPEN_WORK"
        else:
            section = "NOTES_ACTIVE"
        if statuses["capture_status"] in {"PRESERVED_PROVISIONAL", "PRESERVED_LITERAL", "APPENDED_WITH_PARENT_IMMUTABLE"} and not q and not r:
            section = "NOTES_PENDING_PRESERVED"
        entries.append({
            "entry_id": f"NOTE_{cid}",
            "title": r.get("title") or q.get("title") or i.get("proposal_id") or c.get("title") or cid,
            "source_induction_id": cid,
            "capture_path": c.get("capture_path") or src["path"],
            "receipt_path": c.get("receipt_path"),
            "capture_hash": c.get("source_sha256") or i.get("source_sha256") or q.get("source_sha256") or src["hash"],
            "source_trace": {"path": c.get("capture_path") or src["path"], "receipt_path": c.get("receipt_path"), "verified_hash": src["hash"], "immutable_source_available": src["exists"]},
            "capture_status": statuses["capture_status"],
            "queue_status": statuses["queue_status"],
            "registry_status": statuses["registry_status"],
            "review_status": statuses["review_status"],
            "promotion_status": statuses["promotion_status"],
            "induction_status": statuses["induction_status"],
            "representation_status": "ACTIVE",
            "current_notes_section": section,
            "source_summary": r.get("notes") or q.get("notes") or i.get("notes") or "Preserved Analysis Intake capture.",
            "open_conditions": [],
            "target_locations": [section],
            "last_synchronized_at": None,
            "synchronization_run_id": None,
        })
        registered_hash = c.get("source_sha256") or i.get("source_sha256") or q.get("source_sha256") or r.get("source_sha256")
        if registered_hash and src["hash"] and registered_hash.lower() != src["hash"].lower():
            conflicts.append({"type": "CAPTURE_HASH_CONFLICT", "induction_id": cid, "registered": registered_hash, "actual": src["hash"]})
        if not src["exists"] and src["path"]:
            conflicts.append({"type": "MISSING_IMMUTABLE_CAPTURE", "induction_id": cid, "path": src["path"]})
        if q and not r:
            conflicts.append({"type": "UNMAPPED_QUEUE_RECORD", "induction_id": cid, "detail": "queued record has no canonical registry binding; pending-link state is visible in the generated notes projection"})
    return entries, conflicts


def render(entries: list[dict]) -> str:
    buckets: dict[str, list[dict]] = {}
    for e in entries:
        buckets.setdefault(e["current_notes_section"], []).append(e)
    headings = {
        "NOTES_PENDING_PRESERVED": "Preserved Proposals — Not Yet Inducted",
        "NOTES_QUEUED": "Queued Research Contributions",
        "NOTES_ACTIVE": "Active Governed Research Notes",
        "NOTES_OPEN_WORK": "Open Definitions, Obligations, and Unresolved Work",
        "NOTES_UNDER_REVIEW": "Under Review",
        "NOTES_INTEGRATED": "Integrated Research Notes",
        "NOTES_SUPERSEDED": "Superseded Research Notes",
        "NOTES_ARCHIVED": "Archived or Explicitly Excluded Research Notes",
    }
    lines = [START, "", "This section is generated from canonical induction, queue, intake, and representation records. It is a projection, not an authority source.", ""]
    for key in headings:
        lines += [f"## {headings[key]}", ""]
        for e in buckets.get(key, []):
            lines += [f"- **{e['title']}** (`{e['source_induction_id']}`): {e['source_summary']}", f"  - Capture: `{e['capture_status']}`; Review: `{e['review_status']}`; Promotion: `{e['promotion_status']}`; Induction: `{e.get('induction_status', 'NOT_RECORDED')}`", f"  - Queue: `{e['queue_status']}`; Registry: `{e['registry_status']}`", f"  - Source: `{e['capture_path']}`; receipt: `{e.get('receipt_path') or 'NOT_RECORDED'}`; SHA-256: `{e['capture_hash'] or 'UNAVAILABLE'}`", ""]
        if not buckets.get(key):
            lines += ["_None recorded._", ""]
    lines += [END]
    return "\n".join(lines)


def sync(args) -> int:
    run_id = "SYNC_GOVERNANCE_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    entries, conflicts = collect()
    report = {
        "sync_run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "input_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in (QUEUE, INDUCTIONS, INTAKE)},
        "output_hashes": {},
        "captures_examined": len(entries),
        "preserved_captures_examined": len(discover_preserved_captures()),
        "preserved_only_entries": [e["source_induction_id"] for e in entries if e["current_notes_section"] == "NOTES_PENDING_PRESERVED"],
        "queue_records_examined": len(load(QUEUE).get("queue", [])),
        "registry_records_examined": len(load(INDUCTIONS).get("entries", [])),
        "notes_entries_created": len(entries),
        "notes_entries_updated": 0,
        "notes_entries_moved": 0,
        "notes_entries_archived": 0,
        "unchanged_entries": 0,
        "missing_links_repaired": 0,
        "conflicts": conflicts,
            "unmapped_records": [c for c in conflicts if c["type"] == "UNMAPPED_QUEUE_RECORD"],
        "validation_results": {"traceability": not any(c["type"] == "MISSING_IMMUTABLE_CAPTURE" for c in conflicts), "reconciliation": not any(c["type"] not in {"UNMAPPED_QUEUE_RECORD"} for c in conflicts), "pending_links_visible": True, "idempotence": "NOT_RUN"},
        "runtime_refresh_status": "NOT_REQUESTED",
        "overall_status": "FAIL_CLOSED" if any(c["type"] != "UNMAPPED_QUEUE_RECORD" for c in conflicts) else ("PASS_WITH_REPAIRS" if conflicts else "PASS"),
    }
    fatal_conflicts = any(c["type"] != "UNMAPPED_QUEUE_RECORD" for c in conflicts)
    if fatal_conflicts or args.check or not args.apply:
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        out_dir = ROOT / "audit_outputs/governance_sync"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"sync_governance_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["overall_status"], "report": str(out), "conflicts": len(conflicts)}, indent=2))
        return 2 if fatal_conflicts else 0
    ledger = {"ledger_id": "REPRESENTATION_LEDGER_001", "schema_version": "1.0.0", "authority": "Governed projection; canonical sources remain authoritative.", "entries": entries}
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    old = NOTES.read_text(encoding="utf-8")
    generated = render(entries)
    existing_region = None
    existing_text = NOTES.read_text(encoding="utf-8") if NOTES.is_file() else ""
    if START in existing_text and END in existing_text:
        existing_region = existing_text[existing_text.index(START):existing_text.index(END) + len(END)]
    report["validation_results"]["idempotence"] = "PASS" if existing_region == generated else "NOT_YET_ESTABLISHED"
    if START in old or END in old:
        if START not in old or END not in old or old.index(START) > old.index(END):
            raise SystemExit("FAIL_CLOSED: invalid generated-region markers")
        new = old[:old.index(START)] + generated + old[old.index(END) + len(END):]
    else:
        new = old.rstrip() + "\n\n" + generated
    if not args.dry_run:
        fd, temp = tempfile.mkstemp(prefix="notes-sync-", suffix=".md", dir=str(NOTES.parent))
        os.close(fd)
        Path(temp).write_text(new, encoding="utf-8")
        os.replace(temp, NOTES)
    if args.refresh_db:
        result = subprocess.run(["python", "scripts/db/snapshot_registries.py"], cwd=ROOT, capture_output=True, text=True)
        report["runtime_refresh_status"] = "PASS" if result.returncode == 0 else "FAIL_CLOSED"
        if result.returncode != 0:
            report["overall_status"] = "FAIL_CLOSED"
            report["conflicts"].append({"type": "RUNTIME_REFRESH_FAILURE", "detail": result.stderr[-2000:]})
    report["output_hashes"] = {"representation_ledger": sha256(LEDGER), "notes_projection": stable_hash(generated)}
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    out_dir = ROOT / "audit_outputs/governance_sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"sync_governance_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["overall_status"], "report": str(out), "entries": len(entries)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--fail-closed", action="store_true")
    parser.add_argument("--repair-missing", action="store_true")
    parser.add_argument("--induction-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--notes", action="store_true")
    parser.add_argument("--refresh-db", action="store_true", help="refresh the runtime database after canonical validation")
    args = parser.parse_args()
    if args.check:
        args.apply = False
    if args.dry_run:
        args.apply = False
    return sync(args)


if __name__ == "__main__":
    raise SystemExit(main())
