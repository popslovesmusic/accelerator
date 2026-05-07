/**
 * IGSOA Gravitational Wave Engine - Echo Generator (SYCL Stub)
 * 
 * Minimal stub to allow compilation of the redesigned GW engine.
 */

#pragma once

#include "symmetry_field.h"
#include <vector>

namespace dase {
namespace igsoa {
namespace gw {

class EchoGenerator {
public:
    explicit EchoGenerator(sycl::queue& q) : q_(q) {}

    // Stubs
    void generateEchoes(SymmetryField& field, std::vector<float>& output) {}

private:
    sycl::queue& q_;
};

} // namespace gw
} // namespace igsoa
} // namespace dase
