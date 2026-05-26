#pragma once
#include <sycl/sycl.hpp>
#include <iostream>
#include <vector>

// Share the struct definition if possible, but for simplicity in a header-only kernel:
// (Usually this would be in a shared common.hpp)
constexpr int BLOCK_SIZE_SYCL = 256;

struct alignas(32) TriadBlockSOA_SYCL {
    float in_channel[3][BLOCK_SIZE_SYCL];
    float out_channel[3][BLOCK_SIZE_SYCL];
    float recursive_reinforcement[3][BLOCK_SIZE_SYCL];
    float coupling_channel[3][BLOCK_SIZE_SYCL];
    float residue[BLOCK_SIZE_SYCL];
    float orientation_vector[BLOCK_SIZE_SYCL];
    float closure_strength[BLOCK_SIZE_SYCL];
    float detectable_mismatch[BLOCK_SIZE_SYCL];
    int collapse_flag[BLOCK_SIZE_SYCL];
    float persistence_score[BLOCK_SIZE_SYCL];
    float inside_admissibility_rate[BLOCK_SIZE_SYCL];
};

namespace dase {
namespace triadic {

class TriadicEngineSYCL {
public:
    TriadicEngineSYCL(int num_blocks, sycl::queue q) : num_blocks_(num_blocks), q_(q) {
        std::cout << "Triadic Substrate SYCL Engine bound to: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    void process_global_coupling(TriadBlockSOA_SYCL* blocks, float coupling_strength, float dt) {
        int nb = num_blocks_;
        
        // Parallel Global Coupling Kernel
        // This replaces the 1D chain neighbor coupling with a GPU-accelerated pass.
        q_.parallel_for(sycl::range<1>(nb), [=](sycl::id<1> b_idx) {
            int b = (int)b_idx[0];
            int prev = (b == 0) ? nb - 1 : b - 1;
            int next = (b == nb - 1) ? 0 : b + 1;
            
            TriadBlockSOA_SYCL& curr_block = blocks[b];
            TriadBlockSOA_SYCL& prev_block = blocks[prev];
            TriadBlockSOA_SYCL& next_block = blocks[next];

            for (int i = 0; i < BLOCK_SIZE_SYCL; ++i) {
                if (curr_block.collapse_flag[i]) continue;

                // Residue-conditioned coupling: <->_R
                float coupling_factor = curr_block.residue[i] * coupling_strength;
                
                // Exchange mismatch pressure from neighbors
                float in_prev = prev_block.out_channel[0][i];
                float in_next = next_block.out_channel[0][i];
                
                float delta_coupling = (in_prev + in_next) * coupling_factor;
                curr_block.coupling_channel[0][i] = delta_coupling;
                
                // Reinject into in_channel
                curr_block.in_channel[0][i] += delta_coupling * dt;
            }
        }).wait();
    }

private:
    int num_blocks_;
    sycl::queue q_;
};

} // namespace triadic
} // namespace dase
