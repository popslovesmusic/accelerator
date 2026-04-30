#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>

namespace dase {
namespace rd {

template <typename T>
class RDEngineSYCL {
public:
    RDEngineSYCL(size_t size, sycl::queue& q) : size_(size), q_(q) {
        D = sycl::malloc_shared<T>(size * size, q_);
        S = sycl::malloc_shared<T>(size * size, q_);
        
        q_.fill(D, static_cast<T>(0), size * size).wait();
        q_.fill(S, static_cast<T>(0), size * size).wait();
    }

    ~RDEngineSYCL() {
        sycl::free(D, q_);
        sycl::free(S, q_);
    }

    void initialize_source(size_t px, size_t py, T radius) {
        const size_t n = size_;
        auto D_ptr = D;
        q_.parallel_for(sycl::range<2>(n, n), [=](sycl::id<2> it) {
            size_t y = it[0];
            size_t x = it[1];
            T dx = static_cast<T>(x) - static_cast<T>(px);
            T dy = static_cast<T>(y) - static_cast<T>(py);
            if (dx * dx + dy * dy <= radius * radius) {
                D_ptr[y * n + x] = 1.0;
            }
        }).wait();
    }

    void step(T dt, T D_diff, T S_diff, T beta, T theta_g, T gamma, T alpha, T source_strength, size_t px, size_t py, T radius) {
        const size_t n = size_;
        auto D_ptr = D;
        auto S_ptr = S;
        
        // Allocate temp buffers for updates to ensure consistency within the step
        T* next_D = sycl::malloc_shared<T>(n * n, q_);
        T* next_S = sycl::malloc_shared<T>(n * n, q_);

        q_.parallel_for(sycl::range<2>(n, n), [=](sycl::id<2> it) {
            size_t y = it[0];
            size_t x = it[1];
            size_t idx = y * n + x;

            // Periodic boundary indices
            size_t up = (y == 0) ? n - 1 : y - 1;
            size_t down = (y == n - 1) ? 0 : y + 1;
            size_t left = (x == 0) ? n - 1 : x - 1;
            size_t right = (x == n - 1) ? 0 : x + 1;

            // 1. Laplacian(D)
            T lapD = D_ptr[up * n + x] + D_ptr[down * n + x] + D_ptr[y * n + left] + D_ptr[y * n + right] - 4 * D_ptr[idx];
            
            // 2. Channeled Divergence div(D * grad S)
            T S_val = S_ptr[idx];
            T S_up = S_ptr[up * n + x];
            T S_down = S_ptr[down * n + x];
            T S_left = S_ptr[y * n + left];
            T S_right = S_ptr[y * n + right];

            T D_val = D_ptr[idx];
            T D_up = D_ptr[up * n + x];
            T D_down = D_ptr[down * n + x];
            T D_left = D_ptr[y * n + left];
            T D_right = D_ptr[y * n + right];

            T flux_r = 0.5f * (D_val + D_right) * (S_right - S_val);
            T flux_l = 0.5f * (D_val + D_left) * (S_val - S_left);
            T flux_d = 0.5f * (D_val + D_down) * (S_down - S_val);
            T flux_u = 0.5f * (D_val + D_up) * (S_val - S_up);

            T div_term = (flux_r - flux_l) + (flux_d - flux_u);

            // Update D
            T grad_term = beta * D_val * (static_cast<T>(1.0) - D_val) * (S_val - theta_g);
            T dD = D_diff * lapD + grad_term - gamma * D_val;
            next_D[idx] = sycl::clamp(D_val + dD * dt, static_cast<T>(0.0), static_cast<T>(1.0));

            // Update S
            T source = 0;
            T dx = static_cast<T>(x) - static_cast<T>(px);
            T dy = static_cast<T>(y) - static_cast<T>(py);
            if (dx * dx + dy * dy <= radius * radius) {
                source = source_strength;
            }
            T dS = S_diff * div_term + source - alpha * S_val;
            next_S[idx] = sycl::max(static_cast<T>(0.0), S_val + dS * dt);

        }).wait();

        q_.copy(next_D, D, n * n).wait();
        q_.copy(next_S, S, n * n).wait();

        sycl::free(next_D, q_);
        sycl::free(next_S, q_);
    }

    T* D, *S;

private:
    size_t size_;
    sycl::queue& q_;
};

} // namespace rd
} // namespace dase
