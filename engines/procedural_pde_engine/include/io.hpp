#pragma once

#include "fields.hpp"
#include <string>
#include <fstream>
#include <stdexcept>

namespace pde {

inline void save_snapshot_2d(const std::string& path, const SimulationState& state, size_t step) {
    // Save to raw binary for efficient analysis later
    std::ofstream out(path, std::ios::binary);
    if (!out) {
        throw std::runtime_error("Failed to open file for writing: " + path);
    }
    
    size_t n = state.epsilon.size();
    out.write(reinterpret_cast<const char*>(state.epsilon.data()), n * sizeof(float));
    out.write(reinterpret_cast<const char*>(state.R.data()), n * sizeof(float));
    out.write(reinterpret_cast<const char*>(state.A.data()), n * sizeof(float));
    out.write(reinterpret_cast<const char*>(state.I.x.data()), n * sizeof(float));
    out.write(reinterpret_cast<const char*>(state.I.y.data()), n * sizeof(float));
}

} // namespace pde
