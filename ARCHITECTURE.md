# Architecture

## Thesis

RPP is not a new protocol. It is a governance overlay on vanilla ATProto.

ATProto does identity, publication, and propagation. RPP does claim structure, provenance, supersession, challenge, and rendering.

```
ATProto = transport + identity + public record fabric
RPP     = typed governance objects + receipt discipline + subject-centric reviewability
```

## Topology

```
ATProto repos / PDSs / labelers / willing operators
        |
   Ingest adapters
        |
   Rust RPP kernel
   - schema validation
   - signature verification
   - receipt normalization
   - supersession/challenge graph
   - subject state derivation
        |
   Python service/API
   - query
   - publish helpers
   - auth
   - admin
   - archiver control
        |
   Web UI / AppView
   - subject pages
   - record pages
   - activity pages
```

## Core objects

Four record types. No fifth unless the first four prove insufficient.

### Claim

A non-sovereign assertion about a subject.

- "subject emitted X kind of behavior"
- "collection Y contains subject Z"
- "service A asserts category B applies"

A claim says what the issuer thinks is true. Nothing more. Claims never imply automatic downstream action.

### Attestation

A scoped, privileged input from a party with declared standing.

- operator attests fresh-account cohort match
- archive attests snapshot authenticity
- moderation service attests review performed under policy P

Hard rule: attestations are visible as attestations, not rendered as truth. Typed, scoped, TTL'd, challengeable.

### Action

A concrete consequence event.

- label applied
- content hidden
- report forwarded
- claim marked inadmissible

Actions always point back to a claim or attestation chain. No floating punishments.

### Challenge

A first-class dispute object. Carries both `subject` (the ultimate subject of the dispute) and `targetRef` (the specific record being challenged).

- wrong subject
- wrong evidence class
- scope exceeded
- TTL expired
- standing disputed
- action disproportionate

Challenges modify interpretation, not object existence. That's the invariant. The explicit `subject` field means challenges index to subjects directly — no heuristic ref-chasing needed.

## State model

Everything is append-only.

- No edits in place, ever
- Latest non-revoked, non-expired object in a supersession chain is current
- Challenges modify interpretation, not object existence
- Actions remain actions even if later found unsound
- Revoked means revoked, not erased
- Superseded means visible but no longer controlling

Supersession chains preserve intellectual scar tissue, not memory holes.

## Common envelope

All RPP records share a common structure:

```json
{
  "id": "...",
  "kind": "claim | attestation | action | challenge",
  "issuer": "did:...",
  "subject": {
    "type": "did | at-uri | uri | blob-ref | external",
    "value": "..."
  },
  "createdAt": "...",
  "status": "active | withdrawn | superseded | revoked | expired",
  "supersedes": [],
  "relatesTo": [],
  "expiresAt": null,
  "evidenceClass": "...",
  "confidence": "...",
  "body": {}
}
```

## Evidence classes

Constrained enum, forcing claims to admit what kind of footing they have:

- `self_report`
- `direct_observation`
- `linked_public_record`
- `external_archive`
- `operator_attestation`
- `inference`
- `unknown`

This alone is an upgrade over vibes.

## Standing model

Thin for now. Each issuer declares a role:

- `individual`
- `moderation_service`
- `operator`
- `archive`
- `witness`
- `other`

Standing is declaration, not throne. Visible, not magical.

## Ingest paths

### Path A: native ATProto collection ingest

Consume RPP collections from Jetstream / firehose / direct repo sync. For public claims, challenges, actions, and attestations published in repo form.

### Path B: operator attestation API

For cooperating PDS operators and labeler operators who don't want to publish custom records immediately. They POST signed attestation payloads; the service verifies, stores, and optionally republishes them. See [docs/operator-attestation-api.md](docs/operator-attestation-api.md).

## Rust kernel

Narrow receipt engine. Not a giant application.

Responsibilities:
- Lexicon/schema validation
- Issuer verification
- Canonical object normalization
- Supersession chain resolution
- Challenge linkage
- Subject-state materialization

Borrows constitutional patterns from Governor (append-only events, content-addressed identity, explicit lineage, no silent mutation, renderable provenance). Does not import Governor as a dependency.

Content-addressed identity pattern: `id = H(schema_version + kind + subject_hash + evidence_hash + issuer)`. Same inputs, same ID. Timestamp is metadata, not identity.

## Storage

Event store + derived indexes.

**Event store** (SQLite for MVP):
- Append-only canonical objects
- Ingest source and receive timestamp
- Verification result
- Object hash, issuer, subject, links

**Derived indexes**:
- subject_current_claims
- subject_current_attestations
- subject_actions
- subject_open_challenges
- issuer_activity
- object_lineage

**Archive sidecar** (separate concern):
- Tombstones, revoked objects, old superseded versions
- External evidence refs
- Protection against "relay is not archival"

## Renderer

Three views for MVP:

**Subject view** — given a DID or AT-URI, show active claims, attestations, actions, open/resolved challenges, supersession history. This is the main product.

**Record view** — one object with raw content, issuer, related objects, status, lineage.

**Activity view** — recent governance objects by issuer, subject, kind, namespace.

## Trust boundaries

What RPP can do:
- Structure claims
- Show provenance
- Preserve dispute
- Render current status
- Make standing visible
- Separate claim from action

What RPP cannot do by magic:
- Make operator telemetry public
- Prove operator honesty by schema alone
- Solve trust universally
- Become a neutral witness just because it has hashes

Operators contribute attestations. Communities contribute claims/challenges. Services contribute actions. RPP contributes legibility and lineage. That's the lane.

## Lexicon namespace

```
zone.neutral.rpp.claim
zone.neutral.rpp.attestation
zone.neutral.rpp.action
zone.neutral.rpp.challenge
```
