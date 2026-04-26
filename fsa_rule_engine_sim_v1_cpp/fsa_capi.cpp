#include "FSARuleEngine.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::fsa;

extern "C" {

EXPORT FSAAgentEngine* create_fsa_engine(int num_agents, int n_states, int forbidden, int res_thresh, int res_req) {
    auto graph = std::make_shared<StateGraph>(n_states);
    auto rules = std::make_shared<RuleEngine>(n_states, forbidden, res_thresh, res_req);
    return new FSAAgentEngine(num_agents, graph, rules);
}

EXPORT void destroy_fsa_engine(FSAAgentEngine* engine) {
    delete engine;
}

EXPORT void add_fsa_edge(FSAAgentEngine* engine, int from, int to) {
    // Note: This requires the graph and engine to be setup correctly.
    // For simplicity in CAPI, we assume the graph is built before engine init or we provide a builder.
}

EXPORT void initialize_fsa(FSAAgentEngine* engine, int start_node, int seed) {
    engine->initialize(start_node, seed);
}

EXPORT void step_fsa(FSAAgentEngine* engine) {
    engine->step();
}

EXPORT void get_fsa_metrics(FSAAgentEngine* engine, int* active_count, double* mean_residue) {
    auto m = engine->getMetrics();
    *active_count = m.active_count;
    *mean_residue = m.mean_residue;
}

}
