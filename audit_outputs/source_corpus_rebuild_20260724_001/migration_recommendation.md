# Migration Recommendation

## Result
The candidate database was rebuilt separately from governed `registry` and `docs` Markdown/JSON sources. The legacy database was preserved and opened read-only for comparison.

## Recommendation
Do not cut over yet. First resolve duplicate identifiers and table-specific legacy-only records, then define an approved mapping from source records to production projections.

Large inline governance evidence was not copied into the candidate database; source paths, hashes, and metadata are retained for reference.

Cutover requires explicit human approval and a separate migration packet with rollback.
