#include "AcceleratorEngineAVX2.h"
#include "LatticeElements.h"
#include "LatticeFactory.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::accelerator;

extern "C" {

EXPORT AcceleratorEngineAVX2* create_engine(size_t particle_count) {
    return new AcceleratorEngineAVX2(particle_count);
}

EXPORT void destroy_engine(AcceleratorEngineAVX2* engine) {
    delete engine;
}

EXPORT void add_drift(AcceleratorEngineAVX2* engine, double length) {
    engine->addElement(std::make_unique<Drift>(length));
}

EXPORT void add_quadrupole(AcceleratorEngineAVX2* engine, double k1, double length) {
    engine->addElement(std::make_unique<Quadrupole>(k1, length));
}

EXPORT void add_rf_cavity(AcceleratorEngineAVX2* engine, double voltage, double phase, double harmonic) {
    engine->addElement(std::make_unique<RFCavity>(voltage, phase, harmonic));
}

EXPORT void add_space_charge_2d(AcceleratorEngineAVX2* engine, int nx, int ny, double width, double height) {
    engine->addElement(std::make_unique<SpaceCharge2D>(nx, ny, width, height));
}

EXPORT void initialize_normal(AcceleratorEngineAVX2* engine, 
                              double x_rms, double px_rms, 
                              double y_rms, double py_rms, 
                              double z_rms, double delta_rms, 
                              int seed) {
    engine->initializeNormal(x_rms, px_rms, y_rms, py_rms, z_rms, delta_rms, seed);
}

EXPORT void run_simulation(AcceleratorEngineAVX2* engine, int steps) {
    engine->run(steps);
}

EXPORT void get_metrics(AcceleratorEngineAVX2* engine, double* x_mean, double* x_rms, double* survival) {
    engine->getMetrics(*x_mean, *x_rms, *survival);
}

}
