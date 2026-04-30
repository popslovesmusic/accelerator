#include "uhd770_runtime.h"
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

int main(int argc, char** argv) {
    std::string out_path;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--out" && i + 1 < argc) {
            out_path = argv[++i];
        }
    }

    auto probe = dase::uhd770::runFp32VectorProbe();

    std::ostringstream report;
    report << "{\n";
    report << "  \"sim_id\": \"uhd770_device_probe_v1\",\n";
    report << "  \"schema\": \"v2.3_recoverable_report\",\n";
    report << "  \"device\": " << dase::uhd770::toJson(probe.device) << ",\n";
    report << "  \"probe\": {\n";
    report << "    \"name\": \"fp32_vector_math\",\n";
    report << "    \"passed\": " << (probe.passed ? "true" : "false") << ",\n";
    report << "    \"n\": " << probe.n << ",\n";
    report << "    \"elapsed_ms\": " << std::fixed << std::setprecision(6) << probe.elapsed_ms << ",\n";
    report << "    \"max_abs_error\": " << std::scientific << probe.max_abs_error << ",\n";
    report << "    \"checksum\": " << std::fixed << std::setprecision(6) << probe.checksum << "\n";
    report << "  },\n";
    report << "  \"rigor_notes\": [\n";
    report << "    \"UHD 770 is treated as an FP32-first SYCL target.\",\n";
    report << "    \"FP64 support is reported but not assumed for integrated-GPU production runs.\",\n";
    report << "    \"This probe verifies device selection and simple numeric agreement only; per-engine CPU/GPU regression remains required.\"\n";
    report << "  ]\n";
    report << "}\n";

    std::cout << report.str();

    if (!out_path.empty()) {
        std::filesystem::path p(out_path);
        if (p.has_parent_path()) {
            std::filesystem::create_directories(p.parent_path());
        }
        std::ofstream out(p);
        out << report.str();
    }

    return probe.passed ? 0 : (probe.device.gpu_available ? 2 : 1);
}
