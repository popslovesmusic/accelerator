# Agent: Configuration Scope

Applies to `configs/**` only.

## Authority

This file governs experiment, validation, runtime, and audit configuration files.

Root `AGENTS.md` still applies unless this file explicitly grants narrower local config maintenance permission.

## Allowed

- Create new config files when explicitly requested.
- Validate JSON/YAML syntax after edits.
- Preserve default configs.
- Add clearly named audit or validation configs.
- Record purpose, intended tool, parameters, and expected outputs.

## Forbidden

- Overwrite default configs without explicit approval.
- Change production or canonical configs silently.
- Reuse old configs as current without checking compatibility.
- Modify configs to make tests pass artificially.

## Required Verification

After any config edit:

- Validate syntax.
- Show `git diff -- configs/`.
- Report whether the config is new, modified, default, canonical, exploratory, or deprecated.

## Naming Rule

New configs should use descriptive names that include purpose and date or run intent when appropriate.
