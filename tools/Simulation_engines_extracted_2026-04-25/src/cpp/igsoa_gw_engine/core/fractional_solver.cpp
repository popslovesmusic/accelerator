#include "fractional_solver.h"
#include <cmath>

namespace dase {
namespace igsoa {
namespace gw {

SOEKernel::SOEKernel(int r, sycl::queue& q) : rank(r) {
    weights = sycl::malloc_shared<float>(rank, q);
    exponents = sycl::malloc_shared<float>(rank, q);
}

void SOEKernel::free(sycl::queue& q) {
    sycl::free(weights, q);
    sycl::free(exponents, q);
}

FractionalSolver::FractionalSolver(int num_points, int soe_rank, sycl::queue& q)
    : num_points_(num_points), soe_rank_(soe_rank), q_(q) {
    allocateMemory();
}

FractionalSolver::~FractionalSolver() {
    freeMemory();
}

void FractionalSolver::allocateMemory() {
    // Shape: [num_points * soe_rank]
    history_states_ = sycl::malloc_shared<std::complex<float>>(num_points_ * soe_rank_, q_);
    q_.fill(history_states_, std::complex<float>(0.0f, 0.0f), num_points_ * soe_rank_).wait();

    // For now, let's just use one kernel set (alpha=1.5 default)
    // In a full implementation, we would have a table of kernels for different alphas
    num_kernels_ = 1;
    kernel_weights_all_ = sycl::malloc_shared<float>(soe_rank_, q_);
    kernel_exponents_all_ = sycl::malloc_shared<float>(soe_rank_, q_);

    // Initialize with a standard alpha=1.5 kernel approximation
    for (int r = 0; r < soe_rank_; r++) {
        kernel_weights_all_[r] = 1.0f / soe_rank_;
        kernel_exponents_all_[r] = 0.1f * std::pow(10.0f, r / (float)soe_rank_);
    }
}

void FractionalSolver::freeMemory() {
    sycl::free(history_states_, q_);
    sycl::free(kernel_weights_all_, q_);
    sycl::free(kernel_exponents_all_, q_);
}

void FractionalSolver::updateHistory(const std::complex<float>* field_values,
                                    const std::complex<float>* field_second_time_derivatives,
                                    const float* alpha_values,
                                    float dt) {
    auto n = num_points_;
    auto rank = soe_rank_;
    auto history = history_states_;
    auto weights = kernel_weights_all_;
    auto exponents = kernel_exponents_all_;

    // ND-Range: [num_points]
    q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> id) {
        int i = id[0];
        // For each point, update all SOE terms
        for (int r = 0; r < rank; r++) {
            int h_idx = i * rank + r;
            float decay = sycl::exp(-exponents[r] * dt);
            // Recursive update: z_r(t+dt) = exp(-s_r dt) z_r(t) + w_r ∂²_t f(t) dt
            history[h_idx] = decay * history[h_idx] + weights[r] * field_second_time_derivatives[i] * dt;
        }
    }).wait();
}

void FractionalSolver::computeDerivatives(std::complex<float>* output, const float* alpha_values) {
    auto n = num_points_;
    auto rank = soe_rank_;
    auto history = history_states_;

    q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> id) {
        int i = id[0];
        std::complex<float> sum(0.0f, 0.0f);
        for (int r = 0; r < rank; r++) {
            sum += history[i * rank + r];
        }
        output[i] = sum;
    }).wait();
}

} // namespace gw
} // namespace igsoa
} // namespace dase
