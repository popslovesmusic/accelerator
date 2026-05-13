import os
import json
import pytest
import subprocess
import shutil

@pytest.fixture
def temp_dir():
    path = "temp_rd_test_dir"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

def test_rd_moving_boundary_short_runs_do_not_crash(temp_dir):
    config = {
        "grid_size": 10,
        "dt": 0.01,
        "steps": 0,
        "seed": 42,
        "D_diff": 0.1,
        "S_diff": 0.2,
        "beta": 1.0,
        "growth_thresh": 0.5,
        "domain_decay": 0.01,
        "signal_decay": 0.01,
        "source_pos": [5, 5],
        "source_radius": 2,
        "source_strength": 1.0
    }
    
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f)
        
    output_dir = os.path.join(temp_dir, "output")
    
    # Try steps=0
    config["steps"] = 0
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    python_cmd = ".venv\\Scripts\\python.exe"
    if not os.path.exists(python_cmd):
        python_cmd = "python"
        
    result = subprocess.run([python_cmd, "tools/rd_moving_boundary_sim_v1/sim.py", "--config", config_path, "--out", output_dir], capture_output=True, text=True)
    assert result.returncode == 0
    
    # Try steps=1
    config["steps"] = 1
    with open(config_path, "w") as f:
        json.dump(config, f)
    result = subprocess.run([python_cmd, "tools/rd_moving_boundary_sim_v1/sim.py", "--config", config_path, "--out", output_dir], capture_output=True, text=True)
    assert result.returncode == 0

    # Try steps=9
    config["steps"] = 9
    with open(config_path, "w") as f:
        json.dump(config, f)
    result = subprocess.run([python_cmd, "tools/rd_moving_boundary_sim_v1/sim.py", "--config", config_path, "--out", output_dir], capture_output=True, text=True)
    assert result.returncode == 0

    # Try steps=10 (first history append)
    config["steps"] = 10
    with open(config_path, "w") as f:
        json.dump(config, f)
    result = subprocess.run([python_cmd, "tools/rd_moving_boundary_sim_v1/sim.py", "--config", config_path, "--out", output_dir], capture_output=True, text=True)
    assert result.returncode == 0
