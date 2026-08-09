# P009 — Formal Symbolic Proof: Admissible Increment

## Goal
Symbolically derive Lemma `L013`: For any process index `α`, the update increment `Δxα` must lie within the admissibility window `Aα`.

## Uses
- Lemma: `L013`
- Definitions: 
    - `D1`: Admissibility window `Aα`
    - `D2`: Admissibility projection `Π_A`
- Specification: `# Formal Specification of ⇔(_R).txt`

## Proof

1. **State the Update Rule.**
   From the unified continuation form of `⇔_R`, the state update for `α` is defined as:
   `x'α = xα + Π_Aα( vα )`
   where `vα` is the candidate navigation vector (e.g., `Σ transport`).

2. **Define the Increment.**
   The update increment `Δxα` is defined as the difference between the updated state and the prior state:
   `Δxα := x'α − xα`

3. **Substitute the Update Rule.**
   Substituting (1) into (2):
   `Δxα = (xα + Π_Aα( vα )) − xα`
   `Δxα = Π_Aα( vα )`

4. **Apply Projection Definition.**
   By definition of the admissibility operator `Π_Aα`, for any candidate vector `vα`, the operator maps the input into the admissibility domain:
   `Π_Aα : V → Aα`
   Therefore, for any `vα` in the domain `V`:
   `Π_Aα( vα ) ∈ Aα`

5. **Conclude.**
   From (3) and (4):
   `Δxα ∈ Aα`

∎

## Status
formally_proven

## Proof Type
symbolic
