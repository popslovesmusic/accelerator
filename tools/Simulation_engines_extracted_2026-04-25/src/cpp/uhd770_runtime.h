#pragma once

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <sstream>
#include <string>
#include <vector>

#if defined(DASE_ENABLE_UHD770_SYCL)
  #if defined(__has_include)
    #if __has_include(<sycl/sycl.hpp>)
      #include <sycl/sycl.hpp>
      #define DASE_HAS_SYCL_RUNTIME 1
    #endif
  #endif
#endif

#ifndef DASE_HAS_SYCL_RUNTIME
#define DASE_HAS_SYCL_RUNTIME 0
#endif

namespace dase::uhd770 {

struct DeviceInfo {
    bool sycl_compiled = false;
    bool gpu_available = false;
    bool uhd770_likely = false;
    bool fp64_supported = false;
    std::string selected_device = "unavailable";
    std::string selected_vendor = "unavailable";
    std::string backend = "cpu_fallback";
    std::string notes;
};

struct ProbeResult {
    DeviceInfo device;
    bool passed = false;
    std::size_t n = 0;
    double elapsed_ms = 0.0;
    double max_abs_error = 0.0;
    double checksum = 0.0;
};

inline bool contains_ci(std::string text, std::string needle) {
    std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    std::transform(needle.begin(), needle.end(), needle.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return text.find(needle) != std::string::npos;
}

inline DeviceInfo detectDevice() {
    DeviceInfo info;
#if DASE_HAS_SYCL_RUNTIME
    info.sycl_compiled = true;
    try {
        std::vector<sycl::device> devices = sycl::device::get_devices();
        sycl::device selected;
        bool found = false;
        for (const auto& dev : devices) {
            std::string name = dev.get_info<sycl::info::device::name>();
            std::string vendor = dev.get_info<sycl::info::device::vendor>();
            if (dev.is_gpu() && contains_ci(vendor, "intel")) {
                selected = dev;
                found = true;
                if (contains_ci(name, "uhd") || contains_ci(name, "770") || contains_ci(name, "graphics")) {
                    break;
                }
            }
        }
        if (!found) {
            info.notes = "SYCL compiled, but no Intel GPU device was found. CPU fallback remains available.";
            return info;
        }

        info.gpu_available = true;
        info.selected_device = selected.get_info<sycl::info::device::name>();
        info.selected_vendor = selected.get_info<sycl::info::device::vendor>();
        info.backend = "oneAPI_SYCL";
        info.uhd770_likely = contains_ci(info.selected_device, "uhd") ||
                             contains_ci(info.selected_device, "770") ||
                             contains_ci(info.selected_device, "graphics");
        info.fp64_supported = selected.has(sycl::aspect::fp64);
        info.notes = info.uhd770_likely
            ? "Intel integrated GPU detected; FP32 kernels are the default rigor path for UHD 770."
            : "Intel GPU detected; name does not explicitly identify UHD 770.";
    } catch (const sycl::exception& e) {
        info.notes = std::string("SYCL device detection failed: ") + e.what();
    }
#else
    info.notes = "Compiled without DASE_ENABLE_UHD770_SYCL or without available <sycl/sycl.hpp>.";
#endif
    return info;
}

inline ProbeResult runFp32VectorProbe(std::size_t n = 1 << 20) {
    ProbeResult result;
    result.n = n;
    result.device = detectDevice();

#if DASE_HAS_SYCL_RUNTIME
    if (!result.device.gpu_available) {
        return result;
    }
    try {
        sycl::queue q(sycl::gpu_selector_v);
        float* a = sycl::malloc_shared<float>(n, q);
        float* b = sycl::malloc_shared<float>(n, q);
        float* c = sycl::malloc_shared<float>(n, q);
        if (!a || !b || !c) {
            result.device.notes += " Allocation failed during FP32 probe.";
            return result;
        }

        for (std::size_t i = 0; i < n; ++i) {
            a[i] = static_cast<float>((i % 1024) * 0.001f);
            b[i] = static_cast<float>(1.0f + (i % 257) * 0.002f);
            c[i] = 0.0f;
        }

        auto start = std::chrono::high_resolution_clock::now();
        q.parallel_for(sycl::range<1>(n), [=](sycl::id<1> idx) {
            std::size_t i = idx.get(0);
            c[i] = a[i] * b[i] + sycl::sin(a[i]);
        }).wait();
        auto end = std::chrono::high_resolution_clock::now();

        double max_error = 0.0;
        double checksum = 0.0;
        for (std::size_t i = 0; i < n; ++i) {
            double expected = static_cast<double>(a[i]) * static_cast<double>(b[i]) + std::sin(static_cast<double>(a[i]));
            double err = std::abs(static_cast<double>(c[i]) - expected);
            max_error = std::max(max_error, err);
            checksum += c[i];
        }

        sycl::free(a, q);
        sycl::free(b, q);
        sycl::free(c, q);

        result.elapsed_ms = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() / 1000.0;
        result.max_abs_error = max_error;
        result.checksum = checksum;
        result.passed = max_error < 5e-6;
    } catch (const sycl::exception& e) {
        result.device.notes += std::string(" FP32 vector probe failed: ") + e.what();
    }
#endif
    return result;
}

inline std::string toJson(const DeviceInfo& info) {
    auto esc = [](const std::string& s) {
        std::string out;
        for (char c : s) {
            if (c == '"' || c == '\\') out.push_back('\\');
            out.push_back(c);
        }
        return out;
    };
    std::ostringstream os;
    os << "{"
       << "\"sycl_compiled\":" << (info.sycl_compiled ? "true" : "false") << ","
       << "\"gpu_available\":" << (info.gpu_available ? "true" : "false") << ","
       << "\"uhd770_likely\":" << (info.uhd770_likely ? "true" : "false") << ","
       << "\"fp64_supported\":" << (info.fp64_supported ? "true" : "false") << ","
       << "\"selected_device\":\"" << esc(info.selected_device) << "\","
       << "\"selected_vendor\":\"" << esc(info.selected_vendor) << "\","
       << "\"backend\":\"" << esc(info.backend) << "\","
       << "\"notes\":\"" << esc(info.notes) << "\""
       << "}";
    return os.str();
}

} // namespace dase::uhd770
