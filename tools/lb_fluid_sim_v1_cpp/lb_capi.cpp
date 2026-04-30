#include "LBFluidEngineSYCL.hpp"
#include <cstring>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {
    typedef dase::fluid::LBFluidEngineSYCL LBEngine;

    EXPORT LBEngine* create_lb_engine(int nx, int ny) {
        return new LBEngine(nx, ny);
    }

    EXPORT void destroy_lb_engine(LBEngine* engine) {
        delete engine;
    }

    EXPORT void initialize_lb_equilibrium(LBEngine* engine, int nx, int ny, float rho_init) {
        if (!engine) return;
        
        for (int idx = 0; idx < nx * ny; ++idx) {
            engine->rho[idx] = rho_init;
            engine->ux[idx] = 0.0f;
            engine->uy[idx] = 0.0f;
            for (int i = 0; i < 9; ++i) {
                engine->f_in[i * nx * ny + idx] = engine->w[i] * rho_init;
            }
        }
    }

    EXPORT void set_lb_mask(LBEngine* engine, uint8_t* mask_data, int nx, int ny) {
        if (!engine) return;
        std::memcpy(engine->mask, mask_data, nx * ny);
    }

    EXPORT void run_lb_steps(LBEngine* engine, float tau, float u_inlet, int steps) {
        if (!engine) return;
        for (int i = 0; i < steps; ++i) {
            engine->step(tau, u_inlet);
        }
    }

    EXPORT float* get_lb_ux_ptr(LBEngine* engine) { return engine->ux; }
    EXPORT float* get_lb_uy_ptr(LBEngine* engine) { return engine->uy; }
    EXPORT float* get_lb_rho_ptr(LBEngine* engine) { return engine->rho; }
}
