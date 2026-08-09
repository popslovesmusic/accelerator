# TR-010: Bounded Distinction-Density and Zero-DOF Decoupling Contracts

**Status:** C1 model-relative formalization candidate  
**Scope:** finite accounting interface only  
**Promotion:** not authorized

## Scope boundary

This note defines a bounded accounting interface for distinction density, closure, redistribution, and zero-DOF decoupling. “Density” is an internal model quantity, not a physical substance, energy, entropy, or conservation law.

## Accounting states

An active domain carries a non-negative density quantity (D_a). A latent reservoir carries (D_r). A closure event is declared with an input and output active density. Under this interface, closure conserves active density:

```text
closure: D_a(out) = D_a(in)
```

A redistribution may change the internal allocation while preserving the declared total. It may not create density.

## Decoupling

A component with `dof = 0` may decouple from the active domain. Decoupling transfers its accounted density from the active domain to the latent reservoir:

```text
active_after = active_before - released
reservoir_after = reservoir_before + released
```

The total across active plus reservoir is preserved for a declared decoupling event, while the active domain loses capacity or participation. A zero-DOF component marked active is invalid.

## Fail-closed rules

1. Negative density is `INVALID_ACCOUNTING`.
2. Closure density increase or loss is `CLOSURE_NONCONSERVING`.
3. A redistribution that changes the declared total is `DENSITY_CREATED_OR_LOST`.
4. Decoupling without zero DOF is `INVALID_DECOUPLING`.
5. An active zero-DOF component is `INERT_STATE_REQUIRED`.

These rules do not define the cause of composition, decomposition, entropy, or MTO/OTM behavior. Those remain separate obligations.

## Claim boundary

Passing fixtures validate finite bookkeeping records only. They do not establish thermodynamic conservation, physical density, or external decoupling.
