# Re-orientation Trigger Condition (Trigger_Reorient)

## 1. Scope
This document formalizes the `Trigger_Reorient` control rule within the Mono-Process Framework. It defines the pre-realization condition that diverts the continuation pipeline into orientation reassessment. This rule is distinct from `Arb_A` realization arbitration and `NavT` reorientation transport.

## 2. Formal Definition
The re-orientation trigger is a control rule represented by the symbol:
$$\text{Trigger\_Reorient}(x, c, R_{\leftrightarrow}, C_t, C_t^S) \to \{\text{TRUE}, \text{FALSE}\}$$

### Trigger Conditions
The trigger evaluates to $\text{TRUE}$ if and only if any of the following conditions are met:
1. **Admissibility Collapse ($\delta_a$ image is empty):**
   $$\delta_a(x; c) = \emptyset$$
2. **Sequential Pruning Exhaustion ($S_{R,A}$ empties candidate set):**
   $$C_t^S = \emptyset$$
3. **Closure Support Degradation:**
   $$S_{\text{closure}} < \tau_R$$
   Where $S_{\text{closure}}$ is the measured closure stability and $\tau_R$ is the admissibility threshold. This allows the trigger to fire under degradation without literal candidate exhaustion.
4. **Orientation Reference Requirement:**
   $$\text{Def}_a(x, c) \text{ requires a new orientation reference } -(i)$$

Formally:
$$\text{Trigger\_Reorient}(x, c, R_{\leftrightarrow}, C_t, C_t^S) = \text{TRUE} \iff [\delta_a(x; c) = \emptyset] \lor [C_t^S = \emptyset] \lor [S_{\text{closure}} < \tau_R] \lor [\text{Def}_a(x, c) \text{ requires new } -(i)]$$

### Execution Branches
- **False Case (Default Continuation):**
  If $\text{Trigger\_Reorient} = \text{FALSE}$, ordinary $\text{Arb\_A}$ realization proceeds over the pruned candidate set $C_t^S$.
- **Success Branch (Reorientation Transport):**
  If $\text{Trigger\_Reorient} = \text{TRUE}$ and $\text{NavT}$ can produce an admissible updated orientation reference $-(i)'$, the pipeline re-enters $\delta_a$ under the new reference:
  $$\text{Re-entry} \to \delta_a(x; c) \text{ with orientation } -(i)'$$
- **Failure Branch (Collapse Review):**
  If $\text{Trigger\_Reorient} = \text{TRUE}$ and no admissible orientation reference can be resolved by $\text{NavT}$, the process halts and enters a $0\text{-state}$ collapse review.

## 3. Role Separation
To preserve operational clarity, the functional roles are partitioned as follows:
- **`Trigger_Reorient` (Control Rule):** Invokes orientation reassessment. It does not perform transport or select realized states.
- **`NavT` (Transport Operator):** Performs reorientation transport and orientation-reference updates. It does not trigger itself or arbitrate.
- **`Arb_A` (Realization Arbitrator):** Selects the realized continuation state $q^*$ from the admissible candidate pool $C_t^S$. It remains downstream of a restored admissible candidate pool.
- **`S` (Sequential Pruner):** Prunes the candidate pool before $\text{Arb\_A}$ based on sequential constraints.

## 4. Bounded Claims & Negative Constraints
- $\text{Trigger\_Reorient}$ is not realization.
- $\text{Trigger\_Reorient}$ is not $\text{Arb\_A}$ or $\text{NavT}$.
- $\text{Trigger\_Reorient}$ does not select the final update state $q^*$.
- $\text{Trigger\_Reorient}$ does not define the new orientation reference $-(i)$.
- $\text{Trigger\_Reorient}$ does not promote topology, geometry, or physics-app claims.
