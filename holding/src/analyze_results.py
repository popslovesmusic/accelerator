from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable


def _import_stdlib_csv():
    original_sys_path = list(sys.path)
    cwd = str(Path.cwd().resolve())
    module_dir = str(Path(__file__).resolve().parent)
    parent_dir = str(Path(__file__).resolve().parent.parent)
    try:
        sys.path = [
            entry for entry in sys.path
            if entry not in {"", cwd, module_dir, parent_dir}
        ]
        import csv as stdlib_csv
    finally:
        sys.path = original_sys_path
    return stdlib_csv


csv = _import_stdlib_csv()


@dataclass
class RunState:
    run_id: str = ""
    sim_id: str = ""
    batch_id: str = ""
    run_date: str = ""
    phase_expression: str = ""
    kappa: float = 0.0
    lam: float = 0.0
    seed: str = ""
    ic_type: str = ""
    source_batch: str = ""
    source_root: str = ""
    final_exclusion_fraction: float = 0.0
    final_mean_rho: float = 0.0
    final_interface_count: float = 0.0
    final_time: float = 0.0
    interface_loss_time: float | None = None
    final_active_fraction: float | None = None
    final_excluded_active_fraction: float | None = None
    max_observed_sharpness: float = 0.0
    collapse_time: str = ""
    seed_unanimity: str = ""
    has_summary: bool = False


@dataclass
class FrontFrame:
    time: float
    position: float
    velocity: float
    width: float
    sharpness: float


@dataclass
class ProfileFrame:
    time: float
    x: list[float]
    eps: list[float]
    rho: list[float]
    residue: list[float]
    node_ratio: list[float]
    sharpness: list[float]


PROFILE_RE = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p]+)\.csv$", re.IGNORECASE)


def classify(state: RunState) -> str:
    if state.final_interface_count < 0.5 and state.final_exclusion_fraction >= 0.95 and state.final_mean_rho <= 0.05:
        return "runaway"
    if (
        state.final_interface_count >= 0.5
        and 0.05 < state.final_exclusion_fraction < 0.95
        and state.final_mean_rho > 0.25
    ):
        return "SS3"
    if state.final_interface_count < 0.5 and state.final_exclusion_fraction <= 0.05 and state.final_mean_rho >= 1.5:
        return "SS2"
    return "other"


def find_native_executable(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))

    here = Path(__file__).resolve().parent
    candidates.extend(
        [
            here / "level2_results_analyzer.exe",
            here / "level2_results_analyzer",
            here.parent / "level2_results_analyzer.exe",
            here.parent / "level2_results_analyzer",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def run_native(native_exe: Path, input_root: Path, output_prefix: Path) -> int:
    command = [str(native_exe), str(input_root), str(output_prefix)]
    completed = subprocess.run(command, check=False)
    return completed.returncode


def read_csv_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def write_csv_rows(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_float_value(*values: object, default: float = 0.0) -> float:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return float(value)
    return default


def collect_run_manifest(input_root: Path) -> dict[str, dict[str, str]]:
    manifests: dict[str, dict[str, str]] = {}
    for path in input_root.rglob("run_manifest.csv"):
        batch = path.parent.name
        for row in read_csv_rows(path):
            manifests[row["run_id"]] = {
                "sim_id": row.get("sim_id", ""),
                "batch_id": row.get("batch_id", batch),
                "run_date": row.get("run_date", ""),
                "phase_expression": row.get("phase_expression", ""),
                "seed": row.get("seed", ""),
                "ic_type": row.get("ic_type", ""),
                "source_batch": batch,
                "source_root": str(path.parent),
            }
    return manifests


def enrich_runs_with_manifest(runs: Dict[str, RunState], manifests: dict[str, dict[str, str]]) -> None:
    for run_id, state in runs.items():
        state.run_id = run_id
        manifest = manifests.get(run_id, {})
        state.sim_id = manifest.get("sim_id", "")
        state.batch_id = manifest.get("batch_id", "")
        state.run_date = manifest.get("run_date", "")
        state.phase_expression = manifest.get("phase_expression", "")
        state.seed = manifest.get("seed", "")
        state.ic_type = manifest.get("ic_type", "")
        state.source_batch = manifest.get("source_batch", "")
        state.source_root = manifest.get("source_root", "")


def analysis_status(state: RunState) -> tuple[str, str]:
    coarse_ok = state.has_summary
    deep_ok = state.has_summary and state.final_time > 0.0 and state.final_active_fraction is not None
    coarse = "ok" if coarse_ok else "missing_required_inputs"
    deep = "ok" if deep_ok else "missing_required_inputs"
    return coarse, deep


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((value - m) ** 2 for value in values) / len(values)


def parse_profile_file(path: Path) -> tuple[str, ProfileFrame] | None:
    match = PROFILE_RE.match(path.name)
    if not match:
        return None
    run_id = match.group("run_id")
    time = float(match.group("time").replace("p", "."))
    x: list[float] = []
    eps: list[float] = []
    rho: list[float] = []
    residue: list[float] = []
    node_ratio: list[float] = []
    sharpness: list[float] = []
    for row in read_csv_rows(path):
        x.append(float(row["x"]))
        eps.append(float(row["eps"]))
        rho.append(float(row["rho"]))
        residue.append(float(row["R"]))
        node_ratio.append(float(row["node_ratio"]))
        sharpness.append(float(row["sharpness"]))
    return run_id, ProfileFrame(time, x, eps, rho, residue, node_ratio, sharpness)


def collect_front_frames(input_root: Path) -> dict[str, list[FrontFrame]]:
    by_run: dict[str, list[FrontFrame]] = defaultdict(list)
    for path in input_root.rglob("front_metrics.csv"):
        for row in read_csv_rows(path):
            by_run[row["run_id"]].append(
                FrontFrame(
                    time=float(row["time"]),
                    position=float(row["front_position"]),
                    velocity=float(row["front_velocity"]),
                    width=float(row["front_width"]),
                    sharpness=float(row["front_sharpness"]),
                )
            )
    return by_run


def collect_profile_frames(input_root: Path) -> dict[str, list[ProfileFrame]]:
    by_run: dict[str, list[ProfileFrame]] = defaultdict(list)
    for path in input_root.rglob("profile_*.csv"):
        parsed = parse_profile_file(path)
        if parsed is None:
            continue
        run_id, frame = parsed
        by_run[run_id].append(frame)
    return by_run


def _count_files(path: Path, pattern: str) -> int:
    return sum(1 for candidate in path.rglob(pattern) if candidate.is_file())


def _batch_priority(batch_name: str) -> int:
    for prefix, score in [
        ("sim17", 1),
        ("sim16", 2),
        ("sim15", 3),
        ("sim14", 4),
        ("sim13", 5),
        ("sim12", 6),
        ("sim11", 7),
    ]:
        if prefix in batch_name:
            return score
    return 99


def build_inventory_outputs(input_root: Path, output_prefix: Path) -> None:
    roots = []
    if (input_root / "final_summary.csv").is_file():
        roots = [input_root]
    else:
        roots = sorted(
            [
                candidate for candidate in input_root.iterdir()
                if candidate.is_dir() and (candidate / "final_summary.csv").is_file()
            ],
            key=lambda candidate: candidate.name,
        )

    readiness_rows: list[dict[str, object]] = []
    rerun_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for batch_root in roots:
        batch_name = batch_root.name
        has_manifest = (batch_root / "run_manifest.csv").is_file()
        has_summary = (batch_root / "final_summary.csv").is_file()
        has_timeseries = (batch_root / "timeseries_global.csv").is_file()
        has_domain = (batch_root / "domain_metrics.csv").is_file()
        has_front = (batch_root / "front_metrics.csv").is_file()
        profile_dir = batch_root / "profiles"
        figure_dir = batch_root / "figures"
        profile_file_count = _count_files(profile_dir, "*.csv") if profile_dir.is_dir() else 0
        figure_file_count = _count_files(figure_dir, "*.png") if figure_dir.is_dir() else 0

        coarse_ready = has_summary and has_timeseries and has_domain
        deep_ready = coarse_ready and has_front and profile_file_count > 0
        if deep_ready:
            rerun_recommendation = "none"
            reason = ""
        elif coarse_ready and has_front and profile_file_count == 0:
            rerun_recommendation = "rerun_with_profiles"
            reason = "front_metrics present but profiles missing"
        elif coarse_ready and not has_front and profile_file_count == 0:
            rerun_recommendation = "rerun_with_fronts_and_profiles"
            reason = "front_metrics and profiles missing"
        elif coarse_ready and not has_front:
            rerun_recommendation = "rerun_with_fronts"
            reason = "profiles present but front_metrics missing"
        else:
            rerun_recommendation = "missing_coarse_inputs"
            reason = "one or more coarse CSV inputs missing"

        priority = _batch_priority(batch_name)
        priority_label = "high" if priority <= 7 else "normal"

        row = {
            "batch_name": batch_name,
            "batch_root": str(batch_root),
            "has_run_manifest": str(has_manifest).lower(),
            "has_final_summary": str(has_summary).lower(),
            "has_timeseries_global": str(has_timeseries).lower(),
            "has_domain_metrics": str(has_domain).lower(),
            "has_front_metrics": str(has_front).lower(),
            "profile_file_count": profile_file_count,
            "figure_file_count": figure_file_count,
            "coarse_ready": str(coarse_ready).lower(),
            "deep_ready": str(deep_ready).lower(),
            "rerun_recommendation": rerun_recommendation,
            "priority_rank": priority,
            "priority_label": priority_label,
            "reason": reason,
        }
        readiness_rows.append(row)

        if rerun_recommendation != "none":
            rerun_rows.append(
                {
                    "batch_name": batch_name,
                    "batch_root": str(batch_root),
                    "priority_rank": priority,
                    "priority_label": priority_label,
                    "rerun_recommendation": rerun_recommendation,
                    "reason": reason,
                    "suggested_flags": "--fast --write-profiles --skip-figures",
                }
            )

    total = len(readiness_rows)
    coarse_ready_count = sum(1 for row in readiness_rows if row["coarse_ready"] == "true")
    deep_ready_count = sum(1 for row in readiness_rows if row["deep_ready"] == "true")
    rerun_needed_count = sum(1 for row in readiness_rows if row["rerun_recommendation"] != "none")
    summary_rows.append(
        {
            "batch_count": total,
            "coarse_ready_count": coarse_ready_count,
            "deep_ready_count": deep_ready_count,
            "rerun_needed_count": rerun_needed_count,
        }
    )

    rerun_rows.sort(key=lambda row: (int(row["priority_rank"]), str(row["batch_name"])))

    write_csv_rows(
        Path(f"{output_prefix}_deep_readiness_report.csv"),
        [
            "batch_name",
            "batch_root",
            "has_run_manifest",
            "has_final_summary",
            "has_timeseries_global",
            "has_domain_metrics",
            "has_front_metrics",
            "profile_file_count",
            "figure_file_count",
            "coarse_ready",
            "deep_ready",
            "rerun_recommendation",
            "priority_rank",
            "priority_label",
            "reason",
        ],
        readiness_rows,
    )
    write_csv_rows(
        Path(f"{output_prefix}_rerun_priority.csv"),
        [
            "batch_name",
            "batch_root",
            "priority_rank",
            "priority_label",
            "rerun_recommendation",
            "reason",
            "suggested_flags",
        ],
        rerun_rows,
    )
    write_csv_rows(
        Path(f"{output_prefix}_inventory_summary.csv"),
        ["batch_count", "coarse_ready_count", "deep_ready_count", "rerun_needed_count"],
        summary_rows,
    )


def final_window_cutoff(state: RunState, frac: float = 0.2) -> float:
    return max(0.0, state.final_time * (1.0 - frac))


def group_fronts_by_time(frames: list[FrontFrame]) -> dict[float, list[FrontFrame]]:
    grouped: dict[float, list[FrontFrame]] = defaultdict(list)
    for frame in frames:
        grouped[frame.time].append(frame)
    return grouped


def profile_depth(frame: ProfileFrame) -> float:
    if not frame.residue:
        return 0.0
    return max(frame.residue) - min(frame.residue)


def wall_strength(frame: ProfileFrame) -> float:
    return max((abs(value) for value in frame.sharpness), default=0.0)


def curvature_proxy(frame: ProfileFrame) -> float:
    if len(frame.residue) < 3 or len(frame.x) < 3:
        return 0.0
    values = []
    for idx in range(1, len(frame.residue) - 1):
        dx1 = frame.x[idx] - frame.x[idx - 1]
        dx2 = frame.x[idx + 1] - frame.x[idx]
        if dx1 == 0 or dx2 == 0:
            continue
        second = (frame.residue[idx + 1] - 2.0 * frame.residue[idx] + frame.residue[idx - 1]) / (0.5 * (dx1 + dx2) ** 2)
        values.append(abs(second))
    return mean(values)


def profile_width(frame: ProfileFrame) -> float:
    if not frame.residue or not frame.x:
        return 0.0
    threshold = 0.5 * max(frame.residue)
    active = [x for x, value in zip(frame.x, frame.residue) if value >= threshold]
    if not active:
        return 0.0
    return max(active) - min(active)


def peak_count(frame: ProfileFrame) -> int:
    count = 0
    for idx in range(1, len(frame.residue) - 1):
        if frame.residue[idx] > frame.residue[idx - 1] and frame.residue[idx] > frame.residue[idx + 1]:
            count += 1
    return count


def profile_similarity(frames: list[ProfileFrame]) -> float:
    if len(frames) < 2:
        return 1.0
    base = frames[-1].residue
    if not base:
        return 0.0
    base_norm = math.sqrt(sum(value * value for value in base)) or 1.0
    sims: list[float] = []
    for frame in frames[:-1]:
        if len(frame.residue) != len(base):
            continue
        dot = sum(a * b for a, b in zip(frame.residue, base))
        norm = math.sqrt(sum(value * value for value in frame.residue)) or 1.0
        sims.append(dot / (base_norm * norm))
    return mean(sims) if sims else 1.0


def classify_shelf_subclass(front_score: float, fold_score: float, src_score: float, interface_fraction: float) -> str:
    if interface_fraction < 0.25 and front_score < 0.25:
        return "shelf_transient"
    if front_score >= 0.6 and fold_score < 0.35:
        return "shelf_persistent_interface"
    if fold_score >= 0.35 and fold_score < 0.6 and src_score < 0.45:
        return "shelf_folded_nonbox"
    if fold_score >= 0.6 and src_score < 0.55:
        return "shelf_prebox"
    if fold_score >= 0.6 and src_score >= 0.55:
        return "shelf_closure_approach"
    if front_score < 0.2 and fold_score < 0.2:
        return "shelf_rigid_trivial"
    return "shelf_unresolved"


def python_fallback(input_root: Path, output_prefix: Path) -> None:
    runs: Dict[str, RunState] = {}
    manifests = collect_run_manifest(input_root)

    for path in input_root.rglob("final_summary.csv"):
        for row in read_csv_rows(path):
            state = runs.setdefault(row["run_id"], RunState(run_id=row["run_id"]))
            state.sim_id = row.get("sim_id", state.sim_id)
            state.batch_id = row.get("batch_id", state.batch_id or path.parent.name)
            state.run_date = row.get("run_date", state.run_date)
            state.phase_expression = row.get("phase_expression", state.phase_expression)
            state.kappa = parse_float_value(row.get("kappa"))
            state.lam = parse_float_value(row.get("lambda"), row.get("lam"))
            state.final_exclusion_fraction = parse_float_value(
                row.get("exclusion_fraction"),
                row.get("final_exclusion_fraction"),
            )
            state.final_mean_rho = parse_float_value(
                row.get("rho_mean"),
                row.get("final_mean_rho"),
            )
            state.final_interface_count = float(row["final_interface_count"])
            state.collapse_time = row.get("collapse_time", "")
            state.seed_unanimity = row.get("seed_unanimity", "")
            state.has_summary = True

    for path in input_root.rglob("timeseries_global.csv"):
        for row in read_csv_rows(path):
            state = runs.get(row["run_id"])
            if state is None:
                continue
            time = float(row["time"])
            interface_count = float(row["interface_count"])
            sharpness = float(row["max_sharpness"])
            state.final_time = max(state.final_time, time)
            state.max_observed_sharpness = max(state.max_observed_sharpness, sharpness)
            if state.interface_loss_time is None and interface_count < 0.5:
                state.interface_loss_time = time

    for path in input_root.rglob("domain_metrics.csv"):
        for row in read_csv_rows(path):
            state = runs.get(row["run_id"])
            if state is None:
                continue
            time = float(row["time"])
            if not hasattr(state, "_last_domain_time") or time >= getattr(state, "_last_domain_time"):
                setattr(state, "_last_domain_time", time)
                state.final_active_fraction = float(row["active_fraction"])
                state.final_excluded_active_fraction = float(row["excluded_active_fraction"])

    enrich_runs_with_manifest(runs, manifests)

    run_output = output_prefix.parent / f"{output_prefix.stem}_run_summary.csv"
    parameter_output = output_prefix.parent / f"{output_prefix.stem}_parameter_summary.csv"

    run_rows = []
    for run_id, state in sorted(runs.items(), key=lambda item: (item[1].kappa, item[1].lam, item[0])):
        if not state.has_summary:
            continue
        coarse_status, deep_status = analysis_status(state)
        run_rows.append(
            {
                "run_id": run_id,
                "sim_id": state.sim_id,
                "batch_id": state.batch_id or state.source_batch,
                "run_date": state.run_date,
                "phase_expression": state.phase_expression,
                "source_batch": state.source_batch,
                "source_root": state.source_root,
                "seed": state.seed,
                "ic_type": state.ic_type,
                "IC_type": state.ic_type,
                "kappa": state.kappa,
                "lam": state.lam,
                "lambda": state.lam,
                "exclusion_rate_k": state.lam,
                "topology_writing_rate_kappa": state.kappa,
                "topology_persistence_lambda": state.lam,
                "inscription_dominance_Pi": state.kappa / state.lam if abs(state.lam) > 1.0e-12 else 0.0,
                "regime_class": classify(state),
                "coarse_metrics_status": coarse_status,
                "deep_metrics_status": deep_status,
                "final_exclusion_fraction": state.final_exclusion_fraction,
                "exclusion_fraction": state.final_exclusion_fraction,
                "final_mean_rho": state.final_mean_rho,
                "rho_mean": state.final_mean_rho,
                "final_interface_count": state.final_interface_count,
                "final_time": state.final_time,
                "collapse_time": state.collapse_time,
                "seed_unanimity": state.seed_unanimity,
                "interface_loss_time": "" if state.interface_loss_time is None else state.interface_loss_time,
                "final_active_fraction": "" if state.final_active_fraction is None else state.final_active_fraction,
                "final_excluded_active_fraction": (
                    "" if state.final_excluded_active_fraction is None else state.final_excluded_active_fraction
                ),
                "max_observed_sharpness": state.max_observed_sharpness,
            }
        )
    write_csv_rows(
        run_output,
        [
            "run_id",
            "sim_id",
            "batch_id",
            "run_date",
            "phase_expression",
            "source_batch",
            "source_root",
            "seed",
            "ic_type",
            "IC_type",
            "kappa",
            "lam",
            "lambda",
            "exclusion_rate_k",
            "topology_writing_rate_kappa",
            "topology_persistence_lambda",
            "inscription_dominance_Pi",
            "regime_class",
            "coarse_metrics_status",
            "deep_metrics_status",
            "final_exclusion_fraction",
            "exclusion_fraction",
            "final_mean_rho",
            "rho_mean",
            "final_interface_count",
            "final_time",
            "collapse_time",
            "seed_unanimity",
            "interface_loss_time",
            "final_active_fraction",
            "final_excluded_active_fraction",
            "max_observed_sharpness",
        ],
        run_rows,
    )

    grouped: dict[tuple[float, float], list[RunState]] = defaultdict(list)
    for state in runs.values():
        if state.has_summary:
            grouped[(state.kappa, state.lam)].append(state)

    parameter_rows = []
    for (kappa, lam), states in sorted(grouped.items()):
        counts = defaultdict(int)
        for state in states:
            counts[classify(state)] += 1
        total = len(states)
        dominant = max(("runaway", "SS3", "SS2", "other"), key=lambda name: counts[name])
        unanimous = counts[dominant] == total

        interface_losses = [state.interface_loss_time for state in states if state.interface_loss_time is not None]
        active_values = [state.final_active_fraction for state in states if state.final_active_fraction is not None]
        excluded_values = [
            state.final_excluded_active_fraction
            for state in states
            if state.final_excluded_active_fraction is not None
        ]

        parameter_rows.append(
            {
                "sim_id": states[0].sim_id,
                "batch_id": states[0].batch_id or states[0].source_batch,
                "run_date": states[0].run_date,
                "phase_expression": states[0].phase_expression,
                "kappa": kappa,
                "lam": lam,
                "lambda": lam,
                "exclusion_rate_k": lam,
                "topology_writing_rate_kappa": kappa,
                "topology_persistence_lambda": lam,
                "inscription_dominance_Pi": kappa / lam if abs(lam) > 1.0e-12 else 0.0,
                "total_runs": total,
                "runaway_count": counts["runaway"],
                "ss3_count": counts["SS3"],
                "ss2_count": counts["SS2"],
                "other_count": counts["other"],
                "dominant_regime": dominant,
                "unanimous": str(unanimous).lower(),
                "seed_unanimity": str(unanimous).lower(),
                "coarse_metrics_status": "ok",
                "deep_metrics_status": "ok" if active_values else "missing_required_inputs",
                "mean_final_exclusion_fraction": sum(s.final_exclusion_fraction for s in states) / total,
                "mean_final_mean_rho": sum(s.final_mean_rho for s in states) / total,
                "mean_final_interface_count": sum(s.final_interface_count for s in states) / total,
                "mean_interface_loss_time": "" if not interface_losses else sum(interface_losses) / len(interface_losses),
                "mean_final_active_fraction": "" if not active_values else sum(active_values) / len(active_values),
                "mean_final_excluded_active_fraction": (
                    "" if not excluded_values else sum(excluded_values) / len(excluded_values)
                ),
                "max_observed_sharpness": max(s.max_observed_sharpness for s in states),
            }
        )
    write_csv_rows(
        parameter_output,
        [
            "sim_id",
            "batch_id",
            "run_date",
            "phase_expression",
            "kappa",
            "lam",
            "lambda",
            "exclusion_rate_k",
            "topology_writing_rate_kappa",
            "topology_persistence_lambda",
            "inscription_dominance_Pi",
            "total_runs",
            "runaway_count",
            "ss3_count",
            "ss2_count",
            "other_count",
            "dominant_regime",
            "unanimous",
            "seed_unanimity",
            "coarse_metrics_status",
            "deep_metrics_status",
            "mean_final_exclusion_fraction",
            "mean_final_mean_rho",
            "mean_final_interface_count",
            "mean_interface_loss_time",
            "mean_final_active_fraction",
            "mean_final_excluded_active_fraction",
            "max_observed_sharpness",
        ],
        parameter_rows,
    )


def load_csv(path: Path) -> list[dict[str, str]]:
    return list(read_csv_rows(path))


def load_runs_from_run_summary(input_root: Path, output_prefix: Path) -> Dict[str, RunState]:
    run_path = output_prefix.parent / f"{output_prefix.stem}_run_summary.csv"
    manifests = collect_run_manifest(input_root)
    runs: Dict[str, RunState] = {}
    for row in load_csv(run_path):
        state = RunState(
            run_id=row["run_id"],
            sim_id=row.get("sim_id", ""),
            batch_id=row.get("batch_id", ""),
            run_date=row.get("run_date", ""),
            phase_expression=row.get("phase_expression", ""),
            kappa=parse_float_value(row.get("kappa")),
            lam=parse_float_value(row.get("lambda"), row.get("lam")),
            seed=row.get("seed", ""),
            ic_type=row.get("ic_type", ""),
            source_batch=row.get("source_batch", ""),
            source_root=row.get("source_root", ""),
            final_exclusion_fraction=parse_float_value(
                row.get("exclusion_fraction"),
                row.get("final_exclusion_fraction"),
            ),
            final_mean_rho=parse_float_value(
                row.get("rho_mean"),
                row.get("final_mean_rho"),
            ),
            final_interface_count=float(row["final_interface_count"]),
            final_time=float(row["final_time"] or 0.0),
            collapse_time=row.get("collapse_time", ""),
            seed_unanimity=row.get("seed_unanimity", ""),
            interface_loss_time=None if row["interface_loss_time"] == "" else float(row["interface_loss_time"]),
            final_active_fraction=None if row["final_active_fraction"] == "" else float(row["final_active_fraction"]),
            final_excluded_active_fraction=None if row["final_excluded_active_fraction"] == "" else float(row["final_excluded_active_fraction"]),
            max_observed_sharpness=float(row["max_observed_sharpness"] or 0.0),
            has_summary=True,
        )
        runs[state.run_id] = state
    enrich_runs_with_manifest(runs, manifests)
    return runs


def build_shelf_outputs(output_prefix: Path) -> None:
    parameter_path = output_prefix.parent / f"{output_prefix.stem}_parameter_summary.csv"
    run_path = output_prefix.parent / f"{output_prefix.stem}_run_summary.csv"
    parameter_rows = load_csv(parameter_path)
    run_rows = load_csv(run_path)
    manifests = collect_run_manifest(output_prefix.parent.parent / "outputs_batches") if "outputs_consolidated" in str(output_prefix.parent) else {}

    grouped_runs: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in run_rows:
        if "source_batch" not in row or not row.get("source_batch"):
            manifest = manifests.get(row["run_id"], {})
            if manifest:
                row["source_batch"] = manifest.get("source_batch", "")
                row["source_root"] = manifest.get("source_root", "")
                row["seed"] = manifest.get("seed", "")
                row["ic_type"] = manifest.get("ic_type", "")
        grouped_runs[(row["kappa"], row["lam"])].append(row)

    by_kappa: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in parameter_rows:
        by_kappa[float(row["kappa"])].append(row)

    shelf_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []

    for kappa, rows in sorted(by_kappa.items()):
        rows.sort(key=lambda row: float(row["lam"]))
        intervals: list[tuple[int, int]] = []
        start = None
        for idx, row in enumerate(rows):
            if row["dominant_regime"] == "other":
                if start is None:
                    start = idx
            elif start is not None:
                intervals.append((start, idx - 1))
                start = None
        if start is not None:
            intervals.append((start, len(rows) - 1))

        for interval_id, (lo, hi) in enumerate(intervals, start=1):
            interval = rows[lo : hi + 1]
            start_lam = float(interval[0]["lam"])
            end_lam = float(interval[-1]["lam"])
            lower_regime = rows[lo - 1]["dominant_regime"] if lo > 0 else ""
            upper_regime = rows[hi + 1]["dominant_regime"] if hi + 1 < len(rows) else ""
            unanimous = all(row["unanimous"] == "true" for row in interval)
            interval_name = f"kappa_{kappa:.6f}_shelf_{interval_id}"
            shelf_rows.append(
                {
                    "kappa": kappa,
                    "side": "lower" if lower_regime == "runaway" else "upper" if upper_regime == "SS2" else "internal",
                    "shelf_interval_id": interval_name,
                    "shelf_start_lam": start_lam,
                    "shelf_end_lam": end_lam,
                    "shelf_width": end_lam - start_lam,
                    "adjacent_lower_regime": lower_regime,
                    "adjacent_upper_regime": upper_regime,
                    "unanimous": str(unanimous).lower(),
                }
            )

            center_index = (lo + hi) // 2
            candidate_specs: list[tuple[str, int]] = [
                ("shelf_lower_edge", lo),
                ("shelf_upper_edge", hi),
                ("shelf_center", center_index),
            ]
            if lo > 0:
                candidate_specs.append(("outer_regime_adjacent", lo - 1))
                if rows[lo - 1]["dominant_regime"] == "SS3" and lo - 2 >= 0:
                    candidate_specs.append(("ss3_adjacent_interior", lo - 1))
            if hi + 1 < len(rows):
                candidate_specs.append(("outer_regime_adjacent", hi + 1))
                if rows[hi + 1]["dominant_regime"] == "SS3":
                    candidate_specs.append(("ss3_adjacent_interior", hi + 1))

            for candidate_type, index in candidate_specs:
                param_row = rows[index]
                key = (param_row["kappa"], param_row["lam"])
                supporting_runs = grouped_runs.get(key, [])
                priority = 100
                if candidate_type == "shelf_center":
                    priority = 10
                elif "edge" in candidate_type:
                    priority = 20
                elif candidate_type == "ss3_adjacent_interior":
                    priority = 30
                elif candidate_type == "outer_regime_adjacent":
                    priority = 40

                if param_row["dominant_regime"] == "SS2":
                    base_type = "control_ss2"
                elif param_row["dominant_regime"] == "runaway":
                    base_type = "control_runaway"
                else:
                    base_type = candidate_type

                if not supporting_runs:
                    candidate_rows.append(
                        {
                            "run_id": "",
                            "batch": "",
                            "seed": "",
                            "kappa": param_row["kappa"],
                            "lambda": param_row["lam"],
                            "dominant_regime": param_row["dominant_regime"],
                            "unanimity": param_row["unanimous"],
                            "candidate_type": base_type,
                            "shelf_interval_id": interval_name,
                            "adjacent_lower_regime": lower_regime,
                            "adjacent_upper_regime": upper_regime,
                            "priority_score": priority,
                        }
                    )
                else:
                    for run in supporting_runs:
                        candidate_rows.append(
                            {
                                "run_id": run["run_id"],
                                "batch": run.get("source_batch", ""),
                                "seed": run.get("seed", ""),
                                "kappa": param_row["kappa"],
                                "lambda": param_row["lam"],
                                "dominant_regime": param_row["dominant_regime"],
                                "unanimity": param_row["unanimous"],
                                "candidate_type": base_type,
                                "shelf_interval_id": interval_name,
                                "adjacent_lower_regime": lower_regime,
                                "adjacent_upper_regime": upper_regime,
                                "priority_score": priority,
                            }
                        )

    write_csv_rows(
        output_prefix.parent / f"{output_prefix.stem}_shelf_interval_summary.csv",
        [
            "kappa",
            "side",
            "shelf_interval_id",
            "shelf_start_lam",
            "shelf_end_lam",
            "shelf_width",
            "adjacent_lower_regime",
            "adjacent_upper_regime",
            "unanimous",
        ],
        shelf_rows,
    )
    write_csv_rows(
        output_prefix.parent / f"{output_prefix.stem}_candidate_manifest.csv",
        [
            "run_id",
            "batch",
            "seed",
            "kappa",
            "lambda",
            "dominant_regime",
            "unanimity",
            "candidate_type",
            "shelf_interval_id",
            "adjacent_lower_regime",
            "adjacent_upper_regime",
            "priority_score",
        ],
        candidate_rows,
    )


def build_deep_outputs(input_root: Path, output_prefix: Path, runs: Dict[str, RunState]) -> None:
    front_frames = collect_front_frames(input_root)
    profile_frames = collect_profile_frames(input_root)

    deep_run_rows: list[dict[str, object]] = []
    grouped_runs: dict[tuple[float, float], list[dict[str, object]]] = defaultdict(list)

    for run_id, state in sorted(runs.items(), key=lambda item: (item[1].kappa, item[1].lam, item[0])):
        if not state.has_summary:
            continue

        cutoff = final_window_cutoff(state)
        run_fronts = [frame for frame in front_frames.get(run_id, []) if frame.time >= cutoff]
        run_profiles = [frame for frame in profile_frames.get(run_id, []) if frame.time >= cutoff]
        run_profiles.sort(key=lambda frame: frame.time)

        has_front = bool(run_fronts)
        has_profiles = bool(run_profiles)
        deep_status = "ok" if has_front and has_profiles else "missing_required_inputs"

        grouped_fronts = group_fronts_by_time(run_fronts)
        front_counts = [float(len(frames)) for _, frames in sorted(grouped_fronts.items())]
        mean_positions = [mean([frame.position for frame in frames]) for _, frames in sorted(grouped_fronts.items())]
        mean_velocities = [mean([frame.velocity for frame in frames]) for _, frames in sorted(grouped_fronts.items())]
        widths = [mean([frame.width for frame in frames]) for _, frames in sorted(grouped_fronts.items())]

        front_count_final = mean(front_counts)
        front_count_var = variance(front_counts)
        position_drift = abs(mean_positions[-1] - mean_positions[0]) if len(mean_positions) >= 2 else 0.0
        speed_drift = abs(mean_velocities[-1] - mean_velocities[0]) if len(mean_velocities) >= 2 else 0.0
        interface_lifetime_fraction = (
            1.0 if state.interface_loss_time is None or state.final_time == 0.0 else state.interface_loss_time / state.final_time
        )
        front_persistence_score = max(
            0.0,
            min(
                1.0,
                0.5 * interface_lifetime_fraction
                + 0.3 * (1.0 / (1.0 + front_count_var))
                + 0.2 * (1.0 / (1.0 + speed_drift)),
            ),
        )

        profile_depth_values = [profile_depth(frame) for frame in run_profiles]
        wall_strength_values = [wall_strength(frame) for frame in run_profiles]
        curvature_values = [curvature_proxy(frame) for frame in run_profiles]
        width_values = [profile_width(frame) for frame in run_profiles]
        peak_values = [float(peak_count(frame)) for frame in run_profiles]

        profile_depth_final = profile_depth_values[-1] if profile_depth_values else 0.0
        profile_wall_strength_final = wall_strength_values[-1] if wall_strength_values else 0.0
        profile_curvature_final = curvature_values[-1] if curvature_values else 0.0
        profile_shape_persistence = profile_similarity(run_profiles) if run_profiles else 0.0
        profile_width_stability = 1.0 / (1.0 + variance(width_values)) if width_values else 0.0
        profile_peak_stability = 1.0 / (1.0 + variance(peak_values)) if peak_values else 0.0

        p_depth = profile_depth_final / (1.0 + profile_depth_final)
        p_wall = profile_wall_strength_final / (1.0 + profile_wall_strength_final)
        p_shape = profile_shape_persistence
        p_front = front_persistence_score
        p_omega = p_depth * p_wall * p_shape * p_front
        fold_score_tilde = mean([p_depth, p_wall, profile_curvature_final / (1.0 + profile_curvature_final), p_omega])

        l_proxy = interface_lifetime_fraction
        dsr_proxy = state.final_mean_rho / max(state.final_exclusion_fraction + 1.0e-12, 1.0e-12)
        src_proxy_score = mean([l_proxy, p_omega, fold_score_tilde])

        shelf_subclass = "shelf_unresolved"
        if classify(state) == "other":
            shelf_subclass = classify_shelf_subclass(front_persistence_score, fold_score_tilde, src_proxy_score, interface_lifetime_fraction)

        deep_row = {
            "run_id": run_id,
            "source_batch": state.source_batch,
            "seed": state.seed,
            "ic_type": state.ic_type,
            "kappa": state.kappa,
            "lam": state.lam,
            "regime_class": classify(state),
            "deep_metrics_status": deep_status,
            "front_count_final": front_count_final if has_front else "",
            "front_count_var_final_window": front_count_var if has_front else "",
            "front_position_drift_final_window": position_drift if has_front else "",
            "front_speed_drift_final_window": speed_drift if has_front else "",
            "interface_lifetime_fraction": interface_lifetime_fraction,
            "front_persistence_score": front_persistence_score if has_front else "",
            "profile_depth_final": profile_depth_final if has_profiles else "",
            "profile_wall_strength_final": profile_wall_strength_final if has_profiles else "",
            "profile_curvature_final": profile_curvature_final if has_profiles else "",
            "profile_shape_persistence": profile_shape_persistence if has_profiles else "",
            "profile_width_stability": profile_width_stability if has_profiles else "",
            "profile_peak_stability": profile_peak_stability if has_profiles else "",
            "P_depth": p_depth if has_profiles else "",
            "P_wall": p_wall if has_profiles else "",
            "P_shape": p_shape if has_profiles else "",
            "P_front": p_front if has_front else "",
            "P_Omega": p_omega if has_front and has_profiles else "",
            "fold_score_tilde": fold_score_tilde if has_profiles else "",
            "L_proxy": l_proxy if has_front else "",
            "Dsr_proxy": dsr_proxy,
            "SRC_proxy_score": src_proxy_score if has_front and has_profiles else "",
            "shelf_subclass": shelf_subclass if deep_status == "ok" else "shelf_unresolved",
        }
        deep_run_rows.append(deep_row)
        grouped_runs[(state.kappa, state.lam)].append(deep_row)

    deep_run_path = output_prefix.parent / f"{output_prefix.stem}_deep_run_summary.csv"
    deep_parameter_path = output_prefix.parent / f"{output_prefix.stem}_deep_parameter_summary.csv"
    shelf_subclass_path = output_prefix.parent / f"{output_prefix.stem}_shelf_subclass_summary.csv"
    box_src_path = output_prefix.parent / f"{output_prefix.stem}_box_src_screening.csv"

    deep_fields = list(deep_run_rows[0].keys()) if deep_run_rows else [
        "run_id", "source_batch", "seed", "ic_type", "kappa", "lam", "regime_class", "deep_metrics_status"
    ]
    write_csv_rows(deep_run_path, deep_fields, deep_run_rows)

    deep_parameter_rows: list[dict[str, object]] = []
    subclass_rows: list[dict[str, object]] = []
    screening_rows: list[dict[str, object]] = []
    for (kappa, lam), rows in sorted(grouped_runs.items()):
        valid = [row for row in rows if row["deep_metrics_status"] == "ok"]
        subclass_counts: dict[str, int] = defaultdict(int)
        for row in valid:
            subclass_counts[str(row["shelf_subclass"])] += 1
        dominant_subclass = max(subclass_counts, key=subclass_counts.get) if subclass_counts else "shelf_unresolved"

        def avg(field: str) -> object:
            values = [float(row[field]) for row in valid if row[field] != ""]
            return "" if not values else mean(values)

        deep_parameter_rows.append(
            {
                "kappa": kappa,
                "lam": lam,
                "run_count": len(rows),
                "deep_valid_run_count": len(valid),
                "deep_metrics_status": "ok" if len(valid) == len(rows) and rows else "missing_required_inputs",
                "mean_front_persistence_score": avg("front_persistence_score"),
                "mean_profile_shape_persistence": avg("profile_shape_persistence"),
                "mean_fold_score_tilde": avg("fold_score_tilde"),
                "mean_P_Omega": avg("P_Omega"),
                "mean_L_proxy": avg("L_proxy"),
                "mean_Dsr_proxy": avg("Dsr_proxy"),
                "mean_SRC_proxy_score": avg("SRC_proxy_score"),
                "dominant_shelf_subclass": dominant_subclass,
            }
        )
        if valid:
            subclass_rows.append(
                {
                    "kappa": kappa,
                    "lam": lam,
                    "dominant_shelf_subclass": dominant_subclass,
                    "subclass_count": subclass_counts[dominant_subclass],
                    "deep_valid_run_count": len(valid),
                }
            )
            screening_rows.append(
                {
                    "kappa": kappa,
                    "lam": lam,
                    "deep_metrics_status": "ok",
                    "fold_score_tilde_mean": avg("fold_score_tilde"),
                    "L_proxy_mean": avg("L_proxy"),
                    "Dsr_proxy_mean": avg("Dsr_proxy"),
                    "SRC_proxy_score_mean": avg("SRC_proxy_score"),
                    "box_screen_flag": str((avg("fold_score_tilde") or 0) >= 0.6).lower() if avg("fold_score_tilde") != "" else "false",
                    "src_screen_flag": str((avg("SRC_proxy_score") or 0) >= 0.55).lower() if avg("SRC_proxy_score") != "" else "false",
                }
            )
        else:
            screening_rows.append(
                {
                    "kappa": kappa,
                    "lam": lam,
                    "deep_metrics_status": "missing_required_inputs",
                    "fold_score_tilde_mean": "",
                    "L_proxy_mean": "",
                    "Dsr_proxy_mean": "",
                    "SRC_proxy_score_mean": "",
                    "box_screen_flag": "false",
                    "src_screen_flag": "false",
                }
            )

    write_csv_rows(
        deep_parameter_path,
        [
            "kappa",
            "lam",
            "run_count",
            "deep_valid_run_count",
            "deep_metrics_status",
            "mean_front_persistence_score",
            "mean_profile_shape_persistence",
            "mean_fold_score_tilde",
            "mean_P_Omega",
            "mean_L_proxy",
            "mean_Dsr_proxy",
            "mean_SRC_proxy_score",
            "dominant_shelf_subclass",
        ],
        deep_parameter_rows,
    )
    write_csv_rows(
        shelf_subclass_path,
        ["kappa", "lam", "dominant_shelf_subclass", "subclass_count", "deep_valid_run_count"],
        subclass_rows,
    )
    write_csv_rows(
        box_src_path,
        [
            "kappa",
            "lam",
            "deep_metrics_status",
            "fold_score_tilde_mean",
            "L_proxy_mean",
            "Dsr_proxy_mean",
            "SRC_proxy_score_mean",
            "box_screen_flag",
            "src_screen_flag",
        ],
        screening_rows,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Level 2 result batches with native-first execution.")
    parser.add_argument("--input-root", required=True, help="Root directory to scan, e.g. outputs_batches.")
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output prefix path. The script writes *_run_summary.csv and *_parameter_summary.csv.",
    )
    parser.add_argument("--native-exe", help="Optional explicit path to level2_results_analyzer executable.")
    parser.add_argument(
        "--force-python",
        action="store_true",
        help="Bypass the native executable and run the Python fallback.",
    )
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Only scan batch readiness and emit deep-readiness / rerun-priority reports.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_root).resolve()
    output_prefix = Path(args.output_prefix).resolve()
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    if args.inventory_only:
        build_inventory_outputs(input_root, output_prefix)
        print("Inventory analysis completed.")
        return

    if not args.force_python:
        native_exe = find_native_executable(args.native_exe)
        if native_exe is not None:
            rc = run_native(native_exe, input_root, output_prefix)
            if rc == 0:
                build_shelf_outputs(output_prefix)
                build_deep_outputs(input_root, output_prefix, load_runs_from_run_summary(input_root, output_prefix))
                print(f"Native analysis completed with {native_exe}")
                return
            print(f"Native analyzer failed with exit code {rc}; falling back to Python.", file=sys.stderr)

    python_fallback(input_root, output_prefix)
    build_shelf_outputs(output_prefix)
    build_deep_outputs(input_root, output_prefix, load_runs_from_run_summary(input_root, output_prefix))
    print("Python fallback analysis completed.")


if __name__ == "__main__":
    main()
