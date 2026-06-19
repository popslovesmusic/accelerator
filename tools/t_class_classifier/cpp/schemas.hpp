#ifndef SCHEMAS_HPP
#define SCHEMAS_HPP

#include <string>
#include <vector>
#include <map>

struct ContinuationStep {
    int stage;
    int from_node;
    int to_node;
};

struct ConnectivityRecord {
    int num_vertices;
    std::vector<std::vector<int>> edges;
};

struct RealizedClosureTrace {
    std::string fixture_id;
    std::string run_id;
    std::vector<ContinuationStep> continuation_trace;
    std::string constraint_context_id;
    std::vector<std::vector<int>> closure_adjacency;
    ConnectivityRecord connectivity_record;
    std::map<std::string, std::string> allowed_metadata;
};

struct TSig {
    int C_count = 0;
    int L_depth = 0;
    double R_conn = 0.0;
    int B_cross = 0;
    int component_count = 0;
    int raw_edge_count = 0;
    int unique_edge_count = 0;
    int parallel_edge_count = 0;
};

struct ClassificationResult {
    TSig t_sig;
    std::string t_class;
    bool is_valid_closure;
};

#endif // SCHEMAS_HPP
