#include "BifurcationEngine.h"
#include <iostream>
#include <vector>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::analysis;

extern "C" {

EXPORT BifurcationEngine* create_bifurcation_engine() {
    return new BifurcationEngine();
}

EXPORT void destroy_bifurcation_engine(BifurcationEngine* engine) {
    delete engine;
}

EXPORT void run_bifurcation_sweep(BifurcationEngine* engine, 
                                 double start, double end, int steps, int plateau_len,
                                 double* params_out, double* means_out, double* lyaps_out) {
    // Standard logistic map for CAPI demonstration
    auto logistic_map = [](double x, double r) {
        return r * x * (1.0 - x);
    };

    auto results = engine->runSweep(start, end, steps, plateau_len, logistic_map);
    
    for (size_t i = 0; i < results.size(); ++i) {
        params_out[i] = results[i].param_value;
        means_out[i] = results[i].observable_mean;
        lyaps_out[i] = results[i].lyapunov_exponent;
    }
}

}
