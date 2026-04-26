#include "CAEngineAVX2.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::ca;

int main() {
    const int width = 512;
    const int height = 512;
    const int num_steps = 100;

    std::cout << "Initializing CAEngineAVX2 with " << width << "x" << height << " grid..." << std::endl;
    CAEngineAVX2 engine(width, height);

    // Set parameters
    engine.setParams(0.1, 0.01, 0.01);
    engine.initialize(10.0, 5, 0.1);

    std::cout << "Running CA simulation for " << num_steps << " steps..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int step = 0; step < num_steps; ++step) {
        engine.step();
        if (step % 20 == 0) {
            auto m = engine.getMetrics();
            std::cout << "Step " << step << ": Active Fraction = " << m.active_fraction << std::endl;
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    auto final_metrics = engine.getMetrics();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "\nFinal CA Metrics:" << std::endl;
    std::cout << "  Active Fraction: " << final_metrics.active_fraction << std::endl;
    std::cout << "  Mean Mismatch:   " << final_metrics.mean_mismatch << std::endl;
    std::cout << "  Mean Residue:    " << final_metrics.mean_residue << std::endl;
    std::cout << "  Runtime:         " << duration << " ms" << std::endl;

    return 0;
}
