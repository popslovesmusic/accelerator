#include <algorithm>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

namespace fs = std::filesystem;

struct AggregateKey {
    double kappa = 0.0;
    double lam = 0.0;

    bool operator<(const AggregateKey& other) const {
        if (kappa != other.kappa) {
            return kappa < other.kappa;
        }
        return lam < other.lam;
    }
};

enum class RegimeClass {
    Runaway,
    SS3,
    SS2,
    Other,
};

struct RunState {
    AggregateKey key;
    bool has_summary = false;
    bool has_timeseries = false;
    bool has_domain = false;

    double final_exclusion_fraction = 0.0;
    double final_mean_rho = 0.0;
    double final_interface_count = 0.0;

    double final_time = 0.0;
    std::optional<double> interface_loss_time;
    double max_observed_sharpness = 0.0;

    double last_domain_time = -std::numeric_limits<double>::infinity();
    double final_active_fraction = 0.0;
    double final_excluded_active_fraction = 0.0;
};

struct RegimeCounts {
    int runaway = 0;
    int ss3 = 0;
    int ss2 = 0;
    int other = 0;

    void add(RegimeClass cls) {
        switch (cls) {
            case RegimeClass::Runaway:
                ++runaway;
                break;
            case RegimeClass::SS3:
                ++ss3;
                break;
            case RegimeClass::SS2:
                ++ss2;
                break;
            case RegimeClass::Other:
                ++other;
                break;
        }
    }

    int total() const {
        return runaway + ss3 + ss2 + other;
    }
};

struct AggregateStats {
    RegimeCounts counts;
    double sum_final_exclusion_fraction = 0.0;
    double sum_final_mean_rho = 0.0;
    double sum_final_interface_count = 0.0;
    double sum_interface_loss_time = 0.0;
    int interface_loss_count = 0;
    double sum_final_active_fraction = 0.0;
    double active_fraction_count = 0.0;
    double sum_final_excluded_active_fraction = 0.0;
    double excluded_active_count = 0.0;
    double max_observed_sharpness = 0.0;
};

std::string trim(std::string value) {
    auto not_space = [](unsigned char ch) { return !std::isspace(ch); };
    value.erase(value.begin(), std::find_if(value.begin(), value.end(), not_space));
    value.erase(std::find_if(value.rbegin(), value.rend(), not_space).base(), value.end());
    return value;
}

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::string current;
    bool in_quotes = false;

    for (size_t i = 0; i < line.size(); ++i) {
        const char ch = line[i];
        if (ch == '"') {
            if (in_quotes && i + 1 < line.size() && line[i + 1] == '"') {
                current.push_back('"');
                ++i;
            } else {
                in_quotes = !in_quotes;
            }
        } else if (ch == ',' && !in_quotes) {
            fields.push_back(current);
            current.clear();
        } else {
            current.push_back(ch);
        }
    }

    fields.push_back(current);
    return fields;
}

double parse_double(const std::string& text) {
    return std::stod(trim(text));
}

std::optional<size_t> find_column(const std::vector<std::string>& header, const std::string& name) {
    for (size_t i = 0; i < header.size(); ++i) {
        if (header[i] == name) {
            return i;
        }
    }
    return std::nullopt;
}

RegimeClass classify(const RunState& row) {
    if (row.final_interface_count < 0.5 &&
        row.final_exclusion_fraction >= 0.95 &&
        row.final_mean_rho <= 0.05) {
        return RegimeClass::Runaway;
    }

    if (row.final_interface_count >= 0.5 &&
        row.final_exclusion_fraction > 0.05 &&
        row.final_exclusion_fraction < 0.95 &&
        row.final_mean_rho > 0.25) {
        return RegimeClass::SS3;
    }

    if (row.final_interface_count < 0.5 &&
        row.final_exclusion_fraction <= 0.05 &&
        row.final_mean_rho >= 1.5) {
        return RegimeClass::SS2;
    }

    return RegimeClass::Other;
}

std::string regime_name(RegimeClass cls) {
    switch (cls) {
        case RegimeClass::Runaway:
            return "runaway";
        case RegimeClass::SS3:
            return "SS3";
        case RegimeClass::SS2:
            return "SS2";
        case RegimeClass::Other:
            return "other";
    }
    return "other";
}

std::string dominant_name(const RegimeCounts& counts) {
    const std::vector<std::pair<std::string, int>> ordered = {
        {"runaway", counts.runaway},
        {"SS3", counts.ss3},
        {"SS2", counts.ss2},
        {"other", counts.other},
    };

    return std::max_element(
               ordered.begin(),
               ordered.end(),
               [](const auto& lhs, const auto& rhs) { return lhs.second < rhs.second; })
        ->first;
}

bool unanimous(const RegimeCounts& counts) {
    const int total = counts.total();
    return total > 0 &&
           (counts.runaway == total || counts.ss3 == total || counts.ss2 == total || counts.other == total);
}

std::string format_double(double value) {
    std::ostringstream stream;
    stream << std::setprecision(12) << value;
    return stream.str();
}

void scan_final_summary(
    const fs::path& root,
    std::unordered_map<std::string, RunState>& runs,
    int& file_count)
{
    for (const auto& entry : fs::recursive_directory_iterator(root)) {
        if (!entry.is_regular_file() || entry.path().filename() != "final_summary.csv") {
            continue;
        }

        std::ifstream input(entry.path());
        if (!input) {
            continue;
        }

        std::string line;
        if (!std::getline(input, line)) {
            continue;
        }

        const auto header = split_csv_line(line);
        const auto run_id_col = find_column(header, "run_id");
        const auto kappa_col = find_column(header, "kappa");
        const auto lam_col = find_column(header, "lam");
        const auto exclusion_col = find_column(header, "final_exclusion_fraction");
        const auto rho_col = find_column(header, "final_mean_rho");
        const auto interface_col = find_column(header, "final_interface_count");
        if (!run_id_col || !kappa_col || !lam_col || !exclusion_col || !rho_col || !interface_col) {
            continue;
        }

        ++file_count;

        while (std::getline(input, line)) {
            if (line.empty()) {
                continue;
            }

            const auto fields = split_csv_line(line);
            if (fields.size() != header.size()) {
                continue;
            }

            try {
                const std::string run_id = fields[*run_id_col];
                RunState& state = runs[run_id];
                state.key.kappa = parse_double(fields[*kappa_col]);
                state.key.lam = parse_double(fields[*lam_col]);
                state.final_exclusion_fraction = parse_double(fields[*exclusion_col]);
                state.final_mean_rho = parse_double(fields[*rho_col]);
                state.final_interface_count = parse_double(fields[*interface_col]);
                state.has_summary = true;
            } catch (...) {
                continue;
            }
        }
    }
}

void scan_timeseries_global(
    const fs::path& root,
    std::unordered_map<std::string, RunState>& runs,
    int& file_count)
{
    for (const auto& entry : fs::recursive_directory_iterator(root)) {
        if (!entry.is_regular_file() || entry.path().filename() != "timeseries_global.csv") {
            continue;
        }

        std::ifstream input(entry.path());
        if (!input) {
            continue;
        }

        std::string line;
        if (!std::getline(input, line)) {
            continue;
        }

        const auto header = split_csv_line(line);
        const auto run_id_col = find_column(header, "run_id");
        const auto time_col = find_column(header, "time");
        const auto interface_col = find_column(header, "interface_count");
        const auto sharpness_col = find_column(header, "max_sharpness");
        if (!run_id_col || !time_col || !interface_col || !sharpness_col) {
            continue;
        }

        ++file_count;

        while (std::getline(input, line)) {
            if (line.empty()) {
                continue;
            }

            const auto fields = split_csv_line(line);
            if (fields.size() != header.size()) {
                continue;
            }

            try {
                const std::string run_id = fields[*run_id_col];
                auto it = runs.find(run_id);
                if (it == runs.end()) {
                    continue;
                }

                RunState& state = it->second;
                const double time = parse_double(fields[*time_col]);
                const double interface_count = parse_double(fields[*interface_col]);
                const double sharpness = parse_double(fields[*sharpness_col]);

                state.final_time = std::max(state.final_time, time);
                state.max_observed_sharpness = std::max(state.max_observed_sharpness, sharpness);
                if (!state.interface_loss_time.has_value() && interface_count < 0.5) {
                    state.interface_loss_time = time;
                }
                state.has_timeseries = true;
            } catch (...) {
                continue;
            }
        }
    }
}

void scan_domain_metrics(
    const fs::path& root,
    std::unordered_map<std::string, RunState>& runs,
    int& file_count)
{
    for (const auto& entry : fs::recursive_directory_iterator(root)) {
        if (!entry.is_regular_file() || entry.path().filename() != "domain_metrics.csv") {
            continue;
        }

        std::ifstream input(entry.path());
        if (!input) {
            continue;
        }

        std::string line;
        if (!std::getline(input, line)) {
            continue;
        }

        const auto header = split_csv_line(line);
        const auto run_id_col = find_column(header, "run_id");
        const auto time_col = find_column(header, "time");
        const auto active_col = find_column(header, "active_fraction");
        const auto excluded_col = find_column(header, "excluded_active_fraction");
        if (!run_id_col || !time_col || !active_col || !excluded_col) {
            continue;
        }

        ++file_count;

        while (std::getline(input, line)) {
            if (line.empty()) {
                continue;
            }

            const auto fields = split_csv_line(line);
            if (fields.size() != header.size()) {
                continue;
            }

            try {
                const std::string run_id = fields[*run_id_col];
                auto it = runs.find(run_id);
                if (it == runs.end()) {
                    continue;
                }

                RunState& state = it->second;
                const double time = parse_double(fields[*time_col]);
                if (time >= state.last_domain_time) {
                    state.last_domain_time = time;
                    state.final_active_fraction = parse_double(fields[*active_col]);
                    state.final_excluded_active_fraction = parse_double(fields[*excluded_col]);
                    state.has_domain = true;
                }
            } catch (...) {
                continue;
            }
        }
    }
}

void build_aggregates(
    const std::unordered_map<std::string, RunState>& runs,
    std::map<AggregateKey, AggregateStats>& aggregates)
{
    for (const auto& [run_id, state] : runs) {
        (void)run_id;
        if (!state.has_summary) {
            continue;
        }

        AggregateStats& stats = aggregates[state.key];
        stats.counts.add(classify(state));
        stats.sum_final_exclusion_fraction += state.final_exclusion_fraction;
        stats.sum_final_mean_rho += state.final_mean_rho;
        stats.sum_final_interface_count += state.final_interface_count;
        stats.max_observed_sharpness = std::max(stats.max_observed_sharpness, state.max_observed_sharpness);

        if (state.interface_loss_time.has_value()) {
            stats.sum_interface_loss_time += *state.interface_loss_time;
            ++stats.interface_loss_count;
        }

        if (state.has_domain) {
            stats.sum_final_active_fraction += state.final_active_fraction;
            stats.sum_final_excluded_active_fraction += state.final_excluded_active_fraction;
            stats.active_fraction_count += 1.0;
            stats.excluded_active_count += 1.0;
        }
    }
}

void write_run_summary_csv(
    const fs::path& output_path,
    const std::unordered_map<std::string, RunState>& runs)
{
    std::ofstream output(output_path);
    output << "run_id,kappa,lam,regime_class,final_exclusion_fraction,final_mean_rho,final_interface_count,final_time,interface_loss_time,final_active_fraction,final_excluded_active_fraction,max_observed_sharpness\n";

    std::vector<std::pair<std::string, RunState>> ordered(runs.begin(), runs.end());
    std::sort(
        ordered.begin(),
        ordered.end(),
        [](const auto& lhs, const auto& rhs) {
            if (lhs.second.key.kappa != rhs.second.key.kappa) {
                return lhs.second.key.kappa < rhs.second.key.kappa;
            }
            if (lhs.second.key.lam != rhs.second.key.lam) {
                return lhs.second.key.lam < rhs.second.key.lam;
            }
            return lhs.first < rhs.first;
        });

    for (const auto& [run_id, state] : ordered) {
        if (!state.has_summary) {
            continue;
        }

        output << run_id << ','
               << format_double(state.key.kappa) << ','
               << format_double(state.key.lam) << ','
               << regime_name(classify(state)) << ','
               << format_double(state.final_exclusion_fraction) << ','
               << format_double(state.final_mean_rho) << ','
               << format_double(state.final_interface_count) << ','
               << format_double(state.final_time) << ',';

        if (state.interface_loss_time.has_value()) {
            output << format_double(*state.interface_loss_time);
        }
        output << ',';

        if (state.has_domain) {
            output << format_double(state.final_active_fraction) << ','
                   << format_double(state.final_excluded_active_fraction);
        } else {
            output << ',';
        }

        output << ',' << format_double(state.max_observed_sharpness) << '\n';
    }
}

void write_parameter_summary_csv(
    const fs::path& output_path,
    const std::map<AggregateKey, AggregateStats>& aggregates)
{
    std::ofstream output(output_path);
    output << "kappa,lam,total_runs,runaway_count,ss3_count,ss2_count,other_count,dominant_regime,unanimous,mean_final_exclusion_fraction,mean_final_mean_rho,mean_final_interface_count,mean_interface_loss_time,mean_final_active_fraction,mean_final_excluded_active_fraction,max_observed_sharpness\n";

    for (const auto& [key, stats] : aggregates) {
        const double total = static_cast<double>(stats.counts.total());
        output << format_double(key.kappa) << ','
               << format_double(key.lam) << ','
               << stats.counts.total() << ','
               << stats.counts.runaway << ','
               << stats.counts.ss3 << ','
               << stats.counts.ss2 << ','
               << stats.counts.other << ','
               << dominant_name(stats.counts) << ','
               << (unanimous(stats.counts) ? "true" : "false") << ','
               << format_double(stats.sum_final_exclusion_fraction / total) << ','
               << format_double(stats.sum_final_mean_rho / total) << ','
               << format_double(stats.sum_final_interface_count / total) << ',';

        if (stats.interface_loss_count > 0) {
            output << format_double(stats.sum_interface_loss_time / static_cast<double>(stats.interface_loss_count));
        }
        output << ',';

        if (stats.active_fraction_count > 0.0) {
            output << format_double(stats.sum_final_active_fraction / stats.active_fraction_count);
        }
        output << ',';

        if (stats.excluded_active_count > 0.0) {
            output << format_double(stats.sum_final_excluded_active_fraction / stats.excluded_active_count);
        }
        output << ','
               << format_double(stats.max_observed_sharpness)
               << '\n';
    }
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: level2_results_analyzer <input_root> <output_prefix>\n";
        return 1;
    }

    const fs::path input_root = argv[1];
    const fs::path output_prefix = argv[2];
    if (!fs::exists(input_root)) {
        std::cerr << "Input root does not exist: " << input_root << '\n';
        return 1;
    }

    std::unordered_map<std::string, RunState> runs;
    int final_summary_files = 0;
    int timeseries_files = 0;
    int domain_files = 0;

    scan_final_summary(input_root, runs, final_summary_files);
    scan_timeseries_global(input_root, runs, timeseries_files);
    scan_domain_metrics(input_root, runs, domain_files);

    std::map<AggregateKey, AggregateStats> aggregates;
    build_aggregates(runs, aggregates);

    const fs::path run_output = output_prefix.parent_path() / (output_prefix.stem().string() + "_run_summary.csv");
    const fs::path parameter_output = output_prefix.parent_path() / (output_prefix.stem().string() + "_parameter_summary.csv");
    write_run_summary_csv(run_output, runs);
    write_parameter_summary_csv(parameter_output, aggregates);

    std::cout << "Scanned final_summary.csv files: " << final_summary_files << '\n';
    std::cout << "Scanned timeseries_global.csv files: " << timeseries_files << '\n';
    std::cout << "Scanned domain_metrics.csv files: " << domain_files << '\n';
    std::cout << "Run summaries written: " << run_output << '\n';
    std::cout << "Parameter summaries written: " << parameter_output << '\n';
    return 0;
}
