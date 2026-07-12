# Semantic Readout State Diagram

## Default Local
`call -> boundary evaluated -> local reply returned`

## Denied Network Attempt
`call -> boundary evaluated -> boundary denied -> local reply returned`

## Authorized Network Success
`call -> boundary evaluated -> network request started -> network request succeeded`

## Authorized Network Failure
`call -> boundary evaluated -> network request started -> network request failed -> local reply returned`

## Guard Conditions
- `capability_enabled` must be true for a network attempt.
- `backend` must be explicitly network-capable.
- `model`, `endpoint`, `credential`, `caller`, `purpose`, capsule validity, and budget must all pass.
- Retry budget is zero by default and no automatic retry is performed.
