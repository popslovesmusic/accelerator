#pragma once

#include "AcceleratorEngineAVX2.h"
#include "LatticeElements.h"
#include "json.hpp"
#include <vector>
#include <memory>
#include <string>

namespace dase {
namespace accelerator {

using json = nlohmann::json;

class LatticeFactory {
public:
    static std::vector<std::unique_ptr<LatticeElement>> createFromJson(const json& lattice_json) {
        std::vector<std::unique_ptr<LatticeElement>> lattice;
        
        for (const auto& el : lattice_json) {
            std::string type = el["type"];
            
            if (type == "drift") {
                lattice.push_back(std::make_unique<Drift>(el["length"].get<double>()));
            } 
            else if (type == "quadrupole") {
                lattice.push_back(std::make_unique<Quadrupole>(
                    el["k1"].get<double>(), 
                    el["length"].get<double>()
                ));
            }
            else if (type == "rf_cavity") {
                lattice.push_back(std::make_unique<RFCavity>(
                    el["voltage"].get<double>(),
                    el["phase"].get<double>(),
                    el["harmonic"].get<double>()
                ));
            }
            else if (type == "space_charge_2d") {
                lattice.push_back(std::make_unique<SpaceCharge2D>(
                    el["nx"].get<int>(),
                    el["ny"].get<int>(),
                    el["width"].get<double>(),
                    el["height"].get<double>()
                ));
            }
        }
        
        return lattice;
    }
};

} // namespace accelerator
} // namespace dase
