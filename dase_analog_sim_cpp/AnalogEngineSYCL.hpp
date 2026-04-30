#pragma once

#include <sycl/sycl.hpp>
#include <vector>
#include <iostream>

namespace dase {
namespace analog {

template <typename T>
class AnalogEngineSYCL {
public:
    AnalogEngineSYCL(size_t num_nodes, sycl::queue& q) 
        : num_nodes_(num_nodes), q_(q) {
        
        integrator_state = sycl::malloc_shared<T>(num_nodes, q_);
        feedback_gain = sycl::malloc_shared<T>(num_nodes, q_);
        current_output = sycl::malloc_shared<T>(num_nodes, q_);
        
        q_.fill(integrator_state, static_cast<T>(0), num_nodes);
        q_.fill(feedback_gain, static_cast<T>(0), num_nodes);
        q_.fill(current_output, static_cast<T>(0), num_nodes).wait();
    }

    ~AnalogEngineSYCL() {
        sycl::free(integrator_state, q_);
        sycl::free(feedback_gain, q_);
        sycl::free(current_output, q_);
    }

    void step(T input_signal, T control_signal, T aux_signal, T dt, int iterations) {
        const size_t n = num_nodes_;
        auto i_state = integrator_state;
        auto f_gain = feedback_gain;
        auto c_out = current_output;

        q_.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            T state = i_state[idx];
            T gain = f_gain[idx];
            T output = 0;

            for (int i = 0; i < iterations; ++i) {
                // 1. Amplify
                T amplified = input_signal * control_signal;

                // 2. Integrate
                state += amplified * static_cast<T>(0.1) * dt;
                state *= static_cast<T>(0.999999);
                state = sycl::clamp(state, static_cast<T>(-1e6), static_cast<T>(1e6));

                // 3. Spectral processing (sum of 8 frequencies)
                T aux_blended = amplified + aux_signal;
                T spectral_boost = 0;
                const T mults[8] = {2.7f, 2.1f, 1.8f, 1.4f, 1.2f, 0.9f, 0.7f, 0.3f};
                for (int j = 0; j < 8; ++j) {
                    spectral_boost += sycl::sin(aux_blended * mults[j]);
                }
                spectral_boost *= static_cast<T>(0.125);

                // 4. Feedback
                T feedback_comp = state * gain;
                T feedback_out = state + feedback_comp;

                // 5. Final output
                output = feedback_out + spectral_boost;
                output = sycl::clamp(output, static_cast<T>(-10.0), static_cast<T>(10.0));
            }

            i_state[idx] = state;
            c_out[idx] = output;
        }).wait();
    }

    T *integrator_state, *feedback_gain, *current_output;

private:
    size_t num_nodes_;
    sycl::queue& q_;
};

} // namespace analog
} // namespace dase
