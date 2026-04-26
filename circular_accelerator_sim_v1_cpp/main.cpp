#include "CircularEngineAVX2.h"
#include "RingLatticeElements.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::circular;

int main() {
    const size_t num_particles = 1000000;
    const int num_turns = 1000;
    const double circumference = 100.0;
    const double momentum_compaction = 0.01;

    std::cout << "Initializing CircularEngineAVX2 with " << num_particles << " particles..." << std::endl;
    CircularEngineAVX2 engine(num_particles, circumference, momentum_compaction);

    // Build a simple ring lattice: Quad + Drift + Quad + Drift + RF
    engine.addElement(std::make_unique<RingQuadrupole>(0.1, 0.5));
    engine.addElement(std::make_unique<RingDrift>(2.0));
    engine.addElement(std::make_unique<RingQuadrupole>(-0.1, 0.5));
    engine.addElement(std::make_unique<RingDrift>(2.0));
    engine.addElement(std::make_unique<RingRFCavity>(0.01, 0.0, 10.0, circumference));
    engine.addElement(std::make_unique<RingAperture>(0.05));

    engine.initialize(42, 1e-3, 1e-4, 1e-3, 1e-4, 0.1, 1e-3);

    std::cout << "Running circular simulation for " << num_turns << " turns..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    engine.run(num_turns);
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    auto m = engine.getMetrics(num_turns);
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "\nFinal Circular Metrics (Turn " << num_turns << "):" << std::endl;
    std::cout << "  Survival: " << (static_cast<double>(m.alive_count) / num_particles) * 100.0 << " %" << std::endl;
    std::cout << "  x_rms:    " << m.x_rms << " m" << std::endl;
    std::cout << "  y_rms:    " << m.y_rms << " m" << std::endl;
    std::cout << "  z_rms:    " << m.z_rms << " m" << std::endl;
    std::cout << "  delta_rms:" << m.delta_rms << std::endl;
    std::cout << "  Runtime:  " << duration << " ms" << std::endl;

    return 0;
}
