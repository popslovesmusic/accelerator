#include "FalsificationRunner.h"
#include <iostream>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

using namespace dase::validation;

extern "C" {

EXPORT FalsificationRunner* create_falsification_runner(int num_threads) {
    return new FalsificationRunner(num_threads);
}

EXPORT void destroy_falsification_runner(FalsificationRunner* runner) {
    delete runner;
}

EXPORT void run_falsification_suite(FalsificationRunner* runner, const char* suite_json_str, char* report_out, int max_len) {
    json suite = json::parse(suite_json_str);
    auto results = runner->runSuite(suite);
    
    json report = results; // Uses the to_json conversion
    std::string s = report.dump();
    strncpy(report_out, s.c_str(), max_len);
}

}
