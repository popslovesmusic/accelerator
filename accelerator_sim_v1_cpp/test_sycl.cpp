#include "AcceleratorEngineSYCL.hpp"
#include <iostream>

int main() {
    try {
        const size_t n = 1024;
        dase::accelerator::SYCLAcceleratorEngine engine(n);
        std::cout << "Successfully created SYCL engine with " << n << " particles." << std::endl;
        
        // Initialize particles
        for (size_t i = 0; i < n; ++i) {
            engine.alive[i] = true;
            engine.x[i] = 0.0f;
            engine.px[i] = 0.001f;
            engine.y[i] = 0.0f;
            engine.py[i] = 0.0f;
            engine.z[i] = 0.0f;
            engine.delta[i] = 0.0f;
        }

        engine.apply_drift(1.0f);
        std::cout << "Successfully ran drift kernel." << std::endl;
        
        std::cout << "Particle 0 position x after drift: " << engine.x[0] << " (expected ~0.001)" << std::endl;

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
