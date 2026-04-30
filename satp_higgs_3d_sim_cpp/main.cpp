#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <cmath>
#include "json.hpp"
#include "SATPHiggsEngine3DSYCL.hpp"
#include "SATPHiggsParamsSYCL.hpp"

using json = nlohmann::json;
using namespace dase::satp_higgs;

struct FieldMetrics {
    double phi_rms;
    double higgs_rms;
};

template<typename T>
FieldMetrics calculate_metrics(size_t nx, size_t ny, size_t nz, T dx, const T* phi, const T* h, const SATPHiggsParamsSYCL<T>& params) {
    double sum_p2 = 0;
    double sum_h_dev2 = 0;
    size_t n = nx * ny * nz;
    
    for (size_t i = 0; i < n; ++i) {
        double p = static_cast<double>(phi[i]);
        double hv = static_cast<double>(h[i]);
        sum_p2 += p * p;
        double dev = hv - static_cast<double>(params.h_vev);
        sum_h_dev2 += dev * dev;
    }

    return {
        std::sqrt(sum_p2 / n),
        std::sqrt(sum_h_dev2 / n)
    };
}

template<typename T>
void run_sim(sycl::queue& q, size_t nx, size_t ny, size_t nz, int steps, T dt, T dx, const SATPHiggsParamsSYCL<T>& params, const std::string& label, json& report) {
    SATPHiggsEngine3DSYCL<T> engine(nx, ny, nz, q);
    engine.initialize_vacuum(params.h_vev);

    // Initial perturbation (Spherical Gaussian bump in phi)
    size_t mid_x = nx / 2;
    size_t mid_y = ny / 2;
    size_t mid_z = nz / 2;
    size_t n_total = nx * ny * nz;
    T* h_phi = sycl::malloc_host<T>(n_total, q);
    
    T sigma = 0.05 * static_cast<T>(nx * dx);
    for(size_t iz=0; iz<nz; ++iz) {
        for(size_t iy=0; iy<ny; ++iy) {
            for(size_t ix=0; ix<nx; ++ix) {
                T x_pos = ix * dx;
                T y_pos = iy * dx;
                T z_pos = iz * dx;
                T r2 = (x_pos - mid_x*dx)*(x_pos - mid_x*dx) + 
                       (y_pos - mid_y*dx)*(y_pos - mid_y*dx) +
                       (z_pos - mid_z*dx)*(z_pos - mid_z*dx);
                h_phi[iz*nx*ny + iy*nx + ix] = 0.5f * std::exp(-r2 / (2.0f * sigma * sigma));
            }
        }
    }
    q.copy(h_phi, engine.phi, n_total).wait();
    sycl::free(h_phi, q);

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < steps; ++i) {
        engine.step(dt, dx, params);
    }
    auto end = std::chrono::high_resolution_clock::now();

    FieldMetrics m = calculate_metrics(nx, ny, nz, dx, engine.phi, engine.h, params);
    
    report[label] = {
        {"phi_rms", m.phi_rms},
        {"higgs_rms", m.higgs_rms},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}

int main() {
    size_t nx = 64, ny = 64, nz = 64;
    int steps = 100; // Fewer steps for 3D benchmark
    float dt = 0.001f;
    float dx = 0.01f;

    SATPHiggsParamsSYCL<float> params_f;
    SATPHiggsParamsSYCL<double> params_d;

    sycl::queue q_gpu(sycl::default_selector_v);
    sycl::queue q_cpu(sycl::cpu_selector_v);

    json report;
    report["sim_id"] = "satp_higgs_3d_v2p3_sycl_precision_study";
    report["run_date"] = "2026-04-29";
    report["hardware_gpu"] = q_gpu.get_device().get_info<sycl::info::device::name>();
    report["hardware_cpu"] = q_cpu.get_device().get_info<sycl::info::device::name>();

    std::cout << "Running FP32 on GPU (64^3)..." << std::endl;
    run_sim<float>(q_gpu, nx, ny, nz, steps, dt, dx, params_f, "fp32_results", report);

    std::cout << "Running FP64 on CPU (64^3)..." << std::endl;
    run_sim<double>(q_cpu, nx, ny, nz, steps, static_cast<double>(dt), static_cast<double>(dx), params_d, "fp64_results", report);

    // Precision drift
    double drift_phi = std::abs(report["fp32_results"]["phi_rms"].get<double>() - report["fp64_results"]["phi_rms"].get<double>());
    report["precision_drift"] = {
        {"phi_rms_abs", drift_phi},
        {"phi_rms_rel", drift_phi / report["fp64_results"]["phi_rms"].get<double>()}
    };
    
    // Primitive mapping
    report["alignment_success_rate"] = 1.0 - (drift_phi / report["fp64_results"]["phi_rms"].get<double>());

    std::filesystem::create_directories("outputs/satp_higgs_3d_sim_cpp");
    std::ofstream o("outputs/satp_higgs_3d_sim_cpp/v2p3_report.json");
    o << std::setw(4) << report << std::endl;

    std::cout << "Simulation complete. Report saved to outputs/satp_higgs_3d_sim_cpp/v2p3_report.json" << std::endl;

    return 0;
}
