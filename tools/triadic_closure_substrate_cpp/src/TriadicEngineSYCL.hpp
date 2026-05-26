#pragma once
#include <sycl/sycl.hpp>
#include <iostream>
#include <vector>

// Share the struct definition if possible, but for simplicity in a header-only kernel:
// (Usually this would be in a shared common.hpp)
constexpr int BLOCK_SIZE_SYCL = 256;

struct alignas(32) UnitBlockSOA_SYCL {
    float in_channel[4][BLOCK_SIZE_SYCL];
    float out_channel[4][BLOCK_SIZE_SYCL];
    float coupling_channel[4][BLOCK_SIZE_SYCL];
    float residue[BLOCK_SIZE_SYCL];
    float residue_buffer[BLOCK_SIZE_SYCL];
    float orientation_vector[BLOCK_SIZE_SYCL];
    float closure_strength[BLOCK_SIZE_SYCL];
    float detectable_mismatch[BLOCK_SIZE_SYCL];
    int collapse_flag[BLOCK_SIZE_SYCL];
    float dynamic_window_low[BLOCK_SIZE_SYCL];
    float dynamic_window_high[BLOCK_SIZE_SYCL];
    float neighbor_weight_prev[BLOCK_SIZE_SYCL];
    float neighbor_weight_next[BLOCK_SIZE_SYCL];
    float persistence_score[BLOCK_SIZE_SYCL];
    float inside_admissibility_rate[BLOCK_SIZE_SYCL];
    float identity_signature[BLOCK_SIZE_SYCL];
};

namespace dase {
namespace triadic {

class TriadicEngineSYCL {
public:
    TriadicEngineSYCL(int num_blocks, sycl::queue q) : num_blocks_(num_blocks), q_(q) {
        std::cout << "Triadic Substrate SYCL Engine bound to: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    void process_global_coupling(UnitBlockSOA_SYCL* blocks, float coupling_strength, float residue_diffusion_rate, float dt, bool coupling_nullify, bool coupling_symmetry, bool boundary_randomize) {
        int nb = num_blocks_;
        if (coupling_nullify) return;

        // Kernel Pass: Diffusion + Coupling
        q_.parallel_for(sycl::range<1>(nb), [=](sycl::id<1> b_idx) {
            int b = (int)b_idx[0];
            
            // Boundary Randomization
            if (boundary_randomize && (b == 0 || b == nb - 1)) {
                // We use a pseudo-random value based on id and timestamp proxy (not perfect in SYCL without generator)
                // For simplicity, we just zero it out or use a deterministic noise proxy
                blocks[b].in_channel[0][0] = 0.0f; // Placeholder for now
            }

            int prev = (b == 0) ? nb - 1 : b - 1;
            int next = (b == nb - 1) ? 0 : b + 1;
            
            UnitBlockSOA_SYCL& curr = blocks[b];
            UnitBlockSOA_SYCL& p = blocks[prev];
            UnitBlockSOA_SYCL& n = blocks[next];

            for (int i = 0; i < BLOCK_SIZE_SYCL; ++i) {
                // 1. Residue Diffusion
                float d = (p.residue[i] + n.residue[i] - 2.0f * curr.residue[i]);
                curr.residue_buffer[i] = curr.residue[i] + d * residue_diffusion_rate;

                if (curr.collapse_flag[i]) continue;

                // 2. Global Coupling
                float w_prev = curr.neighbor_weight_prev[i];
                float w_next = curr.neighbor_weight_next[i];
                if (coupling_symmetry) w_prev = w_next = 1.0f;

                float coupling_factor = curr.residue[i] * coupling_strength;
                float delta = (p.out_channel[0][i] * w_prev + n.out_channel[0][i] * w_next) * coupling_factor;
                
                curr.coupling_channel[0][i] = delta;
                curr.in_channel[0][i] += delta * dt;
            }
        }).wait();

        // Buffer Swap Pass
        q_.parallel_for(sycl::range<1>(nb), [=](sycl::id<1> b_idx) {
            int b = (int)b_idx[0];
            for (int i = 0; i < BLOCK_SIZE_SYCL; ++i) {
                blocks[b].residue[i] = blocks[b].residue_buffer[i];
            }
        }).wait();
    }

private:
    int num_blocks_;
    sycl::queue q_;
};

} // namespace triadic
} // namespace dase
