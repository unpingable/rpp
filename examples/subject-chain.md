# Subject Chain Example

A walkthrough of one complete claim-attestation-action-challenge flow, showing how RPP records compose into a legible governance chain.

## Setup

Actors:
- **Alice** (`did:plc:alice`) — publishes a post
- **Watchtower** (`did:plc:labeler-watchtower`) — a third-party labeler
- **Mainfeed** (`did:plc:feedsvc-mainfeed`) — a feed/view service
- **Indie PDS** (`did:plc:pds-operator-indie`) — a cooperating PDS operator

Subject: `at://did:plc:alice/app.bsky.feed.post/3abc123`

## Step 1: Alice publishes a post

Alice publishes a post about vaccine efficacy data on Bluesky. This is a normal ATProto record — RPP has no involvement yet.

At this point: the post exists. Nobody has claimed anything about it.

## Step 2: Watchtower makes a claim

Watchtower, a third-party labeler, reviews the post and publishes an RPP claim:

```json
{
  "$type": "zone.neutral.rpp.claim",
  "issuer": "did:plc:labeler-watchtower",
  "subject": {"subjectType": "at-uri", "value": "at://did:plc:alice/app.bsky.feed.post/3abc123"},
  "claimType": "classification",
  "value": {"polarity": "cautionary", "domain": "public_health", "summary": "Post cites a retracted preprint."},
  "evidenceClass": "direct_observation",
  "confidence": 7200,
  "status": "active",
  "createdAt": "2026-04-12T03:17:00Z"
}
```

At this point: a claim exists. **Nothing visible has changed** unless some view service chooses to use it. A claim is not magic. It does not self-execute.

## Step 3: Mainfeed acts

Mainfeed ingests Watchtower claims as one input among many. Its policy says: cautionary public-health claims with confidence >7000 bps from trusted labelers trigger content hiding in default views for 7 days.

Mainfeed publishes an RPP action:

```json
{
  "$type": "zone.neutral.rpp.action",
  "issuer": "did:plc:feedsvc-mainfeed",
  "subject": {"subjectType": "at-uri", "value": "at://did:plc:alice/app.bsky.feed.post/3abc123"},
  "actionType": "content_hidden",
  "causeRefs": ["at://did:plc:labeler-watchtower/zone.neutral.rpp.claim/3claim900"],
  "scope": "Hidden from guest and default feed. Accessible via direct link.",
  "reversible": true,
  "status": "active",
  "createdAt": "2026-04-12T03:17:12Z"
}
```

At this point: something actually changed. The post is less visible in the default feed. **The action's authorship is attached to Mainfeed, not Watchtower.** The feed service owns the consequence.

## Step 4: Indie PDS adds an attestation

Separately, the indie PDS operator notices that Alice's account was created in a batch of 15 accounts within 60 seconds. They contribute an attestation via the operator API:

```json
{
  "$type": "zone.neutral.rpp.attestation",
  "issuer": "did:plc:pds-operator-indie",
  "subject": {"subjectType": "did", "value": "did:plc:alice"},
  "attestationType": "batch_creation_pattern",
  "basis": "operator_telemetry",
  "scope": "Temporal clustering only. Does not assert coordination or intent.",
  "confidence": "medium",
  "issuerRole": "operator",
  "status": "active",
  "expiresAt": "2026-07-12T14:00:00Z",
  "createdAt": "2026-04-12T14:00:00Z"
}
```

At this point: an operator has contributed a signal. It's typed as an operator attestation with explicit scope and TTL. It doesn't claim Alice is bad — it says accounts were created together. That's a different object than a claim.

## Step 5: Alice challenges

Alice disagrees with Watchtower's claim. She publishes an RPP challenge:

```json
{
  "$type": "zone.neutral.rpp.challenge",
  "challenger": "did:plc:alice",
  "targetRef": "at://did:plc:labeler-watchtower/zone.neutral.rpp.claim/3claim900",
  "grounds": ["insufficient_evidence", "counterevidence_available"],
  "body": "The cited preprint was retracted for methodology issues unrelated to my claim. My data comes from the NEJM Phase III trial.",
  "evidenceRefs": ["https://nejm.example/phase3-trial-456"],
  "requestedRemedy": "withdraw_claim",
  "status": "open",
  "createdAt": "2026-04-12T03:18:00Z"
}
```

## Step 6: Subject view

An RPP subject view for `at://did:plc:alice/app.bsky.feed.post/3abc123` now shows:

| Object | Issuer | Status | Key detail |
|--------|--------|--------|------------|
| Claim | Watchtower | active | classification, cautionary, 72% confidence |
| Action | Mainfeed | active | content_hidden, caused by Watchtower claim |
| Challenge | Alice | open | insufficient_evidence, counterevidence cited |

And for `did:plc:alice`:

| Object | Issuer | Status | Key detail |
|--------|--------|--------|------------|
| Attestation | Indie PDS | active | batch_creation_pattern, medium confidence, expires 2026-07 |

The chain is legible. **Who said what, on what basis, with what consequence, and when.**

## What happens next

Watchtower may:
- Uphold the claim
- Amend the confidence
- Withdraw the claim (new record with `supersedes` pointing to the original)

Mainfeed may:
- Keep the action
- Reverse the action (new action record with `actionType: content_restored`)
- Revise the action independent of Watchtower's response

If Watchtower withdraws, the original claim still exists in the record — it's just marked `withdrawn`. If Mainfeed reverses, the original action still exists — marked `reversed`. The history is preserved.

That's the point. Not memory holes. Scar tissue.
