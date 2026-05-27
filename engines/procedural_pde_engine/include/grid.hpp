#pragma once

#include <vector>
#include <cstddef>
#include <string>
#include <stdexcept>

namespace pde {

enum class BoundaryCondition {
    PERIODIC,
    DIRICHLET,
    NEUMANN
};

struct GridConfig {
    size_t dim;
    size_t nx;
    size_t ny;
    size_t nz;
    BoundaryCondition boundary;

    size_t total_cells() const {
        if (dim == 2) return nx * ny;
        if (dim == 3) return nx * ny * nz;
        return 0;
    }
};

class Grid {
public:
    Grid(const GridConfig& config) : config_(config) {}

    // Linear index mapping
    inline size_t index_2d(size_t x, size_t y) const {
        return y * config_.nx + x;
    }

    inline size_t index_3d(size_t x, size_t y, size_t z) const {
        return z * config_.nx * config_.ny + y * config_.nx + x;
    }
    
    // Neighbor access with boundary conditions (Periodic only for now)
    inline size_t neighbor_x(size_t x, int dx) const {
        long long nx = static_cast<long long>(x) + dx;
        long long max_x = static_cast<long long>(config_.nx);
        if (nx < 0) return (nx % max_x + max_x) % max_x;
        return nx % max_x;
    }
    
    inline size_t neighbor_y(size_t y, int dy) const {
        long long ny = static_cast<long long>(y) + dy;
        long long max_y = static_cast<long long>(config_.ny);
        if (ny < 0) return (ny % max_y + max_y) % max_y;
        return ny % max_y;
    }
    
    inline size_t neighbor_z(size_t z, int dz) const {
        long long nz = static_cast<long long>(z) + dz;
        long long max_z = static_cast<long long>(config_.nz);
        if (nz < 0) return (nz % max_z + max_z) % max_z;
        return nz % max_z;
    }
    
    const GridConfig& config() const { return config_; }

private:
    GridConfig config_;
};

} // namespace pde
