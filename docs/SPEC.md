# Receipt Publication Protocol (RPP)

A protocol for signed publication, typed reference, capability-scoped access, and externally observable governance.

## 0. Design stance

RPP is not a "social protocol." It is a **publication and consequence protocol**.

It is built around four assumptions:

1. **Identity, publication, discovery, and governance are different layers.**
2. **Claims about content are not the same thing as actions taken on content.**
3. **Views are projections, not reality.**
4. **If a system can affect visibility, access, or standing, it must emit evidence of that fact.**

## 1. Non-goals

RPP does **not** try to define:

* one canonical feed
* one canonical moderation regime
* one canonical identity provider
* one canonical transport
* one canonical app UX

It defines a grammar. It does not define the empire.

---

# 2. Core entities

## 2.1 Actor

A stable identifier with signing authority.

Required fields:

* `actor_id`
* `current_keys`
* `delegations`
* `service_records`
* `rotation_chain`

An Actor answers only:

* who may sign
* where its log is fetchable
* what changed
* who was delegated what authority

It does not smuggle in discovery, reputation, or ranking.

## 2.2 Log

An append-only sequence of signed envelopes for one Actor.

Required properties:

* strictly monotonic `seq`
* hash-linked `prev`
* signed by an authorized key
* fetchable as full log, range, snapshot, or tail

The Log establishes:

* authorship
* local order
* replayability

It does **not** establish universal order.

## 2.3 Object

An immutable, content-addressed payload.

Required fields:

* `object_id` or content hash
* `schema`
* `body`
* `created_at`
* optional `media_refs`

Examples:

* post
* profile fragment
* article
* image manifest
* policy text
* evidence bundle

## 2.4 Ref

A typed edge between entities.

Required fields:

* `source`
* `target`
* `rel`

Examples of `rel`:

* `reply_to`
* `quotes`
* `cites`
* `annotates`
* `supersedes`
* `depends_on`
* `evidence_for`
* `targets_actor`
* `targets_object`

## 2.5 Claim

An assertion made by an issuer about a subject.

Required fields:

* `claim_id`
* `issuer`
* `subject`
* `claim_kind`
* `value`
* `confidence_bps` (integer, 0–10000 basis points)
* `evidence_refs`
* `policy_ref`
* `asserted_at`

Examples:

* classification label
* authenticity assertion
* provenance note
* identity linkage
* spam claim
* policy-violation claim

A Claim says what the issuer thinks is true. Nothing more.

## 2.6 Recommendation

A suggested consequence derived from one or more Claims.

Required fields:

* `recommendation_id`
* `issuer`
* `subject`
* `recommended_action`
* `scope`
* `rationale_refs`
* `policy_ref`
* `recommended_at`

This is optional but useful. It keeps "what should happen" distinct from both claim and execution.

## 2.7 Action

A concrete operation taken by a service.

Required fields:

* `action_id`
* `issuer`
* `subject`
* `action_kind`
* `effective_scope`
* `effective_at`
* `cause_refs`
* `policy_ref`

Examples:

* downranked in view X
* hidden from guest access
* grant revoked
* object quarantined
* account write-disabled
* fetch denied

If consequence changed, an Action object exists. No silent hand-waving.

## 2.8 Receipt

Evidence that an observation, Action, or state transition occurred.

RPP Receipts use **WLP v0 receipt format** as the witness substrate.
WLP provides canonicalization, hash linkage, signatures, offline
verification, coverage/gap semantics, and repair semantics. RPP
defines *when* receipts are required and *what* they witness; WLP
defines *how* they are formed, linked, verified, and repaired.

An RPP Receipt is a WLP v0 receipt where:

* `subject` identifies the observed event or state change
* `proposal.kind` is `"observation"` or `"action_witness"`
* `evidence[]` contains witness artifacts (snapshots, query proofs)
* `coverage` declares what was and was not observed
* `adjudication` records the integrity assessment

Required RPP-specific fields (carried inside the WLP envelope):

* `subject.kind`: the RPP entity type being witnessed
* `evidence[].ref`: witness artifacts (snapshots, proofs)
* `coverage.gap_flags`: what was not observed

Optional:

* `replay_token`: opaque token for replaying the observation
* `related_receipts`: links to prior receipts for the same subject

Receipts are the protocol's anti-kayfabe layer.

## 2.9 Grant

A capability issued by one actor or service to another.

Required fields:

* `grant_id`
* `grantor`
* `grantee`
* `operations`
* `scope`
* `expiry`
* `visibility`
* `transferability`

Examples:

* read object set
* mirror actor log
* consume relay stream
* publish on behalf of actor
* moderate within scope Y

## 2.10 View

A declared projection over logs, objects, claims, and actions.

Required fields:

* `view_id`
* `issuer`
* `sources`
* `selection_policy`
* `ranking_policy`
* `claim_inputs`
* `freshness`
* `known_omissions`
* `generated_at`

A View is a projection and must identify itself as such.

## 2.11 Challenge

A first-class dispute object.

Required fields:

* `challenge_id`
* `challenger`
* `target_ref`
* `grounds`
* `opened_at`

Optional:

* `evidence_refs`
* `requested_remedy`
* `deadline`

Appeals must become protocol-visible objects, not tickets in an invisible Zendesk mausoleum.

---

# 3. Envelope format

Everything in a Log is a signed envelope.

```json
{
  "v": 1,
  "kind": "publish|claim|recommend|action|receipt|grant|view|challenge|retract",
  "actor": "actor:example:123",
  "seq": 1042,
  "prev": "hash:abc123",
  "ts": {
    "authored_at": "2026-04-02T03:14:15Z",
    "published_at": "2026-04-02T03:14:20Z"
  },
  "body": "cid:...",
  "refs": [
    {"rel": "reply_to", "target": "cid:..."},
    {"rel": "evidence_for", "target": "cid:..."}
  ],
  "audience": "public|grant:xyz",
  "capability": "grant:xyz",
  "sig": {
    "alg": "ed25519",
    "kid": "key:1",
    "value": "base64..."
  }
}
```

### Envelope rules

* `seq` MUST increase by 1 within a log.
* `prev` SHOULD hash-link to prior envelope.
* `body` MUST be content-addressed.
* `sig` MUST validate against actor key or delegated key.
* `kind` MUST not imply hidden consequence. Consequence requires an `action`.

---

# 4. Time model

RPP treats time as plural.

Recognized timestamps:

* `authored_at`
* `published_at`
* `observed_at`
* `effective_at`
* `superseded_at`
* `revoked_at`

No collapsing these into one magic timestamp. Ordering is part of the politics.

---

# 5. Trust model

Trust is decomposed, not mystical.

A client or service evaluates five separate questions.

## 5.1 Authenticity

Was this envelope signed by a valid current or delegated key?

## 5.2 Standing

Was the issuer authorized to make this kind of claim or action?

A random relay may observe. It may not have standing to enforce.

## 5.3 Scope

Did the relevant Grant actually allow this operation over this subject?

## 5.4 Evidence

Does the claim or action cite accessible evidence or declared policy?

## 5.5 Divergence

Do other trusted issuers materially disagree?

Trust is therefore not binary. A subject may be:

* authentic but low-standing
* standing-bearing but low-evidence
* high-confidence but divergence-heavy

That is the point.

---

# 6. Transport model

RPP allows multiple transport modes.

Supported patterns:

* actor-log pull
* relay subscription
* mirror sync
* snapshot + tail replay
* bounded range fetch

No sacred firehose.

A relay is a convenience, not ontology.

---

# 7. Observatory requirements

Any service that changes visibility, access, ranking, or standing SHOULD emit observability artifacts.

Minimum observatory outputs:

## 7.1 Identity events

* key rotated
* delegation added
* delegation revoked
* service record changed

## 7.2 Publication events

* object published
* object superseded
* object withdrawn
* log gap detected

## 7.3 Claim events

* claim asserted
* claim amended
* confidence changed
* claim withdrawn

## 7.4 Action events

* ranking changed
* visibility changed
* access denied
* account limited
* grant issued
* grant revoked

## 7.5 View events

* index coverage changed
* freshness degraded
* policy version changed
* omission declared

## 7.6 Transport events

* relay lag
* mirror divergence
* replay completed
* partial snapshot served

## 7.7 Challenge events

* challenge opened
* challenge acknowledged
* challenge resolved
* remedy applied
* remedy denied

A system may still be closed in places, but it must at least confess where the closures are.

---

# 8. Normative rules

* **Claims and Actions MUST be representable separately.**
* **Views MUST declare source set and policy digest.**
* **Grants MUST declare scope and expiry.**
* **Actions affecting third-party visibility SHOULD emit Receipts.**
* **Known omissions SHOULD be represented explicitly where possible.**
* **No layer may imply canonicality merely by being widely used.**

---

# 9. Example moderation flow

A post is published:

* `publish` envelope -> Object

A labeler classifies it:

* `claim` envelope -> "misleading", confidence 0.72, evidence refs

A feed service downranks it:

* `recommend` envelope -> suggested demotion
* `action` envelope -> demoted in View X

An observatory sees the change:

* `receipt` envelope (WLP v0 format) -> observed in View X at time T

A user disputes it:

* `challenge` envelope -> cites counter-evidence

Now the chain is legible:
**who said what, on what basis, with what consequence, and when.**

---

# 10. One-sentence summary

**Identity signs logs; logs publish objects; objects attract claims; claims may generate recommendations; services take actions; actions emit receipts; views project partial worlds; users choose whom to trust.**

---

# 11. Wire schemas

These are intentionally small. The rule is: **no field gets to smuggle in an adjacent layer's authority**.

## 11.1 Actor document

```json
{
  "actor_id": "actor:example:alice",
  "version": 7,
  "keys": [
    {
      "kid": "key:alice:root:7",
      "alg": "ed25519",
      "public_key": "base64...",
      "purpose": ["sign_log", "rotate_keys"],
      "valid_from": "2026-04-02T00:00:00Z"
    }
  ],
  "delegations": [
    {
      "delegate": "actor:svc:alice-mobile",
      "kid": "key:alice:mobile:2",
      "purpose": ["sign_log"],
      "scope": {
        "kinds": ["publish", "retract"],
        "audience": ["public"]
      },
      "issued_at": "2026-04-02T00:10:00Z",
      "expires_at": "2026-07-01T00:00:00Z"
    }
  ],
  "service_records": [
    {
      "service_id": "svc:alice:primary-log",
      "role": "log_origin",
      "endpoint": "https://alice.example/log",
      "declared_capabilities": ["range_fetch", "snapshot", "tail"]
    },
    {
      "service_id": "svc:alice:object-store",
      "role": "object_origin",
      "endpoint": "https://alice.example/obj"
    }
  ],
  "prev_actor_doc": "cid:prev-version",
  "signed_at": "2026-04-02T00:00:00Z",
  "sig": {
    "kid": "key:alice:root:7",
    "alg": "ed25519",
    "value": "base64..."
  }
}
```

### Notes

* No reputation fields.
* No discovery hints pretending to be identity.
* No "trust score."
* Service records are declarative, not authoritative.

Identity says where to look, not what to believe.

## 11.2 Log envelope

```json
{
  "v": 1,
  "envelope_id": "cid:env-1042",
  "kind": "publish",
  "actor": "actor:example:alice",
  "seq": 1042,
  "prev": "cid:env-1041",
  "body": "cid:obj-post-555",
  "refs": [
    {
      "rel": "reply_to",
      "target": "cid:obj-post-444"
    }
  ],
  "audience": {
    "mode": "public"
  },
  "ts": {
    "authored_at": "2026-04-02T03:14:15Z",
    "published_at": "2026-04-02T03:14:20Z"
  },
  "sig": {
    "kid": "key:alice:mobile:2",
    "alg": "ed25519",
    "value": "base64..."
  }
}
```

## 11.3 Object schema: post

```json
{
  "object_id": "cid:obj-post-555",
  "schema": "rpp.object.post.v1",
  "author": "actor:example:alice",
  "body": {
    "text": "Post body here.",
    "lang": "en"
  },
  "attachments": [
    {
      "kind": "image",
      "target": "cid:img-777"
    }
  ],
  "created_at": "2026-04-02T03:14:15Z"
}
```

## 11.4 Claim schema

```json
{
  "claim_id": "cid:claim-900",
  "schema": "rpp.claim.classification.v1",
  "issuer": "actor:labeler:watchtower",
  "subject": {
    "kind": "object",
    "target": "cid:obj-post-555"
  },
  "claim_kind": "misleading_context",
  "value": {
    "polarity": "cautionary",
    "domain": "public_health"
  },
  "confidence_bps": 7200,
  "evidence_refs": [
    "cid:evidence-2001",
    "cid:evidence-2002"
  ],
  "policy_ref": "cid:policy-watchtower-v12",
  "asserted_at": "2026-04-02T03:17:00Z"
}
```

### Notes

* `claim_kind` is not an action.
* `value` can hold a typed ontology, but it stays a claim.
* Confidence is in basis points (7200 = 72%) because ambiguity is real and floats are goblins.
* Evidence and policy are linkable, not theatrical.

## 11.5 Recommendation schema

```json
{
  "recommendation_id": "cid:rec-901",
  "schema": "rpp.recommendation.visibility.v1",
  "issuer": "actor:labeler:watchtower",
  "subject": {
    "kind": "object",
    "target": "cid:obj-post-555"
  },
  "recommended_action": "deprioritize",
  "scope": {
    "applies_to": ["view:feed:default"],
    "duration": "P7D"
  },
  "rationale_refs": [
    "cid:claim-900"
  ],
  "policy_ref": "cid:policy-watchtower-v12",
  "recommended_at": "2026-04-02T03:17:05Z"
}
```

## 11.6 Action schema

```json
{
  "action_id": "cid:act-333",
  "schema": "rpp.action.visibility.v1",
  "issuer": "actor:viewsvc:mainfeed",
  "subject": {
    "kind": "object",
    "target": "cid:obj-post-555"
  },
  "action_kind": "deprioritized",
  "effective_scope": {
    "view_id": "view:feed:default",
    "audiences": ["guest", "logged_in"]
  },
  "effective_at": "2026-04-02T03:17:12Z",
  "cause_refs": [
    "cid:claim-900",
    "cid:rec-901"
  ],
  "policy_ref": "cid:mainfeed-policy-v8"
}
```

### Important

The feed service owns the action, not the labeler. **Authorship of consequence** stays attached to the actor that actually changed visibility.

No more "the label did it." No. You did it.

## 11.7 Receipt schema

RPP Receipts use the WLP v0 receipt envelope. The RPP-specific content
lives in the standard WLP fields (`subject`, `proposal`, `evidence`,
`adjudication`, `coverage`). Canonicalization, hashing, signing, chain
linkage, and verification follow the WLP receipt-v0 spec.

```json
{
  "schema": "wlp.receipt/v0",
  "receipt_id": "wr_...",
  "content_hash": "sha256:...",
  "receipt_hash": "sha256:...",
  "prev_receipt_hash": "sha256:...",

  "subject": {
    "kind": "rpp.action",
    "id": "cid:act-333",
    "scope": ["view:feed:default"],
    "locator": "cid:obj-post-555"
  },

  "proposal": {
    "kind": "observation",
    "summary": "Observed deprioritization of obj-post-555 in default feed",
    "requested_by": {
      "actor_type": "system",
      "actor_id": "actor:obs:publicwatch"
    },
    "declared_commitment": "C1",
    "derived_commitment": "C1"
  },

  "evidence": [
    {
      "evidence_id": "ev_snapshot_01",
      "kind": "external_observation",
      "ref": "cid:snapshot-view-default-031720",
      "digest": "sha256:...",
      "captured_at": "2026-04-02T03:17:20Z",
      "producer": {
        "actor_type": "system",
        "actor_id": "actor:obs:publicwatch"
      },
      "freshness": {
        "status": "fresh",
        "observed_age_ms": 8000,
        "max_age_ms": 60000
      },
      "authenticity_basis": {
        "mode": "external_black_box"
      },
      "admissibility": {
        "standing": "accepted",
        "role": ["existence_proof"],
        "basis": [
          {"rule_id": "obs.snapshot", "reason_code": "matches_subject"}
        ],
        "sufficiency_weight": "strong"
      }
    }
  ],

  "adjudication": {
    "constitution_digest": "sha256:publicwatch-policy-v3",
    "decision": "observe_only",
    "decision_basis": [
      {"rule_id": "obs.witnessed", "reason_code": "quorum_met"}
    ],
    "temporal": {
      "decision_at": "2026-04-02T03:17:20Z"
    }
  },

  "outcome": {
    "status": "executed",
    "outcome_ref": "cid:rcpt-444"
  },

  "coverage": {
    "coverage_class": "partial",
    "gap_flags": ["out_of_band_action"]
  },

  "related_receipts": [],
  "signatures": [
    {
      "signer": "actor:obs:publicwatch",
      "sig_type": "ed25519",
      "sig": "base64..."
    }
  ]
}
```

Receipts should be able to say both what was observed and what was **not** observed.
The `coverage` block makes this explicit: `gap_flags` declares known blind spots,
and `coverage_class: "partial"` is the honest default for external observation.

## 11.8 Grant schema

```json
{
  "grant_id": "cid:grant-111",
  "schema": "rpp.grant.capability.v1",
  "grantor": "actor:example:alice",
  "grantee": "actor:viewsvc:friendsfeed",
  "operations": ["fetch_object", "mirror_log"],
  "scope": {
    "actors": ["actor:example:alice"],
    "audience_classes": ["public", "followers"]
  },
  "expiry": "2026-12-31T23:59:59Z",
  "visibility": "public",
  "transferability": "non_transferable",
  "issued_at": "2026-04-02T00:00:00Z"
}
```

## 11.9 View schema

```json
{
  "view_id": "view:feed:default",
  "schema": "rpp.view.feed.v1",
  "issuer": "actor:viewsvc:mainfeed",
  "sources": {
    "logs": ["relay:global-a"],
    "claims": ["actor:labeler:watchtower"],
    "actions": ["self"]
  },
  "selection_policy": "cid:select-v4",
  "ranking_policy": "cid:rank-v8",
  "claim_inputs": [
    {
      "issuer": "actor:labeler:watchtower",
      "weight_bps": 8000
    }
  ],
  "freshness": {
    "generated_at": "2026-04-02T03:17:15Z",
    "max_source_lag_ms": 8500
  },
  "known_omissions": [
    {
      "kind": "scope_gap",
      "detail": "private follower-scoped posts excluded"
    }
  ]
}
```

A View must confess its projection rules. If it can't, it's doing ideology.

## 11.10 Challenge schema

```json
{
  "challenge_id": "cid:challenge-777",
  "schema": "rpp.challenge.v1",
  "challenger": "actor:example:alice",
  "target_ref": "cid:claim-900",
  "grounds": [
    "insufficient_context",
    "counterevidence_available"
  ],
  "evidence_refs": [
    "cid:evidence-9001"
  ],
  "requested_remedy": "withdraw_claim_and_reverse_actions",
  "opened_at": "2026-04-02T03:18:00Z",
  "deadline": "2026-04-05T03:18:00Z"
}
```

---

# 12. End-to-end example

Actors:

* **Alice** publishes a post.
* **Watchtower** is a third-party labeler.
* **Mainfeed** is a ranking/view service.
* **PublicWatch** is an observatory.
* **Bob** is a user with his own client and local trust policy.

## Step 1: Alice publishes

Alice creates `obj-post-555`.
She appends `env-1042` to her log.

Result:

* a post exists
* authorship exists
* order exists
* nobody has yet claimed anything about it

Bob's client may fetch Alice's actor doc, log tail, and the object. Bob may render it immediately if his client policy allows.

## Step 2: Watchtower makes a claim

Watchtower sees the post and issues `claim-900`:

* `misleading_context`
* confidence 7200 bps (72%)
* evidence linked
* policy linked

At this point, nothing visible has changed unless Bob's client or some view service chooses to use this claim.

That is deliberate. A claim is not magic. It does not get to self-execute.

## Step 3: Mainfeed acts

Mainfeed ingests Watchtower claims as one of many inputs.
Its policy says: cautionary public-health labels with confidence >7000 bps from trusted issuer Watchtower trigger deprioritization in default guest and logged-in feeds for 7 days.

So Mainfeed issues:

* `rec-901`
* `act-333`

Now something changed. The post's ranking in `view:feed:default` is lower.

That is consequence. Therefore it must be legible.

## Step 4: PublicWatch observes

PublicWatch regularly snapshots selected views, action logs, and issuer claims.

It sees:

* `claim-900`
* `act-333`
* reduced ranking presence for `obj-post-555` in default feed snapshot

It emits `rcpt-444`.

Now an outside observer can say:

* yes, the action happened
* here is who claimed
* here is who acted
* here is when
* here is which view
* here is what we did and did not observe

## Step 5: Bob evaluates locally

Bob's client has local trust config:

* trust Alice for publication authenticity
* trust PublicWatch for receipts
* do **not** automatically trust Watchtower claims
* treat Mainfeed default view as convenience, not truth

So Bob's client may display the post normally in his own direct-follow view while showing Watchtower's claim as advisory context and noting Mainfeed's action as scoped information.

**The protocol does not force Bob's experience to collapse into Mainfeed's experience.**

The action has scope. Bob can inspect the scope.

## Step 6: Alice challenges

Alice disagrees. She opens `challenge-777`.

### Watchtower may:

* uphold claim
* amend confidence
* withdraw claim

### Mainfeed may:

* keep action
* reverse action
* revise action independent of Watchtower

### PublicWatch may:

* observe whether any of that happened
* emit new receipts

Now the dispute is legible as a sequence, not an invisible moral weather pattern.

---

# 13. Local client model

A client session should be assembled from explicit mounts.

Bob's client config:

```json
{
  "identity_sources": [
    "resolver:public-keys-1"
  ],
  "publication_sources": [
    "relay:global-a",
    "origin-fetch"
  ],
  "claim_sources": [
    "actor:labeler:watchtower",
    "actor:labeler:localcollective"
  ],
  "receipt_sources": [
    "actor:obs:publicwatch"
  ],
  "view_sources": [
    "actor:viewsvc:mainfeed",
    "actor:viewsvc:friendsfeed"
  ],
  "trust_policy": {
    "claims": {
      "actor:labeler:watchtower": "advisory",
      "actor:labeler:localcollective": "preferred"
    },
    "actions": {
      "actor:viewsvc:mainfeed": "scoped_only",
      "actor:viewsvc:friendsfeed": "high_trust"
    },
    "receipts": {
      "actor:obs:publicwatch": "high_trust"
    }
  }
}
```

This is **per-session namespace composition for social infrastructure**.

---

# 14. Failure modes the protocol makes visible

## 14.1 Claim/action mismatch

A labeler issues mild cautionary claims. A feed service turns them into heavy suppression. Now you can prove claim tone vs. action severity divergence. Labelwatch-type analysis becomes native.

## 14.2 Silent enforcement

A service changes visibility but emits no action object. Detectable as unexplained view divergence and missing action receipts.

## 14.3 Policy drift

A view changes ranking policy version. Outside observers can correlate policy version shifts with changed outcomes.

## 14.4 Identity delegation abuse

An actor's mobile delegate issues things outside scope. Clients can detect invalid purpose, expired delegation, kind mismatch.

## 14.5 Relay partiality

A relay falls behind or excludes some actor classes. If views and receipts declare source set + lag + omissions, that becomes speakable.

---

# 15. Minimum viable protocol profile

MVP needs only:

* Actor document
* append-only Log
* Object
* Claim
* Action
* Receipt
* View
* Grant

You can ship without Recommendations or Challenges at first, though you'll miss them fast.

The absolute irreducible thesis is:

**Publication, claim, consequence, and observation must not collapse into one another.**

---

# 16. The actual political difference

Most modern stacks make one or more of these moves:

* let claims masquerade as actions
* let actions hide behind claims
* let views pretend to be reality
* let access policy masquerade as openness
* let workflow state pretend to be evidence

RPP is built to stop those cheats. Not eliminate them entirely. Just force them to become visible enough that outside parties can argue about something real.

---

# 17. Slogans

* **Language is a proposal. Action is a fact.**
* **A view is a projection, not a world.**
* **If consequence changed, authorship must remain attached.**
* **Claims may advise. Actions must confess.**
* **Openness without observable consequence is branding.**
* **The seam is where the power is.**

---

# 18. Where it would get attacked

People would immediately complain that it is:

* too explicit
* too hard for normies
* too many objects
* too much observability burden
* too hard to optimize for frictionless UX
* too willing to admit partiality

And they'd be right. That's the trade.

You'd be choosing:

* legibility over enchantment
* inspectability over "it just works"
* scoped trust over universal feed theater
* receipts over vibes

---

# 19. Open questions

Next steps toward implementable:

* **A.** Trust-evaluation algorithm for clients and observatories
* **B.** Policy/ontology profile for labelers and moderation systems
* **C.** Relay and mirror model so transport doesn't quietly become governance again
