#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>
#include <cstdint>

namespace dase {
namespace structural_box {

template <typename T>
class StructuralBoxEngineSYCL {
public:
    StructuralBoxEngineSYCL(size_t nx, sycl::queue& q) : nx_(nx), q_(q) {
        epsilon = sycl::malloc_shared<T>(nx, q_);
        rho = sycl::malloc_shared<T>(nx, q_);
        residue = sycl::malloc_shared<T>(nx, q_);
        
        next_eps_ = sycl::malloc_shared<T>(nx, q_);
        next_rho_ = sycl::malloc_shared<T>(nx, q_);
        next_res_ = sycl::malloc_shared<T>(nx, q_);
        
        q_.fill(epsilon, static_cast<T>(0), nx);
        q_.fill(rho, static_cast<T>(0), nx);
        q_.fill(residue, static_cast<T>(0), nx).wait();
    }

    ~StructuralBoxEngineSYCL() {
        sycl::free(epsilon, q_);
        sycl::free(rho, q_);
        sycl::free(residue, q_);
        sycl::free(next_eps_, q_);
        sycl::free(next_rho_, q_);
        sycl::free(next_res_, q_);
    }

    void initialize_gaussian(T base, T amplitude, T sigma, T offset, T length) {
        const size_t nx = nx_;
        auto eps_ptr = epsilon;
        T dx = length / nx;
        q_.parallel_for(sycl::range<1>(nx), [=](sycl::id<1> i) {
            size_t idx = i.get(0);
            T x = static_cast<T>(idx) * dx - static_cast<T>(0.5) * length;
            T r2 = (x - offset) * (x - offset);
            eps_ptr[idx] = base + amplitude * sycl::exp(-static_cast<T>(0.5) * r2 / (sigma * sigma));
        }).wait();
    }

    void initialize_noise(T base, T noise_std, int seed) {
        const size_t nx = nx_;
        auto eps_ptr = epsilon;
        q_.parallel_for(sycl::range<1>(nx), [=](sycl::id<1> i) {
            size_t idx = i.get(0);
            // Simple hash for deterministic noise per index
            uint32_t x = static_cast<uint32_t>(idx) + static_cast<uint32_t>(seed) + 1;
            x = ((x >> 16) ^ x) * 0x45d9f3b;
            x = ((x >> 16) ^ x) * 0x45d9f3b;
            x = (x >> 16) ^ x;
            float norm = static_cast<float>(x) / 4294967295.0f; // / 2^32-1
            eps_ptr[idx] = base + static_cast<T>(norm - 0.5f) * noise_std;
        }).wait();
    }

    void initialize_uniform(T* field, T base) {
        q_.fill(field, base, nx_).wait();
    }

    void step(T dt, T dx, 
              T D_epsilon, T D_rho, T D_R,
              T a, T b, T c, T u, T s,
              T alpha, T beta, T gamma, T v, T h,
              T kappa, T lambda_R) {
        const size_t nx = nx_;
        auto eps_ptr = epsilon;
        auto rho_ptr = rho;
        auto res_ptr = residue;

        auto n_eps = next_eps_;
        auto n_rho = next_rho_;
        auto n_res = next_res_;

        T inv_dx2 = static_cast<T>(1.0) / (dx * dx);

        q_.parallel_for(sycl::range<1>(nx), [=](sycl::id<1> i) {
            size_t idx = i.get(0);
            
            // Neumann Boundary Conditions (Edge padding)
            size_t left = (idx == 0) ? 0 : idx - 1;
            size_t right = (idx == nx - 1) ? nx - 1 : idx + 1;

            T e = eps_ptr[idx];
            T r = rho_ptr[idx];
            T R = res_ptr[idx];

            T lapE = (eps_ptr[left] - static_cast<T>(2.0) * e + eps_ptr[right]) * inv_dx2;
            T lapRho = (rho_ptr[left] - static_cast<T>(2.0) * r + rho_ptr[right]) * inv_dx2;
            T lapR = (res_ptr[left] - static_cast<T>(2.0) * R + res_ptr[right]) * inv_dx2;

            T de = D_epsilon * lapE + a * e - b * e * r - c * e * e + u * R + s;
            T dr = D_rho * lapRho + alpha * r - beta * e * r - gamma * r * r - v * R + h;
            T dR = D_R * lapR + kappa * e - lambda_R * R;

            n_eps[idx] = sycl::max(static_cast<T>(0), e + de * dt);
            n_rho[idx] = sycl::max(static_cast<T>(0), r + dr * dt);
            n_res[idx] = sycl::max(static_cast<T>(0), R + dR * dt);
        }).wait();

        q_.copy(n_eps, epsilon, nx).wait();
        q_.copy(n_rho, rho, nx).wait();
        q_.copy(n_res, residue, nx).wait();
    }

    T* epsilon, *rho, *residue;

private:
    size_t nx_;
    sycl::queue& q_;
    T* next_eps_, *next_rho_, *next_res_;
};

} // namespace structural_box
} // namespace dase
