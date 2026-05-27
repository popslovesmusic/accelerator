#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <nlohmann/json.hpp>

#include "../include/grid.hpp"
#include "../include/fields.hpp"
#include "../include/update_rules.hpp"
#include "../include/metrics.hpp"
#include "../include/io.hpp"

using json = nlohmann::json;

namespace pde {
    void step_2d(SimulationState& state, const Grid& grid, const UpdateParams& params);
    void step_3d(SimulationState& state, const Grid& grid, const UpdateParams& params);
}

void initialize_state(pde::SimulationState& state, const pde::Grid& grid, int seed) {
    std::mt19937 gen(seed);
    std::uniform_real_distribution<float> dis_eps(0.0f, 0.1f);
    std::uniform_real_distribution<float> dis_rho(0.1f, 0.3f);
    
    for (size_t i = 0; i < grid.config().total_cells(); ++i) {
        state.epsilon[i] = dis_eps(gen);
        state.rho[i] = dis_rho(gen);
        state.R[i] = 0.0f;
    }
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <config_file> <output_dir>\n";
        return 1;
    }

    std::string config_path = argv[1];
    std::string output_dir = argv[2];

    std::ifstream config_file(config_path);
    if (!config_file.is_open()) {
        std::cerr << "Failed to open config file: " << config_path << "\n";
        return 1;
    }

    json config;
    config_file >> config;

    pde::GridConfig grid_cfg;
    grid_cfg.dim = config.value("dimension", 2);
    grid_cfg.nx = config.value("nx", 256);
    grid_cfg.ny = config.value("ny", 256);
    grid_cfg.nz = config.value("nz", 1);
    grid_cfg.boundary = pde::BoundaryCondition::PERIODIC;

    pde::UpdateParams params;
    params.dt = config.value("dt", 0.01f);
    params.diff_eps = config.value("diff_eps", 0.1f);
    params.source_eps = config.value("source_eps", 0.01f);
    params.damp_eps = config.value("damp_eps", 0.05f);
    params.alpha_I = config.value("alpha_I", 0.2f);
    params.beta_I = config.value("beta_I", 0.8f);
    params.theta_A = config.value("theta_A", 1.0f);
    params.gamma_A = config.value("gamma_A", 2.0f);
    params.kappa_rho = config.value("kappa_rho", 0.5f);
    params.decay_R = config.value("decay_R", 0.99f);
    params.write_rate_R = config.value("write_rate_R", 0.1f);
    params.A_min = config.value("A_min", 0.1f);
    params.epsilon_max = config.value("epsilon_max", 10.0f);
    params.R_corridor_threshold = config.value("R_corridor_threshold", 0.5f);
    params.I_min = config.value("I_min", 0.2f);
    
    params.falsification_mode = config.value("falsification_mode", "");
    params.falsification_intensity = config.value("falsification_intensity", 1.0f);

    int steps = config.value("steps", 2000);
    int seed = config.value("seed", 42);
    int snapshot_interval = config.value("snapshot_interval", 100);

    pde::Grid grid(grid_cfg);
    pde::SimulationState state(grid_cfg);

    initialize_state(state, grid, seed);

    std::string metrics_path = output_dir + "/metrics_timeseries.csv";
    std::ofstream metrics_file(metrics_path);
    metrics_file << "step,residue_coherence,orientation_alignment,corridor_count\n";

    for (int step = 0; step < steps; ++step) {
        params.step_current = step;
        if (grid_cfg.dim == 2) {
            pde::step_2d(state, grid, params);
        } else if (grid_cfg.dim == 3) {
            pde::step_3d(state, grid, params);
        }

        if (step % snapshot_interval == 0 || step == steps - 1) {
            pde::RunMetrics metrics;
            if (grid_cfg.dim == 2) {
                metrics = pde::compute_metrics_2d(state, grid);
            } else if (grid_cfg.dim == 3) {
                metrics = pde::compute_metrics_3d(state, grid);
            }
            
            metrics_file << step << "," 
                         << metrics.residue_coherence << ","
                         << metrics.orientation_alignment << ","
                         << metrics.corridor_count << "\n";
                         
            // For now, reuse save_snapshot_2d for 3D as it just dumps the 1D arrays
            pde::save_snapshot_2d(output_dir + "/field_snapshot_" + std::to_string(step) + ".bin", state, step);
        }
    }

    // Save final summary
    pde::RunMetrics final_metrics;
    if (grid_cfg.dim == 2) {
        final_metrics = pde::compute_metrics_2d(state, grid);
    } else if (grid_cfg.dim == 3) {
        final_metrics = pde::compute_metrics_3d(state, grid);
    }
    
    json summary;
    summary["final_residue_coherence"] = final_metrics.residue_coherence;
    summary["final_orientation_alignment"] = final_metrics.orientation_alignment;
    summary["final_corridor_count"] = final_metrics.corridor_count;
    
    std::ofstream summary_file(output_dir + "/summary_metrics.json");
    summary_file << summary.dump(4);

    return 0;
}
