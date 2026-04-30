#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
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

double uniform(std::mt19937& rng, double a, double b) {
    std::uniform_real_distribution<double> d(a, b);
    return d(rng);
}

json sample_params(const json& scan, std::mt19937& rng) {
    json sampled = json::object();
    for (auto it = scan.begin(); it != scan.end(); ++it) {
        const auto& rule = it.value();
        std::string type = rule.value("type", "uniform");
        if (type == "uniform") sampled[it.key()] = uniform(rng, rule["min"].get<double>(), rule["max"].get<double>());
        else if (type == "choice") {
            const auto& vals = rule["values"];
            std::uniform_int_distribution<size_t> pick(0, vals.size() - 1);
            sampled[it.key()] = vals[pick(rng)];
        }
    }
    return sampled;
}
}

int main(int argc, char** argv) {
    std::string config_path;
    std::string out_root = "outputs/mc_ensemble_sim_v1_cpp/default";
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (a == "--out" && i + 1 < argc) out_root = argv[++i];
    }

    json cfg = {
        {"trials", 1},
        {"seed", 123},
        {"command_template", ""},
        {"base_config", {{"steps", 1}}},
        {"scan_params", {{"K", {{"type", "uniform"}, {"min", 0.0}, {"max", 1.0}}}}}
    };
    if (!config_path.empty()) {
        std::ifstream in(config_path);
        in >> cfg;
    }

    std::filesystem::create_directories(out_root);
    std::ofstream csv(std::filesystem::path(out_root) / "ensemble_results.csv");
    csv << "trial_id,status,config_path,out_dir";
    for (auto it = cfg["scan_params"].begin(); it != cfg["scan_params"].end(); ++it) csv << "," << it.key();
    csv << "\n";

    std::mt19937 rng(cfg.value("seed", 123));
    int trials = cfg.value("trials", 1);
    std::string templ = cfg.value("command_template", "");
    int failures = 0;
    for (int i = 0; i < trials; ++i) {
        auto trial_dir = std::filesystem::path(out_root) / ("trial_" + std::to_string(10000 + i).substr(1));
        std::filesystem::create_directories(trial_dir);
        json trial_cfg = cfg["base_config"];
        json sampled = sample_params(cfg["scan_params"], rng);
        for (auto it = sampled.begin(); it != sampled.end(); ++it) trial_cfg[it.key()] = it.value();
        auto trial_config_path = trial_dir / "config.json";
        std::ofstream tc(trial_config_path);
        tc << std::setw(2) << trial_cfg << "\n";
        tc.close();

        int rc = 0;
        if (!templ.empty()) {
            std::string cmd = replace_all(replace_all(templ, "{config}", trial_config_path.string()), "{out}", trial_dir.string());
            rc = std::system(cmd.c_str());
        }
        if (rc != 0) failures++;
        csv << i << "," << (rc == 0 ? "completed" : "failed") << "," << trial_config_path.string() << "," << trial_dir.string();
        for (auto it = sampled.begin(); it != sampled.end(); ++it) csv << "," << it.value();
        csv << "\n";
    }

    json report = {
        {"sim_id", "mc_ensemble_orchestrator_v2p3"},
        {"schema", "v2.3_recoverable_report"},
        {"trials", trials},
        {"failures", failures},
        {"artifact_risk", "Orchestrator validates trial generation and command return codes; scientific metrics remain responsibility of target simulator outputs."}
    };
    std::ofstream out(std::filesystem::path(out_root) / "ensemble_report.json");
    out << std::setw(2) << report << "\n";
    std::cout << "Ensemble manifest saved to " << (std::filesystem::path(out_root) / "ensemble_results.csv").string() << "\n";
    return failures == 0 ? 0 : 1;
}
