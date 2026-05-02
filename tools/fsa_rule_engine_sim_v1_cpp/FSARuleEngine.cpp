#include "FSARuleEngine.h"
#include <iostream>
#include <numeric>
#include <algorithm>

namespace dase {
namespace fsa {

FSAAgentEngine::FSAAgentEngine(int num_agents, std::shared_ptr<StateGraph> graph, std::shared_ptr<RuleEngine> rules)
    : num_agents_(num_agents), graph_(graph), rules_(rules) {
    current_state_.resize(num_agents);
    residue_.resize(num_agents, 0);
    active_.resize(num_agents, true);
}

void FSAAgentEngine::initialize(int start_node, int seed) {
    gen_.seed(seed);
    std::fill(current_state_.begin(), current_state_.end(), start_node);
    std::fill(residue_.begin(), residue_.end(), 0);
    std::fill(active_.begin(), active_.end(), true);
    active_history_.clear();
    active_history_.push_back(num_agents_);
}

void FSAAgentEngine::step() {
    #pragma omp parallel
    {
        // Each thread needs its own local RNG to avoid contention
        std::mt19937 local_gen(omp_get_thread_num() ^ 0xABCDEF);
        
        #pragma omp for
        for (int i = 0; i < num_agents_; ++i) {
            if (!active_[i]) continue;

            int curr = current_state_[i];
            int start = graph_->row_offsets[curr];
            int end = graph_->row_offsets[curr + 1];

            std::vector<int> admissible;
            for (int j = start; j < end; ++j) {
                int target = graph_->column_indices[j];
                if (rules_->isAdmissible(target, residue_[i], local_gen)) {
                    admissible.push_back(target);
                }
            }

            if (admissible.empty()) {
                active_[i] = false;
            } else {
                std::uniform_int_distribution<int> dist(0, admissible.size() - 1);
                current_state_[i] = admissible[dist(local_gen)];
                residue_[i]++;
            }
        }
    }
    
    // Log active count
    int active_count = 0;
    for (int i = 0; i < num_agents_; ++i) {
        if (active_[i]) active_count++;
    }
    active_history_.push_back(active_count);
}

FSAAgentEngine::Metrics FSAAgentEngine::getMetrics() const {
    int active_count = 0;
    long long total_res = 0;
    for (int i = 0; i < num_agents_; ++i) {
        if (active_[i]) {
            active_count++;
            total_res += residue_[i];
        }
    }
    return {
        active_count,
        (active_count > 0) ? static_cast<double>(total_res) / active_count : 0.0
    };
}

} // namespace fsa
} // namespace dase
