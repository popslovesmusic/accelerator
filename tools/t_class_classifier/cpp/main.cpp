#include "schemas.hpp"
#include "json.hpp"
#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>

using json = nlohmann::json;

// Declaring functions from other files to build without headers where simple
RealizedClosureTrace parse_trace(const json& j);
void validate_schema_integrity(const json& j);
void sanitize_and_filter(json& j, const std::string& action);
TSig build_t_sig(const RealizedClosureTrace& trace);
ClassificationResult assign_t_class(const TSig& sig);
void write_decision_audit(const ClassificationResult& res, const std::string& output_path);

int main(int argc, char* argv[]) {
    std::string input_path = "";
    std::string output_path = "";
    std::string action = "reject";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) {
            input_path = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            output_path = argv[++i];
        } else if (arg == "--action" && i + 1 < argc) {
            action = argv[++i];
        }
    }

    if (input_path.empty() || output_path.empty()) {
        std::cerr << "Usage: " << argv[0] << " --input <input_file> --output <output_file> [--action <reject|strip>]\n";
        return 1;
    }

    try {
        std::ifstream in(input_path);
        if (!in.is_open()) {
            throw std::runtime_error("Could not open input file: " + input_path);
        }
        
        json raw_data;
        in >> raw_data;

        validate_schema_integrity(raw_data);
        sanitize_and_filter(raw_data, action);

        RealizedClosureTrace trace = parse_trace(raw_data);
        TSig sig = build_t_sig(trace);
        ClassificationResult res = assign_t_class(sig);

        write_decision_audit(res, output_path);
        std::cout << "Classification successful: Assigned class " << res.t_class << " to " << input_path << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error during classification: " << e.what() << "\n";
        return 1;
    }
}
