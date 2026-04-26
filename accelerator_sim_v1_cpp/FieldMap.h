#pragma once

#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <immintrin.h>

namespace dase {
namespace accelerator {

/**
 * 3D Field Map for Magnetic/RF fields.
 * Performs trilinear interpolation on a regular grid.
 */
class FieldMap3D {
public:
    FieldMap3D(int nx, int ny, int nz, double dx, double dy, double dz, double x0, double y0, double z0)
        : nx_(nx), ny_(ny), nz_(nz), dx_(dx), dy_(dy), dz_(dz), x0_(x0), y0_(y0), z0_(z0) {
        bx_.resize(nx * ny * nz, 0.0);
        by_.resize(nx * ny * nz, 0.0);
        bz_.resize(nx * ny * nz, 0.0);
    }

    // Simple setter for filling the map
    void setField(int ix, int iy, int iz, double bx, double by, double bz) {
        int idx = (iz * ny_ + iy) * nx_ + ix;
        bx_[idx] = bx;
        by_[idx] = by;
        bz_[idx] = bz;
    }

    /**
     * Vectorized trilinear interpolation for 4 particles.
     */
    void interpolateAVX2(const __m256d x, const __m256d y, const __m256d z,
                         __m256d& bx_out, __m256d& by_out, __m256d& bz_out) const {
        // Implementation note: Trilinear interpolation is compute-heavy.
        // We convert coordinates to grid indices, load the 8 surrounding points, and blend.
        
        alignas(32) double px[4], py[4], pz[4];
        _mm256_store_pd(px, x);
        _mm256_store_pd(py, y);
        _mm256_store_pd(pz, z);

        alignas(32) double rbx[4], rby[4], rbz[4];

        for (int i = 0; i < 4; ++i) {
            double gx = (px[i] - x0_) / dx_;
            double gy = (py[i] - y0_) / dy_;
            double gz = (pz[i] - z0_) / dz_;

            int ix = static_cast<int>(std::floor(gx));
            int iy = static_cast<int>(std::floor(gy));
            int iz = static_cast<int>(std::floor(gz));

            if (ix < 0 || ix >= nx_ - 1 || iy < 0 || iy >= ny_ - 1 || iz < 0 || iz >= nz_ - 1) {
                rbx[i] = rby[i] = rbz[i] = 0.0;
                continue;
            }

            double fx = gx - ix;
            double fy = gy - iy;
            double fz = gz - iz;

            auto get = [&](int ox, int oy, int oz) {
                return (iz + oz) * ny_ * nx_ + (iy + oy) * nx_ + (ix + ox);
            };

            // Trilinear interpolation logic
            auto interp = [&](const std::vector<double>& v) {
                double c000 = v[get(0,0,0)];
                double c100 = v[get(1,0,0)];
                double c010 = v[get(0,1,0)];
                double c110 = v[get(1,1,0)];
                double c001 = v[get(0,0,1)];
                double c101 = v[get(1,0,1)];
                double c011 = v[get(0,1,1)];
                double c111 = v[get(1,1,1)];

                double c00 = c000 * (1-fx) + c100 * fx;
                double c01 = c001 * (1-fx) + c101 * fx;
                double c10 = c010 * (1-fx) + c110 * fx;
                double c11 = c011 * (1-fx) + c111 * fx;

                double c0 = c00 * (1-fy) + c10 * fy;
                double c1 = c01 * (1-fy) + c11 * fy;

                return c0 * (1-fz) + c1 * fz;
            };

            rbx[i] = interp(bx_);
            rby[i] = interp(by_);
            rbz[i] = interp(bz_);
        }

        bx_out = _mm256_load_pd(rbx);
        by_out = _mm256_load_pd(rby);
        bz_out = _mm256_load_pd(rbz);
    }

private:
    int nx_, ny_, nz_;
    double dx_, dy_, dz_;
    double x0_, y0_, z0_;
    std::vector<double> bx_, by_, bz_;
};

/**
 * Vectorized PRNG (Xorshift128+)
 */
struct VectorizedPRNG {
    __m256i s0, s1;

    VectorizedPRNG(uint64_t seed) {
        s0 = _mm256_set1_epi64x(seed ^ 0xDEADBEEF);
        s1 = _mm256_set1_epi64x(seed ^ 0xCAFEBABE);
    }

    // Generate 4 doubles in [0, 1)
    __m256d next() {
        // Simple Xorshift128+ implementation in AVX2
        __m256i x = s0;
        __m256i y = s1;
        s0 = y;
        x = _mm256_xor_si256(x, _mm256_slli_epi64(x, 23));
        s1 = _mm256_xor_si256(_mm256_xor_si256(x, y), 
             _mm256_xor_si256(_mm256_srli_epi64(x, 17), _mm256_srli_epi64(y, 26)));
        
        __m256i res = _mm256_add_epi64(s1, y);
        // Map to double [0, 1)
        __m256i mask = _mm256_set1_epi64x(0x000FFFFFFFFFFFFF);
        __m256d one = _mm256_set1_pd(1.0);
        __m256d val = _mm256_cvtepi64_pd(_mm256_and_si256(res, mask));
        return _mm256_div_pd(val, _mm256_set1_pd(4503599627370496.0)); // 2^52
    }
};

} // namespace accelerator
} // namespace dase
