# Campaign 005: Domain-Relative Entropy Projection Test

## Scope
This C1 campaign applies one frozen projection to 700 immutable Campaign 004 orientations. It does not retest or modify orientation.

## Directly observed/defined
The projection is a deterministic domain-relative log ratio over the declared redistribution content, retained with source domain, source primitive, relation identity, and the pre-projection orientation hash.

## Primary projection results
Projection stability, orientation preservation, inverse compatibility, relation-identity preservation, and deterministic hashing all passed at 1.0. The independent verifier reproduced the projection results and integrity checks.

## Controls and information loss
Typed projection retained all tested orientation identities. Scalar-only and role-erasing controls discarded domain, primitive, context, or ordered-role information. Projection output was treated as an application observable, not as orientation identity.

## External entropy comparison
The comparison was documented but not run. Campaign 004 records contain no physical thermodynamic state variables. Adding such variables after projection freeze would violate the packet's input contract; therefore no conventional entropy correspondence claim is made.

## Inferred inside framework
Within the executed records, a deterministic domain-relative projection can be layered over frozen orientations without changing their hashes or relation identities, and inversion compatibility can be represented as an application-level inverse observable.

## External resemblance (Analogy only)
The signed log-ratio resembles a change observable used in multiplicative state comparisons. This resemblance is not evidence of thermodynamic identity.

## What it does NOT prove
It does not show that entropy is identical to distinction density, that this projection is physically correct, or that conventional entropy behavior has been reproduced.

## Failure modes / uncertainty
The external comparison is not comparable under the frozen input contract. The projection formula is one bounded candidate and may be replaced only by a separately authorized campaign.

## Status and next action
Status: `PROJECTION_SUPPORTED_NO_EXTERNAL_CORRESPONDENCE` (C1). A new campaign would need preregistered physical state fields and independent references to test external entropy correspondence.
