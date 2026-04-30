#include "MetricsEngineSYCL.hpp"
#include <iostream>
#include <vector>
#include <random>

int main() {
    try {
        dase::metrics::MetricsEngineSYCL engine;
        auto& q = engine.get_queue();

        const size_t n = 1000000;
        float* data = sycl::malloc_shared<float>(n, q);

        // Generate Gaussian noise
        std::mt19937 gen(42);
        std::normal_distribution<float> d(0, 1);
        for (size_t i = 0; i < n; ++i) {
            data[i] = d(gen);
        }

        const int num_bins = 100;
        uint32_t* bins = sycl::malloc_shared<uint32_t>(num_bins, q);

        std::cout << "Computing histogram for " << n << " samples..." << std::endl;
        engine.compute_histogram(data, n, -3.0f, 3.0f, bins, num_bins);

        uint32_t total_count = 0;
        for (int i = 0; i < num_bins; ++i) {
            total_count += bins[i];
        }

        std::cout << "Histogram complete. Total samples in range [-3, 3]: " << total_count << std::endl;
        
        // Simple entropy calculation
        float entropy = 0.0f;
        for (int i = 0; i < num_bins; ++i) {
            if (bins[i] > 0) {
                float p = static_cast<float>(bins[i]) / n;
                entropy -= p * std::log2(p);
            }
        }
        std::cout << "Approximate Shannon Entropy: " << entropy << " bits" << std::endl;

        sycl::free(data, q);
        sycl::free(bins, q);

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
