#pragma once

#include <vector>
#include <string>
#include <memory>
#include <random>
#include <omp.h>

namespace dase {
namespace fsa {

/**
 * High-performance CSR (Compressed Sparse Row) Graph for State Machine.
 */
struct StateGraph {
    std::vector<int> row_offsets;
    std::vector<int> column_indices;
    int num_states;

    StateGraph(int n) : num_states(n) {
        row_offsets.assign(n + 1, 0);
    }
};

/**
 * Rule Engine for Admissibility Logic.
 */
class RuleEngine {
public:
    RuleEngine(int n_states, int forbidden, int res_thresh_node, int res_required, double mismatch_rate = 0.0)
        : n_states_(n_states), forbidden_(forbidden), 
          res_thresh_node_(res_thresh_node), res_required_(res_required),
          mismatch_rate_(mismatch_rate) {}

    bool isAdmissible(int target_node, int agent_residue, std::mt19937& gen) const {
        if (target_node == forbidden_) return false;
        if (target_node >= res_thresh_node_ && agent_residue < res_required_) return false;
        
        // Falsification Injection: random mismatch
        if (mismatch_rate_ > 0.0) {
            std::uniform_real_distribution<double> dist(0.0, 1.0);
            if (dist(gen) < mismatch_rate_) return false;
        }
        
        return true;
    }

    int n_states() const { return n_states_; }

private:
    int n_states_;
    int forbidden_;
    int res_thresh_node_;
    int res_required_;
    double mismatch_rate_;
};

/**
 * High-performance Agent Engine for FSA.
 */
class FSAAgentEngine {
public:
    FSAAgentEngine(int num_agents, std::shared_ptr<StateGraph> graph, std::shared_ptr<RuleEngine> rules);
    
    void step();
    void initialize(int start_node, int seed);

    struct Metrics {
        int active_count;
        double mean_residue;
    };
    
    Metrics getMetrics() const;
    const std::vector<int>& getActiveHistory() const { return active_history_; }

private:
    int num_agents_;
    std::shared_ptr<StateGraph> graph_;
    std::shared_ptr<RuleEngine> rules_;

    // Agent SoA
    std::vector<int> current_state_;
    std::vector<int> residue_;
    std::vector<bool> active_;
    std::vector<int> active_history_;
    
    std::mt19937 gen_;
};

} // namespace fsa
} // namespace dase
