from typing import List, Dict, Any
from schemas import ClassificationResult

def compute_statistical_aggregates(results: List[ClassificationResult]) -> Dict[str, Any]:
    n = len(results)
    if n == 0:
        return {
            "class_counts": {},
            "class_frequencies": {},
            "mean_C_count": 0.0,
            "mean_R_conn": 0.0,
            "var_R_conn": 0.0
        }

    counts = {"T_0": 0, "T_1": 0, "T_2": 0, "T_3": 0, "T_4": 0, "T_x": 0}
    sum_c = 0
    sum_r = 0.0

    for res in results:
        counts[res.t_class] = counts.get(res.t_class, 0) + 1
        sum_c += res.t_sig.C_count
        sum_r += res.t_sig.R_conn

    mean_c = float(sum_c) / n
    mean_r = sum_r / n

    sum_sq_diff_r = 0.0
    for res in results:
        diff = res.t_sig.R_conn - mean_r
        sum_sq_diff_r += diff * diff
    var_r = sum_sq_diff_r / n if n > 0 else 0.0

    freqs = {k: float(v) / n for k, v in counts.items()}

    return {
        "class_counts": counts,
        "class_frequencies": freqs,
        "mean_C_count": mean_c,
        "mean_R_conn": mean_r,
        "var_R_conn": var_r
    }
