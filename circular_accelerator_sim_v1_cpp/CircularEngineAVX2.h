#pragma once

#include <vector>
#include <string>
#include <memory>
#include <immintrin.h>
#include <omp.h>

namespace dase {
namespace circular {

/**
 * Structure of Arrays (SoA) for Circular Accelerator Bunch.
 */
struct RingBunchSoA {
    size_t count;
    double* x;
    double* px;
    double* y;
    double* py;
    double* z;
    double* delta;
    bool* alive;

    explicit RingBunchSoA(size_t n);
    ~RingBunchSoA();
};

/**
 * Base class for ring lattice elements.
 */
class RingElement {
public:
    virtual ~RingElement() = default;
    virtual void apply(RingBunchSoA& bunch) = 0;
};

/**
 * High-performance Circular Accelerator Engine using AVX2.
 */
class CircularEngineAVX2 {
public:
    explicit CircularEngineAVX2(size_t particle_count, double circumference, double momentum_compaction);
    
    void addElement(std::unique_ptr<RingElement> element);
    void run(int turns);
    
    void initialize(int seed, double x_sigma, double px_sigma, double y_sigma, double py_sigma, double z_sigma, double delta_sigma);
    
    struct Metrics {
        int turn;
        size_t alive_count;
        double x_rms;
        double y_rms;
        double z_rms;
        double delta_rms;
    };
    
    Metrics getMetrics(int turn) const;

private:
    size_t count_;
    double circumference_;
    double momentum_compaction_;
    std::unique_ptr<RingBunchSoA> bunch_;
    std::vector<std::unique_ptr<RingElement>> lattice_;

    void advanceLongitudinal();
};

} // namespace circular
} // namespace dase
