#pragma once

#include <vector>
#include <fftw3.h>

namespace dase {
namespace accelerator {

/**
 * 2D Poisson Solver for Space Charge calculations.
 * Uses FFT-based method on a rectangular grid.
 */
class PoissonSolver2D {
public:
    PoissonSolver2D(int nx, int ny, double dx, double dy);
    ~PoissonSolver2D();

    /**
     * Solve ∇²φ = -ρ/ε₀
     * @param rho Input charge density grid (nx * ny)
     * @param phi Output potential grid (nx * ny)
     */
    void solve(const double* rho, double* phi);

private:
    int nx_, ny_;
    double dx_, dy_;
    
    fftw_complex *rho_fft_, *phi_fft_;
    fftw_plan plan_forward_, plan_backward_;
    
    std::vector<double> kernel_;

    void computeKernel();
};

} // namespace accelerator
} // namespace dase
