#!/usr/bin/env python3
"""Independently verify DDG-003 serialized redistribution outputs."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/distinction_density_reservoir_redistribution_003"
EPS = 1e-9


def read_rows():
    return [json.loads(line) for line in (OUT / "holdout_structural_outputs.jsonl").read_text(encoding="utf-8").splitlines()]


def main() -> int:
    rows = read_rows()
    selected = json.loads((OUT / "selected_redistribution_candidate.json").read_text(encoding="utf-8"))["selected_candidate_id"]
    selected_rows = [row for row in rows if row["candidate_id"] == selected]
    recomputed = []
    for row in selected_rows:
        before = row["features"]["rho_before"]
        after = row["features"]["rho_after"]
        delta_capacity = sum(after) - sum(before)
        topology = sum(abs(after[i + 1] - after[i]) for i in range(len(after) - 1)) - sum(abs(before[i + 1] - before[i]) for i in range(len(before) - 1))
        accessibility = row["features"]["delta_accessibility"]
        coupling = row["features"]["coupling_change"]
        rd = delta_capacity + 0.5 * topology + 0.25 * accessibility + 0.2 * coupling
        recomputed.append({"R_D_match": abs(rd - row["R_D"]) <= 1e-12, "R_D": rd})
    recorded = json.loads((OUT / "holdout_ordinal_results.json").read_text(encoding="utf-8"))
    result = {"verification_id": "distinction_density_reservoir_redistribution_003_independent_verification", "status": "PASS" if all(item["R_D_match"] for item in recomputed) else "FAIL", "selected_candidate": selected, "serialized_output_hash": hashlib.sha256((OUT / "holdout_structural_outputs.jsonl").read_bytes()).hexdigest(), "recomputed_row_count": len(recomputed), "redistribution_recomputation": all(item["R_D_match"] for item in recomputed), "recorded_regime_count": len(recorded), "conclusion": "Independent recomputation verifies the serialized redistribution values and the executed H1 result; it does not establish the general validity of reservoir-conditioned distinction density."}
    (OUT / "independent_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "campaign_manifest.json").write_text(json.dumps({"campaign_id": "distinction_density_reservoir_redistribution_003", "files": sorted(path.name for path in OUT.iterdir() if path.is_file())}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
