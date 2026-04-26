#pragma once

#include "CircularEngineAVX2.h"
#include <cmath>
#include <immintrin.h>

namespace dase {
namespace circular {

/**
 * Drift element for Ring.
 */
class RingDrift : public RingElement {
public:
    explicit RingDrift(double length) : length_(length) {}
    
    void apply(RingBunchSoA& bunch) override {
        if (length_ == 0) return;
        const int n = static_cast<int>(bunch.count);
        __m256d l_vec = _mm256_set1_pd(length_);
        __m256d one = _mm256_set1_pd(1.0);
        __m256d eps = _mm256_set1_pd(1e-12);

        #pragma omp parallel for
        for (int i = 0; i < n; i += 4) {
            __m256d x = _mm256_load_pd(&bunch.x[i]);
            __m256d y = _mm256_load_pd(&bunch.y[i]);
            __m256d px = _mm256_load_pd(&bunch.px[i]);
            __m256d py = _mm256_load_pd(&bunch.py[i]);
            __m256d delta = _mm256_load_pd(&bunch.delta[i]);

            __m256d rigidity = _mm256_max_pd(_mm256_add_pd(one, delta), eps);
            __m256d inv_rigidity = _mm256_div_pd(one, rigidity);

            x = _mm256_fmadd_pd(_mm256_mul_pd(l_vec, px), inv_rigidity, x);
            y = _mm256_fmadd_pd(_mm256_mul_pd(l_vec, py), inv_rigidity, y);
            
            _mm256_store_pd(&bunch.x[i], x);
            _mm256_store_pd(&bunch.y[i], y);
        }
    }

private:
    double length_;
};

/**
 * Yoshida 4th-order Quadrupole.
 */
class RingQuadrupole : public RingElement {
public:
    RingQuadrupole(double k1, double length) : k1_(k1), length_(length) {
        const double c2 = std::pow(2.0, 1.0/3.0);
        w1 = 1.0 / (2.0 - c2);
        w0 = -c2 * w1;
        d1 = w1 * length; d2 = w0 * length; d3 = d1;
        c1 = w1 * 0.5 * length; c2_coeff = (w1+w0) * 0.5 * length; c3 = c2_coeff; c4 = c1;
    }

    void apply(RingBunchSoA& bunch) override {
        auto drift = [&](double d) { RingDrift(d).apply(bunch); };
        auto kick = [&](double c) {
            const double kL = k1_ * c;
            __m256d kl_vec = _mm256_set1_pd(kL);
            #pragma omp parallel for
            for (int i = 0; i < static_cast<int>(bunch.count); i += 4) {
                __m256d x = _mm256_load_pd(&bunch.x[i]);
                __m256d y = _mm256_load_pd(&bunch.y[i]);
                __m256d px = _mm256_load_pd(&bunch.px[i]);
                __m256d py = _mm256_load_pd(&bunch.py[i]);
                px = _mm256_fnmadd_pd(kl_vec, x, px);
                py = _mm256_fmadd_pd(kl_vec, y, py);
                _mm256_store_pd(&bunch.px[i], px);
                _mm256_store_pd(&bunch.py[i], py);
            }
        };

        drift(c1); kick(d1); drift(c2_coeff); kick(d2); drift(c3); kick(d3); drift(c4);
    }

private:
    double k1_, length_;
    double w1, w0, c1, c2_coeff, c3, c4, d1, d2, d3;
};

/**
 * RF Cavity for Ring.
 */
class RingRFCavity : public RingElement {
public:
    RingRFCavity(double voltage, double phase, double harmonic, double circumference)
        : v_(voltage), p_(phase), h_(harmonic), circ_(circumference) {}

    void apply(RingBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        const double factor = 2.0 * 3.1415926535 * h_ / circ_;
        
        #pragma omp parallel for
        for (int i = 0; i < n; ++i) {
            if (!bunch.alive[i]) continue;
            double rf_phase = factor * bunch.z[i] + p_;
            bunch.delta[i] += v_ * std::sin(rf_phase);
        }
    }

private:
    double v_, p_, h_, circ_;
};

/**
 * Physical Aperture for Ring.
 */
class RingAperture : public RingElement {
public:
    explicit RingAperture(double radius) : r2_(radius * radius) {}

    void apply(RingBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        for (int i = 0; i < n; ++i) {
            if (!bunch.alive[i]) continue;
            if (bunch.x[i]*bunch.x[i] + bunch.y[i]*bunch.y[i] > r2_) {
                bunch.alive[i] = false;
            }
        }
    }

private:
    double r2_;
};

} // namespace circular
} // namespace dase
