#include "BifurcationEngine.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::analysis;

int main() {
    BifurcationEngine analyzer;
    
    // Test with Logistic Map: x_{n+1} = r * x_n * (1 - x_n)
    auto logistic_map = [](double x, double r) {
        return r * x * (1.0 - x);
    };

    std::cout << "Starting high-speed bifurcation analysis (Logistic Map)..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Sweep parameter r from 2.5 to 4.0 (the interesting range)
    auto results = analyzer.runSweep(2.5, 4.0, 200, 1000, logistic_map);
    
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "\nBifurcation Results Sample:" << std::endl;
    std::cout << "R-Value | Mean-X | Lyapunov | Status" << std::endl;
    std::cout << "------------------------------------------" << std::endl;
    
    for (int i = 0; i < results.size(); i += 20) {
        const auto& r = results[i];
        std::string status = (r.lyapunov_exponent > 0) ? "CHAOTIC" : "STABLE";
        std::cout << r.param_value << "  | " << r.observable_mean << " | " 
                  << r.lyapunov_exponent << "  | " << status << std::endl;
    }

    std::cout << "\nAnalysis completed in " << duration << " ms" << std::endl;
    std::cout << "Total iterations evaluated: ~" << (200 * (1000 + 1000 + 1000)) << std::endl;

    return 0;
}
