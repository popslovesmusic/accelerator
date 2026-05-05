#pragma once

#include <vector>
#include <string>
#include <memory>
#include <immintrin.h>
#include <omp.h>

namespace dase {
namespace swarm {

/**
 * Structure of Arrays (SoA) for Swarm Agent state.
 */
struct AgentBunchSoA {
    size_t count;
    double* x;       // Position
    double* p;       // Momentum
    double* phi;     // Phase
    double* residue; // Residue
    double* mismatch;// Mismatch
    double* omega;   // Natural frequency

    explicit AgentBunchSoA(size_t n);
    ~AgentBunchSoA();

    // Prevent copying
    AgentBunchSoA(const AgentBunchSoA&) = delete;
    AgentBunchSoA& operator=(const AgentBunchSoA&) = delete;
};

/**
 * High-performance Agent-Based Swarm Engine using AVX2 and Spatial Hashing.
 */
class AgentEngineAVX2 {
public:
    explicit AgentEngineAVX2(size_t agent_count);
    
    void setParams(double kappa, double R_c, double K_phi, double mismatch_rate, double mismatch_phase, double bias_strength, double residue_decay);
    void initialize(int seed, double x_std, double p_std, double omega_mean, double omega_std);
    
    void step(double dt);
    
    struct Metrics {
        double x_mean;
        double x_rms;
        double order_parameter;
        double residue_mean;
        double mismatch_mean;
    };
    
    Metrics getMetrics() const;

private:
    size_t count_;
    std::unique_ptr<AgentBunchSoA> bunch_;
    
    // Parameters
    double kappa_ = 1.0;
    double R_c_ = 1.0;
    double K_phi_ = 1.0;
    double mismatch_rate_ = 0.01;
    double mismatch_phase_ = 0.0;
    double bias_strength_ = 0.0;
    double residue_decay_ = 0.1;

    void computeDerivatives(const AgentBunchSoA& in, AgentBunchSoA& out);
};

} // namespace swarm
} // namespace dase
