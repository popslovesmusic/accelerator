#include "engine_r2b_vector.h"

#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

namespace {

struct CliConfig {
    std::filesystem::path output_dir = "smoke_output";
    std::string case_label = "runtime_r2b_smoke";
    std::uint64_t seed = 30101;
    std::size_t node_count = 128;
    std::uint64_t steps = 1024;
    std::uint64_t snapshot_interval = 128;
    double dt = 0.05;
    double drive = 0.20;
    bool enable_split_eligibility = true;
    bool enable_barrier_scaffold = true;
    bool enable_residue = true;
};

std::string escape_csv(const std::string& value) {
    if (value.find_first_of(",\"") == std::string::npos) {
        return value;
    }
    std::string escaped = "\"";
    for (char ch : value) {
        if (ch == '"') {
            escaped += "\"\"";
        } else {
            escaped += ch;
        }
    }
    escaped += "\"";
    return escaped;
}

std::string to_fixed(double value) {
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(6) << value;
    return stream.str();
}

bool parse_bool_value(const std::string& value) {
    if (value == "1" || value == "true" || value == "TRUE" || value == "True") {
        return true;
    }
    if (value == "0" || value == "false" || value == "FALSE" || value == "False") {
        return false;
    }
    throw std::runtime_error("invalid boolean value: " + value);
}

std::string classify_regime(const analog_r2b::StepMetrics& metrics) {
    if (metrics.mean_total_activation < 0.07 &&
        metrics.mean_barrier_scaffold < 0.03 &&
        metrics.corridor_edge_fraction < 0.05) {
        return "quiet_vector";
    }
    if (metrics.barrier_edge_fraction >= 0.55 &&
        metrics.mean_barrier_scaffold >= 0.25) {
        return "scaffold_lock_candidate";
    }
    if (metrics.mean_split_eligibility >= 0.018 &&
        metrics.mean_tension >= 0.04 &&
        metrics.mean_barrier_scaffold >= 0.025 &&
        metrics.barrier_edge_fraction < 0.20) {
        return "split_coexistence_candidate";
    }
    if (metrics.coexistence_edge_fraction >= 0.08 &&
        metrics.barrier_edge_fraction >= 0.05 &&
        metrics.mean_channel_coexistence >= 0.03) {
        return "split_coexistence_candidate";
    }
    if (metrics.corridor_edge_fraction >= 0.20 &&
        metrics.mean_directional_dominance >= 0.30) {
        return "directional_corridor_candidate";
    }
    return "directional_precursor_candidate";
}

CliConfig parse_args(int argc, char** argv) {
    CliConfig config;
    const auto require_value = [&](int index, const std::string& flag) -> std::string {
        if (index + 1 >= argc) {
            throw std::runtime_error("missing value for " + flag);
        }
        return argv[index + 1];
    };

    for (int index = 1; index < argc; ++index) {
        const std::string flag = argv[index];
        if (flag == "--output-dir") {
            config.output_dir = require_value(index, flag);
            ++index;
        } else if (flag == "--case-label") {
            config.case_label = require_value(index, flag);
            ++index;
        } else if (flag == "--seed") {
            config.seed = static_cast<std::uint64_t>(std::stoull(require_value(index, flag)));
            ++index;
        } else if (flag == "--nodes") {
            config.node_count = static_cast<std::size_t>(std::stoull(require_value(index, flag)));
            ++index;
        } else if (flag == "--steps") {
            config.steps = static_cast<std::uint64_t>(std::stoull(require_value(index, flag)));
            ++index;
        } else if (flag == "--snapshot-interval") {
            config.snapshot_interval = static_cast<std::uint64_t>(std::stoull(require_value(index, flag)));
            ++index;
        } else if (flag == "--dt") {
            config.dt = std::stod(require_value(index, flag));
            ++index;
        } else if (flag == "--drive") {
            config.drive = std::stod(require_value(index, flag));
            ++index;
        } else if (flag == "--enable-split-eligibility") {
            config.enable_split_eligibility = parse_bool_value(require_value(index, flag));
            ++index;
        } else if (flag == "--enable-barrier-scaffold") {
            config.enable_barrier_scaffold = parse_bool_value(require_value(index, flag));
            ++index;
        } else if (flag == "--enable-residue") {
            config.enable_residue = parse_bool_value(require_value(index, flag));
            ++index;
        } else {
            throw std::runtime_error("unknown argument: " + flag);
        }
    }

    return config;
}

void write_timeseries_header(std::ofstream& stream) {
    stream << "step_index,mean_output,mean_abs_output,output_variance,"
              "mean_total_activation,mean_forward_channel,mean_reverse_channel,"
              "mean_directional_dominance,mean_channel_coexistence,mean_split_eligibility,"
              "mean_admissibility,mean_residue,mean_tension,mean_barrier_scaffold,"
              "mean_abs_step_delta,corridor_edge_fraction,coexistence_edge_fraction,"
              "barrier_edge_fraction,dual_active_node_fraction,output_interface_count\n";
}

void write_timeseries_row(std::ofstream& stream, const analog_r2b::StepMetrics& metrics) {
    stream << metrics.step_index << ','
           << to_fixed(metrics.mean_output) << ','
           << to_fixed(metrics.mean_abs_output) << ','
           << to_fixed(metrics.output_variance) << ','
           << to_fixed(metrics.mean_total_activation) << ','
           << to_fixed(metrics.mean_forward_channel) << ','
           << to_fixed(metrics.mean_reverse_channel) << ','
           << to_fixed(metrics.mean_directional_dominance) << ','
           << to_fixed(metrics.mean_channel_coexistence) << ','
           << to_fixed(metrics.mean_split_eligibility) << ','
           << to_fixed(metrics.mean_admissibility) << ','
           << to_fixed(metrics.mean_residue) << ','
           << to_fixed(metrics.mean_tension) << ','
           << to_fixed(metrics.mean_barrier_scaffold) << ','
           << to_fixed(metrics.mean_abs_step_delta) << ','
           << to_fixed(metrics.corridor_edge_fraction) << ','
           << to_fixed(metrics.coexistence_edge_fraction) << ','
           << to_fixed(metrics.barrier_edge_fraction) << ','
           << to_fixed(metrics.dual_active_node_fraction) << ','
           << metrics.output_interface_count << '\n';
}

void write_run_metrics_csv(const std::filesystem::path& path,
                           const std::string& case_label,
                           const std::string& regime,
                           const analog_r2b::StepMetrics& metrics) {
    std::ofstream stream(path);
    if (!stream) {
        throw std::runtime_error("unable to write run_metrics.csv");
    }
    stream << "case_label,regime,step_index,mean_output,mean_abs_output,output_variance,"
              "mean_total_activation,mean_forward_channel,mean_reverse_channel,"
              "mean_directional_dominance,mean_channel_coexistence,mean_split_eligibility,mean_admissibility,"
              "mean_residue,mean_tension,mean_barrier_scaffold,mean_abs_step_delta,"
              "corridor_edge_fraction,coexistence_edge_fraction,barrier_edge_fraction,"
              "dual_active_node_fraction,output_interface_count\n";
    stream << escape_csv(case_label) << ','
           << escape_csv(regime) << ','
           << metrics.step_index << ','
           << to_fixed(metrics.mean_output) << ','
           << to_fixed(metrics.mean_abs_output) << ','
           << to_fixed(metrics.output_variance) << ','
           << to_fixed(metrics.mean_total_activation) << ','
           << to_fixed(metrics.mean_forward_channel) << ','
           << to_fixed(metrics.mean_reverse_channel) << ','
           << to_fixed(metrics.mean_directional_dominance) << ','
           << to_fixed(metrics.mean_channel_coexistence) << ','
           << to_fixed(metrics.mean_split_eligibility) << ','
           << to_fixed(metrics.mean_admissibility) << ','
           << to_fixed(metrics.mean_residue) << ','
           << to_fixed(metrics.mean_tension) << ','
           << to_fixed(metrics.mean_barrier_scaffold) << ','
           << to_fixed(metrics.mean_abs_step_delta) << ','
           << to_fixed(metrics.corridor_edge_fraction) << ','
           << to_fixed(metrics.coexistence_edge_fraction) << ','
           << to_fixed(metrics.barrier_edge_fraction) << ','
           << to_fixed(metrics.dual_active_node_fraction) << ','
           << metrics.output_interface_count << '\n';
}

void write_metadata_json(const std::filesystem::path& path,
                         const CliConfig& cli,
                         const analog_r2b::EngineConfig& engine,
                         const std::string& regime) {
    std::ofstream stream(path);
    if (!stream) {
        throw std::runtime_error("unable to write run_metadata.json");
    }
    stream << "{\n"
           << "  \"case_label\": \"" << cli.case_label << "\",\n"
           << "  \"seed\": " << cli.seed << ",\n"
           << "  \"node_count\": " << cli.node_count << ",\n"
           << "  \"steps\": " << cli.steps << ",\n"
           << "  \"snapshot_interval\": " << cli.snapshot_interval << ",\n"
           << "  \"regime\": \"" << regime << "\",\n"
           << "  \"drive\": " << to_fixed(engine.drive) << ",\n"
           << "  \"enable_split_eligibility\": " << (engine.enable_split_eligibility ? "true" : "false") << ",\n"
           << "  \"enable_barrier_scaffold\": " << (engine.enable_barrier_scaffold ? "true" : "false") << ",\n"
           << "  \"enable_residue\": " << (engine.enable_residue ? "true" : "false") << "\n"
           << "}\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const CliConfig cli = parse_args(argc, argv);

        analog_r2b::EngineConfig config;
        config.node_count = cli.node_count;
        config.dt = cli.dt;
        config.drive = cli.drive;
        config.enable_split_eligibility = cli.enable_split_eligibility;
        config.enable_barrier_scaffold = cli.enable_barrier_scaffold;
        config.enable_residue = cli.enable_residue;
        config.seed = cli.seed;

        analog_r2b::VectorEngine engine(config);
        engine.reseed(cli.seed);
        engine.initialize_near_undifferentiated();

        std::filesystem::create_directories(cli.output_dir);
        const std::filesystem::path timeseries_path = cli.output_dir / "run_timeseries.csv";
        std::ofstream timeseries(timeseries_path);
        if (!timeseries) {
            throw std::runtime_error("unable to open run_timeseries.csv");
        }
        write_timeseries_header(timeseries);

        write_timeseries_row(timeseries, engine.compute_metrics());
        for (std::uint64_t start = 0; start < cli.steps; start += cli.snapshot_interval) {
            const std::uint64_t chunk = std::min(cli.snapshot_interval, cli.steps - start);
            engine.run(chunk);
            write_timeseries_row(timeseries, engine.compute_metrics());
        }

        const analog_r2b::StepMetrics final_metrics = engine.compute_metrics();
        const std::string regime = classify_regime(final_metrics);

        write_run_metrics_csv(cli.output_dir / "run_metrics.csv", cli.case_label, regime, final_metrics);
        write_metadata_json(cli.output_dir / "run_metadata.json", cli, config, regime);

        std::cout << "case_label=" << cli.case_label << '\n'
                  << "regime=" << regime << '\n'
                  << "mean_total_activation=" << to_fixed(final_metrics.mean_total_activation) << '\n'
                  << "mean_directional_dominance=" << to_fixed(final_metrics.mean_directional_dominance) << '\n'
                  << "mean_channel_coexistence=" << to_fixed(final_metrics.mean_channel_coexistence) << '\n'
                  << "mean_split_eligibility=" << to_fixed(final_metrics.mean_split_eligibility) << '\n'
                  << "mean_admissibility=" << to_fixed(final_metrics.mean_admissibility) << '\n'
                  << "mean_residue=" << to_fixed(final_metrics.mean_residue) << '\n'
                  << "mean_tension=" << to_fixed(final_metrics.mean_tension) << '\n'
                  << "mean_barrier_scaffold=" << to_fixed(final_metrics.mean_barrier_scaffold) << '\n'
                  << "corridor_edge_fraction=" << to_fixed(final_metrics.corridor_edge_fraction) << '\n'
                  << "coexistence_edge_fraction=" << to_fixed(final_metrics.coexistence_edge_fraction) << '\n'
                  << "barrier_edge_fraction=" << to_fixed(final_metrics.barrier_edge_fraction) << '\n';

        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "runtime_r2b probe failed: " << ex.what() << '\n';
        return 1;
    }
}
