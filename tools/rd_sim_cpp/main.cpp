#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <cmath>
#include "json.hpp"
#include "RDEngineSYCL.hpp"

using json = nlohmann::json;
using namespace dase::rd;

template<typename T>
struct Metrics {
    double active_area;
    double total_signal;
    double max_signal;
};

template<typename T>
Metrics<T> calculate_metrics(size_t size, const T* D, const T* S) {
    double area = 0;
    double signal = 0;
    double max_s = 0;
    for (size_t i = 0; i < size * size; ++i) {
        area += static_cast<double>(D[i]);
        signal += static_cast<double>(S[i]);
        if (static_cast<double>(S[i]) > max_s) max_s = static_cast<double>(S[i]);
    }
    return {area, signal, max_s};
}

template<typename T>
void run_sim(sycl::queue& q, size_t size, int steps, T dt, T D_diff, T S_diff, T beta, T theta_g, T gamma, T alpha, T source_strength, size_t px, size_t py, T radius, const std::string& label, json& report) {
    RDEngineSYCL<T> engine(size, q);
    engine.initialize_source(px, py, radius);

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < steps; ++i) {
        engine.step(dt, D_diff, S_diff, beta, theta_g, gamma, alpha, source_strength, px, py, radius);
    }
    auto end = std::chrono::high_resolution_clock::now();

    Metrics<T> m = calculate_metrics(size, engine.D, engine.S);
    
    report[label] = {
        {"active_area", m.active_area},
        {"total_signal", m.total_signal},
        {"max_signal", m.max_signal},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/rd_sim_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    // Default parameters
    size_t size = 128;
    int steps = 1000;
    float dt = 0.01f;
    float D_diff = 0.1f;
    float S_diff = 0.5f;
    float beta = 1.0f;
    float theta_g = 0.2f;
    float gamma = 0.01f;
    float alpha = 0.05f;
    float source_strength = 0.1f;
    size_t px = 64, py = 64;
    float radius = 5.0f;

    json config_json;
    if (!config_path.empty()) {
        std::ifstream f(config_path);
        if (f.is_open()) {
            config_json = json::parse(f);
            size = config_json.value("size", 128);
            steps = config_json.value("steps", 1000);
            dt = config_json.value("dt", 0.01f);
            D_diff = config_json.value("D_diff", 0.1f);
            S_diff = config_json.value("S_diff", 0.5f);
            beta = config_json.value("beta", 1.0f);
            theta_g = config_json.value("theta_g", 0.2f);
            gamma = config_json.value("gamma", 0.01f);
            alpha = config_json.value("alpha", 0.05f);
            source_strength = config_json.value("source_strength", 0.1f);
            px = config_json.value("px", 64);
            py = config_json.value("py", 64);
            radius = config_json.value("radius", 5.0f);
        }
    }

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "rd_moving_boundary_v2p3_sycl_precision_study";
    report["run_date"] = "2026-04-30";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU..." << std::endl;
    run_sim<float>(q_gpu, size, steps, dt, D_diff, S_diff, beta, theta_g, gamma, alpha, source_strength, px, py, radius, "fp32_results", report);

    std::cout << "Running FP64 on CPU..." << std::endl;
    run_sim<double>(q_cpu, size, steps, static_cast<double>(dt), static_cast<double>(D_diff), static_cast<double>(S_diff), static_cast<double>(beta), static_cast<double>(theta_g), static_cast<double>(gamma), static_cast<double>(alpha), static_cast<double>(source_strength), px, py, static_cast<double>(radius), "fp64_results", report);

    // Falsification: High Signal Decay (alpha) should result in zero domain growth
    std::cout << "Running Falsification (High Decay)..." << std::endl;
    run_sim<double>(q_cpu, size, steps, static_cast<double>(dt), static_cast<double>(D_diff), static_cast<double>(S_diff), static_cast<double>(beta), static_cast<double>(theta_g), static_cast<double>(gamma), 10.0, static_cast<double>(source_strength), px, py, static_cast<double>(radius), "falsification_high_decay", report);

    // Charter metrics mapping
    double area_drift = std::abs(report["fp32_results"]["active_area"].get<double>() - report["fp64_results"]["active_area"].get<double>());
    report["precision_drift"] = {
        {"active_area_abs", area_drift},
        {"active_area_rel", report["fp64_results"]["active_area"].get<double>() != 0 ? area_drift / report["fp64_results"]["active_area"].get<double>() : 0.0}
    };
    
    // Primitive mapping
    report["exclusion_rate_k"] = report["fp64_results"]["active_area"].get<double>() != 0 ? report["falsification_high_decay"]["active_area"].get<double>() / report["fp64_results"]["active_area"].get<double>() : 1.0;

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
