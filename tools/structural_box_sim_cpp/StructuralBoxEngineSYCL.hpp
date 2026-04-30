#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>

namespace dase {
namespace structural_box {

template <typename T>
class StructuralBoxEngineSYCL {
public:
    StructuralBoxEngineSYCL(size_t nx, sycl::queue& q) : nx_(nx), q_(q) {
        epsilon = sycl::malloc_shared<T>(nx, q_);
        rho = sycl::malloc_shared<T>(nx, q_);
        residue = sycl::malloc_shared<T>(nx, q_);
        
        q_.fill(epsilon, static_cast<T>(0), nx);
        q_.fill(rho, static_cast<T>(0), nx);
        q_.fill(residue, static_cast<T>(0), nx).wait();
    }

    ~StructuralBoxEngineSYCL() {
        sycl::free(epsilon, q_);
        sycl::free(rho, q_);
        sycl::free(residue, q_);
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

        T* next_eps = sycl::malloc_shared<T>(nx, q_);
        T* next_rho = sycl::malloc_shared<T>(nx, q_);
        T* next_res = sycl::malloc_shared<T>(nx, q_);

        T inv_dx2 = 1.0f / (dx * dx);

        q_.parallel_for(sycl::range<1>(nx), [=](sycl::id<1> i) {
            size_t idx = i.get(0);
            
            // Neumann Boundary Conditions (Edge padding)
            size_t left = (idx == 0) ? 0 : idx - 1;
            size_t right = (idx == nx - 1) ? nx - 1 : idx + 1;

            T e = eps_ptr[idx];
            T r = rho_ptr[idx];
            T R = res_ptr[idx];

            T lapE = (eps_ptr[left] - 2.0f * e + eps_ptr[right]) * inv_dx2;
            T lapRho = (rho_ptr[left] - 2.0f * r + rho_ptr[right]) * inv_dx2;
            T lapR = (res_ptr[left] - 2.0f * R + res_ptr[right]) * inv_dx2;

            T de = D_epsilon * lapE + a * e - b * e * r - c * e * e + u * R + s;
            T dr = D_rho * lapRho + alpha * r - beta * e * r - gamma * r * r - v * R + h;
            T dR = D_R * lapR + kappa * e - lambda_R * R;

            next_eps[idx] = sycl::max(static_cast<T>(0), e + de * dt);
            next_rho[idx] = sycl::max(static_cast<T>(0), r + dr * dt);
            next_res[idx] = sycl::max(static_cast<T>(0), R + dR * dt);
        }).wait();

        q_.copy(next_eps, epsilon, nx).wait();
        q_.copy(next_rho, rho, nx).wait();
        q_.copy(next_res, residue, nx).wait();

        sycl::free(next_eps, q_);
        sycl::free(next_rho, q_);
        sycl::free(next_res, q_);
    }

    T* epsilon, *rho, *residue;

private:
    size_t nx_;
    sycl::queue& q_;
};

} // namespace structural_box
} // namespace dase
