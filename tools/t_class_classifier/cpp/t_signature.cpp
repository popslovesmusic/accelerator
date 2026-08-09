#include "schemas.hpp"

void compute_graph_metrics(
    const RealizedClosureTrace& trace,
    int& V,
    int& E,
    int& C,
    int& loop_count,
    int& raw_edge_count,
    int& parallel_edge_count
);
int estimate_braid_proxy(const RealizedClosureTrace& trace, int loop_count);

TSig build_t_sig(const RealizedClosureTrace& trace) {
    int V = 0, E = 0, C = 0, loop_count = 0, raw_edge_count = 0, parallel_edge_count = 0;
    compute_graph_metrics(trace, V, E, C, loop_count, raw_edge_count, parallel_edge_count);

    int L_depth = 0;
    if (loop_count == 0) {
        L_depth = 0;
    } else if (loop_count == 1) {
        L_depth = 1;
    } else {
        L_depth = 2;
    }

    double R_conn = 0.0;
    if (V > 0) {
        R_conn = static_cast<double>(E) / static_cast<double>(V);
    }

    int B_cross = estimate_braid_proxy(trace, loop_count);

    TSig sig;
    sig.C_count = loop_count;
    sig.L_depth = L_depth;
    sig.R_conn = R_conn;
    sig.B_cross = B_cross;
    sig.component_count = C;
    sig.raw_edge_count = raw_edge_count;
    sig.unique_edge_count = E;
    sig.parallel_edge_count = parallel_edge_count;
    return sig;
}
