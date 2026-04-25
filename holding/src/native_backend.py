from __future__ import annotations

from dataclasses import asdict
from typing import Dict

import numpy as np

try:
    from . import _level2_native as _native  # type: ignore[attr-defined]
except ImportError:
    try:
        import _level2_native as _native  # type: ignore[no-redef]
    except ImportError:
        _native = None


def is_native_backend_available() -> bool:
    return _native is not None


def native_backend_name() -> str | None:
    if _native is None:
        return None
    return "_level2_native"


def native_backend_max_threads() -> int | None:
    if _native is None:
        return None
    return int(_native.get_max_threads())


def set_native_backend_threads(num_threads: int) -> None:
    if _native is None:
        raise RuntimeError("Native Level 2 backend is not available.")
    _native.set_num_threads(int(num_threads))


def simulate_native(
    params: object,
    grid: object,
    initial_state: Dict[str, np.ndarray],
    blowup_threshold: float,
    phase_expression: str = "standard",
) -> Dict[str, object]:
    if _native is None:
        raise RuntimeError("Native Level 2 backend is not available.")

    result = _native.simulate_pde(
        asdict(params),
        asdict(grid),
        {
            "epsilon": np.asarray(initial_state["epsilon"], dtype=float),
            "rho": np.asarray(initial_state["rho"], dtype=float),
            "residue": np.asarray(initial_state["residue"], dtype=float),
        },
        float(blowup_threshold),
        str(phase_expression),
    )
    return {
        "x": np.asarray(result["x"], dtype=float),
        "times": list(result["times"]),
        "snapshots": [
            {
                **{
                    "epsilon": np.asarray(snapshot["epsilon"], dtype=float),
                    "rho": np.asarray(snapshot["rho"], dtype=float),
                    "residue": np.asarray(snapshot["residue"], dtype=float),
                },
                **(
                    {"delta": np.asarray(snapshot["delta"], dtype=float)}
                    if "delta" in snapshot
                    else {}
                ),
                **(
                    {"sigma": np.asarray(snapshot["sigma"], dtype=float)}
                    if "sigma" in snapshot
                    else {}
                ),
            }
            for snapshot in result["snapshots"]
        ],
        "blew_up": bool(result["blew_up"]),
        "negative_undershoot_steps_detected": int(result["negative_undershoot_steps_detected"]),
        "negative_undershoot_events": int(result["negative_undershoot_events"]),
        "nonnegativity_violations": int(result["nonnegativity_violations"]),
        "engine_name": str(result.get("engine_name", "level2_pde_cpp")),
    }


def compute_snapshot_metrics_native(
    x: np.ndarray,
    time: float,
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
) -> tuple[Dict[str, float], list[Dict[str, float]], Dict[str, np.ndarray]]:
    if _native is None:
        raise RuntimeError("Native Level 2 backend is not available.")

    result = _native.compute_snapshot_metrics(
        np.asarray(x, dtype=float),
        float(time),
        np.asarray(epsilon, dtype=float),
        np.asarray(rho, dtype=float),
        np.asarray(residue, dtype=float),
    )
    profile = {
        "x": np.asarray(result["profile"]["x"], dtype=float),
        "eps": np.asarray(result["profile"]["eps"], dtype=float),
        "rho": np.asarray(result["profile"]["rho"], dtype=float),
        "R": np.asarray(result["profile"]["R"], dtype=float),
        "node_ratio": np.asarray(result["profile"]["node_ratio"], dtype=float),
        "sharpness": np.asarray(result["profile"]["sharpness"], dtype=float),
    }
    return dict(result["metrics"]), [dict(front) for front in result["fronts"]], profile
