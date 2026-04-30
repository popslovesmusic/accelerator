#include "LBFluidEngineSYCL.hpp"
#include <chrono>
#include <vector>

#include "json.hpp"
#include <fstream>
#include <filesystem>

using json = nlohmann::json;

int main(int argc, char** argv) {
    std::string config_path = "";
    std::string out_dir = "outputs/lb_fluid_sim_v1_cpp";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == "--out" && i + 1 < argc) out_dir = argv[++i];
    }

    try {
        int nx = 256;
        int ny = 128;
        int steps = 100;
        float tau = 0.6f;
        float u_inlet = 0.1f;

        json config_json;
        if (!config_path.empty()) {
            std::ifstream f(config_path);
            if (f.is_open()) {
                config_json = json::parse(f);
                nx = config_json.value("nx", 256);
                ny = config_json.value("ny", 128);
                steps = config_json.value("steps", 100);
                tau = config_json.value("tau", 0.6f);
                u_inlet = config_json.value("u_inlet", 0.1f);
            }
        }

        dase::fluid::LBFluidEngineSYCL engine(nx, ny);

        // Initialize mask (boundary)
        std::vector<uint8_t> h_mask(nx * ny, 0);
        for(int x=0; x<nx; ++x) {
            h_mask[0 * nx + x] = 1;      // Bottom wall
            h_mask[(ny-1) * nx + x] = 1; // Top wall
        }
        
        // Circular obstacle
        int cx = nx/4, cy = ny/2, r = 15;
        for(int y=0; y<ny; ++y) {
            for(int x=0; x<nx; ++x) {
                if((x-cx)*(x-cx) + (y-cy)*(y-cy) < r*r) {
                    h_mask[y*nx + x] = 1;
                }
            }
        }
        std::memcpy(engine.mask, h_mask.data(), nx * ny);

        // Initialize equilibrium
        for(int i=0; i<nx*ny; ++i) {
            engine.rho[i] = 1.0f;
            for(int d=0; d<9; ++d) {
                engine.f_in[d*nx*ny + i] = engine.w[d];
            }
        }

        std::cout << "Starting LB Fluid simulation: " << nx << "x" << ny << ", " << steps << " steps..." << std::endl;

        auto start = std::chrono::high_resolution_clock::now();
        for(int i=0; i<steps; ++i) {
            engine.step(tau, u_inlet);
        }
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double> diff = end - start;
        
        json final_metrics;
        final_metrics["runtime_ms"] = diff.count() * 1000.0;
        final_metrics["fluid_volume"] = 0; // Placeholder for actual calculation
        final_metrics["mean_velocity"] = 0; // Placeholder

        json summary;
        summary["config"] = config_json;
        summary["final_metrics"] = final_metrics;
        summary["status"] = "completed";

        std::filesystem::create_directories(out_dir);
        std::ofstream o(std::filesystem::path(out_dir) / "summary.json");
        o << std::setw(4) << summary << std::endl;

        std::cout << "Simulation complete. Summary saved to " << out_dir << "/summary.json" << std::endl;

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
