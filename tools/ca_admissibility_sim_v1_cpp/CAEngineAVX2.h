#pragma once

#include <vector>
#include <string>
#include <memory>
#include <immintrin.h>
#include <omp.h>

namespace dase {
namespace ca {

/**
 * 2D Grid for Admissibility CA.
 * Aligned for AVX2 stencil operations.
 */
struct Grid2D {
    int width;
    int height;
    double* epsilon;
    double* R;
    double* next_epsilon; // Buffer for diffusion update

    Grid2D(int w, int h);
    ~Grid2D();

    // Aligned access
    double& getEpsilon(int x, int y) { return epsilon[y * width + x]; }
    double& getR(int x, int y) { return R[y * width + x]; }
};

/**
 * High-performance 2D Admissibility CA Engine using AVX2.
 */
class CAEngineAVX2 {
public:
    explicit CAEngineAVX2(int width, int height);
    
    void setParams(double D, double delta_R, double gamma_R);
    void initialize(double source_strength, int source_radius, double initial_residue);
    
    void step();
    
    struct Metrics {
        double active_fraction;
        double mean_mismatch;
        double mean_residue;
    };
    
    Metrics getMetrics() const;

private:
    std::unique_ptr<Grid2D> grid_;
    
    // Parameters
    double D_ = 0.1;
    double delta_R_ = 0.01;
    double gamma_R_ = 0.01;

    void updateGatedDiffusion();
    void updateResidue();
};

} // namespace ca
} // namespace dase
