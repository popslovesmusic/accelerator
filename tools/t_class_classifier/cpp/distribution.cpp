#include "schemas.hpp"
#include "json.hpp"
#include <vector>
#include <map>

using json = nlohmann::json;

json compute_statistical_aggregates(const std::vector<ClassificationResult>& results) {
    int n = static_cast<int>(results.size());
    if (n == 0) {
        return {
            {"class_counts", json::object()},
            {"class_frequencies", json::object()},
            {"mean_C_count", 0.0},
            {"mean_R_conn", 0.0},
            {"var_R_conn", 0.0}
        };
    }

    std::map<std::string, int> counts = {
        {"T_0", 0}, {"T_1", 0}, {"T_2", 0}, {"T_3", 0}, {"T_4", 0}, {"T_x", 0}
    };
    int sum_c = 0;
    double sum_r = 0.0;

    for (const auto& res : results) {
        counts[res.t_class] += 1;
        sum_c += res.t_sig.C_count;
        sum_r += res.t_sig.R_conn;
    }

    double mean_c = static_cast<double>(sum_c) / n;
    double mean_r = sum_r / n;

    double sum_sq_diff_r = 0.0;
    for (const auto& res : results) {
        double diff = res.t_sig.R_conn - mean_r;
        sum_sq_diff_r += diff * diff;
    }
    double var_r = sum_sq_diff_r / n;

    std::map<std::string, double> freqs;
    for (const auto& pair : counts) {
        freqs[pair.first] = static_cast<double>(pair.second) / n;
    }

    return {
        {"class_counts", counts},
        {"class_frequencies", freqs},
        {"mean_C_count", mean_c},
        {"mean_R_conn", mean_r},
        {"var_R_conn", var_r}
    };
}
