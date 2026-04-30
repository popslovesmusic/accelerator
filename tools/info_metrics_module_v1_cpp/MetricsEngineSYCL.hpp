#pragma once
#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>
#include <cmath>

namespace dase {
namespace metrics {

/**
 * GPU-Accelerated Information Metrics Engine using SYCL.
 * Optimized for Intel UHD 770.
 */
class MetricsEngineSYCL {
public:
    MetricsEngineSYCL() : q_(sycl::default_selector_v) {
        std::cout << "Metrics SYCL Engine Initialized on: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << std::endl;
    }

    /**
     * Compute a 1D histogram on the GPU using atomic operations.
     */
    void compute_histogram(const float* data, size_t n, float min_val, float max_val, uint32_t* bins, int num_bins) {
        if (n == 0) return;
        
        // Ensure bins are cleared (could be done on host, but GPU fill is fast)
        q_.fill(bins, 0u, num_bins).wait();

        float range = max_val - min_val;
        if (range <= 1e-9f) {
            // All data in one bin if range is effectively zero
            uint32_t count = static_cast<uint32_t>(n);
            q_.memcpy(bins, &count, sizeof(uint32_t)).wait();
            return;
        }

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            float val = data[idx[0]];
            if (val >= min_val && val <= max_val) {
                int bin_idx = static_cast<int>((val - min_val) / range * num_bins);
                if (bin_idx >= num_bins) bin_idx = num_bins - 1;
                if (bin_idx < 0) bin_idx = 0;
                
                auto bin_ref = sycl::atomic_ref<uint32_t, sycl::memory_order::relaxed, sycl::memory_scope::device, sycl::access::address_space::global_space>(bins[bin_idx]);
                bin_ref.fetch_add(1);
            }
        }).wait();
    }

    /**
     * Compute a 2D histogram on the GPU for joint entropy / mutual information.
     */
    void compute_histogram_2d(const float* x_data, const float* y_data, size_t n, 
                               float x_min, float x_max, float y_min, float y_max,
                               uint32_t* bins, int num_bins) {
        if (n == 0) return;

        q_.fill(bins, 0u, num_bins * num_bins).wait();

        float x_range = x_max - x_min;
        float y_range = y_max - y_min;
        
        if (x_range <= 1e-9f || y_range <= 1e-9f) {
             uint32_t count = static_cast<uint32_t>(n);
             q_.memcpy(bins, &count, sizeof(uint32_t)).wait();
             return;
        }

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            float xv = x_data[idx[0]];
            float yv = y_data[idx[0]];
            
            if (xv >= x_min && xv <= x_max && yv >= y_min && yv <= y_max) {
                int bx = static_cast<int>((xv - x_min) / x_range * num_bins);
                int by = static_cast<int>((yv - y_min) / y_range * num_bins);
                
                if (bx >= num_bins) bx = num_bins - 1;
                if (bx < 0) bx = 0;
                if (by >= num_bins) by = num_bins - 1;
                if (by < 0) by = 0;
                
                int bin_idx = by * num_bins + bx;
                auto bin_ref = sycl::atomic_ref<uint32_t, sycl::memory_order::relaxed, sycl::memory_scope::device, sycl::access::address_space::global_space>(bins[bin_idx]);
                bin_ref.fetch_add(1);
            }
        }).wait();
    }

    sycl::queue& get_queue() { return q_; }

private:
    sycl::queue q_;
};

} // namespace metrics
} // namespace dase
