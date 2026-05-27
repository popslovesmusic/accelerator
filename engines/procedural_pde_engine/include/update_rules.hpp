#pragma once

#include "fields.hpp"
#include "grid.hpp"
#include <cmath>

namespace pde {

struct UpdateParams {
    float dt;
    float diff_eps;
    float source_eps;
    float damp_eps;
    float alpha_I;
    float beta_I;
    float theta_A;
    float gamma_A;
    float kappa_rho;
    float decay_R;
    float write_rate_R;
    float A_min;
    float epsilon_max;
    float R_corridor_threshold;
    float I_min;
    
    std::string falsification_mode;
    float falsification_intensity;
    int step_current; // passed in to allow time-based effects
};

// Computes 2D Central Difference Laplacian
inline float compute_laplacian_2d(const std::vector<float>& f, const Grid& grid, size_t x, size_t y) {
    size_t nx0 = grid.neighbor_x(x, -1);
    size_t nx1 = grid.neighbor_x(x, 1);
    size_t ny0 = grid.neighbor_y(y, -1);
    size_t ny1 = grid.neighbor_y(y, 1);
    
    size_t idx = grid.index_2d(x, y);
    
    float val = f[idx];
    return f[grid.index_2d(nx0, y)] + f[grid.index_2d(nx1, y)] + 
           f[grid.index_2d(x, ny0)] + f[grid.index_2d(x, ny1)] - 4.0f * val;
}

inline float compute_laplacian_3d(const std::vector<float>& f, const Grid& grid, size_t x, size_t y, size_t z) {
    size_t nx0 = grid.neighbor_x(x, -1);
    size_t nx1 = grid.neighbor_x(x, 1);
    size_t ny0 = grid.neighbor_y(y, -1);
    size_t ny1 = grid.neighbor_y(y, 1);
    size_t nz0 = grid.neighbor_z(z, -1);
    size_t nz1 = grid.neighbor_z(z, 1);
    
    size_t idx = grid.index_3d(x, y, z);
    
    float val = f[idx];
    return f[grid.index_3d(nx0, y, z)] + f[grid.index_3d(nx1, y, z)] + 
           f[grid.index_3d(x, ny0, z)] + f[grid.index_3d(x, ny1, z)] +
           f[grid.index_3d(x, y, nz0)] + f[grid.index_3d(x, y, nz1)] - 6.0f * val;
}

// Computes 2D Gradient (Central Difference)
inline void compute_gradient_2d(const std::vector<float>& f, const Grid& grid, size_t x, size_t y, float& gx, float& gy) {
    size_t nx0 = grid.neighbor_x(x, -1);
    size_t nx1 = grid.neighbor_x(x, 1);
    size_t ny0 = grid.neighbor_y(y, -1);
    size_t ny1 = grid.neighbor_y(y, 1);
    
    gx = 0.5f * (f[grid.index_2d(nx1, y)] - f[grid.index_2d(nx0, y)]);
    gy = 0.5f * (f[grid.index_2d(x, ny1)] - f[grid.index_2d(x, ny0)]);
}

// Computes 3D Gradient (Central Difference)
inline void compute_gradient_3d(const std::vector<float>& f, const Grid& grid, size_t x, size_t y, size_t z, float& gx, float& gy, float& gz) {
    size_t nx0 = grid.neighbor_x(x, -1);
    size_t nx1 = grid.neighbor_x(x, 1);
    size_t ny0 = grid.neighbor_y(y, -1);
    size_t ny1 = grid.neighbor_y(y, 1);
    size_t nz0 = grid.neighbor_z(z, -1);
    size_t nz1 = grid.neighbor_z(z, 1);
    
    gx = 0.5f * (f[grid.index_3d(nx1, y, z)] - f[grid.index_3d(nx0, y, z)]);
    gy = 0.5f * (f[grid.index_3d(x, ny1, z)] - f[grid.index_3d(x, ny0, z)]);
    gz = 0.5f * (f[grid.index_3d(x, y, nz1)] - f[grid.index_3d(x, y, nz0)]);
}

inline float sigmoid(float x) {
    return 1.0f / (1.0f + std::exp(-x));
}

} // namespace pde
