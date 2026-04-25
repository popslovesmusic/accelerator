from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


EPS = 1.0e-12
NOISE_FLOOR = 1.0e-300


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compute_d_sr(mean_r: float, mean_eps: float, mean_rho: float) -> float:
    return mean_r / max(mean_eps + mean_rho, EPS)


def compute_l(interface_lifetime: float, t_max: float) -> float:
    return max(0.0, min(1.0, interface_lifetime / max(t_max, EPS)))


def clean_scalar(value: float) -> float:
    if abs(value) < NOISE_FLOOR:
        return 0.0
    return value


def classify_proxy(d_sr: float, l_value: float, k_value: float, collapsed: bool, final_exclusion_fraction: float) -> str:
    if collapsed and final_exclusion_fraction >= 0.999 and d_sr < 10.0:
        return "collapse"
    if d_sr >= 10.0 and l_value >= 0.75 and k_value >= 1.0:
        return "self_referential"
    if d_sr >= 10.0 and l_value < 0.75 and k_value < 1.0:
        return "transient_high_density"
    return "intermediate"


def normalize_ic(ic_value: str) -> str:
    mapping = {"0": "IC0", "1": "IC1", "2": "IC2"}
    return mapping.get(ic_value, ic_value)


def load_run_level_rows(root: Path) -> list[dict[str, str]]:
    run_results_path = root / "run_results.csv"
    if run_results_path.exists():
        return read_csv(run_results_path)

    manifest = {row["run_id"]: row for row in read_csv(root / "run_manifest.csv")}
    summary = {row["run_id"]: row for row in read_csv(root / "final_summary.csv")}
    timeseries: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(root / "timeseries_global.csv"):
        timeseries[row["run_id"]].append(row)

    rows: list[dict[str, str]] = []
    for run_id, manifest_row in manifest.items():
        summary_row = summary[run_id]
        series = timeseries[run_id]
        t_max = float(manifest_row["t_final"])
        exclusion_time = None
        interface_loss_time = None
        max_interface_count = 0
        for row in series:
            time_value = float(row["time"])
            exclusion_fraction = float(row["exclusion_fraction"])
            interface_count = int(float(row["interface_count"]))
            max_interface_count = max(max_interface_count, interface_count)
            if exclusion_time is None and exclusion_fraction >= 1.0:
                exclusion_time = time_value
            if interface_loss_time is None and interface_count == 0:
                interface_loss_time = time_value
        rows.append(
            {
                "run_id": run_id,
                "kappa": manifest_row["kappa"],
                "lambda": manifest_row["lam"],
                "D_eps": manifest_row["D_eps"],
                "D_rho": manifest_row["D_rho"],
                "IC_family": manifest_row["ic_type"],
                "replicate_id": manifest_row["seed"],
                "seed": manifest_row["seed"],
                "T_max": manifest_row["t_final"],
                "collapsed_bool": str(exclusion_time is not None),
                "time_to_full_exclusion": f"{(exclusion_time if exclusion_time is not None else t_max):.6f}",
                "final_exclusion_fraction": summary_row["final_exclusion_fraction"],
                "final_mean_rho": summary_row["final_mean_rho"],
                "final_mean_R": summary_row["final_mean_R"],
                "final_mean_eps": summary_row["final_mean_eps"],
                "max_interface_count": str(max_interface_count),
                "late_time_front_speed": summary_row["late_time_mean_front_speed"],
                "interface_lifetime": f"{(interface_loss_time if interface_loss_time is not None else t_max):.6f}",
                "rho_plateau_duration": f"{(t_max if float(summary_row['final_mean_rho']) > 0.0 else 0.0):.6f}",
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute empirical L and D_sr proxies from existing CSV exports.")
    parser.add_argument("--input-root", required=True, help="Batch output directory containing run_results.csv or batch_runner CSVs.")
    parser.add_argument("--output-prefix", default="sr_metrics", help="Prefix for generated CSV files inside the input root.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.input_root).resolve()
    rows = load_run_level_rows(root)

    run_metric_rows: list[dict[str, str]] = []
    parameter_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        t_max = float(row["T_max"])
        final_mean_r = clean_scalar(float(row["final_mean_R"]))
        final_mean_eps = clean_scalar(float(row["final_mean_eps"]))
        final_mean_rho = clean_scalar(float(row["final_mean_rho"]))
        interface_lifetime = float(row["interface_lifetime"])
        k_value = float(row["max_interface_count"])
        d_sr = compute_d_sr(final_mean_r, final_mean_eps, final_mean_rho)
        l_value = compute_l(interface_lifetime, t_max)
        collapsed = row["collapsed_bool"].lower() == "true"
        final_exclusion_fraction = float(row["final_exclusion_fraction"])
        proxy_class = classify_proxy(d_sr, l_value, k_value, collapsed, final_exclusion_fraction)

        metric_row = {
            "run_id": row["run_id"],
            "kappa": row["kappa"],
            "lambda": row["lambda"],
            "D_eps": row["D_eps"],
            "D_rho": row["D_rho"],
            "IC_family": normalize_ic(row["IC_family"]),
            "seed": row["seed"],
            "T_max": row["T_max"],
            "collapsed_bool": row["collapsed_bool"],
            "time_to_full_exclusion": row["time_to_full_exclusion"],
            "final_exclusion_fraction": row["final_exclusion_fraction"],
            "final_mean_rho": f"{final_mean_rho:.6f}",
            "final_mean_R": f"{final_mean_r:.6f}",
            "final_mean_eps": f"{final_mean_eps:.6f}",
            "K_proxy": f"{k_value:.6f}",
            "L_proxy": f"{l_value:.6f}",
            "D_sr_proxy": f"{d_sr:.6f}",
            "proxy_class": proxy_class,
        }
        run_metric_rows.append(metric_row)
        parameter_groups[(row["D_eps"], row["D_rho"], row["kappa"], row["lambda"])].append(metric_row)

    run_fields = [
        "run_id", "kappa", "lambda", "D_eps", "D_rho", "IC_family", "seed", "T_max", "collapsed_bool",
        "time_to_full_exclusion", "final_exclusion_fraction", "final_mean_rho", "final_mean_R", "final_mean_eps",
        "K_proxy", "L_proxy", "D_sr_proxy", "proxy_class",
    ]
    write_csv(root / f"{args.output_prefix}_run_metrics.csv", run_metric_rows, run_fields)

    parameter_rows: list[dict[str, str]] = []
    for key, group_rows in sorted(parameter_groups.items(), key=lambda item: tuple(float(v) for v in item[0])):
        d_eps, d_rho, kappa, lam = key
        d_sr_values = [float(row["D_sr_proxy"]) for row in group_rows]
        l_values = [float(row["L_proxy"]) for row in group_rows]
        k_values = [float(row["K_proxy"]) for row in group_rows]
        collapse_fraction = sum(row["collapsed_bool"].lower() == "true" for row in group_rows) / len(group_rows)
        class_counts: dict[str, int] = defaultdict(int)
        for row in group_rows:
            class_counts[row["proxy_class"]] += 1
        dominant_class = max(class_counts.items(), key=lambda item: item[1])[0]
        parameter_rows.append(
            {
                "D_eps": d_eps,
                "D_rho": d_rho,
                "kappa": kappa,
                "lambda": lam,
                "n_runs": str(len(group_rows)),
                "collapse_fraction": f"{collapse_fraction:.6f}",
                "mean_D_sr_proxy": f"{mean(d_sr_values):.6f}",
                "max_D_sr_proxy": f"{max(d_sr_values):.6f}",
                "mean_L_proxy": f"{mean(l_values):.6f}",
                "mean_K_proxy": f"{mean(k_values):.6f}",
                "dominant_proxy_class": dominant_class,
            }
        )

    parameter_fields = [
        "D_eps", "D_rho", "kappa", "lambda", "n_runs", "collapse_fraction",
        "mean_D_sr_proxy", "max_D_sr_proxy", "mean_L_proxy", "mean_K_proxy", "dominant_proxy_class",
    ]
    write_csv(root / f"{args.output_prefix}_parameter_summary.csv", parameter_rows, parameter_fields)

    readme = (
        "Empirical proxy definitions used here:\n"
        "- D_sr_proxy = final_mean_R / max(final_mean_eps + final_mean_rho, 1e-12)\n"
        "- L_proxy = interface_lifetime / T_max, clamped to [0, 1]\n"
        "- K_proxy = max_interface_count\n"
        "These are operational proxies derived from existing CSV exports, not theorem-level definitions.\n"
    )
    (root / f"{args.output_prefix}_README.txt").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
