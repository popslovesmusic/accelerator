import os
import json
import pytest
import numpy as np
from tools.structural_box_sim_v2.sim import GridConfig, ModelConfig, RunConfig, BoxConfig, InitialConditionConfig, simulate

def test_stable_small_dt_case_runs():
    grid = GridConfig(nx=32, dt=1e-5, t_final=0.001)
    model = ModelConfig(D_epsilon=1e-4, D_rho=1e-4, D_R=1e-4)
    # dx = 1/32 = 0.03125
    # dx^2 / (2*D) = (0.03125)^2 / (2e-4) = 0.0009765625 / 2e-4 = 4.88
    # dt=1e-5 is well below the limit
    
    config = RunConfig(
        grid=grid,
        model=model,
        initial_condition=InitialConditionConfig(),
        box=BoxConfig(),
        output_dir="temp_test_stable"
    )
    
    result = simulate(config)
    assert len(result["stability_warnings"]) == 0
    assert result["diagnostics"][-1]["within_box"] is True

def test_large_dt_warns_diffusion():
    # dx = 1/32 = 0.03125
    # dx^2 / (2*D) = 4.88
    # If D is large, e.g. D=10.0
    # dx^2 / (2*D) = 0.0009765625 / 20 = 4.88e-5
    # dt = 1e-4 will be larger than cfl limit
    
    grid = GridConfig(nx=32, dt=1e-4, t_final=0.0002)
    model = ModelConfig(D_epsilon=10.0)
    
    config = RunConfig(
        grid=grid,
        model=model,
        initial_condition=InitialConditionConfig(),
        box=BoxConfig(),
        output_dir="temp_test_unstable_diffusion"
    )
    
    result = simulate(config)
    assert any("diffusion stability limit" in w for w in result["stability_warnings"])

def test_large_dt_warns_stiffness():
    # dt * max_coeff > 0.1
    # if a = 2.0, dt = 0.1, dt*a = 0.2
    grid = GridConfig(nx=32, dt=0.1, t_final=0.2)
    model = ModelConfig(a=2.0)
    
    config = RunConfig(
        grid=grid,
        model=model,
        initial_condition=InitialConditionConfig(),
        box=BoxConfig(),
        output_dir="temp_test_unstable_stiffness"
    )
    
    result = simulate(config)
    assert any("Stiffness risk detected" in w for w in result["stability_warnings"])

def test_clamp_not_marked_as_stability_proof():
    policy_path = "docs/math/structural_box_euler_stability_policy.md"
    with open(policy_path, "r") as f:
        content = f.read().lower()
    assert "clamping" in content
    assert "not" in content
    assert "numerical stability proof" in content
    assert "mask underlying instabilities" in content
