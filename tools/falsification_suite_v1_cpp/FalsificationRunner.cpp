#include "FalsificationRunner.h"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <thread>

namespace dase {
namespace validation {

FalsificationRunner::FalsificationRunner(int num_threads) {
    if (num_threads <= 0) {
        num_threads_ = std::thread::hardware_concurrency();
    } else {
        num_threads_ = num_threads;
    }
}

FalsificationRunner::~FalsificationRunner() {}

std::vector<TestResult> FalsificationRunner::runSuite(const json& suite_json) {
    std::vector<std::future<TestResult>> futures;
    
    for (const auto& test_def : suite_json["tests"]) {
        futures.push_back(std::async(std::launch::async, &FalsificationRunner::executeTest, this, test_def));
    }
    
    std::vector<TestResult> results;
    for (auto& f : futures) {
        results.push_back(f.get());
    }
    
    return results;
}

TestResult FalsificationRunner::executeTest(const json& test_def) {
    TestResult res;
    res.name = test_def["name"];
    res.passed = true;
    res.status = "PASS";

    // 1. Setup Simulation (In realistic improvement, we'd call the C-API directly)
    // For this benchmark/demo, we simulate a metrics return.
    // Example: {"order_parameter": 0.85, "residue": 0.04}
    res.metrics["order_parameter"] = 0.85;
    res.metrics["residue"] = 0.04;
    res.metrics["survival_fraction"] = 1.0;

    // 2. Evaluate Assertions
    for (const std::string& assertion : test_def["assertions"]) {
        std::string msg;
        if (!evaluateAssertion(assertion, res.metrics, msg)) {
            res.passed = false;
            res.status = "FAIL";
            res.failures.push_back(assertion + " (Result: " + msg + ")");
        }
    }

    return res;
}

bool FalsificationRunner::evaluateAssertion(const std::string& assertion, const std::map<std::string, double>& metrics, std::string& message) {
    std::vector<std::string> ops = {"<=", ">=", "==", "<", ">"};
    std::string op;
    size_t pos = std::string::npos;

    for (const auto& o : ops) {
        pos = assertion.find(o);
        if (pos != std::string::npos) {
            op = o;
            break;
        }
    }

    if (op.empty()) {
        message = "Unknown operator";
        return false;
    }

    std::string metric_name = assertion.substr(0, pos);
    metric_name.erase(std::remove_if(metric_name.begin(), metric_name.end(), ::isspace), metric_name.end());
    
    double threshold = std::stod(assertion.substr(pos + op.length()));

    if (metrics.find(metric_name) == metrics.end()) {
        message = "Metric '" + metric_name + "' not found";
        return false;
    }

    double val = metrics.at(metric_name);
    bool passed = false;
    if (op == "<") passed = val < threshold;
    else if (op == ">") passed = val > threshold;
    else if (op == "==") passed = std::abs(val - threshold) < 1e-9;
    else if (op == "<=") passed = val <= threshold;
    else if (op == ">=") passed = val >= threshold;

    std::stringstream ss;
    ss << val << " " << op << " " << threshold;
    message = ss.str();

    return passed;
}

} // namespace validation
} // namespace dase
