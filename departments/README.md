# Departments Root

This directory is the common root for first-class governed departments.

The governing policy is recorded in:

- `registry/governance/patches/MPF_GOV_DEPARTMENT_INDUCTION_001.json`

## Root Rule

All departments shall exist as peer directories beneath `departments/`.

This root exists to preserve:
- equal constitutional standing,
- consistent tooling,
- consistent vector routing,
- uniform governance,
- future scalability.

## Minimum Department Contract

Each department must contain:
- `department_ssot.md` or an equivalent local SSOT file,
- `AGENTS.md`.

Departments may additionally define:
- `registry/`
- `models/`
- `proofs/`
- `validation/`
- `applications/`
- `references/`

## Inheritance Rule

Every department inherits:
- global governance,
- claim governance,
- operator registry,
- ontology,
- RT/Core,
- term registry.

Departments may define local vocabulary, interpretation frameworks, domain evidence rules, local registries, and applications.

Departments may not define new primitive ontology, replacement governance, replacement RT/Core, or replacement operator semantics.
