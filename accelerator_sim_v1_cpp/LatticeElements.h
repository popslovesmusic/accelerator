#pragma once

#include "AcceleratorEngineAVX2.h"
#include "PoissonSolver.h"
#include "FieldMap.h"
#include <cmath>
#include <vector>
#include <immintrin.h>
#include <algorithm>

namespace dase {
namespace accelerator {

/**
 * Drift element.
 */
class Drift : public LatticeElement {
public:
    explicit Drift(double length) : length_(length) {}
    
    void apply(ParticleBunchSoA& bunch) override {
        if (length_ == 0) return;
        const double L = length_;
        const int n = static_cast<int>(bunch.count);
        
        __m256d l_vec = _mm256_set1_pd(L);
        __m256d one_vec = _mm256_set1_pd(1.0);
        __m256d eps_vec = _mm256_set1_pd(1e-12);

        #pragma omp parallel for
        for (int i = 0; i < n; i += 4) {
            __m256d x = _mm256_load_pd(&bunch.x[i]);
            __m256d px = _mm256_load_pd(&bunch.px[i]);
            __m256d y = _mm256_load_pd(&bunch.y[i]);
            __m256d py = _mm256_load_pd(&bunch.py[i]);
            __m256d z = _mm256_load_pd(&bunch.z[i]);
            __m256d delta = _mm256_load_pd(&bunch.delta[i]);

            __m256d rigidity = _mm256_add_pd(one_vec, delta);
            rigidity = _mm256_max_pd(rigidity, eps_vec);
            __m256d inv_rigidity = _mm256_div_pd(one_vec, rigidity);

            x = _mm256_fmadd_pd(_mm256_mul_pd(l_vec, px), inv_rigidity, x);
            y = _mm256_fmadd_pd(_mm256_mul_pd(l_vec, py), inv_rigidity, y);
            z = _mm256_fmadd_pd(l_vec, delta, z);

            _mm256_store_pd(&bunch.x[i], x);
            _mm256_store_pd(&bunch.y[i], y);
            _mm256_store_pd(&bunch.z[i], z);
        }
    }

    std::string name() const override { return "Drift"; }

private:
    double length_;
};

/**
 * Quadrupole element.
 * Implements a 4th-order Symplectic Integrator (Yoshida).
 */
class Quadrupole : public LatticeElement {
public:
    Quadrupole(double k1, double length) : k1_(k1), length_(length) {
        const double cube_root_2 = std::pow(2.0, 1.0/3.0);
        w1_ = 1.0 / (2.0 - cube_root_2);
        w0_ = -cube_root_2 * w1_;
        
        d1_ = w1_ * length_;
        d2_ = w0_ * length_;
        d3_ = d1_;
        
        c1_ = w1_ * 0.5 * length_;
        c2_ = (w1_ + w0_) * 0.5 * length_;
        c3_ = c2_;
        c4_ = c1_;
    }

    void apply(ParticleBunchSoA& bunch) override {
        auto drift = [&](double d) { Drift(d).apply(bunch); };
        auto kick = [&](double c) {
            const double kL = k1_ * c;
            const int n = static_cast<int>(bunch.count);
            __m256d kl_vec = _mm256_set1_pd(kL);
            #pragma omp parallel for
            for (int i = 0; i < n; i += 4) {
                __m256d x = _mm256_load_pd(&bunch.x[i]);
                __m256d px = _mm256_load_pd(&bunch.px[i]);
                __m256d y = _mm256_load_pd(&bunch.y[i]);
                __m256d py = _mm256_load_pd(&bunch.py[i]);
                px = _mm256_fnmadd_pd(kl_vec, x, px);
                py = _mm256_fmadd_pd(kl_vec, y, py);
                _mm256_store_pd(&bunch.px[i], px);
                _mm256_store_pd(&bunch.py[i], py);
            }
        };

        drift(c1_); kick(d1_);
        drift(c2_); kick(d2_);
        drift(c3_); kick(d3_);
        drift(c4_);
    }

    std::string name() const override { return "Quadrupole"; }

private:
    double k1_, length_;
    double w1_, w0_, c1_, c2_, c3_, c4_, d1_, d2_, d3_;
};

/**
 * RF Cavity element.
 */
class RFCavity : public LatticeElement {
public:
    RFCavity(double voltage, double phase, double harmonic) 
        : voltage_(voltage), phase_(phase), harmonic_(harmonic) {}

    void apply(ParticleBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        __m256d h_vec = _mm256_set1_pd(harmonic_);
        __m256d p_vec = _mm256_set1_pd(phase_);

        #pragma omp parallel for
        for (int i = 0; i < n; i += 4) {
            __m256d z = _mm256_load_pd(&bunch.z[i]);
            __m256d delta = _mm256_load_pd(&bunch.delta[i]);
            
            alignas(32) double args[4];
            __m256d arg = _mm256_fmadd_pd(h_vec, z, p_vec);
            _mm256_store_pd(args, arg);
            
            alignas(32) double deltas[4];
            _mm256_store_pd(deltas, delta);
            
            for(int j=0; j<4; ++j) {
                deltas[j] += voltage_ * std::sin(args[j]);
            }
            
            delta = _mm256_load_pd(deltas);
            _mm256_store_pd(&bunch.delta[i], delta);
        }
    }

    std::string name() const override { return "RFCavity"; }

private:
    double voltage_;
    double phase_;
    double harmonic_;
};

/**
 * Space Charge 2D element.
 */
class SpaceCharge2D : public LatticeElement {
public:
    SpaceCharge2D(int nx, int ny, double width, double height) 
        : nx_(nx), ny_(ny), width_(width), height_(height) {
        solver_ = std::make_unique<PoissonSolver2D>(nx, ny, width/nx, height/ny);
        rho_grid_.resize(nx * ny, 0.0);
        phi_grid_.resize(nx * ny, 0.0);
    }

    void apply(ParticleBunchSoA& bunch) override {
        std::fill(rho_grid_.begin(), rho_grid_.end(), 0.0);
        const double dx = width_ / nx_;
        const double dy = height_ / ny_;
        const double inv_dx = 1.0 / dx;
        const double inv_dy = 1.0 / dy;

        for (size_t i = 0; i < bunch.count; ++i) {
            if (!bunch.alive[i]) continue;
            int ix = static_cast<int>((bunch.x[i] + width_*0.5) * inv_dx);
            int iy = static_cast<int>((bunch.y[i] + height_*0.5) * inv_dy);
            if (ix >= 0 && ix < nx_ && iy >= 0 && iy < ny_) {
                rho_grid_[iy * nx_ + ix] += 1.0;
            }
        }

        solver_->solve(rho_grid_.data(), phi_grid_.data());

        #pragma omp parallel for
        for (int i = 0; i < static_cast<int>(bunch.count); ++i) {
            if (!bunch.alive[i]) continue;
            double x_grid = (bunch.x[i] + width_*0.5) * inv_dx;
            double y_grid = (bunch.y[i] + height_*0.5) * inv_dy;
            int ix = static_cast<int>(x_grid);
            int iy = static_cast<int>(y_grid);
            if (ix > 0 && ix < nx_-1 && iy > 0 && iy < ny_-1) {
                double ex = -(phi_grid_[iy * nx_ + (ix+1)] - phi_grid_[iy * nx_ + (ix-1)]) * 0.5 * inv_dx;
                double ey = -(phi_grid_[(iy+1) * nx_ + ix] - phi_grid_[(iy-1) * nx_ + ix]) * 0.5 * inv_dy;
                bunch.px[i] += ex * 1e-6;
                bunch.py[i] += ey * 1e-6;
            }
        }
    }

    std::string name() const override { return "SpaceCharge2D"; }

private:
    int nx_, ny_;
    double width_, height_;
    std::unique_ptr<PoissonSolver2D> solver_;
    std::vector<double> rho_grid_;
    std::vector<double> phi_grid_;
};

/**
 * Field Map Element.
 */
class FieldMapElement : public LatticeElement {
public:
    FieldMapElement(std::shared_ptr<FieldMap3D> map, double length) : map_(map), length_(length) {}

    void apply(ParticleBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        const double L = length_;
        __m256d l_vec = _mm256_set1_pd(L);

        #pragma omp parallel for
        for (int i = 0; i < n; i += 4) {
            __m256d x = _mm256_load_pd(&bunch.x[i]);
            __m256d y = _mm256_load_pd(&bunch.y[i]);
            __m256d z = _mm256_load_pd(&bunch.z[i]);
            __m256d px = _mm256_load_pd(&bunch.px[i]);
            __m256d py = _mm256_load_pd(&bunch.py[i]);
            __m256d bx, by, bz;
            map_->interpolateAVX2(x, y, z, bx, by, bz);

            __m256d one = _mm256_set1_pd(1.0);
            __m256d dpx = _mm256_sub_pd(_mm256_mul_pd(py, bz), by); 
            __m256d dpy = _mm256_sub_pd(bx, _mm256_mul_pd(px, bz));

            px = _mm256_fmadd_pd(dpx, l_vec, px);
            py = _mm256_fmadd_pd(dpy, l_vec, py);

            _mm256_store_pd(&bunch.px[i], px);
            _mm256_store_pd(&bunch.py[i], py);
            
            x = _mm256_fmadd_pd(px, l_vec, x);
            y = _mm256_fmadd_pd(py, l_vec, y);
            z = _mm256_fmadd_pd(one, l_vec, z);
            
            _mm256_store_pd(&bunch.x[i], x);
            _mm256_store_pd(&bunch.y[i], y);
            _mm256_store_pd(&bunch.z[i], z);
        }
    }

    std::string name() const override { return "FieldMap"; }

private:
    std::shared_ptr<FieldMap3D> map_;
    double length_;
};

/**
 * Synchrotron Radiation Element.
 */
class SynchrotronRadiation : public LatticeElement {
public:
    SynchrotronRadiation(double loss_per_m, double excitation_std, uint64_t seed) 
        : loss_(loss_per_m), sigma_(excitation_std), prng_(seed) {}

    void apply(ParticleBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        __m256d loss_vec = _mm256_set1_pd(loss_);
        __m256d sigma_vec = _mm256_set1_pd(sigma_);

        #pragma omp parallel for
        for (int i = 0; i < n; i += 4) {
            __m256d delta = _mm256_load_pd(&bunch.delta[i]);
            delta = _mm256_sub_pd(delta, loss_vec);
            __m256d rand = prng_.next();
            __m256d noise = _mm256_mul_pd(_mm256_sub_pd(rand, _mm256_set1_pd(0.5)), sigma_vec);
            delta = _mm256_add_pd(delta, noise);
            _mm256_store_pd(&bunch.delta[i], delta);
        }
    }

    std::string name() const override { return "SynchrotronRadiation"; }

private:
    double loss_, sigma_;
    VectorizedPRNG prng_;
};

/**
 * Collimator Element.
 */
class Collimator : public LatticeElement {
public:
    Collimator(double radius) : r2_(radius * radius) {}

    void apply(ParticleBunchSoA& bunch) override {
        const int n = static_cast<int>(bunch.count);
        __m256d r2_vec = _mm256_set1_pd(r2_);
        for (int i = 0; i < n; i += 4) {
            __m256d x = _mm256_load_pd(&bunch.x[i]);
            __m256d y = _mm256_load_pd(&bunch.y[i]);
            __m256d r2_part = _mm256_add_pd(_mm256_mul_pd(x, x), _mm256_mul_pd(y, y));
            __m256d mask = _mm256_cmp_pd(r2_part, r2_vec, _CMP_LE_OQ);
            alignas(32) double results[4];
            _mm256_store_pd(results, mask);
            for(int j=0; j<4; ++j) {
                if (results[j] == 0) bunch.alive[i+j] = false;
            }
        }
    }

    std::string name() const override { return "Collimator"; }

private:
    double r2_;
};

} // namespace accelerator
} // namespace dase
