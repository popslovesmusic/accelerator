#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>

namespace dase {
namespace accelerator {

/**
 * GPU-Accelerated Kernels using SYCL (oneAPI).
 * Optimized for Intel UHD 770 (Single Precision).
 */
class SYCLAcceleratorEngine {
public:
    SYCLAcceleratorEngine(size_t n) : count_(n), q_(sycl::default_selector_v) {
        // Allocate Unified Shared Memory (USM) - zero-copy access for CPU/GPU
        // Using float (fp32) because Intel UHD 770 typically lacks fp64 support
        x = sycl::malloc_shared<float>(n, q_);
        px = sycl::malloc_shared<float>(n, q_);
        y = sycl::malloc_shared<float>(n, q_);
        py = sycl::malloc_shared<float>(n, q_);
        z = sycl::malloc_shared<float>(n, q_);
        delta = sycl::malloc_shared<float>(n, q_);
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
    void apply_drift(float length) {
        const size_t n = count_;
        auto x_ptr = x;
        auto px_ptr = px;
        auto y_ptr = y;
        auto py_ptr = py;
        auto z_ptr = z;
        auto delta_ptr = delta;
        auto alive_ptr = alive;
        
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            if (!alive_ptr[i]) return;
            
            float inv_rigidity = 1.0f / (1.0f + delta_ptr[i]);
            x_ptr[i] += length * px_ptr[i] * inv_rigidity;
            y_ptr[i] += length * py_ptr[i] * inv_rigidity;
            z_ptr[i] += length * delta_ptr[i];
        }).wait();
    }

    /**
     * GPU Quadrupole Kick Kernel
     */
    void apply_kick(float kL) {
        const size_t n = count_;
        auto x_ptr = x;
        auto px_ptr = px;
        auto y_ptr = y;
        auto py_ptr = py;
        auto alive_ptr = alive;

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            if (!alive_ptr[i]) return;
            
            px_ptr[i] -= kL * x_ptr[i];
            py_ptr[i] += kL * y_ptr[i];
        }).wait();
    }

    // Pointers to USM buffers
    float *x, *px, *y, *py, *z, *delta;
    bool *alive;

private:
    size_t count_;
    sycl::queue q_;
};

} // namespace accelerator
} // namespace dase
