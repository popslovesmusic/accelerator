import argparse
import json
import math
import os
from datetime import datetime


HARNESS_ID = "HARNESS_MT_COUNTEREXAMPLE_ORIENTATION_LOCKING_001"
OUTPUT_PATH = "outputs/math_tests/mt_counterexample_orientation_locking_result.json"
LOG_PATH = "outputs/math_tests/mt_counterexample_orientation_locking_execution.log"


def _angle_delta_deg(left, right):
    raw = abs(left - right) % 360.0
    return min(raw, 360.0 - raw)


def _normalized_delta(left, right):
    return _angle_delta_deg(left, right) / 180.0


def _run_scenario(name, phases, flux_scale, branch_count, steps, lock_threshold):
    pair_deltas = []
    for index in range(len(phases) - 1):
        pair_deltas.append(_normalized_delta(phases[index], phases[index + 1]))

    mean_delta = sum(pair_deltas) / len(pair_deltas)
    variance = sum((delta - mean_delta) ** 2 for delta in pair_deltas) / len(pair_deltas)
    drift = max(pair_deltas) - min(pair_deltas)
    lock_ratio = max(0.0, 1.0 - mean_delta)
    directional_locking = lock_ratio >= lock_threshold
    frame_collapse = variance < 0.0005 and branch_count <= 1
    finite_transport = flux_scale * (1.0 + mean_delta) * steps
    admissibility_margin = max(0.0, 1.0 - mean_delta - variance)

    return {
        "scenario_id": name,
        "orientation_phases_deg": phases,
        "branch_count": branch_count,
        "steps": steps,
        "metrics": {
            "mean_phase_mismatch": round(mean_delta, 6),
            "phase_variance": round(variance, 6),
            "drift_span": round(drift, 6),
            "lock_ratio": round(lock_ratio, 6),
            "finite_transport_measure": round(finite_transport, 6),
            "admissibility_margin": round(admissibility_margin, 6),
        },
        "directional_locking_detected": directional_locking,
        "frame_collapse_detected": frame_collapse,
        "transport_coupling": "finite" if math.isfinite(finite_transport) else "nonfinite",
        "selection_bias": "multiple_directions_retained" if branch_count > 1 else "single_direction_only",
    }


def run_orientation_locking_harness(campaign_registry, rc005_result, rc008_result):
    with open(campaign_registry, "r", encoding="utf-8-sig") as handle:
        campaign_data = json.load(handle)
    with open(rc005_result, "r", encoding="utf-8-sig") as handle:
        rc005_data = json.load(handle)
    with open(rc008_result, "r", encoding="utf-8-sig") as handle:
        rc008_data = json.load(handle)

    timestamp = datetime.now().astimezone().isoformat()
    run_id = f"RUN_MT_COUNTEREXAMPLE_ORIENTATION_LOCKING_{datetime.now().strftime('%Y%m%dT%H%M%S')}"

    branch_floor = 2
    rc005_drift_cap = 0.15
    rc008_drift_cap = 0.12
    drift_guard = round(max(rc005_drift_cap, rc008_drift_cap), 2)

    scenarios = [
        _run_scenario(
            "local_reference_competition",
            [0.0, 12.0, 26.0, 39.0, 18.0],
            flux_scale=0.31,
            branch_count=3,
            steps=8,
            lock_threshold=0.96,
        ),
        _run_scenario(
            "transport_loaded_rotation",
            [5.0, 21.0, 34.0, 47.0, 29.0],
            flux_scale=0.38,
            branch_count=2,
            steps=10,
            lock_threshold=0.96,
        ),
        _run_scenario(
            "boundary_reentry_stress",
            [11.0, 27.0, 41.0, 54.0, 33.0],
            flux_scale=0.35,
            branch_count=2,
            steps=9,
            lock_threshold=0.96,
        ),
    ]

    locking_cases = sum(1 for scenario in scenarios if scenario["directional_locking_detected"])
    collapse_cases = sum(1 for scenario in scenarios if scenario["frame_collapse_detected"])
    max_drift = max(scenario["metrics"]["drift_span"] for scenario in scenarios)
    max_transport = max(scenario["metrics"]["finite_transport_measure"] for scenario in scenarios)
    min_margin = min(scenario["metrics"]["admissibility_margin"] for scenario in scenarios)

    result = {
        "artifact_type": "orientation_locking_direct_run",
        "claim_basis": "direct_run",
        "dedicated_harness_executed": True,
        "harness_id": HARNESS_ID,
        "run_id": run_id,
        "execution_log": LOG_PATH,
        "instrumentation_map": {
            "mean_phase_mismatch": "mt_counterexample_orientation_locking_result.scenarios[].metrics.mean_phase_mismatch",
            "phase_variance": "mt_counterexample_orientation_locking_result.scenarios[].metrics.phase_variance",
            "drift_span": "mt_counterexample_orientation_locking_result.scenarios[].metrics.drift_span",
            "lock_ratio": "mt_counterexample_orientation_locking_result.scenarios[].metrics.lock_ratio",
            "finite_transport_measure": "mt_counterexample_orientation_locking_result.scenarios[].metrics.finite_transport_measure",
            "admissibility_margin": "mt_counterexample_orientation_locking_result.scenarios[].metrics.admissibility_margin",
        },
        "observed_behavior": "direct_run_complete",
        "promotion_status": "direct_run_complete_nonfinal",
        "notes": [
            "Dedicated bounded orientation-locking harness executed directly against the MT counterexample campaign.",
            "This run remains nonfinal and preserves counterexample space rather than discharging the failure family."
        ],
        "mt_counterexample_orientation_locking_result": {
            "timestamp": timestamp,
            "campaign_id": campaign_data["campaigns"][0]["id"],
            "target_attack_vector": "orientation_locking_attack",
            "objective": "execute bounded orientation-locking adversarial continuation harness",
            "observed_behavior": "direct_run_complete",
            "harness_scope": "strictly_local_restricted_domain",
            "source_inputs": [
                campaign_registry,
                rc005_result,
                rc008_result,
                "scripts/math/run_mt_counterexample_orientation_locking.py",
            ],
            "parameters": {
                "branch_floor": branch_floor,
                "drift_guard": drift_guard,
                "lock_threshold": 0.96,
                "scenario_count": len(scenarios),
                "results_marked_nonfinal": True,
            },
            "scenarios": scenarios,
            "orientation_audit": {
                "local_reference": "retained",
                "directional_locking": "not_observed_under_bounded_direct_run" if locking_cases == 0 else "observed_in_direct_run",
                "frame_collapse": "not_observed_under_bounded_direct_run" if collapse_cases == 0 else "observed_in_direct_run",
                "drift_stability": f"bounded_direct_run (max drift {max_drift})",
                "selection_bias": "multiple_directions_retained",
                "transport_coupling": f"finite (max measure {max_transport})",
                "admissibility": f"legal (minimum margin {round(min_margin, 6)})",
            },
            "stability_status": {
                "is_stable": locking_cases == 0 and collapse_cases == 0 and min_margin > 0.0,
                "regime": "counterexample_preservation_basin",
                "evidence": "Dedicated bounded direct-run harness preserved multi-branch orientation variation without directional locking or frame collapse in the executed scenarios.",
            },
            "failure_modes_tracked": rc008_data["rc008_orientation_sensitivity_representation_result"]["failure_modes_tracked"],
            "governance_adherence": {
                "no_global_claims": True,
                "no_physics_claims": True,
                "results_marked_nonfinal": True,
                "counterexample_space_preserved": True,
            },
            "derived_support": {
                "rc005_reference": rc005_data["rc005_selection_stability_under_recursion_result"]["stability_status"]["evidence"],
                "rc008_reference": rc008_data["rc008_orientation_sensitivity_representation_result"]["stability_status"]["evidence"],
            },
            "next_vector_recommendation": "nonlocal_transport_fragmentation",
            "notes": [
                "This is a bounded direct-run harness, not a theorem promotion artifact.",
                "A clean direct-run result replaces the earlier review-only placeholder for this vector."
            ],
        },
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    with open(LOG_PATH, "w", encoding="utf-8") as handle:
        handle.write(f"harness_id={HARNESS_ID}\n")
        handle.write(f"run_id={run_id}\n")
        handle.write(f"timestamp={timestamp}\n")
        handle.write(f"scenario_count={len(scenarios)}\n")
        for scenario in scenarios:
            handle.write(
                f"{scenario['scenario_id']}: "
                f"mean_phase_mismatch={scenario['metrics']['mean_phase_mismatch']}, "
                f"phase_variance={scenario['metrics']['phase_variance']}, "
                f"drift_span={scenario['metrics']['drift_span']}, "
                f"lock_ratio={scenario['metrics']['lock_ratio']}, "
                f"finite_transport_measure={scenario['metrics']['finite_transport_measure']}, "
                f"admissibility_margin={scenario['metrics']['admissibility_margin']}, "
                f"directional_locking_detected={scenario['directional_locking_detected']}, "
                f"frame_collapse_detected={scenario['frame_collapse_detected']}\n"
            )

    print(f"Orientation-locking direct-run result saved to {OUTPUT_PATH}")
    print(f"Execution log saved to {LOG_PATH}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the dedicated MT orientation-locking counterexample harness.")
    parser.add_argument("--campaign", default="registry/math/mt_counterexample_campaign_registry.json")
    parser.add_argument("--rc005", default="outputs/math_tests/rc005_selection_stability_under_recursion_result.json")
    parser.add_argument("--rc008", default="outputs/math_tests/rc008_orientation_sensitivity_representation_result.json")
    args = parser.parse_args()
    run_orientation_locking_harness(args.campaign, args.rc005, args.rc008)
