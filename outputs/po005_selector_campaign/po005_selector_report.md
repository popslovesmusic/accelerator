# PO_005 Selector Campaign Report

## 1. Scope and Target
* **Target obligation:** PO_005 (Orientation acts as a topological selector)
* **Goal:** Verify that specific knot-classes only emerge under compatible orientation regimes, demonstrating that orientation functions as a boundary selector mapping to distinct topological closures.

## 2. Directly Observed and Simulated Results
The campaign simulated topological selection over 64 seeds across four distinct orientation regimes:

* **Alternating O1:**
  * $T_0$ (No closure): 0.0781
  * $T_1$ (Simple closure): 0.7969 (Dominant)
  * $T_2$ (Linked closure): 0.1250
  * $T_3$ (Braided closure): 0.0000
* **Parallel O2:**
  * $T_0$ (No closure): 0.1094
  * $T_1$ (Simple closure): 0.0312
  * $T_2$ (Linked closure): 0.8125 (Dominant)
  * $T_3$ (Braided closure): 0.0469
* **Helical O3:**
  * $T_0$ (No closure): 0.2188
  * $T_1$ (Simple closure): 0.0469
  * $T_2$ (Linked closure): 0.0156
  * $T_3$ (Braided closure): 0.7188 (Dominant)
* **Shuffled (Randomized):**
  * $T_0$ (No closure): 0.6094 (Dominant)
  * $T_1$ (Simple closure): 0.1250
  * $T_2$ (Linked closure): 0.1250
  * $T_3$ (Braided closure): 0.1406

### Specificity Outcomes
* **$T_1$ Selector Specificity:** 0.6719
* **$T_2$ Selector Specificity:** 0.6875
* **$T_3$ Selector Specificity:** 0.5781
* **Shuffled Null-Emergence Collapse:** 0.6094

## 3. Inferred inside Framework
* The emergence of specific, non-null knot classes is highly dependent on matching orientation constraints. 
* Randomizing orientation destroys selector mapping, yielding mostly null/unorganized closures ($T_0$).
* This confirms that orientation functions as an active topological selector, supporting the selector-bridge formulation of `OPEN_BRIDGE_001`.

## 4. What it does NOT prove
* **CRITICAL LIMITATION:** This result does NOT prove that orientation acts as an independent primitive or physical driver of stability. It is a boundary selection mapping under aspect-co-conditioning. No physical claims regarding geometry, gravity, or matter are implied.

## 5. Ruling and Consequence
* **Outcome:** **PASS** (Success conditions satisfied).
* **Consequence:** PO_005 enters status `PASSED_PENDING_RIGOR_ENDORSEMENT`.
