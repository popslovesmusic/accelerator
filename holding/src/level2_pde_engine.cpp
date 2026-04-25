#include "level2_engine.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <sstream>
#include <stdexcept>
#include <vector>

#if defined(__AVX2__)
#include <immintrin.h>
#endif

namespace level2 {
namespace {

constexpr double kEpsilon = 1.0e-12;
constexpr double kRhoFloor = 1.0e-6;
constexpr double kActivityFloor = 1.0e-8;
constexpr double kExclusionThreshold = 1.0;
constexpr int kParallelThreshold = 256;
constexpr int kSimdParallelThreshold = 1024;
constexpr const char* kPhaseExpressionStandard = "standard";
constexpr const char* kPhaseExpressionInverted = "I_phi_inverted";
constexpr const char* kPhaseExpressionBasisInverse = "I_phi_v2_basis_inverse";
constexpr const char* kPhaseExpressionDeltaSigmaRho = "I_phi_v3_delta_sigma_rho";

std::vector<double> linspace(double start, double stop, int count) {
    std::vector<double> values(static_cast<std::size_t>(count));
    if (count <= 0) {
        return values;
    }
    const double step = (stop - start) / static_cast<double>(count);
    for (int i = 0; i < count; ++i) {
        values[static_cast<std::size_t>(i)] = start + static_cast<double>(i) * step;
    }
    return values;
}

std::string normalize_phase_expression(const std::string& phase_expression) {
    const std::string normalized = phase_expression.empty() ? std::string{kPhaseExpressionStandard} : phase_expression;
    if (
        normalized != kPhaseExpressionStandard
        && normalized != kPhaseExpressionInverted
        && normalized != kPhaseExpressionBasisInverse
        && normalized != kPhaseExpressionDeltaSigmaRho
    ) {
        throw std::invalid_argument("Unsupported phase_expression: " + phase_expression);
    }
    return normalized;
}

double basis_inverse_determinant(const Parameters& params) {
    return 1.0 - params.mu * params.nu;
}

void validate_basis_inverse_params(const Parameters& params) {
    const double determinant = basis_inverse_determinant(params);
    if (std::abs(determinant) <= 1.0e-9) {
        std::ostringstream message;
        message
            << "I_phi_v2_basis_inverse requires an invertible basis map; got 1 - mu*nu = "
            << determinant;
        throw std::invalid_argument(message.str());
    }
}

double delta_sigma_denominator(const Parameters& params) {
    return params.delta_alpha + params.delta_beta;
}

void validate_delta_sigma_params(const Parameters& params) {
    const double denominator = delta_sigma_denominator(params);
    if (std::abs(denominator) <= 1.0e-9) {
        std::ostringstream message;
        message
            << "I_phi_v3_delta_sigma_rho requires delta_alpha + delta_beta to be nonzero; got "
            << denominator;
        throw std::invalid_argument(message.str());
    }
}

void map_to_basis(
    const std::vector<double>& epsilon,
    const std::vector<double>& residue,
    const Parameters& params,
    std::vector<double>& basis_epsilon,
    std::vector<double>& basis_residue
) {
    basis_epsilon.resize(epsilon.size());
    basis_residue.resize(residue.size());
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(epsilon.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(epsilon.size()); ++i) {
        basis_epsilon[static_cast<std::size_t>(i)] = epsilon[static_cast<std::size_t>(i)] + params.mu * residue[static_cast<std::size_t>(i)];
        basis_residue[static_cast<std::size_t>(i)] = residue[static_cast<std::size_t>(i)] + params.nu * epsilon[static_cast<std::size_t>(i)];
    }
}

void map_from_basis(
    const std::vector<double>& basis_epsilon,
    const std::vector<double>& basis_residue,
    const Parameters& params,
    std::vector<double>& epsilon,
    std::vector<double>& residue
) {
    const double determinant = basis_inverse_determinant(params);
    epsilon.resize(basis_epsilon.size());
    residue.resize(basis_residue.size());
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(basis_epsilon.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(basis_epsilon.size()); ++i) {
        epsilon[static_cast<std::size_t>(i)] = (
            basis_epsilon[static_cast<std::size_t>(i)] - params.mu * basis_residue[static_cast<std::size_t>(i)]
        ) / determinant;
        residue[static_cast<std::size_t>(i)] = (
            basis_residue[static_cast<std::size_t>(i)] - params.nu * basis_epsilon[static_cast<std::size_t>(i)]
        ) / determinant;
    }
}

void map_to_delta_sigma(
    const std::vector<double>& epsilon,
    const std::vector<double>& residue,
    const Parameters& params,
    std::vector<double>& delta,
    std::vector<double>& sigma
) {
    delta.resize(epsilon.size());
    sigma.resize(residue.size());
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(epsilon.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(epsilon.size()); ++i) {
        delta[static_cast<std::size_t>(i)] = epsilon[static_cast<std::size_t>(i)] - params.delta_alpha * residue[static_cast<std::size_t>(i)];
        sigma[static_cast<std::size_t>(i)] = epsilon[static_cast<std::size_t>(i)] + params.delta_beta * residue[static_cast<std::size_t>(i)];
    }
}

void map_from_delta_sigma(
    const std::vector<double>& delta,
    const std::vector<double>& sigma,
    const Parameters& params,
    std::vector<double>& epsilon,
    std::vector<double>& residue
) {
    const double denominator = delta_sigma_denominator(params);
    epsilon.resize(delta.size());
    residue.resize(sigma.size());
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(delta.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(delta.size()); ++i) {
        epsilon[static_cast<std::size_t>(i)] = (
            params.delta_beta * delta[static_cast<std::size_t>(i)]
            + params.delta_alpha * sigma[static_cast<std::size_t>(i)]
        ) / denominator;
        residue[static_cast<std::size_t>(i)] = (
            sigma[static_cast<std::size_t>(i)] - delta[static_cast<std::size_t>(i)]
        ) / denominator;
    }
}

struct Bands {
    std::vector<double> lower;
    std::vector<double> diag;
    std::vector<double> upper;
};

struct TridiagonalWorkspace {
    std::vector<double> c_prime;
    std::vector<double> d_prime;
    std::vector<double> solution;

    explicit TridiagonalWorkspace(int n)
        : c_prime(static_cast<std::size_t>(std::max(0, n - 1)), 0.0)
        , d_prime(static_cast<std::size_t>(std::max(0, n)), 0.0)
        , solution(static_cast<std::size_t>(std::max(0, n)), 0.0) {}
};

Bands diffusion_matrix_bands(double diffusion, double dt, double dx, int n) {
    if (n < 2 || diffusion == 0.0 || dt == 0.0) {
        return Bands{
            std::vector<double>(static_cast<std::size_t>(std::max(0, n - 1)), 0.0),
            std::vector<double>(static_cast<std::size_t>(std::max(0, n)), 1.0),
            std::vector<double>(static_cast<std::size_t>(std::max(0, n - 1)), 0.0),
        };
    }

    const double r = diffusion * dt / (dx * dx);
    Bands bands{
        std::vector<double>(static_cast<std::size_t>(n - 1), -r),
        std::vector<double>(static_cast<std::size_t>(n), 1.0 + 2.0 * r),
        std::vector<double>(static_cast<std::size_t>(n - 1), -r),
    };
    bands.upper[0] = -2.0 * r;
    bands.lower[static_cast<std::size_t>(n - 2)] = -2.0 * r;
    return bands;
}

std::vector<double> solve_tridiagonal(
    const std::vector<double>& lower,
    const std::vector<double>& diag,
    const std::vector<double>& upper,
    const std::vector<double>& rhs,
    TridiagonalWorkspace& workspace
) {
    const int n = static_cast<int>(diag.size());
    if (n == 0) {
        return {};
    }
    if (n == 1) {
        return {rhs[0] / diag[0]};
    }

    std::vector<double>& c_prime = workspace.c_prime;
    std::vector<double>& d_prime = workspace.d_prime;
    std::vector<double>& solution = workspace.solution;

    c_prime[0] = upper[0] / diag[0];
    d_prime[0] = rhs[0] / diag[0];

    for (int i = 1; i < n; ++i) {
        const double denom = diag[static_cast<std::size_t>(i)] - lower[static_cast<std::size_t>(i - 1)] * c_prime[static_cast<std::size_t>(i - 1)];
        if (i < n - 1) {
            c_prime[static_cast<std::size_t>(i)] = upper[static_cast<std::size_t>(i)] / denom;
        }
        d_prime[static_cast<std::size_t>(i)] = (rhs[static_cast<std::size_t>(i)] - lower[static_cast<std::size_t>(i - 1)] * d_prime[static_cast<std::size_t>(i - 1)]) / denom;
    }

    solution[static_cast<std::size_t>(n - 1)] = d_prime[static_cast<std::size_t>(n - 1)];
    for (int i = n - 2; i >= 0; --i) {
        solution[static_cast<std::size_t>(i)] = d_prime[static_cast<std::size_t>(i)] - c_prime[static_cast<std::size_t>(i)] * solution[static_cast<std::size_t>(i + 1)];
    }
    return solution;
}

std::vector<double> implicit_diffusion_step(
    const std::vector<double>& field,
    const std::vector<double>& reaction,
    const Bands& bands,
    const GridConfig& grid,
    TridiagonalWorkspace& workspace
) {
    std::vector<double> rhs(field.size(), 0.0);
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(field.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(field.size()); ++i) {
        rhs[i] = field[i] + grid.dt * reaction[i];
    }
    if (field.size() < 2) {
        return rhs;
    }
    if (bands.diag.size() != field.size() || bands.lower.empty() || bands.upper.empty()) {
        return rhs;
    }
    return solve_tridiagonal(bands.lower, bands.diag, bands.upper, rhs, workspace);
}

bool any_invalid(const std::vector<double>& values, double threshold) {
    int invalid = 0;
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) reduction(|:invalid) if(static_cast<int>(values.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(values.size()); ++i) {
        const double value = values[static_cast<std::size_t>(i)];
        invalid |= (!std::isfinite(value) || std::abs(value) > threshold) ? 1 : 0;
    }
    return invalid != 0;
}

int count_negative_violations(const std::vector<double>& values) {
    int found_negative = 0;
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) reduction(|:found_negative) if(static_cast<int>(values.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(values.size()); ++i) {
        found_negative |= values[static_cast<std::size_t>(i)] < -kEpsilon ? 1 : 0;
    }
    return found_negative;
}

void clamp_nonnegative_inplace(std::vector<double>& values) {
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(static_cast<int>(values.size()) >= kParallelThreshold)
#endif
    for (int i = 0; i < static_cast<int>(values.size()); ++i) {
        if (values[static_cast<std::size_t>(i)] < 0.0) {
            values[static_cast<std::size_t>(i)] = 0.0;
        }
    }
}

void compute_reaction_terms(
    const std::vector<double>& epsilon,
    const std::vector<double>& rho,
    const std::vector<double>& residue,
    const Parameters& params,
    const std::string& phase_expression,
    std::vector<double>& epsilon_reaction,
    std::vector<double>& rho_reaction,
    std::vector<double>& residue_reaction
) {
    const int n = static_cast<int>(epsilon.size());
    const bool inverted = phase_expression == kPhaseExpressionInverted;
    const bool basis_inverse = phase_expression == kPhaseExpressionBasisInverse;
    const bool delta_sigma = phase_expression == kPhaseExpressionDeltaSigmaRho;

#if defined(__AVX2__)
    if (!delta_sigma) {
    const __m256d a_vec = _mm256_set1_pd(params.a);
    const __m256d alpha_vec = _mm256_set1_pd(params.alpha);
    const __m256d b_vec = _mm256_set1_pd(params.b);
    const __m256d beta_vec = _mm256_set1_pd(params.beta);
    const __m256d c_vec = _mm256_set1_pd(params.c);
    const __m256d gamma_vec = _mm256_set1_pd(params.gamma);
    const __m256d kappa_vec = _mm256_set1_pd(params.kappa);
    const __m256d lam_vec = _mm256_set1_pd(params.lam);
    const __m256d u_vec = _mm256_set1_pd(params.u);
    const __m256d v_vec = _mm256_set1_pd(params.v);
    const __m256d s_vec = _mm256_set1_pd(params.s);
    const __m256d h_vec = _mm256_set1_pd(params.h);
    const __m256d eta_kappa_vec = _mm256_set1_pd(params.eta_kappa);
    const __m256d eta_u_vec = _mm256_set1_pd(params.eta_u);
    const int simd_end = n - (n % 4);

    if (!inverted || basis_inverse) {
#if defined(_OPENMP)
        #pragma omp parallel for schedule(static) if(n >= kSimdParallelThreshold)
#endif
        for (int i = 0; i < simd_end; i += 4) {
            const __m256d eps = _mm256_loadu_pd(epsilon.data() + i);
            const __m256d rho_value = _mm256_loadu_pd(rho.data() + i);
            const __m256d residue_value = _mm256_loadu_pd(residue.data() + i);
            const __m256d eps_rho = _mm256_mul_pd(eps, rho_value);

            const __m256d eps_term = _mm256_mul_pd(a_vec, eps);
            const __m256d eps_cross = _mm256_mul_pd(b_vec, eps_rho);
            const __m256d eps_square = _mm256_mul_pd(c_vec, _mm256_mul_pd(eps, eps));
            const __m256d eps_residue = _mm256_mul_pd(u_vec, residue_value);
            const __m256d eps_result = _mm256_add_pd(
                _mm256_sub_pd(_mm256_sub_pd(eps_term, eps_cross), eps_square),
                _mm256_add_pd(eps_residue, s_vec)
            );

            const __m256d rho_term = _mm256_mul_pd(alpha_vec, rho_value);
            const __m256d rho_cross = _mm256_mul_pd(beta_vec, eps_rho);
            const __m256d rho_square = _mm256_mul_pd(gamma_vec, _mm256_mul_pd(rho_value, rho_value));
            const __m256d rho_residue = _mm256_mul_pd(v_vec, residue_value);
            const __m256d rho_result = _mm256_add_pd(
                _mm256_sub_pd(_mm256_sub_pd(rho_term, rho_cross), rho_square),
                _mm256_sub_pd(h_vec, rho_residue)
            );

            const __m256d residue_result = _mm256_sub_pd(_mm256_mul_pd(kappa_vec, eps), _mm256_mul_pd(lam_vec, residue_value));

            _mm256_storeu_pd(epsilon_reaction.data() + i, eps_result);
            _mm256_storeu_pd(rho_reaction.data() + i, rho_result);
            _mm256_storeu_pd(residue_reaction.data() + i, residue_result);
        }
    } else {
#if defined(_OPENMP)
        #pragma omp parallel for schedule(static) if(n >= kSimdParallelThreshold)
#endif
        for (int i = 0; i < simd_end; i += 4) {
            const __m256d eps = _mm256_loadu_pd(epsilon.data() + i);
            const __m256d rho_value = _mm256_loadu_pd(rho.data() + i);
            const __m256d residue_value = _mm256_loadu_pd(residue.data() + i);
            const __m256d eps_rho = _mm256_mul_pd(eps, rho_value);
            const __m256d residue_rho = _mm256_mul_pd(residue_value, rho_value);

            const __m256d eps_result = _mm256_sub_pd(
                _mm256_mul_pd(_mm256_mul_pd(eta_kappa_vec, kappa_vec), residue_value),
                _mm256_mul_pd(lam_vec, eps)
            );

            const __m256d rho_term = _mm256_mul_pd(alpha_vec, rho_value);
            const __m256d rho_cross = _mm256_mul_pd(beta_vec, eps_rho);
            const __m256d rho_square = _mm256_mul_pd(gamma_vec, _mm256_mul_pd(rho_value, rho_value));
            const __m256d rho_residue = _mm256_mul_pd(v_vec, residue_value);
            const __m256d rho_result = _mm256_add_pd(
                _mm256_sub_pd(_mm256_sub_pd(rho_term, rho_cross), rho_square),
                _mm256_sub_pd(h_vec, rho_residue)
            );

            const __m256d residue_term = _mm256_mul_pd(a_vec, residue_value);
            const __m256d residue_cross = _mm256_mul_pd(b_vec, residue_rho);
            const __m256d residue_square = _mm256_mul_pd(c_vec, _mm256_mul_pd(residue_value, residue_value));
            const __m256d residue_eps = _mm256_mul_pd(_mm256_mul_pd(eta_u_vec, u_vec), eps);
            const __m256d residue_result = _mm256_add_pd(
                _mm256_sub_pd(_mm256_sub_pd(residue_term, residue_cross), residue_square),
                _mm256_add_pd(residue_eps, s_vec)
            );

            _mm256_storeu_pd(epsilon_reaction.data() + i, eps_result);
            _mm256_storeu_pd(rho_reaction.data() + i, rho_result);
            _mm256_storeu_pd(residue_reaction.data() + i, residue_result);
        }
    }

#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if((n - simd_end) >= kParallelThreshold)
#endif
    for (int i = simd_end; i < n; ++i) {
        const double eps = epsilon[static_cast<std::size_t>(i)];
        const double rho_value = rho[static_cast<std::size_t>(i)];
        const double residue_value = residue[static_cast<std::size_t>(i)];
        const double eps_rho = eps * rho_value;
        if (!inverted || basis_inverse) {
            epsilon_reaction[static_cast<std::size_t>(i)] = (
                params.a * eps
                - params.b * eps_rho
                - params.c * eps * eps
                + params.u * residue_value
                + params.s
            );
            residue_reaction[static_cast<std::size_t>(i)] = params.kappa * eps - params.lam * residue_value;
        } else {
            epsilon_reaction[static_cast<std::size_t>(i)] = params.eta_kappa * params.kappa * residue_value - params.lam * eps;
            residue_reaction[static_cast<std::size_t>(i)] = (
                params.a * residue_value
                - params.b * residue_value * rho_value
                - params.c * residue_value * residue_value
                + params.eta_u * params.u * eps
                + params.s
            );
        }
        rho_reaction[static_cast<std::size_t>(i)] = (
            params.alpha * rho_value
            - params.beta * eps_rho
            - params.gamma * rho_value * rho_value
            - params.v * residue_value
            + params.h
        );
    }
    }
#else
#if defined(_OPENMP)
    #pragma omp parallel for schedule(static) if(n >= kParallelThreshold)
#endif
    for (int i = 0; i < n; ++i) {
        const double eps = epsilon[static_cast<std::size_t>(i)];
        const double rho_value = rho[static_cast<std::size_t>(i)];
        const double residue_value = residue[static_cast<std::size_t>(i)];
        const double eps_rho = eps * rho_value;
        if (delta_sigma) {
            epsilon_reaction[static_cast<std::size_t>(i)] = (
                params.a * eps
                - params.b * eps_rho
                - params.c * eps * eps * eps
                - params.u * eps * residue_value
                + params.s
            );
            residue_reaction[static_cast<std::size_t>(i)] = (
                (params.a - params.lam) * residue_value
                + params.kappa * eps
                - params.b * residue_value * rho_value
                - params.c * residue_value * residue_value
                + params.s
            );
            rho_reaction[static_cast<std::size_t>(i)] = (
                params.alpha * rho_value
                - params.beta * eps_rho
                - params.gamma * rho_value * rho_value
                - params.v * residue_value
                + params.h
            );
        } else if (!inverted || basis_inverse) {
            epsilon_reaction[static_cast<std::size_t>(i)] = (
                params.a * eps
                - params.b * eps_rho
                - params.c * eps * eps
                + params.u * residue_value
                + params.s
            );
            residue_reaction[static_cast<std::size_t>(i)] = params.kappa * eps - params.lam * residue_value;
        } else {
            epsilon_reaction[static_cast<std::size_t>(i)] = params.eta_kappa * params.kappa * residue_value - params.lam * eps;
            residue_reaction[static_cast<std::size_t>(i)] = (
                params.a * residue_value
                - params.b * residue_value * rho_value
                - params.c * residue_value * residue_value
                + params.eta_u * params.u * eps
                + params.s
            );
        }
        rho_reaction[static_cast<std::size_t>(i)] = (
            params.alpha * rho_value
            - params.beta * eps_rho
            - params.gamma * rho_value * rho_value
            - params.v * residue_value
            + params.h
        );
    }
#endif
}

class PdeSimulationEngine final : public ISimulationEngine {
public:
    const char* name() const noexcept override {
        return "level2_pde_cpp";
    }

    SimulationResult run(
        const Parameters& params,
        const GridConfig& grid,
        const SimulationState& initial_state,
        double blowup_threshold,
        const std::string& phase_expression
    ) const override {
        if (grid.Nx <= 0) {
            throw std::invalid_argument("Grid Nx must be positive.");
        }
        if (grid.dt <= 0.0) {
            throw std::invalid_argument("Grid dt must be positive.");
        }
        if (grid.save_every <= 0) {
            throw std::invalid_argument("Grid save_every must be positive.");
        }

        SimulationResult result;
        result.x = linspace(0.0, grid.L, grid.Nx);
        const std::string normalized_phase_expression = normalize_phase_expression(phase_expression);
        result.engine_name = std::string{name()} + "[" + normalized_phase_expression + "]";
        const bool use_basis_inverse = normalized_phase_expression == kPhaseExpressionBasisInverse;
        const bool use_delta_sigma = normalized_phase_expression == kPhaseExpressionDeltaSigmaRho;

        std::vector<double> epsilon = initial_state.epsilon;
        std::vector<double> rho = initial_state.rho;
        std::vector<double> residue = initial_state.residue;
        if (
            epsilon.size() != static_cast<std::size_t>(grid.Nx)
            || rho.size() != static_cast<std::size_t>(grid.Nx)
            || residue.size() != static_cast<std::size_t>(grid.Nx)
        ) {
            std::ostringstream message;
            message
                << "Initial state size mismatch: expected Nx=" << grid.Nx
                << ", epsilon=" << epsilon.size()
                << ", rho=" << rho.size()
                << ", residue=" << residue.size();
            throw std::runtime_error(message.str());
        }
        if (use_basis_inverse) {
            validate_basis_inverse_params(params);
            std::vector<double> basis_epsilon;
            std::vector<double> basis_residue;
            map_to_basis(epsilon, residue, params, basis_epsilon, basis_residue);
            epsilon = std::move(basis_epsilon);
            residue = std::move(basis_residue);
        } else if (use_delta_sigma) {
            validate_delta_sigma_params(params);
            std::vector<double> delta;
            std::vector<double> sigma;
            map_to_delta_sigma(epsilon, residue, params, delta, sigma);
            epsilon = std::move(delta);
            residue = std::move(sigma);
        }
        const Bands epsilon_bands = diffusion_matrix_bands(params.D_eps, grid.dt, grid.dx(), grid.Nx);
        const Bands rho_bands = diffusion_matrix_bands(params.D_rho, grid.dt, grid.dx(), grid.Nx);
        const Bands residue_bands = diffusion_matrix_bands(params.D_R, grid.dt, grid.dx(), grid.Nx);
        TridiagonalWorkspace epsilon_workspace(grid.Nx);
        TridiagonalWorkspace rho_workspace(grid.Nx);
        TridiagonalWorkspace residue_workspace(grid.Nx);
        std::vector<double> mapped_epsilon;
        std::vector<double> mapped_residue;
        std::vector<double> next_mapped_epsilon;
        std::vector<double> next_mapped_residue;
        std::vector<double> mapped_delta;
        std::vector<double> mapped_sigma;

        for (int step = 0; step <= grid.n_steps(); ++step) {
            if (step % grid.save_every == 0 || step == grid.n_steps()) {
                if (use_basis_inverse) {
                    map_from_basis(epsilon, residue, params, mapped_epsilon, mapped_residue);
                    mapped_delta.clear();
                    mapped_sigma.clear();
                } else if (use_delta_sigma) {
                    map_from_delta_sigma(epsilon, residue, params, mapped_epsilon, mapped_residue);
                    mapped_delta = epsilon;
                    mapped_sigma = residue;
                } else {
                    mapped_epsilon = epsilon;
                    mapped_residue = residue;
                    mapped_delta.clear();
                    mapped_sigma.clear();
                }
                result.times.push_back(static_cast<double>(step) * grid.dt);
                result.snapshots.push_back(Snapshot{mapped_epsilon, rho, mapped_residue, mapped_delta, mapped_sigma});
            }

            if (step == grid.n_steps()) {
                break;
            }

            std::vector<double> epsilon_reaction(epsilon.size(), 0.0);
            std::vector<double> rho_reaction(rho.size(), 0.0);
            std::vector<double> residue_reaction(residue.size(), 0.0);
            compute_reaction_terms(
                epsilon,
                rho,
                residue,
                params,
                normalized_phase_expression,
                epsilon_reaction,
                rho_reaction,
                residue_reaction
            );

            std::vector<double> next_epsilon = implicit_diffusion_step(epsilon, epsilon_reaction, epsilon_bands, grid, epsilon_workspace);
            std::vector<double> next_rho = implicit_diffusion_step(rho, rho_reaction, rho_bands, grid, rho_workspace);
            std::vector<double> next_residue = implicit_diffusion_step(residue, residue_reaction, residue_bands, grid, residue_workspace);

            if (use_basis_inverse) {
                map_from_basis(next_epsilon, next_residue, params, next_mapped_epsilon, next_mapped_residue);
            } else if (use_delta_sigma) {
                map_from_delta_sigma(next_epsilon, next_residue, params, next_mapped_epsilon, next_mapped_residue);
            } else {
                next_mapped_epsilon = next_epsilon;
                next_mapped_residue = next_residue;
            }

            if (
                any_invalid(next_epsilon, blowup_threshold)
                || any_invalid(next_rho, blowup_threshold)
                || any_invalid(next_residue, blowup_threshold)
                || any_invalid(next_mapped_epsilon, blowup_threshold)
                || any_invalid(next_mapped_residue, blowup_threshold)
            ) {
                result.blew_up = true;
                break;
            }

            result.negative_undershoot_events += count_negative_violations(next_mapped_epsilon);
            result.negative_undershoot_events += count_negative_violations(next_rho);
            result.negative_undershoot_events += count_negative_violations(next_mapped_residue);

            clamp_nonnegative_inplace(next_rho);
            if (!use_delta_sigma) {
                clamp_nonnegative_inplace(next_epsilon);
            }
            clamp_nonnegative_inplace(next_residue);
            epsilon = std::move(next_epsilon);
            rho = std::move(next_rho);
            residue = std::move(next_residue);
        }

        return result;
    }
};

}  // namespace

const ISimulationEngine& default_pde_engine() {
    static const PdeSimulationEngine engine{};
    return engine;
}

}  // namespace level2
