#include "NetworkEngineAVX2.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::network;

int main() {
    const int n_nodes = 1000;
    const int num_steps = 100;
    const double dt = 0.05;

    std::cout << "Initializing NetworkEngineAVX2 with " << n_nodes << " nodes..." << std::endl;
    NetworkEngineAVX2 engine(n_nodes);

    // Set parameters (K, theta_decouple, theta_recouple, P_recouple)
    engine.setParams(1.0, 0.5, 0.1, 0.01);
    engine.initialize(42, 1.0, 0.1);

    std::cout << "Running network dynamics for " << num_steps << " steps..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int step = 0; step < num_steps; ++step) {
        engine.step(dt);
        engine.rewire();
        if (step % 20 == 0) {
            auto m = engine.getMetrics();
            std::cout << "Step " << step << ": Order Param = " << m.order_parameter << ", Edges = " << m.edge_count << std::endl;
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    auto m = engine.getMetrics();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "\nFinal Network Metrics:" << std::endl;
    std::cout << "  Order Parameter: " << m.order_parameter << std::endl;
    std::cout << "  Edge Count:      " << m.edge_count << std::endl;
    std::cout << "  Avg Degree:      " << m.avg_degree << std::endl;
    std::cout << "  Runtime:         " << duration << " ms" << std::endl;

    return 0;
}
