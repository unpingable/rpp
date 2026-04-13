# RPP

A receipts and reviewability overlay for ATProto.

## The problem

Someone labels your post on Bluesky. Your reach drops. You don't know who made the claim, what evidence they had, or whether anyone reviewed it. You can't see the chain of reasoning. You can't dispute it. The label just... is.

On the other side: an operator notices a batch of accounts created in the same minute. They flag it internally, but that signal lives in a private log. Nobody outside the operator can see it, reference it, or challenge it. If a downstream service acts on it, there's no visible link between the signal and the consequence.

Moderation decisions happen. Consequences land. But the *receipts* — who said what, on what basis, with what effect — are invisible, inconsistent, or locked inside the platform that made the call.

## What RPP does

RPP publishes governance decisions as structured, reviewable ATProto records. Four record types:

- **Claim** — someone says something about a subject ("this post cites a retracted study")
- **Attestation** — an operator contributes a scoped signal ("these accounts were created together")
- **Action** — a service makes something happen ("post hidden from default feed")
- **Challenge** — someone disputes a claim or action ("that study wasn't retracted for the reason you say")

Claims don't self-execute. Actions point back to the claims that caused them. Challenges are first-class objects, not support tickets. Nothing gets silently edited — old records stay visible as superseded, not deleted.

The result: for any post, account, or URI, you can pull up the full chain — who claimed what, who acted on it, who disputed it, and what the current state is.

**[See the full story in one walkthrough.](examples/subject-chain.md)** A post gets published, labeled, hidden, attested, and challenged — five steps, all legible.

## Why third-party

If Bluesky built this, it would always be under pressure to become a house view or a liability shield. Third-party means:

- No obligation to harmonize with platform incentives
- Standing is visible, not inherited as default authority
- Corrections and ugly edge cases can be shown honestly
- Operator signals stay typed and contestable, not portable truth

## Architecture

ATProto handles identity, publication, and distribution. RPP adds claim structure, provenance, challenge paths, and subject-centric rendering on top.

Five layers: publish (ATProto records) → ingest (firehose, operator API, adapters) → kernel (Rust validation and indexing) → service (Python API) → render (subject-centric web views).

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full picture.

## Quick start

```bash
pip install -e ".[dev]"
rpp-viewer
# visit http://localhost:8400
```

The viewer loads example records, indexes them by subject, and serves a chain view. Try the subject page for `at://did:plc:alice/app.bsky.feed.post/3abc123` to see a claim → action → challenge flow.

## Reading order

1. **This README** — the problem and the shape of the solution
2. **[examples/subject-chain.md](examples/subject-chain.md)** — one complete lifecycle, start to finish
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** — record types, state model, ingest paths, trust boundaries
4. Then, depending on what you're building:
   - Integrating operator signals? → [docs/operator-attestation-api.md](docs/operator-attestation-api.md)
   - Importing from existing systems (Ozone, labelers)? → [docs/PROVENANCE-AND-ADAPTERS.md](docs/PROVENANCE-AND-ADAPTERS.md)
   - Understanding the design philosophy? → [docs/RATIONALE.md](docs/RATIONALE.md)
   - Open problems (federation, archival)? → [docs/gaps/](docs/gaps/)

## Status

Early. The object model, lexicons, example records, subject-state index, and a working subject-chain viewer exist. The Rust kernel, full service layer, and operator attestation ingress do not yet.

## License

Licensed under either Apache-2.0 or MIT, at your option.
