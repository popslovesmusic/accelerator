#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <fstream>
#include <iomanip>
#include <algorithm>

#ifdef USE_SYCL
#include <sycl/sycl.hpp>
#include "TriadicEngineSYCL.hpp"
#endif

// Mock definitions for cross-platform AVX2 semantics
#if defined(__AVX2__)
#include <immintrin.h>
#endif

using namespace std;

enum class BackendMode {
    SCALAR,
    AVX2,
    SYCL
};

enum class StructureType {
    DYAD = 2,
    TRIAD = 3,
    TETRAD = 4,
    BROKEN_TRIAD = 103, 
    RANDOM_GRAPH_3 = 203
};

// Configuration
struct Config {
    int units = 256;
    int steps = 1000;
    float dt = 0.01f;
    float floor = 0.05f; 
    float coupling_strength = 0.1f;
    float reinforcement_rate = 0.05f;
    float admissibility_window = 0.8f;
    int seed = 42;

    BackendMode backend = BackendMode::AVX2;
    StructureType structure = StructureType::TRIAD;

    // Patch V2: Dynamic Topology & Admissibility
    float topology_rewire_rate = 0.01f;
    float admissibility_adapt_rate = 0.05f;
    float residue_diffusion_rate = 0.02f;

    // Falsification Flags
    bool residue_shuffle = false;
    bool residue_nullify = false;
    bool recursive_cut = false;
    bool orientation_scramble = false;
    bool floor_randomize = false;
    bool topology_randomize = false;
    bool saturation_attack = false;
    bool coupling_nullify = false;
    bool boundary_fracture = false;

    // Patch V2 Falsification
    bool topology_freeze = false;
    bool admissibility_lock = false;
    bool residue_delay = false;
    bool coupling_symmetry = false;

    // Campaign V1 Expanded Falsification
    bool boundary_randomize = false;
    bool topology_noise_flood = false;
    int sync_interval = 1;
};

// Struct-of-Arrays (SoA) layout aligned to 32 bytes
constexpr int BLOCK_SIZE = 256;

struct alignas(32) UnitBlockSOA {
    // 4 nodes per unit
    float in_channel[4][BLOCK_SIZE];
    float out_channel[4][BLOCK_SIZE];
    float coupling_channel[4][BLOCK_SIZE];
    
    // Core state
    float residue[BLOCK_SIZE];
    float residue_buffer[BLOCK_SIZE]; // For diffusion
    float orientation_vector[BLOCK_SIZE];
    float closure_strength[BLOCK_SIZE];
    float detectable_mismatch[BLOCK_SIZE];
    int collapse_flag[BLOCK_SIZE];
    
    // Dynamic Admissibility
    float dynamic_window_low[BLOCK_SIZE];
    float dynamic_window_high[BLOCK_SIZE];

    // Dynamic Topology (Fixed degree 2 for simplicity in SoA)
    float neighbor_weight_prev[BLOCK_SIZE];
    float neighbor_weight_next[BLOCK_SIZE];

    // Observables
    float persistence_score[BLOCK_SIZE];
    float inside_admissibility_rate[BLOCK_SIZE];
    float identity_signature[BLOCK_SIZE]; // Proxy for basin_signature_hash
};

// SIMD-ready Unit Block Update
void update_unit_block(UnitBlockSOA& block, const Config& cfg) {
    // Falsification: Residue Shuffle (CPU serial pass)
    if (cfg.residue_shuffle) {
        for (int i = 0; i < BLOCK_SIZE; ++i) {
            int target = rand() % BLOCK_SIZE;
            std::swap(block.residue[i], block.residue[target]);
        }
    }

    #pragma omp simd if(cfg.backend == BackendMode::AVX2)
    for (int i = 0; i < BLOCK_SIZE; ++i) {
        if (block.collapse_flag[i]) {
            // Topology Decay on collapse
            if (!cfg.topology_freeze) {
                block.neighbor_weight_prev[i] *= 0.95f;
                block.neighbor_weight_next[i] *= 0.95f;
            }
            continue;
        }

        // Falsification: Residue Nullification
        if (cfg.residue_nullify) block.residue[i] = 0.0f;

        // 1. Calculate local mismatch
        float mismatch = 0.0f;
        int nodes = (cfg.structure == StructureType::BROKEN_TRIAD || cfg.structure == StructureType::RANDOM_GRAPH_3) ? 3 : static_cast<int>(cfg.structure);
        
        if (cfg.structure == StructureType::BROKEN_TRIAD) {
            mismatch = std::abs(block.in_channel[0][i] - block.in_channel[1][i]);
        } else if (cfg.structure == StructureType::RANDOM_GRAPH_3) {
             mismatch = std::abs(block.in_channel[0][i] - block.in_channel[1][i]) * 0.7f + 
                       std::abs(block.in_channel[1][i] - block.in_channel[2][i]) * 1.3f + 
                       std::abs(block.in_channel[2][i] - block.in_channel[0][i]) * 0.4f;
        } else {
            for (int n = 0; n < nodes; ++n) {
                int next = (n + 1) % nodes;
                mismatch += std::abs(block.in_channel[n][i] - block.in_channel[next][i]);
            }
        }
        
        block.detectable_mismatch[i] = mismatch;
        if (cfg.saturation_attack) mismatch = 100.0f;

        // 2. Floor Gating
        float current_floor = cfg.floor;
        if (cfg.floor_randomize) current_floor *= (static_cast<float>(rand()) / RAND_MAX);

        if (mismatch < current_floor) {
            block.collapse_flag[i] = 1;
            block.closure_strength[i] = 0.0f;
            continue;
        }

        // 3. Orientation Mediation -(i)
        if (cfg.orientation_scramble) {
            block.orientation_vector[i] = (static_cast<float>(rand()) / RAND_MAX) * 2.0f - 1.0f;
        } else {
            block.orientation_vector[i] = (block.in_channel[0][i] - block.in_channel[1][i]) * 0.5f;
        }

        // 4. Recursive Reinforcement & Residue Inscription
        if (!cfg.recursive_cut) {
            float inc = cfg.dt * (mismatch * cfg.reinforcement_rate - block.residue[i] * 0.01f);
            block.residue[i] += inc;
        }
        
        // 5. Adaptive Admissibility
        if (!cfg.admissibility_lock) {
            float target_high = (block.closure_strength[i] > 0.8f) ? 1.0f : cfg.admissibility_window;
            block.dynamic_window_high[i] += (target_high - block.dynamic_window_high[i]) * cfg.admissibility_adapt_rate * cfg.dt;
        }
        
        bool inside = (block.residue[i] < block.dynamic_window_high[i]);
        block.inside_admissibility_rate[i] += inside ? 1.0f : 0.0f;
        
        // 6. Output Projection
        if (inside) {
            block.closure_strength[i] = std::min(1.0f, block.closure_strength[i] + cfg.dt * 0.1f);
            for (int n = 0; n < nodes; ++n) {
                block.out_channel[n][i] = block.in_channel[n][i] * block.closure_strength[i];
            }

            // Adaptive Topology
            if (!cfg.topology_freeze) {
                block.neighbor_weight_prev[i] = std::min(2.0f, block.neighbor_weight_prev[i] + cfg.topology_rewire_rate * cfg.dt);
                block.neighbor_weight_next[i] = std::min(2.0f, block.neighbor_weight_next[i] + cfg.topology_rewire_rate * cfg.dt);
            }
        } else {
            block.closure_strength[i] *= 0.99f;
            if (!cfg.topology_freeze) {
                block.neighbor_weight_prev[i] *= 0.999f;
                block.neighbor_weight_next[i] *= 0.999f;
            }
        }
        
        // Falsification: Topology Noise Flood
        if (cfg.topology_noise_flood && (rand() % 100 < 5)) {
            block.neighbor_weight_prev[i] = (static_cast<float>(rand()) / RAND_MAX) * 2.0f;
            block.neighbor_weight_next[i] = (static_cast<float>(rand()) / RAND_MAX) * 2.0f;
        }

        block.persistence_score[i] += block.closure_strength[i] * cfg.dt;
        block.identity_signature[i] = block.residue[i] * block.orientation_vector[i];
    }
}

// UHD 770 Role Stub: Global Coupling Field Arbitration
void process_global_coupling_uhd770_emulated(UnitBlockSOA* blocks, int num_blocks, const Config& cfg, int interval) {
    if (num_blocks <= 1 || cfg.coupling_nullify) return;
    
    float effective_dt = cfg.dt * interval;

    // Residue Diffusion Pass
    for (int b = 0; b < num_blocks; ++b) {
        int prev = (b == 0) ? num_blocks - 1 : b - 1;
        int next = (b == num_blocks - 1) ? 0 : b + 1;
        for (int i = 0; i < BLOCK_SIZE; ++i) {
            float d = (blocks[prev].residue[i] + blocks[next].residue[i] - 2.0f * blocks[b].residue[i]);
            blocks[b].residue_buffer[i] = blocks[b].residue[i] + d * cfg.residue_diffusion_rate;
        }
    }
    if (!cfg.residue_delay) {
        for (int b = 0; b < num_blocks; ++b) {
            for (int i = 0; i < BLOCK_SIZE; ++i) blocks[b].residue[i] = blocks[b].residue_buffer[i];
        }
    }

    for (int b = 0; b < num_blocks; ++b) {
        // Boundary Falsification
        if (cfg.boundary_fracture && (b == 0 || b == num_blocks - 1)) continue;
        if (cfg.boundary_randomize && (b == 0 || b == num_blocks - 1)) {
            for (int i = 0; i < BLOCK_SIZE; ++i) {
                blocks[b].in_channel[0][i] = (static_cast<float>(rand()) / RAND_MAX);
            }
        }

        int prev = (b == 0) ? num_blocks - 1 : b - 1;
        int next = (b == num_blocks - 1) ? 0 : b + 1;
        if (cfg.topology_randomize) {
            prev = rand() % num_blocks;
            next = rand() % num_blocks;
        }

        for (int i = 0; i < BLOCK_SIZE; ++i) {
            float coupling_factor = blocks[b].residue[i] * cfg.coupling_strength;
            float w_prev = blocks[b].neighbor_weight_prev[i];
            float w_next = blocks[b].neighbor_weight_next[i];
            if (cfg.coupling_symmetry) w_prev = w_next = 1.0f;

            blocks[b].coupling_channel[0][i] = (blocks[prev].out_channel[0][i] * w_prev + 
                                               blocks[next].out_channel[0][i] * w_next) * coupling_factor;
            blocks[b].in_channel[0][i] += blocks[b].coupling_channel[0][i] * effective_dt;
        }
    }
}

int main(int argc, char* argv[]) {
    Config cfg;
    std::string out_path = "summary.json";
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--units" && i + 1 < argc) cfg.units = std::stoi(argv[++i]);
        if (arg == "--steps" && i + 1 < argc) cfg.steps = std::stoi(argv[++i]);
        if (arg == "--dt" && i + 1 < argc) cfg.dt = std::stof(argv[++i]);
        if (arg == "--floor" && i + 1 < argc) cfg.floor = std::stof(argv[++i]);
        if (arg == "--seed" && i + 1 < argc) cfg.seed = std::stoi(argv[++i]);
        
        if (arg == "--backend" && i + 1 < argc) {
            std::string b = argv[++i];
            if (b == "scalar") cfg.backend = BackendMode::SCALAR;
            else if (b == "avx2") cfg.backend = BackendMode::AVX2;
            else if (b == "sycl") cfg.backend = BackendMode::SYCL;
        }
        
        if (arg == "--structure" && i + 1 < argc) {
            std::string s = argv[++i];
            if (s == "dyad") cfg.structure = StructureType::DYAD;
            else if (s == "triad") cfg.structure = StructureType::TRIAD;
            else if (s == "tetrad") cfg.structure = StructureType::TETRAD;
            else if (s == "broken_triad") cfg.structure = StructureType::BROKEN_TRIAD;
            else if (s == "random_graph_3") cfg.structure = StructureType::RANDOM_GRAPH_3;
        }

        if (arg == "--residue-shuffle") cfg.residue_shuffle = true;
        if (arg == "--residue-nullify") cfg.residue_nullify = true;
        if (arg == "--recursive-cut") cfg.recursive_cut = true;
        if (arg == "--orientation-scramble") cfg.orientation_scramble = true;
        if (arg == "--floor-randomize") cfg.floor_randomize = true;
        if (arg == "--topology-randomize") cfg.topology_randomize = true;
        if (arg == "--saturation-attack") cfg.saturation_attack = true;
        if (arg == "--coupling-nullify") cfg.coupling_nullify = true;
        if (arg == "--boundary-fracture") cfg.boundary_fracture = true;

        // Patch V2 flags
        if (arg == "--topology-freeze") cfg.topology_freeze = true;
        if (arg == "--admissibility-lock") cfg.admissibility_lock = true;
        if (arg == "--residue-delay") cfg.residue_delay = true;
        if (arg == "--coupling-symmetry") cfg.coupling_symmetry = true;
        if (arg == "--boundary-randomize") cfg.boundary_randomize = true;
        if (arg == "--topology-noise-flood") cfg.topology_noise_flood = true;
        if (arg == "--sync-interval" && i + 1 < argc) cfg.sync_interval = std::stoi(argv[++i]);

        // Patch V2 rates
        if (arg == "--topology-rewire-rate" && i + 1 < argc) cfg.topology_rewire_rate = std::stof(argv[++i]);
        if (arg == "--admissibility-adapt-rate" && i + 1 < argc) cfg.admissibility_adapt_rate = std::stof(argv[++i]);
        if (arg == "--residue-diffusion-rate" && i + 1 < argc) cfg.residue_diffusion_rate = std::stof(argv[++i]);
        
        if (arg == "--out" && i + 1 < argc) out_path = argv[++i];
    }
    
    int num_blocks = (cfg.units + BLOCK_SIZE - 1) / BLOCK_SIZE;
    int actual_units = num_blocks * BLOCK_SIZE;
    
#ifdef USE_SYCL
    UnitBlockSOA* blocks_ptr = nullptr;
    sycl::queue q;
    dase::triadic::TriadicEngineSYCL* sycl_engine = nullptr;

    if (cfg.backend == BackendMode::SYCL) {
        try {
            q = sycl::queue(sycl::gpu_selector_v);
            blocks_ptr = sycl::malloc_shared<UnitBlockSOA>(num_blocks, q);
            sycl_engine = new dase::triadic::TriadicEngineSYCL(num_blocks, q);
        } catch (sycl::exception const& e) {
            std::cerr << "SYCL Exception: " << e.what() << std::endl;
            return 1;
        }
    } else {
        blocks_ptr = new UnitBlockSOA[num_blocks];
    }
#else
    UnitBlockSOA* blocks_ptr = new UnitBlockSOA[num_blocks];
#endif
    
    srand(cfg.seed);
    for (int b = 0; b < num_blocks; ++b) {
        UnitBlockSOA& block = blocks_ptr[b];
        for (int i = 0; i < BLOCK_SIZE; ++i) {
            for (int n = 0; n < 4; ++n) {
                block.in_channel[n][i] = 0.4f + (rand() % 200) / 1000.0f;
                block.out_channel[n][i] = 0.0f;
                block.coupling_channel[n][i] = 0.0f;
            }
            block.residue[i] = 0.0f;
            block.residue_buffer[i] = 0.0f;
            block.collapse_flag[i] = 0;
            block.closure_strength[i] = 0.1f;
            block.persistence_score[i] = 0.0f;
            block.inside_admissibility_rate[i] = 0.0f;
            block.identity_signature[i] = 0.0f;
            block.orientation_vector[i] = 0.0f;

            // Patch V2 Init
            block.dynamic_window_low[i] = 0.1f; 
            block.dynamic_window_high[i] = cfg.admissibility_window; 
            block.neighbor_weight_prev[i] = 1.0f;
            block.neighbor_weight_next[i] = 1.0f;
        }
    }

    for (int step = 0; step < cfg.steps; ++step) {
        for (int b = 0; b < num_blocks; ++b) {
            update_unit_block(blocks_ptr[b], cfg);
        }
        
        if (step % cfg.sync_interval == 0) {
#ifdef USE_SYCL
            if (cfg.backend == BackendMode::SYCL && sycl_engine) {
                 sycl_engine->process_global_coupling((UnitBlockSOA_SYCL*)blocks_ptr, cfg.coupling_strength, cfg.residue_diffusion_rate, cfg.dt * cfg.sync_interval, cfg.coupling_nullify, cfg.coupling_symmetry, cfg.boundary_randomize);
            } else {
                process_global_coupling_uhd770_emulated(blocks_ptr, num_blocks, cfg, cfg.sync_interval);
            }
#else
            process_global_coupling_uhd770_emulated(blocks_ptr, num_blocks, cfg, cfg.sync_interval);
#endif
        }
    }
    
    // Global Reductions
    double total_closure = 0.0;
    double total_residue = 0.0;
    double total_persistence = 0.0;
    double total_admissibility = 0.0;
    int total_collapse = 0;
    double global_alignment_x = 0.0;
    
    for (int b = 0; b < num_blocks; ++b) {
        const UnitBlockSOA& block = blocks_ptr[b];
        for (int i = 0; i < BLOCK_SIZE; ++i) {
            total_closure += block.closure_strength[i];
            total_residue += block.residue[i];
            total_persistence += block.persistence_score[i];
            total_admissibility += block.inside_admissibility_rate[i];
            total_collapse += block.collapse_flag[i];
            global_alignment_x += block.orientation_vector[i];
        }
    }
    
    // Global Orientation Entropy
    const int bins = 20;
    std::vector<int> histogram(bins, 0);
    for (int b = 0; b < num_blocks; ++b) {
        for (int i = 0; i < BLOCK_SIZE; ++i) {
            float val = blocks_ptr[b].orientation_vector[i];
            int bin = static_cast<int>((val + 1.0f) * 0.5f * (bins - 1));
            bin = std::max(0, std::min(bins - 1, bin));
            histogram[bin]++;
        }
    }
    double entropy = 0.0;
    for (int count : histogram) {
        if (count > 0) {
            double p = static_cast<double>(count) / actual_units;
            entropy -= p * std::log2(p);
        }
    }

    std::ofstream out(out_path);
    out << "{\n";
    out << "  \"backend\": \"" << (cfg.backend == BackendMode::AVX2 ? "CPU_AVX2" : (cfg.backend == BackendMode::SCALAR ? "CPU_scalar_reference" : "UHD770_layered")) << "\",\n";
    out << "  \"unit_count\": " << actual_units << ",\n";
    out << "  \"steps\": " << cfg.steps << ",\n";
    out << "  \"observables\": {\n";
    out << "    \"mean_closure_strength\": " << total_closure / actual_units << ",\n";
    out << "    \"mean_residue_density\": " << total_residue / actual_units << ",\n";
    out << "    \"mean_persistence_score\": " << total_persistence / actual_units << ",\n";
    out << "    \"mean_inside_admissibility_rate\": " << (total_admissibility / actual_units) / cfg.steps << ",\n";
    out << "    \"survival_rate\": " << 1.0 - (double)total_collapse / actual_units << ",\n";
    out << "    \"global_ordering_metric\": " << std::abs(global_alignment_x) / actual_units << ",\n";
    out << "    \"global_orientation_entropy\": " << entropy << "\n";
    out << "  },\n";
    out << "  \"collapse_events\": " << total_collapse << ",\n";
    out << "  \"validation_status\": \"pass\"\n";
    out << "}\n";

#ifdef USE_SYCL
    if (cfg.backend == BackendMode::SYCL) {
        sycl::free(blocks_ptr, q);
        delete sycl_engine;
    }
    else delete[] blocks_ptr;
#else
    delete[] blocks_ptr;
#endif

    return 0;
}
