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
    int count = 0;
    int max_size = 0;
    double mean_size = 0.0;
    double active_fraction = 0.0;
};

std::vector<std::vector<double>> read_grid_csv(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("could not open grid CSV");
    std::vector<std::vector<double>> grid;
    std::string line;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::string cell;
        std::vector<double> row;
        while (std::getline(ss, cell, ',')) row.push_back(std::stod(cell));
        if (!row.empty()) grid.push_back(row);
    }
    return grid;
}

Topology compute_topology(const std::vector<std::vector<double>>& grid, double threshold) {
    const int h = static_cast<int>(grid.size());
    const int w = h > 0 ? static_cast<int>(grid[0].size()) : 0;
    std::vector<std::vector<int>> visited(h, std::vector<int>(w, 0));
    int active = 0;
    std::vector<int> sizes;
    const int dirs[8][2] = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (grid[y][x] > threshold) active++;
            if (visited[y][x] || grid[y][x] <= threshold) continue;
            int size = 0;
            std::queue<std::pair<int,int>> q;
            q.push({y, x});
            visited[y][x] = 1;
            while (!q.empty()) {
                auto [cy, cx] = q.front();
                q.pop();
                size++;
                for (auto& d : dirs) {
                    int ny = cy + d[0], nx = cx + d[1];
                    if (ny < 0 || ny >= h || nx < 0 || nx >= w) continue;
                    if (!visited[ny][nx] && grid[ny][nx] > threshold) {
                        visited[ny][nx] = 1;
                        q.push({ny, nx});
                    }
                }
            }
            sizes.push_back(size);
        }
    }
    Topology t;
    t.count = static_cast<int>(sizes.size());
    t.max_size = sizes.empty() ? 0 : *std::max_element(sizes.begin(), sizes.end());
    int sum = std::accumulate(sizes.begin(), sizes.end(), 0);
    t.mean_size = sizes.empty() ? 0.0 : static_cast<double>(sum) / static_cast<double>(sizes.size());
    t.active_fraction = (h * w) > 0 ? static_cast<double>(active) / static_cast<double>(h * w) : 0.0;
    return t;
}

Topology compute_network_topology(const std::vector<std::vector<double>>& adj) {
    const int n = static_cast<int>(adj.size());
    std::vector<int> visited(n, 0);
    std::vector<int> sizes;
    for (int i = 0; i < n; ++i) {
        if (visited[i]) continue;
        int size = 0;
        std::queue<int> q;
        q.push(i);
        visited[i] = 1;
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            size++;
            for (int v = 0; v < n; ++v) {
                if (!visited[v] && v < static_cast<int>(adj[u].size()) && adj[u][v] != 0.0) {
                    visited[v] = 1;
                    q.push(v);
                }
            }
        }
        sizes.push_back(size);
    }
    Topology t;
    t.count = static_cast<int>(sizes.size());
    t.max_size = sizes.empty() ? 0 : *std::max_element(sizes.begin(), sizes.end());
    int sum = std::accumulate(sizes.begin(), sizes.end(), 0);
    t.mean_size = sizes.empty() ? 0.0 : static_cast<double>(sum) / static_cast<double>(sizes.size());
    t.active_fraction = 0.0;
    return t;
}

json to_json(const Topology& t) {
    return {{"count", t.count}, {"max_size", t.max_size}, {"mean_size", t.mean_size}, {"active_fraction", t.active_fraction}};
}
}

int main(int argc, char** argv) {
    std::string file;
    std::string mode = "spatial";
    std::string out_dir = "outputs/tda_module_v1_cpp/control";
    double threshold = 0.5;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--file" && i + 1 < argc) file = argv[++i];
        else if (a == "--mode" && i + 1 < argc) mode = argv[++i];
        else if (a == "--out" && i + 1 < argc) out_dir = argv[++i];
        else if (a == "--threshold" && i + 1 < argc) threshold = std::stod(argv[++i]);
    }

    std::filesystem::create_directories(out_dir);
    json report;
    report["sim_id"] = "tda_betti0_v2p3";
    report["schema"] = "v2.3_recoverable_report";
    report["mode"] = mode;
    report["threshold"] = threshold;

    if (!file.empty()) {
        auto grid = read_grid_csv(file);
        report["source"] = file;
        report["topology"] = to_json(mode == "network" ? compute_network_topology(grid) : compute_topology(grid, threshold));
        report["falsification"] = {{"tests_run", json::array()}, {"passed", true}, {"notes", "custom grid analysis"}};
    } else {
        std::vector<std::vector<double>> empty(8, std::vector<double>(8, 0.0));
        std::vector<std::vector<double>> one(8, std::vector<double>(8, 0.0));
        for (int y = 2; y < 6; ++y) for (int x = 2; x < 6; ++x) one[y][x] = 1.0;
        std::vector<std::vector<double>> two(8, std::vector<double>(8, 0.0));
        two[1][1] = two[1][2] = two[2][1] = 1.0;
        two[6][6] = two[6][5] = two[5][6] = 1.0;
        auto e = compute_topology(empty, threshold);
        auto o = compute_topology(one, threshold);
        auto tw = compute_topology(two, threshold);
        std::vector<std::vector<double>> adj = {
            {0,1,0,0},
            {1,0,0,0},
            {0,0,0,1},
            {0,0,1,0}
        };
        auto net = compute_network_topology(adj);
        bool passed = e.count == 0 && o.count == 1 && tw.count == 2 && net.count == 2;
        report["source"] = "built_in_component_controls";
        report["controls"] = {{"empty", to_json(e)}, {"single_component", to_json(o)}, {"two_components", to_json(tw)}, {"network_two_components", to_json(net)}};
        report["falsification"] = {
            {"tests_run", json::array({"empty_mask_count_0", "single_blob_count_1", "two_blob_count_2", "network_two_component_count_2"})},
            {"passed", passed}
        };
    }

    std::ofstream out(std::filesystem::path(out_dir) / "topology_report.json");
    out << std::setw(2) << report << "\n";
    std::cout << "Report saved to " << (std::filesystem::path(out_dir) / "topology_report.json").string() << "\n";
    return report["falsification"]["passed"].get<bool>() ? 0 : 2;
}
