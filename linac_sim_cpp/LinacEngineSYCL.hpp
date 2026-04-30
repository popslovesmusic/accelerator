#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>
#include "LinacLatticeElements.h"

namespace dase {
namespace linac {

const float SPEED_OF_LIGHT = 299792458.0f;
const double SPEED_OF_LIGHT_D = 299792458.0;

struct SimulationMetrics {
    float exclusion_rate_k;
    float alignment_success_rate;
    float emittance_y_rms;
    float emittance_z_rms;
};

template <typename T>
class LinacEngineSYCL {
public:
    LinacEngineSYCL(size_t n, sycl::queue& q) : count_(n), q_(q) {
        x = sycl::malloc_shared<T>(n, q_);
        px = sycl::malloc_shared<T>(n, q_);
        y = sycl::malloc_shared<T>(n, q_);
        py = sycl::malloc_shared<T>(n, q_);
        z = sycl::malloc_shared<T>(n, q_);
        pz = sycl::malloc_shared<T>(n, q_);
        alive = sycl::malloc_shared<bool>(n, q_);
        
        // Initialize as alive
        q_.fill(alive, true, n).wait();
    }

    ~LinacEngineSYCL() {
        sycl::free(x, q_);
        sycl::free(px, q_);
        sycl::free(y, q_);
        sycl::free(py, q_);
        sycl::free(z, q_);
        sycl::free(pz, q_);
        sycl::free(alive, q_);
    }

    void step(T dt, T time, const ComponentData* lattice, size_t lattice_size, T mass, T charge, T aperture_radius) {
        const size_t n = count_;
        auto x_ptr = x;
        auto px_ptr = px;
        auto y_ptr = y;
        auto py_ptr = py;
        auto z_ptr = z;
        auto pz_ptr = pz;
        auto alive_ptr = alive;

        T c = static_cast<T>(SPEED_OF_LIGHT_D);

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) {
            if (!alive_ptr[i]) return;

            // Find current component
            const ComponentData* current = nullptr;
            for (size_t j = 0; j < lattice_size; ++j) {
                if (x_ptr[i] >= lattice[j].start_m && x_ptr[i] < (lattice[j].start_m + lattice[j].length_m)) {
                    current = &lattice[j];
                    break;
                }
            }

            T field = 0;
            T ky = 0;
            T kz = 0;

            if (current) {
                if (current->type == ComponentType::RF_GAP) {
                    T omega = 2.0f * 3.1415926535f * current->frequency_hz;
                    field = current->peak_field_v_per_m * sycl::sin(omega * time + current->phase_rad);
                } else if (current->type == ComponentType::FOCUSING_LENS) {
                    ky = current->focusing_strength_1_per_m2;
                    kz = current->z_focusing_strength_1_per_m2;
                }
            }

            // Relativistic dynamics
            T p_total_sq = px_ptr[i] * px_ptr[i] + py_ptr[i] * py_ptr[i] + pz_ptr[i] * pz_ptr[i];
            T mc = mass * c;
            T gamma = sycl::sqrt(1.0f + p_total_sq / (mc * mc));
            T v_long = px_ptr[i] / (gamma * mass);
            T v_y = py_ptr[i] / (gamma * mass);
            T v_z = pz_ptr[i] / (gamma * mass);

            // Momentum updates
            px_ptr[i] += charge * field * dt;
            py_ptr[i] += -ky * px_ptr[i] * v_long * y_ptr[i] * dt;
            pz_ptr[i] += -kz * px_ptr[i] * v_long * z_ptr[i] * dt;

            // Position updates
            x_ptr[i] += v_long * dt;
            y_ptr[i] += v_y * dt;
            z_ptr[i] += v_z * dt;

            // Aperture check
            if (sycl::sqrt(y_ptr[i] * y_ptr[i] + z_ptr[i] * z_ptr[i]) > aperture_radius) {
                alive_ptr[i] = false;
            }
            if (x_ptr[i] < -0.1f) {
                alive_ptr[i] = false;
            }
        }).wait();
    }

    T* x, *px, *y, *py, *z, *pz;
    bool* alive;

private:
    size_t count_;
    sycl::queue& q_;
};

} // namespace linac
} // namespace dase
