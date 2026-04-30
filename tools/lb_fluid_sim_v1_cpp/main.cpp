#include "LBFluidEngineSYCL.hpp"
#include <chrono>
#include <vector>

int main() {
    try {
        const int nx = 256;
        const int ny = 128;
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

        const int steps = 100;
        std::cout << "Starting benchmark: " << nx << "x" << ny << ", " << steps << " steps..." << std::endl;

        auto start = std::chrono::high_resolution_clock::now();
        for(int i=0; i<steps; ++i) {
            engine.step(0.6f, 0.1f);
        }
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double> diff = end - start;
        std::cout << "Benchmark complete in " << diff.count() << " seconds." << std::endl;
        std::cout << "Throughput: " << (double)nx*ny*steps / diff.count() / 1e6 << " million cell updates/sec" << std::endl;

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
