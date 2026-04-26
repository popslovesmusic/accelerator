#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace fsa {

/**
 * Intel UHD 770 SYCL Kernel for Automata Logic.
 * Optimized for compatibility and performance.
 */
class FSAEngineSYCL {
public:
    FSAEngineSYCL(int num_agents, int num_edges) : n_agents_(num_agents), n_edges_(num_edges), q_(sycl::default_selector_v) {
        state_ = sycl::malloc_shared<int>(num_agents, q_);
        residue_ = sycl::malloc_shared<int>(num_agents, q_);
        active_ = sycl::malloc_shared<bool>(num_agents, q_);
        
        // CSR Graph on GPU
        row_offsets_ = sycl::malloc_shared<int>(1001, q_); 
        col_indices_ = sycl::malloc_shared<int>(num_edges, q_);
        
        std::cout << "FSA Rule SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~FSAEngineSYCL() {
        sycl::free(state_, q_); sycl::free(residue_, q_); sycl::free(active_, q_);
        sycl::free(row_offsets_, q_); sycl::free(col_indices_, q_);
    }

    void step(int forbidden, int res_thresh, int res_req) {
        int* state = state_; int* residue = residue_; bool* active = active_;
        int* offsets = row_offsets_; int* cols = col_indices_;
        int n_agents = n_agents_;
        
        q_.parallel_for(sycl::range<1>(n_agents), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            if (!active[i]) return;
            
            int curr = state[i];
            int start = offsets[curr];
            int end = offsets[curr + 1];
            
            int valid_targets[100]; // Local buffer for GPU thread
            int v_count = 0;
            
            for (int j = start; j < end; ++j) {
                int target = cols[j];
                bool ok = true;
                if (target == forbidden) ok = false;
                if (target >= res_thresh && residue[i] < res_req) ok = false;
                
                if (ok && v_count < 100) {
                    valid_targets[v_count++] = target;
                }
            }
            
            if (v_count == 0) {
                active[i] = false;
            } else {
                state[i] = valid_targets[0]; // Deterministic fallback for SYCL demo
                residue[i]++;
            }
        }).wait();
    }

    int *state_, *residue_;
    bool *active_;
    int *row_offsets_, *col_indices_;

private:
    int n_agents_, n_edges_;
    sycl::queue q_;
};

} // namespace fsa
} // namespace dase
