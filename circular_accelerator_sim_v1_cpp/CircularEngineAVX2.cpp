#include "CircularEngineAVX2.h"
#include "RingLatticeElements.h"
#include <iostream>
#include <random>
#include <cmath>
#include <algorithm>

namespace dase {
namespace circular {

RingBunchSoA::RingBunchSoA(size_t n) : count(n) {
    x = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    px = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    y = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    py = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    z = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    delta = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    alive = new bool[n];
    for (size_t i = 0; i < n; ++i) alive[i] = true;
}

RingBunchSoA::~RingBunchSoA() {
    _mm_free(x); _mm_free(px); _mm_free(y); _mm_free(py); _mm_free(z); _mm_free(delta);
    delete[] alive;
}

CircularEngineAVX2::CircularEngineAVX2(size_t particle_count, double circumference, double momentum_compaction)
    : count_(particle_count), circumference_(circumference), momentum_compaction_(momentum_compaction) {
    bunch_ = std::make_unique<RingBunchSoA>(particle_count);
}

void CircularEngineAVX2::addElement(std::unique_ptr<RingElement> element) {
    lattice_.push_back(std::move(element));
}

void CircularEngineAVX2::initialize(int seed, double x_sigma, double px_sigma, double y_sigma, double py_sigma, double z_sigma, double delta_sigma) {
    std::mt19937 gen(seed);
    std::normal_distribution<double> dx(0, x_sigma), dpx(0, px_sigma), dy(0, y_sigma), dpy(0, py_sigma), dz(0, z_sigma), dd(0, delta_sigma);

    for (size_t i = 0; i < count_; ++i) {
        bunch_->x[i] = dx(gen);
        bunch_->px[i] = dpx(gen);
        bunch_->y[i] = dy(gen);
        bunch_->py[i] = dpy(gen);
        bunch_->z[i] = dz(gen);
        bunch_->delta[i] = dd(gen);
        bunch_->alive[i] = true;
    }
}

void CircularEngineAVX2::advanceLongitudinal() {
    const int n = static_cast<int>(count_);
    const double mc_c = momentum_compaction_ * circumference_;
    const double circ = circumference_;
    const double half_circ = 0.5 * circ;

    #pragma omp parallel for
    for (int i = 0; i < n; ++i) {
        if (!bunch_->alive[i]) continue;
        bunch_->z[i] += mc_c * bunch_->delta[i];
        // Wrap
        bunch_->z[i] = std::fmod(bunch_->z[i] + half_circ, circ);
        if (bunch_->z[i] < 0) bunch_->z[i] += circ;
        bunch_->z[i] -= half_circ;
    }
}

void CircularEngineAVX2::run(int turns) {
    for (int t = 1; t <= turns; ++t) {
        for (auto& element : lattice_) {
            element->apply(*bunch_);
        }
        advanceLongitudinal();
    }
}

CircularEngineAVX2::Metrics CircularEngineAVX2::getMetrics(int turn) const {
    double sx = 0, sx2 = 0, sy = 0, sy2 = 0, sz = 0, sz2 = 0, sd = 0, sd2 = 0;
    size_t alive_count = 0;

    for (size_t i = 0; i < count_; ++i) {
        if (bunch_->alive[i]) {
            sx += bunch_->x[i]; sx2 += bunch_->x[i]*bunch_->x[i];
            sy += bunch_->y[i]; sy2 += bunch_->y[i]*bunch_->y[i];
            sz += bunch_->z[i]; sz2 += bunch_->z[i]*bunch_->z[i];
            sd += bunch_->delta[i]; sd2 += bunch_->delta[i]*bunch_->delta[i];
            alive_count++;
        }
    }

    if (alive_count == 0) return {turn, 0, 0, 0, 0, 0};

    auto calc_rms = [&](double s, double s2) {
        double m = s / alive_count;
        return std::sqrt(std::max(s2 / alive_count - m*m, 0.0));
    };

    return {
        turn,
        alive_count,
        calc_rms(sx, sx2),
        calc_rms(sy, sy2),
        calc_rms(sz, sz2),
        calc_rms(sd, sd2)
    };
}

} // namespace circular
} // namespace dase
