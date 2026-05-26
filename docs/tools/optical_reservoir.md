# Optical Reservoir Simulation Tool (v1)

## Overview
The **Optical Reservoir Simulation Tool** (`optical_reservoir_sim_v1`) is a high-fidelity discrete-time simulator designed to study the emergence of stable relational basins through optical feedback loops. It models the interaction between LED emitters and light sensors, mediated by an "admissibility window" (comparator) and network-level coupling.

This tool is a primary engine for researching **Relational Persistence** and **Process Synchronization** within the Mono-Process Framework.

---

## Theoretical Mapping
The tool's parameters and internal states map directly to the core primitives of the Mono-Process Framework:

| Primitive | Model Implementation | Description |
| :--- | :--- | :--- |
| **$\epsilon$ (Epsilon)** | `pattern_a/b`, `ambient` | External signal pressure and baseline noise. |
| **$R$ (Residue)** | `rc_tau`, `light_decay` | System memory, including sensor integration and surface field traces. |
| **$\Delta$ (Delta)** | `window_low/high` | Admissibility gating; the comparator selects signals for feedback. |
| **$-(i)$ (Orientation)** | `triad_readout` | Readout re-orientation via difference-vector extraction. |
| **$K$ (Coupling)** | `TriadNetworkParams` | Inter-triad topology (Chain, Ring, Fully-Connected). |
| **$\rho$ (Rho)** | `feedback_enable` | The capacity for the process to continue through self-sustaining loops. |

---

## Key Capabilities

### 1. Triad-Based Architecture
The simulation is built around the **Triad** unit: a cluster of 3 sensors and 3 LEDs.
*   **Intra-Triad Mixing:** Sensors respond to a weighted mix of LED outputs.
*   **Orientation Extraction:** Local orientation is derived from pairwise differences between sensor readouts.

### 2. Network Topologies
The tool supports multiple network configurations for multi-triad interaction:
*   **Isolated:** Triads operate independently.
*   **Chain:** Linear coupling between neighbors.
*   **Ring:** Periodic boundary coupling.
*   **Fully Connected:** Every triad influences every other triad.

### 3. "Open to Closed Loop" Experiment
A flagship capability that traces the lifecycle of process stabilization:
1.  **Open Propagation:** Linear signal flow.
2.  **Delayed Self-Contact:** Feedback with high latency.
3.  **Local Loop Closure:** Low-latency feedback leading to basin emergence.
4.  **Stable Knot-Like Basin:** High-persistence states under asymmetry.
5.  **Collapse/Saturation:** System failure under extreme drive.

### 4. Advanced Observables
*   **Persistence Score:** Measures the temporal stability of internal residue.
*   **Synchronization Index:** Quantifies phase-locking across the network.
*   **Inside Rate:** Percentage of time the system state spends within the admissibility window.
*   **Oscillation Score:** Spectral measure of recurrent periodicity.

---

## Usage

### Basic Execution
```powershell
python tools/optical_reservoir/simulate_optical_reservoir.py --steps 2000 --dt 0.005 --feedback
```

### Input Pattern Grammar
Patterns for `--pattern-a` and `--pattern-b`:
*   `const:<v>` (e.g., `const:0.5`)
*   `sine:<freq>:<amp>:<bias>` (e.g., `sine:2:0.5:0.5`)
*   `blink:<period>:<duty>:<v>` (e.g., `blink:0.2:0.5:1.0`)
*   `randbits:<period>:<v>` (e.g., `randbits:0.05:1.0`)

### Network Mode
```powershell
python tools/optical_reservoir/simulate_optical_reservoir.py --network-mode triad_network --triads 3 --topology ring --inter-strength 0.1
```

---

## Rigor & Validation Status

**Current Level: C4 (High Rigor)**

### Validation Benchmarks
*   **Numerical Stability:** Converged at `dt <= 0.01`. Usage of `dt > 0.05` is discouraged for high-rigor claims.
*   **Falsification:** Passed negative-control tests for feedback removal and admissibility window masking.
*   **Uncertainty:** Characterized via multi-seed ensembles ($n=3$) under noise and asymmetry.
*   **Cross-Model:** Synchronization behavior verified against Kuramoto-class C++ engines.

### Known Limits
*   **Implementation:** Python-only. While high-rigor for internal research, Level C5+ claims require porting to the C++ `dase_analog` or `igsoa_complex` architectures.
*   **Computational Cost:** Performance scales $O(N^2)$ with the number of triads in fully-connected mode.

---

## Output Formats
*   **Standard Out:** JSON summary or space-delimited legacy metrics.
*   **NPZ:** Compressed NumPy arrays containing full timeseries for all internal states (`sensors`, `rc`, `comp`, `out_led`, etc.).
*   **PNG:** Multi-panel diagnostic plots showing signal traces and admissibility boundaries.
