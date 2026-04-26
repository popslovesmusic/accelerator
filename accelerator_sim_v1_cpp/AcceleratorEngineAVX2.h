#pragma once

#include <vector>
#include <string>
#include <memory>
#include <immintrin.h>
#include <omp.h>

namespace dase {
namespace accelerator {

/**
 * Structure of Arrays (SoA) for particle bunch state.
 * Optimized for AVX2 (256-bit) vectorization.
 * 
 * Each array is aligned to 32 bytes to allow for efficient 
 * aligned loads/stores (_mm256_load_pd / _mm256_store_pd).
 */
struct ParticleBunchSoA {
    size_t count;
    double* x;     // x position
    double* px;    // x momentum
    double* y;     // y position
    double* py;    // y momentum
    double* z;     // longitudinal position
    double* delta; // energy deviation
    bool* alive;   // survival status

    explicit ParticleBunchSoA(size_t n);
    ~ParticleBunchSoA();

    // Prevent copying
    ParticleBunchSoA(const ParticleBunchSoA&) = delete;
    ParticleBunchSoA& operator=(const ParticleBunchSoA&) = delete;
};

/**
 * Base class for lattice elements.
 */
class LatticeElement {
public:
    virtual ~LatticeElement() = default;
    virtual void apply(ParticleBunchSoA& bunch) = 0;
    virtual std::string name() const = 0;
};

/**
 * High-performance 6D Accelerator Engine using AVX2.
 */
class AcceleratorEngineAVX2 {
public:
    explicit AcceleratorEngineAVX2(size_t particle_count);
    
    void addElement(std::unique_ptr<LatticeElement> element);
    void run(int steps);
    
    // Bunch initialization
    void initializeNormal(double x_rms, double px_rms, double y_rms, double py_rms, double z_rms, double delta_rms, int seed);

    // Getters for metrics
    void getMetrics(double& x_mean, double& x_rms, double& survival_fraction) const;

private:
    size_t particle_count_;
    std::unique_ptr<ParticleBunchSoA> bunch_;
    std::vector<std::unique_ptr<LatticeElement>> lattice_;
    
    // Performance counters
    uint64_t total_ops_ = 0;
    double execution_time_ns_ = 0;
};

} // namespace accelerator
} // namespace dase
