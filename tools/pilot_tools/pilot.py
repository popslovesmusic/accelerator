"""
LFCR_004 Phase-Lag Closure Pilot v0.2

Purpose:
Exploratory only. Tests whether stable closure is better explained by
non-canceling phase-lagged recurrence than by raw synchronization.

Claim under test:
D(A|B)_phi <=>_ra D(B|A)_{phi + Delta_phi_R} > 0

This pilot does NOT make ontology-level claims.
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Config:
    mode: str = "M0_PHASE_LAG_RA"
    n_nodes: int = 2
    steps: int = 3000
    dt: float = 0.03
    coupling: float = 1.0
    alpha: float = 0.75              # target phase lag Δφ_R
    residue_decay: float = 0.03
    noise: float = 0.01
    seed: int = 42
    perturb_step: int = 1500
    perturb_strength: float = 0.8


class PhaseLagClosurePilot:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.phi = self.rng.uniform(0, 2*np.pi, cfg.n_nodes)
        self.omega = self.rng.normal(1.0, 0.03, cfg.n_nodes)
        self.residue = np.zeros((cfg.n_nodes, cfg.n_nodes))
        self.phase_history = []

    def wrap(self, x):
        return (x + np.pi) % (2*np.pi) - np.pi

    def target_alpha(self, i, j, step):
        c = self.cfg

        if c.mode == "M1_ZERO_LAG":
            return 0.0

        if c.mode == "M2_RANDOM_LAG":
            return self.rng.uniform(-np.pi, np.pi)

        if c.mode == "M3_CANCELING_LAG":
            return np.pi

        return c.alpha

    def residue_factor(self, i, j, diff):
        c = self.cfg

        if c.mode == "M4_MEMORYLESS_LAG":
            return 0.0

        # residue tracks recurrence of the same phase relation,
        # not generic synchrony
        self.residue[i, j] = (
            (1.0 - c.residue_decay) * self.residue[i, j]
            + c.residue_decay * np.cos(diff)
        )
        return self.residue[i, j]

    def step(self, step_idx):
        c = self.cfg
        dphi = np.zeros(c.n_nodes)

        for i in range(c.n_nodes):
            coupling_sum = 0.0

            for j in range(c.n_nodes):
                if i == j:
                    continue

                alpha_ij = self.target_alpha(i, j, step_idx)
                diff = self.wrap((self.phi[j] - self.phi[i]) - alpha_ij)

                r = self.residue_factor(i, j, diff)

                if c.mode == "M5_TOPOLOGY_MATCH":
                    # topology preserved, phase relation scrambled
                    diff = self.wrap(self.rng.uniform(-np.pi, np.pi))

                if c.mode == "M6_DENSITY_MATCH":
                    # same coupling density/strength, no coherent phase target
                    alpha_ij = 0.0
                    diff = self.wrap(self.phi[j] - self.phi[i])

                coupling_sum += c.coupling * np.sin(diff) * (1.0 + r)

            dphi[i] = self.omega[i] + coupling_sum / max(1, c.n_nodes - 1)

        dphi += self.rng.normal(0, c.noise, c.n_nodes)

        if step_idx == c.perturb_step:
            self.phi += self.rng.normal(0, c.perturb_strength, c.n_nodes)

        self.phi = (self.phi + c.dt * dphi) % (2*np.pi)

        if c.n_nodes == 2:
            phase_diff = self.wrap(self.phi[1] - self.phi[0])
            self.phase_history.append(float(phase_diff))

    def run(self):
        for t in range(self.cfg.steps):
            self.step(t)
        return self.metrics()

    def metrics(self):
        c = self.cfg
        hist = np.array(self.phase_history)
        tail = hist[len(hist)//2:]

        if len(tail) == 0:
            raise RuntimeError("No phase history recorded.")

        # Raw synchronization: kept as diagnostic only, not target closure
        order_parameter = abs(np.mean(np.exp(1j * self.phi)))

        # Target phase relation
        if c.mode == "M1_ZERO_LAG":
            target = 0.0
        elif c.mode == "M3_CANCELING_LAG":
            target = np.pi
        elif c.mode in ["M5_TOPOLOGY_MATCH", "M6_DENSITY_MATCH"]:
            target = 0.0
        else:
            target = c.alpha

        phase_error = np.abs([self.wrap(x - target) for x in tail])
        phase_error_mean = float(np.mean(phase_error))
        phase_error_std = float(np.std(phase_error))

        # Closure should mean stable recurrence of intended phase relation
        phase_lock_score = float(np.exp(-phase_error_mean))

        # Non-canceling score penalizes zero and pi cancellation bands
        nonzero_score = float(1.0 - np.exp(-abs(self.wrap(np.mean(tail)))))
        noncancel_score = float(1.0 - np.exp(-abs(abs(self.wrap(np.mean(tail))) - np.pi)))

        # Residue coherence
        residue_mean = float(np.mean(self.residue))
        residue_abs = float(np.mean(np.abs(self.residue)))

        # Perturbation recovery: compare before/after tail stability
        midpoint = len(hist) // 2
        post = hist[midpoint:]
        recovery_std = float(np.std(post))

        closure_score = float(
            0.45 * phase_lock_score
            + 0.25 * nonzero_score
            + 0.15 * noncancel_score
            + 0.15 * np.exp(-recovery_std)
        )

        return {
            "mode": c.mode,
            "order_parameter_diagnostic": float(order_parameter),
            "target_phase": float(target),
            "phase_error_mean": phase_error_mean,
            "phase_error_std": phase_error_std,
            "phase_lock_score": phase_lock_score,
            "nonzero_phase_score": nonzero_score,
            "noncancel_score": noncancel_score,
            "residue_mean": residue_mean,
            "residue_abs": residue_abs,
            "recovery_std": recovery_std,
            "S_phase_closure": closure_score
        }


def run_sweep(out_dir="results/LFCR_004_PHASE_LAG_PILOT_V02", seeds=100):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    modes = [
        "M0_PHASE_LAG_RA",
        "M1_ZERO_LAG",
        "M2_RANDOM_LAG",
        "M3_CANCELING_LAG",
        "M4_MEMORYLESS_LAG",
        "M5_TOPOLOGY_MATCH",
        "M6_DENSITY_MATCH"
    ]

    all_rows = []

    for mode in modes:
        rows = []
        for seed in range(seeds):
            cfg = Config(mode=mode, seed=seed)
            sim = PhaseLagClosurePilot(cfg)
            metrics = sim.run()
            rows.append(metrics)
            all_rows.append(metrics)

        summary = {
            "mode": mode,
            "seeds": seeds,
            "mean_S_phase_closure": float(np.mean([r["S_phase_closure"] for r in rows])),
            "std_S_phase_closure": float(np.std([r["S_phase_closure"] for r in rows])),
            "mean_order_parameter_diagnostic": float(np.mean([r["order_parameter_diagnostic"] for r in rows])),
            "mean_phase_error": float(np.mean([r["phase_error_mean"] for r in rows])),
            "mean_residue_abs": float(np.mean([r["residue_abs"] for r in rows]))
        }

        with open(out / f"{mode}_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    with open(out / "all_metrics.json", "w") as f:
        json.dump(all_rows, f, indent=2)

    print(json.dumps({
        "status": "EXPLORATORY_ONLY",
        "out_dir": str(out),
        "seeds": seeds,
        "note": "Uses phase-closure metric, not raw Kuramoto synchronization as closure."
    }, indent=2))


if __name__ == "__main__":
    run_sweep()