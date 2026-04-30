#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <cmath>
#include "json.hpp"
#include "AnalogEngineSYCL.hpp"

using json = nlohmann::json;
using namespace dase::analog;

struct NodeStats {
    double mean_output;
    double max_output;
    double mean_integrator;
};

template<typename T>
NodeStats calculate_stats(size_t n, const T* output, const T* integrator) {
    double sum_out = 0;
    double max_out = -1e10;
    double sum_int = 0;

    for (size_t i = 0; i < n; ++i) {
        double o = static_cast<double>(output[i]);
        double in = static_cast<double>(integrator[i]);
        sum_out += o;
        if (o > max_out) max_out = o;
        sum_int += in;
    }

    return {sum_out / n, max_out, sum_int / n};
}

template<typename T>
void run_sim(sycl::queue& q, size_t n_nodes, int steps, int iterations, T dt, const std::string& label, json& report) {
    AnalogEngineSYCL<T> engine(n_nodes, q);

    // Initial feedback gains
    T* h_gains = sycl::malloc_host<T>(n_nodes, q);
    for(size_t i=0; i<n_nodes; ++i) h_gains[i] = static_cast<T>(0.05 * (i % 10));
    q.copy(h_gains, engine.feedback_gain, n_nodes).wait();
    sycl::free(h_gains, q);

    auto start = std::chrono::high_resolution_clock::now();
    for (int s = 0; s < steps; ++s) {
        T input = static_cast<T>(std::sin(s * 0.01));
        T control = static_cast<T>(std::cos(s * 0.01));
        engine.step(input, control, static_cast<T>(0.0), dt, iterations);
    }
    auto end = std::chrono::high_resolution_clock::now();

    NodeStats stats = calculate_stats(n_nodes, engine.current_output, engine.integrator_state);
    
    report[label] = {
        {"mean_output", stats.mean_output},
        {"max_output", stats.max_output},
        {"mean_integrator", stats.mean_integrator},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/dase_analog_sim_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    // Default parameters
    size_t n_nodes = 10000;
    int steps = 1000;
    int iterations = 30; // Per node per step
    float dt = 1.0f / 48000.0f;

    json config_json;
    if (!config_path.empty()) {
        std::ifstream f(config_path);
        if (f.is_open()) {
            config_json = json::parse(f);
            n_nodes = config_json.value("n_nodes", n_nodes);
            steps = config_json.value("steps", steps);
            iterations = config_json.value("iterations", iterations);
            dt = config_json.value("dt", dt);
        }
    }

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "dase_analog_v2p3_sycl_precision_study";
    report["run_date"] = "2026-04-30";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU..." << std::endl;
    run_sim<float>(q_gpu, n_nodes, steps, iterations, dt, "fp32_results", report);

    std::cout << "Running FP64 on CPU..." << std::endl;
    run_sim<double>(q_cpu, n_nodes, steps, iterations, static_cast<double>(dt), "fp64_results", report);

    // Precision drift
    double drift_out = std::abs(report["fp32_results"]["mean_output"].get<double>() - report["fp64_results"]["mean_output"].get<double>());
    report["precision_drift"] = {
        {"mean_output_abs", drift_out},
        {"mean_output_rel", report["fp64_results"]["mean_output"].get<double>() != 0 ? drift_out / std::abs(report["fp64_results"]["mean_output"].get<double>()) : 0.0}
    };
    
    report["alignment_success_rate"] = 1.0 - (drift_out / std::abs(report["fp64_results"]["mean_output"].get<double>()));

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
