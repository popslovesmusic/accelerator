import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Config:
    mode: str = "M0_CORE"
    steps: int = 3000
    n_candidates: int = 5
    epsilon_floor: float = 0.05
    residue_decay: float = 0.1
    noise: float = 0.01
    seed: int = 42
    initial_E: float = 1.0
    decay: float = 0.05  # Natural tendency to collapse
    candidate_sigma: float = 0.1

class CoreAxiomPilot:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.E = cfg.initial_E
        self.residue = 0.0
        self.history = []
        self.a_survival_history = []
        self.collapsed = False

    def get_features(self):
        m = self.cfg.mode
        # Features: [E_nonzero_init, delta_a, residue]
        if m == "M0_CORE":
            return True, True, True
        if m == "M1_NO_RESIDUE":
            return True, True, False
        if m == "M2_NO_ADMISSIBILITY":
            return True, False, False
        if m == "M3_ZERO_PRESSURE":
            return False, False, False
        if m == "M4_MEMORY_ONLY":
            return True, False, True
        return True, False, False

    def is_admissible(self, d, E):
        # Admissible if it prevents collapse
        return (E - self.cfg.decay + d) > self.cfg.epsilon_floor

    def step(self):
        c = self.cfg
        if self.collapsed:
            self.history.append(0.0)
            self.a_survival_history.append(0.0)
            return

        e_init, delta_a, use_residue = self.get_features()

        # Generate candidates
        candidates = self.rng.normal(c.decay, c.candidate_sigma, c.n_candidates)

        if delta_a:
            admissible = [d for d in candidates if self.is_admissible(d, self.E)]
        else:
            admissible = list(candidates)

        self.a_survival_history.append(len(admissible) / c.n_candidates)

        if not admissible:
            self.E = 0.0
            self.collapsed = True
            self.history.append(0.0)
            return

        if use_residue:
            # Pick candidate closest to residue (previous successful directions)
            idx = np.argmin([abs(d - self.residue) for d in admissible])
            d_selected = admissible[idx]
        else:
            # Random pick
            d_selected = self.rng.choice(admissible)

        # Update E
        self.E = self.E - c.decay + d_selected + self.rng.normal(0, c.noise)
        
        # Enforce hard floor
        if self.E <= 0:
            self.E = 0.0
            self.collapsed = True
        
        self.history.append(float(self.E))

        # Update residue
        if use_residue:
            self.residue = (1.0 - c.residue_decay) * self.residue + c.residue_decay * d_selected

    def run(self):
        e_init, _, _ = self.get_features()
        if not e_init:
            self.E = 0.0
            self.collapsed = True
        
        for _ in range(self.cfg.steps):
            self.step()
        return self.metrics()

    def metrics(self):
        hist = np.array(self.history)
        e_persist = np.mean(hist > self.cfg.epsilon_floor)
        
        collapsed_indices = np.where(hist <= self.cfg.epsilon_floor)[0]
        if len(collapsed_indices) > 0:
            collapse_step = int(collapsed_indices[0])
            collapse_rate = 1.0 / (collapse_step + 1)
        else:
            collapse_rate = 0.0
            
        a_survival = np.mean(self.a_survival_history)
        
        # R_dependence: if use_residue, how much did E stabilize?
        # We can use variance of E in the tail as a proxy for stability.
        tail = hist[len(hist)//2:]
        stability = float(np.std(tail)) if len(tail) > 0 else 1.0

        return {
            "mode": self.cfg.mode,
            "E_persist": float(e_persist),
            "E_collapse_rate": float(collapse_rate),
            "A_survival": float(a_survival),
            "stability_std": stability,
            "final_E": float(self.E)
        }

def run_campaign(out_dir="results/LFCR_005_CORE_AXIOM_PILOT", seeds=100):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    modes = [
        "M0_CORE",
        "M1_NO_RESIDUE",
        "M2_NO_ADMISSIBILITY",
        "M3_ZERO_PRESSURE",
        "M4_MEMORY_ONLY"
    ]

    all_results = []

    for mode in modes:
        mode_results = []
        print(f"Running mode: {mode}")
        for seed in range(seeds):
            cfg = Config(mode=mode, seed=seed)
            sim = CoreAxiomPilot(cfg)
            res = sim.run()
            mode_results.append(res)
            all_results.append(res)
            
        summary = {
            "mode": mode,
            "seeds": seeds,
            "mean_E_persist": float(np.mean([r["E_persist"] for r in mode_results])),
            "mean_E_collapse_rate": float(np.mean([r["E_collapse_rate"] for r in mode_results])),
            "mean_A_survival": float(np.mean([r["A_survival"] for r in mode_results])),
            "mean_stability_std": float(np.mean([r["stability_std"] for r in mode_results])),
            "mean_final_E": float(np.mean([r["final_E"] for r in mode_results]))
        }
        
        with open(out / f"{mode}_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    with open(out / "all_metrics.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Success comparison
    summaries = {}
    for mode in modes:
        with open(out / f"{mode}_summary.json", "r") as f:
            summaries[mode] = json.load(f)
            
    m0_p = summaries["M0_CORE"]["mean_E_persist"]
    m1_p = summaries["M1_NO_RESIDUE"]["mean_E_persist"]
    m2_p = summaries["M2_NO_ADMISSIBILITY"]["mean_E_persist"]
    m4_p = summaries["M4_MEMORY_ONLY"]["mean_E_persist"]
    
    report = {
        "campaign_id": "LFCR_005_CORE_AXIOM_PILOT",
        "status": "COMPLETED",
        "m0_vs_m1_diff": m0_p - m1_p,
        "m0_vs_m2_diff": m0_p - m2_p,
        "m0_vs_m4_diff": m0_p - m4_p,
        "success": (m0_p > m1_p) and (m0_p > m2_p) and (m0_p > m4_p)
    }
    
    with open(out / "campaign_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_campaign()
