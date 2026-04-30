#include "CircularEngineAVX2.h"
#include "RingLatticeElements.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::circular;

extern "C" {

EXPORT CircularEngineAVX2* create_circular_engine(size_t particle_count, double circumference, double momentum_compaction) {
    return new CircularEngineAVX2(particle_count, circumference, momentum_compaction);
}

EXPORT void destroy_circular_engine(CircularEngineAVX2* engine) {
    delete engine;
}

EXPORT void add_ring_drift(CircularEngineAVX2* engine, double length) {
    engine->addElement(std::make_unique<RingDrift>(length));
}

EXPORT void add_ring_quadrupole(CircularEngineAVX2* engine, double k1, double length) {
    engine->addElement(std::make_unique<RingQuadrupole>(k1, length));
}

EXPORT void add_ring_rf_cavity(CircularEngineAVX2* engine, double voltage, double phase, double harmonic, double circumference) {
    engine->addElement(std::make_unique<RingRFCavity>(voltage, phase, harmonic, circumference));
}

EXPORT void add_ring_aperture(CircularEngineAVX2* engine, double radius) {
    engine->addElement(std::make_unique<RingAperture>(radius));
}

EXPORT void initialize_ring(CircularEngineAVX2* engine, int seed, 
                           double x_sigma, double px_sigma, 
                           double y_sigma, double py_sigma, 
                           double z_sigma, double delta_sigma) {
    engine->initialize(seed, x_sigma, px_sigma, y_sigma, py_sigma, z_sigma, delta_sigma);
}

EXPORT void run_ring(CircularEngineAVX2* engine, int turns) {
    engine->run(turns);
}

EXPORT void get_ring_metrics(CircularEngineAVX2* engine, int turn, 
                            size_t* alive_count, double* x_rms, double* y_rms, 
                            double* z_rms, double* delta_rms) {
    auto m = engine->getMetrics(turn);
    *alive_count = m.alive_count;
    *x_rms = m.x_rms;
    *y_rms = m.y_rms;
    *z_rms = m.z_rms;
    *delta_rms = m.delta_rms;
}

}
