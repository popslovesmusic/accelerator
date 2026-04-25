from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OdeParameters:
    k: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float
    v: float
    s: float
    h: float
    kappa: float
    lambda_: float

    @classmethod
    def from_dict(cls, data: dict) -> "OdeParameters":
        return cls(
            k=float(data["k"]),
            b=float(data["b"]),
            c=float(data["c"]),
            alpha=float(data["alpha"]),
            beta=float(data["beta"]),
            gamma=float(data["gamma"]),
            v=float(data["v"]),
            s=float(data["s"]),
            h=float(data["h"]),
            kappa=float(data["kappa"]),
            lambda_=float(data["lambda"]),
        )


def ode_rhs(state: tuple[float, float, float], params: OdeParameters) -> tuple[float, float, float]:
    epsilon, rho, residue = state
    d_epsilon = params.k * epsilon - params.b * epsilon * rho - params.c * epsilon * epsilon + params.s
    d_rho = params.alpha * rho - params.beta * epsilon * rho - params.gamma * rho * rho - params.v * residue + params.h
    d_residue = params.kappa * epsilon - params.lambda_ * residue
    return d_epsilon, d_rho, d_residue
