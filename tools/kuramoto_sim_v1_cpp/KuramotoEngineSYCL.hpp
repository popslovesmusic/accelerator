#pragma once
#include <sycl/sycl.hpp>
#include <iostream>
#include <cmath>

namespace dase {
namespace kuramoto {

/**
 * GPU-Accelerated Kuramoto Model using SYCL (oneAPI).
 * Optimized for Intel UHD 770 (FP32).
 * 1D Ring Coupling.
 */
class KuramotoEngineSYCL {
public:
    KuramotoEngineSYCL(size_t n) : count_(n), q_(sycl::default_selector_v) {
        phi = sycl::malloc_shared<float>(n, q_);
        omega = sycl::malloc_shared<float>(n, q_);
        
        // Intermediate buffers for RK4
        k1 = sycl::malloc_shared<float>(n, q_);
        k2 = sycl::malloc_shared<float>(n, q_);
        k3 = sycl::malloc_shared<float>(n, q_);
        k4 = sycl::malloc_shared<float>(n, q_);
        temp_phi = sycl::malloc_shared<float>(n, q_);

        std::cout << "Kuramoto SYCL Engine Initialized on: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << std::endl;
    }

    ~KuramotoEngineSYCL() {
        sycl::free(phi, q_);
        sycl::free(omega, q_);
        sycl::free(k1, q_);
        sycl::free(k2, q_);
        sycl::free(k3, q_);
        sycl::free(k4, q_);
        sycl::free(temp_phi, q_);
    }

    /**
     * GPU Kernel for Derivatives: dphi = omega + K * (sin(phi_next - phi) + sin(phi_prev - phi))
     */
    void compute_derivatives(const float* p_in, float* d_out, float K) {
        const size_t n = count_;
        auto p_ptr = p_in;
        auto d_ptr = d_out;
        auto o_ptr = omega;

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            int next = (i + 1) % n;
            int prev = (i - 1 + n) % n;

            float phi_curr = p_ptr[i];
            float coupling = sycl::sin(p_ptr[next] - phi_curr) + sycl::sin(p_ptr[prev] - phi_curr);
            d_ptr[i] = o_ptr[i] + K * coupling;
        }).wait();
    }

    /**
     * RK4 Step implementation on GPU
     */
    void step_rk4(float dt, float K) {
        const size_t n = count_;
        
        // k1 = f(phi, t)
        compute_derivatives(phi, k1, K);

        // k2 = f(phi + 0.5*dt*k1, t + 0.5*dt)
        auto p_ptr = phi;
        auto k1_ptr = k1;
        auto tp_ptr = temp_phi;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            tp_ptr[idx] = p_ptr[idx] + 0.5f * dt * k1_ptr[idx];
        }).wait();
        compute_derivatives(temp_phi, k2, K);

        // k3 = f(phi + 0.5*dt*k2, t + 0.5*dt)
        auto k2_ptr = k2;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            tp_ptr[idx] = p_ptr[idx] + 0.5f * dt * k2_ptr[idx];
        }).wait();
        compute_derivatives(temp_phi, k3, K);

        // k4 = f(phi + dt*k3, t + dt)
        auto k3_ptr = k3;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            tp_ptr[idx] = p_ptr[idx] + dt * k3_ptr[idx];
        }).wait();
        compute_derivatives(temp_phi, k4, K);

        // phi = phi + (dt/6) * (k1 + 2k2 + 2k3 + k4)
        auto k4_ptr = k4;
        const float TWO_PI = 6.28318530718f;
        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            float delta = (dt / 6.0f) * (k1_ptr[idx] + 2.0f * k2_ptr[idx] + 2.0f * k3_ptr[idx] + k4_ptr[idx]);
            float new_phi = p_ptr[idx] + delta;
            
            // Wrap to [0, 2pi]
            new_phi = sycl::fmod(new_phi, TWO_PI);
            if (new_phi < 0) new_phi += TWO_PI;
            p_ptr[idx] = new_phi;
        }).wait();
    }

    /**
     * Compute Global Order Parameter R on Host (from USM data)
     */
    float compute_order_parameter() {
        float sum_cos = 0.0f;
        float sum_sin = 0.0f;
        for (size_t i = 0; i < count_; ++i) {
            sum_cos += std::cos(phi[i]);
            sum_sin += std::sin(phi[i]);
        }
        float r_cos = sum_cos / count_;
        float r_sin = sum_sin / count_;
        return std::sqrt(r_cos * r_cos + r_sin * r_sin);
    }

    float *phi, *omega;
    float *k1, *k2, *k3, *k4, *temp_phi;

private:
    size_t count_;
    sycl::queue q_;
};

} // namespace kuramoto
} // namespace dase
