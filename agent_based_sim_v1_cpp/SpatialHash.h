#pragma once

#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>

namespace dase {
namespace swarm {

/**
 * 2D Spatial Hash for Phase-Space (x, p).
 * Optimizes neighbor search for R_c radius.
 */
class SpatialHash2D {
public:
    SpatialHash2D(double cell_size, size_t n_agents) 
        : cell_size_(cell_size), inv_cell_size_(1.0 / cell_size) {
        head_.resize(4096, -1); // Hash table size
        next_.resize(n_agents, -1);
    }

    void clear() {
        std::fill(head_.begin(), head_.end(), -1);
    }

    uint32_t hash(double x, double p) const {
        int ix = static_cast<int>(std::floor(x * inv_cell_size_));
        int ip = static_cast<int>(std::floor(p * inv_cell_size_));
        // Simple Cantor-like hash or XOR
        return (static_cast<uint32_t>(ix * 73856093) ^ 
                static_cast<uint32_t>(ip * 19349663)) % head_.size();
    }

    void build(const double* x, const double* p, size_t n) {
        clear();
        for (size_t i = 0; i < n; ++i) {
            uint32_t h = hash(x[i], p[i]);
            next_[i] = head_[h];
            head_[h] = static_cast<int>(i);
        }
    }

    /**
     * Finds neighbors in a given cell and its 8 neighbors.
     * For simplicity here, we return a list or use a callback.
     */
    template<typename Callback>
    void query(double x, double p, double r, const double* ax, const double* ap, Callback cb) const {
        double r2 = r * r;
        int ix_start = static_cast<int>(std::floor((x - r) * inv_cell_size_));
        int ix_end = static_cast<int>(std::floor((x + r) * inv_cell_size_));
        int ip_start = static_cast<int>(std::floor((p - r) * inv_cell_size_));
        int ip_end = static_cast<int>(std::floor((p + r) * inv_cell_size_));

        for (int ix = ix_start; ix <= ix_end; ++ix) {
            for (int ip = ip_start; ip <= ip_end; ++ip) {
                uint32_t h = (static_cast<uint32_t>(ix * 73856093) ^ 
                             static_cast<uint32_t>(ip * 19349663)) % head_.size();
                
                int curr = head_[h];
                while (curr != -1) {
                    double dx = x - ax[curr];
                    double dp = p - ap[curr];
                    if (dx*dx + dp*dp < r2) {
                        cb(curr);
                    }
                    curr = next_[curr];
                }
            }
        }
    }

private:
    double cell_size_;
    double inv_cell_size_;
    std::vector<int> head_;
    std::vector<int> next_;
};

} // namespace swarm
} // namespace dase
