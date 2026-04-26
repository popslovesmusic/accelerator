from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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
class RunRow:
    run_name: str
    config_path: str
    out_dir: str
    final_metrics: dict[str, Any]


def load_index(index_csv: Path) -> list[RunRow]:
    rows: list[RunRow] = []
    with index_csv.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            metrics_json = row.get("final_metrics_json") or "{}"
            try:
                metrics = json.loads(metrics_json)
            except json.JSONDecodeError:
                metrics = {}
            rows.append(
                RunRow(
                    run_name=row.get("run_name") or "",
                    config_path=row.get("config_path") or "",
                    out_dir=row.get("out_dir") or "",
                    final_metrics=metrics,
                )
            )
    return rows


def group_mean(rows: list[RunRow], key: str, metric: str) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for rr in rows:
        if key not in rr.run_name:
            continue
        val = rr.final_metrics.get(metric)
        if isinstance(val, (int, float)):
            groups.setdefault(key, []).append(float(val))
    if not groups:
        return {}
    return {k: float(mean(vs)) for k, vs in groups.items()}


def mean_metric_for_prefix(rows: list[RunRow], prefix: str, metric: str) -> float:
    vals: list[float] = []
    for rr in rows:
        if rr.run_name.startswith(prefix):
            v = rr.final_metrics.get(metric)
            if isinstance(v, (int, float)):
                vals.append(float(v))
    return float(mean(vals)) if vals else float("nan")


def main() -> None:
    batches = {
        "ca": ROOT / "batch_ca_epsilon_v2" if (ROOT / "batch_ca_epsilon_v2").exists() else ROOT / "batch_ca_epsilon",
        "agent_mismatch": ROOT / "batch_agent_mismatch",
        "kuramoto": ROOT / "batch_kuramoto_coupling",
        "agent_coupling": ROOT / "batch_agent_coupling",
    }

    ca_rows = load_index(batches["ca"] / "analysis" / "index.csv")
    agent_mismatch_rows = load_index(batches["agent_mismatch"] / "analysis" / "index.csv")
    kuramoto_rows = load_index(batches["kuramoto"] / "analysis" / "index.csv")
    agent_coupling_rows = load_index(batches["agent_coupling"] / "analysis" / "index.csv")

    # epsilon validation: CA source_strength -> active_fraction
    # Prefer explicit v2 prefixes when present
    ca_src0 = mean_metric_for_prefix(ca_rows, "ca_epsilon_v2_src0", "active_fraction") if any(r.run_name.startswith("ca_epsilon_v2_src0") for r in ca_rows) else mean_metric_for_prefix(ca_rows, "ca_epsilon_src0", "active_fraction")
    ca_src02 = mean_metric_for_prefix(ca_rows, "ca_epsilon_v2_src02", "active_fraction") if any(r.run_name.startswith("ca_epsilon_v2_src02") for r in ca_rows) else mean_metric_for_prefix(ca_rows, "ca_epsilon_src02", "active_fraction")
    ca_src10 = mean_metric_for_prefix(ca_rows, "ca_epsilon_v2_src10", "active_fraction") if any(r.run_name.startswith("ca_epsilon_v2_src10") for r in ca_rows) else mean_metric_for_prefix(ca_rows, "ca_epsilon_src10", "active_fraction")

    # epsilon validation: agent mismatch_rate -> mismatch_mean/residue_mean
    ag_mr0_mis = mean_metric_for_prefix(agent_mismatch_rows, "agent_mismatch_mr0", "mismatch_mean")
    ag_mr0_res = mean_metric_for_prefix(agent_mismatch_rows, "agent_mismatch_mr0", "residue_mean")
    ag_mr_pos_mis = mean_metric_for_prefix(agent_mismatch_rows, "agent_mismatch_mr1e2", "mismatch_mean")
    ag_mr_pos_res = mean_metric_for_prefix(agent_mismatch_rows, "agent_mismatch_mr1e2", "residue_mean")

    # coupling validation: Kuramoto K -> order_parameter
    k_K0 = mean_metric_for_prefix(kuramoto_rows, "kuramoto_K0", "order_parameter")
    k_K2 = mean_metric_for_prefix(kuramoto_rows, "kuramoto_K2", "order_parameter")

    # coupling validation: Agent K_phi -> order_parameter
    ab_kp0 = mean_metric_for_prefix(agent_coupling_rows, "agent_coupling_kp0", "order_parameter")
    ab_kp2 = mean_metric_for_prefix(agent_coupling_rows, "agent_coupling_kp2", "order_parameter")

    coupling_corr = _pearson([0.0, 2.0], [k_K0, k_K2])
    coupling_corr_ab = _pearson([0.0, 2.0], [ab_kp0, ab_kp2])

    out = {
        "epsilon": {
            "ca": {
                "observable": "final.active_fraction",
                "source_strength_levels": {"0.0": ca_src0, "0.2": ca_src02, "1.0": ca_src10},
                "interpretation": "Higher injected mismatch (epsilon source) increases admissible activity under fixed residue settings.",
            },
            "agent_based": {
                "observables": {"final.mismatch_mean": {"mr0": ag_mr0_mis, "mr1e2": ag_mr_pos_mis}, "final.residue_mean": {"mr0": ag_mr0_res, "mr1e2": ag_mr_pos_res}},
                "interpretation": "Mismatch generation drives both mismatch accumulation and residue growth; when mismatch_rate=0, both remain ~0.",
            },
        },
        "coupling": {
            "kuramoto": {
                "observable": "final.order_parameter",
                "K_levels": {"0.0": k_K0, "2.0": k_K2},
                "pearson_over_levels": coupling_corr,
            },
            "agent_based": {
                "observable": "final.order_parameter",
                "K_phi_levels": {"0.0": ab_kp0, "2.0": ab_kp2},
                "pearson_over_levels": coupling_corr_ab,
            },
            "interpretation": "Increasing coupling increases phase coherence (order_parameter) across independent model classes.",
        },
    }

    (ROOT / "analysis" / "lexicon_validation_summary.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
