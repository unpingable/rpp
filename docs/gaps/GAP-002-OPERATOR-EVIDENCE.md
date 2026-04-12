# GAP-002: Operator Evidence Boundary

Status: `open`

## Problem

The strongest anti-abuse and governance signals live on the operator side: signup telemetry, session patterns, network correlates, authentication events. ATProto's public repo model does not make this data available, and it shouldn't — much of it is legitimately private.

RPP's operator attestation API lets operators contribute bounded conclusions, but the underlying evidence stays on their side. This creates an irreducible asymmetry: the attestation says "I saw X" but the community cannot independently verify X.

## Why it matters

If operator attestations are accepted at face value, RPP becomes a laundering service for operator authority. If they're rejected as unverifiable, the strongest signals are excluded and the system runs on public-surface vibes only.

Neither extreme works. The gap is: how does RPP handle evidence it can reference but not inspect?

## Current state

The operator attestation API spec requires:
- Typed attestations (never rendered as portable truth)
- Explicit basis/evidence class
- Scope declarations
- TTL
- Challengeability

This is the right interface discipline. But the spec does not yet address:
- How challenges against operator attestations are resolved when the evidence is private
- Whether operator attestations should carry different confidence ceilings than public-evidence claims
- How to detect and surface patterns of operator attestation abuse
- What happens when two operators make contradictory attestations about the same subject

## Minimal resolution

1. Define confidence ceiling rules: operator attestations with private evidence can declare confidence, but renderers may apply a discount or distinct visual treatment
2. Define challenge resolution for private-evidence attestations: what constitutes a valid challenge, and what counts as a response
3. Define contradiction handling: when operators disagree, how is the divergence surfaced?
4. Consider corroboration: can multiple independent operator attestations about the same subject strengthen the signal without revealing the underlying evidence?

This does not need to solve the epistemology of private knowledge. It needs to make the asymmetry visible and give downstream consumers enough structure to form their own trust judgments.

## Dependencies

- Operator attestation API (designed)
- Challenge record type (exists in lexicon)
- Renderer subject view (not yet implemented)

## Related gaps

- GAP-001 (archival) — operator attestations may need separate archival/retention rules
