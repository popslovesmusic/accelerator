#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <fstream>
#include <iomanip>
#include <random>
#include <algorithm>
#include <numeric>

using namespace std;

struct SummaryData {
    float mean_D = 0.0f;
    float mean_delta_alpha = 0.0f;
    float mean_organization_score = 0.0f;
};

int main(int argc, char* argv[]) {
    int cycles = 1000;
    int runs = 100;
    string out_csv = "results/vortex_cpp_equivalence/vortex_cpp_results.csv";
    string out_json = "results/vortex_cpp_equivalence/vortex_cpp_results.json";

    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--cycles" && i + 1 < argc) cycles = stoi(argv[++i]);
        if (arg == "--runs" && i + 1 < argc) runs = stoi(argv[++i]);
        if (arg == "--out-csv" && i + 1 < argc) out_csv = argv[++i];
        if (arg == "--out-json" && i + 1 < argc) out_json = argv[++i];
    }

    vector<string> comparison_modes = {"no_bar", "collapse_bar", "random_bar", "valid_bar"};
    int dim = 10;

    // We need to track the full trajectory for generating plots
    // metrics[mode][run][cycle]
    struct MetricSeries {
        vector<vector<float>> D;
        vector<vector<float>> delta_alpha;
        vector<vector<float>> organization_score;
    };

    vector<MetricSeries> metrics_by_mode(comparison_modes.size());
    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        metrics_by_mode[m].D.assign(runs, vector<float>(cycles, 0.0f));
        metrics_by_mode[m].delta_alpha.assign(runs, vector<float>(cycles, 0.0f));
        metrics_by_mode[m].organization_score.assign(runs, vector<float>(cycles, 0.0f));
    }

    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        string mode = comparison_modes[m];
        for (int run = 0; run < runs; ++run) {
            // Seed matching Python run + 42
            mt19937 gen(run + 42);
            normal_distribution<float> d_norm(0.0f, 1.0f);

            vector<float> alpha_base(dim, 1.0f);
            vector<float> alpha = alpha_base;

            for (int cycle = 0; cycle < cycles; ++cycle) {
                vector<float> A(dim);
                for (int d = 0; d < dim; ++d) A[d] = d_norm(gen);

                vector<float> B(dim);
                float D_val = 0.0f;
                vector<float> alpha_next = alpha;
                float org = 0.0f;

                if (mode == "no_bar") {
                    for (int d = 0; d < dim; ++d) B[d] = d_norm(gen);
                    D_val = 0.0f;
                    org = 0.0f;
                }
                else if (mode == "collapse_bar") {
                    B = A;
                    D_val = 0.0f;
                    org = 0.0f;
                }
                else if (mode == "random_bar") {
                    for (int d = 0; d < dim; ++d) B[d] = d_norm(gen);
                    
                    // Compute distinction D = mean(abs(alpha * (A - B)))
                    float sum_dist = 0.0f;
                    for (int d = 0; d < dim; ++d) {
                        sum_dist += abs(alpha[d] * (A[d] - B[d]));
                    }
                    D_val = sum_dist / dim;

                    // Update filter with white noise
                    for (int d = 0; d < dim; ++d) {
                        alpha_next[d] = alpha[d] + 0.02f * d_norm(gen);
                        alpha_next[d] = max(0.1f, min(5.0f, alpha_next[d]));
                    }

                    // Compute random org proxy
                    float sum_noise_abs = 0.0f;
                    for (int d = 0; d < dim; ++d) sum_noise_abs += abs(d_norm(gen));
                    org = (sum_noise_abs / dim) * 0.1f;
                }
                else if (mode == "valid_bar") {
                    // bias_direction = alpha - alpha_base
                    vector<float> bias_direction(dim);
                    for (int d = 0; d < dim; ++d) bias_direction[d] = alpha[d] - alpha_base[d];

                    // B = A + 0.5 * randn + 0.3 * bias_direction
                    for (int d = 0; d < dim; ++d) {
                        B[d] = A[d] + 0.5f * d_norm(gen) + 0.3f * bias_direction[d];
                    }

                    // Compute distinction D
                    float sum_dist = 0.0f;
                    for (int d = 0; d < dim; ++d) {
                        sum_dist += abs(alpha[d] * (A[d] - B[d]));
                    }
                    D_val = sum_dist / dim;

                    // Update delta_alpha with gradient
                    for (int d = 0; d < dim; ++d) {
                        alpha_next[d] = alpha[d] + 0.015f * D_val * (A[d] - B[d]);
                        // Relax toward base
                        alpha_next[d] = alpha_next[d] - 0.005f * (alpha_next[d] - alpha_base[d]);
                        alpha_next[d] = max(0.1f, min(5.0f, alpha_next[d]));
                    }

                    // Compute organization score alignment
                    if (cycle > 0) {
                        float dot_product = 0.0f;
                        float norm_bias = 0.0f;
                        float norm_diff = 0.0f;
                        for (int d = 0; d < dim; ++d) {
                            float diff = A[d] - B[d];
                            dot_product += bias_direction[d] * diff;
                            norm_bias += bias_direction[d] * bias_direction[d];
                            norm_diff += diff * diff;
                        }
                        org = abs(dot_product) / (sqrt(norm_bias) * sqrt(norm_diff) + 1e-8f);
                    } else {
                        org = 0.0f;
                    }
                }

                // Compute delta_alpha: mean(abs(alpha_next - alpha_base))
                float sum_da = 0.0f;
                for (int d = 0; d < dim; ++d) {
                    sum_da += abs(alpha_next[d] - alpha_base[d]);
                }
                float delta_alpha_val = sum_da / dim;

                // Record metrics
                metrics_by_mode[m].D[run][cycle] = D_val;
                metrics_by_mode[m].delta_alpha[run][cycle] = delta_alpha_val;
                metrics_by_mode[m].organization_score[run][cycle] = org;

                // Advance state
                alpha = alpha_next;
            }
        }
    }

    // Calculate means across runs at the final cycle
    vector<SummaryData> summary(comparison_modes.size());
    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        float sum_D = 0.0f;
        float sum_da = 0.0f;
        float sum_org = 0.0f;
        for (int run = 0; run < runs; ++run) {
            sum_D += metrics_by_mode[m].D[run][cycles - 1];
            sum_da += metrics_by_mode[m].delta_alpha[run][cycles - 1];
            sum_org += metrics_by_mode[m].organization_score[run][cycles - 1];
        }
        summary[m].mean_D = sum_D / runs;
        summary[m].mean_delta_alpha = sum_da / runs;
        summary[m].mean_organization_score = sum_org / runs;
    }

    // 1. Output CSV
    ofstream csv_f(out_csv);
    csv_f << "mode,run_id,final_D,final_delta_alpha,final_organization_score\n";
    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        for (int run = 0; run < runs; ++run) {
            csv_f << comparison_modes[m] << "," << run << ","
                  << fixed << setprecision(6)
                  << metrics_by_mode[m].D[run][cycles - 1] << ","
                  << metrics_by_mode[m].delta_alpha[run][cycles - 1] << ","
                  << metrics_by_mode[m].organization_score[run][cycles - 1] << "\n";
        }
    }
    csv_f.close();

    // 2. Output JSON
    ofstream json_f(out_json);
    json_f << "{\n";
    json_f << "  \"campaign_id\": \"MPF_VORTEX_ADMISSIBILITY_CAMPAIGN_001\",\n";
    json_f << "  \"status\": \"EVIDENCE_RECORDED\",\n";
    json_f << "  \"backend\": \"C++\",\n";
    json_f << "  \"summary\": {\n";
    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        json_f << "    \"" << comparison_modes[m] << "\": {\n";
        json_f << "      \"mean_D\": " << summary[m].mean_D << ",\n";
        json_f << "      \"mean_delta_alpha\": " << summary[m].mean_delta_alpha << ",\n";
        json_f << "      \"mean_organization_score\": " << summary[m].mean_organization_score << "\n";
        json_f << "    }" << (m == comparison_modes.size() - 1 ? "" : ",") << "\n";
    }
    json_f << "  },\n";

    // Output cycle trajectories for plotting (we will output averaged trajectories for simplicity)
    json_f << "  \"trajectories\": {\n";
    for (size_t m = 0; m < comparison_modes.size(); ++m) {
        json_f << "    \"" << comparison_modes[m] << "\": {\n";
        
        // Average D over runs per cycle
        json_f << "      \"D\": [";
        for (int c = 0; c < cycles; ++c) {
            float sum_c = 0.0f;
            for (int r = 0; r < runs; ++r) sum_c += metrics_by_mode[m].D[r][c];
            json_f << (c == 0 ? "" : ", ") << (sum_c / runs);
        }
        json_f << "],\n";

        // Average delta_alpha
        json_f << "      \"delta_alpha\": [";
        for (int c = 0; c < cycles; ++c) {
            float sum_c = 0.0f;
            for (int r = 0; r < runs; ++r) sum_c += metrics_by_mode[m].delta_alpha[r][c];
            json_f << (c == 0 ? "" : ", ") << (sum_c / runs);
        }
        json_f << "],\n";

        // Average organization_score
        json_f << "      \"organization_score\": [";
        for (int c = 0; c < cycles; ++c) {
            float sum_c = 0.0f;
            for (int r = 0; r < runs; ++r) sum_c += metrics_by_mode[m].organization_score[r][c];
            json_f << (c == 0 ? "" : ", ") << (sum_c / runs);
        }
        json_f << "]\n";
        json_f << "    }" << (m == comparison_modes.size() - 1 ? "" : ",") << "\n";
    }
    json_f << "  }\n";
    json_f << "}\n";
    json_f.close();

    cout << "Vortex Admissibility C++ Campaign simulation completed successfully." << endl;
    return 0;
}
