/**
 * IGSOA Gravitational Wave Engine - Fractional Solver Module (SYCL Redesign)
 *
 * Implements Caputo fractional derivative with SOE optimization.
 * SYCL-native implementation for GPU acceleration.
 */

#pragma once

#include "../../uhd770_runtime.h"
#include <complex>
#include <vector>

namespace dase {
namespace igsoa {
namespace gw {

/**
 * SOE Kernel coefficients (Stored in USM for GPU access)
 */
struct SOEKernel {
    float* weights;
    float* exponents;
    int rank;

    SOEKernel(int r, sycl::queue& q);
    void free(sycl::queue& q);
};

/**
 * Fractional Solver (SYCL-native)
 */
class FractionalSolver {
public:
    explicit FractionalSolver(int num_points, int soe_rank, sycl::queue& q);
    ~FractionalSolver();

    // Disable copy
    FractionalSolver(const FractionalSolver&) = delete;
    FractionalSolver& operator=(const FractionalSolver&) = delete;

    /**
     * Update history states z_r(t) on GPU.
     * Uses ND-Range kernels.
     */
    void updateHistory(const std::complex<float>* field_values,
                      const std::complex<float>* field_second_time_derivatives,
                      const float* alpha_values,
                      float dt);

    /**
     * Compute fractional derivatives for all points.
     */
    void computeDerivatives(std::complex<float>* output, const float* alpha_values);

private:
    int num_points_;
    int soe_rank_;
    sycl::queue& q_;

    // USM Pointers
    // Shape: [num_points * soe_rank]
    std::complex<float>* history_states_;
    
    // Cached kernels for different alpha values
    // In SYCL, we might want to interpolate between kernels to avoid too many branches
    float* kernel_weights_all_;
    float* kernel_exponents_all_;
    int num_kernels_;

    void allocateMemory();
    void freeMemory();
};

} // namespace gw
} // namespace igsoa
} // namespace dase
