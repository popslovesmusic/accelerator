#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>

namespace dase {
namespace stochastic {

// Simple PRNG for kernels (MWC or XORShift)
struct KernelPRNG {
    uint32_t state;
    
    KernelPRNG(uint32_t seed, uint32_t id) : state(seed ^ id) {}

    uint32_t next() {
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        return state;
    }

    float next_float() {
        return static_cast<float>(next()) / static_cast<float>(0xFFFFFFFF);
    }

    // Box-Muller transform for Gaussian noise
    float next_gaussian() {
        float u1 = next_float();
        float u2 = next_float();
        if (u1 < 1e-7f) u1 = 1e-7f; // Avoid log(0)
        return sycl::sqrt(-2.0f * sycl::log(u1)) * sycl::cos(2.0f * 3.14159265f * u2);
    }
};

template <typename T>
class StochasticEngineSYCL {
public:
    StochasticEngineSYCL(size_t n, sycl::queue& q) : count_(n), q_(q) {
        x = sycl::malloc_shared<T>(n, q_);
        onset_times = sycl::malloc_shared<T>(n, q_);
        has_crossed = sycl::malloc_shared<bool>(n, q_);
        
        q_.fill(onset_times, static_cast<T>(-1.0), n);
        q_.fill(has_crossed, false, n).wait();
    }

    ~StochasticEngineSYCL() {
        sycl::free(x, q_);
        sycl::free(onset_times, q_);
        sycl::free(has_crossed, q_);
    }

    void initialize(T initial_x) {
        q_.fill(x, initial_x, count_).wait();
    }

    void step(T dt, T kappa, T sigma, T x_thresh, T current_time, uint32_t seed) {
        const size_t n = count_;
        auto x_ptr = x;
        auto onset_ptr = onset_times;
        auto crossed_ptr = has_crossed;

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            uint32_t idx = static_cast<uint32_t>(i.get(0));
            KernelPRNG prng(seed, idx);

            T x_val = x_ptr[idx];
            
            // Euler-Maruyama: dx = -kappa * x * dt + sigma * dW
            T force = -kappa * x_val;
            T dW = static_cast<T>(prng.next_gaussian() * sycl::sqrt(static_cast<float>(dt)));
            
            x_val += force * dt + sigma * dW;
            x_ptr[idx] = x_val;

            // Threshold detection
            if (x_val >= x_thresh && !crossed_ptr[idx]) {
                crossed_ptr[idx] = true;
                onset_ptr[idx] = current_time;
            }
        }).wait();
    }

    T* x;
    T* onset_times;
    bool* has_crossed;

private:
    size_t count_;
    sycl::queue& q_;
};

} // namespace stochastic
} // namespace dase
