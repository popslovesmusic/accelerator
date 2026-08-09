import json
from typing import Dict, Any
from schemas import ClassificationResult

def serialize_result(res: ClassificationResult) -> Dict[str, Any]:
    return {
        "t_sig": {
            "C_count": res.t_sig.C_count,
            "L_depth": res.t_sig.L_depth,
            "R_conn": res.t_sig.R_conn,
            "B_cross": res.t_sig.B_cross,
            "component_count": res.t_sig.component_count,
            "raw_edge_count": res.t_sig.raw_edge_count,
            "unique_edge_count": res.t_sig.unique_edge_count,
            "parallel_edge_count": res.t_sig.parallel_edge_count
        },
        "T_class": res.t_class,
        "is_valid_closure": res.is_valid_closure
    }

def write_decision_audit(res: ClassificationResult, output_path: str) -> None:
    data = serialize_result(res)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
