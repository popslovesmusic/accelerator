#pragma once

#include "grid.hpp"
#include <vector>
#include <iostream>

namespace pde {

struct VectorField {
    std::vector<float> x;
    std::vector<float> y;
    std::vector<float> z; // Empty for 2D

    VectorField(size_t size, size_t dim) : x(size, 0.0f), y(size, 0.0f) {
        if (dim == 3) {
            z.resize(size, 0.0f);
        }
    }
};

struct SimulationState {
    std::vector<float> epsilon;
    std::vector<float> rho;
    std::vector<float> R;
    std::vector<float> A;
    VectorField I;
    
    std::vector<int> basin_labels; // For tracking structures
    std::vector<int> corridor_flags; 
    
    SimulationState(const GridConfig& config) : 
        epsilon(config.total_cells(), 0.0f),
        rho(config.total_cells(), 0.0f),
        R(config.total_cells(), 0.0f),
        A(config.total_cells(), 0.0f),
        I(config.total_cells(), config.dim),
        basin_labels(config.total_cells(), 0),
        corridor_flags(config.total_cells(), 0)
    {}
};

} // namespace pde
