#pragma once

#include <string>
#include <vector>
#include <cmath>

namespace dase {
namespace linac {

enum class ComponentType {
    DRIFT = 0,
    FOCUSING_LENS = 1,
    RF_GAP = 2
};

struct ComponentData {
    ComponentType type;
    float start_m;
    float length_m;
    float peak_field_v_per_m;
    float frequency_hz;
    float phase_rad;
    float focusing_strength_1_per_m2;
    float z_focusing_strength_1_per_m2;
};

} // namespace linac
} // namespace dase
