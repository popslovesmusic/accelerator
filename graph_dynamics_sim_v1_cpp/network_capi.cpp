#include "NetworkEngineAVX2.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::network;

extern "C" {

EXPORT NetworkEngineAVX2* create_network_engine(int n_nodes) {
    return new NetworkEngineAVX2(n_nodes);
}

EXPORT void destroy_network_engine(NetworkEngineAVX2* engine) {
    delete engine;
}

EXPORT void set_network_params(NetworkEngineAVX2* engine, double K, double theta_de, double theta_re, double P_re) {
    engine->setParams(K, theta_de, theta_re, P_re);
}

EXPORT void initialize_network(NetworkEngineAVX2* engine, int seed, double omega_mean, double omega_std) {
    engine->initialize(seed, omega_mean, omega_std);
}

EXPORT void step_network(NetworkEngineAVX2* engine, double dt) {
    engine->step(dt);
}

EXPORT void rewire_network(NetworkEngineAVX2* engine) {
    engine->rewire();
}

EXPORT void get_network_metrics(NetworkEngineAVX2* engine, double* avg_degree, int* edge_count, double* order_param) {
    auto m = engine->getMetrics();
    *avg_degree = m.avg_degree;
    *edge_count = m.edge_count;
    *order_param = m.order_parameter;
}

}
