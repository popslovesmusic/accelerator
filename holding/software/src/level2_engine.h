#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace level2 {

struct Parameters {
    double a;
    double alpha;
    double b;
    double beta;
    double c;
    double gamma;
    double kappa;
    double lam;
    double u;
    double v;
    double s;
    double h;
    double D_eps;
    double D_rho;
    double D_R;
    double eta_kappa = 1.0;
    double eta_u = 1.0;
    double mu = 0.0;
    double nu = 0.0;
    double delta_alpha = 0.0;
    double delta_beta = 0.0;
};

struct GridConfig {
    double L;
    int Nx;
    double t_final;
    double dt;
    int save_every;

    double dx() const noexcept {
        return static_cast<double>(L) / static_cast<double>(Nx);
    }

    int n_steps() const noexcept {
        return static_cast<int>(t_final / dt + 0.5);
    }
};

struct SimulationState {
    std::vector<double> epsilon;
    std::vector<double> rho;
    std::vector<double> residue;
};

struct Snapshot {
    std::vector<double> epsilon;
    std::vector<double> rho;
    std::vector<double> residue;
    std::vector<double> delta;
    std::vector<double> sigma;
};

struct SimulationResult {
    std::vector<double> x;
    std::vector<double> times;
    std::vector<Snapshot> snapshots;
    bool blew_up = false;
    int negative_undershoot_events = 0;
    std::string engine_name;
};

class ISimulationEngine {
public:
    virtual ~ISimulationEngine() = default;
    virtual const char* name() const noexcept = 0;
    virtual SimulationResult run(
        const Parameters& params,
        const GridConfig& grid,
        const SimulationState& initial_state,
        double blowup_threshold,
        const std::string& phase_expression
    ) const = 0;
};

}  // namespace level2
