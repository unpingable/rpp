# RPP

A receipts and reviewability overlay for ATProto.

## What it does

RPP gives governance-relevant claims first-class structure, then renders them as governance objects rather than ordinary social content. It does not replace ATProto and does not try to solve trust by fiat.

Four record types:

- **Claim** — a non-sovereign assertion about a subject (classification, provenance note, behavioral observation)
- **Attestation** — a scoped, privileged input from a party with declared standing (PDS operator, labeler, archive)
- **Action** — a concrete consequence event (label applied, content hidden, report forwarded)
- **Challenge** — a first-class dispute (wrong evidence class, scope exceeded, standing disputed)

These publish as custom ATProto lexicon records under `zone.neutral.rpp.*`, consumed through a dedicated service layer, and rendered subject-centrically — so you can look up any DID or AT-URI and see the full chain of claims, attestations, actions, and challenges in one place.

## What this is not

- Not a new social protocol or ATProto replacement
- Not a moderation oracle or trust-score system
- Not a universal witness ledger — ATProto relays are non-archival
- Not beholden to any single platform operator

## Why third-party

If Bluesky built this, the layer would always be under pressure to become a house view, a liability shield, or a trust-and-safety accessory pretending not to be one. Third-party means:

- No obligation to harmonize with platform incentives
- Standing is made visible, not inherited as authority by default
- Corrections, disputes, and ugly edge cases can be shown honestly
- Operator attestations stay typed and contestable, not portable truth

## Architecture

ATProto provides identity, publication, and distribution. RPP provides claim structure, provenance, supersession, challenge paths, and subject-centric rendering on top.

Five layers:

1. **Publish** — ATProto repos with RPP lexicon records
2. **Ingest** — Jetstream / firehose / direct repo reads / operator attestation API
3. **Kernel** — Rust receipt engine (validate, normalize, index relations, derive subject state)
4. **Service** — Python API (query, publish helpers, auth, archiver)
5. **Render** — Web UI / AppView for subject-centric governance views

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Operator integration

PDS operators and labeler operators can contribute bounded attestations via a POST API without publishing custom records themselves. Attestations are stored as first-class objects, never rendered as profile badges or portable caste markers.

See [docs/operator-attestation-api.md](docs/operator-attestation-api.md) for the integration surface.

## Quick start

```bash
pip install -e ".[dev]"
rpp-viewer
# visit http://localhost:8400
```

The viewer loads example records from `examples/`, indexes them by subject, and serves a subject-centric chain view. Try the subject page for `at://did:plc:alice/app.bsky.feed.post/3abc123` to see a full claim → action → challenge flow.

## Status

Early. The object model, lexicons, example records, subject-state index, and a working subject-chain viewer exist. The Rust kernel, full service layer, and operator attestation ingress do not yet.

## License

Licensed under either Apache-2.0 or MIT, at your option.
