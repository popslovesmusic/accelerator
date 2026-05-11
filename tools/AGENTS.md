# Agent: Tool Health and Validation Scope

Applies to `tools/**` only.

## Authority

This file governs tool health inspection, validation artifacts, smoke tests, and certification evidence inside tool directories.

Root `AGENTS.md` still applies unless this file explicitly grants narrower local maintenance permission.

## Allowed

- Inspect tool manifests and validation directories.
- Run smoke tests for existing tools.
- Check executable loadability.
- Check stdout, stderr, and exit codes.
- Inspect validation artifacts such as `certification_manifest.json`, `smoke_report.json`, and `uncertainty_report.json`.
- Report missing or contradictory validation artifacts.

## Forbidden

- Modify engine code without explicit user authorization.
- Rewrite simulation logic.
- Upgrade certification level without direct evidence.
- Treat a successful smoke test as scientific validation.
- Treat local validation artifacts as self-certifying claims.
- Delete tool outputs, binaries, or validation files without explicit approval.

## Required Verification

For any tool health claim, include:

- tool path,
- command used,
- exit code,
- stdout excerpt,
- stderr excerpt,
- artifact path if applicable.

## Certification Boundary

Runtime health, certification level, and claim strength are separate categories.

A tool may run successfully while still lacking sufficient certification for strong claims.
