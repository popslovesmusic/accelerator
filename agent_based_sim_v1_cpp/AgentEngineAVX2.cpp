#include "AgentEngineAVX2.h"
#include "SpatialHash.h"
#include <iostream>
#include <random>
#include <cmath>
#include <algorithm>

namespace dase {
namespace swarm {

AgentBunchSoA::AgentBunchSoA(size_t n) : count(n) {
    x = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    p = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    phi = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    residue = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    mismatch = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    omega = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
}

AgentBunchSoA::~AgentBunchSoA() {
    _mm_free(x); _mm_free(p); _mm_free(phi);
    _mm_free(residue); _mm_free(mismatch); _mm_free(omega);
}

AgentEngineAVX2::AgentEngineAVX2(size_t agent_count) : count_(agent_count) {
    bunch_ = std::make_unique<AgentBunchSoA>(agent_count);
}

void AgentEngineAVX2::setParams(double kappa, double R_c, double K_phi, double mismatch_rate, double residue_decay) {
    kappa_ = kappa; R_c_ = R_c; K_phi_ = K_phi; mismatch_rate_ = mismatch_rate; residue_decay_ = residue_decay;
}

void AgentEngineAVX2::initialize(int seed, double x_std, double p_std, double omega_mean, double omega_std) {
    std::mt19937 gen(seed);
    std::normal_distribution<double> dist_x(0, x_std);
    std::normal_distribution<double> dist_p(0, p_std);
    std::normal_distribution<double> dist_omega(omega_mean, omega_std);
    std::uniform_real_distribution<double> dist_phi(0, 2.0 * 3.1415926535);

    for (size_t i = 0; i < count_; ++i) {
        bunch_->x[i] = dist_x(gen);
        bunch_->p[i] = dist_p(gen);
        bunch_->phi[i] = dist_phi(gen);
        bunch_->omega[i] = dist_omega(gen);
        bunch_->residue[i] = 0.0;
        bunch_->mismatch[i] = 0.0;
    }
}

void AgentEngineAVX2::computeDerivatives(const AgentBunchSoA& in, AgentBunchSoA& out) {
    SpatialHash2D hash(R_c_, count_);
    hash.build(in.x, in.p, count_);

    const double inv_n = 1.0 / count_;

    #pragma omp parallel for
    for (int i = 0; i < static_cast<int>(count_); ++i) {
        // 1. Kinematics
        out.x[i] = in.p[i];
        out.p[i] = -kappa_ * in.x[i];

        // 2. Neighbor coupling
        double phase_coupling = 0.0;
        double local_coherence = 0.0;
        int neighbors = 0;

        hash.query(in.x[i], in.p[i], R_c_, in.x, in.p, [&](int j) {
            if (i == j) return;
            double dphi = in.phi[j] - in.phi[i];
            phase_coupling += std::sin(dphi);
            local_coherence += std::cos(dphi);
            neighbors++;
        });

        // 3. Phase Dynamics
        out.phi[i] = in.omega[i] + (K_phi_ * inv_n) * phase_coupling;

        // 4. Mismatch & Residue
        double coh = (neighbors > 0) ? (local_coherence / neighbors) : 0.0;
        out.mismatch[i] = mismatch_rate_ - 0.1 * coh * in.mismatch[i];
        out.residue[i] = in.mismatch[i] - residue_decay_ * in.residue[i];
    }
}

void AgentEngineAVX2::step(double dt) {
    AgentBunchSoA k1(count_), k2(count_), k3(count_), k4(count_), tmp(count_);

    auto add_scaled = [&](const AgentBunchSoA& base, const AgentBunchSoA& der, double s, AgentBunchSoA& res) {
        for (size_t i = 0; i < count_; ++i) {
            res.x[i] = base.x[i] + s * der.x[i];
            res.p[i] = base.p[i] + s * der.p[i];
            res.phi[i] = base.phi[i] + s * der.phi[i];
            res.residue[i] = base.residue[i] + s * der.residue[i];
            res.mismatch[i] = base.mismatch[i] + s * der.mismatch[i];
        }
    };

    computeDerivatives(*bunch_, k1);
    
    add_scaled(*bunch_, k1, 0.5 * dt, tmp);
    computeDerivatives(tmp, k2);

    add_scaled(*bunch_, k2, 0.5 * dt, tmp);
    computeDerivatives(tmp, k3);

    add_scaled(*bunch_, k3, dt, tmp);
    computeDerivatives(tmp, k4);

    for (size_t i = 0; i < count_; ++i) {
        bunch_->x[i] += (dt / 6.0) * (k1.x[i] + 2*k2.x[i] + 2*k3.x[i] + k4.x[i]);
        bunch_->p[i] += (dt / 6.0) * (k1.p[i] + 2*k2.p[i] + 2*k3.p[i] + k4.p[i]);
        bunch_->phi[i] += (dt / 6.0) * (k1.phi[i] + 2*k2.phi[i] + 2*k3.phi[i] + k4.phi[i]);
        bunch_->residue[i] += (dt / 6.0) * (k1.residue[i] + 2*k2.residue[i] + 2*k3.residue[i] + k4.residue[i]);
        bunch_->mismatch[i] += (dt / 6.0) * (k1.mismatch[i] + 2*k2.mismatch[i] + 2*k3.mismatch[i] + k4.mismatch[i]);
        
        // Phase wrap
        bunch_->phi[i] = std::fmod(bunch_->phi[i], 2.0 * 3.1415926535);
        if (bunch_->phi[i] < 0) bunch_->phi[i] += 2.0 * 3.1415926535;
    }
}

AgentEngineAVX2::Metrics AgentEngineAVX2::getMetrics() const {
    double sum_x = 0, sum_x2 = 0, sum_re = 0, sum_im = 0, sum_res = 0;
    for (size_t i = 0; i < count_; ++i) {
        sum_x += bunch_->x[i];
        sum_x2 += bunch_->x[i] * bunch_->x[i];
        sum_re += std::cos(bunch_->phi[i]);
        sum_im += std::sin(bunch_->phi[i]);
        sum_res += bunch_->residue[i];
    }
    double mean_x = sum_x / count_;
    return {
        mean_x,
        std::sqrt(sum_x2 / count_ - mean_x * mean_x),
        std::sqrt(sum_re * sum_re + sum_im * sum_im) / count_,
        sum_res / count_
    };
}

} // namespace swarm
} // namespace dase
