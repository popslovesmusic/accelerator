#include "symmetry_field.h"
#include <iostream>

namespace dase {
namespace igsoa {
namespace gw {

SymmetryField::SymmetryField(const SymmetryFieldConfig& config, sycl::queue& q)
    : config_(config), q_(q) {
    allocateMemory();
}

SymmetryField::~SymmetryField() {
    freeMemory();
}

void SymmetryField::allocateMemory() {
    size_t total = getTotalPoints();
    delta_phi_ = sycl::malloc_shared<std::complex<float>>(total, q_);
    alpha_values_ = sycl::malloc_shared<float>(total, q_);
    gradient_magnitude_ = sycl::malloc_shared<float>(total, q_);
    potential_ = sycl::malloc_shared<float>(total, q_);

    // Initialize
    q_.fill(delta_phi_, std::complex<float>(0.0f, 0.0f), total);
    q_.fill(alpha_values_, 2.0f, total); // Default: no memory
    q_.fill(gradient_magnitude_, 0.0f, total);
    q_.fill(potential_, 0.0f, total);
    q_.wait();
}

void SymmetryField::freeMemory() {
    sycl::free(delta_phi_, q_);
    sycl::free(alpha_values_, q_);
    sycl::free(gradient_magnitude_, q_);
    sycl::free(potential_, q_);
}

void SymmetryField::evolveStep(const std::complex<float>* fractional_derivatives,
                              const std::complex<float>* source_terms) {
    auto nx = config_.nx;
    auto ny = config_.ny;
    auto nz = config_.nz;
    auto dx2 = config_.dx * config_.dx;
    auto dy2 = config_.dy * config_.dy;
    auto dz2 = config_.dz * config_.dz;
    auto dt = config_.dt;
    auto lambda = config_.lambda;
    auto kappa = config_.kappa;

    auto phi = delta_phi_;
    auto potential = potential_;

    // ND-Range: [nx, ny, nz]
    // Local size: [sub_group_size, 1, 1] for X-dimension optimization
    const int sg_size = 16; 
    sycl::range<3> global_size(nx, ny, nz);
    sycl::range<3> local_size(sg_size, 1, 1);

    q_.submit([&](sycl::handler& h) {
        h.parallel_for(sycl::nd_range<3>(global_size, local_size), [=](sycl::nd_item<3> item) {
            auto sg = item.get_sub_group();
            int i = item.get_global_id(0);
            int j = item.get_global_id(1);
            int k = item.get_global_id(2);

            if (i <= 0 || i >= nx - 1 || j <= 0 || j >= ny - 1 || k <= 0 || k >= nz - 1) return;

            int idx = i + j * nx + k * nx * ny;

            // 1. Optimized Laplacian using Sub-Group Shuffles for X-axis
            std::complex<float> center = phi[idx];
            float r_center = center.real();
            float i_center = center.imag();
            
            // Sub-group shift for X +/- 1
            float r_xp = sycl::shift_group_left(sg, r_center, 1);
            float i_xp = sycl::shift_group_left(sg, i_center, 1);
            std::complex<float> phi_xp(r_xp, i_xp);
            if (sg.get_local_id()[0] == sg_size - 1) phi_xp = phi[idx + 1]; // Handle SG boundary

            float r_xm = sycl::shift_group_right(sg, r_center, 1);
            float i_xm = sycl::shift_group_right(sg, i_center, 1);
            std::complex<float> phi_xm(r_xm, i_xm);
            if (sg.get_local_id()[0] == 0) phi_xm = phi[idx - 1]; // Handle SG boundary

            std::complex<float> d2phidx2 = (phi_xp - 2.0f * center + phi_xm) / dx2;

            // Y and Z axes (global memory reads)
            std::complex<float> phi_yp = phi[idx + nx];
            std::complex<float> phi_ym = phi[idx - nx];
            std::complex<float> d2phidy2 = (phi_yp - 2.0f * center + phi_ym) / dy2;

            std::complex<float> phi_zp = phi[idx + nx * ny];
            std::complex<float> phi_zm = phi[idx - nx * ny];
            std::complex<float> d2phidz2 = (phi_zp - 2.0f * center + phi_zm) / dz2;

            std::complex<float> laplacian = d2phidx2 + d2phidy2 + d2phidz2;

            // 2. Potential & Physics
            float abs_phi_sq = std::norm(center);
            float V = lambda * abs_phi_sq + kappa * abs_phi_sq * abs_phi_sq;
            
            // 3. Update Equation: ∂²ₓ ψ - ₀D^α_t ψ - Vψ + S
            std::complex<float> frac_deriv = fractional_derivatives[idx];
            std::complex<float> source = source_terms[idx];
            
            std::complex<float> rhs = laplacian - frac_deriv - V * center + source;
            
            // Simple Forward Euler (as in original)
            phi[idx] = center + dt * rhs;
        });
    }).wait();
}

void SymmetryField::updateCaches() {
    // Porting the gradient/potential cache update to SYCL
    auto nx = config_.nx;
    auto ny = config_.ny;
    auto nz = config_.nz;
    auto phi = delta_phi_;
    auto potential = potential_;
    auto kappa = config_.kappa;
    auto lambda = config_.lambda;

    q_.parallel_for(sycl::range<3>(nx, ny, nz), [=](sycl::id<3> id) {
        int i = id[0]; int j = id[1]; int k = id[2];
        int idx = i + j * nx + k * nx * ny;
        
        float abs_phi_sq = std::norm(phi[idx]);
        potential[idx] = lambda * abs_phi_sq + kappa * abs_phi_sq * abs_phi_sq;
    }).wait();
}

void SymmetryField::copyToHost(std::vector<std::complex<float>>& host_phi) {
    q_.memcpy(host_phi.data(), delta_phi_, host_phi.size() * sizeof(std::complex<float>)).wait();
}

} // namespace gw
} // namespace igsoa
} // namespace dase
