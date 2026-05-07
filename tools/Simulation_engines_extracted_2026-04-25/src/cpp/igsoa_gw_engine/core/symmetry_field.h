/**
 * IGSOA Gravitational Wave Engine - Symmetry Field Module (SYCL Redesign)
 *
 * Highly optimized SYCL implementation for UHD 770.
 * Uses ND-Range and Sub-Groups for stencil performance.
 */

#pragma once

#include "../../uhd770_runtime.h"
#include <complex>
#include <vector>

namespace dase {
namespace igsoa {
namespace gw {

/**
 * 3D Vector for spatial coordinates (SYCL compatible)
 */
struct Vector3D {
    float x, y, z; // Switching to float for UHD 770 optimization

    Vector3D() : x(0), y(0), z(0) {}
    Vector3D(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}
};

/**
 * Configuration for symmetry field grid
 */
struct SymmetryFieldConfig {
    int nx, ny, nz;
    float dx, dy, dz;
    float kappa;
    float lambda;
    float dt;

    SymmetryFieldConfig()
        : nx(64), ny(64), nz(64)
        , dx(1000.0f), dy(1000.0f), dz(1000.0f)
        , kappa(1.0f), lambda(0.1f), dt(0.01f) {}
};

/**
 * Main symmetry field class (SYCL-native)
 */
class SymmetryField {
public:
    explicit SymmetryField(const SymmetryFieldConfig& config, sycl::queue& q);
    ~SymmetryField();

    // Disable copy
    SymmetryField(const SymmetryField&) = delete;
    SymmetryField& operator=(const SymmetryField&) = delete;

    // === GPU Data Access (USM) ===
    std::complex<float>* getDeltaPhiPtr() { return delta_phi_; }
    float* getAlphaPtr() { return alpha_values_; }
    float* getPotentialPtr() { return potential_; }

    // === Spatial Operations (Kernels) ===
    void updateCaches();
    
    /**
     * Advance field using ND-Range kernels with Sub-Group optimizations.
     */
    void evolveStep(const std::complex<float>* fractional_derivatives,
                   const std::complex<float>* source_terms);

    // === Host Sync ===
    void copyToHost(std::vector<std::complex<float>>& host_phi);

    int getTotalPoints() const { return config_.nx * config_.ny * config_.nz; }

private:
    SymmetryFieldConfig config_;
    sycl::queue& q_;

    // USM Pointers (Shared for easy host/device access)
    std::complex<float>* delta_phi_;
    float* alpha_values_;
    float* gradient_magnitude_;
    float* potential_;

    void allocateMemory();
    void freeMemory();
};

} // namespace gw
} // namespace igsoa
} // namespace dase
