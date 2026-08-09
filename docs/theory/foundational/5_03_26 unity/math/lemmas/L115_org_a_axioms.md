# Lemma L115 — Org_a: Admissible Organization Axioms

## 1. Statement
Within these models:
1. **Organizational Operator:** The admissible organization operator $Org_a(G)$ organizes admissible distinction participation over a typed grouped participation graph $G$. It is not a set collector, object bundle, state container, or semantic category.
2. **Input Requirements:** The operator requires a typed grouped participation graph $G$ satisfying grouped bar admissibility ($Adm_{|}^{G}(G)$), orientation admissibility ($Adm_O(G, o)$ for some $o \in O(G)$), grouped distinction evaluation ($Eval_{D}^{G}(G)$), and positive distinction $D_G(G) > \epsilon_a$.
3. **Axioms of Admissible Organization:** A transformation of an organized field $G \iff_R G'$ is governed by three candidate axioms:
   - **Inventory Preservation (ORG_A_AX_001):** Legal transformations under $Org_a$ must preserve the admissible distinction inventory of $G$, meaning the participating distinction inventory remains traceable: $Inv_D(G) = Inv_D(G')$.
   - **Admissibility Conservation (ORG_A_AX_002):** Transformations must conserve admissibility, ensuring the organized participation field does not violate typed participation or fall below $\epsilon_a$: $Org_a(G) \land G \iff_R G' \implies Adm_a(G')$.
   - **Topological Consistency (ORG_A_AX_003):** Transformations must preserve orientation-consistent participation structure, meaning $G$ and $G'$ remain orientation-equivalent: $Org_a(G) \land G \iff_R G' \implies G \simeq_O G'$.
4. **Admissible Organization Closure:** An organized participation field is admissibly closed under $Adm_{Org}(G)$ iff grouped participation, orientation compatibility, distinction evaluation, inventory preservation, admissibility conservation, and topological consistency all hold:
   $$ Adm_{Org}(G) := Adm_{|}^{G}(G) \land \exists o\in O(G) Adm_O(G,o) \land D_G(G)>\epsilon_a \land InvPres_D(G) \land AdmCons_a(G) \land TopCons_O(G) $$
5. **Relationship to D and iff_R:** $Org_a$ organizes already evaluable admissible distinction participation, and $iff_R$ supplies the admissible preservation relation under which transformations are judged. These axioms are candidate definitions until formally derived from $D(A|B) > \epsilon_a$ and $iff_R$.

## 2. Dependencies
- Definitions: `Org_a`
- Prior lemmas: L113 (Vertical Bar Operator: Admissible Participation Separator), L114 (Grouped Bar Closure and Triadic Participation)

## 3. Proof Sketch
Admissible organization represents a structure of co-participation. To be lawfully transformed without collapse, the distinction inventory (the content of comparison) must be preserved, the admissibility rules (the conditions of participation) must remain satisfied, and the topological orientation (the directional trajectories) must remain compatible. These three requirements form the axioms of $Org_a$, ensuring that $G \iff_R G'$ acts as a homomorphism of distinction-preserving graphs.

## 4. Status
provisional

## 5. Supersedes / Superseded-by
None.
