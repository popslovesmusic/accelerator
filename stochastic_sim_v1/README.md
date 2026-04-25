# Stochastic Threshold Simulation (v1)

This simulation models an ensemble of states subject to continuous stochastic noise (Langevin dynamics) and deterministic restorative forces. It is designed to study **deviation floors**, **detection thresholds**, and **phase packet onset** events.

## Theoretical Basis

- **Deviation Floor:** The base level of stochastic fluctuation ($\sigma$) that prevents the system from reaching a perfect zero-mismatch state.
- **Detection Threshold:** A defined barrier in state-space ($x_{\text{thresh}}$).
- **Phase Packet Onset:** The stochastic crossing of the detection threshold, representing a discrete event emerging from continuous noise.
- **Kramers Escape:** The simulation tracks the statistics of particles escaping a potential well due to noise.

## Model Equations

### Langevin Dynamics (Overdamped)
$$dx_i = -\frac{dU}{dx_i} dt + \sigma dW_i$$
where $U(x)$ is the potential, and $dW$ is a Wiener process.

### Default Potential (Quadratic)
$U(x) = \frac{1}{2} \kappa x^2$

## Usage

```powershell
python sim.py --config configs/default.json --out outputs/stochastic_run_01
```

## Outputs

- `metrics.csv`: Time-series of mean deviation and cumulative detection rate.
- `summary.json`: Final stats and first-passage time distributions.
- `plots/`: Trajectory traces and onset histograms (if Matplotlib is installed).
