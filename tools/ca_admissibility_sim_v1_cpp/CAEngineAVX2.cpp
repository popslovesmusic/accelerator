#include "CAEngineAVX2.h"
#include <iostream>
#include <cmath>
#include <algorithm>
#include <immintrin.h>

namespace dase {
namespace ca {

Grid2D::Grid2D(int w, int h) : width(w), height(h) {
    size_t n = static_cast<size_t>(w) * h;
    epsilon = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    R = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
    next_epsilon = static_cast<double*>(_mm_malloc(n * sizeof(double), 32));
}

Grid2D::~Grid2D() {
    _mm_free(epsilon);
    _mm_free(R);
    _mm_free(next_epsilon);
}

CAEngineAVX2::CAEngineAVX2(int width, int height) {
    grid_ = std::make_unique<Grid2D>(width, height);
}

void CAEngineAVX2::setParams(double D, double delta_R, double gamma_R) {
    D_ = D; delta_R_ = delta_R; gamma_R_ = gamma_R;
}

void CAEngineAVX2::initialize(double source_strength, int source_radius, double initial_residue) {
    int w = grid_->width;
    int h = grid_->height;
    int cx = w / 2;
    int cy = h / 2;
    double r2 = source_radius * source_radius;

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int idx = y * w + x;
            double dx = x - cx;
            double dy = y - cy;
            grid_->epsilon[idx] = (dx*dx + dy*dy <= r2) ? source_strength : 0.0;
            grid_->R[idx] = initial_residue;
            grid_->next_epsilon[idx] = grid_->epsilon[idx];
        }
    }
}

void CAEngineAVX2::updateGatedDiffusion() {
    const int w = grid_->width;
    const int h = grid_->height;
    const __m256d d_vec = _mm256_set1_pd(D_);
    const __m256d four_vec = _mm256_set1_pd(4.0);

    #pragma omp parallel for
    for (int y = 1; y < h - 1; ++y) {
        for (int x = 0; x < w; x += 4) {
            if (x == 0 || x + 4 >= w) { // Simple boundary scalar for edges
                 for(int k=0; k<4 && x+k < w; ++k) {
                     int idx = y * w + (x+k);
                     double grad = std::abs(grid_->epsilon[idx] - grid_->epsilon[idx-1]) + 
                                   std::abs(grid_->epsilon[idx] - grid_->epsilon[idx+1]) +
                                   std::abs(grid_->epsilon[idx] - grid_->epsilon[idx-w]) +
                                   std::abs(grid_->epsilon[idx] - grid_->epsilon[idx+w]);
                     if (grad > grid_->R[idx]) {
                         double lap = grid_->epsilon[idx-1] + grid_->epsilon[idx+1] + 
                                      grid_->epsilon[idx-w] + grid_->epsilon[idx+w] - 4*grid_->epsilon[idx];
                         grid_->next_epsilon[idx] = grid_->epsilon[idx] + D_ * lap;
                     } else {
                         grid_->next_epsilon[idx] = grid_->epsilon[idx];
                     }
                 }
                 continue;
            }

            // Load vectors
            int idx = y * w + x;
            __m256d e_curr = _mm256_load_pd(&grid_->epsilon[idx]);
            __m256d e_up   = _mm256_load_pd(&grid_->epsilon[idx - w]);
            __m256d e_down = _mm256_load_pd(&grid_->epsilon[idx + w]);
            __m256d e_left = _mm256_loadu_pd(&grid_->epsilon[idx - 1]);
            __m256d e_right= _mm256_loadu_pd(&grid_->epsilon[idx + 1]);
            __m256d r_curr = _mm256_load_pd(&grid_->R[idx]);

            // Calculate gradient magnitude
            __m256d g_up = _mm256_andnot_pd(_mm256_set1_pd(-0.0), _mm256_sub_pd(e_curr, e_up));
            __m256d g_down = _mm256_andnot_pd(_mm256_set1_pd(-0.0), _mm256_sub_pd(e_curr, e_down));
            __m256d g_left = _mm256_andnot_pd(_mm256_set1_pd(-0.0), _mm256_sub_pd(e_curr, e_left));
            __m256d g_right = _mm256_andnot_pd(_mm256_set1_pd(-0.0), _mm256_sub_pd(e_curr, e_right));
            __m256d grad = _mm256_add_pd(_mm256_add_pd(g_up, g_down), _mm256_add_pd(g_left, g_right));

            // Admissibility Mask
            __m256d mask = _mm256_cmp_pd(grad, r_curr, _CMP_GT_OQ);

            // Laplacian
            __m256d lap = _mm256_add_pd(_mm256_add_pd(e_up, e_down), _mm256_add_pd(e_left, e_right));
            lap = _mm256_sub_pd(lap, _mm256_mul_pd(four_vec, e_curr));

            // Kick
            __m256d kick = _mm256_mul_pd(d_vec, lap);
            __m256d gated_kick = _mm256_and_pd(mask, kick);
            __m256d next_e = _mm256_add_pd(e_curr, gated_kick);

            _mm256_store_pd(&grid_->next_epsilon[idx], next_e);
        }
    }
    std::swap(grid_->epsilon, grid_->next_epsilon);
}

void CAEngineAVX2::updateResidue() {
    const int n = grid_->width * grid_->height;
    const __m256d one_minus_gamma = _mm256_set1_pd(1.0 - gamma_R_);
    const __m256d delta_vec = _mm256_set1_pd(delta_R_);

    #pragma omp parallel for
    for (int i = 0; i < n; i += 4) {
        __m256d r = _mm256_load_pd(&grid_->R[i]);
        __m256d e_prev = _mm256_load_pd(&grid_->epsilon[i]);
        __m256d e_next = _mm256_load_pd(&grid_->next_epsilon[i]); // epsilon is now next_epsilon swapped
        
        // Activity detection: did epsilon change?
        __m256d diff = _mm256_sub_pd(e_next, e_prev);
        __m256d abs_diff = _mm256_andnot_pd(_mm256_set1_pd(-0.0), diff);
        __m256d active_mask = _mm256_cmp_pd(abs_diff, _mm256_setzero_pd(), _CMP_GT_OQ);

        r = _mm256_mul_pd(r, one_minus_gamma);
        __m256d growth = _mm256_and_pd(active_mask, delta_vec);
        r = _mm256_add_pd(r, growth);

        _mm256_store_pd(&grid_->R[i], r);
    }
}

void CAEngineAVX2::step() {
    // 1. Snapshot current epsilon to next_epsilon to detect activity in updateResidue
    std::copy(grid_->epsilon, grid_->epsilon + grid_->width * grid_->height, grid_->next_epsilon);
    
    // 2. Diffuse (overwrites grid_->epsilon)
    updateGatedDiffusion();
    
    // 3. Update R based on epsilon change (using grid_->next_epsilon which was snapshotted)
    updateResidue();
}

CAEngineAVX2::Metrics CAEngineAVX2::getMetrics() const {
    const int n = grid_->width * grid_->height;
    double sum_e = 0, sum_r = 0;
    int active_count = 0;

    for (int i = 0; i < n; ++i) {
        sum_e += grid_->epsilon[i];
        sum_r += grid_->R[i];
        if (grid_->epsilon[i] > 1e-6) active_count++;
    }

    return {
        static_cast<double>(active_count) / n,
        sum_e / n,
        sum_r / n
    };
}

} // namespace ca
} // namespace dase
