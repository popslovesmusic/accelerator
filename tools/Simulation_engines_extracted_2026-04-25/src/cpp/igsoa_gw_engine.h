/**
 * IGSOA Gravitational Wave Engine Orchestrator (SYCL Redesign)
 *
 * Integrates redesigned SYCL-native core components for UHD 770.
 */

#pragma once

#include "igsoa_gw_engine/core/symmetry_field.h"
#include "igsoa_gw_engine/core/fractional_solver.h"
#include "igsoa_gw_engine/core/source_manager.h"
#include <chrono>
#include <memory>
#include <vector>

namespace dase {
namespace igsoa {
namespace gw {

class IGSOAGWEngine {
public:
    explicit IGSOAGWEngine(const SymmetryFieldConfig& config, sycl::queue& q)
        : q_(q)
        , field_(std::make_unique<SymmetryField>(config, q))
        , current_time_(0.0f)
        , total_steps_(0)
    {
        // 12-rank SOE for fractional solver
        solver_ = std::make_unique<FractionalSolver>(field_->getTotalPoints(), 12, q);
        
        BinaryMergerConfig binary_config;
        source_manager_ = std::make_unique<BinaryMerger>(binary_config, q);

        // USM scratch buffer for source terms
        source_buffer_ = sycl::malloc_device<std::complex<float>>(field_->getTotalPoints(), q);
        frac_deriv_buffer_ = sycl::malloc_device<std::complex<float>>(field_->getTotalPoints(), q);
    }

    ~IGSOAGWEngine() {
        sycl::free(source_buffer_, q_);
        sycl::free(frac_deriv_buffer_, q_);
    }

    void runMission(uint64_t num_steps) {
        auto start = std::chrono::high_resolution_clock::now();
        float dt = 0.01f; // Target timestep
        
        for (uint64_t step = 0; step < num_steps; step++) {
            // 1. Evolve orbital system and generate source terms on GPU
            source_manager_->evolveOrbit(dt);
            source_manager_->generateSourceTerms(source_buffer_, 64, 64, 64, 1000.0f, 1000.0f, 1000.0f, Vector3D(0,0,0));

            // 2. Compute fractional derivatives on GPU
            solver_->computeDerivatives(frac_deriv_buffer_, field_->getAlphaPtr());

            // 3. Optimized field evolution (Phase 3: Fused Kernel)
            field_->evolveStep(frac_deriv_buffer_, source_buffer_);

            // 4. Update memory history
            solver_->updateHistory(field_->getDeltaPhiPtr(), field_->getDeltaPhiPtr(), field_->getAlphaPtr(), dt);

            current_time_ += dt;
            total_steps_++;
        }
        q_.wait();
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);

        uint64_t ops_this_run = static_cast<uint64_t>(field_->getTotalPoints()) * num_steps;
        total_operations_ += ops_this_run;
        if (ops_this_run > 0) {
            ns_per_op_ = static_cast<double>(duration.count()) / ops_this_run;
            ops_per_sec_ = 1.0e9 / ns_per_op_;
        }
    }

    // Metrics and State
    void getMetrics(double& ns_per_op, double& ops_per_sec, double& speedup, uint64_t& total_ops) const {
        ns_per_op = ns_per_op_;
        ops_per_sec = ops_per_sec_;
        speedup = (ns_per_op_ > 0.0) ? (15500.0 / ns_per_op_) : 0.0;
        total_ops = total_operations_;
    }

    double getTotalEnergy() const { 
        // For the redesign, return a simple proxy or 0 for now
        return 0.0; 
    }
    double getCurrentTime() const { return current_time_; }
    int getNumNodes() const { return field_->getTotalPoints(); }

    // Diagnostics
    void getFieldData(std::vector<std::complex<float>>& output) {
        output.resize(field_->getTotalPoints());
        field_->copyToHost(output);
    }

private:
    sycl::queue& q_;
    std::unique_ptr<SymmetryField> field_;
    std::unique_ptr<FractionalSolver> solver_;
    std::unique_ptr<BinaryMerger> source_manager_;

    // USM Intermediates
    std::complex<float>* source_buffer_;
    std::complex<float>* frac_deriv_buffer_;

    float current_time_;
    uint64_t total_steps_;
    uint64_t total_operations_ = 0;
    double ns_per_op_ = 0.0;
    double ops_per_sec_ = 0.0;
};

} // namespace gw
} // namespace igsoa
} // namespace dase
