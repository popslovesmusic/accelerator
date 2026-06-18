# L099 — Projection Legality (Geo Projection Legality)

## Statement
For any admissible topology $T$ under the projection operator $\Pi_{\text{geo}} : \text{Topology\_app} \to \text{Geometry\_app}$, the mapping preserves distinction class, admissibility status, orientation class, and closure class.

Specifically, the following four legality requirements must hold:
1. **G1 (Distinction Preservation):** Projection shall not erase admissible distinctions.
   $$ D_{\text{topology}}(A \parallel B) > 0 \implies D_{\text{geometry}}(\Pi_{\text{geo}}(A) \parallel \Pi_{\text{geo}}(B)) > 0 $$
   *Failure Condition:* Distinct topology structures collapse into indistinguishable geometry.
2. **G2 (Admissibility Preservation):** Projection shall not generate illegal structures.
   $$ P_{\text{adm}}(T) = 1 \implies P_{\text{adm}}(\Pi_{\text{geo}}(T)) = 1 $$
   *Failure Condition:* Projection produces geometry violating upstream legality constraints.
3. **G3 (Orientation Preservation):** Orientation class must remain traceable through projection.
   $$ \text{Class}_{\text{orient}}(T) \implies \text{Class}_{\text{orient}}(\Pi_{\text{geo}}(T)) $$
   *Failure Condition:* Orientation selector information becomes unrecoverable.
4. **G4 (Closure Preservation):** Closure structure must survive projection unless explicitly transformed by a governed operator.
   $$ \text{Closure}(T) \implies \text{Closure}(\Pi_{\text{geo}}(T)) $$
   *Failure Condition:* Closure is destroyed without a lawful explanatory mechanism.

## Dependencies
- Lemma L045 (Topology-Geometry Biconditional)
- Lemma L080 (Cross-Basin Projection)

## Proof Sketch
1. By L045, topology and geometry are co-conditioning projections of the underlying process.
2. By L080, micro-updates scale to macro-geometry preserving structural features.
3. If any of the requirements G1-G4 are violated, the projection $\Pi_{\text{geo}}$ destroys the relational process trace, making it mathematically ill-posed.
4. Therefore, $\Pi_{\text{geo}}$ must be restricted to the admissible partition satisfying these four properties.

## Status
- **Status:** unproven
- **Proof Type:** formal_procedural
- **Endorsement:** Level C1 targeted

## Metadata
- **Codex Grounding:** GEO-HARDENING-001
- **Authority:** Mono-Process Framework Core Math Program. ∎
