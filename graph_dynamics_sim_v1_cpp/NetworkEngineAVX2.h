#pragma once

#include <vector>
#include <string>
#include <memory>
#include <immintrin.h>
#include <omp.h>
#include <random>

namespace dase {
namespace network {

/**
 * High-performance Network Dynamics Engine using AVX2.
 */
class NetworkEngineAVX2 {
public:
    explicit NetworkEngineAVX2(int n_nodes);
    ~NetworkEngineAVX2();

    void setParams(double K, double theta_decouple, double theta_recouple, double P_recouple);
    void initialize(int seed, double omega_mean, double omega_std);
    
    void step(double dt);
    void rewire();

    struct Metrics {
        double avg_degree;
        int edge_count;
        double order_parameter;
    };
    
    Metrics getMetrics() const;

private:
    int n_;
    double K_ = 1.0;
    double theta_decouple_ = 0.5;
    double theta_recouple_ = 0.1;
    double P_recouple_ = 0.01;

    // Node State (Aligned for AVX2)
    double* phi_;
    double* omega_;
    double* dphi_buffer_;
    
    // Adjacency Matrix (Dense for now, could be sparse CSR if connectivity is very low)
    // We use a flat array n*n
    uint8_t* A_; 

    std::mt19937 gen_;

    void computeDerivatives(const double* phi_in, double* dphi_out);
};

} // namespace network
} // namespace dase
