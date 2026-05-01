#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "analog_universal_node_engine_avx2.h"

namespace py = pybind11;

PYBIND11_MODULE(dase_engine, m) {
    m.doc() = "DASE Analog Engine AVX2 Python Bindings";

    // ------------------------------------------------------------------------
    //  CPU Feature Access Layer
    // ------------------------------------------------------------------------
    py::class_<CPUFeatures>(m, "CPUFeatures")
        .def(py::init<>())
        .def_static("has_avx2", &CPUFeatures::hasAVX2)
        .def_static("has_fma", &CPUFeatures::hasFMA)
        .def_static("print_capabilities", &CPUFeatures::printCapabilities);

    m.def("cpu_has_avx2", []() { return CPUFeatures::hasAVX2(); });
    m.def("cpu_has_fma", []() { return CPUFeatures::hasFMA(); });
    m.def("cpu_print_capabilities", []() { CPUFeatures::printCapabilities(); });

    // ------------------------------------------------------------------------
    //  Engine Metrics
    // ------------------------------------------------------------------------
    py::class_<EngineMetrics>(m, "EngineMetrics")
        .def(py::init<>())
        .def_readwrite("total_operations", &EngineMetrics::total_operations)
        .def_readwrite("avx2_operations", &EngineMetrics::avx2_operations)
        .def_readwrite("node_processes", &EngineMetrics::node_processes)
        .def_readwrite("harmonic_generations", &EngineMetrics::harmonic_generations)
        .def_readwrite("avg_time_ns", &EngineMetrics::avg_time_ns)
        .def_readwrite("throughput_gflops", &EngineMetrics::throughput_gflops)
        .def_readwrite("current_ns_per_op", &EngineMetrics::current_ns_per_op)
        .def_readwrite("current_ops_per_second", &EngineMetrics::current_ops_per_second)
        .def_readwrite("speedup_factor", &EngineMetrics::speedup_factor)
        .def("update_performance", &EngineMetrics::update_performance)
        .def("print_metrics", &EngineMetrics::print_metrics)
        .def("reset", &EngineMetrics::reset);

    // ------------------------------------------------------------------------
    //  Analog Universal Node (AVX2)
    // ------------------------------------------------------------------------
    py::class_<AnalogUniversalNodeAVX2>(m, "AnalogUniversalNodeAVX2")
        .def(py::init<>())
        .def("process_signal_avx2", &AnalogUniversalNodeAVX2::processSignalAVX2)
        .def("process_signal", &AnalogUniversalNodeAVX2::processSignal)
        .def("set_feedback", &AnalogUniversalNodeAVX2::setFeedback)
        .def("get_output", &AnalogUniversalNodeAVX2::getOutput)
        .def("get_integrator_state", &AnalogUniversalNodeAVX2::getIntegratorState)
        .def("reset_integrator", &AnalogUniversalNodeAVX2::resetIntegrator)
        .def("amplify", &AnalogUniversalNodeAVX2::amplify)
        .def("integrate", &AnalogUniversalNodeAVX2::integrate)
        .def("apply_feedback", &AnalogUniversalNodeAVX2::applyFeedback)
        // --- Oscillator and Filter ---
        .def("oscillate", &AnalogUniversalNodeAVX2::oscillate,
             py::arg("frequency_hz"), py::arg("duration_seconds"),
             "Generate an oscillatory waveform at specified frequency (Hz) for given duration (seconds)")
        .def("process_block_frequency_domain", &AnalogUniversalNodeAVX2::processBlockFrequencyDomain,
             py::arg("input_block"),
             "Process a block of data in the frequency domain for filtering (bandpass)")
        // --- NumPy zero-copy versions ---
        .def("oscillate_np", [](AnalogUniversalNodeAVX2& self, double frequency_hz, double duration_seconds) {
            const int sample_rate = 48000;
            const int num_samples = static_cast<int>(duration_seconds * sample_rate);
            py::array_t<float> output(num_samples);
            py::buffer_info buf = output.request();
            float* ptr = static_cast<float*>(buf.ptr);
            self.oscillate_inplace(ptr, num_samples, frequency_hz, sample_rate);
            return output;
        }, py::arg("frequency_hz"), py::arg("duration_seconds"),
           "Generate waveform with NumPy zero-copy (2-3x faster)")
        .def("process_block_frequency_domain_np", [](AnalogUniversalNodeAVX2& self, py::array_t<float> data) {
            py::buffer_info buf = data.request();
            if (buf.ndim != 1) {
                throw std::runtime_error("Input must be 1-dimensional array");
            }
            float* ptr = static_cast<float*>(buf.ptr);
            int num_samples = static_cast<int>(buf.shape[0]);
            self.processBlockFrequencyDomain_inplace(ptr, num_samples);
            return data;
        }, py::arg("data"),
           "Process signal block with NumPy zero-copy (in-place, faster)")
        // --- Batch processing ---
        .def("process_batch", &AnalogUniversalNodeAVX2::processBatch,
             py::arg("input_signals"), py::arg("control_signals"), py::arg("aux_signals"),
             "Process multiple samples in one call (5-10x faster than individual calls)")
        // --- Public state access ---
        .def_readwrite("x", &AnalogUniversalNodeAVX2::x)
        .def_readwrite("y", &AnalogUniversalNodeAVX2::y)
        .def_readwrite("z", &AnalogUniversalNodeAVX2::z)
        .def_readwrite("node_id", &AnalogUniversalNodeAVX2::node_id)
        .def_readwrite("integrator_state", &AnalogUniversalNodeAVX2::integrator_state)
        .def_readwrite("previous_input", &AnalogUniversalNodeAVX2::previous_input)
        .def_readwrite("current_output", &AnalogUniversalNodeAVX2::current_output)
        .def_readwrite("feedback_gain", &AnalogUniversalNodeAVX2::feedback_gain);

    // ------------------------------------------------------------------------
    //  Analog Cellular Engine
    // ------------------------------------------------------------------------
    py::class_<AnalogCellularEngineAVX2>(m, "AnalogCellularEngineAVX2")
        .def(py::init<std::size_t>(), py::arg("num_nodes") = 1024)
        .def("run_mission", &AnalogCellularEngineAVX2::runMission)
        .def("run_builtin_benchmark", &AnalogCellularEngineAVX2::runBuiltinBenchmark)
        .def("run_massive_benchmark", &AnalogCellularEngineAVX2::runMassiveBenchmark)
        .def("run_drag_race_benchmark", &AnalogCellularEngineAVX2::runDragRaceBenchmark)
        .def("process_signal_wave_avx2", &AnalogCellularEngineAVX2::processSignalWaveAVX2)
        .def("perform_signal_sweep_avx2", &AnalogCellularEngineAVX2::performSignalSweepAVX2)
        .def("process_block_frequency_domain", &AnalogCellularEngineAVX2::processBlockFrequencyDomain)
        .def("calculate_inter_node_coupling", &AnalogCellularEngineAVX2::calculateInterNodeCoupling)
        .def("generate_noise_signal", &AnalogCellularEngineAVX2::generateNoiseSignal)
        .def("get_node_outputs", &AnalogCellularEngineAVX2::getNodeOutputs)
        .def("get_metrics", &AnalogCellularEngineAVX2::getMetrics)
        .def("print_live_metrics", &AnalogCellularEngineAVX2::printLiveMetrics)
        .def("reset_metrics", &AnalogCellularEngineAVX2::resetMetrics)
        // --- Integrated Phase Continuation Mission (Phase 2) ---
        .def("run_phase_continuation_mission_avx2", [](AnalogCellularEngineAVX2& self,
                                                     py::array_t<float> input_stream,
                                                     uint32_t engine_steps_per_frame,
                                                     bool use_eeg_input) {
            py::buffer_info in_buf = input_stream.request();
            
            uint64_t num_frames = 0;
            if (use_eeg_input) {
                if (in_buf.ndim != 2 || in_buf.shape[1] != 8) {
                    throw std::runtime_error("EEG input must be 2D array [frames, 8]");
                }
                num_frames = static_cast<uint64_t>(in_buf.shape[0]);
            } else {
                if (in_buf.ndim != 1) {
                    throw std::runtime_error("Scalar input must be 1D array [frames]");
                }
                num_frames = static_cast<uint64_t>(in_buf.shape[0]);
            }
            
            py::array_t<float> output_phases({num_frames, (uint64_t)8});
            py::array_t<float> mismatches(num_frames);
            
            py::buffer_info out_phi_buf = output_phases.request();
            py::buffer_info mis_buf = mismatches.request();
            
            self.runPhaseContinuationMissionAVX2(
                static_cast<float*>(in_buf.ptr),
                static_cast<float*>(out_phi_buf.ptr),
                static_cast<float*>(mis_buf.ptr),
                num_frames,
                engine_steps_per_frame,
                use_eeg_input
            );
            
            return py::make_tuple(output_phases, mismatches);
        }, py::arg("input_stream"), py::arg("engine_steps_per_frame") = 20, py::arg("use_eeg_input") = false,
           "Run integrated SignalScope mission with zero Python loop overhead");

    // ------------------------------------------------------------------------
    //  Benchmark Helper
    // ------------------------------------------------------------------------
    m.def("benchmark_engine", []() {
        AnalogCellularEngineAVX2 engine(1024);
        engine.runMission(3000);
        EngineMetrics metrics = engine.getMetrics();
        metrics.print_metrics();
        return metrics.throughput_gflops;
    });
}
