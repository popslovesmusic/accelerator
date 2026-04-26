#include "CAEngineAVX2.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::ca;

extern "C" {

EXPORT CAEngineAVX2* create_ca_engine(int width, int height) {
    return new CAEngineAVX2(width, height);
}

EXPORT void destroy_ca_engine(CAEngineAVX2* engine) {
    delete engine;
}

EXPORT void set_ca_params(CAEngineAVX2* engine, double D, double delta_R, double gamma_R) {
    engine->setParams(D, delta_R, gamma_R);
}

EXPORT void initialize_ca(CAEngineAVX2* engine, double source_strength, int source_radius, double initial_residue) {
    engine->initialize(source_strength, source_radius, initial_residue);
}

EXPORT void step_ca(CAEngineAVX2* engine) {
    engine->step();
}

EXPORT void get_ca_metrics(CAEngineAVX2* engine, double* active_frac, double* mean_e, double* mean_r) {
    auto m = engine->getMetrics();
    *active_frac = m.active_fraction;
    *mean_e = m.mean_mismatch;
    *mean_r = m.mean_residue;
}

}
