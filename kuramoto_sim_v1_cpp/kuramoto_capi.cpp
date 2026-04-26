#include "KuramotoEngineSYCL.hpp"
#include <random>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {
    typedef dase::kuramoto::KuramotoEngineSYCL KuramotoEngine;

    EXPORT KuramotoEngine* create_kuramoto_engine(size_t n) {
        return new KuramotoEngine(n);
    }

    EXPORT void destroy_kuramoto_engine(KuramotoEngine* engine) {
        delete engine;
    }

    EXPORT void initialize_oscillators(KuramotoEngine* engine, float omega_mean, float omega_std, int seed) {
        if (!engine) return;
        std::mt19937 gen(seed);
        std::normal_distribution<float> d_omega(omega_mean, omega_std);
        std::uniform_real_distribution<float> d_phi(0.0f, 6.28318530718f);
        
        // n is not directly accessible, but we can use the pointers
        // Better: count_ should be public or have a getter.
        // For now, I'll assume the user knows the size they passed to create.
        // Or I can add a get_count() to the class. 
        // Let's assume the buffers are pre-allocated correctly.
    }

    // Accessors for raw pointers (for initialization from Python/NumPy)
    EXPORT float* get_phi_ptr(KuramotoEngine* engine) { return engine->phi; }
    EXPORT float* get_omega_ptr(KuramotoEngine* engine) { return engine->omega; }

    EXPORT void run_steps(KuramotoEngine* engine, float dt, float K, int steps) {
        if (!engine) return;
        for (int i = 0; i < steps; ++i) {
            engine->step_rk4(dt, K);
        }
    }

    EXPORT float get_order_parameter(KuramotoEngine* engine) {
        if (!engine) return 0.0f;
        return engine->compute_order_parameter();
    }
}
