#include "schemas.hpp"
#include "json.hpp"
#include <fstream>
#include <stdexcept>
#include <iostream>

using json = nlohmann::json;

RealizedClosureTrace parse_trace(const json& j) {
    RealizedClosureTrace trace;
    
    if (j.contains("fixture_id") && !j["fixture_id"].is_null()) {
        trace.fixture_id = j["fixture_id"].get<std::string>();
    }
    if (j.contains("run_id") && !j["run_id"].is_null()) {
        trace.run_id = j["run_id"].get<std::string>();
    }
    if (j.contains("constraint_context_id") && !j["constraint_context_id"].is_null()) {
        trace.constraint_context_id = j["constraint_context_id"].get<std::string>();
    }
    
    if (j.contains("continuation_trace") && j["continuation_trace"].is_array()) {
        for (const auto& item : j["continuation_trace"]) {
            ContinuationStep step;
            step.stage = item["stage"].get<int>();
            step.from_node = item["from_node"].get<int>();
            step.to_node = item["to_node"].get<int>();
            trace.continuation_trace.push_back(step);
        }
    }
    
    if (j.contains("closure_adjacency") && j["closure_adjacency"].is_array()) {
        for (const auto& row : j["closure_adjacency"]) {
            std::vector<int> r;
            for (const auto& val : row) {
                r.push_back(val.get<int>());
            }
            trace.closure_adjacency.push_back(r);
        }
    }
    
    if (j.contains("connectivity_record") && !j["connectivity_record"].is_null()) {
        const auto& conn = j["connectivity_record"];
        trace.connectivity_record.num_vertices = conn.value("num_vertices", 0);
        if (conn.contains("edges") && conn["edges"].is_array()) {
            for (const auto& edge : conn["edges"]) {
                std::vector<int> e;
                for (const auto& val : edge) {
                    e.push_back(val.get<int>());
                }
                trace.connectivity_record.edges.push_back(e);
            }
        }
    }
    
    if (j.contains("allowed_metadata") && j["allowed_metadata"].is_object()) {
        for (auto it = j["allowed_metadata"].begin(); it != j["allowed_metadata"].end(); ++it) {
            if (it.value().is_string()) {
                trace.allowed_metadata[it.key()] = it.value().get<std::string>();
            }
        }
    }
    
    return trace;
}
