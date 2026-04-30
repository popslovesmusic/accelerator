#include "AcceleratorEngineAVX2.h"
#include "LatticeElements.h"
#include <iostream>
#include <random>
#include <chrono>

namespace dase {
namespace accelerator {

ParticleBunchSoA::ParticleBunchSoA(size_t n) : count(n) {
    // Allocate 32-byte aligned memory for AVX2
    x = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    px = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    y = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    py = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    z = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    delta = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    alive = new bool[n];
    
    for (size_t i = 0; i < n; ++i) alive[i] = true;
}

ParticleBunchSoA::~ParticleBunchSoA() {
    _mm_free(x);
    _mm_free(px);
    _mm_free(y);
    _mm_free(py);
    _mm_free(z);
    _mm_free(delta);
    delete[] alive;
}

AcceleratorEngineAVX2::AcceleratorEngineAVX2(size_t particle_count)
    : particle_count_(particle_count) {
    bunch_ = std::make_unique<ParticleBunchSoA>(particle_count);
}

void AcceleratorEngineAVX2::addElement(std::unique_ptr<LatticeElement> element) {
    lattice_.push_back(std::move(element));
}

void AcceleratorEngineAVX2::initializeNormal(double x_rms, double px_rms, double y_rms, double py_rms, double z_rms, double delta_rms, int seed) {
    std::mt19937 gen(seed);
    std::normal_distribution<double> dist_x(0, x_rms);
    std::normal_distribution<double> dist_px(0, px_rms);
    std::normal_distribution<double> dist_y(0, y_rms);
    std::normal_distribution<double> dist_py(0, py_rms);
    std::normal_distribution<double> dist_z(0, z_rms);
    std::normal_distribution<double> dist_delta(0, delta_rms);

    for (size_t i = 0; i < particle_count_; ++i) {
        bunch_->x[i] = dist_x(gen);
        bunch_->px[i] = dist_px(gen);
        bunch_->y[i] = dist_y(gen);
        bunch_->py[i] = dist_py(gen);
        bunch_->z[i] = dist_z(gen);
        bunch_->delta[i] = dist_delta(gen);
        bunch_->alive[i] = true;
    }
}

void AcceleratorEngineAVX2::run(int steps) {
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int step = 0; step < steps; ++step) {
        for (auto& element : lattice_) {
            element->apply(*bunch_);
        }
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    execution_time_ns_ = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
    total_ops_ = static_cast<uint64_t>(steps) * lattice_.size() * particle_count_;
    
    std::cout << "Simulation completed in " << execution_time_ns_ / 1e6 << " ms" << std::endl;
    std::cout << "Performance: " << (execution_time_ns_ / total_ops_) << " ns/particle/element" << std::endl;
}

void AcceleratorEngineAVX2::getMetrics(double& x_mean, double& x_rms, double& survival_fraction) const {
    double sum_x = 0;
    double sum_x2 = 0;
    size_t alive_count = 0;

    for (size_t i = 0; i < particle_count_; ++i) {
        if (bunch_->alive[i]) {
            sum_x += bunch_->x[i];
            sum_x2 += bunch_->x[i] * bunch_->x[i];
            alive_count++;
        }
    }

    if (alive_count > 0) {
        x_mean = sum_x / alive_count;
        x_rms = std::sqrt(sum_x2 / alive_count - x_mean * x_mean);
    } else {
        x_mean = 0;
        x_rms = 0;
    }
    survival_fraction = static_cast<double>(alive_count) / particle_count_;
}

} // namespace accelerator
} // namespace dase
