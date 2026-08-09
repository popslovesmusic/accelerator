from __future__ import annotations

import math

from clean_room_oracle import admissible_de, non_collapsed_e, representable_d


ENV = {"low": 0.2, "mid": 0.5, "high": 0.8}


def baseline():
    return {
        "row_id": "baseline-001",
        "relation_type": "SourceRelation",
        "context": "C7",
        "target_context": "C7",
        "source_payload": [10, 20],
        "witness": {"token": [10, 20]},
        "history": [{"step": 0, "state": "S0"}, {"step": 1, "state": "T1"}],
        "target": "T1",
        "profile": "mid",
        "distinction": 0.6,
    }


def test_baseline_is_admissible():
    admitted, detail = admissible_de(baseline(), ENV)
    assert admitted is True
    assert detail["representable_d"] == "REPRESENTABLE"
    assert detail["non_collapsed_e"] == "NON_COLLAPSED"


def test_context_transport_rejected_first():
    row = baseline(); row["target_context"] = "C8"; row["profile"] = "unknown"
    ok, result = representable_d(row, ENV)
    assert ok is False and result == "REJECT_CONTEXT"


def test_strict_threshold_boundary():
    row = baseline(); row["distinction"] = 0.5
    assert non_collapsed_e(row, ENV) == (False, "REJECT_SUBTHRESHOLD")
    row["distinction"] = math.nextafter(0.5, math.inf)
    assert non_collapsed_e(row, ENV) == (True, "NON_COLLAPSED")


def test_unknown_profile_rejected():
    row = baseline(); row["profile"] = "unknown"
    assert representable_d(row, ENV) == (False, "REJECT_PROFILE")
    assert non_collapsed_e(row, ENV) == (False, "REJECT_PROFILE")


def test_history_requires_strict_order_and_terminal():
    row = baseline(); row["history"] = [{"step": 1, "state": "S0"}, {"step": 1, "state": "T1"}]
    assert representable_d(row, ENV) == (False, "REJECT_HISTORY")
    row["history"] = [{"step": 0, "state": "S0"}, {"step": 1, "state": "OTHER"}]
    assert representable_d(row, ENV) == (False, "REJECT_HISTORY")
