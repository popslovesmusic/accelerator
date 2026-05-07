/**
 * IGSOA Gravitational Wave Engine - Binary Merger Source Manager (SYCL Redesign)
 */

#pragma once

#include "symmetry_field.h"
#include <complex>
#include <vector>

namespace dase {
namespace igsoa {
namespace gw {

struct BinaryMergerConfig {
    float mass1, mass2;
    float initial_separation;
    float initial_orbital_phase;
    Vector3D center;
    float gaussian_width;
    float source_amplitude;
    bool enable_inspiral;

    BinaryMergerConfig()
        : mass1(30.0f), mass2(30.0f)
        , initial_separation(200e3f)
        , initial_orbital_phase(0.0f)
        , center(0, 0, 0)
        , gaussian_width(5e3f)
        , source_amplitude(1.0f)
        , enable_inspiral(false) {}
};

class BinaryMerger {
public:
    explicit BinaryMerger(const BinaryMergerConfig& config, sycl::queue& q);
    ~BinaryMerger();

    void evolveOrbit(float dt);

    /**
     * Compute source terms S(x,t) directly into GPU USM buffer.
     */
    void generateSourceTerms(std::complex<float>* output,
                            int nx, int ny, int nz,
                            float dx, float dy, float dz,
                            const Vector3D& grid_origin);

private:
    BinaryMergerConfig config_;
    sycl::queue& q_;

    // Current orbital state
    Vector3D pos1_, pos2_;
    float current_phase_;
};

} // namespace gw
} // namespace igsoa
} // namespace dase
