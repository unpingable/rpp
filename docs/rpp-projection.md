# RPP Projection Adjacency

**Status:** Candidate record. Non-binding. Not authorization to build.

This memo names a candidate use of RPP's record vocabulary so the shape can be reviewed before — or instead of — implementation. It does not specify a service, daemon, CLI, or live dependency. It is a mapping memo, not a build plan.

## What this is

RPP is not currently a service implementation, and adoption is not the goal.

Its plausible near-term role is as a **projection vocabulary** for subject-centered reviewability views over the outputs of existing observatories. Specifically:

- **labelwatch** — label emissions, negations, conflicts, per-subject slices, labeler regime signals
- **driftwatch** — claim persistence, fingerprint-based mutation tracking, receipted decisions

The useful artifact this enables is a rendered subject chain showing:

- what public signals exist for a subject
- what claims and actions can be reconstructed from them
- where rationale, challenge, appeal, or review records are not visible in public sources

That last category — the gaps — is the point.

**Load-bearing principle:** the viewer shows where the *record* stops, not where reality stops. RPP is not proving absence of governance. It is proving absence of reviewable public record. Every gap marker is a claim about record visibility, never a claim about what did or did not happen out of view.

## Direction

The relationship is one-way:

```
labelwatch / driftwatch  →  projected through RPP vocabulary  →  rendered subject chain
```

RPP does **not** depend on labelwatch or driftwatch. It does not import their schemas, their storage, or their runtime. The observatories remain self-contained. Projection happens at the read boundary, when a subject view is rendered.

This is the load-bearing constraint: collapse it and you get a beautiful little dependency knot. Keep it one-way and RPP remains a vocabulary that *anything* shaped vaguely like an observatory can project into.

## Inputs

### From labelwatch

Likely sources include the per-subject label slice (e.g. `/v1/whatsonme/{did}` or equivalent) and labeler-side observation surfaces. Per public label structure:

- subject (DID or AT-URI)
- label value
- source labeler (`src`)
- timestamp (`cts`)
- negation flag (`neg`)
- expiration (`exp`) where present
- observed conflicts between labelers
- persistence and flip-flop history

### From driftwatch

Likely sources include the receipted decision ledger and the cluster/fingerprint event stream:

- fingerprint identity for a claim
- mutation events (edits, surface variations, repost graph)
- persistence and burst metrics
- receipted decisions (rule id, fingerprint version, evidence hashes)
- identity enrichment (DID → PDS, account state)

Specific endpoint and field names should be resolved against current labelwatch/driftwatch surfaces at the time of any actual implementation. This memo names the projection, not the wire format.

## Projection mapping

Approximate, not normative:

### Claim
> "subject S has been classified as C by source X at time T"

Projects from: each labelwatch label emission, each driftwatch fingerprint observation that carries a classification.

### Action
> "label applied / negated / expired"
> "decision emitted into ledger"
> "claim observation produced"

Projects from: labelwatch state transitions (apply, negate, expire), driftwatch decision-receipt events. Action authorship stays attached to the actor that produced the change in observable state — labelwatch reports it, the labeler caused it.

### Attestation
> "labelwatch observed this label at this time"
> "driftwatch observed this fingerprint with this persistence profile"

Projects from: the observatories themselves, as third-party non-sovereign witnesses. The attestation type is `external_observation` (Tier 0 provenance per [PROVENANCE-AND-ADAPTERS.md](PROVENANCE-AND-ADAPTERS.md)). Attestations are not re-published as native RPP records; they are projection-time annotations.

### Challenge
> "no public challenge record visible for this claim"
> "no rationale record visible for this label"
> "no appeal trail visible for this action"

Challenges are usually **absences**, not records. The projection emits gap markers, not synthetic challenges. A real challenge record exists only when an actual challenger has published one through some channel that survives projection.

## Gap categories

The viewer's job, if one is ever built, is to highlight what's missing. Standard gap categories:

Each gap is a statement about what is **not visible from public sources at projection time**. None of them assert that the corresponding process did not occur — only that no record of it surfaced.

| Gap | Meaning |
|-----|---------|
| `rationale_absent` | No published rationale visible for this claim/action in this projection |
| `evidence_absent` | No inspectable evidence reference visible for this claim |
| `challenge_absent` | No public challenge record visible for a claim that has had real consequence |
| `review_absent` | No public review record visible for this claim/action |
| `appeal_absent` | No public appeal channel or appeal-use record visible for this subject |
| `provenance_unclear` | Source labeler/operator cannot be authenticated from public data available to this projection |

These are projection-time annotations, not RPP records. They describe what would be needed for the subject's chain to be reviewable end-to-end *on the public record*, not what is.

## What this is NOT

- Not a service spec. There is no `rppd`, no API surface defined here, no schema for a connector to consume.
- Not authorization to build the connector. This memo exists so that *if* a connector is ever built, it has a vocabulary to use. The memo is the deliverable.
- Not a replacement for the operator attestation API ([docs/operator-attestation-api.md](operator-attestation-api.md)) or for native RPP publication. It describes a Tier 0 use of RPP vocabulary over already-public observatory output.
- Not a dependency declaration. labelwatch and driftwatch are named because they are the most natural projection sources today, not because RPP requires them.

**Naming discipline:** if a viewer is ever built, it is an *exhibit*, not a service. Acceptable name: "RPP Subject Chain Viewer." Names to refuse: `rppd`, `rpp-live`, `rpp-connect`, `moderation-receipt-service`, anything ending in `-service` or `-daemon`. Names with daemon eggs in them tend to hatch.

## Open questions

To be ratified locally before any implementation, not preemptively answered here:

1. Should projected attestations carry a stable identifier so they can be challenged downstream, or are they ephemeral by construction (regenerated on each render)?
2. How should conflicting projections from labelwatch and driftwatch be reconciled at render time — show both, prefer one, or annotate the conflict?
3. What is the right boundary between "gap" (absent record) and "claim about absence" (positive record asserting that no review happened)? The second is itself a claim and may itself need challenge surface.
4. If the projected chain becomes the basis for a published RPP record (someone takes the rendered view and publishes it as a `claim` of kind "this is the public reviewability surface for subject S"), does the projection need provenance receipts of its own?

These are not blockers. They are the kind of question that gets answered when there's a current need with testable acceptance criteria.

## Litmus

If "build the connector" enters scope without a current task or external collaborator that requires it, the YAGNI reflex is firing correctly. This memo is the minimum useful record. It exists so that future-us, or someone else, doesn't have to re-derive the projection from scratch.

The connector is not the deliverable. The vocabulary is.
