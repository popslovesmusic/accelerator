#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <random>
#include "json.hpp"
#include "LinacEngineSYCL.hpp"
#include "LinacLatticeElements.h"

using json = nlohmann::json;
using namespace dase::linac;

template<typename T>
struct RunResult {
    double emittance_y;
    double emittance_z;
    float survival;
    long long time_ms;
};

// Helper to calculate statistics using double precision
template<typename T>
void calculate_metrics(size_t n, const T* y, const T* py, const bool* alive, double& rms_emittance, float& survival) {
    size_t active_count = 0;
    double sum_y = 0, sum_py = 0;
    double sum_y2 = 0, sum_py2 = 0, sum_ypy = 0;

    for (size_t i = 0; i < n; ++i) {
        if (alive[i]) {
            active_count++;
            double dy = static_cast<double>(y[i]);
            double dpy = static_cast<double>(py[i]);
            sum_y += dy;
            sum_py += dpy;
            sum_y2 += dy * dy;
            sum_py2 += dpy * dpy;
            sum_ypy += dy * dpy;
        }
    }

    if (active_count > 1) {
        double mean_y = sum_y / active_count;
        double mean_py = sum_py / active_count;
        double var_y = (sum_y2 / active_count) - (mean_y * mean_y);
        double var_py = (sum_py2 / active_count) - (mean_py * mean_py);
        double cov_ypy = (sum_ypy / active_count) - (mean_y * mean_py);
        rms_emittance = std::sqrt(std::max(0.0, var_y * var_py - cov_ypy * cov_ypy));
    } else {
        rms_emittance = 0;
    }
    survival = static_cast<float>(active_count) / n;
}

template<typename T>
RunResult<T> run_experiment(sycl::queue& q, size_t n_particles, int steps, T dt, const std::vector<ComponentData>& lattice, T mass, T charge, T aperture, unsigned int seed) {
    ComponentData* d_lattice = sycl::malloc_shared<ComponentData>(lattice.size(), q);
    std::memcpy(d_lattice, lattice.data(), lattice.size() * sizeof(ComponentData));

    LinacEngineSYCL<T> engine(n_particles, q);
    
    std::mt19937 gen(seed);
    std::normal_distribution<T> dist_y(0, 0.001);
    std::normal_distribution<T> dist_py(0, 1e-22);
    std::normal_distribution<T> dist_z(0, 0.001);
    std::normal_distribution<T> dist_pz(0, 1e-22);

    for (size_t i = 0; i < n_particles; ++i) {
        engine.x[i] = 0;
        engine.px[i] = 2.3e-20; 
        engine.y[i] = dist_y(gen);
        engine.py[i] = dist_py(gen);
        engine.z[i] = dist_z(gen);
        engine.pz[i] = dist_pz(gen);
        engine.alive[i] = true;
    }

    T time = 0;
    auto start = std::chrono::high_resolution_clock::now();
    for (int s = 0; s < steps; ++s) {
        engine.step(dt, time, d_lattice, lattice.size(), mass, charge, aperture);
        time += dt;
    }
    auto end = std::chrono::high_resolution_clock::now();

    double em_y, em_z;
    float surv;
    calculate_metrics(n_particles, engine.y, engine.py, engine.alive, em_y, surv);
    calculate_metrics(n_particles, engine.z, engine.pz, engine.alive, em_z, surv);

    sycl::free(d_lattice, q);
    return {em_y, em_z, surv, std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()};
}

int main(int argc, char* argv[]) {
    size_t n_particles = 10000;
    float dt = 2e-12f;
    float t_final = 1e-7f;
    float mass = 1.67262192369e-27f;
    float charge = 1.602176634e-19f;
    float aperture = 0.01f;
    int gap_count = 20;
    unsigned int seed = 12345;
    int steps = static_cast<int>(t_final / dt);

    std::vector<ComponentData> lattice;
    float pos = 0;
    for (int i = 0; i < gap_count; ++i) {
        lattice.push_back({ComponentType::DRIFT, pos, 0.0175f, 0, 0, 0, 0, 0});
        pos += 0.0175f;
        lattice.push_back({ComponentType::FOCUSING_LENS, pos, 0.005f, 0, 0, 0, 25.0f, 25.0f});
        pos += 0.005f;
        lattice.push_back({ComponentType::DRIFT, pos, 0.0175f, 0, 0, 0, 0, 0});
        pos += 0.0175f;
        lattice.push_back({ComponentType::RF_GAP, pos, 0.01f, 2e6f, 200e6f, 1.570796f, 0, 0});
        pos += 0.01f;
    }

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    std::cout << "Running FP32 on: " << q_gpu.get_device().get_info<sycl::info::device::name>() << std::endl;
    auto res_fp32 = run_experiment<float>(q_gpu, n_particles, steps, dt, lattice, mass, charge, aperture, seed);

    std::cout << "Running FP64 on: " << q_cpu.get_device().get_info<sycl::info::device::name>() << std::endl;
    auto res_fp64 = run_experiment<double>(q_cpu, n_particles, steps, static_cast<double>(dt), lattice, static_cast<double>(mass), static_cast<double>(charge), static_cast<double>(aperture), seed);

    // Falsification Case: Zero Mismatch (No fields)
    std::vector<ComponentData> zero_lattice = lattice;
    for (auto& c : zero_lattice) {
        c.peak_field_v_per_m = 0;
        c.focusing_strength_1_per_m2 = 0;
        c.z_focusing_strength_1_per_m2 = 0;
    }
    std::cout << "Running Falsification (Zero-Field) on: " << q_cpu.get_device().get_info<sycl::info::device::name>() << std::endl;
    auto res_falsify = run_experiment<double>(q_cpu, n_particles, steps, static_cast<double>(dt), zero_lattice, static_cast<double>(mass), static_cast<double>(charge), static_cast<double>(aperture), seed);

    double drift_y = std::abs(res_fp32.emittance_y - res_fp64.emittance_y);
    double drift_z = std::abs(res_fp32.emittance_z - res_fp64.emittance_z);

    json report;
    report["sim_id"] = "linac_sim_v2p3_sycl_precision_study";
    report["batch_id"] = "rerun_ground_zero";
    report["run_date"] = "2026-04-29";
    report["fp32_results"] = {
        {"emittance_y", res_fp32.emittance_y},
        {"emittance_z", res_fp32.emittance_z},
        {"survival", res_fp32.survival},
        {"time_ms", res_fp32.time_ms}
    };
    report["fp64_results"] = {
        {"emittance_y", res_fp64.emittance_y},
        {"emittance_z", res_fp64.emittance_z},
        {"survival", res_fp64.survival},
        {"time_ms", res_fp64.time_ms}
    };
    report["precision_drift"] = {
        {"emittance_y_abs", drift_y},
        {"emittance_y_rel", drift_y / res_fp64.emittance_y},
        {"emittance_z_abs", drift_z},
        {"emittance_z_rel", drift_z / res_fp64.emittance_z}
    };
    report["falsification"] = {
        {"zero_field_emittance_y", res_falsify.emittance_y},
        {"zero_field_emittance_z", res_falsify.emittance_z},
        {"zero_field_survival", res_falsify.survival}
    };
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::filesystem::create_directories("outputs/linac_sim_cpp");
    std::ofstream o("outputs/linac_sim_cpp/v2p3_precision_report.json");
    o << std::setw(4) << report << std::endl;

    std::cout << "Simulation complete. Precision report saved to outputs/linac_sim_cpp/v2p3_precision_report.json" << std::endl;

    return 0;
}
