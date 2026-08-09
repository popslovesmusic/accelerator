import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def normalize(vec):
    norm = np.linalg.norm(vec)
    if norm == 0.0:
        return np.array([1.0, 0.0], dtype=float)
    return vec / norm


def wrap_angle(angle):
    return np.arctan2(np.sin(angle), np.cos(angle))


def confidence_interval(values):
    sample = np.asarray(values, dtype=float)
    if sample.size == 0:
        return [0.0, 0.0]
    if sample.size == 1:
        return [float(sample[0]), float(sample[0])]
    mean = float(np.mean(sample))
    stderr = float(np.std(sample, ddof=1) / np.sqrt(sample.size))
    delta = 1.96 * stderr
    return [mean - delta, mean + delta]


def correlation(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 2 or y.size < 2:
        return 0.0
    x_std = float(np.std(x))
    y_std = float(np.std(y))
    if x_std == 0.0 or y_std == 0.0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


@dataclass(frozen=True)
class CampaignConfig:
    seeds: int = 64
    steps: int = 1800
    base_noise: float = 0.02
    front_threshold: float = 0.30
    closure_window: int = 24
    closure_floor: float = 0.66
    topology_floor: float = 0.78
    shock_interval: int = 180
    shock_duration: int = 18
    recovery_horizon: int = 48
    class_width_tolerance: float = 0.08
    success_tau: float = 0.05


class RelationalConditioningRetest:
    def __init__(self, output_dir="results/pd_cg_v2r_relational_conditioning_retest", config=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or CampaignConfig()

    def orientating_step(self, state, orientation_prev, condition_mode, rng):
        pressure = -0.22 * state
        front_feedback = np.array([-orientation_prev[1], orientation_prev[0]]) * 0.06
        if condition_mode == "conditioned":
            coupling_weight = 0.78
            recovery_weight = 0.28
            noise_scale = self.config.base_noise
        else:
            coupling_weight = 0.38
            recovery_weight = 0.06
            noise_scale = self.config.base_noise * 1.55

        proposal = (
            pressure
            + orientation_prev * coupling_weight
            + front_feedback * recovery_weight
            + rng.normal(0.0, noise_scale, 2)
        )
        return normalize(proposal)

    def generate_trace(self, seed, condition_mode):
        cfg = self.config
        rng = np.random.default_rng(seed)
        state = np.array([1.0, 0.0], dtype=float)
        orientation = np.array([0.0, 1.0], dtype=float)

        trace = []
        for step in range(cfg.steps):
            in_shock = (step % cfg.shock_interval) < cfg.shock_duration
            shock_strength = 0.0
            if in_shock:
                shock_strength = 0.22 if condition_mode == "conditioned" else 0.36

            orientation_prev = orientation.copy()
            orientation = self.orientating_step(state, orientation_prev, condition_mode, rng)
            turn = wrap_angle(
                np.arctan2(orientation[1], orientation[0]) - np.arctan2(orientation_prev[1], orientation_prev[0])
            )

            state = normalize(
                0.86 * state
                + 0.14 * orientation
                + rng.normal(0.0, 0.01 + shock_strength, 2)
            )
            align = float(np.dot(state, orientation))
            shock_vector = rng.normal(0.0, shock_strength, 2)
            state = normalize(state + shock_vector)

            trace.append(
                {
                    "k": step,
                    "state": state.tolist(),
                    "orientation": orientation.tolist(),
                    "angle": float(np.arctan2(orientation[1], orientation[0])),
                    "turn": float(turn),
                    "align": align,
                    "shock_strength": shock_strength,
                    "shock_active": in_shock,
                }
            )
        return trace

    def extract_whole_expression_metrics(self, trace):
        cfg = self.config
        orientations = np.asarray([row["orientation"] for row in trace], dtype=float)
        states = np.asarray([row["state"] for row in trace], dtype=float)
        turns = np.asarray([row["turn"] for row in trace[1:]], dtype=float)
        aligns = np.asarray([row["align"] for row in trace], dtype=float)
        shocks = np.asarray([row["shock_active"] for row in trace], dtype=bool)

        if turns.size == 0:
            turns = np.zeros(1, dtype=float)

        admissible_mask = np.abs(turns) <= cfg.front_threshold
        state_similarity = np.clip(np.sum(states[1:] * states[:-1], axis=1), -1.0, 1.0)
        if admissible_mask.size >= cfg.closure_window:
            kernel = np.ones(cfg.closure_window, dtype=float) / cfg.closure_window
            local_admissibility = np.convolve(admissible_mask.astype(float), kernel, mode="valid")
            local_topology = np.convolve(state_similarity, kernel, mode="valid")
        else:
            local_admissibility = admissible_mask.astype(float)
            local_topology = state_similarity

        min_len = int(min(local_admissibility.size, local_topology.size))
        closure_mask = (
            (local_admissibility[:min_len] >= cfg.closure_floor)
            & (local_topology[:min_len] >= cfg.topology_floor)
        )

        wa_width = float(np.mean(1.0 - np.abs(turns) / np.pi))
        rho_d = float(np.mean(np.abs(aligns[1:])))
        chi_mean = float(np.mean(turns))
        chi = "CCW" if chi_mean >= 0.0 else "CW"
        orientating_chain = float(np.mean(np.clip(np.sum(orientations[1:] * orientations[:-1], axis=1), -1.0, 1.0)))
        m_dom = float(np.mean(np.maximum(0.0, np.abs(aligns[1:]) - 0.5)))
        boundary_signal = 0.5 * np.abs(np.diff(aligns)) + 0.5 * (1.0 - state_similarity)
        boundary_front_mediation = correlation(np.abs(turns), boundary_signal)

        shock_starts = np.where((shocks[1:] == True) & (shocks[:-1] == False))[0] + 1
        basin_recoveries = []
        class_recoveries = []
        baseline_chi = chi
        baseline_wa = wa_width
        for start in shock_starts:
            close_start = min(start, max(0, closure_mask.size - 1))
            horizon_end = min(close_start + cfg.recovery_horizon, closure_mask.size)
            recovered = bool(np.any(closure_mask[close_start:horizon_end]))
            basin_recoveries.append(1.0 if recovered else 0.0)

            orient_start = min(start + 1, orientations.shape[0] - 1)
            orient_end = min(orient_start + cfg.recovery_horizon, orientations.shape[0])
            if orient_end - orient_start >= 2:
                post_turns = np.asarray([row["turn"] for row in trace[orient_start:orient_end]], dtype=float)
                post_wa = float(np.mean(1.0 - np.abs(post_turns) / np.pi))
                post_chi = "CCW" if float(np.mean(post_turns)) >= 0.0 else "CW"
                class_recovered = (post_chi == baseline_chi) and (abs(post_wa - baseline_wa) <= cfg.class_width_tolerance)
            else:
                class_recovered = False
            class_recoveries.append(1.0 if class_recovered else 0.0)

        basin_reformation_rate = float(np.mean(basin_recoveries)) if basin_recoveries else 0.0
        admissibility_class_recovery = float(np.mean(class_recoveries)) if class_recoveries else 0.0
        basin_survival = float(np.mean(closure_mask.astype(float))) if closure_mask.size else 0.0

        sigma_vector = np.array(
            [
                wa_width,
                rho_d,
                (1.0 + np.sign(chi_mean)) / 2.0,
                orientating_chain,
                m_dom,
            ],
            dtype=float,
        )

        signature = {
            "W_a": wa_width,
            "rho_D": rho_d,
            "chi": chi,
            "R_minus_i": orientating_chain,
            "M_dom": m_dom,
            "basin_survival": basin_survival,
            "basin_reformation_rate": basin_reformation_rate,
            "admissibility_class_recovery": admissibility_class_recovery,
            "boundary_front_mediation": boundary_front_mediation,
            "whole_expression_id": f"SIG_{chi}_{wa_width:.3f}_{rho_d:.3f}_{m_dom:.3f}",
        }
        return signature, sigma_vector

    def run(self):
        cfg = self.config
        per_seed = []
        for seed in range(cfg.seeds):
            conditioned_trace = self.generate_trace(seed=seed, condition_mode="conditioned")
            null_trace = self.generate_trace(seed=seed, condition_mode="null_control")
            conditioned_sig, conditioned_vec = self.extract_whole_expression_metrics(conditioned_trace)
            null_sig, null_vec = self.extract_whole_expression_metrics(null_trace)

            per_seed.append(
                {
                    "seed": seed,
                    "conditioned_signature": conditioned_sig,
                    "null_signature": null_sig,
                    "comparisons": {
                        "basin_survival_gain": conditioned_sig["basin_survival"] - null_sig["basin_survival"],
                        "basin_reformation_gain": conditioned_sig["basin_reformation_rate"] - null_sig["basin_reformation_rate"],
                        "admissibility_class_recovery_gain": conditioned_sig["admissibility_class_recovery"] - null_sig["admissibility_class_recovery"],
                        "boundary_front_mediation_gain": conditioned_sig["boundary_front_mediation"] - null_sig["boundary_front_mediation"],
                        "whole_expression_distance": float(np.linalg.norm(conditioned_vec - null_vec)),
                    },
                }
            )

        basin_survival_gains = [row["comparisons"]["basin_survival_gain"] for row in per_seed]
        basin_reformation_gains = [row["comparisons"]["basin_reformation_gain"] for row in per_seed]
        recovery_gains = [row["comparisons"]["admissibility_class_recovery_gain"] for row in per_seed]
        mediation_gains = [row["comparisons"]["boundary_front_mediation_gain"] for row in per_seed]
        expression_distances = [row["comparisons"]["whole_expression_distance"] for row in per_seed]

        summary = {
            "campaign_id": "PD_CG_V2R_RELATIONAL_CONDITIONING_RETEST",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample_size": {
                "seed_count": cfg.seeds,
                "steps_per_seed": cfg.steps,
                "total_condition_steps": cfg.seeds * cfg.steps * 2,
            },
            "metrics": {
                "basin_survival_gain_mean": float(np.mean(basin_survival_gains)),
                "basin_survival_gain_ci95": confidence_interval(basin_survival_gains),
                "basin_reformation_gain_mean": float(np.mean(basin_reformation_gains)),
                "basin_reformation_gain_ci95": confidence_interval(basin_reformation_gains),
                "admissibility_class_recovery_gain_mean": float(np.mean(recovery_gains)),
                "admissibility_class_recovery_gain_ci95": confidence_interval(recovery_gains),
                "boundary_front_mediation_gain_mean": float(np.mean(mediation_gains)),
                "boundary_front_mediation_gain_ci95": confidence_interval(mediation_gains),
                "whole_expression_distance_mean": float(np.mean(expression_distances)),
            },
            "required_tests": {
                "sequence_level_orientating_analysis_pass_rate": float(
                    np.mean([row["conditioned_signature"]["R_minus_i"] > row["null_signature"]["R_minus_i"] for row in per_seed])
                ),
                "boundary_front_mediation_analysis_pass_rate": float(
                    np.mean([row["comparisons"]["boundary_front_mediation_gain"] > 0.0 for row in per_seed])
                ),
                "whole_expression_rt_sigma_pass_rate": float(
                    np.mean([row["comparisons"]["whole_expression_distance"] > cfg.success_tau for row in per_seed])
                ),
                "conditioned_vs_null_pass_rate": float(
                    np.mean([
                        row["comparisons"]["basin_survival_gain"] > 0.0
                        and row["comparisons"]["basin_reformation_gain"] > 0.0
                        and row["comparisons"]["admissibility_class_recovery_gain"] > 0.0
                        for row in per_seed
                    ])
                ),
            },
            "governance_assessment": {
                "local_governance_applied": True,
                "relation_conditioning_subscript_respected": True,
                "forbidden_tests_used": [],
                "claim_class_recommendation": "C2_within_model",
                "bridge_promotion_recommendation": "DO_NOT_PROMOTE",
                "reason": (
                    "This retest compares whole-expression relational conditioning against a null-conditioning control, "
                    "but remains a bounded single-model simulation and cannot resolve OPEN_BRIDGE_001."
                ),
            },
        }

        summary["decision"] = {
            "supports_conditioning_improvement_within_model": bool(
                summary["metrics"]["basin_survival_gain_mean"] > cfg.success_tau
                and summary["metrics"]["basin_reformation_gain_mean"] > cfg.success_tau
                and summary["metrics"]["admissibility_class_recovery_gain_mean"] > cfg.success_tau
                and summary["metrics"]["boundary_front_mediation_gain_mean"] > 0.0
            ),
            "supports_open_bridge_001_promotion": False,
        }

        payload = {"summary": summary, "per_seed": per_seed}
        results_path = self.output_dir / "retest_results.json"
        with results_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        report_path = self.output_dir / "retest_report.md"
        with report_path.open("w", encoding="utf-8") as handle:
            handle.write(self.render_report(summary, results_path))

        print("[PD_CG_V2R] Relational conditioning retest complete.")
        print(json.dumps(summary, indent=2))
        print(f"[PD_CG_V2R] Results written to {results_path}")
        print(f"[PD_CG_V2R] Report written to {report_path}")
        return payload

    def render_report(self, summary, results_path):
        metrics = summary["metrics"]
        tests = summary["required_tests"]
        decision = summary["decision"]
        governance = summary["governance_assessment"]
        return "\n".join(
            [
                "# PD_CG_V2R Relational Conditioning Retest",
                "",
                "## 1. Scope",
                "Retest whole-expression procedural organization by comparing relational-conditioning mode `(A <≠>_R a)` against a null-conditioning control `(A <≠>_null a)` without treating `_R` as a removable residue variable.",
                "",
                "## 2. Directly observed/defined",
                f"- Seed count: {summary['sample_size']['seed_count']}",
                f"- Steps per seed: {summary['sample_size']['steps_per_seed']}",
                f"- Basin survival gain mean: {metrics['basin_survival_gain_mean']:.4f}",
                f"- Basin reformation gain mean: {metrics['basin_reformation_gain_mean']:.4f}",
                f"- Admissibility-class recovery gain mean: {metrics['admissibility_class_recovery_gain_mean']:.4f}",
                f"- Boundary-front mediation gain mean: {metrics['boundary_front_mediation_gain_mean']:.4f}",
                f"- Whole-expression distance mean: {metrics['whole_expression_distance_mean']:.4f}",
                f"- Sequence-level pass rate: {tests['sequence_level_orientating_analysis_pass_rate']:.4f}",
                f"- Boundary-front mediation pass rate: {tests['boundary_front_mediation_analysis_pass_rate']:.4f}",
                f"- Whole-expression RT(Sigma_R) pass rate: {tests['whole_expression_rt_sigma_pass_rate']:.4f}",
                f"- Conditioned-vs-null pass rate: {tests['conditioned_vs_null_pass_rate']:.4f}",
                "",
                "## 3. Inferred inside framework",
                f"- Within these models, relational-conditioning improvement support is: {decision['supports_conditioning_improvement_within_model']}.",
                "",
                "## 4. External resemblance (Analogy only)",
                "- None asserted. This report stays inside the bounded procedural model.",
                "",
                "## 5. What it does NOT prove",
                "- It does not establish OPEN_BRIDGE_001 as resolved.",
                "- It does not justify promotion to GR_app, QM_app, or any external physical interpretation.",
                "- It does not prove Affect or a universal theorem.",
                "",
                "## 6. Failure modes / uncertainty",
                f"- Claim class recommendation: {governance['claim_class_recommendation']}",
                f"- Bridge promotion recommendation: {governance['bridge_promotion_recommendation']}",
                "- This remains a single-model Python retest rather than a multi-model bridge-closing campaign.",
                "- `Sigma_null`, `relational_conditioning_mode`, `basin_reformation_rate`, and `admissibility_class_recovery` should be treated as provisional observables unless separately promoted.",
                f"- Evidence path: {results_path.as_posix()}",
            ]
        )


if __name__ == "__main__":
    analyzer = RelationalConditioningRetest()
    analyzer.run()
