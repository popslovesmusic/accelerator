# Notebook 16 Design: Projection-Driven Organizational DoF Isolation

## Scope

Notebook 16 is a pre-execution Colab campaign design for `MPF_SIM_PROJECTION_DOF_ISOLATION_001`.

It asks whether increasing admissible organizational degree of freedom produces genuinely new continuation organizations while preserving the primitive law inside a bounded symbolic model.

Current status: `C1_SPECIFICATION_ONLY`.

## Research Question

Does increasing admissible organizational DoF produce new continuation organizations while preserving the primitive law?

## Core Contrast

- Null hypothesis: higher organizational dimensions are representational only.
- Experimental hypothesis: higher organizational DoF produces additional lawful continuation classes that cannot exist in lower-DoF domains.

## Operationalization

Notebook 16 does not vary geometry, external physics, or RT_core.

It varies only organizational DoF, operationalized as the maximum number of distinct aspect positions admitted by a single continuation-binding event. The primitive binding rule itself remains unchanged across all DoF values.

Bounded initial sweep:

- DoF 1: primitive chain / single-position organization,
- DoF 2: paired organization,
- DoF 3: recursive triads,
- DoF 4-6: higher nested RT organizations.

## Primary Measurements

For each DoF, Notebook 16 records:

- primitive preserved,
- number of lawful organizations,
- number of illegal organizations,
- closure percentage,
- average continuation depth,
- organization entropy,
- projection diversity,
- new stable organization count,
- continuation branching,
- symmetry counts,
- asymmetry counts,
- novel organization rate.

## Novel Organization Discovery

Notebook 16 adds one measurement that earlier notebooks did not target directly:

`novel_organization_rate`

A lawful organization counts as novel only if it cannot be projected losslessly into any lower-DoF domain under the declared projection operator. Larger arity by itself is not enough.

## Follow-On Campaign

Notebook 16 writes a projection-loss table that prepares a separate governed follow-on campaign:

`MPF_SIM_PROJECTION_INDUCTION_001`

That follow-on campaign asks whether every higher-DoF organization can be projected back into lower-DoF organization without loss of closure, continuation structure, symmetry classification, or organization identity.

## What Notebook 16 Does Not Prove

Notebook 16 does not prove a theorem about the full calculus. It does not establish external physical validation. It does not show that symbolic organizational richness equals ontological expansion. It only creates bounded evidence inside a declared symbolic continuation model and only after execution outputs are recovered and inducted.
