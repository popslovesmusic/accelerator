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


class AffixPositionTest:
    def __init__(self, output_dir="results/pd_cg_v3_affix_position_test", config=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or CampaignConfig()
        self.mode_params = {
            "bare": {
                "coupling_weight": 0.56,
                "recovery_weight": 0.14,
                "noise_scale": 1.00,
                "shock_scale": 0.30,
                "state_blend": 0.14,
            },
            "subscripted": {
                "coupling_weight": 0.61,
                "recovery_weight": 0.18,
                "noise_scale": 0.95,
                "shock_scale": 0.28,
                "state_blend": 0.15,
            },
            "prefixed": {
                "coupling_weight": 0.74,
                "recovery_weight": 0.27,
                "noise_scale": 0.80,
                "shock_scale": 0.22,
                "state_blend": 0.17,
            },
        }

    def orientating_step(self, state, orientation_prev, mode, rng):
        params = self.mode_params[mode]
        pressure = -0.22 * state
        front_feedback = np.array([-orientation_prev[1], orientation_prev[0]]) * 0.06
        proposal = (
            pressure
            + orientation_prev * params["coupling_weight"]
            + front_feedback * params["recovery_weight"]
            + rng.normal(0.0, self.config.base_noise * params["noise_scale"], 2)
        )
        return normalize(proposal)

    def generate_trace(self, seed, mode):
        cfg = self.config
        params = self.mode_params[mode]
        rng = np.random.default_rng(seed)
        state = np.array([1.0, 0.0], dtype=float)
        orientation = np.array([0.0, 1.0], dtype=float)

        trace = []
        for step in range(cfg.steps):
            in_shock = (step % cfg.shock_interval) < cfg.shock_duration
            shock_strength = params["shock_scale"] if in_shock else 0.0

            orientation_prev = orientation.copy()
            orientation = self.orientating_step(state, orientation_prev, mode, rng)
            turn = wrap_angle(
                np.arctan2(orientation[1], orientation[0]) - np.arctan2(orientation_prev[1], orientation_prev[0])
            )

            state = normalize(
                (1.0 - params["state_blend"]) * state
                + params["state_blend"] * orientation
                + rng.normal(0.0, 0.01 + shock_strength, 2)
            )
            align = float(np.dot(state, orientation))
            state = normalize(state + rng.normal(0.0, shock_strength, 2))

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

    def pair_summary(self, per_seed, left_key, right_key):
        basin_survival_gains = [
            row["comparisons"][f"{left_key}_vs_{right_key}"]["basin_survival_gain"] for row in per_seed
        ]
        basin_reformation_gains = [
            row["comparisons"][f"{left_key}_vs_{right_key}"]["basin_reformation_gain"] for row in per_seed
        ]
        recovery_gains = [
            row["comparisons"][f"{left_key}_vs_{right_key}"]["admissibility_class_recovery_gain"] for row in per_seed
        ]
        mediation_gains = [
            row["comparisons"][f"{left_key}_vs_{right_key}"]["boundary_front_mediation_gain"] for row in per_seed
        ]
        expression_distances = [
            row["comparisons"][f"{left_key}_vs_{right_key}"]["affix_position_separation_score"] for row in per_seed
        ]
        return {
            "basin_survival_gain_mean": float(np.mean(basin_survival_gains)),
            "basin_survival_gain_ci95": confidence_interval(basin_survival_gains),
            "basin_reformation_gain_mean": float(np.mean(basin_reformation_gains)),
            "basin_reformation_gain_ci95": confidence_interval(basin_reformation_gains),
            "admissibility_class_recovery_gain_mean": float(np.mean(recovery_gains)),
            "admissibility_class_recovery_gain_ci95": confidence_interval(recovery_gains),
            "boundary_front_mediation_gain_mean": float(np.mean(mediation_gains)),
            "boundary_front_mediation_gain_ci95": confidence_interval(mediation_gains),
            "affix_position_separation_score_mean": float(np.mean(expression_distances)),
            "whole_expression_RT_pass_rate": float(
                np.mean([score > self.config.success_tau for score in expression_distances])
            ),
        }

    def run(self):
        cfg = self.config
        per_seed = []
        for seed in range(cfg.seeds):
            bare_trace = self.generate_trace(seed=seed, mode="bare")
            subscripted_trace = self.generate_trace(seed=seed, mode="subscripted")
            prefixed_trace = self.generate_trace(seed=seed, mode="prefixed")

            bare_sig, bare_vec = self.extract_whole_expression_metrics(bare_trace)
            sub_sig, sub_vec = self.extract_whole_expression_metrics(subscripted_trace)
            pre_sig, pre_vec = self.extract_whole_expression_metrics(prefixed_trace)

            per_seed.append(
                {
                    "seed": seed,
                    "bare_signature": bare_sig,
                    "subscripted_signature": sub_sig,
                    "prefixed_signature": pre_sig,
                    "comparisons": {
                        "bare_vs_subscripted": {
                            "basin_survival_gain": sub_sig["basin_survival"] - bare_sig["basin_survival"],
                            "basin_reformation_gain": sub_sig["basin_reformation_rate"] - bare_sig["basin_reformation_rate"],
                            "admissibility_class_recovery_gain": sub_sig["admissibility_class_recovery"] - bare_sig["admissibility_class_recovery"],
                            "boundary_front_mediation_gain": sub_sig["boundary_front_mediation"] - bare_sig["boundary_front_mediation"],
                            "affix_position_separation_score": float(np.linalg.norm(sub_vec - bare_vec)),
                        },
                        "bare_vs_prefixed": {
                            "basin_survival_gain": pre_sig["basin_survival"] - bare_sig["basin_survival"],
                            "basin_reformation_gain": pre_sig["basin_reformation_rate"] - bare_sig["basin_reformation_rate"],
                            "admissibility_class_recovery_gain": pre_sig["admissibility_class_recovery"] - bare_sig["admissibility_class_recovery"],
                            "boundary_front_mediation_gain": pre_sig["boundary_front_mediation"] - bare_sig["boundary_front_mediation"],
                            "affix_position_separation_score": float(np.linalg.norm(pre_vec - bare_vec)),
                        },
                        "subscripted_vs_prefixed": {
                            "basin_survival_gain": pre_sig["basin_survival"] - sub_sig["basin_survival"],
                            "basin_reformation_gain": pre_sig["basin_reformation_rate"] - sub_sig["basin_reformation_rate"],
                            "admissibility_class_recovery_gain": pre_sig["admissibility_class_recovery"] - sub_sig["admissibility_class_recovery"],
                            "boundary_front_mediation_gain": pre_sig["boundary_front_mediation"] - sub_sig["boundary_front_mediation"],
                            "affix_position_separation_score": float(np.linalg.norm(pre_vec - sub_vec)),
                        },
                    },
                }
            )

        bare_vs_sub = self.pair_summary(per_seed, "bare", "subscripted")
        bare_vs_pre = self.pair_summary(per_seed, "bare", "prefixed")
        sub_vs_pre = self.pair_summary(per_seed, "subscripted", "prefixed")

        subscript_wins = (
            bare_vs_sub["basin_survival_gain_mean"] > cfg.success_tau
            and bare_vs_sub["admissibility_class_recovery_gain_mean"] > cfg.success_tau
            and bare_vs_sub["boundary_front_mediation_gain_mean"] > 0.0
        )
        prefix_wins = (
            bare_vs_pre["basin_survival_gain_mean"] > cfg.success_tau
            and bare_vs_pre["admissibility_class_recovery_gain_mean"] > cfg.success_tau
            and bare_vs_pre["boundary_front_mediation_gain_mean"] > 0.0
        )
        affix_distinct = sub_vs_pre["affix_position_separation_score_mean"] > cfg.success_tau

        if prefix_wins and not subscript_wins:
            winning_form = "prefixed"
        elif subscript_wins and not prefix_wins:
            winning_form = "subscripted"
        elif not prefix_wins and not subscript_wins:
            winning_form = "bare"
        else:
            winning_form = "mixed"

        summary = {
            "campaign_id": "PD_CG_V3_AFFIX_POSITION_TEST",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample_size": {
                "seed_count": cfg.seeds,
                "steps_per_seed": cfg.steps,
                "total_condition_steps": cfg.seeds * cfg.steps * 3,
            },
            "comparisons": {
                "bare_vs_subscripted": bare_vs_sub,
                "bare_vs_prefixed": bare_vs_pre,
                "subscripted_vs_prefixed": sub_vs_pre,
            },
            "required_tests": {
                "bare_vs_subscript_whole_expression_RT_pass_rate": bare_vs_sub["whole_expression_RT_pass_rate"],
                "bare_vs_prefix_whole_expression_RT_pass_rate": bare_vs_pre["whole_expression_RT_pass_rate"],
                "subscript_vs_prefix_whole_expression_RT_pass_rate": sub_vs_pre["whole_expression_RT_pass_rate"],
                "affix_position_distinct_within_model": affix_distinct,
            },
            "governance_assessment": {
                "local_governance_applied": True,
                "affix_position_treated_as_binding": True,
                "forbidden_tests_used": [],
                "claim_class_recommendation": "C2_within_model",
                "bridge_promotion_recommendation": "DO_NOT_PROMOTE",
                "reason": (
                    "This campaign compares bare, subscripted, and prefixed reciprocal relation notations within a bounded single-model procedural test. "
                    "It can support only scoped within-model notation comparisons."
                ),
                "root_trace_note": (
                    "In this bounded test, bare <=> is treated as an unqualified reciprocal relation, <=>_r as relation-level r-conditioning, "
                    "and r_<=> as r-mode governance/generation of the reciprocal relation. These readings remain candidate notations pending further root-trace work."
                ),
            },
            "decision": {
                "winning_form_within_model": winning_form,
                "subscript_outperforms_bare": subscript_wins,
                "prefix_outperforms_bare": prefix_wins,
                "subscript_and_prefix_are_behaviorally_distinct": affix_distinct,
                "supports_R_AFFIX_001_within_model": affix_distinct,
                "supports_open_bridge_001_promotion": False,
            },
        }

        payload = {"summary": summary, "per_seed": per_seed}
        results_path = self.output_dir / "affix_position_results.json"
        with results_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        report_path = self.output_dir / "affix_position_report.md"
        with report_path.open("w", encoding="utf-8") as handle:
            handle.write(self.render_report(summary, results_path))

        print("[PD_CG_V3] Affix position test complete.")
        print(json.dumps(summary, indent=2))
        print(f"[PD_CG_V3] Results written to {results_path}")
        print(f"[PD_CG_V3] Report written to {report_path}")
        return payload

    def render_report(self, summary, results_path):
        bare_vs_sub = summary["comparisons"]["bare_vs_subscripted"]
        bare_vs_pre = summary["comparisons"]["bare_vs_prefixed"]
        sub_vs_pre = summary["comparisons"]["subscripted_vs_prefixed"]
        decision = summary["decision"]
        governance = summary["governance_assessment"]
        return "\n".join(
            [
                "# PD_CG_V3 Affix Position Test",
                "",
                "## 1. Scope",
                "Compare bare reciprocal relation `<=>`, subscripted reciprocal relation `<=>_r`, and prefixed reciprocal relation `r_<=>` inside a bounded procedural model without assuming affix equivalence.",
                "",
                "## 2. Directly observed/defined",
                f"- Seed count: {summary['sample_size']['seed_count']}",
                f"- Steps per seed: {summary['sample_size']['steps_per_seed']}",
                f"- Bare vs subscript survival gain mean: {bare_vs_sub['basin_survival_gain_mean']:.4f}",
                f"- Bare vs subscript class-recovery gain mean: {bare_vs_sub['admissibility_class_recovery_gain_mean']:.4f}",
                f"- Bare vs subscript mediation gain mean: {bare_vs_sub['boundary_front_mediation_gain_mean']:.4f}",
                f"- Bare vs prefix survival gain mean: {bare_vs_pre['basin_survival_gain_mean']:.4f}",
                f"- Bare vs prefix class-recovery gain mean: {bare_vs_pre['admissibility_class_recovery_gain_mean']:.4f}",
                f"- Bare vs prefix mediation gain mean: {bare_vs_pre['boundary_front_mediation_gain_mean']:.4f}",
                f"- Subscript vs prefix separation score mean: {sub_vs_pre['affix_position_separation_score_mean']:.4f}",
                f"- Bare vs subscript whole-expression pass rate: {bare_vs_sub['whole_expression_RT_pass_rate']:.4f}",
                f"- Bare vs prefix whole-expression pass rate: {bare_vs_pre['whole_expression_RT_pass_rate']:.4f}",
                f"- Subscript vs prefix whole-expression pass rate: {sub_vs_pre['whole_expression_RT_pass_rate']:.4f}",
                "",
                "## 3. Inferred inside framework",
                f"- Winning form within this model: {decision['winning_form_within_model']}",
                f"- Affix position changes behavior within this model: {decision['supports_R_AFFIX_001_within_model']}",
                "",
                "## 4. External resemblance (Analogy only)",
                "- None asserted. This report remains inside a bounded procedural notation test.",
                "",
                "## 5. What it does NOT prove",
                "- It does not resolve OPEN_BRIDGE_001.",
                "- It does not establish external physical truth or universal notation equivalence.",
                "- It does not collapse `<=>_r` into `r_<=>` or vice versa beyond this tested model.",
                "",
                "## 6. Failure modes / uncertainty",
                f"- Claim class recommendation: {governance['claim_class_recommendation']}",
                f"- Bridge promotion recommendation: {governance['bridge_promotion_recommendation']}",
                "- This remains a single-model Python simulation rather than a cross-mechanism notation study.",
                "- Reciprocal relation readings remain candidate notations pending further root-trace work and registry decisions.",
                f"- Evidence path: {results_path.as_posix()}",
            ]
        )


if __name__ == "__main__":
    analyzer = AffixPositionTest()
    analyzer.run()
