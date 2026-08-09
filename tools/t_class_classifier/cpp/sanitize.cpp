#include "json.hpp"
#include <string>
#include <vector>
#include <stdexcept>

using json = nlohmann::json;

const std::vector<std::string> FORBIDDEN_FIELDS = {
    "C_orient", "-(i)", "𝒪", "orientation_regime", "orientation_label", "S_closure"
};

bool find_forbidden_recursive(const json& j) {
    if (j.is_object()) {
        for (auto it = j.begin(); it != j.end(); ++it) {
            for (const auto& forbidden : FORBIDDEN_FIELDS) {
                if (it.key() == forbidden) {
                    return true;
                }
            }
            if (find_forbidden_recursive(it.value())) {
                return true;
            }
        }
    } else if (j.is_array()) {
        for (const auto& item : j) {
            if (find_forbidden_recursive(item)) {
                return true;
            }
        }
    }
    return false;
}

void strip_forbidden_recursive(json& j) {
    if (j.is_object()) {
        std::vector<std::string> keys_to_remove;
        for (auto it = j.begin(); it != j.end(); ++it) {
            for (const auto& forbidden : FORBIDDEN_FIELDS) {
                if (it.key() == forbidden) {
                    keys_to_remove.push_back(it.key());
                }
            }
        }
        for (const auto& k : keys_to_remove) {
            j.erase(k);
        }
        for (auto it = j.begin(); it != j.end(); ++it) {
            strip_forbidden_recursive(it.value());
        }
    } else if (j.is_array()) {
        for (auto& item : j) {
            strip_forbidden_recursive(item);
        }
    }
}

void validate_schema_integrity(const json& j) {
    std::vector<std::string> required = {"continuation_trace", "closure_adjacency", "connectivity_record"};
    for (const auto& req : required) {
        if (!j.contains(req)) {
            throw std::runtime_error("Missing required field in trace JSON: '" + req + "'");
        }
    }
}

void sanitize_and_filter(json& j, const std::string& action) {
    if (find_forbidden_recursive(j)) {
        if (action == "reject") {
            throw std::runtime_error("Forbidden field detected in input trace data: Rejecting execution.");
        } else if (action == "strip") {
            strip_forbidden_recursive(j);
        }
    }
}
