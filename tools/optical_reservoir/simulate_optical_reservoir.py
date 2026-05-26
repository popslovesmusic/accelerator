#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass

import numpy as np


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def _clip01(x: np.ndarray | float) -> np.ndarray | float:
    return np.clip(x, 0.0, 1.0)


def parse_pattern(pattern: str, steps: int, dt: float) -> np.ndarray:
    """
    Supported patterns:
      - const:<v>                 e.g. const:0.7
      - pulse:<t0>:<t1>:<v>       e.g. pulse:0.5:1.0:1.0  (seconds)
      - blink:<period>:<duty>:<v> e.g. blink:0.2:0.5:1.0  (seconds, 0..1, 0..1)
      - sine:<freq>:<amp>:<bias>  e.g. sine:2:0.5:0.5     (Hz)
      - randbits:<period>:<v>     e.g. randbits:0.1:1.0   (seconds)
      - list:<v0>,<v1>,...        per-step list (repeats/truncates)
    """
    if ":" not in pattern:
        raise ValueError(f"Bad pattern '{pattern}'. Expected kind:args")
    kind, rest = pattern.split(":", 1)
    t = np.arange(steps) * dt

    if kind == "const":
        v = float(rest)
        return np.full(steps, v, dtype=float)

    if kind == "pulse":
        t0_s, t1_s, v_s = rest.split(":")
        t0 = float(t0_s)
        t1 = float(t1_s)
        v = float(v_s)
        out = np.zeros(steps, dtype=float)
        out[(t >= t0) & (t < t1)] = v
        return out

    if kind == "blink":
        period_s, duty_s, v_s = rest.split(":")
        period = float(period_s)
        duty = float(duty_s)
        v = float(v_s)
        phase = np.mod(t, period) / period
        return np.where(phase < duty, v, 0.0).astype(float)

    if kind == "sine":
        freq_s, amp_s, bias_s = rest.split(":")
        freq = float(freq_s)
        amp = float(amp_s)
        bias = float(bias_s)
        return (bias + amp * np.sin(2 * math.pi * freq * t)).astype(float)

    if kind == "randbits":
        period_s, v_s = rest.split(":")
        period = float(period_s)
        v = float(v_s)
        samples_per = max(1, int(round(period / dt)))
        rng = np.random.default_rng(0)
        bits = rng.integers(0, 2, size=int(math.ceil(steps / samples_per)))
        return np.repeat(bits.astype(float) * v, samples_per)[:steps]

    if kind == "list":
        values = [float(x.strip()) for x in rest.split(",") if x.strip() != ""]
        if not values:
            raise ValueError("list: needs at least one value")
        reps = int(math.ceil(steps / len(values)))
        return np.tile(np.array(values, dtype=float), reps)[:steps]

    raise ValueError(f"Unknown pattern kind '{kind}'")


@dataclass(frozen=True)
class OpticalReservoirParams:
    # LED -> sensor mixing weights. Shape: (num_sensors, num_leds)
    W: np.ndarray
    ambient: float = 0.02
    sensor_nonlinearity: float = 1.0  # 1.0 = linear, <1 compresses, >1 expands
    sensor_noise_std: float = 0.0
    light_decay: float = 0.0  # 0..1, leaky surface field memory

    # "Op-amp" stage (modeled as gain + saturation)
    opamp_gain: float = 8.0
    opamp_bias: float = 0.0
    opamp_sat: float = 1.0  # output saturation magnitude
    common_mode_gain: float = 0.0  # adds sensitivity to overall brightness (enables "too_high" exhaustion)

    # RC memory (low-pass on op-amp output), roughly "residue/history"
    rc_tau: float = 0.10  # seconds
    rc_decay: float | None = None  # if set, overrides rc_tau via discrete decay factor 0..1

    # Comparator "admissibility window" (pots), plus hysteresis
    window_low: float = 0.35
    window_high: float = 0.70
    hysteresis: float = 0.03

    # Output LED dynamics and feedback strength
    out_tau: float = 0.05  # seconds
    out_level: float = 1.0

    # Optional leaky-integrator extra state to encourage richer dynamics
    extra_leak_tau: float = 0.25  # seconds
    extra_state_gain: float = 0.0


@dataclass(frozen=True)
class TriadNetworkParams:
    triads: int = 1
    topology: str = "chain"  # isolated, chain, ring, fully_connected
    intra_strength: float = 1.0
    inter_strength: float = 0.08
    asymmetry: float = 0.03
    seed: int = 0
    per_triad_windows: bool = True
    delay_steps: int = 1  # feedback / coupling delay in discrete steps


def build_topology_matrix(triad_count: int, topology: str, inter_strength: float) -> np.ndarray:
    """
    Returns T with shape (triad_count, triad_count). Diagonal is 0.
    T[k,j] scales contribution of triad j output into triad k's LED drive.
    """
    n = int(triad_count)
    if n <= 0:
        raise ValueError("triad_count must be > 0")
    s = float(inter_strength)
    if s < 0:
        raise ValueError("inter_strength must be >= 0")

    T = np.zeros((n, n), dtype=float)
    if topology == "isolated" or s == 0.0:
        return T

    if topology == "chain":
        for k in range(n):
            if k - 1 >= 0:
                T[k, k - 1] = s
            if k + 1 < n:
                T[k, k + 1] = s
        return T

    if topology == "ring":
        for k in range(n):
            T[k, (k - 1) % n] = s
            T[k, (k + 1) % n] = s
        return T

    if topology == "fully_connected":
        for k in range(n):
            for j in range(n):
                if k != j:
                    T[k, j] = s / max(1, (n - 1))
        return T

    raise ValueError(f"Unknown topology '{topology}'")


def _orientation_readout_3(sensor_field: np.ndarray) -> np.ndarray:
    """
    sensor_field: shape (..., 3)
    Returns a 3-channel 'difference' vector per triad/channel.
    """
    s0 = sensor_field[..., 0]
    s1 = sensor_field[..., 1]
    s2 = sensor_field[..., 2]
    return np.stack([s0 - s1, s1 - s2, s2 - s0], axis=-1)


def _mean_pairwise_corr(X: np.ndarray) -> float:
    """
    X: shape (T, N). Returns mean upper-triangle Pearson correlation.
    Robust to zero-variance channels (they are ignored).
    """
    if X.ndim != 2:
        raise ValueError("X must be 2D (T,N)")
    T, N = X.shape
    if N < 2:
        return 1.0
    Xc = X - X.mean(axis=0, keepdims=True)
    std = Xc.std(axis=0, ddof=1, keepdims=True)
    good = (std[0] > 1e-12)
    if np.sum(good) < 2:
        return 0.0
    Xn = np.zeros_like(Xc)
    Xn[:, good] = Xc[:, good] / std[:, good]
    corr = (Xn.T @ Xn) / max(1, (T - 1))
    iu = np.triu_indices(N, k=1)
    vals = corr[iu]
    # Filter out correlations involving bad channels by masking pairs
    mask = good[iu[0]] & good[iu[1]]
    if not np.any(mask):
        return 0.0
    m = float(np.mean(vals[mask]))
    return float(np.clip(m, -1.0, 1.0))


def simulate_triad_network(
    *,
    steps: int,
    dt: float,
    led_inputs: np.ndarray,
    feedback_enable: bool,
    base_params: OpticalReservoirParams,
    net: TriadNetworkParams,
) -> dict[str, np.ndarray]:
    """
    Multi-triad extension. Shapes:
      - led_inputs: (steps, triads, 3) external input LEDs (A,B,EXT/0)
      - out_led: (steps, triads, 3)
      - sensors: (steps, triads, 3)
      - rc/extra: (steps, triads, 3)
      - comp: (steps, triads)
    """
    triads = int(net.triads)
    if triads <= 0:
        raise ValueError("--triads must be >= 1")
    if led_inputs.shape != (steps, triads, 3):
        raise ValueError("led_inputs must be shape (steps, triads, 3)")
    if base_params.W.shape != (3, 3):
        raise ValueError("base_params.W must be (3,3)")

    rng = np.random.default_rng(int(net.seed))

    # Local (intra) matrices per triad, plus small asymmetries.
    # Keep the structure stable and explicit so it can be ported to C++.
    intra_base = float(net.intra_strength) * base_params.W
    intra = np.repeat(intra_base[None, :, :], triads, axis=0)  # (triads,3,3)

    if net.asymmetry > 0.0:
        a = float(net.asymmetry)
        intra += rng.normal(0.0, a, size=intra.shape)
        intra = np.maximum(intra, 0.0)

    # Per-triad sensor biases and per-triad gain offsets (D/I proxies)
    sensor_bias = np.zeros((triads, 3), dtype=float)
    triad_gain = np.ones((triads, 1), dtype=float)
    if net.asymmetry > 0.0:
        a = float(net.asymmetry)
        sensor_bias = rng.normal(0.0, a, size=(triads, 3))
        triad_gain = 1.0 + rng.normal(0.0, a, size=(triads, 1))

    # Topology (inter-triad coupling)
    T = build_topology_matrix(triads, net.topology, float(net.inter_strength))
    if net.asymmetry > 0.0 and triads > 1:
        # Directional weight perturbation, preserving non-negativity.
        T = np.maximum(0.0, T + rng.normal(0.0, float(net.asymmetry), size=T.shape))
        np.fill_diagonal(T, 0.0)

    out_led = np.zeros((steps, triads, 3), dtype=float)
    sensors = np.zeros((steps, triads, 3), dtype=float)
    surface = np.zeros((steps, triads, 3), dtype=float)
    opamp = np.zeros((steps, triads, 3), dtype=float)
    rc = np.zeros((steps, triads, 3), dtype=float)
    extra = np.zeros((steps, triads, 3), dtype=float)
    comp = np.zeros((steps, triads), dtype=float)

    # Decays / low-pass
    if base_params.rc_decay is not None:
        a_rc = float(np.clip(base_params.rc_decay, 0.0, 1.0))
    else:
        a_rc = math.exp(-dt / max(1e-9, base_params.rc_tau))
    a_out = math.exp(-dt / max(1e-9, base_params.out_tau))
    a_extra = math.exp(-dt / max(1e-9, base_params.extra_leak_tau))
    a_light = float(np.clip(base_params.light_decay, 0.0, 1.0))

    # Per-triad admissibility windows (optional small offsets)
    win_low = np.full(triads, float(base_params.window_low), dtype=float)
    win_high = np.full(triads, float(base_params.window_high), dtype=float)
    if net.per_triad_windows and net.asymmetry > 0.0:
        a = float(net.asymmetry)
        win_low = win_low + rng.normal(0.0, a, size=triads)
        win_high = win_high + rng.normal(0.0, a, size=triads)
        win_low = np.clip(win_low, 0.0, 1.0)
        win_high = np.clip(win_high, 0.0, 1.0)
        win_low, win_high = np.minimum(win_low, win_high), np.maximum(win_low, win_high)

    last_comp = np.zeros(triads, dtype=float)

    for i in range(steps):
        d = int(net.delay_steps)
        if d < 1:
            d = 1
        idx = i - d
        out_prev = out_led[idx] if idx >= 0 else np.zeros((triads, 3), dtype=float)

        # Neighbor coupling in LED-space: sum_j T[k,j] * out_prev[j]
        neighbor_drive = T @ out_prev  # (triads,3)

        local_leds = led_inputs[i].copy()
        if feedback_enable:
            local_leds += out_prev
        total_leds = _clip01(local_leds + neighbor_drive)

        # Sensor field (with surface memory / light decay)
        drive = np.einsum("kij,kj->ki", intra, total_leds) + float(base_params.ambient)
        drive = np.maximum(drive + sensor_bias, 0.0)
        if base_params.sensor_nonlinearity != 1.0:
            drive = drive ** float(base_params.sensor_nonlinearity)

        if base_params.light_decay > 0.0:
            prev_field = surface[i - 1] if i > 0 else np.zeros((triads, 3), dtype=float)
            field = a_light * prev_field + (1.0 - a_light) * drive
        else:
            field = drive
        surface[i] = field

        raw = field
        if base_params.sensor_noise_std > 0.0:
            # per-channel noise, with optional asymmetry already in sensor_bias
            raw = raw + rng.normal(0.0, float(base_params.sensor_noise_std), size=raw.shape)
        sensors[i] = raw

        # Orientation-sensitive readout -> opamp -> 0..1
        diff_vec = _orientation_readout_3(raw)
        if base_params.common_mode_gain != 0.0:
            cm = np.mean(raw, axis=1, keepdims=True)  # (triads,1)
            diff_vec = diff_vec + float(base_params.common_mode_gain) * cm
        diff_vec = diff_vec * triad_gain
        v = float(base_params.opamp_gain) * diff_vec + float(base_params.opamp_bias)
        v = np.clip(v, -float(base_params.opamp_sat), float(base_params.opamp_sat))
        v01 = _sigmoid(v)
        opamp[i] = v01

        # Residue/history per triad per channel
        rc_prev = rc[i - 1] if i > 0 else np.zeros((triads, 3), dtype=float)
        rc_i = a_rc * rc_prev + (1.0 - a_rc) * v01
        rc[i] = rc_i

        extra_prev = extra[i - 1] if i > 0 else np.zeros((triads, 3), dtype=float)
        extra_i = a_extra * extra_prev + (1.0 - a_extra) * (float(base_params.extra_state_gain) * rc_i)
        extra[i] = extra_i

        state = rc_i + extra_i  # (triads,3)
        state_scalar = np.mean(state, axis=1)  # (triads,)

        low = win_low - (float(base_params.hysteresis) * (last_comp > 0.5))
        high = win_high + (float(base_params.hysteresis) * (last_comp < 0.5))
        within = ((state_scalar >= low) & (state_scalar <= high)).astype(float)
        comp[i] = within
        last_comp = within

        target = within[:, None] * float(base_params.out_level)
        out_led[i] = a_out * out_prev + (1.0 - a_out) * target

    return {
        "t": np.arange(steps) * dt,
        "led_inputs": led_inputs,
        "topology": T,
        "sensors": sensors,
        "surface": surface,
        "opamp": opamp,
        "rc": rc,
        "extra": extra,
        "comp": comp,
        "out_led": out_led,
        "win_low": win_low,
        "win_high": win_high,
    }


def _network_summary_json(
    *,
    simn: dict[str, np.ndarray],
    triads: int,
    topology: str,
    params: OpticalReservoirParams,
    net: TriadNetworkParams,
    persistence_eps: float,
    collapse_eps: float,
    stage: str | None = None,
) -> dict:
    state = simn["rc"] + simn["extra"]  # (steps,triads,3)
    state_scalar = np.mean(state, axis=2)  # (steps,triads)
    below = state_scalar < simn["win_low"][None, :]
    above = state_scalar > simn["win_high"][None, :]
    inside = (~below) & (~above)

    per_inside = inside.mean(axis=0)
    per_below = below.mean(axis=0)
    per_above = above.mean(axis=0)
    per_comp = simn["comp"].mean(axis=0)
    out = simn["out_led"]
    per_out_mean = out.mean(axis=(0, 2))
    per_out_std = out.std(axis=(0, 2))

    out_mean_t = out.mean(axis=2)  # (steps,triads)
    delta_out = np.diff(out_mean_t, axis=0)  # (steps-1,triads)
    mean_pairwise_corr = _mean_pairwise_corr(out_mean_t)
    mean_pairwise_delta_corr = _mean_pairwise_corr(delta_out)
    sync_index = abs(mean_pairwise_delta_corr)

    net_state_t = np.mean(state_scalar, axis=1)  # (steps,)
    persistence = float(np.mean(np.abs(np.diff(net_state_t)) < float(persistence_eps)))
    collapse_count = int(np.sum(np.std(out_mean_t, axis=0) < float(collapse_eps)))

    summary = {
        "mode": "triad_network",
        "triads": triads,
        "topology": topology,
        "stage": stage,
        "params": {
            "intra_strength": net.intra_strength,
            "inter_strength": net.inter_strength,
            "asymmetry": net.asymmetry,
            "delay_steps": net.delay_steps,
            "light_decay": params.light_decay,
            "memory_decay": params.rc_decay,
            "window_low": params.window_low,
            "window_high": params.window_high,
            "persistence_eps": float(persistence_eps),
            "collapse_eps": float(collapse_eps),
            "common_mode_gain": params.common_mode_gain,
            "out_level": params.out_level,
            "opamp_gain": params.opamp_gain,
        },
        "per_triad": [
            {
                "triad": int(k),
                "inside_rate": float(per_inside[k]),
                "below_rate": float(per_below[k]),
                "above_rate": float(per_above[k]),
                "comp_on_rate": float(per_comp[k]),
                "out_mean": float(per_out_mean[k]),
                "out_std": float(per_out_std[k]),
                "oscillation_score": float(np.mean(np.abs(np.diff(out_mean_t[:, k])))),
            }
            for k in range(triads)
        ],
        "network": {
            "global_inside_rate": float(inside.mean()),
            "global_failure_rate": float(below.mean()),
            "global_saturation_rate": float(above.mean()),
            "mean_pairwise_correlation": mean_pairwise_corr,
            "mean_pairwise_delta_correlation": mean_pairwise_delta_corr,
            "synchronization_index": sync_index,
            "persistence_score": persistence,
            "collapse_count": collapse_count,
        },
    }
    # Drop stage key when not used
    if stage is None:
        summary.pop("stage", None)
    # feedback_enable lives outside net/params; set by caller via injection
    return summary


def run_open_to_closed_loop_experiment(
    *,
    steps: int,
    dt: float,
    led_a: np.ndarray,
    led_b: np.ndarray,
    triads: int,
    topology: str,
    params: OpticalReservoirParams,
    base_net: TriadNetworkParams,
    persistence_eps: float,
    collapse_eps: float,
    plot_prefix: str,
    save_npz_prefix: str,
) -> list[dict]:
    """
    Implements the staged transition:
      0 open propagation (no feedback, no coupling)
      1 weak return influence (weak coupling)
      2 delayed self-contact (feedback with delay>1)
      3 local loop closure (feedback delay=1)
      4 stable knot-like basin (same, with asymmetry)
      5 collapse/saturation (enable common-mode + overdrive)
    Returns list of JSON-able summaries (one per stage).
    """
    led_inputs = np.zeros((steps, triads, 3), dtype=float)
    led_inputs[:, :, 0] = led_a[:, None]
    led_inputs[:, :, 1] = led_b[:, None]

    stages: list[tuple[str, dict]] = [
        ("stage_0_open_propagation", {"feedback": False, "inter_strength": 0.0, "delay_steps": 1}),
        ("stage_1_weak_return_influence", {"feedback": False, "inter_strength": 0.02, "delay_steps": 1}),
        ("stage_2_delayed_self_contact", {"feedback": True, "inter_strength": 0.02, "delay_steps": max(2, int(round(0.05 / dt)))}),
        ("stage_3_local_loop_closure", {"feedback": True, "inter_strength": float(base_net.inter_strength), "delay_steps": 1}),
        ("stage_4_stable_basin", {"feedback": True, "inter_strength": float(base_net.inter_strength), "delay_steps": 1, "asymmetry": float(base_net.asymmetry)}),
        ("stage_5_collapse_or_saturation", {"feedback": True, "inter_strength": max(float(base_net.inter_strength), 0.6), "delay_steps": 1, "common_mode_gain": max(params.common_mode_gain, 1.0), "opamp_gain": max(params.opamp_gain, 20.0), "out_level": max(params.out_level, 2.0)}),
    ]

    results: list[dict] = []
    for name, overrides in stages:
        feedback = bool(overrides.get("feedback", True))
        net = TriadNetworkParams(
            triads=triads,
            topology=topology,
            intra_strength=float(base_net.intra_strength),
            inter_strength=float(overrides.get("inter_strength", base_net.inter_strength)),
            asymmetry=float(overrides.get("asymmetry", base_net.asymmetry)),
            seed=int(base_net.seed),
            per_triad_windows=bool(base_net.per_triad_windows),
            delay_steps=int(overrides.get("delay_steps", base_net.delay_steps)),
        )
        stage_params = OpticalReservoirParams(
            W=params.W,
            ambient=params.ambient,
            sensor_nonlinearity=params.sensor_nonlinearity,
            sensor_noise_std=params.sensor_noise_std,
            light_decay=params.light_decay,
            opamp_gain=float(overrides.get("opamp_gain", params.opamp_gain)),
            opamp_bias=params.opamp_bias,
            opamp_sat=params.opamp_sat,
            common_mode_gain=float(overrides.get("common_mode_gain", params.common_mode_gain)),
            rc_tau=params.rc_tau,
            rc_decay=params.rc_decay,
            window_low=params.window_low,
            window_high=params.window_high,
            hysteresis=params.hysteresis,
            out_tau=params.out_tau,
            out_level=float(overrides.get("out_level", params.out_level)),
            extra_leak_tau=params.extra_leak_tau,
            extra_state_gain=params.extra_state_gain,
        )

        simn = simulate_triad_network(
            steps=steps,
            dt=dt,
            led_inputs=led_inputs,
            feedback_enable=feedback,
            base_params=stage_params,
            net=net,
        )

        summary = _network_summary_json(
            simn=simn,
            triads=triads,
            topology=topology,
            params=stage_params,
            net=net,
            persistence_eps=persistence_eps,
            collapse_eps=collapse_eps,
            stage=name,
        )
        summary["params"]["feedback"] = feedback
        results.append(summary)

        if save_npz_prefix:
            np.savez_compressed(
                f"{save_npz_prefix}_{name}.npz",
                t=simn["t"],
                led_inputs=simn["led_inputs"],
                topology=simn["topology"],
                sensors=simn["sensors"],
                surface=simn["surface"],
                opamp=simn["opamp"],
                rc=simn["rc"],
                extra=simn["extra"],
                comp=simn["comp"],
                out_led=simn["out_led"],
                win_low=simn["win_low"],
                win_high=simn["win_high"],
            )

        if plot_prefix:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            out_mean_t = simn["out_led"].mean(axis=2)
            state_scalar = np.mean(simn["rc"] + simn["extra"], axis=2)
            t = simn["t"]

            fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
            axes[0].plot(t, out_mean_t, linewidth=1)
            axes[0].set_ylabel("out_mean(t)")
            axes[0].set_title(name)
            axes[1].step(t, simn["comp"], where="post")
            axes[1].set_ylabel("comp")
            axes[1].set_ylim(-0.1, 1.1)
            axes[2].plot(t, state_scalar, linewidth=1)
            axes[2].set_ylabel("state")
            axes[2].set_xlabel("t (s)")
            fig.tight_layout()
            fig.savefig(f"{plot_prefix}_{name}.png", dpi=160)

    return results


def simulate(
    steps: int,
    dt: float,
    led_a: np.ndarray,
    led_b: np.ndarray,
    feedback_enable: bool,
    params: OpticalReservoirParams,
) -> dict[str, np.ndarray]:
    if led_a.shape != (steps,) or led_b.shape != (steps,):
        raise ValueError("led_a/led_b must be shape (steps,)")
    if params.W.shape != (3, 3):
        raise ValueError("params.W must be shape (3, 3) for 3 sensors x 3 LEDs")

    rng = np.random.default_rng(1)
    num_sensors = 3

    out_led = np.zeros(steps, dtype=float)
    sensors = np.zeros((steps, num_sensors), dtype=float)
    surface = np.zeros((steps, num_sensors), dtype=float)
    op = np.zeros(steps, dtype=float)
    rc = np.zeros(steps, dtype=float)
    extra = np.zeros(steps, dtype=float)
    comp = np.zeros(steps, dtype=float)

    # Precompute low-pass coefficients
    if params.rc_decay is not None:
        a_rc = float(np.clip(params.rc_decay, 0.0, 1.0))
    else:
        a_rc = math.exp(-dt / max(1e-9, params.rc_tau))
    a_out = math.exp(-dt / max(1e-9, params.out_tau))
    a_extra = math.exp(-dt / max(1e-9, params.extra_leak_tau))

    last_comp = 0.0
    for i in range(steps):
        leds = np.array(
            [
                float(led_a[i]),
                float(led_b[i]),
                float(out_led[i - 1] if i > 0 else 0.0) if feedback_enable else 0.0,
            ],
            dtype=float,
        )
        leds = _clip01(leds)

        drive = params.W @ leds + params.ambient
        drive = np.maximum(drive, 0.0)
        if params.sensor_nonlinearity != 1.0:
            drive = drive ** params.sensor_nonlinearity

        if params.light_decay > 0.0:
            a_light = float(np.clip(params.light_decay, 0.0, 1.0))
            prev = surface[i - 1] if i > 0 else np.zeros(num_sensors, dtype=float)
            field = a_light * prev + (1.0 - a_light) * drive
        else:
            field = drive
        surface[i] = field

        raw = field
        if params.sensor_noise_std > 0:
            raw = raw + rng.normal(0.0, params.sensor_noise_std, size=raw.shape)
        sensors[i] = raw

        # 3-sensor readout: combine pairwise differences, optionally plus common-mode brightness.
        diff = (raw[0] - raw[1]) + 0.7 * (raw[1] - raw[2]) + 0.4 * (raw[2] - raw[0])
        diff = diff + float(params.common_mode_gain) * float(np.mean(raw))
        diff = float(diff)

        v = params.opamp_gain * diff + params.opamp_bias
        v = float(np.clip(v, -params.opamp_sat, params.opamp_sat))
        # Map to 0..1 so the admissibility window can naturally live in [0,1]
        v01 = float(_sigmoid(v))
        op[i] = v01

        # RC memory
        rc_prev = rc[i - 1] if i > 0 else 0.0
        rc_i = a_rc * rc_prev + (1.0 - a_rc) * v01
        rc[i] = rc_i

        # Extra leaky state (optional richness)
        extra_prev = extra[i - 1] if i > 0 else 0.0
        extra_i = a_extra * extra_prev + (1.0 - a_extra) * (params.extra_state_gain * rc_i)
        extra[i] = extra_i

        # Comparator with window + hysteresis. We let hysteresis widen the window
        # depending on the previous comparator output.
        low = params.window_low - (params.hysteresis if last_comp > 0.5 else 0.0)
        high = params.window_high + (params.hysteresis if last_comp < 0.5 else 0.0)
        within = 1.0 if (low <= (rc_i + extra_i) <= high) else 0.0
        comp[i] = within
        last_comp = within

        # Output LED (smoothed)
        out_prev = out_led[i - 1] if i > 0 else 0.0
        target = params.out_level if within > 0.5 else 0.0
        out_led[i] = a_out * out_prev + (1.0 - a_out) * target

    return {
        "led_a": led_a,
        "led_b": led_b,
        "out_led": out_led,
        "sensors": sensors,
        "surface": surface,
        "opamp": op,
        "rc": rc,
        "extra": extra,
        "comp": comp,
        "t": np.arange(steps) * dt,
    }


def build_default_params(mix: str, feedback_strength: float) -> OpticalReservoirParams:
    # 3-sensor x 3-LED default:
    # LEDs are [A, B, OUT], sensors are [S0, S1, S2].
    if mix == "symmetric":
        W = np.array(
            [
                [1.00, 0.35, 0.55 * feedback_strength],
                [0.35, 1.00, 0.55 * feedback_strength],
                [0.55, 0.55, 0.55 * feedback_strength],
            ],
            dtype=float,
        )
    elif mix == "directional":
        W = np.array(
            [
                [1.00, 0.20, 0.65 * feedback_strength],
                [0.10, 1.00, 0.40 * feedback_strength],
                [0.35, 0.55, 0.25 * feedback_strength],
            ],
            dtype=float,
        )
    elif mix == "weird":
        # stronger cross-talk + asymmetric feedback to encourage flicker/lock-in
        W = np.array(
            [
                [1.00, 0.55, 0.80 * feedback_strength],
                [0.45, 1.00, 0.25 * feedback_strength],
                [0.65, 0.25, 0.55 * feedback_strength],
            ],
            dtype=float,
        )
    else:
        raise ValueError(f"Unknown mix '{mix}'")
    return OpticalReservoirParams(W=W)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discrete-time simulator for a simple LED–surface–sensor feedback 'optical reservoir'."
    )
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--dt", type=float, default=0.002)
    parser.add_argument("--pattern-a", type=str, default="blink:0.20:0.5:1.0")
    parser.add_argument("--pattern-b", type=str, default="blink:0.23:0.5:1.0")
    parser.add_argument("--feedback", action="store_true", help="Enable output LED optical feedback")
    parser.add_argument("--mix", type=str, default="weird", choices=["symmetric", "directional", "weird"])
    parser.add_argument("--feedback-strength", type=float, default=0.15)
    parser.add_argument("--window-low", type=float, default=0.35)
    parser.add_argument("--window-high", type=float, default=0.70)
    parser.add_argument("--hysteresis", type=float, default=0.03)
    parser.add_argument("--opamp-gain", type=float, default=8.0)
    parser.add_argument("--opamp-sat", type=float, default=1.0)
    parser.add_argument("--common-mode-gain", type=float, default=0.0, help="Adds brightness sensitivity to the readout (enables 'too_high').")
    parser.add_argument("--rc-tau", type=float, default=0.10)
    parser.add_argument("--memory-decay", type=float, default=0.92, help="Discrete RC decay 0..1 (overrides --rc-tau)")
    parser.add_argument("--out-tau", type=float, default=0.05)
    parser.add_argument("--out-level", type=float, default=1.0)
    parser.add_argument("--ambient", type=float, default=0.02)
    parser.add_argument("--light-decay", type=float, default=0.85, help="Surface field decay 0..1")
    parser.add_argument("--noise", type=float, default=0.01)
    parser.add_argument("--sensor-nonlinearity", type=float, default=1.0)
    parser.add_argument("--extra-state-gain", type=float, default=0.0)
    parser.add_argument("--extra-tau", type=float, default=0.25)
    parser.add_argument("--plot", type=str, default="", help="Write plot PNG to this path (e.g. out.png)")

    # Multi-triad extension (defaults preserve legacy behavior)
    parser.add_argument(
        "--network-mode",
        type=str,
        default="legacy",
        choices=["legacy", "triad_network"],
        help="Simulation mode. 'legacy' preserves single-triad behavior.",
    )
    parser.add_argument("--triads", type=int, default=1, help="Number of triads to simulate. 1 preserves legacy behavior.")
    parser.add_argument(
        "--topology",
        type=str,
        default="chain",
        choices=["isolated", "chain", "ring", "fully_connected"],
        help="Inter-triad coupling topology (network mode only).",
    )
    parser.add_argument("--inter-strength", type=float, default=0.08, help="Inter-triad coupling strength (network mode only).")
    parser.add_argument("--intra-strength", type=float, default=1.0, help="Intra-triad mixing strength (network mode only).")
    parser.add_argument("--asymmetry", type=float, default=0.03, help="Asymmetry strength (network mode only). 0 disables.")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed (network mode only).")
    parser.add_argument("--delay-steps", type=int, default=1, help="Feedback/coupling delay in steps (network mode only).")
    parser.add_argument(
        "--per-triad-windows",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable per-triad window offsets (network mode only).",
    )
    parser.add_argument("--save-npz", type=str, default="", help="Write NPZ timeseries to this path (network mode only).")
    parser.add_argument("--persistence-eps", type=float, default=1e-3, help="Epsilon for persistence_score (network mode only).")
    parser.add_argument("--collapse-eps", type=float, default=1e-2, help="Std threshold for collapse_count (network mode only).")
    parser.add_argument(
        "--experiment",
        type=str,
        default="",
        choices=["", "open_to_closed_loop"],
        help="Run a predefined experiment (network mode only).",
    )
    parser.add_argument("--plot-prefix", type=str, default="", help="Write per-stage PNGs with this prefix (experiment only).")
    parser.add_argument("--npz-prefix", type=str, default="", help="Write per-stage NPZs with this prefix (experiment only).")

    args = parser.parse_args()

    steps = int(args.steps)
    dt = float(args.dt)
    if steps <= 1 or dt <= 0:
        raise SystemExit("--steps must be >1 and --dt must be >0")

    led_a = parse_pattern(args.pattern_a, steps=steps, dt=dt)
    led_b = parse_pattern(args.pattern_b, steps=steps, dt=dt)
    params0 = build_default_params(args.mix, feedback_strength=float(args.feedback_strength))
    params = OpticalReservoirParams(
        W=params0.W,
        ambient=float(args.ambient),
        rc_tau=float(args.rc_tau),
        rc_decay=float(args.memory_decay) if args.memory_decay is not None else None,
        out_tau=float(args.out_tau),
        out_level=float(args.out_level),
        window_low=float(args.window_low),
        window_high=float(args.window_high),
        hysteresis=float(args.hysteresis),
        light_decay=float(args.light_decay),
        sensor_noise_std=float(args.noise),
        sensor_nonlinearity=float(args.sensor_nonlinearity),
        opamp_gain=float(args.opamp_gain),
        opamp_sat=float(args.opamp_sat),
        common_mode_gain=float(args.common_mode_gain),
        extra_state_gain=float(args.extra_state_gain),
        extra_leak_tau=float(args.extra_tau),
    )

    if args.network_mode == "legacy":
        sim = simulate(
            steps=steps,
            dt=dt,
            led_a=led_a,
            led_b=led_b,
            feedback_enable=bool(args.feedback),
            params=params,
        )

        # Basic numeric summary (no plotting required) - keep legacy style
        state = sim["rc"] + sim["extra"]
        below = float(np.mean(state < params.window_low))
        above = float(np.mean(state > params.window_high))
        inside = float(np.mean((state >= params.window_low) & (state <= params.window_high)))
        comp_rate = float(np.mean(sim["comp"]))
        out_mean = float(np.mean(sim["out_led"]))
        out_std = float(np.std(sim["out_led"]))
        print(
            " ".join(
                [
                    f"inside_rate={inside:.3f}",
                    f"below_rate={below:.3f}",
                    f"above_rate={above:.3f}",
                    f"comp_on_rate={comp_rate:.3f}",
                    f"out_mean={out_mean:.3f}",
                    f"out_std={out_std:.3f}",
                    f"feedback={args.feedback}",
                ]
            )
        )

        if args.plot:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            t = sim["t"]
            fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

            axes[0].plot(t, sim["led_a"], label="LED_A")
            axes[0].plot(t, sim["led_b"], label="LED_B")
            axes[0].plot(t, sim["out_led"], label="LED_OUT")
            axes[0].set_ylabel("LED")
            axes[0].legend(loc="upper right")

            axes[1].plot(t, sim["sensors"][:, 0], label="S0")
            axes[1].plot(t, sim["sensors"][:, 1], label="S1")
            axes[1].plot(t, sim["sensors"][:, 2], label="S2")
            axes[1].set_ylabel("Sensors")
            axes[1].legend(loc="upper right")

            axes[2].plot(t, sim["rc"], label="RC")
            axes[2].plot(t, sim["rc"] + sim["extra"], label="RC+extra", alpha=0.7)
            axes[2].axhline(params.window_low, color="k", linewidth=1, alpha=0.3)
            axes[2].axhline(params.window_high, color="k", linewidth=1, alpha=0.3)
            axes[2].set_ylabel("State")
            axes[2].legend(loc="upper right")

            axes[3].step(t, sim["comp"], label="Comparator", where="post")
            axes[3].set_ylabel("Comp")
            axes[3].set_xlabel("t (s)")
            axes[3].set_ylim(-0.1, 1.1)

            fig.tight_layout()
            fig.savefig(args.plot, dpi=160)
            print(f"Wrote {args.plot}")
        return 0

    # Network mode (JSON summary + optional NPZ/PNG)
    triads = int(args.triads)
    if triads <= 0:
        raise SystemExit("--triads must be >= 1")

    led_inputs = np.zeros((steps, triads, 3), dtype=float)
    led_inputs[:, :, 0] = led_a[:, None]
    led_inputs[:, :, 1] = led_b[:, None]

    persistence_eps = float(args.persistence_eps)
    collapse_eps = float(args.collapse_eps)

    net = TriadNetworkParams(
        triads=triads,
        topology=str(args.topology),
        intra_strength=float(args.intra_strength),
        inter_strength=float(args.inter_strength),
        asymmetry=float(args.asymmetry),
        seed=int(args.seed),
        per_triad_windows=bool(args.per_triad_windows),
        delay_steps=int(args.delay_steps),
    )

    if args.experiment == "open_to_closed_loop":
        results = run_open_to_closed_loop_experiment(
            steps=steps,
            dt=dt,
            led_a=led_a,
            led_b=led_b,
            triads=triads,
            topology=str(args.topology),
            params=params,
            base_net=net,
            persistence_eps=persistence_eps,
            collapse_eps=collapse_eps,
            plot_prefix=str(args.plot_prefix),
            save_npz_prefix=str(args.npz_prefix),
        )
        for row in results:
            print(json.dumps(row, separators=(",", ":"), sort_keys=False))
        return 0

    simn = simulate_triad_network(
        steps=steps,
        dt=dt,
        led_inputs=led_inputs,
        feedback_enable=bool(args.feedback),
        base_params=params,
        net=net,
    )

    state = simn["rc"] + simn["extra"]  # (steps,triads,3)
    state_scalar = np.mean(state, axis=2)  # (steps,triads)
    below = state_scalar < simn["win_low"][None, :]
    above = state_scalar > simn["win_high"][None, :]
    inside = (~below) & (~above)

    per_inside = inside.mean(axis=0)
    per_below = below.mean(axis=0)
    per_above = above.mean(axis=0)
    per_comp = simn["comp"].mean(axis=0)
    out = simn["out_led"]
    per_out_mean = out.mean(axis=(0, 2))
    per_out_std = out.std(axis=(0, 2))

    # Correlation / synchronization metrics
    # Use mean output intensity per triad as a 1D signal.
    out_mean_t = out.mean(axis=2)  # (steps,triads)
    delta_out = np.diff(out_mean_t, axis=0)  # (steps-1,triads)
    mean_pairwise_corr = _mean_pairwise_corr(out_mean_t)
    mean_pairwise_delta_corr = _mean_pairwise_corr(delta_out)
    sync_index = abs(mean_pairwise_delta_corr)
    # Persistence should track residue/history, not LED smoothing.
    net_state_t = np.mean(state_scalar, axis=1)  # (steps,)
    persistence = float(np.mean(np.abs(np.diff(net_state_t)) < persistence_eps))
    collapse_count = int(np.sum(np.std(out_mean_t, axis=0) < collapse_eps))

    summary = {
        "mode": "triad_network",
        "triads": triads,
        "topology": net.topology,
        "params": {
            "intra_strength": net.intra_strength,
            "inter_strength": net.inter_strength,
            "asymmetry": net.asymmetry,
            "feedback": bool(args.feedback),
            "light_decay": params.light_decay,
            "memory_decay": params.rc_decay,
            "window_low": params.window_low,
            "window_high": params.window_high,
            "persistence_eps": persistence_eps,
            "collapse_eps": collapse_eps,
        },
        "per_triad": [
            {
                "triad": int(k),
                "inside_rate": float(per_inside[k]),
                "below_rate": float(per_below[k]),
                "above_rate": float(per_above[k]),
                "comp_on_rate": float(per_comp[k]),
                "out_mean": float(per_out_mean[k]),
                "out_std": float(per_out_std[k]),
                "oscillation_score": float(np.mean(np.abs(np.diff(out_mean_t[:, k])))),
            }
            for k in range(triads)
        ],
        "network": {
            "global_inside_rate": float(inside.mean()),
            "global_failure_rate": float(below.mean()),
            "global_saturation_rate": float(above.mean()),
            "mean_pairwise_correlation": mean_pairwise_corr,
            "mean_pairwise_delta_correlation": mean_pairwise_delta_corr,
            "synchronization_index": sync_index,
            "persistence_score": persistence,
            "collapse_count": collapse_count,
        },
    }
    print(json.dumps(summary, separators=(",", ":"), sort_keys=False))

    if args.save_npz:
        np.savez_compressed(
            args.save_npz,
            t=simn["t"],
            led_inputs=simn["led_inputs"],
            topology=simn["topology"],
            sensors=simn["sensors"],
            surface=simn["surface"],
            opamp=simn["opamp"],
            rc=simn["rc"],
            extra=simn["extra"],
            comp=simn["comp"],
            out_led=simn["out_led"],
            win_low=simn["win_low"],
            win_high=simn["win_high"],
        )

    if args.plot:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        t = simn["t"]
        fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
        axes[0].plot(t, out_mean_t, linewidth=1)
        axes[0].set_ylabel("out_mean(t)")
        axes[0].set_title(f"Triad outputs (n={triads}, topology={net.topology})")

        axes[1].step(t, simn["comp"], where="post")
        axes[1].set_ylabel("comp")
        axes[1].set_ylim(-0.1, 1.1)

        axes[2].plot(t, state_scalar, linewidth=1)
        axes[2].set_ylabel("state")

        axes[3].plot(t, inside.mean(axis=1), label="inside_rate(t)")
        axes[3].plot(t, below.mean(axis=1), label="below_rate(t)")
        axes[3].plot(t, above.mean(axis=1), label="above_rate(t)")
        axes[3].set_ylabel("collapse")
        axes[3].set_xlabel("t (s)")
        axes[3].legend(loc="upper right")

        fig.tight_layout()
        fig.savefig(args.plot, dpi=160)
        print(f"Wrote {args.plot}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
