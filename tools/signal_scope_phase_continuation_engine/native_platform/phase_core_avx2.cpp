#include <immintrin.h>
#include <cmath>
#include <algorithm>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {

/**
 * Computes the 8-element phase vector using AVX2.
 * Weights: [2.0, 2.0, 2.0, 1.5, 1.5, 2.0, 2.0, 2.0]
 * Inputs: W (3 floats), C (1 float), E (1 float), V (3 floats)
 * Output: out (8 floats, 32-byte aligned)
 */
EXPORT void compute_phase_vector_avx2(const float* W, float C, float E, const float* V, float* out) {
    alignas(32) float temp[8];
    temp[0] = 2.0f * W[0];
    temp[1] = 2.0f * W[1];
    temp[2] = 2.0f * W[2];
    temp[3] = 1.5f * C;
    temp[4] = 1.5f * E;
    temp[5] = 2.0f * V[0];
    temp[6] = 2.0f * V[1];
    temp[7] = 2.0f * V[2];

    __m256 v = _mm256_load_ps(temp);
    
    // Normalize: v / sqrt(sum(v*v))
    __m256 v2 = _mm256_mul_ps(v, v);
    
    // Horizontal sum of 8 floats in v2
    __m128 xhigh = _mm256_extractf128_ps(v2, 1);
    __m128 xlow = _mm256_castps256_ps128(v2);
    __m128 xsum = _mm_add_ps(xlow, xhigh); // [f0+f4, f1+f5, f2+f6, f3+f7]
    
    xsum = _mm_hadd_ps(xsum, xsum); // [f0+f4+f1+f5, f2+f6+f3+f7, ...]
    xsum = _mm_hadd_ps(xsum, xsum); // [sum, sum, sum, sum]
    
    float norm_sq = _mm_cvtss_f32(xsum);
    
    if (norm_sq > 1e-18f) {
        float inv_norm = 1.0f / std::sqrt(norm_sq);
        __m256 vinv = _mm256_set1_ps(inv_norm);
        v = _mm256_mul_ps(v, vinv);
    }
    
    _mm256_store_ps(out, v);
}

/**
 * Calculates phase mismatch (1 - cosine similarity) using AVX2.
 * Inputs: phi1, phi2 (8 floats each, 32-byte aligned)
 */
EXPORT float phase_mismatch_avx2(const float* phi1, const float* phi2) {
    __m256 v1 = _mm256_load_ps(phi1);
    __m256 v2 = _mm256_load_ps(phi2);
    
    __m256 vmul = _mm256_mul_ps(v1, v2);
    
    // Horizontal sum
    __m128 xhigh = _mm256_extractf128_ps(vmul, 1);
    __m128 xlow = _mm256_castps256_ps128(vmul);
    __m128 xsum = _mm_add_ps(xlow, xhigh);
    
    xsum = _mm_hadd_ps(xsum, xsum);
    xsum = _mm_hadd_ps(xsum, xsum);
    
    float dot = _mm_cvtss_f32(xsum);
    
    // Clamp to [-1, 1]
    if (dot > 1.0f) dot = 1.0f;
    else if (dot < -1.0f) dot = -1.0f;
    
    return 1.0f - dot;
}

}
