# Operator Attestation API

## Purpose

PDS operators and labeler operators can contribute bounded attestations into RPP without publishing custom ATProto records themselves. The API accepts signed attestation payloads, verifies them, and stores them as first-class RPP attestation objects.

## Who uses this

- **PDS operators** attesting signals from their own infrastructure (account creation patterns, recovery events, review completions)
- **Labeler operators** attesting categorization outcomes, review results, policy applications
- **Archive services** attesting snapshot authenticity, content preservation

## Flow

```
PDS / labeler operator
   | signed attestation payload
   v
RPP ingest API
   | verify issuer + schema + signature + TTL
   v
Rust kernel
   | normalize + store + index
   v
Renderer
   | show as typed attestation on subject view
```

## Payload

```json
{
  "issuer": "did:plc:operator-example",
  "subject": {
    "type": "did",
    "value": "did:plc:user-example"
  },
  "attestationType": "batch_creation_pattern",
  "basis": "operator_telemetry",
  "scope": "accounts created within same 60s window from same signup flow",
  "confidence": "medium",
  "issuedAt": "2026-04-12T14:00:00Z",
  "expiresAt": "2026-07-12T14:00:00Z",
  "supersedes": null,
  "signature": "base64..."
}
```

### Field semantics

| Field | Required | Description |
|-------|----------|-------------|
| `issuer` | yes | DID of the attesting operator |
| `subject` | yes | DID, AT-URI, or external ref being attested about |
| `attestationType` | yes | What is being attested (constrained vocabulary, extensible) |
| `basis` | yes | Evidence class: `operator_telemetry`, `direct_observation`, `external_archive`, etc. |
| `scope` | yes | Human-readable description of what exactly is being attested and what is not |
| `confidence` | yes | `low`, `medium`, `high` |
| `issuedAt` | yes | ISO 8601 UTC timestamp |
| `expiresAt` | no | TTL — no eternal stink clouds |
| `supersedes` | no | ID of a prior attestation this one replaces |
| `signature` | yes | Cryptographic signature over the canonical payload |

### Attestation types (initial vocabulary)

- `batch_creation_pattern` — accounts created in suspicious temporal/behavioral cluster
- `account_recovery_event` — account recovered through operator-assisted process
- `operator_review_complete` — manual review performed under stated policy
- `content_authenticity` — operator attests content provenance
- `service_relationship` — operator attests relationship between accounts/services

This vocabulary is extensible. New types should be documented before use.

## Verification

On receipt, the service:

1. Validates the payload against the attestation schema
2. Resolves the issuer DID and retrieves signing keys
3. Verifies the signature against the canonical payload
4. Checks TTL is reasonable (not eternal, not already expired)
5. Stores the normalized attestation with ingest metadata
6. Indexes by subject for the subject view

## Hard rules

- **Append-only**: attestations are never silently mutated. Corrections are new attestations that supersede the old one.
- **Typed**: always rendered as "operator X attests Y under conditions Z", never as "Y is true."
- **Challengeable**: like any RPP object, attestations can be challenged.
- **No raw signals**: no IP addresses, session tokens, device fingerprints, or other raw telemetry in the payload. The attestation is a typed conclusion, not a data dump.
- **No profile badges**: attestations are never rendered as portable profile-level markers by default. They are inputs to subject-centric views, not caste stamps.

## Republication

The RPP service may optionally republish received attestations as ATProto records in its own service repo, making them available through normal collection ingest paths. The original operator signature is preserved.
