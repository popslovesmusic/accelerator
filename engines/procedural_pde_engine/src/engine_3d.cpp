#include "../include/grid.hpp"
#include "../include/fields.hpp"
#include "../include/update_rules.hpp"
#include "../include/metrics.hpp"
#include "../include/io.hpp"

#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <algorithm>

namespace pde {

void step_3d(SimulationState& state, const Grid& grid, const UpdateParams& params) {
    const size_t nx = grid.config().nx;
    const size_t ny = grid.config().ny;
    const size_t nz = grid.config().nz;
    const size_t total_cells = grid.config().total_cells();

    // Buffers for next state
    std::vector<float> next_eps(total_cells, 0.0f);
    std::vector<float> next_rho(total_cells, 0.0f);
    std::vector<float> next_R(total_cells, 0.0f);
    
    for (size_t z = 0; z < nz; ++z) {
        for (size_t y = 0; y < ny; ++y) {
            for (size_t x = 0; x < nx; ++x) {
                size_t idx = grid.index_3d(x, y, z);
                
                // 1. Compute Gradients & Laplacian
                float lap_eps = compute_laplacian_3d(state.epsilon, grid, x, y, z);
                float grad_eps_x, grad_eps_y, grad_eps_z;
                compute_gradient_3d(state.epsilon, grid, x, y, z, grad_eps_x, grad_eps_y, grad_eps_z);
                
                if (params.falsification_mode == "FV_005_gradient_collapse") {
                    grad_eps_x *= (1.0f - params.falsification_intensity);
                    grad_eps_y *= (1.0f - params.falsification_intensity);
                    grad_eps_z *= (1.0f - params.falsification_intensity);
                }
                
                float grad_R_x, grad_R_y, grad_R_z;
                compute_gradient_3d(state.R, grid, x, y, z, grad_R_x, grad_R_y, grad_R_z);
                
                // 2. Epsilon Update
                float dE = params.diff_eps * lap_eps + params.source_eps - params.damp_eps * state.epsilon[idx];
                next_eps[idx] = std::max(0.0f, state.epsilon[idx] + dE * params.dt);
                
                if (params.falsification_mode == "FV_006_noise_injection") {
                    // simple pseudo-random noise using coordinates and step
                    float noise = std::sin(x * 12.9898f + y * 78.233f + z * 31.415f + params.step_current * 37.719f) * 43758.5453f;
                    noise = noise - std::floor(noise) - 0.5f; // [-0.5, 0.5]
                    next_eps[idx] += noise * params.falsification_intensity;
                }
                
                // 3. Orientation Update
                float ix = state.I.x[idx] + params.alpha_I * grad_eps_x + params.beta_I * grad_R_x;
                float iy = state.I.y[idx] + params.alpha_I * grad_eps_y + params.beta_I * grad_R_y;
                float iz = state.I.z[idx] + params.alpha_I * grad_eps_z + params.beta_I * grad_R_z;
                
                if (params.falsification_mode == "FV_002_orientation_inversion") {
                    ix *= -1.0f;
                    iy *= -1.0f;
                    iz *= -1.0f;
                }
                
                float norm = std::sqrt(ix*ix + iy*iy + iz*iz);
                if (norm > 1e-6f) {
                    state.I.x[idx] = ix / norm;
                    state.I.y[idx] = iy / norm;
                    state.I.z[idx] = iz / norm;
                }
                
                // 4. Admissibility Update
                float A_arg = params.theta_A - std::abs(next_eps[idx]) + params.gamma_A * state.R[idx];
                if (params.falsification_mode == "FV_003_admissibility_narrowing") {
                    A_arg -= params.falsification_intensity * (params.step_current * 0.01f);
                }
                state.A[idx] = sigmoid(A_arg);
                
                if (params.falsification_mode == "FV_007_boundary_overload") {
                    state.A[idx] = 1.0f; // Force open admissibility
                }
                
                // 5. Rho Update
                float aligned_flow = state.I.x[idx] * grad_eps_x + state.I.y[idx] * grad_eps_y + state.I.z[idx] * grad_eps_z;
                float drho = state.A[idx] * state.rho[idx] + params.kappa_rho * aligned_flow;
                next_rho[idx] = std::max(0.0f, state.rho[idx] + drho * params.dt); // Ensure non-negative
                
                // 6. Residue Update
                float R_change = params.write_rate_R * state.A[idx] * std::abs(next_rho[idx] - state.rho[idx]);
                next_R[idx] = params.decay_R * state.R[idx] + R_change;
                
                if (params.falsification_mode == "FV_004_corridor_randomization" && state.corridor_flags[idx] > 0) {
                    float rand_val = std::sin(idx * 12.9898f + params.step_current * 37.719f) * 43758.5453f;
                    rand_val = rand_val - std::floor(rand_val);
                    if (rand_val < params.falsification_intensity) {
                        next_R[idx] = 0.0f;
                    }
                }
                
                // 7. Collapse & Corridor conditions
                if (state.A[idx] < params.A_min || std::abs(next_eps[idx]) > params.epsilon_max) {
                    // Local collapse
                    next_rho[idx] = 0.0f;
                }
                
                if (next_R[idx] > params.R_corridor_threshold && norm > params.I_min) {
                    state.corridor_flags[idx] = 1;
                } else {
                    state.corridor_flags[idx] = 0;
                }
            }
        }
    }
    
    if (params.falsification_mode == "FV_001_residue_scramble") {
        if (params.step_current > 0 && params.step_current % 100 == 0) {
            std::random_device rd;
            std::mt19937 g(rd());
            std::shuffle(next_R.begin(), next_R.end(), g);
        }
    }
    
    // Commit updates
    state.epsilon = std::move(next_eps);
    state.rho = std::move(next_rho);
    state.R = std::move(next_R);
}

} // namespace pde