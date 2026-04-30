#pragma once
#include <sycl/sycl.hpp>
#include <iostream>

namespace dase {
namespace circular {

/**
 * Intel UHD 770 SYCL Kernel for Circular Tracking.
 * Optimized for Single Precision (FP32).
 */
class CircularEngineSYCL {
public:
    CircularEngineSYCL(size_t n, float circ, float mc) 
        : count_(n), circ_(circ), mc_(mc), q_(sycl::default_selector_v) {
        x_ = sycl::malloc_shared<float>(n, q_);
        px_ = sycl::malloc_shared<float>(n, q_);
        y_ = sycl::malloc_shared<float>(n, q_);
        py_ = sycl::malloc_shared<float>(n, q_);
        z_ = sycl::malloc_shared<float>(n, q_);
        delta_ = sycl::malloc_shared<float>(n, q_);
        alive_ = sycl::malloc_shared<bool>(n, q_);
        std::cout << "Circular SYCL Engine initialized on: " << q_.get_device().get_info<sycl::info::device::name>() << "\n";
    }

    ~CircularEngineSYCL() {
        sycl::free(x_, q_); sycl::free(px_, q_); sycl::free(y_, q_);
        sycl::free(py_, q_); sycl::free(z_, q_); sycl::free(delta_, q_); sycl::free(alive_, q_);
    }

    void apply_drift(float length) {
        float* x = x_; float* y = y_; float* px = px_; float* py = py_; float* delta = delta_; bool* alive = alive_;
        q_.parallel_for(sycl::range<1>(count_), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            if (alive[i]) {
                float inv_rigidity = 1.0f / sycl::max(1.0f + delta[i], 1e-12f);
                x[i] += length * px[i] * inv_rigidity;
                y[i] += length * py[i] * inv_rigidity;
            }
        }).wait();
    }

    void apply_kick(float kL) {
        float* x = x_; float* y = y_; float* px = px_; float* py = py_; bool* alive = alive_;
        q_.parallel_for(sycl::range<1>(count_), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            if (alive[i]) {
                px[i] -= kL * x[i];
                py[i] += kL * y[i];
            }
        }).wait();
    }

    void advance_longitudinal() {
        float* z = z_; float* delta = delta_; bool* alive = alive_;
        float mc_c = mc_ * circ_; float c = circ_; float half_c = 0.5f * c;
        q_.parallel_for(sycl::range<1>(count_), [=](sycl::id<1> idx) {
            int i = (int)idx[0];
            if (alive[i]) {
                z[i] += mc_c * delta[i];
                z[i] = sycl::fmod(z[i] + half_c, c);
                if (z[i] < 0.0f) z[i] += c;
                z[i] -= half_c;
            }
        }).wait();
    }

    float *x_, *px_, *y_, *py_, *z_, *delta_;
    bool *alive_;

private:
    size_t count_;
    float circ_, mc_;
    sycl::queue q_;
};

} // namespace circular
} // namespace dase
