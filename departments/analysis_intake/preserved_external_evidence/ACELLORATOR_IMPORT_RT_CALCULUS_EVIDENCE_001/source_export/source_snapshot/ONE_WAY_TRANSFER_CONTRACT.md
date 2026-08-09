# RT Calculus → Acellorator One-Way Transfer Contract

## Direction

Information may flow only from this RT Calculus repository to an Acellorator receiving process.

```text
RT Calculus evidence package ──export──> outbound/acellorator/ ──manual or governed receive──> Acellorator
```

There is no reverse synchronization channel.

## RT-side guarantees

- The exporter reads only the local frozen evidence package.
- The exporter writes only to `outbound/acellorator/` inside this repository.
- The exporter does not read, write, import, query, or modify `D:\projects\acellorator`.
- Existing outbound exports are immutable; an existing export ID causes the exporter to stop.
- Every exported file has a relative path, byte size, and SHA-256 digest.
- Export metadata records `NOT_SUBMITTED`; generating an export is not Analysis Intake.

## Receiving-side boundary

Acellorator may accept or reject an export through its own Analysis Intake governance. The RT repository receives no status, registry, queue, or authority updates from that process.

## Evidence ceiling

Exported material remains provisional evidence. The transfer does not establish independent verification, promotion, theorem status, or external validity.
