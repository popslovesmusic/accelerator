#include "AgentEngineAVX2.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::swarm;

int main() {
    const size_t num_agents = 10000; // 10k agents
    const int num_steps = 100;
    const double dt = 0.01;

    std::cout << "Initializing AgentEngineAVX2 with " << num_agents << " agents..." << std::endl;
    AgentEngineAVX2 engine(num_agents);

    // Set parameters
    engine.setParams(1.0, 0.5, 1.0, 0.01, 0.1);
    engine.initialize(42, 0.5, 0.5, 1.0, 0.1);

    std::cout << "Running swarm simulation for " << num_steps << " steps..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int step = 0; step < num_steps; ++step) {
        engine.step(dt);
        if (step % 10 == 0) {
            auto m = engine.getMetrics();
            std::cout << "Step " << step << ": Order Parameter = " << m.order_parameter << std::endl;
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    auto final_metrics = engine.getMetrics();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "\nFinal Swarm Metrics:" << std::endl;
    std::cout << "  Order Parameter: " << final_metrics.order_parameter << std::endl;
    std::cout << "  Mean Residue:    " << final_metrics.residue_mean << std::endl;
    std::cout << "  Runtime:         " << duration << " ms" << std::endl;

    return 0;
}
