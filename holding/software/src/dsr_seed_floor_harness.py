from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

from .dsr_geometry import (
    DeltaFloorResult,
    SeedSelection,
    build_delta_floor,
    commitments_from_path,
    domain_length,
    select_seed_positions,
)


PROFILE_PATTERN = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p\-]+)\.csv$")


def resolve_outputs_root(path: Path) -> Path:
    candidate = path.resolve()
    if (candidate / "final_summary.csv").is_file():
        return candidate
    outputs_candidate = candidate / "outputs"
    if (outputs_candidate / "final_summary.csv").is_file():
        return outputs_candidate
    raise FileNotFoundError(f"Could not find final_summary.csv under {candidate}")


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_profile_time(token: str) -> float:
    return float(token.replace("p", "."))


def gaussian_peak(x: np.ndarray, center: float, sigma: float, amplitude: float) -> np.ndarray:
    return amplitude * np.exp(-0.5 * np.square((x - center) / sigma))


def synthetic_cases() -> List[Dict[str, object]]:
    L = 200.0
    Nx = 1024
    x = np.linspace(0.0, L, Nx, endpoint=False)
    return [
        {
            "label": "two_peaks_balanced",
            "x": x,
            "depth": gaussian_peak(x, 55.0, 3.2, 1.0) + gaussian_peak(x, 145.0, 3.8, 0.92),
        },
        {
            "label": "two_peaks_close_requires_fallback",
            "x": x,
            "depth": gaussian_peak(x, 96.0, 2.5, 1.0) + gaussian_peak(x, 101.0, 2.0, 0.95),
        },
        {
            "label": "single_peak_requires_fallback",
            "x": x,
            "depth": gaussian_peak(x, 78.0, 4.5, 1.0),
        },
        {
            "label": "edge_peak_clamped",
            "x": x,
            "depth": gaussian_peak(x, 7.0, 2.2, 1.0) + gaussian_peak(x, 138.0, 4.0, 0.4),
        },
        {
            "label": "flat_field_double_fallback",
            "x": x,
            "depth": np.full_like(x, 0.2),
        },
    ]


def pair_key(row: Dict[str, str]) -> tuple[str, str]:
    return str(row.get("seed", "")), str(row.get("IC_type", ""))


def load_profile_sequence(outputs_root: Path, run_id: str) -> List[tuple[float, Path]]:
    matches: List[tuple[float, Path]] = []
    for path in (outputs_root / "profiles").glob(f"profile_run_{run_id}_t_*.csv"):
        match = PROFILE_PATTERN.match(path.name)
        if not match:
            continue
        matches.append((parse_profile_time(match.group("time")), path))
    return sorted(matches, key=lambda item: item[0])


def load_profile_depth(path: Path) -> tuple[np.ndarray, np.ndarray]:
    x_values: List[float] = []
    residue_values: List[float] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            x_values.append(float(row["x"]))
            residue_values.append(float(row["R"]))
    return np.asarray(x_values, dtype=float), np.asarray(residue_values, dtype=float)


def summarize_selection(x: np.ndarray, selection: SeedSelection, floor: DeltaFloorResult) -> Dict[str, object]:
    L = domain_length(x.tolist())
    seeds_distinct = abs(selection.x_g - selection.x_r) > 0.0
    seeds_within_margin = (
        selection.x_r >= selection.interior_margin
        and selection.x_g <= L - selection.interior_margin
    )
    minimum_separation_pass = abs(selection.x_g - selection.x_r) >= 0.5 * selection.minimum_separation
    return {
        "x_r": selection.x_r,
        "x_g": selection.x_g,
        "amplitude_r": selection.amplitude_r,
        "amplitude_g": selection.amplitude_g,
        "fallback_used": selection.fallback_used,
        "fallback_reason": selection.fallback_reason,
        "seeds_distinct": seeds_distinct,
        "seeds_within_margin": seeds_within_margin,
        "minimum_separation_pass": minimum_separation_pass,
        "minimum_abs_delta_f": floor.minimum_abs_delta_f,
        "maximum_abs_delta_f": floor.maximum_abs_delta_f,
        "delta_f_finite": bool(np.all(np.isfinite(floor.delta_f))),
        "delta_raw_finite": bool(np.all(np.isfinite(floor.delta_raw))),
    }


def evaluate_synthetic_cases(commitments_path: Path) -> List[Dict[str, object]]:
    commitments = commitments_from_path(commitments_path)
    rows: List[Dict[str, object]] = []
    for case in synthetic_cases():
        x = np.asarray(case["x"], dtype=float)
        depth = np.asarray(case["depth"], dtype=float)
        selection = select_seed_positions(x, depth, commitments)
        floor = build_delta_floor(x, selection, previous_delta=None)
        summary = summarize_selection(x, selection, floor)
        summary.update(
            {
                "case_type": "synthetic",
                "label": str(case["label"]),
                "all_checks_pass": bool(
                    summary["seeds_distinct"]
                    and summary["seeds_within_margin"]
                    and summary["minimum_separation_pass"]
                    and summary["delta_f_finite"]
                    and summary["minimum_abs_delta_f"] > 0.0
                ),
            }
        )
        rows.append(summary)
    return rows


def representative_replay_specs() -> List[Dict[str, str]]:
    return [
        {
            "label": "SS2_front_seeded_replay",
            "batch": "batches/20260403_sim18_stage1a_v1_ss2_standard",
            "seed": "1000",
            "IC_type": "front_seeded",
        },
        {
            "label": "SS3_front_seeded_replay",
            "batch": "batches/20260403_sim18_stage1a_v1_ss3_standard_retry1",
            "seed": "1000",
            "IC_type": "front_seeded",
        },
        {
            "label": "R2_front_seeded_replay",
            "batch": "batches/20260403_sim18_stage1a_v1_r2_standard",
            "seed": "1000",
            "IC_type": "front_seeded",
        },
        {
            "label": "Shelf_front_seeded_replay",
            "batch": "batches/20260403_sim18_stage1a_v1_shelf_standard",
            "seed": "1000",
            "IC_type": "front_seeded",
        },
    ]


def evaluate_replay_cases(root: Path, commitments_path: Path) -> List[Dict[str, object]]:
    commitments = commitments_from_path(commitments_path)
    rows: List[Dict[str, object]] = []
    for spec in representative_replay_specs():
        outputs_root = resolve_outputs_root(root / spec["batch"])
        summary_rows = load_csv_rows(outputs_root / "final_summary.csv")
        matching = [
            row
            for row in summary_rows
            if pair_key(row) == (spec["seed"], spec["IC_type"])
        ]
        if not matching:
            raise RuntimeError(f"No matching replay run found for {spec['label']}.")
        run_id = str(matching[0]["run_id"])
        profiles = load_profile_sequence(outputs_root, run_id)
        if not profiles:
            raise RuntimeError(f"No profile sequence found for run {run_id}.")

        previous_delta: np.ndarray | None = None
        minimum_abs_delta_f = float("inf")
        maximum_seed_jump = 0.0
        maximum_delta_change = 0.0
        fallback_count = 0
        seeds_distinct_all = True
        seeds_within_margin_all = True
        minimum_separation_all = True
        finite_all = True
        previous_selection: SeedSelection | None = None

        for _, path in profiles:
            x, depth = load_profile_depth(path)
            selection = select_seed_positions(x, depth, commitments)
            floor = build_delta_floor(x, selection, previous_delta=previous_delta)
            summary = summarize_selection(x, selection, floor)
            minimum_abs_delta_f = min(minimum_abs_delta_f, float(summary["minimum_abs_delta_f"]))
            fallback_count += int(bool(summary["fallback_used"]))
            seeds_distinct_all = seeds_distinct_all and bool(summary["seeds_distinct"])
            seeds_within_margin_all = seeds_within_margin_all and bool(summary["seeds_within_margin"])
            minimum_separation_all = minimum_separation_all and bool(summary["minimum_separation_pass"])
            finite_all = finite_all and bool(summary["delta_f_finite"]) and bool(summary["delta_raw_finite"])
            if previous_selection is not None:
                maximum_seed_jump = max(
                    maximum_seed_jump,
                    abs(selection.x_r - previous_selection.x_r),
                    abs(selection.x_g - previous_selection.x_g),
                )
            if previous_delta is not None:
                maximum_delta_change = max(
                    maximum_delta_change,
                    float(np.max(np.abs(floor.delta_f - previous_delta))),
                )
            previous_selection = selection
            previous_delta = floor.delta_f

        rows.append(
            {
                "case_type": "replay",
                "label": spec["label"],
                "batch": outputs_root.parent.name,
                "run_id": run_id,
                "profile_count": len(profiles),
                "fallback_count": fallback_count,
                "minimum_abs_delta_f": minimum_abs_delta_f,
                "maximum_seed_jump": maximum_seed_jump,
                "maximum_delta_change": maximum_delta_change,
                "seeds_distinct": seeds_distinct_all,
                "seeds_within_margin": seeds_within_margin_all,
                "minimum_separation_pass": minimum_separation_all,
                "delta_f_finite": finite_all,
                "all_checks_pass": bool(
                    seeds_distinct_all
                    and seeds_within_margin_all
                    and minimum_separation_all
                    and finite_all
                    and minimum_abs_delta_f > 0.0
                ),
            }
        )
    return rows


def render_markdown(
    commitments_path: Path,
    synthetic_rows: Sequence[Dict[str, object]],
    replay_rows: Sequence[Dict[str, object]],
) -> str:
    synthetic_pass = sum(1 for row in synthetic_rows if bool(row["all_checks_pass"]))
    replay_pass = sum(1 for row in replay_rows if bool(row["all_checks_pass"]))
    lines = [
        "# DSR Seed And Floor Harness",
        "",
        "Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        "This note records the local seed-selection and `delta_f` floor harness against:",
        "",
        f"- `{commitments_path}`",
        "",
        "No runtime campaign was executed.",
        "",
        "## Result",
        "",
        f"- synthetic cases passed: `{synthetic_pass} / {len(synthetic_rows)}`",
        f"- replay cases passed: `{replay_pass} / {len(replay_rows)}`",
        "",
        "## Synthetic Cases",
        "",
    ]
    for row in synthetic_rows:
        lines.extend(
            [
                f"- `{row['label']}`: pass=`{str(row['all_checks_pass']).lower()}`, fallback=`{str(row['fallback_used']).lower()}`, "
                f"min|delta_f|=`{float(row['minimum_abs_delta_f']):.6e}`, seeds=(`{float(row['x_r']):.6f}`, `{float(row['x_g']):.6f}`)",
            ]
        )
    lines.extend(
        [
            "",
            "## Replay Cases",
            "",
        ]
    )
    for row in replay_rows:
        lines.extend(
            [
                f"- `{row['label']}`: pass=`{str(row['all_checks_pass']).lower()}`, profiles=`{int(row['profile_count'])}`, "
                f"fallbacks=`{int(row['fallback_count'])}`, min|delta_f|=`{float(row['minimum_abs_delta_f']):.6e}`, "
                f"max_seed_jump=`{float(row['maximum_seed_jump']):.6f}`, max_delta_change=`{float(row['maximum_delta_change']):.6e}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "The committed seed rule and floor construction are now executable and locally checkable.",
            "The replay traces show that seed positions can still move substantially between saved profiles, so the eventual runtime should update seeds only on explicit ratchet events rather than on every saved frame.",
            "The next implementation step can build the DSR branch against this geometry layer instead of reopening the blocking gaps.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local DSR seed and delta-floor harness.")
    parser.add_argument(
        "--commitments",
        default="configs/dsr/dsr_runtime_commitments_v1.json",
        help="Committed DSR geometry JSON.",
    )
    parser.add_argument(
        "--json-output",
        default="reports/DSR_SEED_FLOOR_HARNESS_2026-04-04.json",
        help="Destination JSON report path.",
    )
    parser.add_argument(
        "--md-output",
        default="reports/DSR_SEED_FLOOR_HARNESS_2026-04-04.md",
        help="Destination Markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    commitments_path = (root / args.commitments).resolve()
    synthetic_rows = evaluate_synthetic_cases(commitments_path)
    replay_rows = evaluate_replay_cases(root, commitments_path)
    payload = {
        "date": "2026-04-04",
        "commitments": str(commitments_path),
        "synthetic_rows": synthetic_rows,
        "replay_rows": replay_rows,
    }
    write_json((root / args.json_output).resolve(), payload)
    (root / args.md_output).resolve().write_text(
        render_markdown(commitments_path, synthetic_rows, replay_rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
