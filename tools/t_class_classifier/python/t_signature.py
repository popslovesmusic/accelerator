from schemas import RealizedClosureTrace, TSig
from feature_extract import compute_graph_metrics, estimate_braid_proxy

def build_t_sig(trace: RealizedClosureTrace) -> TSig:
    V, E, C, loop_count, raw_edge_count, parallel_edge_count = compute_graph_metrics(trace)
    
    # Calculate loop nesting depth. 
    if loop_count == 0:
        L_depth = 0
    elif loop_count == 1:
        L_depth = 1
    else:
        L_depth = 2

    # Connectivity persistence R_conn = E / V
    R_conn = float(E) / float(V) if V > 0 else 0.0

    # Braid index proxy
    B_cross = estimate_braid_proxy(trace, loop_count)

    return TSig(
        C_count=loop_count,
        L_depth=L_depth,
        R_conn=R_conn,
        B_cross=B_cross,
        component_count=C,
        raw_edge_count=raw_edge_count,
        unique_edge_count=E,
        parallel_edge_count=parallel_edge_count
    )
