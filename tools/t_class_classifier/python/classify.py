from schemas import TSig, ClassificationResult

def assign_t_class(t_sig: TSig) -> ClassificationResult:
    C_count = t_sig.C_count
    B_cross = t_sig.B_cross
    component_count = t_sig.component_count
    raw_edge_count = t_sig.raw_edge_count
    unique_edge_count = t_sig.unique_edge_count
    parallel_edge_count = t_sig.parallel_edge_count

    if C_count == 0:
        if unique_edge_count > 0 or raw_edge_count > 0 or parallel_edge_count > 0:
            t_class = "T_x"
            is_valid_closure = True
        else:
            t_class = "T_0"
            is_valid_closure = False
    elif C_count == 1:
        t_class = "T_1"
        is_valid_closure = True
    elif C_count == 2 and (component_count >= 2 or B_cross <= 2):
        t_class = "T_2"
        is_valid_closure = True
    elif C_count >= 3:
        if B_cross <= 3:
            t_class = "T_3"
        else:
            t_class = "T_4"
        is_valid_closure = True
    else:
        t_class = "T_x"
        is_valid_closure = True

    return ClassificationResult(
        t_sig=t_sig,
        t_class=t_class,
        is_valid_closure=is_valid_closure
    )
