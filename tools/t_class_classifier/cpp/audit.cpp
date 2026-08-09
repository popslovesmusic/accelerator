#include "schemas.hpp"
#include "json.hpp"
#include <fstream>

using json = nlohmann::json;

json serialize_result(const ClassificationResult& res) {
    return {
        {"t_sig", {
            {"C_count", res.t_sig.C_count},
            {"L_depth", res.t_sig.L_depth},
            {"R_conn", res.t_sig.R_conn},
            {"B_cross", res.t_sig.B_cross},
            {"component_count", res.t_sig.component_count},
            {"raw_edge_count", res.t_sig.raw_edge_count},
            {"unique_edge_count", res.t_sig.unique_edge_count},
            {"parallel_edge_count", res.t_sig.parallel_edge_count}
        }},
        {"T_class", res.t_class},
        {"is_valid_closure", res.is_valid_closure}
    };
}

void write_decision_audit(const ClassificationResult& res, const std::string& output_path) {
    json data = serialize_result(res);
    std::ofstream out(output_path);
    out << data.dump(2);
}
