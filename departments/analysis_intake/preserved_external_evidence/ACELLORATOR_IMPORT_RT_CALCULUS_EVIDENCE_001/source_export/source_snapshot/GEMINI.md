# Local Governance Layer (GEMINI.md)

This document is the active execution authority for the RT Calculus falsification workspace.

Its purpose is to ensure that every attack is reproducible, independently verifiable, correctly classified, and permanently traceable.

This repository is an independent attack platform.

It is **not** the canonical RT repository, theorem authority, publication source, or claim promotion system.

---

# Authority Scope

This document governs only attack execution within its authorized scope.

It shall not supersede higher-precedence repository instructions, platform safety requirements, or explicitly authorized runtime directives.

Evidence produced here is independent and may later be inducted into the RT program through its own governance process.

---

# Mission

Assume every mathematical concept entering this repository is vulnerable.

The purpose of this workspace is to determine:

- whether it fails,
- where it fails,
- why it fails,
- under which assumptions it fails,
- the lowest abstraction level at which failure is justified.

No concept is protected from attack.

---

# Attack Protocol

Every attack shall declare:

- Unique Attack ID
- Target concept
- Target formulation
- Mathematical representation
- Explicit assumptions
- Attack boundaries
- Python implementation
- Independent verification method
- Reproducibility information

---

# Reproducibility Contract

Every attack shall record:

- Python version
- Dependency lock / requirements
- Operating system
- Runtime information
- Random seed(s)
- Input data hashes
- Configuration hashes
- Source hash
- Tool versions
- Exact execution command
- Output directory

The attack shall be reproducible from the recorded information alone. All future runs must satisfy the reproducibility contract. All run outputs must be immutable, saved to run-specific paths, and run-ID-addressed. Existing historical packets must never be overwritten.

---

# Independent Verification

Independent verification shall be structurally independent from the primary attack.

Examples include:

- independent implementation
- independent algorithm
- independent mathematical derivation
- independent simulation
- independent reviewer

 A second function inside the same implementation is not considered independent verification. Program M and Program S co-located in the same execution script are classified as `SAME_SCRIPT_DUAL_COMPARISON` (dual analyses) and do not establish independent verification.

---

# Representation Rule

When an external mathematical framework is used
(Category Theory, Dynamical Systems, Information Theory, etc.)

the attack shall explicitly state

- preserved RT semantics
- omitted RT semantics
- introduced assumptions
- known projection losses
- falsification conditions for the representation itself

Failure of a representation is not automatically failure of the RT concept.

---

# Failure Attribution

Failures shall be attributed to the lowest justified abstraction level.

Default precedence:

1. Representation
2. Formulation
3. Procedure
4. Concept

Escalation to a higher level requires explicit justification that lower-level explanations are insufficient.

---

# Outcome Classification

Every completed attack shall terminate with exactly one primary outcome.

- ATTACK_INVALID
- ATTACK_INCONCLUSIVE
- PROJECTION_FALSIFIED
- FORMULATION_FALSIFIED
- PROCEDURE_FALSIFIED
- CONCEPT_FALSIFIED
- SURVIVED_SPECIFIED_ATTACK

Definitions:

ATTACK_INVALID
: malformed attack, insufficient controls, failed reproducibility,
failed independent verification, or incomplete execution.

ATTACK_INCONCLUSIVE
: attack executed correctly but insufficient evidence exists to reach a determination.

SURVIVED_SPECIFIED_ATTACK
: the predefined falsifier was not observed within the declared attack bounds.

Survived is **not proof**.

---

# Claim Boundary

Every report shall explicitly declare:

- evidence class
- epistemic status
- proof status
- scope
- remaining untested assumptions
- applicability level

The report shall identify whether its conclusions apply to

- representation
- formulation
- procedure
- concept

---

# Registry

All attack records are append-only.

Every registry entry shall contain:

- Attack ID
- Parent attack(s)
- Timestamp
- Reviewer
- Representation
- Script path
- Source hash
- Configuration hash
- Input hash
- Outcome
- Findings
- Record hash

Historical records and reports shall never be modified in place. Corrections, reinterpretations, and reformulations shall create new linked records. Overstrong language must be scope-corrected in the evidence index rather than deleted. Every future report must explicitly separate: (1) direct execution observation, (2) model-internal interpretation, (3) standard mathematics comparison, and (4) unsupported or unresolved claims.

---

# Execution Safety

Attack execution shall not modify:

- canonical registries
- engine source
- default configurations
- textbook authority
- historical attack records

unless separately authorized.

---

# Resource Limits

Every attack shall declare:

- maximum runtime
- maximum search depth
- maximum candidate count
- termination condition
- continuation token (if applicable)

Every execution shall terminate with an explicit stopping reason.

---

# Repository Boundary

This repository exists solely to generate independent evidence.

It does not establish mathematical authority.

Evidence generated here may later be inducted into the RT program through its own governance process. Induction decisions occur outside this repository. No attack result in this workspace promotes authority outside the platform. Induction decisions and processes remain external to this repository.
