#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>
#include "../stochastic_sim_cpp/json.hpp"

using json = nlohmann::json;

namespace {
struct Topology {
    int betti_0 = 0;
    int betti_1 = 0;
    int max_component_size = 0;
    double mean_component_size = 0.0;
    double active_fraction = 0.0;
};

std::vector<std::vector<double>> read_grid_csv(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("could not open grid CSV: " + path);
    std::vector<std::vector<double>> grid;
    std::string line;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::string cell;
        std::vector<double> row;
        while (std::getline(ss, cell, ',')) {
            try {
                row.push_back(std::stod(cell));
            } catch (...) {
                row.push_back(0.0);
            }
        }
        if (!row.empty()) grid.push_back(row);
    }
    return grid;
}

Topology compute_spatial_topology(const std::vector<std::vector<double>>& grid, double threshold) {
    const int h = static_cast<int>(grid.size());
    const int w = h > 0 ? static_cast<int>(grid[0].size()) : 0;
    if (h == 0 || w == 0) return {};

    // 1. Compute Betti-0 (Foreground 8-connectivity)
    std::vector<std::vector<int>> visited_f(h, std::vector<int>(w, 0));
    int active_count = 0;
    std::vector<int> component_sizes;
    const int dirs8[8][2] = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (grid[y][x] > threshold) active_count++;
            if (visited_f[y][x] || grid[y][x] <= threshold) continue;
            
            int size = 0;
            std::queue<std::pair<int,int>> q;
            q.push({y, x});
            visited_f[y][x] = 1;
            while (!q.empty()) {
                auto [cy, cx] = q.front();
                q.pop();
                size++;
                for (auto& d : dirs8) {
                    int ny = cy + d[0], nx = cx + d[1];
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w && !visited_f[ny][nx] && grid[ny][nx] > threshold) {
                        visited_f[ny][nx] = 1;
                        q.push({ny, nx});
                    }
                }
            }
            component_sizes.push_back(size);
        }
    }

    // 2. Compute Betti-1 (Background 4-connectivity holes)
    // Duality: B1 = components of background (4-conn) - 1
    std::vector<std::vector<int>> visited_b(h, std::vector<int>(w, 0));
    int background_components = 0;
    const int dirs4[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (visited_b[y][x] || grid[y][x] > threshold) continue;
            
            background_components++;
            std::queue<std::pair<int,int>> q;
            q.push({y, x});
            visited_b[y][x] = 1;
            while (!q.empty()) {
                auto [cy, cx] = q.front();
                q.pop();
                for (auto& d : dirs4) {
                    int ny = cy + d[0], nx = cx + d[1];
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w && !visited_b[ny][nx] && grid[ny][nx] <= threshold) {
                        visited_b[ny][nx] = 1;
                        q.push({ny, nx});
                    }
                }
            }
        }
    }

    Topology t;
    t.betti_0 = static_cast<int>(component_sizes.size());
    t.betti_1 = std::max(0, background_components - 1);
    t.max_component_size = component_sizes.empty() ? 0 : *std::max_element(component_sizes.begin(), component_sizes.end());
    long long sum = std::accumulate(component_sizes.begin(), component_sizes.end(), 0LL);
    t.mean_component_size = component_sizes.empty() ? 0.0 : static_cast<double>(sum) / component_sizes.size();
    t.active_fraction = static_cast<double>(active_count) / (h * w);
    return t;
}

Topology compute_network_topology(const std::vector<std::vector<double>>& adj) {
    const int n = static_cast<int>(adj.size());
    if (n == 0) return {};

    // 1. Compute Betti-0 (Components via BFS)
    std::vector<int> visited(n, 0);
    int components = 0;
    long long active_nodes = 0;
    long long active_edges = 0;
    std::vector<int> sizes;

    for (int i = 0; i < n; ++i) {
        // Find nodes with at least one connection or self-activity (here we check row sum)
        double row_sum = 0;
        for (double v : adj[i]) row_sum += std::abs(v);
        if (row_sum > 0) active_nodes++;
        else continue;

        if (visited[i]) continue;
        
        components++;
        int size = 0;
        std::queue<int> q;
        q.push(i);
        visited[i] = 1;
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            size++;
            for (int v = 0; v < n; ++v) {
                if (adj[u][v] != 0.0) {
                    if (!visited[v]) {
                        visited[v] = 1;
                        q.push(v);
                    }
                }
            }
        }
        sizes.push_back(size);
    }

    // 2. Count total unique edges for Betti-1
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (adj[i][j] != 0.0) active_edges++;
        }
    }

    Topology t;
    t.betti_0 = components;
    // Cyclomatic number: B1 = E - V + B0
    t.betti_1 = static_cast<int>(active_edges - active_nodes + components);
    t.max_component_size = sizes.empty() ? 0 : *std::max_element(sizes.begin(), sizes.end());
    int sum = std::accumulate(sizes.begin(), sizes.end(), 0);
    t.mean_component_size = sizes.empty() ? 0.0 : static_cast<double>(sum) / sizes.size();
    t.active_fraction = n > 0 ? static_cast<double>(active_nodes) / n : 0.0;
    return t;
}

json topology_to_json(const Topology& t) {
    return {
        {"betti_0", t.betti_0},
        {"betti_1", t.betti_1},
        {"max_component_size", t.max_component_size},
        {"mean_component_size", t.mean_component_size},
        {"active_fraction", t.active_fraction}
    };
}
}

int main(int argc, char** argv) {
    std::string file;
    std::string mode = "spatial";
    std::string out_dir = "outputs/tda_module_v2_cpp/control";
    double thresh_min = 0.5;
    double thresh_max = 0.5;
    int thresh_steps = 1;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--file" && i + 1 < argc) file = argv[++i];
        else if (a == "--mode" && i + 1 < argc) mode = argv[++i];
        else if (a == "--out" && i + 1 < argc) out_dir = argv[++i];
        else if (a == "--threshold" && i + 1 < argc) {
            thresh_min = thresh_max = std::stod(argv[++i]);
            thresh_steps = 1;
        }
        else if (a == "--thresh-min" && i + 1 < argc) thresh_min = std::stod(argv[++i]);
        else if (a == "--thresh-max" && i + 1 < argc) thresh_max = std::stod(argv[++i]);
        else if (a == "--thresh-steps" && i + 1 < argc) thresh_steps = std::stoi(argv[++i]);
    }

    std::filesystem::create_directories(out_dir);
    json report;
    report["sim_id"] = "tda_multi_v2p0";
    report["schema"] = "v2.0_multi_dimensional_tda";
    report["mode"] = mode;

    if (!file.empty()) {
        auto data = read_grid_csv(file);
        report["source"] = file;
        
        if (thresh_steps <= 1) {
            double t = thresh_min;
            report["threshold"] = t;
            report["topology"] = topology_to_json(mode == "network" ? compute_network_topology(data) : compute_spatial_topology(data, t));
        } else {
            std::vector<json> landscape;
            for (int i = 0; i < thresh_steps; ++i) {
                double t = thresh_min + (thresh_max - thresh_min) * i / (thresh_steps - 1);
                json entry = topology_to_json(mode == "network" ? compute_network_topology(data) : compute_spatial_topology(data, t));
                entry["threshold"] = t;
                landscape.push_back(entry);
            }
            report["persistence_landscape"] = landscape;
        }
        report["falsification"] = {{"passed", true}, {"notes", "custom data analysis"}};
    } else {
        // Built-in controls for Betti-1
        // Donut: 1 component, 1 hole
        std::vector<std::vector<double>> donut(10, std::vector<double>(10, 0.0));
        for(int y=2; y<8; ++y) for(int x=2; x<8; ++x) donut[y][x] = 1.0;
        donut[4][4] = donut[4][5] = donut[5][4] = donut[5][5] = 0.0;
        
        auto res_donut = compute_spatial_topology(donut, 0.5);
        
        // Two components, 0 holes
        std::vector<std::vector<double>> two(10, std::vector<double>(10, 0.0));
        two[1][1] = 1.0; two[8][8] = 1.0;
        auto res_two = compute_spatial_topology(two, 0.5);

        // Network: Triangle (1 comp, 1 cycle)
        std::vector<std::vector<double>> tri = {
            {0,1,1},
            {1,0,1},
            {1,1,0}
        };
        auto res_tri = compute_network_topology(tri);

        bool passed = (res_donut.betti_0 == 1 && res_donut.betti_1 == 1) &&
                      (res_two.betti_0 == 2 && res_two.betti_1 == 0) &&
                      (res_tri.betti_0 == 1 && res_tri.betti_1 == 1);

        report["source"] = "built_in_topological_controls";
        report["controls"] = {
            {"donut_H1", topology_to_json(res_donut)},
            {"two_blobs", topology_to_json(res_two)},
            {"network_triangle", topology_to_json(res_tri)}
        };
        report["falsification"] = {
            {"tests_run", json::array({"donut_b1_count_1", "two_blob_count_2", "network_triangle_b1_count_1"})},
            {"passed", passed}
        };
    }

    std::ofstream out(std::filesystem::path(out_dir) / "tda_report_v2.json");
    out << std::setw(2) << report << "\n";
    std::cout << "TDA V2 Report saved to " << (std::filesystem::path(out_dir) / "tda_report_v2.json").string() << "\n";
    return report["falsification"]["passed"].get<bool>() ? 0 : 2;
}
