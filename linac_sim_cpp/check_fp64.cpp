#include <sycl/sycl.hpp>
#include <iostream>

int main() {
    sycl::queue q(sycl::default_selector_v);
    auto dev = q.get_device();
    std::cout << "Device: " << dev.get_info<sycl::info::device::name>() << std::endl;
    std::cout << "FP64 support: " << (dev.has(sycl::aspect::fp64) ? "Yes" : "No") << std::endl;
    return 0;
}
