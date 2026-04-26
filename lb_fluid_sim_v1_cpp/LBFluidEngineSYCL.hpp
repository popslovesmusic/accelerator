#pragma once
#include <sycl/sycl.hpp>
#include <iostream>
#include <vector>
#include <cmath>

namespace dase {
namespace fluid {

/**
 * GPU-Accelerated D2Q9 Lattice Boltzmann Fluid Engine using SYCL.
 * Optimized for Intel UHD 770 (FP32).
 */
class LBFluidEngineSYCL {
public:
    LBFluidEngineSYCL(int nx, int ny) : nx_(nx), ny_(ny), q_(sycl::default_selector_v) {
        size_t n = static_cast<size_t>(nx) * ny;
        
        // 9 distributions per cell
        f_in = sycl::malloc_shared<float>(9 * n, q_);
        f_out = sycl::malloc_shared<float>(9 * n, q_);
        rho = sycl::malloc_shared<float>(n, q_);
        ux = sycl::malloc_shared<float>(n, q_);
        uy = sycl::malloc_shared<float>(n, q_);
        mask = sycl::malloc_shared<uint8_t>(n, q_); // 1 for wall, 0 for fluid
        
        std::cout << "LB Fluid SYCL Engine Initialized on: " 
                  << q_.get_device().get_info<sycl::info::device::name>() << " (" << nx << "x" << ny << ")" << std::endl;
        
        // Initialize weights and directions (on host for reference)
        w[0] = 4.0f/9.0f;
        w[1] = 1.0f/9.0f; w[2] = 1.0f/9.0f; w[3] = 1.0f/9.0f; w[4] = 1.0f/9.0f;
        w[5] = 1.0f/36.0f; w[6] = 1.0f/36.0f; w[7] = 1.0f/36.0f; w[8] = 1.0f/36.0f;
        
        ex[0] = 0; ey[0] = 0;
        ex[1] = 1; ey[1] = 0;
        ex[2] = 0; ey[2] = 1;
        ex[3] = -1; ey[3] = 0;
        ex[4] = 0; ey[4] = -1;
        ex[5] = 1; ey[5] = 1;
        ex[6] = -1; ey[6] = 1;
        ex[7] = -1; ey[7] = -1;
        ex[8] = 1; ey[8] = -1;
        
        opp[0]=0; opp[1]=3; opp[2]=4; opp[3]=1; opp[4]=2; opp[5]=7; opp[6]=8; opp[7]=5; opp[8]=6;
    }

    ~LBFluidEngineSYCL() {
        sycl::free(f_in, q_);
        sycl::free(f_out, q_);
        sycl::free(rho, q_);
        sycl::free(ux, q_);
        sycl::free(uy, q_);
        sycl::free(mask, q_);
    }

    void step(float tau, float u_inlet) {
        const int nx = nx_;
        const int ny = ny_;
        const float omega = 1.0f / tau;
        
        // Pointers for kernel
        auto fi_ptr = f_in;
        auto fo_ptr = f_out;
        auto r_ptr = rho;
        auto ux_ptr = ux;
        auto uy_ptr = uy;
        auto m_ptr = mask;

        // D2Q9 constants as local arrays in lambda or capture
        const float cw[9] = {4.0f/9.0f, 1.0f/9.0f, 1.0f/9.0f, 1.0f/9.0f, 1.0f/9.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f};
        const int cex[9] = {0, 1, 0, -1, 0, 1, -1, -1, 1};
        const int cey[9] = {0, 0, 1, 0, -1, 1, 1, -1, -1};
        const int copp[9] = {0, 3, 4, 1, 2, 7, 8, 5, 6};

        // Main Kernel: Collision and Pull-Streaming
        q_.parallel_for(sycl::range<2>(ny, nx), [=](sycl::id<2> id) {
            int y = (int)id[0];
            int x = (int)id[1];
            int idx = y * nx + x;

            if (m_ptr[idx]) {
                // Bounce-back logic for walls
                for (int i = 0; i < 9; ++i) {
                    fo_ptr[i * nx * ny + idx] = fi_ptr[copp[i] * nx * ny + idx];
                }
                return;
            }

            // Compute macroscopic quantities
            float cur_rho = 0;
            float cur_ux = 0;
            float cur_uy = 0;
            
            for (int i = 0; i < 9; ++i) {
                float val = fi_ptr[i * nx * ny + idx];
                cur_rho += val;
                cur_ux += val * cex[i];
                cur_uy += val * cey[i];
            }
            
            // Boundary condition: Inlet (left wall)
            if (x == 0) {
                cur_ux = u_inlet;
                cur_uy = 0.0f;
            }

            cur_ux /= cur_rho;
            cur_uy /= cur_rho;
            
            r_ptr[idx] = cur_rho;
            ux_ptr[idx] = cur_ux;
            uy_ptr[idx] = cur_uy;

            // Collision and Streaming (Pull)
            float u2 = cur_ux * cur_ux + cur_uy * cur_uy;
            for (int i = 0; i < 9; ++i) {
                float eu = cex[i] * cur_ux + cey[i] * cur_uy;
                float feq = cw[i] * cur_rho * (1.0f + 3.0f * eu + 4.5f * eu * eu - 1.5f * u2);
                float f_val = fi_ptr[i * nx * ny + idx];
                
                // Relax towards equilibrium
                f_val = f_val - omega * (f_val - feq);
                
                // Stream to neighbors (Pull: we read from previous, write to next with shift)
                int nx_target = (x + cex[i] + nx) % nx;
                int ny_target = (y + cey[i] + ny) % ny;
                fo_ptr[i * nx * ny + (ny_target * nx + nx_target)] = f_val;
            }
        }).wait();

        // Swap f_in and f_out
        std::swap(f_in, f_out);
    }

    float *f_in, *f_out, *rho, *ux, *uy;
    uint8_t *mask;
    float w[9];
    int ex[9], ey[9], opp[9];

private:
    int nx_, ny_;
    sycl::queue q_;
};

} // namespace fluid
} // namespace dase
