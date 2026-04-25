from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
CALIBRATION_PATH = ROOT / "configs" / "sim18_v3" / "delta_sigma_calibration_v1.json"


@dataclass(frozen=True)
class DeltaSigmaCalibration:
    family: str
    alpha: float
    beta: float
    identifiable: bool
    scope: str
    source: str
    status: str


def load_delta_sigma_calibration_table() -> Dict[str, Any]:
    with CALIBRATION_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def infer_delta_family(spec: Dict[str, object]) -> str | None:
    explicit = str(spec.get("delta_family", "")).strip()
    if explicit:
        return explicit

    for field in ("spot_verification_point", "label", "source_reference"):
        text = str(spec.get(field, "")).lower()
        if "ss2" in text:
            return "SS2"
        if "ss3" in text:
            return "SS3"
        if "r2" in text:
            return "R2"
        if "shelf" in text:
            return "Shelf"
    return None


def resolve_delta_sigma_calibration(
    spec: Dict[str, object],
    ic_type: str,
) -> DeltaSigmaCalibration:
    explicit_alpha = spec.get("delta_alpha")
    explicit_beta = spec.get("delta_beta")
    if explicit_alpha is not None:
        alpha = float(explicit_alpha)
        beta = alpha if explicit_beta is None else float(explicit_beta)
        explicit_family = str(spec.get("delta_family", "explicit")).strip() or "explicit"
        return DeltaSigmaCalibration(
            family=explicit_family,
            alpha=alpha,
            beta=beta,
            identifiable=bool(spec.get("delta_alpha_identifiable", True)),
            scope="explicit",
            source=str(spec.get("delta_calibration_source", CALIBRATION_PATH)),
            status="explicit_override",
        )

    family = infer_delta_family(spec)
    if family is None:
        raise ValueError(
            "Could not infer delta_family for Delta-Sigma-rho runtime. "
            "Set spec['delta_family'] explicitly."
        )

    table = load_delta_sigma_calibration_table()
    family_entry = table["families"].get(family)
    if family_entry is None:
        raise ValueError(f"No frozen Delta-Sigma calibration entry for family '{family}'.")

    mode = str(family_entry.get("mode", "family_wide"))
    if mode == "by_ic_type":
        alpha = float(family_entry["alphas"][ic_type])
        scope = "ic_type"
        status = "active"
    else:
        alpha = float(family_entry["alpha"])
        scope = "family_wide"
        status = str(family_entry.get("status", "active"))

    beta_rule = str(family_entry.get("beta_rule", "same_as_alpha"))
    if beta_rule == "same_as_alpha":
        beta = alpha
    else:
        beta = float(family_entry["beta"])

    return DeltaSigmaCalibration(
        family=family,
        alpha=alpha,
        beta=beta,
        identifiable=bool(family_entry.get("identifiable", True)),
        scope=scope,
        source=str(CALIBRATION_PATH),
        status=status,
    )
