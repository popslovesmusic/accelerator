#include "level2_engine.h"
#include "level2_pde_engine_factory.h"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace py = pybind11;

namespace {

constexpr double kRhoFloor = 1.0e-6;
constexpr double kActivityFloor = 1.0e-8;
constexpr double kExclusionThreshold = 1.0;

std::vector<double> as_vector(const py::array_t<double, py::array::c_style | py::array::forcecast>& array) {
    const auto view = array.unchecked<1>();
    std::vector<double> values(static_cast<std::size_t>(view.shape(0)));
    for (py::ssize_t i = 0; i < view.shape(0); ++i) {
        values[static_cast<std::size_t>(i)] = view(i);
    }
    return values;
}

py::array_t<double> as_numpy(const std::vector<double>& values) {
    py::array_t<double> array(values.size());
    auto view = array.mutable_unchecked<1>();
    for (py::ssize_t i = 0; i < view.shape(0); ++i) {
        view(i) = values[static_cast<std::size_t>(i)];
    }
    return array;
}

py::dict snapshot_to_dict(const level2::Snapshot& snapshot) {
    py::dict data;
    data["epsilon"] = as_numpy(snapshot.epsilon);
    data["rho"] = as_numpy(snapshot.rho);
    data["residue"] = as_numpy(snapshot.residue);
    if (!snapshot.delta.empty()) {
        data["delta"] = as_numpy(snapshot.delta);
    }
    if (!snapshot.sigma.empty()) {
        data["sigma"] = as_numpy(snapshot.sigma);
    }
    return data;
}

double trapz(const std::vector<double>& y, const std::vector<double>& x) {
    if (y.size() < 2 || x.size() < 2 || y.size() != x.size()) {
        return 0.0;
    }
    double total = 0.0;
    for (std::size_t i = 0; i + 1 < y.size(); ++i) {
        total += 0.5 * (y[i] + y[i + 1]) * (x[i + 1] - x[i]);
    }
    return total;
}

std::vector<bool> activity_mask(const std::vector<double>& epsilon, const std::vector<double>& rho) {
    std::vector<bool> active(epsilon.size(), false);
    for (std::size_t i = 0; i < epsilon.size(); ++i) {
        active[i] = (epsilon[i] + rho[i]) > kActivityFloor;
    }
    return active;
}

std::vector<double> node_ratio(const std::vector<double>& epsilon, const std::vector<double>& rho, const std::vector<bool>& active) {
    std::vector<double> ratio(epsilon.size(), 0.0);
    for (std::size_t i = 0; i < epsilon.size(); ++i) {
        if (!active[i]) {
            ratio[i] = std::numeric_limits<double>::quiet_NaN();
            continue;
        }
        ratio[i] = epsilon[i] / std::max(rho[i], kRhoFloor);
    }
    return ratio;
}

std::vector<double> sharpness(const std::vector<double>& ratio, double dx) {
    std::vector<double> sigma(ratio.size(), 0.0);
    if (ratio.empty()) {
        return sigma;
    }
    if (ratio.size() == 1 || dx == 0.0) {
        return sigma;
    }
    std::vector<double> safe_ratio(ratio.size(), 0.0);
    for (std::size_t i = 0; i < ratio.size(); ++i) {
        safe_ratio[i] = std::isfinite(ratio[i]) ? ratio[i] : 0.0;
    }
    sigma[0] = std::abs((safe_ratio[1] - safe_ratio[0]) / dx);
    for (std::size_t i = 1; i + 1 < ratio.size(); ++i) {
        sigma[i] = std::abs((safe_ratio[i + 1] - safe_ratio[i - 1]) / (2.0 * dx));
    }
    sigma[ratio.size() - 1] = std::abs((safe_ratio[ratio.size() - 1] - safe_ratio[ratio.size() - 2]) / dx);
    for (std::size_t i = 0; i < ratio.size(); ++i) {
        if (!std::isfinite(ratio[i])) {
            sigma[i] = 0.0;
        }
    }
    return sigma;
}

std::vector<double> connected_lengths(const std::vector<bool>& mask, double dx) {
    std::vector<double> lengths;
    int start = -1;
    for (int i = 0; i < static_cast<int>(mask.size()); ++i) {
        if (mask[static_cast<std::size_t>(i)] && start < 0) {
            start = i;
        } else if (!mask[static_cast<std::size_t>(i)] && start >= 0) {
            lengths.push_back(static_cast<double>(i - start) * dx);
            start = -1;
        }
    }
    if (start >= 0) {
        lengths.push_back(static_cast<double>(static_cast<int>(mask.size()) - start) * dx);
    }
    return lengths;
}

std::vector<double> interface_positions(const std::vector<double>& x, const std::vector<double>& ratio) {
    std::vector<double> positions;
    if (x.size() < 2 || ratio.size() < 2) {
        return positions;
    }
    for (std::size_t i = 0; i + 1 < ratio.size(); ++i) {
        const double left = ratio[i] - 1.0;
        const double right = ratio[i + 1] - 1.0;
        if (!std::isfinite(left) || !std::isfinite(right)) {
            continue;
        }
        if (left == 0.0) {
            positions.push_back(x[i]);
        } else if (left * right < 0.0) {
            const double frac = std::abs(left) / (std::abs(left) + std::abs(right));
            positions.push_back(x[i] + frac * (x[i + 1] - x[i]));
        }
    }
    return positions;
}

double mean_of_masked_side(const std::vector<double>& x, const std::vector<double>& residue, double position, bool left_side) {
    double total = 0.0;
    int count = 0;
    for (std::size_t i = 0; i < x.size(); ++i) {
        const bool include = left_side ? (x[i] < position) : (x[i] >= position);
        if (include) {
            total += residue[i];
            ++count;
        }
    }
    if (count > 0) {
        return total / static_cast<double>(count);
    }
    return left_side ? residue.front() : residue.back();
}

double median_copy(std::vector<double> values) {
    if (values.empty()) {
        return 0.0;
    }
    const std::size_t mid = values.size() / 2;
    std::nth_element(values.begin(), values.begin() + static_cast<std::ptrdiff_t>(mid), values.end());
    if (values.size() % 2 == 1) {
        return values[mid];
    }
    const double high = values[mid];
    std::nth_element(values.begin(), values.begin() + static_cast<std::ptrdiff_t>(mid - 1), values.begin() + static_cast<std::ptrdiff_t>(mid));
    return 0.5 * (values[mid - 1] + high);
}

py::dict compute_snapshot_metrics_cpp(
    const py::array_t<double, py::array::c_style | py::array::forcecast>& x_array,
    double time_value,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& epsilon_array,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& rho_array,
    const py::array_t<double, py::array::c_style | py::array::forcecast>& residue_array
) {
    const std::vector<double> x = as_vector(x_array);
    const std::vector<double> epsilon = as_vector(epsilon_array);
    const std::vector<double> rho = as_vector(rho_array);
    const std::vector<double> residue = as_vector(residue_array);
    if (x.empty() || epsilon.empty() || rho.empty() || residue.empty()) {
        throw std::runtime_error("compute_snapshot_metrics requires non-empty x, epsilon, rho, and residue arrays");
    }
    if (x.size() != epsilon.size() || x.size() != rho.size() || x.size() != residue.size()) {
        throw std::runtime_error("compute_snapshot_metrics requires x, epsilon, rho, and residue arrays of equal length");
    }

    const double dx = x.size() > 1 ? (x[1] - x[0]) : 1.0;
    const std::vector<bool> active = activity_mask(epsilon, rho);
    const std::vector<double> ratio = node_ratio(epsilon, rho, active);
    const std::vector<double> sigma = sharpness(ratio, dx);

    std::vector<bool> exclusion_mask(ratio.size(), false);
    std::vector<bool> pressure_mask(ratio.size(), false);
    int exclusion_count = 0;
    int active_count = 0;
    int undefined_ratio_count = 0;
    for (std::size_t i = 0; i < ratio.size(); ++i) {
        exclusion_mask[i] = active[i] && ratio[i] > kExclusionThreshold;
        pressure_mask[i] = active[i] && !exclusion_mask[i];
        exclusion_count += exclusion_mask[i] ? 1 : 0;
        active_count += active[i] ? 1 : 0;
        undefined_ratio_count += !std::isfinite(ratio[i]) ? 1 : 0;
    }

    const std::vector<double> exclusion_lengths = connected_lengths(exclusion_mask, dx);
    const std::vector<double> pressure_lengths = connected_lengths(pressure_mask, dx);
    const std::vector<double> front_positions = interface_positions(x, ratio);

    py::list fronts;
    for (std::size_t front_id = 0; front_id < front_positions.size(); ++front_id) {
        const double position = front_positions[front_id];
        const auto it = std::lower_bound(x.begin(), x.end(), position);
        std::size_t nearest_idx = static_cast<std::size_t>(std::distance(x.begin(), it));
        if (nearest_idx >= x.size()) {
            nearest_idx = x.size() - 1;
        }
        const double left_mean_R = mean_of_masked_side(x, residue, position, true);
        const double right_mean_R = mean_of_masked_side(x, residue, position, false);
        py::dict front;
        front["time"] = time_value;
        front["front_id"] = static_cast<int>(front_id);
        front["front_position"] = position;
        front["front_velocity"] = 0.0;
        front["front_width"] = 1.0 / std::max(sigma[nearest_idx], kRhoFloor);
        front["front_sharpness"] = sigma[nearest_idx];
        front["left_mean_R"] = left_mean_R;
        front["right_mean_R"] = right_mean_R;
        front["residue_asymmetry"] = left_mean_R - right_mean_R;
        fronts.append(front);
    }

    const double mean_eps = std::accumulate(epsilon.begin(), epsilon.end(), 0.0) / static_cast<double>(epsilon.size());
    const double mean_rho = std::accumulate(rho.begin(), rho.end(), 0.0) / static_cast<double>(rho.size());
    const double mean_residue = std::accumulate(residue.begin(), residue.end(), 0.0) / static_cast<double>(residue.size());
    double var_eps = 0.0;
    double var_rho = 0.0;
    double var_residue = 0.0;
    double ratio_sum = 0.0;
    double sigma_sum = 0.0;
    std::vector<double> active_ratio_values;
    double max_ratio = 0.0;
    double max_sigma = 0.0;
    for (std::size_t i = 0; i < epsilon.size(); ++i) {
        const double eps_delta = epsilon[i] - mean_eps;
        const double rho_delta = rho[i] - mean_rho;
        const double residue_delta = residue[i] - mean_residue;
        var_eps += eps_delta * eps_delta;
        var_rho += rho_delta * rho_delta;
        var_residue += residue_delta * residue_delta;
        if (active[i]) {
            ratio_sum += ratio[i];
            sigma_sum += sigma[i];
            active_ratio_values.push_back(ratio[i]);
            max_ratio = std::max(max_ratio, ratio[i]);
            max_sigma = std::max(max_sigma, sigma[i]);
        }
    }
    var_eps /= static_cast<double>(epsilon.size());
    var_rho /= static_cast<double>(rho.size());
    var_residue /= static_cast<double>(residue.size());
    const double mean_ratio = active_count > 0 ? ratio_sum / static_cast<double>(active_count) : 0.0;
    const double mean_sigma = active_count > 0 ? sigma_sum / static_cast<double>(active_count) : 0.0;

    py::dict metrics;
    metrics["time"] = time_value;
    metrics["mean_eps"] = mean_eps;
    metrics["mean_rho"] = mean_rho;
    metrics["mean_R"] = mean_residue;
    metrics["var_eps"] = var_eps;
    metrics["var_rho"] = var_rho;
    metrics["var_R"] = var_residue;
    metrics["total_eps"] = trapz(epsilon, x);
    metrics["total_rho"] = trapz(rho, x);
    metrics["total_R"] = trapz(residue, x);
    metrics["exclusion_fraction"] = active_count > 0 ? static_cast<double>(exclusion_count) / static_cast<double>(active_count) : 0.0;
    metrics["interface_count"] = static_cast<int>(front_positions.size());
    metrics["max_sharpness"] = max_sigma;
    metrics["n_exclusion_domains"] = static_cast<int>(exclusion_lengths.size());
    metrics["largest_exclusion_domain"] = exclusion_lengths.empty() ? 0.0 : *std::max_element(exclusion_lengths.begin(), exclusion_lengths.end());
    metrics["largest_pressure_domain"] = pressure_lengths.empty() ? 0.0 : *std::max_element(pressure_lengths.begin(), pressure_lengths.end());
    metrics["mean_node_ratio"] = mean_ratio;
    metrics["median_node_ratio"] = median_copy(active_ratio_values);
    metrics["max_node_ratio"] = max_ratio;
    metrics["mean_sharpness"] = mean_sigma;
    metrics["inactive_fraction"] = 1.0 - (static_cast<double>(active_count) / static_cast<double>(ratio.size()));
    metrics["active_fraction"] = static_cast<double>(active_count) / static_cast<double>(ratio.size());
    metrics["excluded_active_fraction"] = active_count > 0 ? static_cast<double>(exclusion_count) / static_cast<double>(active_count) : 0.0;
    metrics["undefined_ratio_fraction"] = static_cast<double>(undefined_ratio_count) / static_cast<double>(ratio.size());

    py::dict profile;
    profile["x"] = as_numpy(x);
    profile["eps"] = as_numpy(epsilon);
    profile["rho"] = as_numpy(rho);
    profile["R"] = as_numpy(residue);
    profile["node_ratio"] = as_numpy(ratio);
    profile["sharpness"] = as_numpy(sigma);

    py::dict response;
    response["metrics"] = metrics;
    response["fronts"] = fronts;
    response["profile"] = profile;
    return response;
}

py::dict simulate_pde_cpp(
    const py::dict& params_dict,
    const py::dict& grid_dict,
    const py::dict& initial_state_dict,
    double blowup_threshold,
    const std::string& phase_expression
) {
    level2::Parameters params{
        params_dict["a"].cast<double>(),
        params_dict["alpha"].cast<double>(),
        params_dict["b"].cast<double>(),
        params_dict["beta"].cast<double>(),
        params_dict["c"].cast<double>(),
        params_dict["gamma"].cast<double>(),
        params_dict["kappa"].cast<double>(),
        params_dict["lam"].cast<double>(),
        params_dict["u"].cast<double>(),
        params_dict["v"].cast<double>(),
        params_dict["s"].cast<double>(),
        params_dict["h"].cast<double>(),
        params_dict["D_eps"].cast<double>(),
        params_dict["D_rho"].cast<double>(),
        params_dict["D_R"].cast<double>(),
        params_dict.contains("eta_kappa") ? params_dict["eta_kappa"].cast<double>() : 1.0,
        params_dict.contains("eta_u") ? params_dict["eta_u"].cast<double>() : 1.0,
        params_dict.contains("mu") ? params_dict["mu"].cast<double>() : 0.0,
        params_dict.contains("nu") ? params_dict["nu"].cast<double>() : 0.0,
        params_dict.contains("delta_alpha") ? params_dict["delta_alpha"].cast<double>() : 0.0,
        params_dict.contains("delta_beta") ? params_dict["delta_beta"].cast<double>() : 0.0,
    };

    level2::GridConfig grid{
        grid_dict["L"].cast<double>(),
        grid_dict["Nx"].cast<int>(),
        grid_dict["t_final"].cast<double>(),
        grid_dict["dt"].cast<double>(),
        grid_dict["save_every"].cast<int>(),
    };

    level2::SimulationState initial_state{
        as_vector(initial_state_dict["epsilon"].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>()),
        as_vector(initial_state_dict["rho"].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>()),
        as_vector(initial_state_dict["residue"].cast<py::array_t<double, py::array::c_style | py::array::forcecast>>()),
    };

    const level2::SimulationResult result = level2::default_pde_engine().run(
        params,
        grid,
        initial_state,
        blowup_threshold,
        phase_expression
    );

    py::list snapshots;
    for (const auto& snapshot : result.snapshots) {
        snapshots.append(snapshot_to_dict(snapshot));
    }

    py::dict response;
    response["x"] = as_numpy(result.x);
    response["times"] = result.times;
    response["snapshots"] = snapshots;
    response["blew_up"] = result.blew_up;
    response["negative_undershoot_steps_detected"] = result.negative_undershoot_events;
    response["negative_undershoot_events"] = result.negative_undershoot_events;
    response["nonnegativity_violations"] = result.negative_undershoot_events;
    response["engine_name"] = result.engine_name;
    return response;
}

int get_native_max_threads() {
#if defined(_OPENMP)
    return omp_get_max_threads();
#else
    return 1;
#endif
}

void set_native_num_threads(int num_threads) {
    if (num_threads < 1) {
        throw std::invalid_argument("num_threads must be >= 1");
    }
#if defined(_OPENMP)
    omp_set_dynamic(0);
    omp_set_num_threads(num_threads);
#else
    (void)num_threads;
#endif
}

}  // namespace

PYBIND11_MODULE(_level2_native, module) {
    module.doc() = "Native Level 2 simulation hooks";
    module.def(
        "simulate_pde",
        &simulate_pde_cpp,
        py::arg("params"),
        py::arg("grid"),
        py::arg("initial_state"),
        py::arg("blowup_threshold") = 1.0e6,
        py::arg("phase_expression") = "standard"
    );
    module.def("compute_snapshot_metrics", &compute_snapshot_metrics_cpp, py::arg("x"), py::arg("time"), py::arg("epsilon"), py::arg("rho"), py::arg("residue"));
    module.def("get_max_threads", &get_native_max_threads);
    module.def("set_num_threads", &set_native_num_threads, py::arg("num_threads"));
}
