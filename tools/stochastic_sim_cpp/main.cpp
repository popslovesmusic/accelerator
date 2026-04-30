#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <cmath>
#include <numeric>
#include <algorithm>
#include "json.hpp"
#include "StochasticEngineSYCL.hpp"

using json = nlohmann::json;
using namespace dase::stochastic;

template<typename T>
struct Metrics {
    double mean_x;
    double std_x;
    float crossing_fraction;
    double mean_onset_time;
};

template<typename T>
Metrics<T> calculate_metrics(size_t n, const T* x, const T* onset_times, const bool* has_crossed) {
    double sum_x = 0;
    double sum_x2 = 0;
    size_t crossed_count = 0;
    double sum_onset = 0;

    for (size_t i = 0; i < n; ++i) {
        double val = static_cast<double>(x[i]);
        sum_x += val;
        sum_x2 += val * val;
        if (has_crossed[i]) {
            crossed_count++;
            sum_onset += static_cast<double>(onset_times[i]);
        }
    }

    double mean = sum_x / n;
    double std = std::sqrt(std::max(0.0, sum_x2 / n - mean * mean));
    return {
        mean,
        std,
        static_cast<float>(crossed_count) / n,
        crossed_count > 0 ? sum_onset / crossed_count : 0.0
    };
}

template<typename T>
void run_sim(sycl::queue& q, size_t n, int steps, T dt, T kappa, T sigma, T x_thresh, T initial_x, uint32_t seed, const std::string& label, json& report) {
    StochasticEngineSYCL<T> engine(n, q);
    engine.initialize(initial_x);

    auto start = std::chrono::high_resolution_clock::now();
    for (int s = 0; s < steps; ++s) {
        T current_time = static_cast<T>(s * dt);
        // Varying the seed per step to get new noise, but deterministic per run
        engine.step(dt, kappa, sigma, x_thresh, current_time, seed + s);
    }
    auto end = std::chrono::high_resolution_clock::now();

    Metrics<T> m = calculate_metrics(n, engine.x, engine.onset_times, engine.has_crossed);
    
    report[label] = {
        {"mean_x", m.mean_x},
        {"std_x", m.std_x},
        {"crossing_fraction", m.crossing_fraction},
        {"mean_onset_time", m.mean_onset_time},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/stochastic_sim_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    // Default parameters
    size_t n_particles = 100000;
    int steps = 1000;
    float dt = 0.01f;
    float kappa = 0.5f;
    float sigma = 0.2f;
    float x_thresh = 0.5f;
    float initial_x = 0.0f;
    uint32_t seed = 42;

    json config_json;
    if (!config_path.empty()) {
        std::ifstream f(config_path);
        if (f.is_open()) {
            config_json = json::parse(f);
            n_particles = config_json.value("n_particles", n_particles);
            steps = config_json.value("steps", steps);
            dt = config_json.value("dt", dt);
            kappa = config_json.value("kappa", kappa);
            sigma = config_json.value("sigma", sigma);
            x_thresh = config_json.value("x_thresh", x_thresh);
            initial_x = config_json.value("initial_x", initial_x);
            seed = config_json.value("seed", seed);
        }
    }

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "stochastic_sim_v2p3_sycl_precision_study";
    report["run_date"] = "2026-04-30";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU..." << std::endl;
    run_sim<float>(q_gpu, n_particles, steps, dt, kappa, sigma, x_thresh, initial_x, seed, "fp32_results", report);

    std::cout << "Running FP64 on CPU..." << std::endl;
    run_sim<double>(q_cpu, n_particles, steps, static_cast<double>(dt), static_cast<double>(kappa), static_cast<double>(sigma), static_cast<double>(x_thresh), static_cast<double>(initial_x), seed, "fp64_results", report);

    // Falsification: Zero Noise should result in Zero Crossings
    std::cout << "Running Falsification (Zero Noise)..." << std::endl;
    run_sim<double>(q_cpu, n_particles, steps, static_cast<double>(dt), static_cast<double>(kappa), 0.0, static_cast<double>(x_thresh), static_cast<double>(initial_x), seed, "falsification_zero_noise", report);

    // Charter metrics mapping
    double fraction_drift = std::abs(report["fp32_results"]["crossing_fraction"].get<double>() - report["fp64_results"]["crossing_fraction"].get<double>());
    report["precision_drift"] = {
        {"crossing_fraction_abs", fraction_drift},
        {"crossing_fraction_rel", report["fp64_results"]["crossing_fraction"].get<double>() > 0 ? fraction_drift / report["fp64_results"]["crossing_fraction"].get<double>() : 0.0}
    };
    
    // Primitive mapping
    report["exclusion_rate_k"] = 1.0 - report["fp64_results"]["crossing_fraction"].get<double>(); // In this context, NOT crossing is exclusion
    report["alignment_success_rate"] = report["fp64_results"]["crossing_fraction"].get<double>();

    std::filesystem::create_directories(out_dir);

    json summary;
    summary["config"] = config_json;
    summary["final_metrics"] = report["fp64_results"];
    summary["report"] = report;
    summary["status"] = "completed";

    std::ofstream o(std::filesystem::path(out_dir) / "summary.json");
    o << std::setw(4) << summary << std::endl;

    std::cout << "Simulation complete. Summary saved to " << out_dir << "/summary.json" << std::endl;

    return 0;
}
