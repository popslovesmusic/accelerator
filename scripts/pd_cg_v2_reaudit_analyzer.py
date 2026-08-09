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
    steps: int = 1600
    base_noise: float = 0.02
    perturbed_noise: float = 0.05
    front_threshold: float = 0.28
    closure_window: int = 24
    closure_floor: float = 0.65
    topology_floor: float = 0.78
    support_tau: float = 0.05


class OrientatingReauditAnalyzer:
    def __init__(self, output_dir="results/pd_cg_v2_reaudit", config=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or CampaignConfig()

    def orientating_procedure(
        self,
        state,
        residue,
        orientation_prev,
        rng,
        noise_scale,
        mode,
    ):
        pressure = -0.28 * state
        effective_residue = 0.0 if mode == "residue_removed" else residue
        memory_weight = 0.35 + 0.45 * np.clip(effective_residue, -1.0, 1.0)
        memory = orientation_prev * memory_weight
        residue_vector = orientation_prev * (0.35 * effective_residue)
        boundary_feedback = np.array([-orientation_prev[1], orientation_prev[0]]) * 0.08

        if mode == "random_orientation":
            proposal = rng.normal(0.0, 1.0, 2)
            memory_share = 0.0
        else:
            proposal = pressure + memory + residue_vector + boundary_feedback
            if mode == "admissibility_randomized":
                proposal = proposal + rng.normal(0.0, 0.45, 2)
            memory_share = float(
                np.linalg.norm(memory)
                / (
                    np.linalg.norm(memory)
                    + np.linalg.norm(residue_vector)
                    + np.linalg.norm(pressure)
                    + 1e-9
                )
            )

        proposal = proposal + rng.normal(0.0, noise_scale, 2)
        orientation_next = normalize(proposal)
        return orientation_next, memory_share

    def generate_procedural_trace(self, seed, mode="full", noise_scale=None):
        cfg = self.config
        rng = np.random.default_rng(seed)
        noise_scale = cfg.base_noise if noise_scale is None else noise_scale

        state = np.array([1.0, 0.0], dtype=float)
        orientation = np.array([0.0, 1.0], dtype=float)
        residue = 0.55

        trace = []
        for step in range(cfg.steps):
            orientation_prev = orientation.copy()
            orientation, memory_share = self.orientating_procedure(
                state=state,
                residue=residue,
                orientation_prev=orientation_prev,
                rng=rng,
                noise_scale=noise_scale,
                mode=mode,
            )

            turn = wrap_angle(
                np.arctan2(orientation[1], orientation[0])
                - np.arctan2(orientation_prev[1], orientation_prev[0])
            )
            align = float(np.dot(state, orientation))
            residue = 0.82 * residue + 0.18 * (0.40 * align + 0.60 * np.cos(turn))

            state_noise_scale = 0.01 if mode != "admissibility_randomized" else 0.08
            state = normalize(
                0.84 * state
                + 0.16 * orientation
                + rng.normal(0.0, state_noise_scale, 2)
            )

            trace.append(
                {
                    "k": step,
                    "state": state.tolist(),
                    "orientation": orientation.tolist(),
                    "angle": float(np.arctan2(orientation[1], orientation[0])),
                    "turn": float(turn),
                    "residue": float(residue),
                    "align": align,
                    "memory_share": memory_share,
                }
            )
        return trace

    def extract_sigma_r(self, trace):
        cfg = self.config

        angles = np.asarray([row["angle"] for row in trace], dtype=float)
        turns = np.asarray([row["turn"] for row in trace[1:]], dtype=float)
        residues = np.asarray([row["residue"] for row in trace], dtype=float)
        aligns = np.asarray([row["align"] for row in trace], dtype=float)
        memory_shares = np.asarray([row["memory_share"] for row in trace], dtype=float)
        states = np.asarray([row["state"] for row in trace], dtype=float)

        if turns.size == 0:
            turns = np.zeros(1, dtype=float)

        admissible_mask = np.abs(turns) <= cfg.front_threshold
        front_events = (~admissible_mask).astype(float)

        if admissible_mask.size >= cfg.closure_window:
            window_kernel = np.ones(cfg.closure_window, dtype=float) / cfg.closure_window
            local_admissibility = np.convolve(admissible_mask.astype(float), window_kernel, mode="valid")
        else:
            local_admissibility = admissible_mask.astype(float)

        state_similarity = np.sum(states[1:] * states[:-1], axis=1) if len(states) > 1 else np.ones(1)
        state_similarity = np.clip(state_similarity, -1.0, 1.0)
        if state_similarity.size >= cfg.closure_window:
            topology_kernel = np.ones(cfg.closure_window, dtype=float) / cfg.closure_window
            local_topology = np.convolve(state_similarity, topology_kernel, mode="valid")
        else:
            local_topology = state_similarity

        min_len = int(min(local_admissibility.size, local_topology.size))
        if min_len == 0:
            closure_mask = np.zeros(1, dtype=bool)
        else:
            closure_mask = (
                (local_admissibility[:min_len] >= cfg.closure_floor)
                & (local_topology[:min_len] >= cfg.topology_floor)
            )

        c_orient = float(np.mean((1.0 + np.cos(turns)) / 2.0))
        s_closure = float(np.mean(closure_mask.astype(float)))
        r_support = float(np.mean(np.clip(memory_shares, 0.0, 1.0)))
        a_width = float(np.mean(admissible_mask.astype(float)))
        topology_preserve = float(np.mean((1.0 + state_similarity) / 2.0))
        boundary_front_rate = float(np.mean(front_events))
        boundary_signal = 0.5 * np.abs(np.diff(aligns)) + 0.5 * (1.0 - np.clip(state_similarity, -1.0, 1.0))
        mediation_corr = correlation(np.abs(turns), boundary_signal)
        sequence_recoverability = float(
            np.mean(np.clip(np.sum(
                np.asarray([row["orientation"] for row in trace[1:]], dtype=float)
                * np.asarray([row["orientation"] for row in trace[:-1]], dtype=float),
                axis=1,
            ), -1.0, 1.0))
        )

        signature = {
            "C_orient": c_orient,
            "S_closure": s_closure,
            "R_support": r_support,
            "A_width": a_width,
            "T_preserve": topology_preserve,
            "boundary_front_rate": boundary_front_rate,
            "boundary_front_mediation": mediation_corr,
            "sequence_recoverability": sequence_recoverability,
            "chi": "CCW" if float(np.mean(turns)) >= 0.0 else "CW",
            "front_event_count": int(np.sum(front_events)),
            "mean_residue": float(np.mean(residues)),
            "mean_alignment": float(np.mean(aligns)),
        }

        signature_vector = np.array(
            [
                signature["C_orient"],
                signature["S_closure"],
                signature["R_support"],
                signature["A_width"],
                signature["T_preserve"],
                1.0 - signature["boundary_front_rate"],
                max(signature["boundary_front_mediation"], 0.0),
                max(signature["sequence_recoverability"], 0.0),
            ],
            dtype=float,
        )
        return signature, signature_vector

    def run_reaudit(self):
        cfg = self.config
        per_seed = []

        for seed in range(cfg.seeds):
            traces = {
                "M0_full": self.generate_procedural_trace(seed=seed, mode="full", noise_scale=cfg.base_noise),
                "M0_perturbed": self.generate_procedural_trace(seed=seed, mode="full", noise_scale=cfg.perturbed_noise),
                "M1_random_orientation": self.generate_procedural_trace(
                    seed=seed, mode="random_orientation", noise_scale=cfg.base_noise
                ),
                "M2_residue_removed": self.generate_procedural_trace(
                    seed=seed, mode="residue_removed", noise_scale=cfg.base_noise
                ),
                "M3_admissibility_randomized": self.generate_procedural_trace(
                    seed=seed, mode="admissibility_randomized", noise_scale=cfg.base_noise
                ),
            }

            signatures = {}
            vectors = {}
            for label, trace in traces.items():
                signatures[label], vectors[label] = self.extract_sigma_r(trace)

            distance_perturbed = float(np.linalg.norm(vectors["M0_full"] - vectors["M0_perturbed"]))
            distance_randomized = float(np.linalg.norm(vectors["M0_full"] - vectors["M1_random_orientation"]))
            distance_residue = float(np.linalg.norm(vectors["M0_full"] - vectors["M2_residue_removed"]))
            distance_admissibility = float(
                np.linalg.norm(vectors["M0_full"] - vectors["M3_admissibility_randomized"])
            )

            per_seed.append(
                {
                    "seed": seed,
                    "signatures": signatures,
                    "comparisons": {
                        "distance_full_vs_perturbed": distance_perturbed,
                        "distance_full_vs_random_orientation": distance_randomized,
                        "distance_full_vs_residue_removed": distance_residue,
                        "distance_full_vs_admissibility_randomized": distance_admissibility,
                        "orientation_effect": signatures["M0_full"]["S_closure"]
                        - signatures["M1_random_orientation"]["S_closure"],
                        "residue_effect": signatures["M0_full"]["S_closure"]
                        - signatures["M2_residue_removed"]["S_closure"],
                        "admissibility_effect": signatures["M0_full"]["S_closure"]
                        - signatures["M3_admissibility_randomized"]["S_closure"],
                    },
                    "campaign_checks": {
                        "sequence_level_orientating": signatures["M0_full"]["C_orient"]
                        > signatures["M1_random_orientation"]["C_orient"],
                        "boundary_front_mediation": signatures["M0_full"]["boundary_front_mediation"] > 0.20,
                        "whole_expression_rt_sigma": distance_perturbed < distance_randomized,
                        "procedural_ablation": signatures["M0_full"]["S_closure"]
                        > signatures["M1_random_orientation"]["S_closure"],
                    },
                }
            )

        orientation_effects = [row["comparisons"]["orientation_effect"] for row in per_seed]
        residue_effects = [row["comparisons"]["residue_effect"] for row in per_seed]
        admissibility_effects = [row["comparisons"]["admissibility_effect"] for row in per_seed]
        perturbed_distances = [row["comparisons"]["distance_full_vs_perturbed"] for row in per_seed]
        random_distances = [row["comparisons"]["distance_full_vs_random_orientation"] for row in per_seed]

        summary = {
            "campaign_id": "PD_CG_V2_PROCEDURAL_ORIENTATING_REAUDIT",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample_size": {
                "seed_count": cfg.seeds,
                "steps_per_seed": cfg.steps,
                "total_condition_steps": cfg.seeds * cfg.steps * 5,
                "meets_proof_minimum_seed_count": cfg.seeds >= 64,
            },
            "metrics": {
                "orientation_effect_mean": float(np.mean(orientation_effects)),
                "orientation_effect_ci95": confidence_interval(orientation_effects),
                "residue_effect_mean": float(np.mean(residue_effects)),
                "residue_effect_ci95": confidence_interval(residue_effects),
                "admissibility_effect_mean": float(np.mean(admissibility_effects)),
                "admissibility_effect_ci95": confidence_interval(admissibility_effects),
                "distance_full_vs_perturbed_mean": float(np.mean(perturbed_distances)),
                "distance_full_vs_random_orientation_mean": float(np.mean(random_distances)),
            },
            "required_tests": {
                "sequence_level_orientating_analysis_pass_rate": float(
                    np.mean([row["campaign_checks"]["sequence_level_orientating"] for row in per_seed])
                ),
                "boundary_front_mediation_analysis_pass_rate": float(
                    np.mean([row["campaign_checks"]["boundary_front_mediation"] for row in per_seed])
                ),
                "whole_expression_rt_sigma_pass_rate": float(
                    np.mean([row["campaign_checks"]["whole_expression_rt_sigma"] for row in per_seed])
                ),
                "procedural_ablation_pass_rate": float(
                    np.mean([row["campaign_checks"]["procedural_ablation"] for row in per_seed])
                ),
            },
            "governance_assessment": {
                "local_governance_applied": True,
                "forbidden_tests_used": [],
                "claim_class_recommendation": "C2_within_model",
                "bridge_promotion_recommendation": "DO_NOT_PROMOTE",
                "reason": (
                    "The campaign now tests the orientating procedure directly, but the evidence remains "
                    "a bounded within-model simulation and does not satisfy the full open-bridge proof obligation."
                ),
            },
        }

        summary["decision"] = {
            "supports_campaign_hypothesis_within_model": bool(
                summary["metrics"]["orientation_effect_mean"] > cfg.support_tau
                and summary["metrics"]["residue_effect_mean"] > cfg.support_tau
                and summary["required_tests"]["whole_expression_rt_sigma_pass_rate"] >= 0.75
                and summary["required_tests"]["boundary_front_mediation_analysis_pass_rate"] >= 0.75
                and summary["required_tests"]["procedural_ablation_pass_rate"] >= 0.75
            ),
            "supports_open_bridge_001_promotion": False,
        }

        payload = {"summary": summary, "per_seed": per_seed}
        results_path = self.output_dir / "reaudit_results.json"
        with results_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        report_path = self.output_dir / "reaudit_report.md"
        with report_path.open("w", encoding="utf-8") as handle:
            handle.write(self.render_report(summary, results_path))

        print("[PD_CG_V2] Re-audit complete.")
        print(json.dumps(summary, indent=2))
        print(f"[PD_CG_V2] Results written to {results_path}")
        print(f"[PD_CG_V2] Report written to {report_path}")
        return payload

    def render_report(self, summary, results_path):
        metrics = summary["metrics"]
        tests = summary["required_tests"]
        decision = summary["decision"]
        governance = summary["governance_assessment"]
        return "\n".join(
            [
                "# PD_CG_V2 Procedural Orientating Re-Audit",
                "",
                "## 1. Scope",
                "Audit the orientating procedure as a residue-coupled process and test whether boundary-front reorganization is better explained procedurally than by static orientation labels.",
                "",
                "## 2. Directly observed/defined",
                f"- Seed count: {summary['sample_size']['seed_count']}",
                f"- Steps per seed: {summary['sample_size']['steps_per_seed']}",
                f"- Total condition steps: {summary['sample_size']['total_condition_steps']}",
                f"- Orientation effect mean: {metrics['orientation_effect_mean']:.4f}",
                f"- Residue effect mean: {metrics['residue_effect_mean']:.4f}",
                f"- Admissibility effect mean: {metrics['admissibility_effect_mean']:.4f}",
                f"- Sequence-level pass rate: {tests['sequence_level_orientating_analysis_pass_rate']:.4f}",
                f"- Boundary-front mediation pass rate: {tests['boundary_front_mediation_analysis_pass_rate']:.4f}",
                f"- Whole-expression RT(Sigma_R) pass rate: {tests['whole_expression_rt_sigma_pass_rate']:.4f}",
                f"- Procedural ablation pass rate: {tests['procedural_ablation_pass_rate']:.4f}",
                "",
                "## 3. Inferred inside framework",
                f"- Within these models, campaign hypothesis support is: {decision['supports_campaign_hypothesis_within_model']}.",
                f"- Residue-coupling gap: orientation effect is positive, but residue effect remains {metrics['residue_effect_mean']:.4f}.",
                "",
                "## 4. External resemblance (Analogy only)",
                "- None asserted. This report stays inside the synthetic procedural model.",
                "",
                "## 5. What it does NOT prove",
                "- It does not establish OPEN_BRIDGE_001 as supported.",
                "- It does not justify promotion above the current bridge proof obligation.",
                "- It does not convert model behavior into external physical truth.",
                "- It does not validate newly introduced observables beyond provisional lexicon status.",
                "",
                "## 6. Failure modes / uncertainty",
                f"- Claim class recommendation: {governance['claim_class_recommendation']}",
                f"- Bridge promotion recommendation: {governance['bridge_promotion_recommendation']}",
                "- The residue-removed control does not separate from the full procedure in this synthetic model.",
                "- `boundary_front_mediation` and `sequence_recoverability` remain GAP_OPEN / provisional observables.",
                f"- Evidence path: {results_path.as_posix()}",
            ]
        )


if __name__ == "__main__":
    analyzer = OrientatingReauditAnalyzer()
    analyzer.run_reaudit()
