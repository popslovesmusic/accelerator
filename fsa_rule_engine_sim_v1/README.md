# Finite-State Automata / Rule Engine Simulation (v1)

This simulation models an **Abstract State Machine** where agents walk a directed graph of discrete states. Transitions (continuations) between states are governed by a strict Boolean **Rule Engine** evaluating admissibility.

## Theoretical Basis

- **Admissible Continuation Set:** Only a subset of possible transitions are allowed based on the system's current configuration and agent history.
- **Exclusion-by-Rule:** Certain states, like $\epsilon=0$ (perfect symmetry), are explicitly forbidden by the Rule Engine.
- **Residue-Gated Transitions:** Transitions to "higher order" states may require the agent to have accumulated a specific amount of **Residue** (history/memory).
- **Continuation Order:** Time is not primitive; it is the order induced by the sequence of admissible continuations.

## Model Logic

### State Graph
- Nodes: Discrete mismatch levels $S_0, S_1, \dots, S_N$.
- Edges: Potential transitions between levels.

### Rule Engine
1. **L0 Rule:** $S_0$ is forbidden. Any edge pointing to $S_0$ is inadmissible.
2. **Residue Rule:** Transitions to states with index $> M$ require agent `residue` $> \theta$.
3. **Connectivity Rule:** If no outgoing edge is admissible, the agent halts ("dead end").

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/fsa_run_01
```

## Outputs

- `metrics.csv`: Time-series of active agent count and mean residue.
- `summary.json`: Final distribution of agents across states.
- `plots/`: Visualization of the state graph colored by agent density (if NetworkX and Matplotlib are installed).
