# Bridge Comparison Schema (MPF-PALG-034)

## 1. Purpose
This document defines the **Bridge Comparison Schema**. It provides the formal structural requirements for comparing distinct projection domains (e.g., QM-like vs. GR-like) within the Process Algebra framework. The schema ensures that domain comparisons are grounded in **shared source-relation traceability** and explicit **differential loss accounting**.

## 2. Core Structure
A valid bridge comparison must include:
- **Shared Source Relation**: The common **⇔R** relational core from which both domains are projected.
- **Domain Mapping**: Formal records of both projection domains, including their operators and depth.
- **Feature Alignment**: Identification of features that are compatible, complementary, or conflicting across the domains.
- **Differential Loss**: A mapping of features lost in one domain but retained in the other, and those lost in both.

## 3. Comparison Rules
- **BCS-RULE-001: Traceability Mandate**: No comparison is permitted without a validated `source_relation` and `shared_trace_id`.
- **BCS-RULE-002: Conflict Transparency**: Feature conflicts must be explicitly documented and preserved rather than collapsed into a "unified" representation.
- **BCS-RULE-003: Mandatory Loss Accounting**: The "information gap" between the domains must be rigorously quantified.
- **BCS-RULE-004: Non-unification Rule**: Agreement between domains is analyzed as **Process Algebra coherence** only. It is never evidence for physical QM/GR unification.

## 4. Coherence Classes
Comparisons are classified into **Multi-Projection Coherence (MPC)** tiers:
- **MPC-1**: Shared Trace only.
- **MPC-2**: Feature overlap.
- **MPC-3**: Loss-aware partial agreement.
- **MPC-4**: Critical projection conflict.

## 5. Usage Limits
- **Banned**: Promoting bridge agreement to physical law status.
- **Banned**: Treating symbolic complementarity as proof of ontological identity.
- **Banned**: Using bridge comparisons to bypass restricted-local scope status.

## 6. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Schema Status**: CANDIDATE_BRIDGE_SCHEMA.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
