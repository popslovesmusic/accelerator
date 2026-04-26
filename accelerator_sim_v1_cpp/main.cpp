#include "AcceleratorEngineAVX2.h"
#include "LatticeElements.h"
#include <iostream>
#include <iomanip>

using namespace dase::accelerator;

int main() {
    const size_t num_particles = 1000000; // 1 million particles
    const int num_steps = 100;

    std::cout << "Initializing AcceleratorEngineAVX2 with " << num_particles << " particles..." << std::endl;
    AcceleratorEngineAVX2 engine(num_particles);

    // Initial bunch distribution
    engine.initializeNormal(1e-3, 1e-4, 1e-3, 1e-4, 0.1, 1e-3, 42);

    // Build a simple FODO lattice with Space Charge
    engine.addElement(std::make_unique<Quadrupole>(0.5, 0.1));  // Focusing
    engine.addElement(std::make_unique<SpaceCharge2D>(64, 64, 0.05, 0.05)); // High-fidelity SC
    engine.addElement(std::make_unique<Drift>(1.0));
    engine.addElement(std::make_unique<Quadrupole>(-0.5, 0.1)); // Defocusing
    engine.addElement(std::make_unique<Drift>(1.0));
    engine.addElement(std::make_unique<RFCavity>(0.01, 0.0, 10.0));

    std::cout << "Running simulation for " << num_steps << " steps..." << std::endl;
    engine.run(num_steps);

    double x_mean, x_rms, survival;
    engine.getMetrics(x_mean, x_rms, survival);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Final Metrics:" << std::endl;
    std::cout << "  x_mean: " << x_mean << " m" << std::endl;
    std::cout << "  x_rms:  " << x_rms << " m" << std::endl;
    std::cout << "  Survival: " << survival * 100.0 << " %" << std::endl;

    return 0;
}
