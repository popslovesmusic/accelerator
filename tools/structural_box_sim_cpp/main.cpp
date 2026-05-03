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
             T a, T b, T c, T u, T s, int s_duration,
             T alpha, T beta, T gamma, T v, T h,
             T kappa, T lambda_R, T activity_thresh,
             const json& init_config,
             const std::string& label, json& report) {
    
    StructuralBoxEngineSYCL<T> engine(nx, q);
    T dx = length / nx;

    // Configurable initialization
    std::string kind = init_config.value("epsilon_kind", "gaussian");
    if (kind == "gaussian") {
        T base = init_config.value("epsilon_base", static_cast<T>(0.0));
        T amp = init_config.value("amplitude", static_cast<T>(0.32));
        T sigma = init_config.value("sigma", static_cast<T>(0.08));
        T offset = init_config.value("offset", static_cast<T>(0.0));
        engine.initialize_gaussian(base, amp, sigma, offset, length);
    } else if (kind == "uniform") {
        T base = init_config.value("epsilon_base", static_cast<T>(0.0));
        T noise = init_config.value("noise_std", static_cast<T>(0.01));
        int seed = init_config.value("seed", 42);
        engine.initialize_noise(base, noise, seed);
    }

    engine.initialize_uniform(engine.rho, init_config.value("rho_base", static_cast<T>(0.25)));
    engine.initialize_uniform(engine.residue, init_config.value("residue_base", static_cast<T>(0.0)));

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < steps; ++i) {
        T current_s = (i < s_duration) ? s : static_cast<T>(0.0);
        engine.step(dt, dx, D_epsilon, D_rho, D_R, a, b, c, u, current_s, alpha, beta, gamma, v, h, kappa, lambda_R);
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

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/structural_box_sim_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    // Default parameters
    size_t nx = 256;
    int steps = 2000;
    int s_duration = 2000; // Default to full duration
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

    json config_json;
    json init_config = json::object(); // Default empty
    if (!config_path.empty()) {
        std::ifstream f(config_path);
        if (f.is_open()) {
            config_json = json::parse(f);
            nx = config_json.value("nx", nx);
            steps = config_json.value("steps", steps);
            s_duration = config_json.value("s_duration", steps);
            dt = config_json.value("dt", dt);
            length = config_json.value("length", length);
            D_epsilon = config_json.value("D_epsilon", D_epsilon);
            D_rho = config_json.value("D_rho", D_rho);
            D_R = config_json.value("D_R", D_R);
            a = config_json.value("a", a);
            b = config_json.value("b", b);
            c = config_json.value("c", c);
            alpha = config_json.value("alpha", alpha);
            beta = config_json.value("beta", beta);
            gamma = config_json.value("gamma", gamma);
            u = config_json.value("u", u);
            v = config_json.value("v", v);
            kappa = config_json.value("kappa", kappa);
            lambda_R = config_json.value("lambda_R", lambda_R);
            s = config_json.value("s", s);
            h = config_json.value("h", h);
            activity_thresh = config_json.value("activity_thresh", activity_thresh);
            if (config_json.contains("initial_condition")) {
                init_config = config_json["initial_condition"];
            }
        }
    }

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "structural_box_v2p3_sycl_precision_study";
    report["run_date"] = "2026-05-03";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU..." << std::endl;
    run_sim<float>(q_gpu, nx, steps, dt, length, D_epsilon, D_rho, D_R, a, b, c, u, s, s_duration, alpha, beta, gamma, v, h, kappa, lambda_R, activity_thresh, init_config, "fp32_results", report);

    std::cout << "Running FP64 on CPU..." << std::endl;
    run_sim<double>(q_cpu, nx, steps, static_cast<double>(dt), static_cast<double>(length), 
                    static_cast<double>(D_epsilon), static_cast<double>(D_rho), static_cast<double>(D_R),
                    static_cast<double>(a), static_cast<double>(b), static_cast<double>(c), static_cast<double>(u), static_cast<double>(s), s_duration,
                    static_cast<double>(alpha), static_cast<double>(beta), static_cast<double>(gamma), static_cast<double>(v), static_cast<double>(h),
                    static_cast<double>(kappa), static_cast<double>(lambda_R), static_cast<double>(activity_thresh), init_config, "fp64_results", report);

    // Falsification: Zero Mismatch (s=0) should lead to structural collapse or lower activity
    std::cout << "Running Falsification (Zero Mismatch)..." << std::endl;
    run_sim<double>(q_cpu, nx, steps, static_cast<double>(dt), static_cast<double>(length), 
                    static_cast<double>(D_epsilon), static_cast<double>(D_rho), static_cast<double>(D_R),
                    static_cast<double>(a), static_cast<double>(b), static_cast<double>(c), static_cast<double>(u), 0.0, 0,
                    static_cast<double>(alpha), static_cast<double>(beta), static_cast<double>(gamma), static_cast<double>(v), static_cast<double>(h),
                    static_cast<double>(kappa), static_cast<double>(lambda_R), static_cast<double>(activity_thresh), init_config, "falsification_zero_s", report);

    // Precision drift calculation
    double drift_e = std::abs(report["fp32_results"]["epsilon_max"].get<double>() - report["fp64_results"]["epsilon_max"].get<double>());
    report["precision_drift"] = {
        {"epsilon_max_abs", drift_e},
        {"epsilon_max_rel", report["fp64_results"]["epsilon_max"].get<double>() != 0 ? drift_e / report["fp64_results"]["epsilon_max"].get<double>() : 0.0}
    };
    
    // Primitive mapping
    report["exclusion_rate_k"] = 1.0 - report["fp64_results"]["epsilon_active_fraction"].get<double>();
    report["alignment_success_rate"] = report["fp64_results"]["epsilon_active_fraction"].get<double>();

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
