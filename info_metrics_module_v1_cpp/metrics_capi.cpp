#include "MetricsEngineSYCL.hpp"
#include <cmath>
#include <algorithm>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {
    typedef dase::metrics::MetricsEngineSYCL MetricsEngine;

    EXPORT MetricsEngine* create_metrics_engine() {
        return new MetricsEngine();
    }

    EXPORT void destroy_metrics_engine(MetricsEngine* engine) {
        delete engine;
    }

    /**
     * Compute Shannon Entropy (bits) using GPU-accelerated histogramming.
     */
    EXPORT float compute_entropy_sycl(MetricsEngine* engine, float* data, size_t n, float min_val, float max_val, int num_bins) {
        if (!engine || n == 0) return 0.0f;
        auto& q = engine->get_queue();
        
        // Allocate USM for bins
        uint32_t* bins = sycl::malloc_shared<uint32_t>(num_bins, q);
        
        engine->compute_histogram(data, n, min_val, max_val, bins, num_bins);
        
        // Compute entropy on host
        float entropy = 0.0f;
        float total = static_cast<float>(n);
        for (int i = 0; i < num_bins; ++i) {
            if (bins[i] > 0) {
                float p = static_cast<float>(bins[i]) / total;
                entropy -= p * std::log2(p);
            }
        }
        
        sycl::free(bins, q);
        return entropy;
    }

    /**
     * Compute Mutual Information (bits) using GPU-accelerated 2D histogramming.
     */
    EXPORT float compute_mutual_information_sycl(MetricsEngine* engine, float* x, float* y, size_t n, 
                                                                float x_min, float x_max, float y_min, float y_max, int num_bins) {
        if (!engine || n == 0) return 0.0f;
        auto& q = engine->get_queue();
        
        uint32_t* bins_2d = sycl::malloc_shared<uint32_t>(num_bins * num_bins, q);
        uint32_t* bins_x = sycl::malloc_shared<uint32_t>(num_bins, q);
        uint32_t* bins_y = sycl::malloc_shared<uint32_t>(num_bins, q);
        
        engine->compute_histogram_2d(x, y, n, x_min, x_max, y_min, y_max, bins_2d, num_bins);
        engine->compute_histogram(x, n, x_min, x_max, bins_x, num_bins);
        engine->compute_histogram(y, n, y_min, y_max, bins_y, num_bins);
        
        float mi = 0.0f;
        float total = static_cast<float>(n);
        
        // I(X;Y) = sum P(x,y) log2 (P(x,y) / (P(x)P(y)))
        for (int j = 0; j < num_bins; ++j) {
            float p_y = static_cast<float>(bins_y[j]) / total;
            if (p_y <= 0) continue;
            
            for (int i = 0; i < num_bins; ++i) {
                uint32_t count_xy = bins_2d[j * num_bins + i];
                if (count_xy > 0) {
                    float p_xy = static_cast<float>(count_xy) / total;
                    float p_x = static_cast<float>(bins_x[i]) / total;
                    if (p_x > 0) {
                        mi += p_xy * std::log2(p_xy / (p_x * p_y));
                    }
                }
            }
        }
        
        sycl::free(bins_2d, q);
        sycl::free(bins_x, q);
        sycl::free(bins_y, q);
        
        return std::max(0.0f, mi);
    }
}
