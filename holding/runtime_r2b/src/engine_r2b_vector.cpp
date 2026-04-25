#include "engine_r2b_vector.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace analog_r2b {

namespace {

double clamp_value(double value, double minimum, double maximum) {
    return std::max(minimum, std::min(value, maximum));
}

double variance_of(const std::vector<double>& values, double mean_value) {
    if (values.empty()) {
        return 0.0;
    }
    double accumulator = 0.0;
    for (double value : values) {
        const double delta = value - mean_value;
        accumulator += delta * delta;
    }
    return accumulator / static_cast<double>(values.size());
}

std::size_t count_sign_interfaces_from_channels(
    const std::vector<double>& forward,
    const std::vector<double>& reverse,
    double threshold) {
    if (forward.empty()) {
        return 0;
    }
    const auto classify = [threshold](double f, double r) -> int {
        const double output = f - r;
        if (output > threshold) {
            return 1;
        }
        if (output < -threshold) {
            return -1;
        }
        return 0;
    };

    std::size_t interfaces = 0;
    int previous = classify(forward.back(), reverse.back());
    for (std::size_t index = 0; index < forward.size(); ++index) {
        const int current = classify(forward[index], reverse[index]);
        if (current != previous) {
            ++interfaces;
        }
        previous = current;
    }
    return interfaces;
}

}  // namespace

VectorEngine::VectorEngine(EngineConfig config)
    : config_(config),
      rng_(config.seed),
      forward_(config.node_count, 0.0),
      next_forward_(config.node_count, 0.0),
      reverse_(config.node_count, 0.0),
      next_reverse_(config.node_count, 0.0),
      admissibility_(config.node_count, config.edge_baseline_admissibility),
      next_admissibility_(config.node_count, config.edge_baseline_admissibility),
      residue_(config.node_count, 0.0),
      next_residue_(config.node_count, 0.0),
      split_eligibility_(config.node_count, 0.0),
      next_split_eligibility_(config.node_count, 0.0),
      tension_(config.node_count, 0.0),
      next_tension_(config.node_count, 0.0),
      barrier_scaffold_(config.node_count, 0.0),
      next_barrier_scaffold_(config.node_count, 0.0) {
    if (config_.node_count == 0) {
        throw std::invalid_argument("node_count must be greater than zero");
    }
}

void VectorEngine::reseed(std::uint64_t seed) {
    config_.seed = seed;
    rng_.seed(seed);
}

void VectorEngine::initialize_near_undifferentiated() {
    for (std::size_t index = 0; index < config_.node_count; ++index) {
        const double n0 = sample_noise();
        const double n1 = sample_noise();
        const double n2 = sample_noise();
        forward_[index] = std::max(
            0.0,
            0.010 + 0.25 * config_.perturbation_amplitude * (0.5 * n0 + 0.5 * n1));
        reverse_[index] = std::max(
            0.0,
            0.010 + 0.25 * config_.perturbation_amplitude * (0.5 * n0 - 0.5 * n1));
        admissibility_[index] = clamp_value(
            config_.edge_baseline_admissibility + config_.edge_baseline_noise * n2,
            0.0,
            1.0);
        residue_[index] = 0.0;
        split_eligibility_[index] = 0.0;
        tension_[index] = 0.0;
        barrier_scaffold_[index] = 0.0;
    }
    current_step_ = 0;
    last_mean_abs_step_delta_ = 0.0;
}

void VectorEngine::step() {
    for (std::size_t edge = 0; edge < config_.node_count; ++edge) {
        const std::size_t right = wrap_index(static_cast<long long>(edge) + 1);
        const std::size_t prev_edge = wrap_index(static_cast<long long>(edge) - 1);
        const std::size_t next_edge = wrap_index(static_cast<long long>(edge) + 1);

        const double f_left = forward_[edge];
        const double f_right = forward_[right];
        const double r_left = reverse_[edge];
        const double r_right = reverse_[right];

        const double a_here = admissibility_[edge];
        const double residue_here = residue_[edge];
        const double eligibility_here = split_eligibility_[edge];
        const double tension_here = tension_[edge];
        const double scaffold_here = barrier_scaffold_[edge];
        const double residue_prev = residue_[prev_edge];
        const double residue_next = residue_[next_edge];
        const double eligibility_prev = split_eligibility_[prev_edge];
        const double eligibility_next = split_eligibility_[next_edge];
        const double scaffold_prev = barrier_scaffold_[prev_edge];
        const double scaffold_next = barrier_scaffold_[next_edge];

        const double forward_pair = std::sqrt(std::max(0.0, f_left * f_right));
        const double reverse_pair = std::sqrt(std::max(0.0, r_left * r_right));
        const double pair_sum = forward_pair + reverse_pair;
        const double dominance =
            pair_sum > 1.0e-9 ? std::abs(forward_pair - reverse_pair) / pair_sum : 0.0;
        const double coexistence =
            0.5 * (std::min(f_left, r_left) + std::min(f_right, r_right));
        const double output_left = f_left - r_left;
        const double output_right = f_right - r_right;
        // Let upper-window interface strain seed eligibility even when local coexistence stays low.
        const double interface_strain =
            clamp_value((std::abs(output_right - output_left) - 0.18) / 0.82, 0.0, 1.0);

        const double activation_gate =
            clamp_value((pair_sum - 0.06) / 0.24, 0.0, 1.0);
        const double drive_split_gate =
            clamp_value((config_.drive - 0.21) / 0.04, 0.0, 1.0);
        const double eligibility_halo = clamp_value(
            (std::max({eligibility_prev, eligibility_here, eligibility_next}) - 0.010) / 0.040,
            0.0,
            1.0);
        const double corridor_support =
            std::max(forward_pair, reverse_pair) * (0.25 + 0.75 * dominance);
        const double split_recognition =
            activation_gate *
            (coexistence * (1.0 - dominance) +
             config_.split_interface_gain * interface_strain * drive_split_gate);
        const double corridor_gate =
            clamp_value((corridor_support - 0.08) / 0.30, 0.0, 1.0);
        const double low_scaffold_gate =
            1.0 - clamp_value(scaffold_here / std::max(1.0e-9, config_.barrier_edge_threshold), 0.0, 1.0);
        const double activation_support =
            clamp_value((pair_sum - 0.10) / 0.25, 0.0, 1.0);
        const double residue_diffusion_delta =
            config_.residue_diffusion_gain * (0.5 * (residue_prev + residue_next) - residue_here);

        const double residue_write =
            config_.enable_residue
                ? config_.residue_write_gain * corridor_support
                : 0.0;
        next_residue_[edge] = clamp_value(
            residue_here +
                config_.dt *
                    (residue_write + residue_diffusion_delta -
                     config_.residue_relax * residue_here),
            0.0,
            1.0);

        const double eligibility_diffusion_delta =
            config_.split_eligibility_diffusion_gain *
            (0.5 * (eligibility_prev + eligibility_next) - eligibility_here);
        const double eligibility_write =
            config_.enable_split_eligibility
                ? config_.split_eligibility_write_gain * split_recognition *
                      (0.25 + 0.75 * corridor_gate) * (0.20 + 0.80 * low_scaffold_gate) +
                      config_.split_eligibility_corridor_gain * corridor_support * split_recognition
                : 0.0;
        next_split_eligibility_[edge] = clamp_value(
            eligibility_here +
                config_.dt * (eligibility_write + eligibility_diffusion_delta -
                              config_.split_eligibility_relax * eligibility_here -
                              config_.split_eligibility_scaffold_suppression_gain *
                                  scaffold_here * eligibility_here),
            0.0,
            1.0);

        const double sustained_stage_support = clamp_value(
            0.55 * activation_support +
                1.50 * next_split_eligibility_[edge] +
                0.50 * split_recognition - 0.05,
            0.0,
            1.0);
        const double tension_scaffold_support =
            clamp_value(0.35 + 0.65 * eligibility_halo, 0.0, 1.0);
        const double tension_target =
            config_.tension_write_gain * next_split_eligibility_[edge] +
            config_.tension_scaffold_gain * scaffold_here * sustained_stage_support *
                tension_scaffold_support;
        const double tension_decay =
            config_.tension_relax +
            config_.tension_collapse_relax_gain * (1.0 - sustained_stage_support);
        next_tension_[edge] = clamp_value(
            tension_here + config_.dt * (tension_target - tension_decay * tension_here),
            0.0,
            4.0);

        const double scaffold_diffusion_delta =
            config_.barrier_scaffold_diffusion_gain *
            (0.5 * (scaffold_prev + scaffold_next) - scaffold_here);
        const double commitment_drive_gate =
            clamp_value((config_.drive - 0.245) / 0.005, 0.0, 1.0);
        const double scaffold_halo = clamp_value(
            (0.5 * (scaffold_prev + scaffold_next) - 0.05) / 0.17,
            0.0,
            1.0);
        const double commitment_zone =
            clamp_value(
                interface_strain * (0.20 + 0.80 * eligibility_halo) +
                    0.35 * eligibility_halo,
                0.0,
                1.0);
        const double commitment_support =
            std::max(sustained_stage_support, scaffold_halo);
        const double scaffold_write =
            config_.enable_barrier_scaffold
                ? sustained_stage_support *
                      (config_.barrier_scaffold_write_gain * next_split_eligibility_[edge] +
                       config_.barrier_scaffold_tension_gain * next_tension_[edge]) +
                      commitment_drive_gate *
                          config_.barrier_scaffold_commitment_gain *
                          commitment_zone *
                          (0.25 + 0.75 * commitment_support)
                : 0.0;
        const double scaffold_decay =
            config_.barrier_scaffold_relax +
            config_.barrier_scaffold_collapse_relax_gain * (1.0 - sustained_stage_support);
        next_barrier_scaffold_[edge] = clamp_value(
            scaffold_here +
                config_.dt *
                    (scaffold_write + scaffold_diffusion_delta -
                     scaffold_decay * scaffold_here),
            0.0,
            3.0);

        const double admissibility_delta =
            config_.admissibility_corridor_gain * corridor_support +
            config_.admissibility_residue_gain * next_residue_[edge] -
            config_.admissibility_tension_gain * next_tension_[edge] -
            config_.admissibility_scaffold_gain * next_barrier_scaffold_[edge] +
            config_.admissibility_baseline_relax *
                (config_.edge_baseline_admissibility - a_here);

        next_admissibility_[edge] =
            clamp_value(a_here + config_.dt * admissibility_delta, 0.0, 1.0);
    }

    double delta_accumulator = 0.0;
    for (std::size_t node = 0; node < config_.node_count; ++node) {
        const std::size_t left_node = wrap_index(static_cast<long long>(node) - 1);
        const std::size_t right_node = wrap_index(static_cast<long long>(node) + 1);
        const std::size_t left_edge = wrap_index(static_cast<long long>(node) - 1);
        const std::size_t right_edge = node;

        const double f_here = forward_[node];
        const double r_here = reverse_[node];
        const double a_left = next_admissibility_[left_edge];
        const double a_right = next_admissibility_[right_edge];
        const double residue_left = next_residue_[left_edge];
        const double residue_right = next_residue_[right_edge];
        const double scaffold_local =
            0.5 * (next_barrier_scaffold_[left_edge] + next_barrier_scaffold_[right_edge]);
        const double tension_local =
            0.5 * (next_tension_[left_edge] + next_tension_[right_edge]);

        const double drive_seed =
            config_.directional_drive_gain * config_.drive *
            (0.40 + 0.60 * 0.5 * (a_left + a_right));

        const double forward_input =
            config_.directional_neighbor_gain * (0.25 + 0.75 * a_left) * forward_[left_node] +
            config_.residue_node_gain * residue_left;
        const double reverse_input =
            config_.directional_neighbor_gain * (0.25 + 0.75 * a_right) * reverse_[right_node] +
            config_.residue_node_gain * residue_right;

        const double forward_sharpen = config_.directional_sharpen_gain * (f_here - r_here);
        const double reverse_sharpen = config_.directional_sharpen_gain * (r_here - f_here);

        const double forward_delta =
            drive_seed + forward_input + forward_sharpen - config_.node_decay * f_here -
            config_.cross_inhibition_gain * r_here -
            config_.node_self_saturation_gain * f_here * f_here -
            config_.scaffold_suppression_gain * scaffold_local * f_here -
            config_.tension_suppression_gain * tension_local * f_here;
        const double reverse_delta =
            drive_seed + reverse_input + reverse_sharpen - config_.node_decay * r_here -
            config_.cross_inhibition_gain * f_here -
            config_.node_self_saturation_gain * r_here * r_here -
            config_.scaffold_suppression_gain * scaffold_local * r_here -
            config_.tension_suppression_gain * tension_local * r_here;

        next_forward_[node] =
            clamp_value(f_here + config_.dt * forward_delta, 0.0, 2.5);
        next_reverse_[node] =
            clamp_value(r_here + config_.dt * reverse_delta, 0.0, 2.5);

        delta_accumulator +=
            std::abs(next_forward_[node] - f_here) + std::abs(next_reverse_[node] - r_here);
    }

    last_mean_abs_step_delta_ =
        delta_accumulator / static_cast<double>(2 * config_.node_count);

    forward_.swap(next_forward_);
    reverse_.swap(next_reverse_);
    admissibility_.swap(next_admissibility_);
    residue_.swap(next_residue_);
    split_eligibility_.swap(next_split_eligibility_);
    tension_.swap(next_tension_);
    barrier_scaffold_.swap(next_barrier_scaffold_);

    ++current_step_;
}

void VectorEngine::run(std::uint64_t steps) {
    for (std::uint64_t step_index = 0; step_index < steps; ++step_index) {
        step();
    }
}

StepMetrics VectorEngine::compute_metrics() const {
    StepMetrics metrics;
    metrics.step_index = current_step_;
    metrics.mean_abs_step_delta = last_mean_abs_step_delta_;

    std::vector<double> outputs(config_.node_count, 0.0);
    double forward_sum = 0.0;
    double reverse_sum = 0.0;
    double total_activation_sum = 0.0;
    double coexistence_sum = 0.0;
    double eligibility_sum = 0.0;
    double dominance_sum = 0.0;
    double admissibility_sum = 0.0;
    double residue_sum = 0.0;
    double tension_sum = 0.0;
    double scaffold_sum = 0.0;
    std::size_t dual_active_nodes = 0;
    std::size_t corridor_edges = 0;
    std::size_t coexistence_edges = 0;
    std::size_t barrier_edges = 0;

    for (std::size_t node = 0; node < config_.node_count; ++node) {
        const double f_here = forward_[node];
        const double r_here = reverse_[node];
        const double output = f_here - r_here;
        outputs[node] = output;
        forward_sum += f_here;
        reverse_sum += r_here;
        total_activation_sum += f_here + r_here;
        coexistence_sum += std::min(f_here, r_here);
        dominance_sum += std::abs(output) / std::max(1.0e-9, f_here + r_here);
        if (std::min(f_here, r_here) >= 0.03) {
            ++dual_active_nodes;
        }
    }

    for (std::size_t edge = 0; edge < config_.node_count; ++edge) {
        const std::size_t right = wrap_index(static_cast<long long>(edge) + 1);
        const double f_pair = std::sqrt(std::max(0.0, forward_[edge] * forward_[right]));
        const double r_pair = std::sqrt(std::max(0.0, reverse_[edge] * reverse_[right]));
        const double pair_sum = f_pair + r_pair;
        const double dominance =
            pair_sum > 1.0e-9 ? std::abs(f_pair - r_pair) / pair_sum : 0.0;
        const double corridor_support = std::max(f_pair, r_pair) * (0.25 + 0.75 * dominance);
        const double coexistence =
            0.5 * (std::min(forward_[edge], reverse_[edge]) +
                   std::min(forward_[right], reverse_[right]));
        const double recognition =
            coexistence * (1.0 - dominance) *
            clamp_value((pair_sum - 0.06) / 0.24, 0.0, 1.0);

        admissibility_sum += admissibility_[edge];
        residue_sum += residue_[edge];
        eligibility_sum += split_eligibility_[edge];
        tension_sum += tension_[edge];
        scaffold_sum += barrier_scaffold_[edge];

        if (corridor_support >= config_.corridor_edge_threshold &&
            barrier_scaffold_[edge] < config_.barrier_edge_threshold * 0.80) {
            ++corridor_edges;
        }
        if (recognition >= config_.coexistence_edge_threshold &&
            barrier_scaffold_[edge] < config_.barrier_edge_threshold) {
            ++coexistence_edges;
        }
        if (barrier_scaffold_[edge] >= config_.barrier_edge_threshold ||
            tension_[edge] >= 0.35) {
            ++barrier_edges;
        }
    }

    const double count = static_cast<double>(config_.node_count);
    const double edge_count = static_cast<double>(config_.node_count);

    metrics.mean_output = std::accumulate(outputs.begin(), outputs.end(), 0.0) / count;
    double mean_abs_output = 0.0;
    for (double output : outputs) {
        mean_abs_output += std::abs(output);
    }
    metrics.mean_abs_output = mean_abs_output / count;
    metrics.output_variance = variance_of(outputs, metrics.mean_output);
    metrics.mean_total_activation = total_activation_sum / count;
    metrics.mean_forward_channel = forward_sum / count;
    metrics.mean_reverse_channel = reverse_sum / count;
    metrics.mean_directional_dominance = dominance_sum / count;
    metrics.mean_channel_coexistence = coexistence_sum / count;
    metrics.mean_split_eligibility = eligibility_sum / edge_count;
    metrics.mean_admissibility = admissibility_sum / edge_count;
    metrics.mean_residue = residue_sum / edge_count;
    metrics.mean_tension = tension_sum / edge_count;
    metrics.mean_barrier_scaffold = scaffold_sum / edge_count;
    metrics.corridor_edge_fraction = static_cast<double>(corridor_edges) / edge_count;
    metrics.coexistence_edge_fraction = static_cast<double>(coexistence_edges) / edge_count;
    metrics.barrier_edge_fraction = static_cast<double>(barrier_edges) / edge_count;
    metrics.dual_active_node_fraction = static_cast<double>(dual_active_nodes) / count;
    metrics.output_interface_count =
        count_sign_interfaces_from_channels(forward_, reverse_, 0.05);

    return metrics;
}

std::size_t VectorEngine::wrap_index(long long index) const {
    const long long count = static_cast<long long>(config_.node_count);
    long long wrapped = index % count;
    if (wrapped < 0) {
        wrapped += count;
    }
    return static_cast<std::size_t>(wrapped);
}

double VectorEngine::sample_noise() {
    return noise_dist_(rng_);
}

}  // namespace analog_r2b
