# Lemma L111 — Typed Zero-Condition Recoupling

## 1. Statement
Within these models, a locally collapsed same-direction expression may participate in higher-order RT only if its zero-condition remains typed and is compared against an oppositely typed zero-condition. 

Nesting does not rehabilitate an illegal RT form unless the collapsed term retains typed residue and is recoupled with an oppositely typed residue under a declared higher-order relation:
1. **Illegal Inner Forms:** 
   - $RT_{minus} := [D(-|-) \langle f \rangle_x D(-|-)] \to 0_{minus}$
   - $RT_{plus} := [D(+|+) \langle f \rangle_x D(+|+)] \to 0_{plus}$
2. **Legal Outer Form:** $[0_{minus} \langle g \rangle_y 0_{plus}] \to RT_{admissible\_candidate}$
3. **Illegal Outer Forms:**
   - $[0_{minus} \langle g \rangle_y 0_{minus}] \to 0_{condition}$
   - $[0_{plus} \langle g \rangle_y 0_{plus}] \to 0_{condition}$
4. **Critical Constraint:** If $0_{minus}$ and $0_{plus}$ are reduced to undifferentiated $0$ (a fully erased null condition with no retained directional provenance), recoupling fails.

## 2. Dependencies
- `L101`: Universal Meta-Relation inside RT
- `L102`: Zero-State Domain Membership
- `L107`: Abstraction Meta-Level Stack

## 3. Proof Sketch
Same-direction expressions collapse locally because they lack productive internal opposition. Under `L102` (Zero-State Domain Membership), fully erased null conditions cannot participate in distinction-domain dynamics. However, if the collapse residue retains directional provenance ($0_{minus} \neq 0_{plus}$), a higher-order relation $\langle g \rangle_y$ at a different nesting layer can resolve their differences into a new admissible higher-order RT candidate. If the typed zeros are reduced to undifferentiated $0$, distinguishability is lost, and the outer comparison collapses, failing to rehabilitate the illegal nested form.

## 4. Status
provisional
