# TR-008: Bounded Admissibility, Trajectory, and Observed-Slice Contracts

**Status:** C1 model-relative formalization candidate  
**Scope:** finite interface contracts only  
**Promotion:** not authorized

## Scope boundary

This note defines a finite interface for an admissibility boundary, a bounded trajectory between two boundary markers, and selection of an observed computational slice. The terms sphere, geodesic, and hexahedron are retained as labels for the proposed model interface; no physical geometry, transport medium, or external causal law is asserted.

## Bounded objects

Let (W) be a finite admissibility window with an ordered set of boundary markers (M). A boundary state is:

```text
BoundaryState = (window_id, marker_id, proposition_id, orientation_field)
```

A perturbation is admissible only when its source, target, proposition, and transition label are declared in the current interface. An admissible transition changes the boundary state; it does not transfer interior organization.

For distinct markers (A) and (B), a trajectory is an ordered finite sequence:

```text
Trajectory(A,B) = [A, m1, ..., mn, B]
```

The sequence is valid only when it starts at (A), ends at (B), contains no duplicate marker, and every consecutive transition is declared admissible. “Geodesic” is an optional model label for this sequence and carries no metric meaning here.

## Observed slice

An observed slice is selected by a declared orientation context and a declared face/interface mapping:

```text
Slice = (trajectory_id, orientation_context, interface_id, ordered_positions)
```

The slice must preserve the interface’s declared position order. A trajectory or orientation may select a different slice, but selection is not allowed to reorder positions silently or expose an undeclared interface.

## Fail-closed rules

1. A missing or mismatched proposition context is `INADMISSIBLE`.
2. A trajectory with an invalid endpoint, duplicate marker, or undeclared edge is `INVALID_TRAJECTORY`.
3. A slice with an unknown interface or non-declared position order is `INVALID_SLICE`.
4. No fixture result is interpreted as physical causality, geometry, or topology outside this bounded interface.

## Required finite coverage

The fixture package tests one valid boundary transition and valid slice, plus rejection of proposition mismatch, invalid endpoints, duplicate markers, undeclared transitions, unknown interfaces, and order loss.

The resulting claim ceiling remains C1 model-relative. Further work is required before linking this interface to density redistribution, MTO/OTM behavior, or external geometry.
