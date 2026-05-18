# RPP-000: Receipt Publication Is Not Receipt Validity

**Status:** Foundational design note. Self-limitation document. Cross-links WLP as the validity dependency.

## Purpose

RPP defines how receipt-bearing artifacts become **publicly noticeable** — and how their public-record state is rendered legibly over time.

It does not define what makes those receipts valid, who has authority to issue them, or whether a public record's existence implies anything about its admissibility. Those questions belong to other layers.

This document names the layer split, the core rule that holds the split in place, and the anti-collapse rules that prevent the layers from quietly fusing.

## Non-goals

RPP does **not**:

- decide receipt validity (that's [WLP](https://github.com/unpingable/wlp)'s job)
- define authority to produce artifacts (that's Wicket / Governor's job)
- provide custody guarantees via substrate magic (substrates can lose records; that's a verifier state, not a fix)
- make social circulation authoritative (circulation is downstream of publication, not upstream of validity)

## Layer split

```
Wicket / Governor   →  policy / authority to produce
WLP                 →  receipt validity / boundary admissibility
RPP                 →  publication state / public notice profiles
Substrate           →  one of {static web, ATProto, mirror, archive, ...}
Viewer              →  legibility surface, not judge-priest
```

RPP is **substrate-neutral**. ATProto is *a* substrate profile, not *the* substrate. Profile families RPP anticipates:

| Profile | Role |
|---|---|
| RPP Base | substrate-neutral publication-state vocabulary (this document) |
| RPP Web Profile | boring canonical public receipts on a controlled domain — the baseline |
| RPP ATProto Profile | public-notice and discovery surface with DID identity and Lexicon shape |
| RPP Archive / Mirror Profile | custody, snapshots, durable replay |

The Web Profile is the proving ground (own your DNS, own your receipts, easy verifier, easy archive). The ATProto Profile is the *discovery* surface — the thing that makes receipts socially encounterable. They serve different functions and neither subsumes the other.

Each layer answers exactly one question:

| Layer | Question it answers |
|---|---|
| Wicket / Governor | Should the world produce this artifact? |
| WLP | If produced, is this receipt admissible across a boundary? |
| RPP | Is there a public record that the receipt was issued, and what's its publication state? |
| Substrate (ATProto, etc.) | Where does the public record live, and can it still be fetched? |
| Viewer | Given all of the above, what should a human be shown? |

## Core rule

> **Publication is evidence of notice, not evidence of validity.**

A record's existence in a substrate proves only that something was published. It does not prove the thing was valid, was issued by an authorized party, or has not been revoked since.

The viewer must always show validity and publication state in distinct surfaces. Collapsing them is the failure mode RPP-000 exists to prevent.

## Publication lifecycle

RPP records can be in one or more of the following states:

| State | Meaning |
|---|---|
| `issued` | Publication record was created |
| `observed` | A third party recorded the publication (mirror, archive, indexer) |
| `mirrored` | A durable copy exists outside the originating substrate |
| `superseded` | A later record explicitly supersedes this one |
| `revoked` | A revocation record (or upstream WLP revocation) makes this notice no longer current |
| `unavailable` | Substrate is reachable but record is not currently returned |
| `deleted` | Substrate confirms the record was deleted (where the substrate supports tombstones) |
| `archive_missing` | Mirror/archive expected but cannot be located |
| `substrate_unknown` | Substrate cannot be queried (offline, deprecated, etc.) |

These states are not mutually exclusive (a record can be `issued` *and* `mirrored` *and* `superseded`). They are publication facts. None of them imply anything about the underlying receipt's validity.

## Verifier surfaces

A conforming RPP viewer renders two distinct columns:

```
Receipt validity              | Publication state
(delegated to WLP)            | (RPP's own surface)
------------------------------|------------------------------
valid                         | issued
invalid                       | observed
revoked                       | mirrored
superseded                    | superseded
inadmissible                  | revoked
unknown                       | unavailable
                              | deleted
                              | archive_missing
                              | substrate_unknown
```

The validity column is **populated by WLP verifier output** or by a declared "unknown" if WLP was not consulted. The publication column is RPP's own. A receipt can be `valid` and `unavailable`. A receipt can be `invalid` and `mirrored`. The two columns answer different questions.

A viewer that quietly merges columns — for example, treating "mirrored" as evidence of validity, or treating "invalid" as a reason to suppress the publication record — is broken. The whole point of the two-column model is that one column can never speak for the other.

## Projection vs publication

RPP currently has two profile families. They share record vocabulary but answer different questions and must not impersonate each other.

**RPP Projection Profile** — read-side. Renders observable outputs from third-party observatories (labelwatch, driftwatch, public label streams) as subject-centric chains with visibility gaps. A projection record says: *"this is how the subject appears in public data right now."* It carries no claim that a WLP receipt exists.

**RPP Publication Profile** — write-side. Public notice that a WLP receipt-bearing artifact was issued. A publication record says: *"this receipt was issued by this party at this time, and here is its publication state."* It carries an explicit WLP receipt reference.

The distinction is load-bearing:

> **Projection says "this is how the subject appears." Publication says "this receipt was issued." Those are not the same verb.**

Records from the projection profile must not be treated as publication records, even when they share field names like `subject`, `claim`, or `lineage`. A projection record never carries WLP receipt provenance because it never had any. Treating projection output as issuance is the laundering move this section exists to prevent.

Conforming records carry an explicit profile discriminator (a `profile` field, a distinct lexicon namespace, or equivalent framing) so a verifier can refuse to mistake one for the other.

See [docs/rpp-projection.md](rpp-projection.md) for the projection profile's specific vocabulary and gap categories.

## Anti-collapse rules

Five distinct facts. Each arrow is a laundering move. RPP exists to make the arrows visible, not to traverse them silently.

```
valid              ≠   published
published          ≠   visible
visible            ≠   circulated
circulated         ≠   authoritative
projected          ≠   issued
```

Concretely:

1. **`valid ≠ published`** — A receipt can pass WLP validation without ever being published. A publication record can exist without referencing a valid receipt. The two facts are independent.

2. **`published ≠ visible`** — A record published to a substrate may not currently be fetchable (deletion, substrate outage, retention rotation). The viewer must distinguish `issued` from `currently reachable`.

3. **`visible ≠ circulated`** — A record being fetchable does not mean it has been seen, mirrored, or referenced by anyone. Social circulation is downstream and not RPP's concern.

4. **`circulated ≠ authoritative`** — A widely-circulated record carries no more validity than an obscure one. WLP decides authority; circulation does not.

5. **`projected ≠ issued`** — A projection record showing how a subject appears in public data is not equivalent to a publication record asserting a receipt was issued. Even when they share subject identifiers and vocabulary.

A verifier that silently collapses any of these arrows is no longer an RPP-conforming verifier.

## What RPP may legitimately validate

RPP can validate **publication-profile conformance** — does this record have the required fields for its profile, does its WLP receipt reference (if any) resolve, does its substrate marker make sense.

RPP must **not** validate **receipt admissibility**. It delegates that to WLP and reports WLP's result without modification. If WLP says invalid, RPP reports invalid. If WLP was not consulted, RPP reports `unknown` — never silent default-valid.

The viewer can show:

```
Receipt validity: valid    (source: WLP verifier, version X)
Publication state: mirrored
```

The viewer must never show:

```
Receipt validity: valid    (source: RPP)
```

Because RPP does not have that authority. Growing it would turn the publication profile into a second receipt kernel, which is the haunted-municipal-portal failure mode this document exists to prevent.

## Substrate notes

Each substrate has its own publication-state semantics and failure modes. The RPP Base vocabulary lets the verifier render those failure modes honestly. The substrate does not get to define them out of existence.

**Substrate ranking, today:**

1. **Static web / signed JSON** — best boring baseline. Own domain, own retention, easy verifier, easy archival, no social substrate dependency. Where the Web Profile lives.
2. **ATProto** — best public-notice / discovery substrate. DID identity, Lexicons, social circulation, weird-object affordance. Where the ATProto Profile lives.
3. **Git tag / release** — good for code artifacts, awkward as general public receipt layer.
4. **Transparency log (Rekor-style)** — good *later* for custody / append-only audit, too heavy as the first wedge.
5. **IPFS / content-addressed storage** — tempting; availability is the usual little goblin. Hashes don't host themselves.
6. **ActivityPub** — public/social, but weaker as a structured verifiable-receipt object substrate.

Doctrine line:

> **ATProto is excellent for notice. Weak for custody. Dangerous if mistaken for validity.**

**ATProto-specific affordances:**

- Public, DID-linked, signed user repos. Records are public-by-default and cryptographically authenticated to a DID.
- Lexicon-shaped records — JSON schemas keyed by NSID. Receipt shape is inspectable without needing to know the publishing app.
- `at://` URIs as stable record references. Other apps can point at receipts without holding copies.

**ATProto-specific weaknesses that the verifier must surface:**

- **AT URIs are not content-addressed.** The spec is explicit: AT URIs reference a *path*, not bytes. For stronger references, pair the AT URI with a CID. A verifier that treats an AT URI alone as immutable provenance is broken.
- **Handle-based AT URIs are not durable.** Handles can change; only DID-form URIs are stable across handle rotation.
- **Deletion is supported without tombstones.** Publication state `deleted` is observable only when a separate observer recorded the prior state; otherwise the verifier reports `unavailable` and cannot distinguish "deleted" from "substrate transient." This is why an Archive / Mirror Profile is a real future thing, not optional polish.

Substrate-specific failure modes must be visible in the publication column, never hidden. A substrate cannot earn `valid` for an underlying receipt by being a particularly compliant substrate. That arrow goes the other way: validity comes from WLP, publication state describes what the substrate is doing right now.

## Provenance

This document is the result of a sparring pass between operator, Claude (rpp-side), and ChatGPT (architectural critique) in 2026-05. The "cursed can" object lesson — a playful receipt wrapper that accidentally surfaced the publication/validity seam — is the proximate cause. The doctrine survives the joke.

## What this document does not authorize

- Building a connector
- Editing the lexicon
- Implementing the two-column verifier
- Defining the projection/publication profile discriminator field

Those are downstream decisions. RPP-000 is the layer-split commitment, not the build plan. Any of those downstream artifacts must point back at RPP-000 and the WLP reference for its terms.

The deliverable is this document.
