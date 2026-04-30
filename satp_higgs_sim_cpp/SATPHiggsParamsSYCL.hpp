#pragma once

#include <cmath>

namespace dase {
namespace satp_higgs {

template <typename T>
struct SATPHiggsParamsSYCL {
    T c;           // Wave speed
    T gamma_phi;   // Scale field dissipation
    T gamma_h;     // Higgs dissipation
    T lambda;      // phi-h coupling strength
    T mu_squared;  // Higgs mass squared
    T lambda_h;    // Higgs self-coupling
    T h_vev;       // Higgs vacuum expectation value

    SATPHiggsParamsSYCL() 
        : c(1.0), gamma_phi(0.0), gamma_h(0.0), 
          lambda(0.1), mu_squared(-1.0), lambda_h(0.5) {
        updateVEV();
    }

    void updateVEV() {
        if (mu_squared < 0 && lambda_h > 0) {
            h_vev = std::sqrt(-mu_squared / (2.0 * lambda_h));
        } else {
            h_vev = 0.0;
        }
    }
};

} // namespace satp_higgs
} // namespace dase
