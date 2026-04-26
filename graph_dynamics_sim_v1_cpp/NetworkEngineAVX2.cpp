#include "NetworkEngineAVX2.h"
#include <iostream>
#include <cmath>
#include <algorithm>
#include <immintrin.h>

namespace dase {
namespace network {

NetworkEngineAVX2::NetworkEngineAVX2(int n_nodes) : n_(n_nodes) {
    phi_ = static_cast<double*>(_mm_malloc(n_ * sizeof(double), 32));
    omega_ = static_cast<double*>(_mm_malloc(n_ * sizeof(double), 32));
    dphi_buffer_ = static_cast<double*>(_mm_malloc(n_ * sizeof(double), 32));
    A_ = static_cast<uint8_t*>(_mm_malloc(n_ * n_ * sizeof(uint8_t), 32));
    std::fill(A_, A_ + n_ * n_, 0);
}

NetworkEngineAVX2::~NetworkEngineAVX2() {
    _mm_free(phi_); _mm_free(omega_); _mm_free(dphi_buffer_); _mm_free(A_);
}

void NetworkEngineAVX2::setParams(double K, double theta_decouple, double theta_recouple, double P_recouple) {
    K_ = K; theta_decouple_ = theta_decouple; theta_recouple_ = theta_recouple; P_recouple_ = P_recouple;
}

void NetworkEngineAVX2::initialize(int seed, double omega_mean, double omega_std) {
    gen_.seed(seed);
    std::normal_distribution<double> dist_omega(omega_mean, omega_std);
    std::uniform_real_distribution<double> dist_phi(0, 2.0 * 3.1415926535);

    for (int i = 0; i < n_; ++i) {
        phi_[i] = dist_phi(gen_);
        omega_[i] = dist_omega(gen_);
        for (int j = 0; j < n_; ++j) {
            if (i == j) continue;
            // Initial edges (example: 10% prob)
            A_[i * n_ + j] = (std::uniform_real_distribution<double>(0, 1)(gen_) < 0.1) ? 1 : 0;
        }
    }
}

void NetworkEngineAVX2::computeDerivatives(const double* phi_in, double* dphi_out) {
    const double k_n = K_ / n_;
    const __m256d kn_vec = _mm256_set1_pd(k_n);

    #pragma omp parallel for
    for (int i = 0; i < n_; ++i) {
        __m256d sum_coupling = _mm256_setzero_pd();
        double phi_i = phi_in[i];
        __m256d phi_i_vec = _mm256_set1_pd(phi_i);

        // Vectorized loop over neighbors
        for (int j = 0; j < n_; j += 4) {
            __m256d phi_j = _mm256_load_pd(&phi_in[j]);
            __m256d diff = _mm256_sub_pd(phi_j, phi_i_vec);
            
            // sin(diff) approx (simplified here, but can use vectorized sin)
            // For the benchmark, we'll use scalar sin to ensure correctness
            alignas(32) double diffs[4];
            _mm256_store_pd(diffs, diff);
            
            alignas(32) double sins[4];
            for(int k=0; k<4; ++k) {
                if (A_[i * n_ + (j+k)]) {
                    sins[k] = std::sin(diffs[k]);
                } else {
                    sins[k] = 0.0;
                }
            }
            __m256d sin_vec = _mm256_load_pd(sins);
            sum_coupling = _mm256_add_pd(sum_coupling, sin_vec);
        }

        // Reduce coupling sum
        alignas(32) double res[4];
        _mm256_store_pd(res, sum_coupling);
        double total_coupling = res[0] + res[1] + res[2] + res[3];
        
        dphi_out[i] = omega_[i] + k_n * total_coupling;
    }
}

void NetworkEngineAVX2::step(double dt) {
    int n = n_;
    std::vector<double> k1(n), k2(n), k3(n), k4(n), tmp(n);

    computeDerivatives(phi_, k1.data());
    
    for(int i=0; i<n; ++i) tmp[i] = phi_[i] + 0.5 * dt * k1[i];
    computeDerivatives(tmp.data(), k2.data());

    for(int i=0; i<n; ++i) tmp[i] = phi_[i] + 0.5 * dt * k2[i];
    computeDerivatives(tmp.data(), k3.data());

    for(int i=0; i<n; ++i) tmp[i] = phi_[i] + dt * k3[i];
    computeDerivatives(tmp.data(), k4.data());

    for(int i=0; i<n; ++i) {
        phi_[i] += (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]);
        phi_[i] = std::fmod(phi_[i], 2.0 * 3.1415926535);
    }
}

void NetworkEngineAVX2::rewire() {
    std::uniform_real_distribution<double> dist_p(0, 1);
    
    #pragma omp parallel for
    for (int i = 0; i < n_; ++i) {
        std::mt19937 local_gen(omp_get_thread_num() ^ 0x123456);
        for (int j = 0; j < n_; ++j) {
            if (i == j) continue;
            
            double diff = phi_[j] - phi_[i];
            double stress = std::abs(std::sin(diff));
            
            if (A_[i * n_ + j]) {
                if (stress > theta_decouple_) {
                    A_[i * n_ + j] = 0;
                }
            } else {
                if (stress < theta_recouple_) {
                    if (std::uniform_real_distribution<double>(0, 1)(local_gen) < P_recouple_) {
                        A_[i * n_ + j] = 1;
                    }
                }
            }
        }
    }
}

NetworkEngineAVX2::Metrics NetworkEngineAVX2::getMetrics() const {
    long long edge_count = 0;
    double sum_re = 0, sum_im = 0;

    for (int i = 0; i < n_; ++i) {
        sum_re += std::cos(phi_[i]);
        sum_im += std::sin(phi_[i]);
        for (int j = 0; j < n_; ++j) {
            if (A_[i * n_ + j]) edge_count++;
        }
    }

    return {
        static_cast<double>(edge_count) / n_,
        static_cast<int>(edge_count / 2),
        std::sqrt(sum_re * sum_re + sum_im * sum_im) / n_
    };
}

} // namespace network
} // namespace dase
