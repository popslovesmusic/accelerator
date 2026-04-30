#pragma once

#include <vector>
#include <string>
#include <functional>
#include <memory>
#include <omp.h>

namespace dase {
namespace analysis {

/**
 * Result for a single parameter plateau.
 */
struct PlateauResult {
    double param_value;
    double observable_mean;
    double lyapunov_exponent;
    std::vector<double> history; // Recent history for Poincare/Chaos mapping
};

/**
 * High-performance Bifurcation & Stability Analyzer.
 * Can wrap any function or engine to map regimes.
 */
class BifurcationEngine {
public:
    using EngineStepFunc = std::function<double(double current_state, double param)>;
    using MetricFunc = std::function<double(const std::vector<double>& history)>;

    BifurcationEngine();

    /**
     * Run a parameter sweep with continuation.
     * @param start Start value of the parameter
     * @param end End value of the parameter
     * @param steps Number of plateaus
     * @param plateau_len Number of iterations at each plateau
     * @param step_func The engine's mapping function x_{n+1} = f(x_n, p)
     */
    std::vector<PlateauResult> runSweep(double start, double end, int steps, int plateau_len, 
                                       EngineStepFunc step_func);

    /**
     * Specialized: Calculate Maximal Lyapunov Exponent.
     */
    double calculateLyapunov(double start_state, double param, int n_iters, EngineStepFunc step_func);

private:
    // Performance counters
    uint64_t total_evals_ = 0;
};

} // namespace analysis
} // namespace dase
