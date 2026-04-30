#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>
#include "SATPHiggsParamsSYCL.hpp"

namespace dase {
namespace satp_higgs {

template <typename T>
class SATPHiggsEngine3DSYCL {
public:
    SATPHiggsEngine3DSYCL(size_t nx, size_t ny, size_t nz, sycl::queue& q) 
        : nx_(nx), ny_(ny), nz_(nz), q_(q) {
        
        size_t n = nx * ny * nz;
        phi = sycl::malloc_shared<T>(n, q_);
        phi_dot = sycl::malloc_shared<T>(n, q_);
        h = sycl::malloc_shared<T>(n, q_);
        h_dot = sycl::malloc_shared<T>(n, q_);
        
        q_.fill(phi, static_cast<T>(0), n);
        q_.fill(phi_dot, static_cast<T>(0), n);
        q_.fill(h, static_cast<T>(0), n);
        q_.fill(h_dot, static_cast<T>(0), n).wait();
    }

    ~SATPHiggsEngine3DSYCL() {
        sycl::free(phi, q_);
        sycl::free(phi_dot, q_);
        sycl::free(h, q_);
        sycl::free(h_dot, q_);
    }

    void initialize_vacuum(T h_vev) {
        size_t n = nx_ * ny_ * nz_;
        q_.fill(phi, static_cast<T>(0), n);
        q_.fill(phi_dot, static_cast<T>(0), n);
        q_.fill(h, h_vev, n);
        q_.fill(h_dot, static_cast<T>(0), n).wait();
    }

    void step(T dt, T dx, const SATPHiggsParamsSYCL<T>& params) {
        const size_t nx = nx_;
        const size_t ny = ny_;
        const size_t nz = nz_;
        auto phi_ptr = phi;
        auto phi_dot_ptr = phi_dot;
        auto h_ptr = h;
        auto h_dot_ptr = h_dot;

        const T c_sq = params.c * params.c;
        const T dx_sq = dx * dx;
        const T inv_dx_sq = static_cast<T>(1.0) / dx_sq;
        const T gamma_phi = params.gamma_phi;
        const T gamma_h = params.gamma_h;
        const T lambda = params.lambda;
        const T mu_sq = params.mu_squared;
        const T lambda_h = params.lambda_h;

        size_t n_total = nx * ny * nz;

        // Intermediate buffers for Velocity Verlet
        T* next_phi = sycl::malloc_shared<T>(n_total, q_);
        T* next_h = sycl::malloc_shared<T>(n_total, q_);
        T* next_phi_dot = sycl::malloc_shared<T>(n_total, q_);
        T* next_h_dot = sycl::malloc_shared<T>(n_total, q_);

        // Step 1: Compute accelerations and update positions
        q_.parallel_for(sycl::range<3>(nz, ny, nx), [=](sycl::id<3> it) {
            size_t iz = it[0];
            size_t iy = it[1];
            size_t ix = it[2];
            size_t idx = iz * (nx * ny) + iy * nx + ix;

            // Periodic neighbors
            size_t zm = (iz == 0) ? nz - 1 : iz - 1;
            size_t zp = (iz == nz - 1) ? 0 : iz + 1;
            size_t ym = (iy == 0) ? ny - 1 : iy - 1;
            size_t yp = (iy == ny - 1) ? 0 : iy + 1;
            size_t xm = (ix == 0) ? nx - 1 : ix - 1;
            size_t xp = (ix == nx - 1) ? 0 : ix + 1;

            T p = phi_ptr[idx];
            T pd = phi_dot_ptr[idx];
            T hv = h_ptr[idx];
            T hd = h_dot_ptr[idx];

            // 3D Laplacian (7-point)
            T lapP = (phi_ptr[iz * nx * ny + iy * nx + xm] + phi_ptr[iz * nx * ny + iy * nx + xp] +
                      phi_ptr[iz * nx * ny + ym * nx + ix] + phi_ptr[iz * nx * ny + yp * nx + ix] +
                      phi_ptr[zm * nx * ny + iy * nx + ix] + phi_ptr[zp * nx * ny + iy * nx + ix] -
                      static_cast<T>(6.0) * p) * inv_dx_sq;

            T lapH = (h_ptr[iz * nx * ny + iy * nx + xm] + h_ptr[iz * nx * ny + iy * nx + xp] +
                      h_ptr[iz * nx * ny + ym * nx + ix] + h_ptr[iz * nx * ny + yp * nx + ix] +
                      h_ptr[zm * nx * ny + iy * nx + ix] + h_ptr[zp * nx * ny + iy * nx + ix] -
                      static_cast<T>(6.0) * hv) * inv_dx_sq;

            // Accelerations at t
            T accP = c_sq * lapP - gamma_phi * pd - static_cast<T>(2.0) * lambda * p * hv * hv;
            T accH = c_sq * lapH - gamma_h * hd - static_cast<T>(2.0) * mu_sq * hv - static_cast<T>(4.0) * lambda_h * hv * hv * hv - static_cast<T>(2.0) * lambda * p * p * hv;

            // Update positions and half-step velocities
            next_phi[idx] = p + pd * dt + static_cast<T>(0.5) * accP * dt * dt;
            next_h[idx] = hv + hd * dt + static_cast<T>(0.5) * accH * dt * dt;
            next_phi_dot[idx] = pd + static_cast<T>(0.5) * accP * dt;
            next_h_dot[idx] = hd + static_cast<T>(0.5) * accH * dt;
        }).wait();

        // Step 2: Full velocity update
        q_.parallel_for(sycl::range<3>(nz, ny, nx), [=](sycl::id<3> it) {
            size_t iz = it[0];
            size_t iy = it[1];
            size_t ix = it[2];
            size_t idx = iz * (nx * ny) + iy * nx + ix;

            size_t zm = (iz == 0) ? nz - 1 : iz - 1;
            size_t zp = (iz == nz - 1) ? 0 : iz + 1;
            size_t ym = (iy == 0) ? ny - 1 : iy - 1;
            size_t yp = (iy == ny - 1) ? 0 : iy + 1;
            size_t xm = (ix == 0) ? nx - 1 : ix - 1;
            size_t xp = (ix == nx - 1) ? 0 : ix + 1;

            T p = next_phi[idx];
            T hv = next_h[idx];

            T lapP = (next_phi[iz * nx * ny + iy * nx + xm] + next_phi[iz * nx * ny + iy * nx + xp] +
                      next_phi[iz * nx * ny + ym * nx + ix] + next_phi[iz * nx * ny + yp * nx + ix] +
                      next_phi[zm * nx * ny + iy * nx + ix] + next_phi[zp * nx * ny + iy * nx + ix] -
                      static_cast<T>(6.0) * p) * inv_dx_sq;

            T lapH = (next_h[iz * nx * ny + iy * nx + xm] + next_h[iz * nx * ny + iy * nx + xp] +
                      next_h[iz * nx * ny + ym * nx + ix] + next_h[iz * nx * ny + yp * nx + ix] +
                      next_h[zm * nx * ny + iy * nx + ix] + next_h[zp * nx * ny + iy * nx + ix] -
                      static_cast<T>(6.0) * hv) * inv_dx_sq;

            T accP_new = c_sq * lapP - gamma_phi * next_phi_dot[idx] - static_cast<T>(2.0) * lambda * p * hv * hv;
            T accH_new = c_sq * lapH - gamma_h * next_h_dot[idx] - static_cast<T>(2.0) * mu_sq * hv - static_cast<T>(4.0) * lambda_h * hv * hv * hv - static_cast<T>(2.0) * lambda * p * p * hv;

            next_phi_dot[idx] += static_cast<T>(0.5) * accP_new * dt;
            next_h_dot[idx] += static_cast<T>(0.5) * accH_new * dt;
        }).wait();

        q_.copy(next_phi, phi, n_total);
        q_.copy(next_h, h, n_total);
        q_.copy(next_phi_dot, phi_dot, n_total);
        q_.copy(next_h_dot, h_dot, n_total).wait();

        sycl::free(next_phi, q_);
        sycl::free(next_h, q_);
        sycl::free(next_phi_dot, q_);
        sycl::free(next_h_dot, q_);
    }

    T *phi, *phi_dot, *h, *h_dot;

private:
    size_t nx_, ny_, nz_;
    sycl::queue& q_;
};

} // namespace satp_higgs
} // namespace dase
