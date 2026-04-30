from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_VALIDATION_ARTIFACTS = [
    "certification_manifest.json",
    "expected_observables.json",
    "known_control_cases.json",
    "smoke_report.json",
    "convergence_report.json",
    "precision_drift_report.json",
    "falsification_report.json",
    "uncertainty_report.json",
    "provenance_report.json",
    "known_limits.md",
]

REQUIRED_CONFIGS = [
    "c4_candidate_default.json",
    "c4_boundary_sweep.json",
    "c4_ablation_matrix.json",
]

REQUIRED_METADATA = [
    "seed",
    "config_hash",
    "backend",
    "precision",
    "timestamp",
    "source_commit",
    "input_generator",
    "run_id",
    "report_path",
]

REQUIRED_FV = {"FV-1", "FV-2", "FV-3", "FV-4"}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def check(condition: bool, passed: list[dict[str, Any]], failed: list[dict[str, Any]], name: str, detail: str) -> None:
    item = {"name": name, "detail": detail}
    if condition:
        passed.append(item)
    else:
        failed.append(item)


def main() -> int:
    parser = argparse.ArgumentParser(description="Signal Scope C4 candidate induction preflight.")
    parser.add_argument("--out", default=None, help="Output directory for the induction report.")
    parser.add_argument("--update-validation", action="store_true", help="Update tool-local validation reports with preflight result.")
    args = parser.parse_args()

    repo = repo_root_from_script()
    tool_dir = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out) if args.out else repo / "outputs" / "runs" / "signal_scope_c4_candidate_preflight"
    out_dir.mkdir(parents=True, exist_ok=True)

    passed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    local_manifest_path = tool_dir / "tool_manifest.json"
    global_manifest_path = repo / "registry" / "tool_manifest.json"
    local_claims_path = tool_dir / "claim_registry.json"
    global_claims_path = repo / "registry" / "claim_registry.json"
    cert_path = tool_dir / "validation" / "certification_manifest.json"

    local_manifest = load_json(local_manifest_path)
    global_manifest = load_json(global_manifest_path)
    local_claims = load_json(local_claims_path)
    global_claims = load_json(global_claims_path)
    cert = load_json(cert_path)

    tool_name = local_manifest["tool_name"]
    global_entries = [t for t in global_manifest.get("tools", []) if t.get("name") == tool_name]

    check(len(global_entries) == 1, passed, failed, "global_manifest_entry", f"{len(global_entries)} entries for {tool_name}")
    check(local_manifest.get("not_medical_tool") is True, passed, failed, "local_non_medical_flag", "tool_manifest not_medical_tool must be true")
    check(bool(global_entries and global_entries[0].get("not_medical_tool") is True), passed, failed, "global_non_medical_flag", "registry tool entry not_medical_tool must be true")
    allowed_scaffold_levels = {"C0", "C1", "C2"}
    check(cert.get("certification_level") in allowed_scaffold_levels, passed, failed, "honest_certification_level", f"current level {cert.get('certification_level')}")
    check(local_manifest.get("implementation_status") in {"not_imported", "imported_smoke_validated"}, passed, failed, "implementation_status", f"implementation_status={local_manifest.get('implementation_status')}")

    entry_point = repo / local_manifest.get("entry_point", "")
    check(entry_point.exists(), passed, failed, "engine_entry_point_exists", str(entry_point))

    for artifact in REQUIRED_VALIDATION_ARTIFACTS:
        check((tool_dir / "validation" / artifact).exists(), passed, failed, f"validation_artifact_{artifact}", artifact)

    for cfg in REQUIRED_CONFIGS:
        cfg_path = tool_dir / "configs" / cfg
        exists = cfg_path.exists()
        if exists and cfg_path.suffix == ".json":
            load_json(cfg_path)
        check(exists, passed, failed, f"config_{cfg}", cfg)

    missing_metadata = [m for m in REQUIRED_METADATA if m not in cert.get("required_metadata", [])]
    check(not missing_metadata, passed, failed, "required_metadata_complete", f"missing={missing_metadata}")

    local_claim_ids = {c.get("claim_id") for c in local_claims.get("claims", [])}
    global_claim_ids = {c.get("claim_id") for c in global_claims.get("claims", []) if c.get("tool_name") == tool_name}
    check(local_claim_ids <= global_claim_ids, passed, failed, "global_claim_linkage", f"local={sorted(local_claim_ids)} global={sorted(global_claim_ids)}")

    control_cases = load_json(tool_dir / "validation" / "known_control_cases.json")
    control_vectors = {c.get("falsification_vector") for c in control_cases}
    check(REQUIRED_FV <= control_vectors, passed, failed, "four_vector_plan_present", f"vectors={sorted(control_vectors)}")

    expected_observables = load_json(tool_dir / "validation" / "expected_observables.json")
    manifest_outputs = set(local_manifest.get("outputs", []))
    missing_output_defs = sorted(o for o in manifest_outputs if o not in expected_observables and o not in {"groove_state", "inductive_state", "rejection_rate", "survival_metrics"})
    if missing_output_defs:
        warnings.append({"name": "observable_definitions_partial", "detail": f"missing detailed definitions for {missing_output_defs}"})
    else:
        passed.append({"name": "observable_definitions_present", "detail": "primary observables defined"})

    executable_ready = entry_point.exists()
    validation_artifacts_ready = not any(i["name"].startswith("validation_artifact_") for i in failed)
    configs_ready = not any(i["name"].startswith("config_") for i in failed)
    entrypoint_and_artifacts_ready = executable_ready and validation_artifacts_ready and configs_ready

    blocked_reasons = []
    if not executable_ready:
        blocked_reasons.append("simulation entry point is missing")
    if cert.get("scientific_validity", {}).get("implementation_verified") is not True:
        blocked_reasons.append("implementation correctness is not verified")
    if cert.get("scientific_validity", {}).get("provenance_verified") is not True:
        blocked_reasons.append("provenance is not verified")

    current_level = cert.get("certification_level", "C0")
    final_certification_recommendation = f"remain_{current_level}"
    if entrypoint_and_artifacts_ready and not blocked_reasons and current_level == "C0":
        final_certification_recommendation = "eligible_for_C1_review"
    elif current_level == "C1":
        final_certification_recommendation = "eligible_for_C2_review_after_multiseed_or_observable_mapping"
    elif current_level == "C2":
        final_certification_recommendation = "remain_C2_pending_falsification_and_cross_mechanism_validation"

    report = {
        "run_id": out_dir.name,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "tool_name": tool_name,
        "model_class": local_manifest.get("model_class"),
        "mechanism_class": local_manifest.get("mechanism_class"),
        "source_commit": git_commit(repo),
        "artifact_hashes": {
            "local_tool_manifest": file_hash(local_manifest_path),
            "global_tool_manifest": file_hash(global_manifest_path),
            "local_claim_registry": file_hash(local_claims_path),
            "global_claim_registry": file_hash(global_claims_path),
            "certification_manifest": file_hash(cert_path),
        },
        "checks_passed": passed,
        "checks_failed": failed,
        "warnings": warnings,
        "engine_entry_point": str(entry_point),
        "entrypoint_and_artifacts_ready": entrypoint_and_artifacts_ready and not blocked_reasons,
        "final_certification_recommendation": final_certification_recommendation,
        "blocked_reasons": blocked_reasons,
        "claim_status": "provisional_induction_only",
        "not_medical_tool": True,
        "next_actions": [
            "import or implement tools/signal_scope_phase_continuation_engine/run_signal_scope.py",
            "run smoke validation and populate smoke_report.json",
            "run five-seed uncertainty battery and populate uncertainty_report.json",
            "run FV-1 through FV-4 and populate falsification_report.json",
            "run at least one independent cross-mechanism comparison before any L2+ claim use",
        ],
    }

    write_json(out_dir / "signal_scope_c4_candidate_preflight_report.json", report)

    if args.update_validation:
        smoke = load_json(tool_dir / "validation" / "smoke_report.json")
        smoke.update({
            "status": "blocked",
            "last_preflight_report": str(out_dir / "signal_scope_c4_candidate_preflight_report.json"),
            "smoke_validated": False,
            "blocked_reasons": blocked_reasons,
        })
        write_json(tool_dir / "validation" / "smoke_report.json", smoke)

        provenance = load_json(tool_dir / "validation" / "provenance_report.json")
        provenance.update({
            "status": "preflight_only",
            "last_preflight_report": str(out_dir / "signal_scope_c4_candidate_preflight_report.json"),
            "source_commit": report["source_commit"],
            "provenance_verified": False,
        })
        write_json(tool_dir / "validation" / "provenance_report.json", provenance)

        cert["latest_validation_outputs"] = [str(out_dir / "signal_scope_c4_candidate_preflight_report.json")]
        cert["known_limits"] = sorted(set(cert.get("known_limits", []) + blocked_reasons))
        write_json(cert_path, cert)

    print(json.dumps({
        "report": str(out_dir / "signal_scope_c4_candidate_preflight_report.json"),
        "recommendation": final_certification_recommendation,
        "blocked_reasons": blocked_reasons,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
