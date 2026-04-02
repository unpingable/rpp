# RPP Design Rationale

Origin: late-night noodling session sketching what a not-bullshit ATProto would look like.

## The core critique

ATProto is application-shaped infrastructure. RPP would be infrastructure-shaped infrastructure.

Less product cosmology. More protocol discipline.

## Why the seams are explicit

A narrower core than "social networking protocol":

* identity/addressing
* append-only event publication
* object retrieval
* signed references
* explicit capability boundaries

A **small core grammar** for publishing and relating to objects, not a whole social product ontology pretending to be neutral substrate.

## Claims and actions separated on purpose

ATProto still smears together in practice:

* what something is claimed to be
* what action a system recommends or takes because of that claim

RPP makes a hard distinction: taxonomy/assertion, confidence/evidence, action recommendation, action execution. That alone makes a bunch of current governance mush much harder to hide.

## Observatory as built-in, not afterthought

Not "trust us, it's open." Instead: if the system matters, it emits enough evidence to be observed from outside the workflow that operates it.

* public receipts for policy actions where possible
* observatory time distinct from workflow time
* explicit visibility into omissions, lag, and partial views
* no pretending the internal moderation UI is the truth of the system

**Evidence belongs to the protocol boundary, not just the operator console.**

## Honest partiality

ATProto still has too much "universal substrate" theater for something with obvious flagship-app gravity. RPP is honest that:

* every view is vantage-bound
* every feed is a constructed projection
* every index is partial
* every relay is a policy surface
* every firehose is only a firehose relative to what is admitted upstream

**Federation without pretending omniscience.**

## Discovery and transport decoupled hard

The usual trap: transport, identity, discovery, and legitimacy accrete toward one another until the stack quietly recentralizes. RPP keeps these apart aggressively:

* transport of events
* storage/retrieval
* indexing/search
* ranking/discovery
* moderation/governance
* identity proofs

Each separately replaceable. Each separately inspectable.

## Capability-based access instead of vibes-based openness

A lot of modern "open" systems are open right up until the data becomes strategically important. RPP makes permissions explicit: what can be fetched, by whom, under what grant, with what audit trail, and whether the denial itself is visible.

Not openness as branding. **Access as a governable, inspectable capability model.**

## Smaller nouns, fewer metaphysical ambitions

Old protocols knew what they were. Modern "protocols" often act like constitutions for an entire digital civilization.

RPP defines a few strong primitives and stops.

Not "here is the future of social."
More like: **here is a durable grammar for signed publication, reference, annotation, and retrieval across uneven trust boundaries.**

## The Plan 9 move

The real divergence from ATProto is not just governance. It's **composition**.

A client doesn't merely "log into the network." It assembles a session from mounted services: this identity resolver, these object mirrors, these rankers, these labelers, this local rule set, these grants, this trust policy.

The user's experience is a **bound namespace of views and policies**, not a single platform worldview.

## Why it would be better

Because it makes the seams visible. Because it stops pretending that identity is discovery, taxonomy is enforcement, access is openness, feed ranking is neutral reality, workflow state is the same as evidence.

## Why it might lose anyway

It would be more modular, more explicit, more inspectable, less magic, harder to narrate as one smooth universal experience. Which means slower onboarding, uglier default UX, less "it just works," fewer opportunities for one company to become reality by default.

What wins fast is the stack that says "don't worry about the seams."
This says "the seams are where the power is."

## The mean one-liner

**ATProto built a future acquisition target with DID documents. RPP would be a protocol.**
