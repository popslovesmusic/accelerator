#include "BifurcationEngine.h"
#include <cmath>
#include <iostream>
#include <numeric>
#include <algorithm>

namespace dase {
namespace analysis {

BifurcationEngine::BifurcationEngine() {}

std::vector<PlateauResult> BifurcationEngine::runSweep(double start, double end, int steps, int plateau_len, 
                                                     EngineStepFunc step_func) {
    std::vector<PlateauResult> results;
    double current_state = 0.5;
    
    for (int i = 0; i < steps; ++i) {
        double p = start + (end - start) * i / (steps - 1);
        
        // 1. Warm-up
        for (int w = 0; w < 1000; ++w) {
             current_state = step_func(current_state, p);
        }
        
        // 2. Data collection
        PlateauResult res;
        res.param_value = p;
        double sum = 0;
        for (int j = 0; j < plateau_len; ++j) {
            current_state = step_func(current_state, p);
            sum += current_state;
            if (j > plateau_len - 50) {
                res.history.push_back(current_state);
            }
        }
        res.observable_mean = sum / plateau_len;
        
        // 3. Stability check
        res.lyapunov_exponent = calculateLyapunov(current_state, p, 1000, step_func);
        
        results.push_back(res);
        total_evals_ += (1000 + plateau_len + 1000);
    }
    
    return results;
}

double BifurcationEngine::calculateLyapunov(double start_state, double param, int n_iters, EngineStepFunc step_func) {
    double x = start_state;
    double lyap = 0;
    const double eps = 1e-9;
    
    for (int i = 0; i < n_iters; ++i) {
        double next_x = step_func(x, param);
        double deriv = (step_func(x + eps, param) - next_x) / eps;
        if (std::abs(deriv) > 0) {
            lyap += std::log(std::abs(deriv));
        }
        x = next_x;
    }
    
    return lyap / n_iters;
}

} // namespace analysis
} // namespace dase
