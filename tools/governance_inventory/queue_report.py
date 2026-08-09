from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ambiguity_risk import QUEUE_GROUP_ORDER, SEVERITY_ORDER
from .reachability_evidence import (
    DEFAULT_SOURCE_SNAPSHOT_FILES,
    build_source_snapshot,
    load_ambiguity_register,
    load_surface_inventory,
    normalize_path_like,
)
from .remediation_queue import build_remediation_queue_bundle


ROOT = Path(__file__).resolve().parents[2]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def build_queue_summary(queue_bundle: Mapping[str, Any]) -> dict[str, Any]:
    records = list(queue_bundle.get("records", []))
    top_25 = [
        {
            "queue_position": record["queue_position"],
            "ambiguity_id": record["ambiguity_id"],
            "source_record_id": record["source_record_id"],
            "path_or_table": record["path_or_table"],
            "queue_group": record["queue_group"],
            "severity": record["severity"],
            "risk_score": record["risk_score"],
            "risk_dimensions": record["risk_dimensions"],
            "recommended_resolution_mode": record["recommended_resolution_mode"],
            "authority_candidates": record["authority_candidates"],
        }
        for record in records[:25]
    ]
    summary = {
        "schema_id": "governance_remediation_queue_summary_v1",
        "schema_version": "1.0.0",
        "record_count": len(records),
        "counts": queue_bundle.get("counts", {}),
        "queue_group_order": list(QUEUE_GROUP_ORDER),
        "severity_order": list(SEVERITY_ORDER),
        "top_25_queue_records": top_25,
        "queue_logical_sha256": queue_bundle.get("logical_hash"),
        "classification_logical_sha256": queue_bundle.get("classification_logical_hash"),
        "source_snapshot": dict(queue_bundle.get("source_snapshot") or {}),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    summary["summary_logical_sha256"] = logical_sha256(
        {
            "schema_id": summary["schema_id"],
            "schema_version": summary["schema_version"],
            "record_count": summary["record_count"],
            "counts": summary["counts"],
            "queue_group_order": summary["queue_group_order"],
            "severity_order": summary["severity_order"],
            "top_25_queue_records": summary["top_25_queue_records"],
            "queue_logical_sha256": summary["queue_logical_sha256"],
        }
    )
    return summary


def build_queue_review_markdown(summary: Mapping[str, Any]) -> str:
    counts = summary.get("counts", {})
    queue_groups = counts.get("queue_groups", {})
    severity = counts.get("severity", {})
    ambiguity_class = counts.get("ambiguity_class", {})
    dimensions = counts.get("risk_dimensions", {})
    resolution_modes = counts.get("resolution_modes", {})
    top_records = summary.get("top_25_queue_records", [])
    lines = [
        "# Governance Ambiguity Remediation Queue Review",
        "",
        "## Scope",
        "Deterministic classification of the 514 blocking governance ambiguities.",
        "",
        "## Directly Observed",
        f"- Queue records: {summary.get('record_count', 0)}",
        f"- Queue logical hash: `{summary.get('queue_logical_sha256', '')}`",
        f"- Classification logical hash: `{summary.get('classification_logical_sha256', '')}`",
        "",
        "## Queue Groups",
    ]
    for group in QUEUE_GROUP_ORDER:
        lines.append(f"- {group}: {queue_groups.get(group, 0)}")
    lines.extend([
        "",
        "## Severity",
    ])
    for level in SEVERITY_ORDER:
        lines.append(f"- {level}: {severity.get(level, 0)}")
    lines.extend([
        "",
        "## Ambiguity Classes",
    ])
    for class_name, count in sorted(ambiguity_class.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {class_name}: {count}")
    lines.extend([
        "",
        "## Dominant Risk Dimensions",
    ])
    for dimension, count in sorted(dimensions.items(), key=lambda item: (-item[1], item[0]))[:10]:
        lines.append(f"- {dimension}: {count}")
    lines.extend([
        "",
        "## Resolution Modes",
    ])
    for mode, count in sorted(resolution_modes.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {mode}: {count}")
    lines.extend([
        "",
        "## Top 25 Queue Records",
    ])
    for record in top_records:
        lines.append(
            f"- {record['queue_position']}. {record['ambiguity_id']} | {record['queue_group']} | "
            f"{record['severity']} | {record['risk_score']} | {record['recommended_resolution_mode']}"
        )
    lines.extend([
        "",
        "## Failure Modes / Uncertainty",
        "- This report does not resolve any ambiguity.",
        "- Missing dependency packages remain a separate environment blocker for the full pytest collection.",
        "- Queue position is a remediation ordering signal, not a status change.",
    ])
    return "\n".join(lines) + "\n"


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _default_source_snapshot() -> dict[str, Any]:
    return build_source_snapshot(
        DEFAULT_SOURCE_SNAPSHOT_FILES,
        workspace_root_identity="acellorator@6ebf84a1e",
        repository_commit="6ebf84a1e",
        included_roots=[
            "docs/manual_repository_audit_2026_07_13.md",
            "docs/textbook/mono_process_textbook_complete.md",
            "governance/core_rules/",
            "governance/evidence_sets/",
            "governance/provenance/",
            "outputs/governance_inventory/",
            "patches/PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004.json",
            "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
        ],
        excluded_roots=[
            "Validation Department activation",
            "database migration",
            "fixing discovered conflicts",
            "governance rewriting",
            "mathematical claim promotion",
            "repository cleanup",
            "schema redesign",
            "scientific truth evaluation",
        ],
        file_count_scanned=1017,
        surface_count_detected=1083,
        working_tree_dirty=True,
        unrelated_changes_preserved=True,
    )


def write_queue_artifacts(
    *,
    classification_path: str | Path,
    queue_path: str | Path,
    summary_path: str | Path,
    review_path: str | Path,
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot = dict(source_snapshot or _default_source_snapshot())
    queue_bundle = build_remediation_queue_bundle(
        surface_inventory=surface_inventory or load_surface_inventory(),
        ambiguity_register=ambiguity_register or load_ambiguity_register(),
        source_snapshot=snapshot,
    )
    summary = build_queue_summary(queue_bundle)
    classification = {
        "schema_id": queue_bundle["source_classification_schema_id"],
        "schema_version": queue_bundle["source_classification_schema_version"],
        "core_rule_reference": queue_bundle["core_rule_reference"],
        "record_count": queue_bundle["record_count"],
        "counts": queue_bundle["counts"],
        "source_snapshot": snapshot,
        "records": sorted(queue_bundle["records"], key=lambda record: record["ambiguity_id"]),
        "logical_hash": queue_bundle["classification_logical_hash"],
    }
    _write_json(Path(classification_path), classification)
    _write_json(Path(queue_path), queue_bundle)
    _write_json(Path(summary_path), summary)
    Path(review_path).parent.mkdir(parents=True, exist_ok=True)
    Path(review_path).write_text(build_queue_review_markdown(summary), encoding="utf-8", newline="\n")
    return {
        "classification": classification,
        "queue": queue_bundle,
        "summary": summary,
        "review_markdown": build_queue_review_markdown(summary),
    }
