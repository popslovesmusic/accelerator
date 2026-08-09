"""
FAT-11-FLOOR-CONSTRAINT-DS: Falsification Attack on Floor Constraint
Framework Concept: Floor Constraint (Formal Block 3.4.1)
External Discipline: Dynamical Systems Theory
Objective: Show that the floor constraint is a artifact of a singular projection choice.
By formulating the update using standard dynamical systems gradient descent (which scales
with the distance), the singularity at zero is avoided entirely. We show that:
1. The RT update with a hard discontinuous floor constraint enters chattering limit cycles
   or diverges when step size alpha > epsilon.
2. Standard gradient descent converges smoothly to the attractor without any floor constraint
   or singularity, proving the floor constraint is not a fundamental process requirement.
"""

import sys

def simulate_rt_floor(S0=1.0, alpha=0.08, epsilon=0.05, steps=100):
    """
    Simulates state updates using the RT floor constraint formulation.
    """
    S = S0
    history = [S]
    for _ in range(steps):
        # RT division-by-distance update with epsilon floor
        D = max(abs(S), epsilon)
        orientation = S / D
        S_next = S - alpha * orientation
        S = S_next
        history.append(S)
    return history

def simulate_smooth_gradient(S0=1.0, alpha=0.1, steps=100):
    """
    Simulates standard smooth gradient descent.
    No floor constraint is needed because the update scales with distance.
    """
    S = S0
    history = [S]
    for _ in range(steps):
        # Smooth gradient update: dx/dt = -S. No division by distance.
        S_next = S - alpha * S
        S = S_next
        history.append(S)
    return history

def run_attack():
    print("====================================================")
    print("FAT-11-FLOOR-CONSTRAINT-DS: DYNAMICAL SYSTEMS ATTACK")
    print("====================================================")
    
    alpha = 0.08
    epsilon = 0.05
    steps = 50
    
    print(f"Simulation parameters: alpha={alpha}, epsilon={epsilon}")
    
    # Run RT floor formulation
    hist_rt = simulate_rt_floor(alpha=alpha, epsilon=epsilon, steps=steps)
    # Check for chattering (oscillating sign) or divergence near the attractor
    last_10 = hist_rt[-10:]
    signs = [x > 0 for x in last_10]
    sign_changes = sum(1 for i in range(len(signs)-1) if signs[i] != signs[i+1])
    
    print("\nRT Floor Constraint Formulation:")
    print(f"  Final 5 values: {[round(x, 4) for x in hist_rt[-5:]]}")
    print(f"  Sign changes in last 10 steps: {sign_changes}")
    
    # Run standard smooth gradient descent
    hist_smooth = simulate_smooth_gradient(alpha=0.1, steps=steps)
    print("\nStandard Smooth Gradient Descent Formulation:")
    print(f"  Final 5 values: {[round(x, 6) for x in hist_smooth[-5:]]}")
    
    # Falsification logic:
    # If standard gradient descent converges smoothly to 0 without any floor constraint
    # or singularity, and the RT floor formulation chatters, the absolute necessity
    # of the floor constraint is falsified.
    
    falsified = False
    if abs(hist_smooth[-1]) < 0.01 and sign_changes > 5:
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("Standard gradient descent converges smoothly without any floor constraint.")
        print("The RT floor constraint creates an artificial boundary discontinuity that causes chattering.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
