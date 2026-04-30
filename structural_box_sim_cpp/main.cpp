#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <cmath>
#include "json.hpp"
#include "StructuralBoxEngineSYCL.hpp"

using json = nlohmann::json;
using namespace dase::structural_box;

struct Diagnostic {
    double epsilon_max;
    double rho_min;
    double residue_max;
    double epsilon_active_fraction;
};

template<typename T>
Diagnostic calculate_diagnostics(size_t nx, const T* epsilon, const T* rho, const T* residue, T activity_threshold) {
    double e_max = -1e10;
    double r_min = 1e10;
    double res_max = -1e10;
    size_t active_count = 0;

    for (size_t i = 0; i < nx; ++i) {
        double e = static_cast<double>(epsilon[i]);
        double r = static_cast<double>(rho[i]);
        double res = static_cast<double>(residue[i]);

        if (e > e_max) e_max = e;
        if (r < r_min) r_min = r;
        if (res > res_max) res_max = res;
        if (e >= static_cast<double>(activity_threshold)) active_count++;
    }

    return {e_max, r_min, res_max, static_cast<double>(active_count) / nx};
}

template<typename T>
void run_sim(sycl::queue& q, size_t nx, int steps, T dt, T length,
             T D_epsilon, T D_rho, T D_R,
             T a, T b, T c, T u, T s,
             T alpha, T beta, T gamma, T v, T h,
             T kappa, T lambda_R, T activity_thresh,
             const std::string& label, json& report) {
    
    StructuralBoxEngineSYCL<T> engine(nx, q);
    T dx = length / nx;

    // Default initialization from Python sim.py
    engine.initialize_gaussian(static_cast<T>(0.0), static_cast<T>(0.32), static_cast<T>(0.08), static_cast<T>(0.0), length);
    engine.initialize_uniform(engine.rho, static_cast<T>(0.25));
    engine.initialize_uniform(engine.residue, static_cast<T>(0.0));

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < steps; ++i) {
        engine.step(dt, dx, D_epsilon, D_rho, D_R, a, b, c, u, s, alpha, beta, gamma, v, h, kappa, lambda_R);
    }
    auto end = std::chrono::high_resolution_clock::now();

    Diagnostic d = calculate_diagnostics(nx, engine.epsilon, engine.rho, engine.residue, activity_thresh);
    
    report[label] = {
        {"epsilon_max", d.epsilon_max},
        {"rho_min", d.rho_min},
        {"residue_max", d.residue_max},
        {"epsilon_active_fraction", d.epsilon_active_fraction},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}

int main() {
    // Standard parameters from Python ModelConfig
    size_t nx = 256;
    int steps = 2000;
    float dt = 1e-4f;
    float length = 1.0f;
    float D_epsilon = 6e-4f;
    float D_rho = 4e-4f;
    float D_R = 2e-4f;
    float a = 0.60f, b = 1.20f, c = 2.00f;
    float alpha = 0.70f, beta = 0.80f, gamma = 1.20f;
    float u = 0.15f, v = 0.08f;
    float kappa = 0.60f, lambda_R = 0.80f, s = 0.01f, h = 0.08f;
    float activity_thresh = 0.05f;

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "structural_box_v2p3_sycl_precision_study";
    report["run_date"] = "2026-04-29";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU..." << std::endl;
    run_sim<float>(q_gpu, nx, steps, dt, length, D_epsilon, D_rho, D_R, a, b, c, u, s, alpha, beta, gamma, v, h, kappa, lambda_R, activity_thresh, "fp32_results", report);

    std::cout << "Running FP64 on CPU..." << std::endl;
    run_sim<double>(q_cpu, nx, steps, static_cast<double>(dt), static_cast<double>(length), 
                    static_cast<double>(D_epsilon), static_cast<double>(D_rho), static_cast<double>(D_R),
                    static_cast<double>(a), static_cast<double>(b), static_cast<double>(c), static_cast<double>(u), static_cast<double>(s),
                    static_cast<double>(alpha), static_cast<double>(beta), static_cast<double>(gamma), static_cast<double>(v), static_cast<double>(h),
                    static_cast<double>(kappa), static_cast<double>(lambda_R), static_cast<double>(activity_thresh), "fp64_results", report);

    // Falsification: Zero Mismatch (s=0) should lead to structural collapse or lower activity
    std::cout << "Running Falsification (Zero Mismatch)..." << std::endl;
    run_sim<double>(q_cpu, nx, steps, static_cast<double>(dt), static_cast<double>(length), 
                    static_cast<double>(D_epsilon), static_cast<double>(D_rho), static_cast<double>(D_R),
                    static_cast<double>(a), static_cast<double>(b), static_cast<double>(c), static_cast<double>(u), 0.0,
                    static_cast<double>(alpha), static_cast<double>(beta), static_cast<double>(gamma), static_cast<double>(v), static_cast<double>(h),
                    static_cast<double>(kappa), static_cast<double>(lambda_R), static_cast<double>(activity_thresh), "falsification_zero_s", report);

    // Precision drift calculation
    double drift_e = std::abs(report["fp32_results"]["epsilon_max"].get<double>() - report["fp64_results"]["epsilon_max"].get<double>());
    report["precision_drift"] = {
        {"epsilon_max_abs", drift_e},
        {"epsilon_max_rel", drift_e / report["fp64_results"]["epsilon_max"].get<double>()}
    };
    
    // Primitive mapping
    report["exclusion_rate_k"] = 1.0 - report["fp64_results"]["epsilon_active_fraction"].get<double>();
    report["alignment_success_rate"] = report["fp64_results"]["epsilon_active_fraction"].get<double>();

    std::filesystem::create_directories("outputs/structural_box_sim_cpp");
    std::ofstream o("outputs/structural_box_sim_cpp/v2p3_report.json");
    o << std::setw(4) << report << std::endl;

    std::cout << "Simulation complete. Report saved to outputs/structural_box_sim_cpp/v2p3_report.json" << std::endl;

    return 0;
}
