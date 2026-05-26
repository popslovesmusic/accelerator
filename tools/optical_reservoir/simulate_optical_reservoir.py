import argparse
import json
import math
import os
from dataclasses import dataclass

import numpy as np


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def _clip01(x: np.ndarray | float) -> np.ndarray | float:
    return np.clip(x, 0.0, 1.0)


def parse_pattern(pattern: str, steps: int, dt: float) -> np.ndarray:
    if ":" not in pattern:
        raise ValueError(f"Bad pattern '{pattern}'. Expected kind:args")
    kind, rest = pattern.split(":", 1)
    t = np.arange(steps) * dt

    if kind == "const":
        v = float(rest)
        return np.full(steps, v, dtype=float)

    if kind == "pulse":
        t0_s, t1_s, v_s = rest.split(":")
        t0, t1, v = float(t0_s), float(t1_s), float(v_s)
        out = np.zeros(steps, dtype=float)
        out[(t >= t0) & (t < t1)] = v
        return out

    if kind == "blink":
        period_s, duty_s, v_s = rest.split(":")
        period, duty, v = float(period_s), float(duty_s), float(v_s)
        phase = np.mod(t, period) / period
        return np.where(phase < duty, v, 0.0).astype(float)

    if kind == "sine":
        freq_s, amp_s, bias_s = rest.split(":")
        freq, amp, bias = float(freq_s), float(amp_s), float(bias_s)
        return (bias + amp * np.sin(2 * math.pi * freq * t)).astype(float)

    if kind == "randbits":
        period_s, v_s = rest.split(":")
        period, v = float(period_s), float(v_s)
        samples_per = max(1, int(round(period / dt)))
        rng = np.random.default_rng(0)
        bits = rng.integers(0, 2, size=int(math.ceil(steps / samples_per)))
        return np.repeat(bits.astype(float) * v, samples_per)[:steps]

    if kind == "list":
        values = [float(x.strip()) for x in rest.split(",") if x.strip() != ""]
        if not values: raise ValueError("list: needs at least one value")
        reps = int(math.ceil(steps / len(values)))
        return np.tile(np.array(values, dtype=float), reps)[:steps]

    raise ValueError(f"Unknown pattern kind '{kind}'")


@dataclass(frozen=True)
class OpticalReservoirParams:
    W: np.ndarray
    ambient: float = 0.02
    sensor_nonlinearity: float = 1.0
    sensor_noise_std: float = 0.0
    light_decay: float = 0.0
    opamp_gain: float = 8.0
    opamp_bias: float = 0.0
    opamp_sat: float = 1.0
    common_mode_gain: float = 0.0
    rc_tau: float = 0.10
    rc_decay: float | None = None
    window_low: float = 0.35
    window_high: float = 0.70
    hysteresis: float = 0.03
    out_tau: float = 0.05
    out_level: float = 1.0
    extra_leak_tau: float = 0.25
    extra_state_gain: float = 0.0
    admissibility_adapt_rate: float = 0.0
    residue_diffusion_rate: float = 0.0


@dataclass(frozen=True)
class TriadNetworkParams:
    triads: int = 1
    topology: str = "chain"
    intra_strength: float = 1.0
    inter_strength: float = 0.08
    asymmetry: float = 0.03
    seed: int = 0
    per_triad_windows: bool = True
    delay_steps: int = 1
    topology_rewire_rate: float = 0.0


def build_topology_matrix(triad_count: int, topology: str, inter_strength: float) -> np.ndarray:
    n, s = int(triad_count), float(inter_strength)
    T = np.zeros((n, n), dtype=float)
    if topology == "isolated" or s == 0.0: return T
    if topology == "chain":
        for k in range(n):
            if k - 1 >= 0: T[k, k - 1] = s
            if k + 1 < n: T[k, k + 1] = s
        return T
    if topology == "ring":
        for k in range(n):
            T[k, (k - 1) % n], T[k, (k + 1) % n] = s, s
        return T
    if topology == "fully_connected":
        for k in range(n):
            for j in range(n):
                if k != j: T[k, j] = s / max(1, (n - 1))
        return T
    raise ValueError(f"Unknown topology '{topology}'")


def _orientation_readout_3(sensor_field: np.ndarray) -> np.ndarray:
    s0, s1, s2 = sensor_field[..., 0], sensor_field[..., 1], sensor_field[..., 2]
    return np.stack([s0 - s1, s1 - s2, s2 - s0], axis=-1)


def _mean_pairwise_corr(X: np.ndarray) -> float:
    T, N = X.shape
    if N < 2: return 1.0
    Xc = X - X.mean(axis=0, keepdims=True)
    std = Xc.std(axis=0, ddof=1, keepdims=True)
    good = (std[0] > 1e-12)
    if np.sum(good) < 2: return 0.0
    Xn = np.zeros_like(Xc)
    Xn[:, good] = Xc[:, good] / std[:, good]
    corr = (Xn.T @ Xn) / max(1, (T - 1))
    iu = np.triu_indices(N, k=1)
    vals = corr[iu]
    mask = good[iu[0]] & good[iu[1]]
    if not np.any(mask): return 0.0
    return float(np.mean(vals[mask]))


def simulate_triad_network(
    *, steps: int, dt: float, led_inputs: np.ndarray, feedback_enable: bool,
    base_params: OpticalReservoirParams, net: TriadNetworkParams
) -> dict[str, np.ndarray]:
    triads = int(net.triads)
    rng = np.random.default_rng(int(net.seed))

    intra_base = float(net.intra_strength) * (np.eye(3) + 0.1 * rng.standard_normal((3, 3)))
    intra = np.repeat(intra_base[None, :, :], triads, axis=0)
    if net.asymmetry > 0.0:
        intra += rng.normal(0.0, float(net.asymmetry), size=intra.shape)
        intra = np.maximum(intra, 0.0)

    sensor_bias = rng.normal(0.0, float(net.asymmetry), size=(triads, 3))
    triad_gain = 1.0 + rng.normal(0.0, float(net.asymmetry), size=(triads, 1))

    T = build_topology_matrix(triads, net.topology, float(net.inter_strength))
    if net.asymmetry > 0.0 and triads > 1:
        T = np.maximum(0.0, T + rng.normal(0.0, float(net.asymmetry), size=T.shape))
        np.fill_diagonal(T, 0.0)

    out_led, sensors, surface = np.zeros((steps, triads, 3)), np.zeros((steps, triads, 3)), np.zeros((steps, triads, 3))
    opamp, rc, extra, comp = np.zeros((steps, triads, 3)), np.zeros((steps, triads, 3)), np.zeros((steps, triads, 3)), np.zeros((steps, triads))

    a_rc = math.exp(-dt / max(1e-9, base_params.rc_tau)) if base_params.rc_decay is None else float(base_params.rc_decay)
    a_out, a_extra = math.exp(-dt / max(1e-9, base_params.out_tau)), math.exp(-dt / max(1e-9, base_params.extra_leak_tau))
    a_light = float(np.clip(base_params.light_decay, 0.0, 1.0))

    win_low, win_high = np.full(triads, float(base_params.window_low)), np.full(triads, float(base_params.window_high))
    last_comp = np.zeros(triads)

    for i in range(steps):
        if base_params.admissibility_adapt_rate > 0.0:
            target_high = np.where(last_comp > 0.5, 1.0, float(base_params.window_high))
            win_high += (target_high - win_high) * float(base_params.admissibility_adapt_rate) * dt
            win_high = np.clip(win_high, 0.0, 1.0)

        if net.topology_rewire_rate > 0.0 and triads > 1:
            T += (last_comp[:, None] * last_comp[None, :] * float(net.topology_rewire_rate) * dt)
            T *= (1.0 - 0.005 * dt)
            np.fill_diagonal(T, 0.0)

        out_prev = out_led[i-1] if i > 0 else np.zeros((triads, 3))
        neighbor_drive = T @ out_prev
        local_leds = led_inputs[i].copy()
        if feedback_enable: local_leds += out_prev
        total_leds = _clip01(local_leds + neighbor_drive)

        drive = np.einsum("kij,kj->ki", intra, total_leds) + float(base_params.ambient)
        drive = np.maximum(drive + sensor_bias, 0.0)
        if base_params.sensor_nonlinearity != 1.0: drive = drive ** float(base_params.sensor_nonlinearity)

        if base_params.light_decay > 0.0:
            prev_field = surface[i-1] if i > 0 else np.zeros((triads, 3))
            field = a_light * prev_field + (1.0 - a_light) * drive
        else: field = drive
        surface[i] = field

        raw = field
        if base_params.sensor_noise_std > 0.0:
            raw += rng.normal(0.0, float(base_params.sensor_noise_std), size=raw.shape)
        sensors[i] = raw

        diff_vec = _orientation_readout_3(raw)
        if base_params.common_mode_gain != 0.0:
            diff_vec += float(base_params.common_mode_gain) * np.mean(raw, axis=1, keepdims=True)
        v = _sigmoid(float(base_params.opamp_gain) * (diff_vec * triad_gain) + float(base_params.opamp_bias))
        opamp[i] = v

        rc_prev = rc[i-1] if i > 0 else np.zeros((triads, 3))
        rc_i = a_rc * rc_prev + (1.0 - a_rc) * v
        if base_params.residue_diffusion_rate > 0.0 and triads > 1:
            rc_i += ((T @ rc_i) - (np.sum(T, axis=1, keepdims=True) * rc_i)) * float(base_params.residue_diffusion_rate)
        rc[i] = rc_i

        extra_prev = extra[i-1] if i > 0 else np.zeros((triads, 3))
        extra_i = a_extra * extra_prev + (1.0 - a_extra) * (float(base_params.extra_state_gain) * rc_i)
        extra[i] = extra_i

        state_scalar = np.mean(rc_i + extra_i, axis=1)
        low, high = win_low - (float(base_params.hysteresis) * (last_comp > 0.5)), win_high + (float(base_params.hysteresis) * (last_comp < 0.5))
        within = ((state_scalar >= low) & (state_scalar <= high)).astype(float)
        comp[i], last_comp = within, within
        out_led[i] = a_out * out_prev + (1.0 - a_out) * (within[:, None] * float(base_params.out_level))

    return {"t": np.arange(steps) * dt, "led_inputs": led_inputs, "topology": T, "sensors": sensors, "surface": surface, "opamp": opamp, "rc": rc, "extra": extra, "comp": comp, "out_led": out_led, "win_low": win_low, "win_high": win_high}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--pattern-a", type=str, default="const:0.5")
    parser.add_argument("--pattern-b", type=str, default="const:0.5")
    parser.add_argument("--feedback", action="store_true")
    parser.add_argument("--window-low", type=float, default=0.35)
    parser.add_argument("--window-high", type=float, default=0.70)
    parser.add_argument("--opamp-gain", type=float, default=8.0)
    parser.add_argument("--rc-tau", type=float, default=0.1)
    parser.add_argument("--memory-decay", type=float)
    parser.add_argument("--out-level", type=float, default=1.0)
    parser.add_argument("--ambient", type=float, default=0.02)
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--network-mode", type=str, default="triad_network")
    parser.add_argument("--triads", type=int, default=1)
    parser.add_argument("--topology", type=str, default="chain")
    parser.add_argument("--inter-strength", type=float, default=0.08)
    parser.add_argument("--intra-strength", type=float, default=1.0)
    parser.add_argument("--asymmetry", type=float, default=0.03)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--persistence-eps", type=float, default=1e-3)
    parser.add_argument("--topology-rewire-rate", type=float, default=0.0)
    parser.add_argument("--admissibility-adapt-rate", type=float, default=0.0)
    parser.add_argument("--residue-diffusion-rate", type=float, default=0.0)

    args, _ = parser.parse_known_args()
    steps, dt = int(args.steps), float(args.dt)
    led_a, led_b = parse_pattern(args.pattern_a, steps, dt), parse_pattern(args.pattern_b, steps, dt)
    params = OpticalReservoirParams(W=np.eye(3), ambient=args.ambient, rc_tau=args.rc_tau, rc_decay=args.memory_decay, window_low=args.window_low, window_high=args.window_high, out_level=args.out_level, sensor_noise_std=args.noise, opamp_gain=args.opamp_gain, admissibility_adapt_rate=args.admissibility_adapt_rate, residue_diffusion_rate=args.residue_diffusion_rate)
    net = TriadNetworkParams(triads=int(args.triads), topology=args.topology, intra_strength=args.intra_strength, inter_strength=args.inter_strength, asymmetry=args.asymmetry, seed=args.seed, topology_rewire_rate=args.topology_rewire_rate)
    
    simn = simulate_triad_network(steps=steps, dt=dt, led_inputs=np.stack([led_a, led_b, np.zeros(steps)], axis=-1)[:, None, :].repeat(int(args.triads), axis=1), feedback_enable=bool(args.feedback), base_params=params, net=net)
    
    state_scalar = np.mean(simn["rc"] + simn["extra"], axis=2)
    inside = (state_scalar >= simn["win_low"][None, :]) & (state_scalar <= simn["win_high"][None, :])
    orientations = _orientation_readout_3(simn["sensors"])[..., 0] # Use only one component for ordering
    ordering_metric = float(np.abs(orientations.mean()))
    hist, _ = np.histogram(orientations.flatten(), bins=20, range=(-1, 1))
    p = hist / (hist.sum() + 1e-12)
    summary = {"mode": "triad_network", "triads": int(args.triads), "network": {"global_inside_rate": float(inside.mean()), "synchronization_index": float(abs(_mean_pairwise_corr(np.diff(simn["out_led"].mean(axis=2), axis=0)))), "persistence_score": float(np.mean(np.abs(np.diff(state_scalar.mean(axis=1))) < float(args.persistence_eps))), "global_ordering_metric": ordering_metric, "global_orientation_entropy": float(-np.sum(p[p>0]*np.log2(p[p>0])))}}
    print(json.dumps(summary, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    main()
