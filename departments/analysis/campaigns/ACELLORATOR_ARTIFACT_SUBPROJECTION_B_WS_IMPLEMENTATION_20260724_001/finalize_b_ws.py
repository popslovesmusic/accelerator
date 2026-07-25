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
    args = p.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    c1 = load(args.run1 / "b_ws_workspace_catalog.json")
    c2 = load(args.run2 / "b_ws_workspace_catalog.json")
    r1 = load(args.run1 / "b_ws_relationship_graph.json")
    r2 = load(args.run2 / "b_ws_relationship_graph.json")
    bgov = load(args.bgov)
    records = c1["records"]
    identities = [record["canonical_identity"] for record in records]
    paths = [record["normalized_workspace_relative_path"] for record in records]
    boundary_violations = [
        record["normalized_workspace_relative_path"]
        for record in records
        if record["normalized_workspace_relative_path"] == "docs"
        or record["normalized_workspace_relative_path"].startswith("docs/")
        or record["normalized_workspace_relative_path"] == "registry"
        or record["normalized_workspace_relative_path"].startswith("registry/")
        or record["normalized_workspace_relative_path"].startswith("departments/analysis/campaigns/")
    ]
    bgov_ids = {record["canonical_identity"] for record in bgov.get("records", [])}
    cross_namespace_collisions = set(identities) & bgov_ids
    validation = {
        "builder_id": "B-WS",
        "builder_version": "B-WS-1.0.0",
        "status": "PASS",
        "checks": {
            "record_count_positive": len(records) > 0,
            "canonical_identity_unique": len(identities) == len(set(identities)),
            "workspace_path_unique": len(paths) == len(set(paths)),
            "all_records_workspace_namespace": all(item.startswith("workspace_artifact:") for item in identities),
            "no_scan_errors": len(c1.get("errors", [])) == 0,
            "relationships_present": len(r1.get("relationships", [])) > 0,
            "b_gov_namespace_collision_absent": not cross_namespace_collisions,
            "repeat_catalog_equal": c1["ordered_rows_sha256"] == c2["ordered_rows_sha256"],
            "repeat_relationship_graph_equal": r1 == r2,
        },
        "observed": {
            "record_count": len(records),
            "relationship_count": len(r1.get("relationships", [])),
            "artifact_class_counts": {k: sum(1 for x in records if x["artifact_class"] == k) for k in sorted({x["artifact_class"] for x in records})},
            "boundary_violations": boundary_violations,
            "cross_namespace_collisions": sorted(cross_namespace_collisions),
        },
        "scope_note": "B-WS is a derived non-production workspace observation. Governed source semantics remain owned by B-GOV; generated, runtime, database, registry, documentation, and temporary roots are explicitly excluded.",
    }
    if not all(validation["checks"].values()):
        validation["status"] = "FAIL"
    write(out / "b_ws_validation_results.json", validation)
    write(out / "b_ws_boundary_validation.json", {
        "status": "PASS" if not boundary_violations and not cross_namespace_collisions else "FAIL",
        "b_gov_dependency": "FROZEN_VALIDATED",
        "b_gov_canonical_identity_namespace": "governed_source:",
        "b_ws_canonical_identity_namespace": "workspace_artifact:",
        "excluded_semantic_roots": ["docs", "registry"],
        "excluded_generated_runtime_roots": ["audit_outputs", "outputs", "validation", "audits", "governance_backups", "scratch", "state", "runtime", "results", "experiments", "departments/analysis/campaigns", ".tmp"],
        "boundary_violations": boundary_violations,
        "cross_namespace_collisions": sorted(cross_namespace_collisions),
    })
    write(out / "b_ws_repeat_build_hashes.json", {
        "status": "PASS" if validation["checks"]["repeat_catalog_equal"] and validation["checks"]["repeat_relationship_graph_equal"] else "FAIL",
        "repeat_1_catalog_sha256": sha256(args.run1 / "b_ws_workspace_catalog.json"),
        "repeat_2_catalog_sha256": sha256(args.run2 / "b_ws_workspace_catalog.json"),
        "repeat_1_relationship_sha256": sha256(args.run1 / "b_ws_relationship_graph.json"),
        "repeat_2_relationship_sha256": sha256(args.run2 / "b_ws_relationship_graph.json"),
        "ordered_rows_sha256": [c1["ordered_rows_sha256"], c2["ordered_rows_sha256"]],
        "record_counts": [len(c1["records"]), len(c2["records"])],
    })
    freeze_status = "FROZEN_VALIDATED" if validation["status"] == "PASS" else "NOT_FROZEN"
    write(out / "b_ws_freeze_manifest.json", {
        "builder_id": "B-WS",
        "builder_version": "B-WS-1.0.0",
        "freeze_status": freeze_status,
        "freeze_criteria": {
            "workspace_discovery": "PASS" if len(records) > 0 and not c1.get("errors") else "FAIL",
            "validation": validation["status"],
            "boundary": "PASS" if not boundary_violations and not cross_namespace_collisions else "FAIL",
            "repeat_build_determinism": "PASS" if validation["checks"]["repeat_catalog_equal"] and validation["checks"]["repeat_relationship_graph_equal"] else "FAIL",
        },
        "ordered_rows_sha256": c1["ordered_rows_sha256"],
        "freeze_rule": "Modification requires B_WS_REVISION_AND_REVALIDATION_PACKET",
        "production_cutover_authorized": False,
    })
    write(out / "artifact_subprojection_progress_matrix.json", {
        "projection_family": "artifacts",
        "governed_source_inventory": "FROZEN_VALIDATED",
        "workspace_artifact_catalog": freeze_status,
        "generated_artifact_catalog": "NOT_STARTED",
        "runtime_transient_catalog": "NOT_STARTED",
        "historical_artifact_register": "NOT_STARTED",
        "composite_view": "NOT_STARTED",
    })
    summary = f"""# B-WS Implementation Summary

## Result

B-WS (`workspace_artifact_catalog`) is `{freeze_status}` as a derived, non-production builder.

## Scope

The builder observed physical files, physical directories, and symlink records using canonical workspace-relative paths. It excluded governed `docs` and `registry` roots, generated/runtime/output roots, databases, temporary roots, and the campaign output tree. Governed-source authority remains with frozen B-GOV.

## Measured output

- Records: {len(records)}
- Relationships: {len(r1.get('relationships', []))}
- Scan errors: {len(c1.get('errors', []))}
- Ordered rows SHA-256: `{c1['ordered_rows_sha256']}`
- Repeat-build equality: `{'PASS' if validation['status'] == 'PASS' else 'FAIL'}`

## Boundary and authority

B-WS uses the `workspace_artifact:` identity namespace and does not emit B-GOV `governed_source:` identities. It is derived filesystem observation, not authoritative source semantics and not a production cutover.

## Limitations

This implementation does not claim to reconstruct the entire legacy 110,596-row monolithic artifacts table. Generated, transient, historical, and governed-source subprojections remain separate downstream work.
"""
    (out / "b_ws_implementation_summary.md").write_text(summary, encoding="utf-8")
    manifest = []
    for path in sorted(out.iterdir(), key=lambda item: item.name):
        if path.name == "deliverable_manifest.json":
            continue
        if path.is_file():
            manifest.append({"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "derived_or_authoritative": "DERIVED_REBUILDABLE", "source_packet_id": "ACELLORATOR_ARTIFACT_SUBPROJECTION_B_WS_IMPLEMENTATION_20260724_001"})
    write(out / "deliverable_manifest.json", {"created_at": datetime.now(timezone.utc).isoformat(), "source_packet_id": "ACELLORATOR_ARTIFACT_SUBPROJECTION_B_WS_IMPLEMENTATION_20260724_001", "entries": manifest})


if __name__ == "__main__":
    main()
