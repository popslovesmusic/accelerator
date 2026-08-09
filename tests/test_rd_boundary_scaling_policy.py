import numpy as np
import pytest
from rd_moving_boundary_sim_v1.rd_engine import RDEngine

@pytest.fixture
def base_config():
    return {
        "grid_size": 10,
        "dt": 0.01,
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

def test_periodic_boundary_default_is_exposed(base_config):
    engine = RDEngine(base_config)
    assert hasattr(engine, 'boundary_mode')
    assert engine.boundary_mode == 'periodic'

def test_unit_grid_scaling_default_is_exposed(base_config):
    engine = RDEngine(base_config)
    assert hasattr(engine, 'dx')
    assert hasattr(engine, 'dy')
    assert engine.dx == 1.0
    assert engine.dy == 1.0

def test_legacy_behavior_preserved(base_config):
    # Create engine with defaults
    engine_default = RDEngine(base_config)
    
    # Create engine with explicit legacy values
    config_explicit = base_config.copy()
    config_explicit['boundary_mode'] = 'periodic'
    config_explicit['dx'] = 1.0
    config_explicit['dy'] = 1.0
    engine_explicit = RDEngine(config_explicit)
    
    # Run one step
    engine_default.step()
    engine_explicit.step()
    
    # Check that results are identical
    np.testing.assert_array_equal(engine_default.D, engine_explicit.D)
    np.testing.assert_array_equal(engine_default.S, engine_explicit.S)

def test_explicit_config_override(base_config):
    config = base_config.copy()
    config['boundary_mode'] = 'periodic' # currently only supported
    config['dx'] = 2.0
    config['dy'] = 0.5
    
    engine = RDEngine(config)
    assert engine.dx == 2.0
    assert engine.dy == 0.5
