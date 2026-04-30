#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace ca {

/**
 * Intel UHD 770 SYCL Kernel for 2D Cellular Automata.
 * Optimized for Single Precision (FP32).
 */
class CAEngineSYCL {
public:
    CAEngineSYCL(int w, int h) : width_(w), height_(h), q_(sycl::default_selector_v) {
        int n = w * h;
        epsilon_ = sycl::malloc_shared<float>(n, q_);
        R_ = sycl::malloc_shared<float>(n, q_);
        next_epsilon_ = sycl::malloc_shared<float>(n, q_);
        std::cout << "CA SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~CAEngineSYCL() {
        sycl::free(epsilon_, q_);
        sycl::free(R_, q_);
        sycl::free(next_epsilon_, q_);
    }

    void step(float D, float delta_R, float gamma_R) {
        int w = width_;
        int h = height_;
        float* eps = epsilon_;
        float* next_eps = next_epsilon_;
        float* r = R_;

        // Gated Diffusion Kernel (Offloaded to GPU Execution Units)
        q_.parallel_for(sycl::range<2>(h - 2, w - 2), [=](sycl::id<2> idx) {
            int y = (int)idx[0] + 1;
            int x = (int)idx[1] + 1;
            int i = y * w + x;

            float curr = eps[i];
            float up = eps[i - w];
            float down = eps[i + w];
            float left = eps[i - 1];
            float right = eps[i + 1];

            float grad = sycl::fabs(curr - up) + sycl::fabs(curr - down) + 
                          sycl::fabs(curr - left) + sycl::fabs(curr - right);

            if (grad > r[i]) {
                float lap = up + down + left + right - 4.0f * curr;
                next_eps[i] = curr + D * lap;
            } else {
                next_eps[i] = curr;
            }
        }).wait();

        // Residue Update Kernel
        q_.parallel_for(sycl::range<1>(w * h), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            float diff = sycl::fabs(next_eps[i] - eps[i]);
            r[i] = r[i] * (1.0f - gamma_R) + (diff > 0.0f ? delta_R : 0.0f);
            eps[i] = next_eps[i]; // Swap
        }).wait();
    }

    float* epsilon_;
    float* R_;
    float* next_epsilon_;

private:
    int width_, height_;
    sycl::queue q_;
};

} // namespace ca
} // namespace dase
