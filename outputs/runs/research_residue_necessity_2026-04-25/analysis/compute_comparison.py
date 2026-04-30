from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = mean(x)
    my = mean(y)
    vx = sum((xi - mx) ** 2 for xi in x)
    vy = sum((yi - my) ** 2 for yi in y)
    if vx <= 0.0 or vy <= 0.0:
        return float("nan")
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    return cov / math.sqrt(vx * vy)


@dataclass(frozen=True)
class SweepPoint:
    level: str
    activity: float


def load_ca_sweep() -> list[SweepPoint]:
    levels = ["L0", "L1", "L2", "L3"]
    points: list[SweepPoint] = []
    for level in levels:
        summary = _read_json(RUNS / f"ca_sweep_{level}" / "summary.json")
        metrics = summary["final_metrics"]
        points.append(SweepPoint(level=level, activity=float(metrics["active_fraction"])))
    return points


def load_fsa_sweep() -> list[SweepPoint]:
    # Map CA levels to FSA residue requirements used in configs
    level_to_req = {"L0": "R0", "L1": "R5", "L2": "R15", "L3": "R30"}
    seeds = [21, 22, 23]
    n_agents = 1000.0
    points: list[SweepPoint] = []
    for level in ["L0", "L1", "L2", "L3"]:
        req = level_to_req[level]
        activities: list[float] = []
        for seed in seeds:
            summary = _read_json(RUNS / f"fsa_sweep_{req}_seed{seed}" / "summary.json")
            metrics = summary["final_metrics"]
            activities.append(float(metrics["active_count"]) / n_agents)
        points.append(SweepPoint(level=level, activity=float(mean(activities))))
    return points


def main() -> None:
    ca = load_ca_sweep()
    fsa = load_fsa_sweep()

    ca_activity = [p.activity for p in ca]
    fsa_activity = [p.activity for p in fsa]
    corr = _pearson(ca_activity, fsa_activity)

    out = {
        "mapping": {
            "law": "V.1 The Filter (Admissibility)",
            "ca_levels": [p.level for p in ca],
            "fsa_levels": [p.level for p in fsa],
            "fsa_level_to_residue_required": {"L0": 0, "L1": 5, "L2": 15, "L3": 30},
        },
        "observables": {
            "ca_activity_fraction": ca_activity,
            "fsa_activity_fraction_mean_over_seeds": fsa_activity,
            "normalization": "[0,1] fractions",
        },
        "cross_model_comparison": {
            "pearson_correlation": corr,
            "agreement_type": (
                "strong" if corr > 0.8 else "partial" if corr > 0.4 else "contradiction"
            ),
        },
    }

    (ROOT / "analysis" / "cross_model_comparison.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # Lightweight CSV for inspection
    lines = ["level,ca_active_fraction,fsa_active_fraction_mean"]
    for level, ca_p, fsa_p in zip([p.level for p in ca], ca, fsa):
        lines.append(f"{level},{ca_p.activity:.9f},{fsa_p.activity:.9f}")
    (ROOT / "analysis" / "sweep_summary.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

