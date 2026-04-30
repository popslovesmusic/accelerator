#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace swarm {

/**
 * Intel UHD 770 SYCL Kernel for Swarm Dynamics.
 * Optimized for Single Precision (FP32).
 */
class AgentEngineSYCL {
public:
    AgentEngineSYCL(size_t n) : count_(n), q_(sycl::default_selector_v) {
        x_ = sycl::malloc_shared<float>(n, q_);
        p_ = sycl::malloc_shared<float>(n, q_);
        phi_ = sycl::malloc_shared<float>(n, q_);
        omega_ = sycl::malloc_shared<float>(n, q_);
        std::cout << "Agent Swarm SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~AgentEngineSYCL() {
        sycl::free(x_, q_); sycl::free(p_, q_); sycl::free(phi_, q_); sycl::free(omega_, q_);
    }

    // All-to-all force calculation (GPU excels at this via tiling)
    void step(float dt, float kappa, float K_phi) {
        float* x = x_; float* p = p_; float* phi = phi_; float* omega = omega_;
        size_t n = count_;
        
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            int i = idx[0];
            float phi_i = phi[i];
            float coupling = 0.0f;
            
            for (int j = 0; j < (int)n; ++j) {
                coupling += sycl::sin(phi[j] - phi_i);
            }
            
            float dphi = omega[i] + (K_phi / (float)n) * coupling;
            
            x[i] += dt * p[i];
            p[i] -= dt * kappa * x[i];
            phi[i] += dt * dphi;
            phi[i] = sycl::fmod(phi[i], 2.0f * 3.1415926535f);
        }).wait();
    }

    float *x_, *p_, *phi_, *omega_;

private:
    size_t count_;
    sycl::queue q_;
};

} // namespace swarm
} // namespace dase
