#include "source_manager.h"
#include <cmath>

namespace dase {
namespace igsoa {
namespace gw {

BinaryMerger::BinaryMerger(const BinaryMergerConfig& config, sycl::queue& q)
    : config_(config), q_(q), current_phase_(config.initial_orbital_phase) {
    evolveOrbit(0.0f); // Set initial positions
}

BinaryMerger::~BinaryMerger() {}

void BinaryMerger::evolveOrbit(float dt) {
    // Simplified circular orbit evolution for the redesign
    // In a full implementation, this would involve Keplerian or Inspiral dynamics
    float omega = 0.1f; // Dummy angular velocity
    current_phase_ += omega * dt;

    float r = config_.initial_separation / 2.0f;
    pos1_ = Vector3D(config_.center.x + r * std::cos(current_phase_),
                     config_.center.y + r * std::sin(current_phase_),
                     config_.center.z);
    
    pos2_ = Vector3D(config_.center.x - r * std::cos(current_phase_),
                     config_.center.y - r * std::sin(current_phase_),
                     config_.center.z);
}

void BinaryMerger::generateSourceTerms(std::complex<float>* output,
                                      int nx, int ny, int nz,
                                      float dx, float dy, float dz,
                                      const Vector3D& grid_origin) {
    auto p1 = pos1_;
    auto p2 = pos2_;
    auto sigma2 = config_.gaussian_width * config_.gaussian_width;
    auto amplitude = config_.source_amplitude;

    q_.parallel_for(sycl::range<3>(nx, ny, nz), [=](sycl::id<3> id) {
        int i = id[0]; int j = id[1]; int k = id[2];
        int idx = i + j * nx + k * nx * ny;

        float x = grid_origin.x + i * dx;
        float y = grid_origin.y + j * dy;
        float z = grid_origin.z + k * dz;

        auto dist1_sq = (x - p1.x)*(x - p1.x) + (y - p1.y)*(y - p1.y) + (z - p1.z)*(z - p1.z);
        auto dist2_sq = (x - p2.x)*(x - p2.x) + (y - p2.y)*(y - p2.y) + (z - p2.z)*(z - p2.z);

        float s1 = amplitude * sycl::exp(-dist1_sq / (2.0f * sigma2));
        float s2 = amplitude * sycl::exp(-dist2_sq / (2.0f * sigma2));

        output[idx] = std::complex<float>(s1 + s2, 0.0f);
    }).wait();
}

} // namespace gw
} // namespace igsoa
} // namespace dase
