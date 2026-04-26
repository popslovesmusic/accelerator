#pragma once

#include <sycl/sycl.hpp>
#include <vector>

namespace dase {
namespace accelerator {

/**
 * GPU-Accelerated Kernels using SYCL (oneAPI).
 * Optimized for Intel UHD 770.
 */
class SYCLAcceleratorEngine {
public:
    SYCLAcceleratorEngine(size_t n) : count_(n), q_(sycl::default_selector_v) {
        // Allocate Unified Shared Memory (USM) - zero-copy access for CPU/GPU
        x = sycl::malloc_shared<double>(n, q_);
        px = sycl::malloc_shared<double>(n, q_);
        y = sycl::malloc_shared<double>(n, q_);
        py = sycl::malloc_shared<double>(n, q_);
        z = sycl::malloc_shared<double>(n, q_);
        delta = sycl::malloc_shared<double>(n, q_);
        alive = sycl::malloc_shared<bool>(n, q_);
        
        std::cout << "SYCL Engine Initialized on: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << std::endl;
    }

    ~SYCLAcceleratorEngine() {
        sycl::free(x, q_);
        sycl::free(px, q_);
        sycl::free(y, q_);
        sycl::free(py, q_);
        sycl::free(z, q_);
        sycl::free(delta, q_);
        sycl::free(alive, q_);
    }

    /**
     * GPU Drift Kernel
     */
    void apply_drift(double length) {
        const size_t n = count_;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            if (!alive[i]) return;
            
            double inv_rigidity = 1.0 / (1.0 + delta[i]);
            x[i] += length * px[i] * inv_rigidity;
            y[i] += length * py[i] * inv_rigidity;
            z[i] += length * delta[i];
        }).wait();
    }

    /**
     * GPU Quadrupole Kick Kernel
     */
    void apply_kick(double kL) {
        const size_t n = count_;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            if (!alive[i]) return;
            
            px[i] -= kL * x[i];
            py[i] += kL * y[i];
        }).wait();
    }

    // Pointers to USM buffers
    double *x, *px, *y, *py, *z, *delta;
    bool *alive;

private:
    size_t count_;
    sycl::queue q_;
};

} // namespace accelerator
} // namespace dase
