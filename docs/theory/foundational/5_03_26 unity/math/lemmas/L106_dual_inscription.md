# Lemma L106 — Dual Inscription of Residue

## 1. Statement
Residue inscription ($\Psi$) occurs in two distinct, co-conditioning modes mapping process outcomes into residue space:
1. **Realized Continuation Inscription ($\Psi_+$):** The inscription of successful, admissibility-admitted transitions into residue, mapping continuation difference and orientation dynamics:
   $$\Psi_+ : R \times X \times \Pi_A(X) \to R$$
2. **Excluded Boundary Inscription ($\Psi_- \text{ or } \Psi_-$):** The inscription of non-admitted, excluded process boundaries into residue, writing constraint geometry to shape future admissibility boundaries:
   $$\Psi_- : R \times X_{\text{excluded}} \to R$$

All process outcomes must be inscribed in either $\Psi_+$ or $\Psi_-$ mode to preserve the history-dependent non-Markovian nature of the admissibility filter $\delta_a$.

## 2. Dependencies
- `L005`: Residue-Conditioned Closure
- `L043`: Tertiary Node Structure ($I, O, R$ Partitioning)
- `L055`: Residue as Memory Kernel

## 3. Proof Sketch
By `L043` and `L055`, stable process persistence requires the accumulation of relational dynamics into a history-sensitive residue space $R$. If only realized transitions are inscribed ($\Psi_+$), the admissibility filter $\delta_a$ fails to incorporate the constraint history of excluded boundaries, leading to coordinate drift and ontological leakage under recursive updates. 
Inscribing excluded boundaries via $\Psi_-$ ensures that boundary-generation events are preserved as first-class process outcomes that constrain future admissibility. Thus, the inscription operator must be partitioned into co-conditioning $\Psi_+$ and $\Psi_-$ modes.

## 4. Status
provisional
