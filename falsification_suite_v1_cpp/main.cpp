#include "FalsificationRunner.h"
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace dase::validation;

int main() {
    FalsificationRunner runner;
    
    // Create a mock suite with 100 tests
    json suite;
    for (int i = 0; i < 100; ++i) {
        json test;
        test["name"] = "Test_" + std::to_string(i);
        test["assertions"] = {"order_parameter > 0.8", "residue < 0.1"};
        suite["tests"].push_back(test);
    }

    std::cout << "Starting high-speed parallel falsification suite (100 tests)..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    auto results = runner.runSuite(suite);
    auto end = std::chrono::high_resolution_clock::now();
    
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

    int passed = 0;
    for (const auto& res : results) {
        if (res.passed) passed++;
    }

    std::cout << "\nSuite Summary:" << std::endl;
    std::cout << "  Total Tests: " << results.size() << std::endl;
    std::cout << "  Passed:      " << passed << std::endl;
    std::cout << "  Failed:      " << (results.size() - passed) << std::endl;
    std::cout << "  Runtime:     " << duration << " ms" << std::endl;
    std::cout << "  Throughput:  " << (duration / results.size()) << " ms/test" << std::endl;

    return 0;
}
