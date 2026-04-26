#include "FSARuleEngine.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::fsa;

int main() {
    const int num_states = 1000;
    const int num_agents = 100000; // 100k agents
    const int num_steps = 100;

    std::cout << "Initializing FSAAgentEngine with " << num_agents << " agents and " << num_states << " states..." << std::endl;
    
    // 1. Build a random graph in CSR format
    auto graph = std::make_shared<StateGraph>(num_states);
    std::mt19937 gen(42);
    std::uniform_int_distribution<int> state_dist(0, num_states - 1);
    
    std::vector<std::vector<int>> adj(num_states);
    for (int i = 0; i < num_states; ++i) {
        int degree = 5 + (gen() % 10);
        for (int j = 0; j < degree; ++j) {
            adj[i].push_back(state_dist(gen));
        }
    }
    
    int current_offset = 0;
    for (int i = 0; i < num_states; ++i) {
        graph->row_offsets[i] = current_offset;
        for (int neighbor : adj[i]) {
            graph->column_indices.push_back(neighbor);
        }
        current_offset += adj[i].size();
    }
    graph->row_offsets[num_states] = current_offset;

    // 2. Setup Rules
    auto rules = std::make_shared<RuleEngine>(num_states, 999, 800, 10);
    
    FSAAgentEngine engine(num_agents, graph, rules);
    engine.initialize(1, 42);

    std::cout << "Running FSA simulation for " << num_steps << " steps..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int step = 0; step < num_steps; ++step) {
        engine.step();
        if (step % 20 == 0) {
            auto m = engine.getMetrics();
            std::cout << "Step " << step << ": Active Count = " << m.active_count << std::endl;
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    auto m = engine.getMetrics();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "\nFinal FSA Metrics:" << std::endl;
    std::cout << "  Active Count: " << m.active_count << std::endl;
    std::cout << "  Mean Residue: " << m.mean_residue << std::endl;
    std::cout << "  Runtime:      " << duration << " ms" << std::endl;

    return 0;
}
