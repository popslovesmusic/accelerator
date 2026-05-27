#pragma once

#include "fields.hpp"
#include <vector>
#include <string>

namespace pde {

struct RunMetrics {
    float residue_coherence;
    float orientation_alignment;
    float corridor_count;
    float corridor_lifetime;
    float basin_count;
    float basin_lifetime;
    float collapse_event_count;
    float collapse_locality;
    float reformation_count;
    float reformation_latency;
    float scope_fragmentation_index;
    float transport_bias;
    float asymmetry_persistence;
    
    RunMetrics() : 
        residue_coherence(0), orientation_alignment(0), corridor_count(0),
        corridor_lifetime(0), basin_count(0), basin_lifetime(0),
        collapse_event_count(0), collapse_locality(0), reformation_count(0),
        reformation_latency(0), scope_fragmentation_index(0), transport_bias(0),
        asymmetry_persistence(0) {}
};

inline RunMetrics compute_metrics_2d(const SimulationState& state, const Grid& grid) {
    RunMetrics m;
    
    float total_R = 0.0f;
    float active_cells = 0.0f;
    float sum_Ix = 0.0f;
    float sum_Iy = 0.0f;
    
    for (size_t i = 0; i < grid.config().total_cells(); ++i) {
        total_R += state.R[i];
        if (state.A[i] > 0.5f) {
            active_cells += 1.0f;
            sum_Ix += state.I.x[i];
            sum_Iy += state.I.y[i];
        }
        if (state.corridor_flags[i] > 0) {
            m.corridor_count += 1.0f;
        }
    }
    
    m.residue_coherence = active_cells > 0 ? (total_R / active_cells) : 0.0f;
    m.orientation_alignment = active_cells > 0 ? std::sqrt(sum_Ix*sum_Ix + sum_Iy*sum_Iy) / active_cells : 0.0f;
    
    return m;
}

inline RunMetrics compute_metrics_3d(const SimulationState& state, const Grid& grid) {
    RunMetrics m;
    
    float total_R = 0.0f;
    float active_cells = 0.0f;
    float sum_Ix = 0.0f;
    float sum_Iy = 0.0f;
    float sum_Iz = 0.0f;
    
    for (size_t i = 0; i < grid.config().total_cells(); ++i) {
        total_R += state.R[i];
        if (state.A[i] > 0.5f) {
            active_cells += 1.0f;
            sum_Ix += state.I.x[i];
            sum_Iy += state.I.y[i];
            sum_Iz += state.I.z[i];
        }
        if (state.corridor_flags[i] > 0) {
            m.corridor_count += 1.0f;
        }
    }
    
    m.residue_coherence = active_cells > 0 ? (total_R / active_cells) : 0.0f;
    m.orientation_alignment = active_cells > 0 ? std::sqrt(sum_Ix*sum_Ix + sum_Iy*sum_Iy + sum_Iz*sum_Iz) / active_cells : 0.0f;
    
    return m;
}

} // namespace pde
