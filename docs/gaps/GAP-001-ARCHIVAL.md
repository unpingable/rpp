# GAP-001: Archival and Witness Guarantees

Status: `open`

## Problem

ATProto relays are explicitly non-archival. The network is not a universal forever-memory by default. RPP needs durable replay and audit guarantees for governance objects, but the social substrate it publishes into does not provide them.

This means:
- Supersession chains can have gaps if relay data is lost
- Challenge/response sequences may become unverifiable after relay rotation
- Subject-centric views may show incomplete history
- "Who said what, when" is only as durable as the archival layer

## Why it matters

Without archival guarantees, RPP degrades from a receipts system to a current-state cache. The whole point of append-only lineage is that the history is replayable. If the history evaporates, you're back to vibes.

Specifically:
- A superseded claim that was later vindicated is invisible if the archive doesn't have it
- A challenge that was never answered looks like it was never filed
- An action that was later reversed can't be proven to have happened

## Current state

The architecture calls for an "archive sidecar" as a separate concern from the main event store. This is the right instinct but has no implementation or spec yet.

## Minimal resolution

1. Define what "archival" means for RPP: which objects, how long, what completeness guarantees
2. Specify the sidecar's ingest, storage, and query contract
3. Decide whether the sidecar is a first-party RPP service or a pluggable interface
4. Define gap detection: how does RPP know when its archive has holes?

This does not need to be a universal witness ledger. It needs to be enough that subject-centric views can show honest history and admit where the gaps are.

## Dependencies

- Core object model (exists)
- Ingest path (not yet implemented)
- Storage model (designed, not implemented)

## Related gaps

- GAP-002 (operator evidence) — operator attestations may need separate archival treatment if they contain restricted-scope data
