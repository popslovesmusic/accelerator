#include "KuramotoEngineSYCL.hpp"
#include <iostream>
#include <vector>
#include <chrono>
#include <random>

#include "json.hpp"
#include <fstream>
#include <filesystem>

using json = nlohmann::json;

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/kuramoto_sim_v1_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    try {
        const size_t n = 100000;
        float dt = 0.1f;
        float K = 0.5f;
        int steps = 100;
        int seed = 42;

        json config_json;
        if (!config_path.empty()) {
            std::ifstream f(config_path);
            if (f.is_open()) {
                config_json = json::parse(f);
                // Note: using different names in config to match Python if needed
                dt = config_json.value("dt", 0.1f);
                K = config_json.value("K", 0.5f);
                steps = config_json.value("steps", 100);
                seed = config_json.value("seed", 42);
            }
        }

        dase::kuramoto::KuramotoEngineSYCL engine(n);

        // Initialize
        std::mt19937 gen(seed);
        std::normal_distribution<float> d_omega(0.0f, 0.1f);
        std::uniform_real_distribution<float> d_phi(0.0f, 6.283185f);

        for (size_t i = 0; i < n; ++i) {
            engine.phi[i] = d_phi(gen);
            engine.omega[i] = d_omega(gen);
        }

        std::cout << "Starting Kuramoto simulation: " << n << " oscillators, " << steps << " RK4 steps..." << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < steps; ++i) {
            engine.step_rk4(dt, K);
        }
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double> diff = end - start;
        float R = engine.compute_order_parameter();
        
        json final_metrics;
        final_metrics["order_parameter"] = R;
        final_metrics["runtime_ms"] = diff.count() * 1000.0;

        json summary;
        summary["config"] = config_json;
        summary["final_metrics"] = final_metrics;
        summary["status"] = "completed";

        std::filesystem::create_directories(out_dir);
        std::ofstream o(std::filesystem::path(out_dir) / "summary.json");
        o << std::setw(4) << summary << std::endl;

        std::cout << "Simulation complete. Summary saved to " << out_dir << "/summary.json" << std::endl;

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
