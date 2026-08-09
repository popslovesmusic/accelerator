"""
FAT-04-REGIME-BOUNDARY-1.2.2b.6: Falsification Attack on L/NL Regime Boundary and Transition
Principle: Operational regimes transition from L to NL when residue feedback deforms local composition.
Objective: Attempt to construct a process that accumulates high residue feedback (R_t >> 0, k > 0)
but remains strictly linear and composable (low fitting error under a linear operator representation),
which would falsify the boundary and transition definition.
"""

import sys
import random
import math

def simulate_regime(feedback_coef, steps=100):
    """
    Simulates a 2D process state S = [x, y] undergoing updates dS = [dx, dy]
    with residue R accumulating and feeding back into the composition rule.
    """
    random.seed(42)
    state = [1.0, 1.0]
    residue = 0.0
    
    # Store histories to fit a linear model: actual_updates vs. input_perturbations
    inputs = []
    actual_updates = []
    
    for _ in range(steps):
        # Generate random inputs (perturbations)
        dx = random.uniform(-0.1, 0.1)
        dy = random.uniform(-0.1, 0.1)
        
        # Additive residue feedback deforms the composition rule:
        # S_next = S + dS + k * R * sin(S)
        dx_actual = dx + feedback_coef * residue * math.sin(state[0])
        dy_actual = dy + feedback_coef * residue * math.cos(state[1])
        
        next_state = [state[0] + dx_actual, state[1] + dy_actual]
        
        # Accumulate residue
        residue += 0.1 * (abs(dx_actual) + abs(dy_actual))
        
        inputs.append((dx, dy))
        actual_updates.append((dx_actual, dy_actual))
        
        state = next_state
        
    return inputs, actual_updates

def fit_linear_operator(inputs, actual_updates):
    """
    Fits a linear operator M such that actual_update = M * input + intercept.
    Computes the coefficient of determination (R2 score) in pure Python.
    """
    dxs = [inp[0] for inp in inputs]
    dys = [inp[1] for inp in inputs]
    dx_actuals = [act[0] for act in actual_updates]
    dy_actuals = [act[1] for act in actual_updates]
    
    def fit_single_dim(xs, ys):
        # Fit y = w*x + b
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        
        sum_xx = sum((x - mean_x)**2 for x in xs)
        sum_xy = sum((x - mean_x)*(y - mean_y) for x, y in zip(xs, ys))
        
        if sum_xx == 0:
            return 0.0, mean_y
        slope = sum_xy / sum_xx
        intercept = mean_y - slope * mean_x
        return slope, intercept

    slope_x, int_x = fit_single_dim(dxs, dx_actuals)
    slope_y, int_y = fit_single_dim(dys, dy_actuals)
    
    def compute_r2(xs, ys, slope, intercept):
        mean_y = sum(ys) / len(ys)
        ss_tot = sum((y - mean_y)**2 for y in ys)
        if ss_tot == 0:
            return 1.0
        ss_res = sum((y - (slope*x + intercept))**2 for x, y in zip(xs, ys))
        return 1.0 - (ss_res / ss_tot)

    r2_x = compute_r2(dxs, dx_actuals, slope_x, int_x)
    r2_y = compute_r2(dys, dy_actuals, slope_y, int_y)
    return (r2_x + r2_y) / 2.0

def run_attack():
    print("====================================================")
    print("FAT-04-REGIME-BOUNDARY-1.2.2b.6: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: L/NL Regime Boundary and Transition")
    print("====================================================")
    
    # Scenario A: Zero Feedback (Linear Regime)
    print("--- Scenario A: Zero Feedback (k = 0.0) ---")
    inputs_a, actuals_a = simulate_regime(feedback_coef=0.0)
    r2_a = fit_linear_operator(inputs_a, actuals_a)
    print(f"Linear Fit Quality (R^2): {r2_a:.6f}")
    
    # Scenario B: High Feedback (Nonlinear Regime transition)
    # We attempt to find if a linear model can still fit this deformed composition.
    print("\n--- Scenario B: High Feedback (k = 0.5) ---")
    inputs_b, actuals_b = simulate_regime(feedback_coef=0.5)
    r2_b = fit_linear_operator(inputs_b, actuals_b)
    print(f"Linear Fit Quality (R^2): {r2_b:.6f}")
    
    # Falsification Rule:
    # If the fit quality remains extremely high (R^2 > 0.99) even under high feedback,
    # then the claim that residue deforms composition and breaks linear representation is falsified.
    # If R^2 drops significantly (R^2 < 0.99), the principle survived (transition to NL verified).
    
    falsified = False
    if r2_b > 0.99:
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("The system maintained a linear representation despite high residue feedback.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (REGIME BOUNDARY SURVIVED).")
        print("Residue feedback successfully deformed composition, making a linear fit inaccurate.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
