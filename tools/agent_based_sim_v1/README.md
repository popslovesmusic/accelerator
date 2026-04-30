# Agent-Based Phase-Space Swarm Simulation (v1)

This simulator implements a **Phase-Space Swarm** model where agents possess both physical trajectories and internal states. It is specifically designed to study the emergence of global constraints from local interactions, as described in "THE LAW OF THE ONE PROCESS."

## 1. Theoretical Framework

Agents in this model represent processes governed by:
- **CSI (Causal Sphere of Influence):** Interaction is local. Two agents $i$ and $j$ only interact if their phase-space distance $d_{ij} = \sqrt{(x_i-x_j)^2 + (p_i-p_j)^2}$ is less than the radius $R_c$.
- **Phase Locking:** Agents attempt to synchronize their internal phases ($\phi$) with their neighbors within their CSI.
- **Mismatch ($\epsilon$):** Represents local deviation or "stress." Mismatch grows naturally but is relaxed when the agent is phase-locked with its neighbors.
- **Residue ($R$):** The historical integration of mismatch, representing the accumulated "trace" of past constraints.

## 2. Getting Started

### Prerequisites
- Python 3.8+
- `numpy`, `pandas` (required for simulation and logging)
- `matplotlib` (optional, for generating plots)

### Quick Run
Execute the default simulation (100 agents, 1000 steps):
```powershell
python sim.py --config configs/default.json --out outputs/my_first_run
```

## 3. Configuration Guide

The simulator is driven by JSON configuration files. Key parameters include:

| Parameter | Description |
| :--- | :--- |
| `n_agents` | Total number of agents in the swarm. |
| `steps` | Number of integration steps. |
| `dt` | Time step for RK4 integration. |
| `R_c` | **Causal Radius.** The distance threshold for interactions. |
| `K_phi` | **Coupling Strength.** How strongly agents align their phases. |
| `kappa` | Harmonic confinement strength (keeps the swarm from drifting to infinity). |
| `omega_mean` / `std` | The natural frequency distribution of the agents' internal oscillators. |
| `mismatch_rate` | Rate at which internal mismatch grows. |
| `initial_distribution` | `"gaussian"` for a single cluster, or `"two_clusters"` for isolation testing. |

## 4. Pre-defined Experimental Scenarios

We have provided several configurations to demonstrate different regimes:

- **`configs/default.json`**: Standard coupled swarm. Shows rapid phase-locking and steady residue growth.
- **`configs/no_coupling.json`**: Sets $K_{\phi} = 0$. Useful for verifying that global coherence does not emerge without interaction.
- **`configs/csi_isolation.json`**: Places two clusters far apart. Demonstrates that phase-locking is local; the two groups will not synchronize with each other if $d > R_c$.
- **`configs/event_chain_trigger.json`**: Low $R_c$ and high $K_{\phi}$. Designed to show a "cascade" or event chain where phase alignment propagates through the swarm like a wave.

## 5. Interpreting Outputs

Results are saved in the directory specified by `--out`:

- **`metrics.csv`**: Time-series data including:
    - `order_parameter`: Global phase coherence (0 to 1).
    - `local_coherence_mean`: Average coherence between neighbors within their CSI.
    - `residue_mean`: Average accumulated trace across the swarm.
- **`summary.json`**: Final state snapshot and a copy of the configuration used.
- **`plots/`** (if Matplotlib is installed):
    - `evolution.png`: Trends for order parameter and residue.
    - `phase_space.png`: Scatter plot of agents in $(x, p)$ colored by their internal phase $\phi$.

## 6. Execution Command Reference

```powershell
# Basic execution
python sim.py --config configs/default.json --out outputs/run_name

# Test isolation behavior
python sim.py --config configs/csi_isolation.json --out outputs/isolation_test

# Observe a cascading event chain
python sim.py --config configs/event_chain_trigger.json --out outputs/cascade
```
