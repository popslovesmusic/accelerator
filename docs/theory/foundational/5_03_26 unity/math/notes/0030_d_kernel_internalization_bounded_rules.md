# D-Semantics Kernel Internalization: Bounded Transition Rules

## Status

`FORMALIZATION_CANDIDATE`

- Scope: RT Calculus Kernel integration for `Eval_D,C`, `Pi_D,C`, `RepDist_C`, and `NonCollapse_C`.
- Claim ceiling: `C1_DEFINED_PROVISIONAL`.
- Relation to prior work: additive companion to notes `0011`–`0029`; no prior lemma or proof is modified.
- Promotion: blocked while `OBL-D-001D` and `OBL-D-001E` remain open.

## Kernel syntax and judgments

For a declared context `C`, the kernel admits the following typed forms:

```text
x : TYPE_AFFECT_EFFECT_C
x ⇓D,C r                         (partial D evaluation)
x ─Pi_D,C→ p : TYPE_PROJECTION_C (typed projection)
(p,q,w_C,t,h) ⊢ RepDist_C         (representable distinction)
(p,q) ⊢ NonCollapse_C             (bounded non-collapse admissibility)
```

`C` is an explicit parameter of every judgment. A missing, cross-context, or incomplete context makes the judgment undefined; it is not silently inferred.

## Transition rules

The kernel transition route is:

```text
TYPE_AFFECT_EFFECT_C
        │  Eval_D,C defined and admissible
        ▼
TYPE_PROJECTION_C
        │  explicit Pi_D,C binding
        ▼
D(*|*) : TYPE_PROJECTION_C
```

The admissible projection rule is:

```text
Γ ⊢ x : TYPE_AFFECT_EFFECT_C     Defined(Pi_D,C(x))
Codomain(Pi_D,C) = TYPE_PROJECTION_C
────────────────────────────────────────────────────
Γ ⊢ x ─Pi_D,C→ Pi_D,C(x) : TYPE_PROJECTION_C
```

Direct substitution from `x` to `D(*|*)` is not a kernel reduction rule. The explicit `Pi_D,C` binding is required.

The representable-preservation rule is conditional on the full witness route:

```text
Γ ⊢ x,y : TYPE_AFFECT_EFFECT_C
Defined(Pi_D,C(x)), Defined(Pi_D,C(y))
project_w,C(w) = w_C
(Pi_D,C(x), Pi_D,C(y), w_C,t,h) ⊢ RepDist_C
────────────────────────────────────────────────────
Γ ⊢ PresRep_D,C(x,y,w,t,h)
```

This is a bounded admissibility rule, not a universal preservation theorem.

The non-collapse rule is:

```text
epsilon_C > 0     A_C ≠ ∅     p ≠ q     distinction_C(p,q) ≥ epsilon_C
──────────────────────────────────────────────────────────────
Γ ⊢ (p,q) : NonCollapse_C
```

Zero, subthreshold, missing-profile, and incompatible-context cases reduce to rejection/undefined outcomes.

## Conditional metatheoretic results

### Preservation (bounded conditional)

If the premises of the typed projection rule hold, then the resulting projection has type `TYPE_PROJECTION_C`. If the premises of the representable-preservation rule also hold, the bounded predicate `RepDist_C` is retained. This does not establish preservation for every source, context, or relation.

### Progress (partial and guarded)

For a well-typed kernel term, exactly one of the following is admissible under the declared context: a permitted transition, a permitted `Undefined(reason)` result, or a rejected boundary case. Progress here is a guarded partial-evaluation property; it does not imply total evaluation.

### Normalization (finite-route condition)

Normalization is available only for a finite, acyclic declared route whose evaluation and projection steps strictly decrease a supplied route measure. No route measure or global termination result is supplied by this note. Therefore normalization remains a conditional obligation, not a completed result.

## Falsification and limits

- A well-typed, same-context input satisfying all premises produces a non-`TYPE_PROJECTION_C` output.
- Direct substitution is accepted without `Pi_D,C`.
- A cross-context witness or history payload is accepted.
- A zero or subthreshold distinction is accepted as `NonCollapse_C`.
- A finite declared route cycles without a decreasing measure.

The note does not establish injectivity, reversibility, complete information preservation, universal normalization, physical validity, or theorem promotion. The accompanying fixtures are finite checks of rule boundaries only.

## Governance disposition

This additive note internalizes the bounded D-semantics route into a kernel-style rule presentation. `OBL-D-001D` and `OBL-D-001E` remain `OPEN`; no claim elevation follows.
