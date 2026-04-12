# CLAUDE.md — Instructions for Claude Code

## What This Is

rpp: ATProto-native receipts and reviewability overlay for governance-relevant claims.

Four record types (claim, attestation, action, challenge) published as custom ATProto lexicon records, consumed through a dedicated service layer, rendered as governance objects instead of social posts.

## What This Is Not

- Not a social protocol or ATProto replacement
- Not a moderation oracle, trust-score system, or anti-abuse detector
- Not a Governor dependency — borrows constitutional patterns (append-only, content-addressed identity, supersession, first-class dispute), does not import Governor code

## Invariants

1. Claims and actions are always separate objects — no claim self-executes
2. Append-only: no silent mutation, superseded objects remain visible as superseded
3. Attestations are privileged inputs, never final judgments — no portable truth

## Quick Start

```bash
pip install -e ".[dev]"
pytest
```

## Project Structure

- `lexicons/` — ATProto lexicon definitions (zone.neutral.rpp.*)
- `examples/` — Example records and subject-chain walkthrough
- `docs/` — Architecture, operator API spec, gap specs, archived prior-art specs
- `src/` — Rust kernel (receipt engine) + Python service layer (TBD)
- `tests/` — pytest suite

## Conventions

- License: Apache-2.0 OR MIT
- Rust for kernel invariants, Python 3.10+ for service/glue
- Testing: pytest for Python, cargo test for Rust
- ATProto lexicon namespace: zone.neutral.rpp.*

## Don't

- Don't add a fifth record type without proving the first four are insufficient
- Don't build trust scores, reputation ranks, or standing priesthood
- Don't import Governor as a dependency — steal shapes, not modules
