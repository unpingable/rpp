# WDC ↔ RPP: the admissibility bridge

Status: `candidate` — non-binding. A handle for review, not a build authorization.

## Why this doc exists

Recurring question: *why does RPP exist at all, if it's "just" a readable audit
trail?* This doc pins the answer by placing RPP next to the Witnessed Derivation
Calculus (WDC, `~/git/lean`) and WLP (`~/git/wlp`), so the layer split stops
dissolving every time someone re-pitches "put the validator inside RPP."

Short answer: **RPP is the publication surface for a witnessed derivation. It
carries the path; it does not judge it.** The judging is a different layer, and
the proof that judging is sound is a third layer that never touches the wire.

## The calculus (what's actually in `~/git/lean`)

WDC is the inductive judgment `Lift Kernel Bridge c`:

- **origin** (`Lift.base`): a claim admitted by the floor `K`, no bridge spend.
- **witnessed transition** (`Lift.cross`): extend a derivation across one bridge
  coordinate. The relation *is* the receipt — there is no free cross-rule.

A derivation is therefore exactly a **paid path**: one floor origin plus an
ordered chain of witnessed bridge steps (`PaidFrom`). The load-bearing theorems,
proved schema-level and axiom-free:

| Theorem | What it buys |
|---|---|
| `no_free_lift` | every derivation traces to a *live floor origin* via a paid path — no manufacture |
| `paid_lift_sound` | sound floor + valid bridges ⇒ sound conclusion |
| `cut_admissible` | two derivations compose without inventing authority |
| `lift_floor_mono` | revocation is a **floor** operation (revoke origins ⇒ shrink the derivable set) |

These are facts about the *calculus*, universally quantified, proved **once**.

## The layer map

| Layer | Component | Job |
|---|---|---|
| Proof | **WDC** (`~/git/lean`) | proves the *wire format* is non-manufacturing and sound. Offline, once. |
| Validator | **WLP** (`~/git/wlp`) | per-artifact: re-checks each path step against the oracle; refuses or degrades, never launders |
| Oracle | **nq** | supplies floor membership (live origins) + bridge witnesses |
| Decision | **Governor / Wicket** | admits or drops the suspended action |
| Publication | **RPP** | carries the witnessed path as governance records; renders it reviewable |

The common pitch ("drop the sequent calculus *into* RPP as a gate") collapses
three of these into one. It is wrong in three specific ways, below.

## Correction 1 — you never ship the Lean proof

The tempting question is "embed the raw Lean derivation tree in the RPP JSON, or
compile it down?" Neither. That's a category error.

The Lean proof is about the *calculus* ("any witnessed path is sound and
non-manufacturing") — proved once, never serialized. What travels per action is
a **witnessed path**, not a proof tree:

- one **origin id**, asserted ∈ floor, and
- an ordered list of **bridge coordinates**, each carrying its own witness/receipt.

The verifier walks the path against nq: *is this origin live? does this bridge's
witness hold?* If every atom checks, `no_free_lift` already guarantees — proved,
not re-derived — that nothing was manufactured. No Lean toolchain at the gate, no
dependent-type re-checking, no proof-tree on the wire. The hard proof is a
theorem *about* the format, not a payload *in* it. That is what keeps the gate
lazy.

## Correction 2 — the path is RPP's subject-chain, not a new record

RPP already has a subject-chain (`examples/`). The witnessed path *is* that
chain, read as a WDC derivation. No fifth record type (respects the `Don't`):

| WDC element | RPP record |
|---|---|
| floor origin / derived node | **claim** (origins = floor; conclusion = derived `c`) |
| bridge witness | **attestation** (privileged input, never a verdict — exactly `Bridge`'s witness) |
| gated effect | **action** (cites a derived `c`; "no claim self-executes" = never cites a bare floor base) |
| revocation | **challenge** (revokes an origin = `lift_floor_mono`, a floor operation) |

"Dropping the calculus into RPP" means: prove that RPP's existing chain, when each
link carries a witness, **is** a paid `Lift` path — then `no_free_lift` says the
chain can't launder standing. Nothing new on the wire; a *reading* plus a checker.

## Correction 3 — the gate does not live in RPP

RPP invariant 3: *attestations are privileged inputs, never final judgments — no
portable truth.* A pass/drop gate inside RPP turns it into the moderation oracle
it is defined not to be, and collapses the projection-vs-decision split already
ratified (RPP-000; projection memo).

Keep the split: **RPP carries the path, WLP checks it, Governor admits/drops, nq
witnesses, WDC proves the checker sound.** This is also WLP's own boundary —
its README puts the decision engine in "Wicket / Governor territory," not in the
wire format.

## Two honest caveats

1. **Soundness is conditional.** `paid_lift_sound` assumes a sound floor (`hK`)
   and valid bridges (`hB`). The calculus proves nothing leaks *past* those
   hypotheses; it relocates trust to checkable atoms (origin admission + witness
   validity). The win is "trust is auditable at named seams," not "unconditional
   security." Any "perfectly secure" phrasing hides the hypotheses.

2. **No single-use authority yet.** `Witnessed/Sequent.lean` says so itself: the
   layer is "not occurrence-sensitive and cannot express resource consumption or
   denial of contraction." Spend-once capabilities (a receipt authorizing exactly
   one action) are **not** modeled — the calculus is structural, not
   substructural. See open candidate below.

## What the lexicons reveal

Reading the four lexicons against "carries the path, does not judge it" surfaced
three things:

1. **The "does not validate itself" fence was on the wrong side — now fixed.**
   It cannot be a record field (a producer can omit or lie about
   `validatesItself: false`). It is a **reader law**. `src/rpp/index.py` used to
   echo the record's self-authored `status` as the only state axis. It now splits:
   `lifecycle` (record-authored: active/withdrawn/superseded/...) vs
   `validity_status` (`unchecked` until a `Validity` checker receipt is attached;
   self-authored status can never promote it). The viewer and `/api/subject` show
   both axes. Tests in `tests/test_index.py` pin the invariant.

   > **Doctrine: RPP records may assert lifecycle. Only readers may report
   > check-state, and only by citing a checker.** The form can say "filed,"
   > "withdrawn," "superseded." It cannot say "the court ruled in my favor"
   > unless it attaches the court.

2. **The witnessed-path edges are spelled five ways** — `causeRefs` (action),
   `relatedClaims` (attestation), `evidenceRefs` (claim), `targetRef` (challenge),
   `supersedes` (all). For "subject-chain = WDC path" to hold, a reader needs one
   uniform notion of **derivation edge** (a paid bridge step), kept distinct from
   **supersession** (temporal replacement) and **evidence pointer** (cited, not yet
   witnessed) and **challenge** (attack/revocation). Until that normalization
   exists, the WDC reading is unpaid, not false. See open candidate below.

3. **Some `status` values are smuggled verdicts.** `withdrawn`/`superseded` are
   author acts (safe to assert). `revoked`/`expired`/`upheld`/`rejected`/
   `inadmissible` are computed, time-dependent, or adjudicated — the reader now
   flags them as `lifecycle_is_verdict_like` so they render as *claimed*, not
   checked. `actionType: claim_marked_inadmissible` is acceptable only as *notice
   that a named authority decided elsewhere*, never as RPP deciding.

## Open candidates (named, not authorized)

- **Witnessed-path checker as a profile.** A conformance reading + checker that
  validates an RPP subject-chain *as* a `Lift` path against nq. Forcing case:
  first real RPP-gated action that a Governor must admit/drop. Until then, this
  doc is the handle.
- **Substructural layer for single-use.** Occurrence-sensitive / linear extension
  of WDC so RPP can express once-only capabilities. Forcing case: a gated action
  whose authority must be consumed, not just held. Lives in `~/git/lean` if built,
  not here.
- **Uniform derivation-edge normalization** (finding 2). A reader-level pass that
  collapses `causeRefs`/`relatedClaims`/`evidenceRefs`/`targetRef`/`supersedes`
  into typed edges (`bridge` | `evidence_pointer` | `temporal_replacement` |
  `external_notice`). Forcing case: the first checker that walks an RPP chain *as*
  a WDC paid path. No new wire fields needed — it's a reading.

## The forcing specimen (the only MVP worth building)

RPP earns its keep iff an **external** reader needs to reconstruct a contested
claim-chain without the publisher's runtime, repo, logs, or trust context. That
test is already the ratified direction — RPP is the projection profile for
observatory output (labelwatch / driftwatch), not a standalone system. The
machinery already exists (`src/rpp/app.py` + the subject viewer). So the open
move is **not build, it's specimen**: feed one real observed case (one subject,
one claim/event, one attestation/capture, one action/label, one challenge), render
it, and ask — *is this easier to inspect and contest than the raw source
artifacts?* If yes, RPP lives as the observatory's publication profile. If no,
archive as prior art without guilt. No daemon, no adoption pitch, no validator
inside RPP.

## Provenance

Reconstructed 2026-06-30 from a layer-collapse pitch ("put the sequent calculus
inside RPP as an active gate"). The structural intuition was right; transport,
placement, and the security claim were not. This doc exists so the corrected
version is the one that calcifies.
