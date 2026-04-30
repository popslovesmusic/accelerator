#include "PoissonSolver.h"
#include <cmath>
#include <iostream>
#include <algorithm>

namespace dase {
namespace accelerator {

PoissonSolver2D::PoissonSolver2D(int nx, int ny, double dx, double dy)
    : nx_(nx), ny_(ny), dx_(dx), dy_(dy) {
    
    size_t n_complex = nx * (ny / 2 + 1); // For real-to-complex FFT
    rho_fft_ = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n_complex);
    phi_fft_ = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n_complex);
    
    // We'll use dft_r2c and dft_c2r for efficiency
    double* rho_real = new double[nx * ny];
    plan_forward_ = fftw_plan_dft_r2c_2d(nx, ny, rho_real, rho_fft_, FFTW_MEASURE);
    plan_backward_ = fftw_plan_dft_c2r_2d(nx, ny, phi_fft_, rho_real, FFTW_MEASURE);
    
    delete[] rho_real;
    
    computeKernel();
}

PoissonSolver2D::~PoissonSolver2D() {
    fftw_destroy_plan(plan_forward_);
    fftw_destroy_plan(plan_backward_);
    fftw_free(rho_fft_);
    fftw_free(phi_fft_);
}

void PoissonSolver2D::computeKernel() {
    size_t n_complex = nx_ * (ny_ / 2 + 1);
    kernel_.resize(n_complex);
    
    const double pi = 3.14159265358979323846;
    
    for (int i = 0; i < nx_; ++i) {
        for (int j = 0; j < (ny_ / 2 + 1); ++j) {
            double kx = 2.0 * pi * (i > nx_/2 ? i - nx_ : i) / (nx_ * dx_);
            double ky = 2.0 * pi * j / (ny_ * dy_);
            
            double k2 = kx*kx + ky*ky;
            if (k2 == 0) {
                kernel_[i * (ny_/2 + 1) + j] = 0.0;
            } else {
                kernel_[i * (ny_/2 + 1) + j] = 1.0 / k2;
            }
        }
    }
}

void PoissonSolver2D::solve(const double* rho, double* phi) {
    // 1. Forward FFT
    // Note: cast away const for fftw_execute_dft_r2c (it doesn't modify input if plan is MEASURE or PATIENT)
    fftw_execute_dft_r2c(plan_forward_, const_cast<double*>(rho), rho_fft_);
    
    // 2. Multiply by Kernel in Frequency Domain
    size_t n_complex = nx_ * (ny_ / 2 + 1);
    for (size_t i = 0; i < n_complex; ++i) {
        phi_fft_[i][0] = rho_fft_[i][0] * kernel_[i];
        phi_fft_[i][1] = rho_fft_[i][1] * kernel_[i];
    }
    
    // 3. Backward FFT
    fftw_execute_dft_c2r(plan_backward_, phi_fft_, phi);
    
    // 4. Normalize
    double norm = 1.0 / (nx_ * ny_);
    for (int i = 0; i < nx_ * ny_; ++i) {
        phi[i] *= norm;
    }
}

} // namespace accelerator
} // namespace dase
