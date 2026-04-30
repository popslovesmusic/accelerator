#pragma once

#include <vector>
#include <string>
#include <future>
#include <functional>
#include <map>
#include "json.hpp"

namespace dase {
namespace validation {

using json = nlohmann::json;

/**
 * Result of a single falsification test.
 */
struct TestResult {
    std::string name;
    bool passed;
    std::string status; // PASS, FAIL, ERROR
    std::map<std::string, double> metrics;
    std::vector<std::string> failures;
};

inline void to_json(json& j, const TestResult& tr) {
    j = json{{"name", tr.name}, {"passed", tr.passed}, {"status", tr.status}, {"metrics", tr.metrics}, {"failures", tr.failures}};
}

/**
 * High-performance Falsification & Unit Test Runner.
 * Orchestrates parallel simulation runs across the ecosystem.
 */
class FalsificationRunner {
public:
    FalsificationRunner(int num_threads = 0);
    ~FalsificationRunner();

    /**
     * Run a full suite defined in JSON.
     */
    std::vector<TestResult> runSuite(const json& suite_json);

    /**
     * Add a single test to the queue.
     */
    void addTest(const json& test_def);

private:
    int num_threads_;
    std::vector<json> test_queue_;

    // Internal dispatcher for parallel execution
    TestResult executeTest(const json& test_def);
    
    // Assertion evaluation logic
    bool evaluateAssertion(const std::string& assertion, const std::map<std::string, double>& metrics, std::string& message);
};

} // namespace validation
} // namespace dase
