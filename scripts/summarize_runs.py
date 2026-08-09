from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}

    def key(name: str) -> str:
        return f"{prefix}.{name}" if prefix else name

    if isinstance(obj, dict):
        for k, v in obj.items():
            k_str = str(k)
            if isinstance(v, dict):
                out.update(flatten(v, key(k_str)))
            elif isinstance(v, list):
                out[key(k_str)] = json.dumps(v, ensure_ascii=False)
            else:
                out[key(k_str)] = v
        return out

    out[prefix or "value"] = obj
    return out


def coerce_number(v: Any) -> float | None:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def read_summaries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return []

    if isinstance(payload, list):
        items = payload
    else:
        items = [payload]

    records = []
    for item in items:
        if not isinstance(item, dict):
            continue
        final_metrics = item.get("final_metrics") or item.get("final") or {}
        record: dict[str, Any] = {
            "run_dir": str(path.parent),
            "run_name": path.parent.name,
            "summary_path": str(path),
        }
        record.update(flatten(item.get("config", {}), prefix="config"))
        record.update(flatten(final_metrics, prefix="final"))
        # keep a couple common high-signal top-level keys, if present
        for k in ("status", "total_halted", "first_box_violation", "engine", "exit_code"):
            if k in item:
                val = item[k]
                record[k] = json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val
        records.append(record)
    return records


def find_summaries(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern))


def write_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    if not rows:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = sorted({k for r in rows for k in r.keys()})
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _try_import_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore

        return plt
    except Exception:
        return None


def make_histograms(rows: list[dict[str, Any]], out_dir: Path, max_metrics: int) -> list[str]:
    plt = _try_import_matplotlib()
    if plt is None:
        return []

    out_dir.mkdir(parents=True, exist_ok=True)

    # Pick numeric columns with more than one distinct value
    numeric_cols: dict[str, list[float]] = {}
    for r in rows:
        for k, v in r.items():
            num = coerce_number(v)
            if num is None:
                continue
            numeric_cols.setdefault(k, []).append(num)

    candidates: list[tuple[str, int]] = []
    for k, vals in numeric_cols.items():
        distinct = len(set(vals))
        if distinct > 1:
            candidates.append((k, distinct))

    candidates.sort(key=lambda kv: kv[1], reverse=True)
    written: list[str] = []
    for k, _distinct in candidates[:max_metrics]:
        vals = numeric_cols[k]
        plt.figure(figsize=(8, 4.5))
        plt.hist(vals, bins=min(30, max(5, int(math.sqrt(len(vals))))), alpha=0.85)
        plt.title(k)
        plt.tight_layout()
        out_path = out_dir / f"hist__{k.replace('/', '_').replace(':', '_')}.png"
        plt.savefig(out_path)
        plt.close()
        written.append(str(out_path))
    return written


def make_sweep_plot(
    rows: list[dict[str, Any]],
    out_dir: Path,
    x_key: str,
    y_key: str,
    group_key: str | None,
    title: str | None,
) -> str | None:
    plt = _try_import_matplotlib()
    if plt is None:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)

    points: list[tuple[float, float, str]] = []
    for r in rows:
        x = coerce_number(r.get(x_key))
        y = coerce_number(r.get(y_key))
        if x is None or y is None:
            continue
        g = str(r.get(group_key)) if group_key else "all"
        points.append((x, y, g))

    if not points:
        return None

    groups: dict[str, list[tuple[float, float]]] = {}
    for x, y, g in points:
        groups.setdefault(g, []).append((x, y))

    plt.figure(figsize=(8, 4.5))
    for g, pts in sorted(groups.items(), key=lambda kv: kv[0]):
        pts_sorted = sorted(pts, key=lambda xy: xy[0])
        xs = [p[0] for p in pts_sorted]
        ys = [p[1] for p in pts_sorted]
        plt.plot(xs, ys, marker="o", linewidth=1.5, markersize=4, label=g)

    plt.xlabel(x_key)
    plt.ylabel(y_key)
    plt.title(title or f"{y_key} vs {x_key}")
    if group_key:
        plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    out_path = out_dir / "sweep.png"
    plt.savefig(out_path)
    plt.close()
    return str(out_path)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize runs/**/summary.json into a tidy CSV (+ optional plots).")
    p.add_argument("--root", default=".", help="Root directory to scan (default: current).")
    p.add_argument("--pattern", default="**/summary.json", help="Glob pattern under root (default: **/summary.json).")
    p.add_argument("--out", default=None, help="Output directory (default: <root>/analysis_summaries).")
    p.add_argument("--csv", default=None, help="CSV path (default: <out>/runs_summary.csv).")
    p.add_argument("--plots", action="store_true", help="Generate plots if matplotlib is available.")
    p.add_argument("--max-hists", type=int, default=12, help="Max histogram plots (default: 12).")
    p.add_argument("--sweep-x", default=None, help="X column for sweep plot.")
    p.add_argument("--sweep-y", default=None, help="Y column for sweep plot.")
    p.add_argument("--sweep-group", default=None, help="Optional grouping column for sweep plot.")
    p.add_argument("--sweep-title", default=None, help="Optional title for sweep plot.")
    return p.parse_args(argv)


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve() if args.out else (root / "analysis_summaries").resolve()
    csv_path = Path(args.csv).resolve() if args.csv else (out_dir / "runs_summary.csv").resolve()

    summaries = find_summaries(root, args.pattern)
    if not summaries:
        print(f"No summaries found under {root} with pattern {args.pattern!r}.")
        return

    all_rows = []
    for p in summaries:
        all_rows.extend(read_summaries(p))

    if not all_rows:
        print("No valid run records found.")
        return

    write_csv(all_rows, csv_path)

    if args.plots:
        plots_dir = out_dir / "plots"
        written = make_histograms(all_rows, plots_dir, max_metrics=args.max_hists)
        if args.sweep_x and args.sweep_y:
            make_sweep_plot(
                all_rows,
                plots_dir,
                x_key=args.sweep_x,
                y_key=args.sweep_y,
                group_key=args.sweep_group,
                title=args.sweep_title,
            )
        # Write a minimal manifest
        (plots_dir / "plots.json").write_text(json.dumps({"plots": written}, indent=2), encoding="utf-8")

    print(f"Wrote CSV: {csv_path}")
    if args.plots:
        print(f"Wrote plots: {out_dir / 'plots'}")


if __name__ == "__main__":
    main()

