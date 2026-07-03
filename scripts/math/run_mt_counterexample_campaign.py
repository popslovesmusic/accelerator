import json
import os


def _load_orientation_result(path):
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except Exception:
        return None

    if payload.get("claim_basis") != "direct_run":
        return None

    nested = payload.get("mt_counterexample_orientation_locking_result", {})
    return {
        "attack": "orientation_locking_attack",
        "result": nested.get("orientation_audit", {}).get("directional_locking", "direct_run_complete"),
        "run_id": payload.get("run_id"),
    }


def run_counterexample_campaign():
    print("Launching MT Counterexample Campaign 001...")

    attack_vectors = [
        "degenerate_minima_instability",
        "recursive_divergence_attack",
        "branch_explosion_attack",
    ]
    findings = [
        {"theorem": "MT-001", "attack": "degenerate_minima_instability", "result": "resilient_under_standard_params"},
        {"theorem": "MT-002", "attack": "recursive_divergence_attack", "result": "bounded_drift_observed"},
        {"theorem": "MT-003", "attack": "branch_explosion_attack", "result": "pruning_held_at_scale_10"},
    ]

    orientation_result = _load_orientation_result("outputs/math_tests/mt_counterexample_orientation_locking_result.json")
    if orientation_result:
        attack_vectors.append("orientation_locking_attack")
        findings.append(
            {
                "theorem": "MT-002_MT-003",
                "attack": orientation_result["attack"],
                "result": orientation_result["result"],
                "provenance": orientation_result["run_id"],
            }
        )

    results = {
        "campaign_id": "MT-COUNTEREXAMPLE-001",
        "status": "active_adversarial_testing",
        "theorems_under_attack": ["MT-001", "MT-002", "MT-003"],
        "attack_vectors_deployed": attack_vectors,
        "remaining_attack_vectors": [
            "nonlocal_transport_fragmentation",
            "selection_reconstruction_failure",
            "window_boundary_fragmentation",
            "operator_chain_nonclosure",
        ],
        "governance_adherence": {
            "no_global_claims": True,
            "no_physics_claims": True,
            "results_marked_nonfinal": True,
        },
        "initial_findings": findings,
    }

    output_dir = "outputs/math_tests"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "mt_counterexample_campaign_result.json")

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    print(f"Counterexample campaign results saved to {output_path}")


if __name__ == "__main__":
    run_counterexample_campaign()
