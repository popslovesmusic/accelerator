/**
 * IGSOA Gravitational Wave Engine Orchestrator
 *
 * Integrates SymmetryField, FractionalSolver, and SourceManager into a
 * complete 3D simulation engine for the DASE ecosystem.
 */

#pragma once

#include "igsoa_gw_engine/core/symmetry_field.h"
#include "igsoa_gw_engine/core/fractional_solver.h"
#include "igsoa_gw_engine/core/source_manager.h"
#include "igsoa_gw_engine/core/projection_operators.h"
#include "igsoa_gw_engine/core/echo_generator.h"
#include <chrono>
#include <memory>
#include <vector>
#include <string>

namespace dase {
namespace igsoa {
namespace gw {

/**
 * IGSOAGWEngine
 *
 * High-level orchestrator for 3D GW simulations
 */
class IGSOAGWEngine {
public:
    /**
     * Constructor
     * @param field_config Configuration for the spatial grid and physics
     */
    explicit IGSOAGWEngine(const SymmetryFieldConfig& field_config)
        : field_(std::make_unique<SymmetryField>(field_config))
        , current_time_(0.0)
        , total_steps_(0)
        , total_operations_(0)
    {
        // Initialize fractional solver
        FractionalSolverConfig solver_config;
        solver_config.dt = field_config.dt;
        solver_config.T_max = 100.0;
        solver_config.alpha_min = field_config.alpha_min;
        solver_config.alpha_max = field_config.alpha_max;
        
        solver_ = std::make_unique<FractionalSolver>(solver_config, field_->getTotalPoints());
        
        // Initialize binary merger (default source)
        BinaryMergerConfig binary_config;
        source_manager_ = std::make_unique<BinaryMerger>(binary_config);
        
        // Initialize operators
        ProjectionConfig projection_config;
        projections_ = std::make_unique<ProjectionOperators>(projection_config);
        
        EchoConfig echo_config;
        echoes_ = std::make_unique<EchoGenerator>(echo_config);
    }

    /**
     * Run simulation steps
     */
    void runMission(uint64_t num_steps) {
        auto start_time = std::chrono::high_resolution_clock::now();
        uint64_t ops_this_run = 0;
        
        double dt = field_->getTimestep();
        int total_points = field_->getTotalPoints();
        
        for (uint64_t step = 0; step < num_steps; step++) {
            // 1. Update source terms (binary system evolution)
            source_manager_->evolveOrbit(dt);
            std::vector<std::complex<double>> sources = source_manager_->computeSourceTerms(*field_, current_time_);
            
            // 2. Compute fractional derivatives (memory effects)
            std::vector<double> alpha_values = field_->getAlphaValues();
            std::vector<std::complex<double>> fractional_derivatives = solver_->computeDerivatives(alpha_values);
            
            // 3. Advance symmetry field δΦ
            field_->evolveStep(fractional_derivatives, sources);
            
            // 4. Update history in solver
            // We use the laplacian as a proxy for the second spatial derivative term
            // in the simplified fractional wave equation implementation
            std::vector<std::complex<double>> laplacians(total_points);
            for (int idx = 0; idx < total_points; idx++) {
                int i, j, k;
                field_->fromFlatIndex(idx, i, j, k);
                laplacians[idx] = field_->computeLaplacian(i, j, k);
            }
            solver_->updateHistory(field_->getDeltaPhiFlat(), laplacians, alpha_values, dt);
            
            // 5. Diagnostics
            echoes_->detectMerger(*field_, current_time_);
            
            current_time_ += dt;
            total_steps_++;
            ops_this_run += static_cast<uint64_t>(total_points) * 10; // Approx ops per node
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
        
        total_operations_ += ops_this_run;
        if (ops_this_run > 0) {
            ns_per_op_ = static_cast<double>(duration.count()) / ops_this_run;
            ops_per_sec_ = 1.0e9 / ns_per_op_;
        }
    }

    /**
     * Metrics and State
     */
    void getMetrics(double& ns_per_op, double& ops_per_sec, double& speedup, uint64_t& total_ops) const {
        ns_per_op = ns_per_op_;
        ops_per_sec = ops_per_sec_;
        speedup = (ns_per_op_ > 0.0) ? (15500.0 / ns_per_op_) : 0.0;
        total_ops = total_operations_;
    }

    double getTotalEnergy() const { return field_->computeTotalEnergy(); }
    double getCurrentTime() const { return current_time_; }
    int getNumNodes() const { return field_->getTotalPoints(); }

    const SymmetryField& getField() const { return *field_; }

private:
    std::unique_ptr<SymmetryField> field_;
    std::unique_ptr<FractionalSolver> solver_;
    std::unique_ptr<BinaryMerger> source_manager_;
    std::unique_ptr<ProjectionOperators> projections_;
    std::unique_ptr<EchoGenerator> echoes_;
    
    double current_time_;
    uint64_t total_steps_;
    uint64_t total_operations_;
    
    double ns_per_op_ = 0.0;
    double ops_per_sec_ = 0.0;
};

} // namespace gw
} // namespace igsoa
} // namespace dase
