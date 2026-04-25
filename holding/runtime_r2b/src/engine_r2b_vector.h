#pragma once

#include <cstddef>
#include <cstdint>
#include <random>
#include <vector>

namespace analog_r2b {

struct EngineConfig {
    std::size_t node_count = 128;
    double dt = 0.05;
    double drive = 0.20;
    double node_decay = 0.28;
    double edge_baseline_admissibility = 0.55;
    double edge_baseline_noise = 0.02;
    double directional_drive_gain = 0.12;
    double directional_neighbor_gain = 0.82;
    double residue_node_gain = 0.18;
    double directional_sharpen_gain = 0.28;
    double cross_inhibition_gain = 0.75;
    double node_self_saturation_gain = 0.60;
    double scaffold_suppression_gain = 0.85;
    double tension_suppression_gain = 0.18;
    double admissibility_corridor_gain = 0.22;
    double admissibility_residue_gain = 0.08;
    double admissibility_tension_gain = 0.18;
    double admissibility_scaffold_gain = 0.16;
    double admissibility_baseline_relax = 0.12;
    double residue_write_gain = 0.26;
    double residue_relax = 0.18;
    double residue_diffusion_gain = 0.10;
    double split_eligibility_write_gain = 0.85;
    double split_eligibility_relax = 0.18;
    double split_eligibility_diffusion_gain = 0.12;
    double split_eligibility_corridor_gain = 0.24;
    double split_eligibility_scaffold_suppression_gain = 0.75;
    double split_interface_gain = 0.52;
    double tension_write_gain = 0.42;
    double tension_relax = 0.14;
    double tension_scaffold_gain = 0.12;
    double tension_collapse_relax_gain = 0.24;
    double barrier_scaffold_write_gain = 0.22;
    double barrier_scaffold_relax = 0.10;
    double barrier_scaffold_diffusion_gain = 0.12;
    double barrier_scaffold_tension_gain = 0.10;
    double barrier_scaffold_commitment_gain = 1.30;
    double barrier_scaffold_collapse_relax_gain = 0.20;
    double perturbation_amplitude = 0.03;
    double corridor_edge_threshold = 0.22;
    double coexistence_edge_threshold = 0.10;
    double barrier_edge_threshold = 0.22;
    bool enable_residue = true;
    bool enable_split_eligibility = true;
    bool enable_barrier_scaffold = true;
    std::uint64_t seed = 1;
};

struct StepMetrics {
    std::uint64_t step_index = 0;
    double mean_output = 0.0;
    double mean_abs_output = 0.0;
    double output_variance = 0.0;
    double mean_total_activation = 0.0;
    double mean_forward_channel = 0.0;
    double mean_reverse_channel = 0.0;
    double mean_directional_dominance = 0.0;
    double mean_channel_coexistence = 0.0;
    double mean_split_eligibility = 0.0;
    double mean_admissibility = 0.0;
    double mean_residue = 0.0;
    double mean_tension = 0.0;
    double mean_barrier_scaffold = 0.0;
    double mean_abs_step_delta = 0.0;
    double corridor_edge_fraction = 0.0;
    double coexistence_edge_fraction = 0.0;
    double barrier_edge_fraction = 0.0;
    double dual_active_node_fraction = 0.0;
    std::size_t output_interface_count = 0;
};

class VectorEngine {
public:
    explicit VectorEngine(EngineConfig config);

    void reseed(std::uint64_t seed);
    void initialize_near_undifferentiated();
    void step();
    void run(std::uint64_t steps);

    StepMetrics compute_metrics() const;

private:
    std::size_t wrap_index(long long index) const;
    double sample_noise();

    EngineConfig config_;
    std::uint64_t current_step_ = 0;
    double last_mean_abs_step_delta_ = 0.0;
    std::mt19937_64 rng_;
    std::normal_distribution<double> noise_dist_{0.0, 1.0};

    std::vector<double> forward_;
    std::vector<double> next_forward_;
    std::vector<double> reverse_;
    std::vector<double> next_reverse_;
    std::vector<double> admissibility_;
    std::vector<double> next_admissibility_;
    std::vector<double> residue_;
    std::vector<double> next_residue_;
    std::vector<double> split_eligibility_;
    std::vector<double> next_split_eligibility_;
    std::vector<double> tension_;
    std::vector<double> next_tension_;
    std::vector<double> barrier_scaffold_;
    std::vector<double> next_barrier_scaffold_;
};

}  // namespace analog_r2b
