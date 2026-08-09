#include "schemas.hpp"
#include <vector>
#include <set>
#include <algorithm>
#include <cmath>

bool connectivity_edges_are_one_based(const RealizedClosureTrace& trace) {
    if (trace.connectivity_record.num_vertices <= 0 || trace.connectivity_record.edges.empty()) {
        return false;
    }

    bool has_endpoint = false;
    for (const auto& edge : trace.connectivity_record.edges) {
        if (edge.size() < 2) {
            continue;
        }
        has_endpoint = true;
        int u = edge[0];
        int v = edge[1];
        if (u == 0 || v == 0) {
            return false;
        }
        if (u < 1 || u > trace.connectivity_record.num_vertices || v < 1 || v > trace.connectivity_record.num_vertices) {
            return false;
        }
    }
    return has_endpoint;
}

void compute_graph_metrics(
    const RealizedClosureTrace& trace,
    int& V,
    int& E,
    int& C,
    int& loop_count,
    int& raw_edge_count,
    int& parallel_edge_count
) {
    V = 0;
    if (!trace.closure_adjacency.empty()) {
        V = static_cast<int>(trace.closure_adjacency.size());
    } else if (trace.connectivity_record.num_vertices > 0) {
        V = trace.connectivity_record.num_vertices;
    }

    std::vector<std::set<int>> graph(V);
    raw_edge_count = 0;
    parallel_edge_count = 0;

    // Adjacency matrix is authoritative when present.
    if (!trace.closure_adjacency.empty()) {
        for (int i = 0; i < static_cast<int>(trace.closure_adjacency.size()); ++i) {
            for (int j = i + 1; j < static_cast<int>(trace.closure_adjacency[i].size()); ++j) {
                if (trace.closure_adjacency[i][j] != 0) {
                    graph[i].insert(j);
                    graph[j].insert(i);
                    raw_edge_count += 1;
                }
            }
        }
    } else if (trace.connectivity_record.num_vertices > 0 && !trace.connectivity_record.edges.empty()) {
        bool one_based_edges = connectivity_edges_are_one_based(trace);
        std::set<std::pair<int, int>> seen_edges;
        for (const auto& edge : trace.connectivity_record.edges) {
            if (edge.size() >= 2) {
                int u = edge[0];
                int v = edge[1];
                raw_edge_count += 1;

                if (one_based_edges) {
                    u -= 1;
                    v -= 1;
                }
                if (u >= 0 && u < V && v >= 0 && v < V) {
                    auto key = std::minmax(u, v);
                    if (seen_edges.find(key) != seen_edges.end()) {
                        parallel_edge_count += 1;
                    } else {
                        seen_edges.insert(key);
                        if (u != v) {
                            graph[u].insert(v);
                            graph[v].insert(u);
                        }
                    }
                }
            }
        }
    }

    // DFS connected components
    std::vector<bool> visited(V, false);
    C = 0;

    for (int i = 0; i < V; ++i) {
        if (!visited[i]) {
            std::vector<int> stack = {i};
            while (!stack.empty()) {
                int curr = stack.back();
                stack.pop_back();
                if (!visited[curr]) {
                    visited[curr] = true;
                    for (int neighbor : graph[curr]) {
                        if (!visited[neighbor]) {
                            stack.push_back(neighbor);
                        }
                    }
                }
            }
            C += 1;
        }
    }

    // Count unique undirected edges
    E = 0;
    for (int i = 0; i < V; ++i) {
        E += static_cast<int>(graph[i].size());
    }
    E /= 2;

    // Loop count
    if (V > 0) {
        loop_count = E - V + C;
    } else {
        loop_count = 0;
    }
}

int estimate_braid_proxy(const RealizedClosureTrace& trace, int loop_count) {
    if (loop_count <= 1) {
        return 1;
    } else if (loop_count == 2) {
        return 2;
    } else {
        return loop_count;
    }
}
