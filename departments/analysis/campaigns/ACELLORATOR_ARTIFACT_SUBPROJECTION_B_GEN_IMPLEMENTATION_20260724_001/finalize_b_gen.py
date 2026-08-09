import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--run1", type=Path, required=True)
    p.add_argument("--run2", type=Path, required=True)
    p.add_argument("--bgov", type=Path, required=True)
    p.add_argument("--bws", type=Path, required=True)
    args = p.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    c1 = load(args.run1 / "b_gen_generated_catalog.json")
    c2 = load(args.run2 / "b_gen_generated_catalog.json")
    bgov = load(args.bgov)
    bws = load(args.bws)
    records = c1["records"]
    ids = [item["canonical_identity"] for item in records]
    bgov_ids = {item["canonical_identity"] for item in bgov.get("records", [])}
    bws_ids = {item["canonical_identity"] for item in bws.get("records", [])}
    namespace_collisions = (set(ids) & bgov_ids) | (set(ids) & bws_ids)
    forbidden = [
        item["normalized_output_path"] for item in records
        if item["normalized_output_path"] == "docs"
        or item["normalized_output_path"].startswith(("docs/", "registry/"))
        or Path(item["normalized_output_path"]).suffix.casefold() in {".sqlite", ".sqlite3", ".db", ".wal", ".shm", ".journal"}
    ]
    missing_provenance = [item["canonical_identity"] for item in records if not item.get("provenance") or not item.get("generator_id")]
    classes = {item["artifact_class"] for item in records}
    checks = {
        "record_count_positive": len(records) > 0,
        "canonical_identity_unique": len(ids) == len(set(ids)),
        "all_records_generated_namespace": all(item.startswith("generated_artifact:") for item in ids),
        "all_records_have_provenance": not missing_provenance,
        "database_artifacts_excluded": not forbidden,
        "cross_subprojection_collisions_absent": not namespace_collisions,
        "repeat_catalog_equal": c1["ordered_rows_sha256"] == c2["ordered_rows_sha256"],
        "repeat_record_count_equal": len(c1["records"]) == len(c2["records"]),
        "no_scan_errors": not c1.get("errors"),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "builder_id": "B-GEN",
        "builder_version": "B-GEN-1.0.0",
        "status": status,
        "checks": checks,
        "observed": {
            "record_count": len(records),
            "artifact_class_counts": {name: sum(1 for item in records if item["artifact_class"] == name) for name in sorted(classes)},
            "forbidden_records": forbidden,
            "missing_provenance": missing_provenance,
            "cross_subprojection_collisions": sorted(namespace_collisions),
        },
        "scope_note": "B-GEN is a derived non-production catalog of recognized generated deliverables. Governed sources, workspace-only records, runtime/database artifacts, and historical-only records remain separate subprojections.",
    }
    write(out / "b_gen_validation_results.json", validation)
    write(out / "b_gen_boundary_validation.json", {
        "status": status,
        "b_gov_dependency": "FROZEN_VALIDATED",
        "b_ws_dependency": "FROZEN_VALIDATED",
        "b_gen_namespace": "generated_artifact:",
        "forbidden_authority_roots": ["docs", "registry"],
        "excluded_database_extensions": [".sqlite", ".sqlite3", ".db", ".wal", ".shm", ".journal"],
        "excluded_raw_result_policy": "outputs/results/validation files are admitted only when recognized as generated deliverables by name or Markdown/archive extension",
        "forbidden_records": forbidden,
        "cross_subprojection_collisions": sorted(namespace_collisions),
    })
    write(out / "b_gen_repeat_build_hashes.json", {
        "status": "PASS" if checks["repeat_catalog_equal"] and checks["repeat_record_count_equal"] else "FAIL",
        "repeat_1_catalog_sha256": sha256(args.run1 / "b_gen_generated_catalog.json"),
        "repeat_2_catalog_sha256": sha256(args.run2 / "b_gen_generated_catalog.json"),
        "ordered_rows_sha256": [c1["ordered_rows_sha256"], c2["ordered_rows_sha256"]],
        "record_counts": [len(c1["records"]), len(c2["records"])],
    })
    freeze = "FROZEN_VALIDATED" if status == "PASS" else "NOT_FROZEN"
    write(out / "b_gen_freeze_manifest.json", {
        "builder_id": "B-GEN",
        "builder_version": "B-GEN-1.0.0",
        "builder_maturity": "L4_FROZEN_REFERENCE_IMPLEMENTATION" if freeze == "FROZEN_VALIDATED" else "UNASSIGNED",
        "freeze_status": freeze,
        "freeze_criteria": {
            "contract_boundary": status,
            "provenance": "PASS" if checks["all_records_have_provenance"] else "FAIL",
            "repeat_build_determinism": "PASS" if checks["repeat_catalog_equal"] and checks["repeat_record_count_equal"] else "FAIL",
            "database_exclusion": "PASS" if checks["database_artifacts_excluded"] else "FAIL",
        },
        "ordered_rows_sha256": c1["ordered_rows_sha256"],
        "freeze_rule": "Modification requires B_GEN_REVISION_AND_REVALIDATION_PACKET",
        "production_cutover_authorized": False,
    })
    write(out / "b_gen_provenance_report.json", {
        "status": "PASS" if checks["all_records_have_provenance"] else "FAIL",
        "builder_id": "B-GEN",
        "record_count": len(records),
        "generator_id_policy": "top-level generated root or root_generated for generated root files",
        "provenance_fields": ["builder_id", "builder_version", "observation", "source_root"],
        "missing_provenance": missing_provenance,
    })
    write(out / "artifact_subprojection_progress_matrix.json", {
        "projection_family": "artifacts",
        "governed_source_inventory": "FROZEN_VALIDATED",
        "workspace_artifact_catalog": "FROZEN_VALIDATED",
        "generated_artifact_catalog": freeze,
        "runtime_transient_catalog": "NOT_STARTED",
        "historical_artifact_register": "NOT_STARTED",
        "composite_view": "NOT_STARTED",
    })
    summary = f"""# B-GEN Implementation Summary

## Result

B-GEN (`generated_artifact_catalog`) is `{freeze}` with maturity `{'L4_FROZEN_REFERENCE_IMPLEMENTATION' if freeze == 'FROZEN_VALIDATED' else 'UNASSIGNED'}`.

## Measured output

- Records: {len(records)}
- Scan errors: {len(c1.get('errors', []))}
- Ordered rows SHA-256: `{c1['ordered_rows_sha256']}`
- Repeat-build equality: `{'PASS' if checks['repeat_catalog_equal'] and checks['repeat_record_count_equal'] else 'FAIL'}`

## Boundary

B-GEN uses `generated_artifact:` identities and preserves B-GOV and B-WS namespaces. Database files and sidecars are excluded as runtime/database scope. Raw simulation/result payloads are not admitted unless recognized as generated deliverables by the explicit naming policy.

## Authority

The catalog is derived, rebuildable, and non-production. L4 refers to the frozen reference implementation maturity of this builder, not canonical authority or production cutover authorization.
"""
    (out / "b_gen_implementation_summary.md").write_text(summary, encoding="utf-8")
    entries = []
    for path in sorted(out.iterdir(), key=lambda item: item.name):
        if path.name in {"deliverable_manifest.json", "b_gen_checkpoint.json"} or not path.is_file():
            continue
        entries.append({"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "derived_or_authoritative": "DERIVED_REBUILDABLE", "source_packet_id": "ACELLORATOR_ARTIFACT_SUBPROJECTION_B_GEN_IMPLEMENTATION_20260724_001"})
    write(out / "deliverable_manifest.json", {"created_at": datetime.now(timezone.utc).isoformat(), "source_packet_id": "ACELLORATOR_ARTIFACT_SUBPROJECTION_B_GEN_IMPLEMENTATION_20260724_001", "entries": entries})


if __name__ == "__main__":
    main()
