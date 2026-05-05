#include "AgentEngineAVX2.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::swarm;

extern "C" {

EXPORT AgentEngineAVX2* create_agent_engine(size_t agent_count) {
    return new AgentEngineAVX2(agent_count);
}

EXPORT void destroy_agent_engine(AgentEngineAVX2* engine) {
    delete engine;
}

EXPORT void set_swarm_params(AgentEngineAVX2* engine, double kappa, double R_c, double K_phi, double mismatch_rate, double mismatch_phase, double bias_strength, double residue_decay) {
    engine->setParams(kappa, R_c, K_phi, mismatch_rate, mismatch_phase, bias_strength, residue_decay);
}

EXPORT void initialize_swarm(AgentEngineAVX2* engine, int seed, double x_std, double p_std, double omega_mean, double omega_std) {
    engine->initialize(seed, x_std, p_std, omega_mean, omega_std);
}

EXPORT void step_swarm(AgentEngineAVX2* engine, double dt) {
    engine->step(dt);
}

EXPORT void get_swarm_metrics(AgentEngineAVX2* engine, double* x_mean, double* x_rms, double* order_param, double* residue_mean, double* mismatch_mean) {
    auto m = engine->getMetrics();
    *x_mean = m.x_mean;
    *x_rms = m.x_rms;
    *order_param = m.order_parameter;
    *residue_mean = m.residue_mean;
    *mismatch_mean = m.mismatch_mean;
}

}
