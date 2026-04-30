# Project Rectification Plan

## 1. Objectives

- Reorganize the repository into a clean, governed structure.
- Preserve all evidence and provenance.
- Standardize paths for docs, tools, configs, and outputs.

## 2. Proposed Layout

```
docs/          - reports, theory, and governance
tools/         - simulator engines (to be moved in Phase 2)
configs/       - multi-runs, canonical, examples
registry/      - manifests and indexes
outputs/runs/  - experiment results
outputs/audits/ - audit results and gap matrices
```

## 3. Move Summary

| Old Path | New Path | Reason |
| --- | --- | --- |
| `C4_STATUS_PLAN_2026-04-29.md` | `docs/theory/C4_STATUS_PLAN_2026-04-29.md` | centralize_theory_and_reports |
| `CPLUSPLUS_PORTING_STATUS_2026-04-29.md` | `docs/theory/CPLUSPLUS_PORTING_STATUS_2026-04-29.md` | centralize_theory_and_reports |
| `directory listing.txt` | `docs/theory/directory listing.txt` | centralize_theory_and_reports |
| `ECOSYSTEM_UPGRADE_REPORT_2026-04-25.md` | `docs/theory/ECOSYSTEM_UPGRADE_REPORT_2026-04-25.md` | centralize_theory_and_reports |
| `gemini.md` | `docs/theory/gemini.md` | centralize_theory_and_reports |
| `HANDOFF_UPGRADE_REPORT_2026-04-25.md` | `docs/theory/HANDOFF_UPGRADE_REPORT_2026-04-25.md` | centralize_theory_and_reports |
| `linear_particle_accelerator_simulation_report.md` | `docs/theory/linear_particle_accelerator_simulation_report.md` | centralize_theory_and_reports |
| `PROJECT_METHODS_PURPOSE_REASONING_REPORT_2026-04-25.md` | `docs/theory/PROJECT_METHODS_PURPOSE_REASONING_REPORT_2026-04-25.md` | centralize_theory_and_reports |
| `questions.txt` | `docs/theory/questions.txt` | centralize_theory_and_reports |
| `report2_6d_accelerator_simulators.md` | `docs/theory/report2_6d_accelerator_simulators.md` | centralize_theory_and_reports |
| `ROOT_DIRECTORY_LAYOUT.md` | `docs/theory/ROOT_DIRECTORY_LAYOUT.md` | centralize_theory_and_reports |
| `TOOL_SCIENTIFIC_PRECISION_REPORT_2026-04-25.md` | `docs/theory/TOOL_SCIENTIFIC_PRECISION_REPORT_2026-04-25.md` | centralize_theory_and_reports |
| `TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-29.md` | `docs/reports/TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-29.md` | centralize_rigor_reports |
| `TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-30.md` | `docs/reports/TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-30.md` | centralize_rigor_reports |
| `Zero_Is_Not_Absence_Technical_Paper.md` | `docs/theory/Zero_Is_Not_Absence_Technical_Paper.md` | centralize_theory_and_reports |
| `accelerator_sim_v1\README.md` | `docs/theory/accelerator_sim_v1\README.md` | centralize_theory_and_reports |
| `accelerator_sim_v1_cpp\README.md` | `docs/theory/accelerator_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `agent_based_sim_v1\README.md` | `docs/theory/agent_based_sim_v1\README.md` | centralize_theory_and_reports |
| `agent_based_sim_v1_cpp\README.md` | `docs/theory/agent_based_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `bifurcation_analyzer_v1\README.md` | `docs/theory/bifurcation_analyzer_v1\README.md` | centralize_theory_and_reports |
| `bifurcation_analyzer_v1_cpp\README.md` | `docs/theory/bifurcation_analyzer_v1_cpp\README.md` | centralize_theory_and_reports |
| `ca_admissibility_sim_v1\README.md` | `docs/theory/ca_admissibility_sim_v1\README.md` | centralize_theory_and_reports |
| `ca_admissibility_sim_v1_cpp\README.md` | `docs/theory/ca_admissibility_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `circular_accelerator_sim_v1\README.md` | `docs/theory/circular_accelerator_sim_v1\README.md` | centralize_theory_and_reports |
| `circular_accelerator_sim_v1_cpp\README.md` | `docs/theory/circular_accelerator_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `continuation_and_constraint_integrated_charter_v2_3\Stability_and_Regime_Transitions_Report.md` | `docs/theory/continuation_and_constraint_integrated_charter_v2_3\Stability_and_Regime_Transitions_Report.md` | centralize_theory_and_reports |
| `dase_analog_sim_cpp\README.md` | `docs/theory/dase_analog_sim_cpp\README.md` | centralize_theory_and_reports |
| `falsification_suite_v1\README.md` | `docs/theory/falsification_suite_v1\README.md` | centralize_theory_and_reports |
| `falsification_suite_v1_cpp\README.md` | `docs/theory/falsification_suite_v1_cpp\README.md` | centralize_theory_and_reports |
| `fsa_rule_engine_sim_v1\README.md` | `docs/theory/fsa_rule_engine_sim_v1\README.md` | centralize_theory_and_reports |
| `fsa_rule_engine_sim_v1_cpp\README.md` | `docs/theory/fsa_rule_engine_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `graph_dynamics_sim_v1\README.md` | `docs/theory/graph_dynamics_sim_v1\README.md` | centralize_theory_and_reports |
| `graph_dynamics_sim_v1_cpp\README.md` | `docs/theory/graph_dynamics_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `holding\lexicon\lexicon_human_readable.md` | `docs/theory/holding\lexicon\lexicon_human_readable.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\CMakeLists.txt` | `docs/theory/holding\runtime_r2b\CMakeLists.txt` | centralize_theory_and_reports |
| `holding\runtime_r2b\README.md` | `docs/theory/holding\runtime_r2b\README.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\build\cmake\CMakeCache.txt` | `docs/theory/holding\runtime_r2b\build\cmake\CMakeCache.txt` | centralize_theory_and_reports |
| `holding\runtime_r2b\build\cmake\CMakeFiles\TargetDirectories.txt` | `docs/theory/holding\runtime_r2b\build\cmake\CMakeFiles\TargetDirectories.txt` | centralize_theory_and_reports |
| `holding\runtime_r2b\build\cmake\CMakeFiles\4.2.0-rc2\VCTargetsPath.txt` | `docs/theory/holding\runtime_r2b\build\cmake\CMakeFiles\4.2.0-rc2\VCTargetsPath.txt` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_assessment_and_plan_v1.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_assessment_and_plan_v1.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_bootstrap_and_causality_report_v1.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_bootstrap_and_causality_report_v1.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_freeze_report_v1.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_freeze_report_v1.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_onset_and_observables_report_v4.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_onset_and_observables_report_v4.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_phase_status.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_phase_status.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_terminal_law_report_v2.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_terminal_law_report_v2.md` | centralize_theory_and_reports |
| `holding\runtime_r2b\reports\runtime_r2b_terminal_law_report_v3.md` | `docs/theory/holding\runtime_r2b\reports\runtime_r2b_terminal_law_report_v3.md` | centralize_theory_and_reports |
| `holding\sim\README.md` | `docs/theory/holding\sim\README.md` | centralize_theory_and_reports |
| `holding\sim\configs\README.md` | `docs/theory/holding\sim\configs\README.md` | centralize_theory_and_reports |
| `holding\sim\output_schema\README.md` | `docs/theory/holding\sim\output_schema\README.md` | centralize_theory_and_reports |
| `holding\sim\scripts\README.md` | `docs/theory/holding\sim\scripts\README.md` | centralize_theory_and_reports |
| `holding\sim\sweeps\README.md` | `docs/theory/holding\sim\sweeps\README.md` | centralize_theory_and_reports |
| `holding\software\README.md` | `docs/theory/holding\software\README.md` | centralize_theory_and_reports |
| `holding\software\src\analyze_level2_results.txt` | `docs/theory/holding\software\src\analyze_level2_results.txt` | centralize_theory_and_reports |
| `holding\software\src\cpp_simulation_backend_notes.md` | `docs/theory/holding\software\src\cpp_simulation_backend_notes.md` | centralize_theory_and_reports |
| `holding\software\src\SIM14_STAGING_NOTES.md` | `docs/theory/holding\software\src\SIM14_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\software\src\SIM15_STAGING_NOTES.md` | `docs/theory/holding\software\src\SIM15_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\software\src\SIM16_STAGING_NOTES.md` | `docs/theory/holding\software\src\SIM16_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\software\src\SIM17_STAGING_NOTES.md` | `docs/theory/holding\software\src\SIM17_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\software\src\spec.txt` | `docs/theory/holding\software\src\spec.txt` | centralize_theory_and_reports |
| `holding\src\analyze_level2_results.txt` | `docs/theory/holding\src\analyze_level2_results.txt` | centralize_theory_and_reports |
| `holding\src\cpp_simulation_backend_notes.md` | `docs/theory/holding\src\cpp_simulation_backend_notes.md` | centralize_theory_and_reports |
| `holding\src\SIM14_STAGING_NOTES.md` | `docs/theory/holding\src\SIM14_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\src\SIM15_STAGING_NOTES.md` | `docs/theory/holding\src\SIM15_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\src\SIM16_STAGING_NOTES.md` | `docs/theory/holding\src\SIM16_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\src\SIM17_STAGING_NOTES.md` | `docs/theory/holding\src\SIM17_STAGING_NOTES.md` | centralize_theory_and_reports |
| `holding\src\spec.txt` | `docs/theory/holding\src\spec.txt` | centralize_theory_and_reports |
| `info_metrics_module_v1\README.md` | `docs/theory/info_metrics_module_v1\README.md` | centralize_theory_and_reports |
| `info_metrics_module_v1_cpp\README.md` | `docs/theory/info_metrics_module_v1_cpp\README.md` | centralize_theory_and_reports |
| `Internal_Sustainability_of_the_NOT_Axiom\Internal_Sustainability_of_the_NOT_Axiom.md` | `docs/theory/Internal_Sustainability_of_the_NOT_Axiom\Internal_Sustainability_of_the_NOT_Axiom.md` | centralize_theory_and_reports |
| `kuramoto_sim_v1\README.md` | `docs/theory/kuramoto_sim_v1\README.md` | centralize_theory_and_reports |
| `kuramoto_sim_v1_cpp\README.md` | `docs/theory/kuramoto_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `lb_fluid_sim_v1\README.md` | `docs/theory/lb_fluid_sim_v1\README.md` | centralize_theory_and_reports |
| `lb_fluid_sim_v1_cpp\README.md` | `docs/theory/lb_fluid_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `linac_sim_cpp\README.md` | `docs/theory/linac_sim_cpp\README.md` | centralize_theory_and_reports |
| `mc_ensemble_sim_v1\README.md` | `docs/theory/mc_ensemble_sim_v1\README.md` | centralize_theory_and_reports |
| `mc_ensemble_sim_v1_cpp\README.md` | `docs/theory/mc_ensemble_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `parameter_optimizer_v1\README.md` | `docs/theory/parameter_optimizer_v1\README.md` | centralize_theory_and_reports |
| `parameter_optimizer_v1_cpp\README.md` | `docs/theory/parameter_optimizer_v1_cpp\README.md` | centralize_theory_and_reports |
| `rd_moving_boundary_sim_v1\README.md` | `docs/theory/rd_moving_boundary_sim_v1\README.md` | centralize_theory_and_reports |
| `rd_sim_cpp\README.md` | `docs/theory/rd_sim_cpp\README.md` | centralize_theory_and_reports |
| `Regime_Transitions_and_Identity_Stabilization\Regime_Transitions_and_Identity_Stabilization.md` | `docs/theory/Regime_Transitions_and_Identity_Stabilization\Regime_Transitions_and_Identity_Stabilization.md` | centralize_theory_and_reports |
| `research_density_stability\density_stability_report.md` | `docs/theory/research_density_stability\density_stability_report.md` | centralize_theory_and_reports |
| `research_density_stability\hypothesis.txt` | `docs/theory/research_density_stability\hypothesis.txt` | centralize_theory_and_reports |
| `research_epsilon_identity_v1\hypothesis.txt` | `docs/theory/research_epsilon_identity_v1\hypothesis.txt` | centralize_theory_and_reports |
| `research_epsilon_identity_v1\Technical_Paper_Identity_Mismatch.md` | `docs/theory/research_epsilon_identity_v1\Technical_Paper_Identity_Mismatch.md` | centralize_theory_and_reports |
| `research_residue_hysteresis\hypothesis.txt` | `docs/theory/research_residue_hysteresis\hypothesis.txt` | centralize_theory_and_reports |
| `research_residue_hysteresis\residue_hysteresis_report.md` | `docs/theory/research_residue_hysteresis\residue_hysteresis_report.md` | centralize_theory_and_reports |
| `satp_higgs_sim_cpp\README.md` | `docs/theory/satp_higgs_sim_cpp\README.md` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\CMakeLists.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\CMakeLists.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\ENGINE_INDEX.md` | `docs/theory/Simulation_engines_extracted_2026-04-25\ENGINE_INDEX.md` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\UHD770_UPDATE_STATUS_2026-04-29.md` | `docs/theory/Simulation_engines_extracted_2026-04-25\UHD770_UPDATE_STATUS_2026-04-29.md` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\build_cli\CMakeCache.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\build_cli\CMakeCache.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\build_cli\CMakeFiles\TargetDirectories.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\build_cli\CMakeFiles\TargetDirectories.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\build_cli\CMakeFiles\4.2.0-rc2\VCTargetsPath.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\build_cli\CMakeFiles\4.2.0-rc2\VCTargetsPath.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\build_uhd770\CMakeCache.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\build_uhd770\CMakeCache.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\build_uhd770\CMakeFiles\TargetDirectories.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\build_uhd770\CMakeFiles\TargetDirectories.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\dase_cli\QUICKSTART.txt` | `docs/theory/Simulation_engines_extracted_2026-04-25\dase_cli\QUICKSTART.txt` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\dase_cli\README_EXTRACTED.md` | `docs/theory/Simulation_engines_extracted_2026-04-25\dase_cli\README_EXTRACTED.md` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\dase_cli\TEST_ANALYSIS_COMMANDS.md` | `docs/theory/Simulation_engines_extracted_2026-04-25\dase_cli\TEST_ANALYSIS_COMMANDS.md` | centralize_theory_and_reports |
| `Simulation_engines_extracted_2026-04-25\dase_cli\VALIDATION_REPORT.md` | `docs/theory/Simulation_engines_extracted_2026-04-25\dase_cli\VALIDATION_REPORT.md` | centralize_theory_and_reports |
| `spectral_analysis_v1\README.md` | `docs/theory/spectral_analysis_v1\README.md` | centralize_theory_and_reports |
| `spectral_analysis_v1_cpp\README.md` | `docs/theory/spectral_analysis_v1_cpp\README.md` | centralize_theory_and_reports |
| `stochastic_sim_cpp\README.md` | `docs/theory/stochastic_sim_cpp\README.md` | centralize_theory_and_reports |
| `stochastic_sim_v1\README.md` | `docs/theory/stochastic_sim_v1\README.md` | centralize_theory_and_reports |
| `structural_box_sim_cpp\README.md` | `docs/theory/structural_box_sim_cpp\README.md` | centralize_theory_and_reports |
| `structural_box_sim_v2\README.md` | `docs/theory/structural_box_sim_v2\README.md` | centralize_theory_and_reports |
| `symplectic_sim_v1\README.md` | `docs/theory/symplectic_sim_v1\README.md` | centralize_theory_and_reports |
| `symplectic_sim_v1_cpp\README.md` | `docs/theory/symplectic_sim_v1_cpp\README.md` | centralize_theory_and_reports |
| `tda_module_v1\README.md` | `docs/theory/tda_module_v1\README.md` | centralize_theory_and_reports |
| `tda_module_v1_cpp\README.md` | `docs/theory/tda_module_v1_cpp\README.md` | centralize_theory_and_reports |
| `theory\Formal Math Treatment_Admissibility Window.txt` | `docs/theory/theory\Formal Math Treatment_Admissibility Window.txt` | centralize_theory_and_reports |
| `theory\Recoupling Theory.txt` | `docs/theory/theory\Recoupling Theory.txt` | centralize_theory_and_reports |
| `theory\Residue-Sustained Admissibility.txt` | `docs/theory/theory\Residue-Sustained Admissibility.txt` | centralize_theory_and_reports |
| `theory\THE LAW OF THE ONE PROCESS.txt` | `docs/theory/theory\THE LAW OF THE ONE PROCESS.txt` | centralize_theory_and_reports |
| `theory\Why Zero Is Not Absence.txt` | `docs/theory/theory\Why Zero Is Not Absence.txt` | centralize_theory_and_reports |
| `theory\lexicon\lexicon_human_readable.md` | `docs/theory/theory\lexicon\lexicon_human_readable.md` | centralize_theory_and_reports |
| `theory\master\note.txt` | `docs/theory/theory\master\note.txt` | centralize_theory_and_reports |
| `theory\master\research_dual_laws_v1\formal_treatment_cdhds.md` | `docs/theory/theory\master\research_dual_laws_v1\formal_treatment_cdhds.md` | centralize_theory_and_reports |
| `utilities\lexicon_resolve.md` | `docs/theory/utilities\lexicon_resolve.md` | centralize_theory_and_reports |
| `utilities\run_many.md` | `docs/theory/utilities\run_many.md` | centralize_theory_and_reports |
| `utilities\summarize_runs.md` | `docs/theory/utilities\summarize_runs.md` | centralize_theory_and_reports |
| `NARRATIVE.md` | `docs/governance/NARRATIVE.md` | normalize_onboarding |
| `AGENTS.md` | `docs/governance/AGENTS.md` | normalize_onboarding |
| `PROJECT_DOCUMENTATION.txt` | `docs/governance/PROJECT_DOCUMENTATION.txt` | normalize_onboarding |
| `linear_particle_accelerator_simulation_report.md` | `outputs/audits/linear_particle_accelerator_simulation_report.md` | move_loose_reports_to_audits |
| `outputs\analysis` | `outputs\runs\analysis` | centralize_run_outputs |
| `outputs\c4_elevation_audit_2026-04-30` | `outputs\runs\c4_elevation_audit_2026-04-30` | centralize_run_outputs |
| `outputs\c4_phase2_smoke_all` | `outputs\runs\c4_phase2_smoke_all` | centralize_run_outputs |
| `outputs\c4_phase3_uq_all` | `outputs\runs\c4_phase3_uq_all` | centralize_run_outputs |
| `outputs\c4_phase4_falsification` | `outputs\runs\c4_phase4_falsification` | centralize_run_outputs |
| `outputs\configs_generated` | `outputs\runs\configs_generated` | centralize_run_outputs |
| `outputs\convergence_phase5_stochastic_dt` | `outputs\runs\convergence_phase5_stochastic_dt` | centralize_run_outputs |
| `outputs\convergence_phase5_symplectic_dt` | `outputs\runs\convergence_phase5_symplectic_dt` | centralize_run_outputs |
| `outputs\convergence_phase5_symplectic_dt_v3` | `outputs\runs\convergence_phase5_symplectic_dt_v3` | centralize_run_outputs |
| `outputs\cpp_smoke` | `outputs\runs\cpp_smoke` | centralize_run_outputs |
| `outputs\default_run` | `outputs\runs\default_run` | centralize_run_outputs |
| `outputs\example_residue_validation` | `outputs\runs\example_residue_validation` | centralize_run_outputs |
| `outputs\full_cpp_validation` | `outputs\runs\full_cpp_validation` | centralize_run_outputs |
| `outputs\lexicon_validation_program_2026-04-25` | `outputs\runs\lexicon_validation_program_2026-04-25` | centralize_run_outputs |
| `outputs\linac_sim_cpp` | `outputs\runs\linac_sim_cpp` | centralize_run_outputs |
| `outputs\mc_ensemble_sim_v1_cpp` | `outputs\runs\mc_ensemble_sim_v1_cpp` | centralize_run_outputs |
| `outputs\parameter_optimizer_v1_cpp` | `outputs\runs\parameter_optimizer_v1_cpp` | centralize_run_outputs |
| `outputs\rd_sim_cpp` | `outputs\runs\rd_sim_cpp` | centralize_run_outputs |
| `outputs\regression_final_dase_analog` | `outputs\runs\regression_final_dase_analog` | centralize_run_outputs |
| `outputs\regression_final_dase_analog_v2` | `outputs\runs\regression_final_dase_analog_v2` | centralize_run_outputs |
| `outputs\regression_phase6_analog` | `outputs\runs\regression_phase6_analog` | centralize_run_outputs |
| `outputs\regression_phase6_symplectic` | `outputs\runs\regression_phase6_symplectic` | centralize_run_outputs |
| `outputs\research_dual_laws_cdhds_v1_2026-04-25` | `outputs\runs\research_dual_laws_cdhds_v1_2026-04-25` | centralize_run_outputs |
| `outputs\research_recoupling_rt1_2026-04-25` | `outputs\runs\research_recoupling_rt1_2026-04-25` | centralize_run_outputs |
| `outputs\research_residue_necessity_2026-04-25` | `outputs\runs\research_residue_necessity_2026-04-25` | centralize_run_outputs |
| `outputs\spectral_analysis_v1_cpp` | `outputs\runs\spectral_analysis_v1_cpp` | centralize_run_outputs |
| `outputs\stochastic_sim_cpp` | `outputs\runs\stochastic_sim_cpp` | centralize_run_outputs |
| `outputs\structural_box_sim_cpp` | `outputs\runs\structural_box_sim_cpp` | centralize_run_outputs |
| `outputs\symplectic_sim_v1_cpp` | `outputs\runs\symplectic_sim_v1_cpp` | centralize_run_outputs |
| `outputs\tda_module_v1_cpp` | `outputs\runs\tda_module_v1_cpp` | centralize_run_outputs |
| `outputs\_tmp_batch_runner_smoke` | `outputs\runs\_tmp_batch_runner_smoke` | centralize_run_outputs |
| `outputs\_tmp_batch_runner_smoke2` | `outputs\runs\_tmp_batch_runner_smoke2` | centralize_run_outputs |
| `outputs\_tmp_ca_seed_check` | `outputs\runs\_tmp_ca_seed_check` | centralize_run_outputs |
| `outputs\_tmp_falsification_core_after_ca_fix` | `outputs\runs\_tmp_falsification_core_after_ca_fix` | centralize_run_outputs |
| `outputs\_tmp_falsification_core_pathfix` | `outputs\runs\_tmp_falsification_core_pathfix` | centralize_run_outputs |
| `tool_manifest.json` | `registry/tool_manifest.json` | centralize_registry |
| `cross_verification_protocol.json` | `registry/cross_verification_protocol.json` | centralize_registry |
| `lexicon.json` | `registry/lexicon.json` | centralize_registry |
| `lexicon_validation_registry.json` | `registry/lexicon_validation_registry.json` | centralize_registry |
