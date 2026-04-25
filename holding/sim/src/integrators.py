from __future__ import annotations

from typing import Callable


State = tuple[float, float, float]
RhsFunction = Callable[[State], State]


def euler_step(rhs: RhsFunction, state: State, dt: float) -> State:
    slope = rhs(state)
    return tuple(value + dt * deriv for value, deriv in zip(state, slope))


def rk4_step(rhs: RhsFunction, state: State, dt: float) -> State:
    k1 = rhs(state)
    k2 = rhs(tuple(value + 0.5 * dt * deriv for value, deriv in zip(state, k1)))
    k3 = rhs(tuple(value + 0.5 * dt * deriv for value, deriv in zip(state, k2)))
    k4 = rhs(tuple(value + dt * deriv for value, deriv in zip(state, k3)))
    return tuple(
        value + (dt / 6.0) * (d1 + 2.0 * d2 + 2.0 * d3 + d4)
        for value, d1, d2, d3, d4 in zip(state, k1, k2, k3, k4)
    )
