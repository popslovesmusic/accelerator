import numpy as np
import os
import sys

# Windows DLL loading for dependencies (FFTW3, etc.)
if sys.platform == "win32":
    engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Simulation_engines_extracted_2026-04-25"))
    if os.path.exists(engine_root):
        os.add_dll_directory(engine_root)

try:
    import dase_engine as engine_bridge
except ImportError:
    engine_bridge = None
    print("Warning: dase_engine.so/pyd not found. Native AVX2 engine will be unavailable.")

class EngineBridge:
    def __init__(self, num_nodes=100):
        self.num_nodes = num_nodes
        if engine_bridge:
            self.engine = engine_bridge.AnalogCellularEngineAVX2(num_nodes)
        else:
            self.engine = None
            self.dummy_outputs = np.zeros(num_nodes)

    def step(self, input_signal, control_pattern=1.0):
        """
        Processes one step of the engine.
        """
        if self.engine:
            # We use process_signal_wave_avx2 as a single step proxy if runMission is too large
            return self.engine.process_signal_wave_avx2(input_signal, control_pattern)
        else:
            # Dummy dynamics: leaky integrator + noise
            self.dummy_outputs = 0.9 * self.dummy_outputs + 0.1 * input_signal + np.random.normal(0, 0.01, self.num_nodes)
            return np.mean(self.dummy_outputs)

    def evolve(self, input_signal, control_pattern=1.0, steps=20):
        """
        Evolves the field for multiple internal steps.
        """
        last = 0.0
        for _ in range(int(steps)):
            last = self.step(input_signal, control_pattern)
        return last

    def get_node_outputs(self):
        if self.engine:
            return np.array(self.engine.get_node_outputs())
        return self.dummy_outputs

    def get_node_states(self):
        # Placeholder for more complex state extraction if needed
        return self.get_node_outputs()
