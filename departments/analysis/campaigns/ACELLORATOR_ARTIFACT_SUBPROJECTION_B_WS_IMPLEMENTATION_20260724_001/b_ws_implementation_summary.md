# B-WS Implementation Summary

## Result

B-WS (`workspace_artifact_catalog`) is `FROZEN_VALIDATED` as a derived, non-production builder.

## Scope

The builder observed physical files, physical directories, and symlink records using canonical workspace-relative paths. It excluded governed `docs` and `registry` roots, generated/runtime/output roots, databases, temporary roots, and the campaign output tree. Governed-source authority remains with frozen B-GOV.

## Measured output

- Records: 3067
- Relationships: 5991
- Scan errors: 0
- Ordered rows SHA-256: `6bb1ea0bfc7cf8ff502583426aa8543c6a98fee012d587e816a65eaae797d16f`
- Repeat-build equality: `PASS`

## Boundary and authority

B-WS uses the `workspace_artifact:` identity namespace and does not emit B-GOV `governed_source:` identities. It is derived filesystem observation, not authoritative source semantics and not a production cutover.

## Limitations

This implementation does not claim to reconstruct the entire legacy 110,596-row monolithic artifacts table. Generated, transient, historical, and governed-source subprojections remain separate downstream work.
