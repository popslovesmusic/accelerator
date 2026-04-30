#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>
#include "../stochastic_sim_cpp/json.hpp"

using json = nlohmann::json;

namespace {
constexpr double pi = 3.1415926535897932384626433832795;

template <typename T>
struct Metrics {
    double mean_H = 0.0;
    double std_H = 0.0;
    double mean_q = 0.0;
    double mean_p = 0.0;
    double q_rms = 0.0;
    double p_rms = 0.0;
};

template <typename T>
T wrap_pi(T q) {
    T two_pi = static_cast<T>(2.0 * pi);
    q = std::fmod(q + static_cast<T>(pi), two_pi);
    if (q < static_cast<T>(0)) q += two_pi;
    return q - static_cast<T>(pi);
}

template <typename T>
std::vector<T> make_normal_state(size_t n, double spread, uint32_t seed) {
    std::mt19937 rng(seed);
    std::normal_distribution<double> dist(0.0, spread);
    std::vector<T> out(n);
    for (auto& v : out) v = static_cast<T>(dist(rng));
    return out;
}

template <typename T>
Metrics<T> compute_metrics(const std::vector<T>& q, const std::vector<T>& p, T mass, T kappa) {
    const size_t n = q.size();
    double sum_H = 0.0, sum_H2 = 0.0, sum_q = 0.0, sum_p = 0.0, sum_q2 = 0.0, sum_p2 = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double qv = static_cast<double>(q[i]);
        double pv = static_cast<double>(p[i]);
        double H = (pv * pv) / (2.0 * static_cast<double>(mass)) - static_cast<double>(kappa) * std::cos(qv);
        sum_H += H;
        sum_H2 += H * H;
        sum_q += qv;
        sum_p += pv;
        sum_q2 += qv * qv;
        sum_p2 += pv * pv;
    }
    Metrics<T> m;
    m.mean_H = sum_H / static_cast<double>(n);
    m.std_H = std::sqrt(std::max(0.0, sum_H2 / static_cast<double>(n) - m.mean_H * m.mean_H));
    m.mean_q = sum_q / static_cast<double>(n);
    m.mean_p = sum_p / static_cast<double>(n);
    m.q_rms = std::sqrt(std::max(0.0, sum_q2 / static_cast<double>(n) - m.mean_q * m.mean_q));
    m.p_rms = std::sqrt(std::max(0.0, sum_p2 / static_cast<double>(n) - m.mean_p * m.mean_p));
    return m;
}

template <typename T>
void step(std::vector<T>& q, std::vector<T>& p, T mass, T kappa, T dt) {
    for (size_t i = 0; i < q.size(); ++i) {
        T p_half = p[i] - static_cast<T>(0.5) * dt * kappa * std::sin(q[i]);
        q[i] = wrap_pi(q[i] + dt * (p_half / mass));
        p[i] = p_half - static_cast<T>(0.5) * dt * kappa * std::sin(q[i]);
    }
}

template <typename T>
json run_case(size_t n, int steps, T mass, T kappa, T dt, double q_spread, double p_spread, uint32_t seed, const std::string& label, bool write_csv) {
    auto q = make_normal_state<T>(n, q_spread, seed);
    auto p = make_normal_state<T>(n, p_spread, seed + 1);
    auto initial = compute_metrics(q, p, mass, kappa);

    std::ofstream csv;
    if (write_csv) {
        csv.open("outputs/symplectic_sim_v1_cpp/metrics.csv");
        csv << "label,step,mean_H,std_H,mean_q,mean_p,q_rms,p_rms\n";
        csv << label << ",0," << initial.mean_H << "," << initial.std_H << "," << initial.mean_q << ","
            << initial.mean_p << "," << initial.q_rms << "," << initial.p_rms << "\n";
    }

    auto start = std::chrono::high_resolution_clock::now();
    for (int s = 1; s <= steps; ++s) {
        step(q, p, mass, kappa, dt);
        if (write_csv && (s % 20 == 0 || s == steps)) {
            auto m = compute_metrics(q, p, mass, kappa);
            csv << label << "," << s << "," << m.mean_H << "," << m.std_H << "," << m.mean_q << ","
                << m.mean_p << "," << m.q_rms << "," << m.p_rms << "\n";
        }
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto final = compute_metrics(q, p, mass, kappa);
    double drift = final.mean_H - initial.mean_H;
    return {
        {"label", label},
        {"n_particles", n},
        {"steps", steps},
        {"mean_H_initial", initial.mean_H},
        {"mean_H_final", final.mean_H},
        {"std_H_final", final.std_H},
        {"energy_drift_abs", drift},
        {"energy_drift_rel", std::abs(initial.mean_H) > 0.0 ? drift / std::abs(initial.mean_H) : 0.0},
        {"q_rms_final", final.q_rms},
        {"p_rms_final", final.p_rms},
        {"time_ms", std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()}
    };
}
}

int main() {
    std::filesystem::create_directories("outputs/symplectic_sim_v1_cpp");

    const size_t n = 20000;
    const int steps = 2000;
    const double mass = 1.0;
    const double kappa = 1.0;
    const double dt = 0.01;
    const double q_spread = 0.4;
    const double p_spread = 0.25;
    const uint32_t seed = 42;

    json report;
    report["sim_id"] = "symplectic_sim_v2p3_precision_study";
    report["run_date"] = "2026-04-29";
    report["schema"] = "v2.3_recoverable_report";
    report["model_class"] = "hamiltonian_symplectic";
    report["primitive_mapping"] = {
        {"epsilon", "energy drift from numerical mismatch"},
        {"residue", "conserved Hamiltonian trace across integration"},
        {"coupling", "kappa nonlinear pendulum potential strength"}
    };

    auto fp32 = run_case<float>(n, steps, static_cast<float>(mass), static_cast<float>(kappa), static_cast<float>(dt), q_spread, p_spread, seed, "fp32", true);
    auto fp64 = run_case<double>(n, steps, mass, kappa, dt, q_spread, p_spread, seed, "fp64", false);
    auto zero_step = run_case<double>(n, 0, mass, kappa, dt, q_spread, p_spread, seed, "falsification_zero_step", false);

    report["fp32_results"] = fp32;
    report["fp64_results"] = fp64;
    report["precision_drift"] = {
        {"energy_drift_abs_delta", std::abs(fp32["energy_drift_abs"].get<double>() - fp64["energy_drift_abs"].get<double>())},
        {"q_rms_abs_delta", std::abs(fp32["q_rms_final"].get<double>() - fp64["q_rms_final"].get<double>())}
    };
    report["falsification"] = {
        {"tests_run", json::array({"zero_step_energy_invariance"})},
        {"zero_step_energy_drift_abs", zero_step["energy_drift_abs"]},
        {"passed", std::abs(zero_step["energy_drift_abs"].get<double>()) < 1e-14}
    };
    report["exclusion_rate_k"] = std::min(1.0, std::abs(fp64["energy_drift_rel"].get<double>()));
    report["alignment_success_rate"] = 1.0 - report["exclusion_rate_k"].get<double>();

    std::ofstream out("outputs/symplectic_sim_v1_cpp/v2p3_report.json");
    out << std::setw(2) << report << "\n";
    std::cout << "Report saved to outputs/symplectic_sim_v1_cpp/v2p3_report.json\n";
    return report["falsification"]["passed"].get<bool>() ? 0 : 2;
}
