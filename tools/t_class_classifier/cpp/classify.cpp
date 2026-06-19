#include "schemas.hpp"

ClassificationResult assign_t_class(const TSig& sig) {
    ClassificationResult res;
    res.t_sig = sig;

    int C_count = sig.C_count;
    int B_cross = sig.B_cross;
    int component_count = sig.component_count;
    int raw_edge_count = sig.raw_edge_count;
    int unique_edge_count = sig.unique_edge_count;
    int parallel_edge_count = sig.parallel_edge_count;

    if (C_count == 0) {
        if (unique_edge_count > 0 || raw_edge_count > 0 || parallel_edge_count > 0) {
            res.t_class = "T_x";
            res.is_valid_closure = true;
        } else {
            res.t_class = "T_0";
            res.is_valid_closure = false;
        }
    } else if (C_count == 1) {
        res.t_class = "T_1";
        res.is_valid_closure = true;
    } else if (C_count == 2 && (component_count >= 2 || B_cross <= 2)) {
        res.t_class = "T_2";
        res.is_valid_closure = true;
    } else if (C_count >= 3) {
        if (B_cross <= 3) {
            res.t_class = "T_3";
        } else {
            res.t_class = "T_4";
        }
        res.is_valid_closure = true;
    } else {
        res.t_class = "T_x";
        res.is_valid_closure = true;
    }

    return res;
}
