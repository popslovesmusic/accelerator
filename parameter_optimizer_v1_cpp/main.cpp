#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include "../stochastic_sim_cpp/json.hpp"

using json = nlohmann::json;

namespace {
std::string replace_all(std::string s, const std::string& key, const std::string& val) {
    size_t pos = 0;
    while ((pos = s.find(key, pos)) != std::string::npos) {
        s.replace(pos, key.size(), val);
        pos += val.size();
    }
    return s;
}

json sample_candidate(const json& params, std::mt19937& rng) {
    json sampled = json::object();
    for (auto it = params.begin(); it != params.end(); ++it) {
        double lo = it.value()[0].get<double>();
        double hi = it.value()[1].get<double>();
        std::uniform_real_distribution<double> d(lo, hi);
        sampled[it.key()] = d(rng);
    }
    return sampled;
}

std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) out.push_back(item);
    return out;
}

double extract_score(const std::filesystem::path& eval_dir, const std::string& spec) {
    if (spec.empty()) return 1.0;
    auto parts = split(spec, ':');
    if (parts.size() != 2) return 1.0;
    std::filesystem::path json_path = eval_dir / parts[0];
    std::ifstream in(json_path);
    if (!in) return 0.0;
    json doc;
    in >> doc;
    json* cur = &doc;
    for (const auto& key : split(parts[1], '.')) {
        if (!cur->is_object() || !cur->contains(key)) return 0.0;
        cur = &((*cur)[key]);
    }
    return cur->is_number() ? cur->get<double>() : 0.0;
}
}

int main(int argc, char** argv) {
    std::string config_path;
    std::string out_root = "outputs/parameter_optimizer_v1_cpp/default";
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (a == "--out" && i + 1 < argc) out_root = argv[++i];
    }

    json cfg = {
        {"max_evals", 4},
        {"seed", 123},
        {"command_template", ""},
        {"base_config", {{"steps", 1}}},
        {"search_params", {{"K", json::array({0.0, 1.0})}}}
    };
    if (!config_path.empty()) {
        std::ifstream in(config_path);
        in >> cfg;
    }

    std::filesystem::create_directories(out_root);
    std::ofstream trace(std::filesystem::path(out_root) / "optimization_trace.csv");
    trace << "eval,status,score,config_path,out_dir";
    for (auto it = cfg["search_params"].begin(); it != cfg["search_params"].end(); ++it) trace << "," << it.key();
    trace << "\n";

    std::mt19937 rng(cfg.value("seed", 123));
    int max_evals = cfg.value("max_evals", 4);
    std::string templ = cfg.value("command_template", "");
    double best_score = -std::numeric_limits<double>::infinity();
    json best_config = cfg["base_config"];
    int failures = 0;
    std::string score_spec = cfg.value("score_metric_path", "");

    for (int i = 0; i < max_evals; ++i) {
        auto eval_dir = std::filesystem::path(out_root) / ("eval_" + std::to_string(10000 + i).substr(1));
        std::filesystem::create_directories(eval_dir);
        json candidate = cfg["base_config"];
        json sampled = sample_candidate(cfg["search_params"], rng);
        for (auto it = sampled.begin(); it != sampled.end(); ++it) candidate[it.key()] = it.value();
        auto candidate_path = eval_dir / "config.json";
        std::ofstream cp(candidate_path);
        cp << std::setw(2) << candidate << "\n";
        cp.close();

        int rc = 0;
        if (!templ.empty()) {
            std::string cmd = replace_all(replace_all(templ, "{config}", candidate_path.string()), "{out}", eval_dir.string());
            rc = std::system(cmd.c_str());
        }
        if (rc != 0) failures++;

        double score = rc == 0 ? extract_score(eval_dir, score_spec) : 0.0;
        if (score > best_score) {
            best_score = score;
            best_config = candidate;
        }

        trace << i << "," << (rc == 0 ? "completed" : "failed") << "," << score << "," << candidate_path.string() << "," << eval_dir.string();
        for (auto it = sampled.begin(); it != sampled.end(); ++it) trace << "," << it.value();
        trace << "\n";
    }

    std::ofstream bc(std::filesystem::path(out_root) / "best_config.json");
    bc << std::setw(2) << best_config << "\n";
    json report = {
        {"sim_id", "parameter_optimizer_v2p3"},
        {"schema", "v2.3_recoverable_report"},
        {"method", "deterministic_random_search"},
        {"score_metric_path", score_spec},
        {"max_evals", max_evals},
        {"best_score", best_score},
        {"failures", failures},
        {"known_model_limits", json::array({"Metric extraction supports file:key.path JSON numeric targets; non-JSON metrics require a target-specific adapter."})}
    };
    std::ofstream out(std::filesystem::path(out_root) / "optimization_report.json");
    out << std::setw(2) << report << "\n";
    std::cout << "Optimization trace saved to " << (std::filesystem::path(out_root) / "optimization_trace.csv").string() << "\n";
    return failures == 0 ? 0 : 1;
}
