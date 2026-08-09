# Falsification Campaign Report: FAT-12-TRIADIC-CLOSURE-4.X.1

## Executive Summary

- **Campaign ID:** `FAT-12-TRIADIC-CLOSURE-4.X.1`
- **Target Concept:** Formal Statement 4.X.1: Asymmetric Triadic Closure Theorem
- **Date & Time of Run:** 2026-08-03 15:46:10 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the assertion that asymmetric triadic closure behaves as a self-reinforcing stabilization basin. Specifically, we test the textbook hypothesis that closure is a consequence of orientation alignment (providing negative feedback) by performing **Ablation M1 (orientation-removal/randomization)**.

### Falsification Criteria
- We model three coupled distinction nodes $N_1, N_2, N_3$ forming a triadic closure relation.
- We compare:
  1. **Compliant (Oriented):** Coupling orientations are aligned with node differentials ($o_{ij} = 1.0$), providing stable attractive restoring forces.
  2. **Ablated (Ablation M1):** Coupling orientations are randomized ($o_{ij} = \pm 1.0$), representing orientation removal.
- If the ablated system can remain stable and bounded without collapsing over 5,000 steps in a high percentage of runs ($>90\%$), the necessity of orientation alignment is falsified. If it diverges and collapses in a significant portion of runs, it survived.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_12_triadic_closure_4_x_1.py`) simulating:
- Three node values initialized at $N_1 = 1.0, N_2 = 3.0, N_3 = -2.0$.
- The triadic consensus coupling:
  $$ N_1(t+1) = N_1(t) + \alpha \Big( (N_2(t) - N_1(t)) \cdot o_{12} - (N_1(t) - N_3(t)) \cdot o_{31} \Big) $$
  $$ N_2(t+1) = N_2(t) + \alpha \Big( (N_3(t) - N_2(t)) \cdot o_{23} - (N_2(t) - N_1(t)) \cdot o_{12} \Big) $$
  $$ N_3(t+1) = N_3(t) + \alpha \Big( (N_1(t) - N_3(t)) \cdot o_{31} - (N_3(t) - N_2(t)) \cdot o_{23} \Big) $$
- Boundary limit: if $\max(|N_i|) > 10.0$, the process collapses.
- We evaluate over 50 seeds and 5,000 steps per seed.

---

## 3. Results & Findings

### Compliant Runs (Oriented, $o_{ij} = 1.0$)
- **Stable Runs:** $50/50$ ($100\%$).
- **Collapsed Runs:** $0/50$ ($0\%$).
- **Finding:** Under aligned orientation, the coupling behaves as a stable contraction mapping, drawing all three nodes to their conserved average ($\frac{2}{3} \approx 0.6667$) and maintaining perfect asymptotic stability.

### Ablated Runs (Ablation M1, randomized $o_{ij} = \pm 1.0$)
- **Stable Runs:** $29/50$ ($58.0\%$).
- **Collapsed Runs:** $21/50$ ($42.0\%$).
- **Finding:** Randomizing the orientation breaks the negative feedback loop. Half of the time the coupling forces become repulsive, turning the node dynamics into a random walk that diverges past the boundary threshold, causing $42.0\%$ of the runs to collapse.

---

## 4. Conclusion & Disposition

The concept of **Asymmetric Triadic Closure** **survived** the attack. Removing orientation alignment (Ablation M1) eliminates the negative feedback mechanism necessary to keep the triadic nodes bounded, causing the system to diverge and collapse in $42.0\%$ of the simulations. This confirms that triadic closure is indeed a consequence of oriented restoring forces.
