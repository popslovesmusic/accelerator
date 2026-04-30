#include "KuramotoEngineSYCL.hpp"
#include <iostream>
#include <vector>
#include <chrono>
#include <random>

int main() {
    try {
        const size_t n = 100000;
        dase::kuramoto::KuramotoEngineSYCL engine(n);

        // Initialize
        std::mt19937 gen(42);
        std::normal_distribution<float> d_omega(0.0f, 0.1f);
        std::uniform_real_distribution<float> d_phi(0.0f, 6.283185f);

        for (size_t i = 0; i < n; ++i) {
            engine.phi[i] = d_phi(gen);
            engine.omega[i] = d_omega(gen);
        }

        const float dt = 0.1f;
        const float K = 0.5f;
        const int steps = 100;

        std::cout << "Starting benchmark: " << n << " oscillators, " << steps << " RK4 steps..." << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < steps; ++i) {
            engine.step_rk4(dt, K);
        }
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double> diff = end - start;
        std::cout << "Benchmark complete in " << diff.count() << " seconds." << std::endl;
        std::cout << "Throughput: " << (steps * n) / diff.count() / 1e6 << " million updates/sec" << std::endl;

        float R = engine.compute_order_parameter();
        std::cout << "Final Global Order Parameter R: " << R << std::endl;

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
