"""Command-line interface for the linac simulator."""

from __future__ import annotations

import argparse
from pathlib import Path

from .simulation import config_from_args, run_simulation, write_result
from .validation import run_validation


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m linac_sim",
        description="Research-oriented 1D linear particle accelerator simulation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="run a linac simulation")
    run_parser.add_argument("--output", type=Path, default=Path("outputs/default_run"))
    run_parser.add_argument("--species", choices=["proton", "electron"], default="proton")
    run_parser.add_argument("--particles", type=int, default=500)
    run_parser.add_argument("--seed", type=int, default=12345)
    run_parser.add_argument("--initial-energy-ev", type=float, default=1_000_000.0)
    run_parser.add_argument("--energy-spread-fraction", type=float, default=0.01)
    run_parser.add_argument("--bunch-length-m", type=float, default=0.002)
    run_parser.add_argument("--transverse-size-m", type=float, default=0.001)
    run_parser.add_argument("--transverse-divergence-rad", type=float, default=0.001)
    run_parser.add_argument("--z-transverse-size-m", type=float, default=0.001)
    run_parser.add_argument("--z-transverse-divergence-rad", type=float, default=0.001)
    run_parser.add_argument("--aperture-radius-m", type=float, default=0.01)
    run_parser.add_argument("--gaps", type=int, default=20)
    run_parser.add_argument("--drift-length-m", type=float, default=0.04)
    run_parser.add_argument("--gap-length-m", type=float, default=0.01)
    run_parser.add_argument("--peak-field", type=float, default=2.0e6)
    run_parser.add_argument("--frequency", type=float, default=200.0e6)
    run_parser.add_argument("--phase", type=float, default=1.5707963267948966)
    run_parser.add_argument("--focusing-strength", type=float, default=25.0)
    run_parser.add_argument("--z-focusing-strength", type=float, default=25.0)
    run_parser.add_argument("--lens-length-m", type=float, default=0.005)
    run_parser.add_argument("--dt", type=float, default=2.0e-12)
    run_parser.add_argument("--max-time", type=float, default=1.0e-7)
    run_parser.add_argument("--history-interval", type=int, default=25)

    subparsers.add_parser("validate", help="run validation checks")

    args = parser.parse_args()
    if args.command is None:
        args = parser.parse_args(["run"])

    if args.command == "validate":
        checks = run_validation()
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"{status} {check.name}: {check.detail}")
        return 0 if all(check.passed for check in checks) else 1

    if args.command == "run":
        config = config_from_args(args)
        result = run_simulation(config)
        plots_written = write_result(result, args.output)
        print(f"output_dir={args.output}")
        print(f"active_count={result.final_summary['active_count']}")
        print(f"transmission_fraction={result.final_summary['transmission_fraction']:.6f}")
        print(f"mean_energy_ev={result.final_summary['mean_energy_ev']:.6f}")
        print(f"rms_energy_spread_ev={result.final_summary['rms_energy_spread_ev']:.6f}")
        print(f"normalized_emittance_m_rad={result.final_summary['normalized_emittance_m_rad']:.6e}")
        print(f"z_normalized_emittance_m_rad={result.final_summary['z_normalized_emittance_m_rad']:.6e}")
        print(f"rms_beam_size_m={result.final_summary['rms_beam_size_m']:.6e}")
        print(f"rms_z_beam_size_m={result.final_summary['rms_z_beam_size_m']:.6e}")
        print(f"rms_radial_beam_size_m={result.final_summary['rms_radial_beam_size_m']:.6e}")
        print(f"plots_written={plots_written}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
