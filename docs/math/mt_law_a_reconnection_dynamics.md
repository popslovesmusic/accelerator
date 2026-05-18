# MT-LAW-A: Reconnection Dynamics (Patch 047)

## 1. Purpose
This document formalizes the **Dynamics of Reconnection** for fractured continuation topology in **MT-LAW-A**. It defines the temporal and admissibility conditions required for two disconnected channels to merge and restore a connected topological state ($Betti\text{-}0 = 1$).

## 2. The Reconnection Gate ($\mathcal{G}_{\mathfrak{R}}$)
Reconnection is not automatic; it is gated by a local admissibility condition.

### 2.1 Admissibility of the Bridge
Two channels $\{\mathcal{T}_i, \mathcal{T}_j\}$ can reconnect if and only if there exists an admissible path $P$ through the local residue field $R$ that connects their basins without crossing a non-admissible barrier.
- **Condition:** $\exists P \subset U$ s.t. $\forall p \in P, S_{achieved}(p) > 0$.

### 2.2 Reconnection Energy ($\epsilon_{\mathfrak{R}}$)
Restoring connectivity requires overcoming the current ridge height of the barrier separating the fragments.
- **Source:** Typically requires external $P_{stab}$ or internal budget replenishment to lower the barrier.

## 3. Dynamic Reconnection Flow

### 3.1 Residue-Mediated Recoupling
Reconnection is facilitated by the **Residue-Mediated Recoupling** rule (R_RECOUPLING_V1). As the residue field $R$ adapts to the existence of the fractured components, it may "soften" the intervening barrier over time, lowering $S_C$ for the reconnection path.

### 3.2 Time-of-Flight Constraint
Reconnection must occur within the **Coherence Lifetime** of the fractured fragments. If the fragments drift too far apart in parameter space or their orientations decorrelate, the reconnection gate closes permanently.

## 4. Operational Classification: Reconnection vs. New Regime
- **True Reconnection:** Restores the original identity continuity $Id_A$ of the parent channel.
- **New Regime Stabilisation:** The fragments merge into a *new* metastable regime $M_{new}$ with a distinct identity.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-047
- **Deliverable ID:** docs/math/mt_law_a_reconnection_dynamics.md
- **Status:** RECONNECTION_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
