#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace analysis {

/**
 * Intel UHD 770 SYCL Kernel for Chaos Detection / Bifurcation.
 * Optimized for Single Precision (FP32).
 */
class BifurcationEngineSYCL {
public:
    BifurcationEngineSYCL(int n_params) : n_(n_params), q_(sycl::default_selector_v) {
        params_ = sycl::malloc_shared<float>(n_params, q_);
        lyap_ = sycl::malloc_shared<float>(n_params, q_);
        std::cout << "Bifurcation SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~BifurcationEngineSYCL() {
        sycl::free(params_, q_); sycl::free(lyap_, q_);
    }

    // Maps thousands of parameter spaces in parallel
    void compute_lyapunov_logistic(int warmup, int iters) {
        float* p = params_;
        float* l = lyap_;
        
        q_.parallel_for(sycl::range<1>(n_), [=](sycl::id<1> idx) {
            int i = idx[0];
            float r = p[i];
            float x = 0.5f;
            
            for(int w=0; w<warmup; ++w) {
                x = r * x * (1.0f - x);
            }
            
            float sum_lyap = 0.0f;
            for(int j=0; j<iters; ++j) {
                float deriv = r - 2.0f * r * x;
                sum_lyap += sycl::log(sycl::fabs(deriv));
                x = r * x * (1.0f - x);
            }
            
            l[i] = sum_lyap / (float)iters;
        }).wait();
    }

    float *params_, *lyap_;

private:
    int n_;
    sycl::queue q_;
};

} // namespace analysis
} // namespace dase
