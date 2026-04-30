#include <algorithm>
#include <cmath>
#include <complex>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include "../stochastic_sim_cpp/json.hpp"

using json = nlohmann::json;

namespace {
constexpr double pi = 3.1415926535897932384626433832795;

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> cols;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, ',')) cols.push_back(item);
    return cols;
}

std::vector<double> read_csv_column(const std::string& path, const std::string& col) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("could not open CSV input");
    std::string header;
    std::getline(in, header);
    auto names = split_csv_line(header);
    auto it = std::find(names.begin(), names.end(), col);
    if (it == names.end()) throw std::runtime_error("column not found: " + col);
    size_t idx = static_cast<size_t>(std::distance(names.begin(), it));
    std::vector<double> values;
    std::string line;
    while (std::getline(in, line)) {
        auto cols = split_csv_line(line);
        if (idx < cols.size()) values.push_back(std::stod(cols[idx]));
    }
    return values;
}

std::vector<std::vector<double>> read_grid_csv(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("could not open grid CSV input");
    std::vector<std::vector<double>> grid;
    std::string line;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::string cell;
        std::vector<double> row;
        while (std::getline(ss, cell, ',')) row.push_back(std::stod(cell));
        if (!row.empty()) grid.push_back(row);
    }
    return grid;
}

std::vector<double> make_control_signal(size_t n, size_t cycles) {
    std::vector<double> x(n);
    for (size_t i = 0; i < n; ++i) {
        x[i] = std::sin(2.0 * pi * static_cast<double>(cycles) * static_cast<double>(i) / static_cast<double>(n));
    }
    return x;
}

std::vector<std::vector<double>> make_spatial_control(size_t n, size_t cycles) {
    std::vector<std::vector<double>> grid(n, std::vector<double>(n, 0.0));
    for (size_t y = 0; y < n; ++y) {
        for (size_t x = 0; x < n; ++x) {
            grid[y][x] = std::sin(2.0 * pi * static_cast<double>(cycles) * static_cast<double>(x) / static_cast<double>(n));
        }
    }
    return grid;
}

json temporal_spectrum(std::vector<double> signal, double fs, size_t top_n) {
    double mean = 0.0;
    for (double v : signal) mean += v;
    mean /= static_cast<double>(signal.size());
    for (double& v : signal) v -= mean;

    const size_t n = signal.size();
    const size_t bins = n / 2 + 1;
    std::vector<std::pair<size_t, double>> power;
    power.reserve(bins);
    double total_power = 0.0;
    for (size_t k = 0; k < bins; ++k) {
        std::complex<double> sum(0.0, 0.0);
        for (size_t t = 0; t < n; ++t) {
            double angle = -2.0 * pi * static_cast<double>(k * t) / static_cast<double>(n);
            sum += signal[t] * std::complex<double>(std::cos(angle), std::sin(angle));
        }
        double p = std::norm(sum) / static_cast<double>(n);
        if (k != 0) {
            power.push_back({k, p});
            total_power += p;
        }
    }
    std::sort(power.begin(), power.end(), [](const auto& a, const auto& b) { return a.second > b.second; });

    json modes = json::array();
    for (size_t i = 0; i < std::min(top_n, power.size()); ++i) {
        double frequency = fs * static_cast<double>(power[i].first) / static_cast<double>(n);
        modes.push_back({{"bin", power[i].first}, {"frequency", frequency}, {"power", power[i].second}});
    }
    double dominant = power.empty() ? 0.0 : power.front().second;
    return {
        {"sample_count", n},
        {"total_power", total_power},
        {"dominant_power_fraction", total_power > 0.0 ? dominant / total_power : 0.0},
        {"dominant_modes", modes}
    };
}

json spatial_spectrum(const std::vector<std::vector<double>>& grid, size_t top_n) {
    const size_t h = grid.size();
    const size_t w = h > 0 ? grid[0].size() : 0;
    std::vector<std::pair<size_t, double>> radial;
    const size_t max_r = static_cast<size_t>(std::sqrt(static_cast<double>(w * w + h * h))) + 1;
    std::vector<double> radial_sum(max_r, 0.0);
    std::vector<size_t> radial_count(max_r, 0);
    double total_power = 0.0;
    for (size_t ky = 0; ky < h; ++ky) {
        for (size_t kx = 0; kx < w; ++kx) {
            std::complex<double> sum(0.0, 0.0);
            for (size_t y = 0; y < h; ++y) {
                for (size_t x = 0; x < w; ++x) {
                    double phase = -2.0 * pi * ((static_cast<double>(kx * x) / static_cast<double>(w)) +
                                                 (static_cast<double>(ky * y) / static_cast<double>(h)));
                    sum += grid[y][x] * std::complex<double>(std::cos(phase), std::sin(phase));
                }
            }
            double p = std::norm(sum) / static_cast<double>(w * h);
            int sx = static_cast<int>(kx <= w / 2 ? kx : kx - w);
            int sy = static_cast<int>(ky <= h / 2 ? ky : ky - h);
            size_t r = static_cast<size_t>(std::round(std::sqrt(static_cast<double>(sx * sx + sy * sy))));
            if (r > 0 && r < max_r) {
                radial_sum[r] += p;
                radial_count[r]++;
                total_power += p;
            }
        }
    }
    for (size_t r = 1; r < max_r; ++r) {
        if (radial_count[r] > 0) radial.push_back({r, radial_sum[r] / static_cast<double>(radial_count[r])});
    }
    std::sort(radial.begin(), radial.end(), [](const auto& a, const auto& b) { return a.second > b.second; });
    json modes = json::array();
    for (size_t i = 0; i < std::min(top_n, radial.size()); ++i) {
        modes.push_back({{"wavenumber", radial[i].first}, {"power", radial[i].second}});
    }
    return {
        {"height", h},
        {"width", w},
        {"total_power", total_power},
        {"dominant_power_fraction", total_power > 0.0 && !radial.empty() ? radial.front().second / total_power : 0.0},
        {"dominant_wavenumbers", modes}
    };
}
}

int main(int argc, char** argv) {
    std::string mode = "temporal";
    std::string file;
    std::string col = "order_parameter";
    std::string out_dir = "outputs/spectral_analysis_v1_cpp/control";
    double fs = 1.0;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--mode" && i + 1 < argc) mode = argv[++i];
        else if (a == "--file" && i + 1 < argc) file = argv[++i];
        else if (a == "--col" && i + 1 < argc) col = argv[++i];
        else if (a == "--out" && i + 1 < argc) out_dir = argv[++i];
        else if (a == "--fs" && i + 1 < argc) fs = std::stod(argv[++i]);
    }

    std::filesystem::create_directories(out_dir);
    bool control_passed = false;
    json report;
    report["sim_id"] = "spectral_analysis_v2p3";
    report["schema"] = "v2.3_recoverable_report";
    report["mode"] = mode;
    report["source"] = file.empty() ? "built_in_control" : file;
    if (mode == "spatial") {
        auto grid = file.empty() ? make_spatial_control(32, 4) : read_grid_csv(file);
        auto spectrum = spatial_spectrum(grid, 5);
        report["spectrum"] = spectrum;
        if (file.empty()) {
            size_t top_k = spectrum["dominant_wavenumbers"][0]["wavenumber"].get<size_t>();
            control_passed = top_k == 4;
        } else {
            control_passed = true;
        }
        report["falsification"] = {
            {"tests_run", json::array({"known_spatial_wavenumber"})},
            {"passed", control_passed},
            {"notes", file.empty() ? "dominant radial wavenumber must equal injected control wavenumber 4" : "custom input run; built-in control not applicable"}
        };
    } else {
        std::vector<double> signal = file.empty() ? make_control_signal(256, 7) : read_csv_column(file, col);
        if (signal.size() < 8) throw std::runtime_error("temporal analysis requires at least 8 samples");
        auto spectrum = temporal_spectrum(signal, fs, 5);
        if (file.empty()) {
            size_t top_bin = spectrum["dominant_modes"][0]["bin"].get<size_t>();
            control_passed = top_bin == 7;
        } else {
            control_passed = true;
        }
        report["column"] = col;
        report["spectrum"] = spectrum;
        report["falsification"] = {
            {"tests_run", json::array({"known_sinusoid_frequency"})},
            {"passed", control_passed},
            {"notes", file.empty() ? "dominant DFT bin must equal injected control bin 7" : "custom input run; built-in control not applicable"}
        };
    }

    std::ofstream out(std::filesystem::path(out_dir) / "spectrum_report.json");
    out << std::setw(2) << report << "\n";
    std::cout << "Report saved to " << (std::filesystem::path(out_dir) / "spectrum_report.json").string() << "\n";
    return report["falsification"]["passed"].get<bool>() ? 0 : 2;
}
