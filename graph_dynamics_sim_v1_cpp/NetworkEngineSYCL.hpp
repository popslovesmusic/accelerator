#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace network {

/**
 * Intel UHD 770 SYCL Kernel for Dynamic Graphs.
 * Optimized for Single Precision (FP32).
 */
class NetworkEngineSYCL {
public:
    NetworkEngineSYCL(int n) : n_(n), q_(sycl::default_selector_v) {
        phi_ = sycl::malloc_shared<float>(n, q_);
        omega_ = sycl::malloc_shared<float>(n, q_);
        A_ = sycl::malloc_shared<uint8_t>(n * n, q_);
        std::cout << "Network Dynamics SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~NetworkEngineSYCL() {
        sycl::free(phi_, q_); sycl::free(omega_, q_); sycl::free(A_, q_);
    }

    void step_and_rewire(float dt, float K, float theta_de, float theta_re) {
        int n = n_;
        float* phi = phi_; float* omega = omega_; uint8_t* A = A_;
        
        // 1. Phase update
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            float phi_i = phi[i];
            float coupling = 0.0f;
            for (int j = 0; j < n; ++j) {
                if (A[i * n + j]) {
                    coupling += sycl::sin(phi[j] - phi_i);
                }
            }
            phi[i] += dt * (omega[i] + (K / (float)n) * coupling);
            phi[i] = sycl::fmod(phi[i], 2.0f * 3.1415926535f);
        }).wait();

        // 2. Rewire (Topological stress evaluation)
        q_.parallel_for(sycl::range<2>(n, n), [=](sycl::id<2> idx) {
            int i = (int)idx[0]; int j = (int)idx[1];
            if (i == j) return;
            
            float stress = sycl::fabs(sycl::sin(phi[j] - phi[i]));
            if (A[i * n + j] && stress > theta_de) {
                A[i * n + j] = 0; // Decouple
            } 
        }).wait();
    }

    float *phi_, *omega_;
    uint8_t *A_;

private:
    int n_;
    sycl::queue q_;
};

} // namespace network
} // namespace dase
