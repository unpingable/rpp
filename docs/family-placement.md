# Family placement

RPP lives under the **atproto-nutrition** workbench umbrella
(`~/git/atproto-nutrition/`) alongside the observatory family — `labelwatch`
(observatory of labeler behavior) and `driftwatch` (observatory of information
drift), plus their siblings. It keeps its own git history and remote
(`unpingable/rpp`); the umbrella is workbench organization, not a monorepo.

**Why it's family.** RPP's near-term role is the family's *reviewability /
projection vertex*: it renders labelwatch and driftwatch outputs into
subject-centered chains (claim → action → challenge). The labelwatch right-of-reply
gap (`labelwatch.operator_contest.v1`) maps directly onto RPP's **Challenge** record
type — that convergence is what motivated co-locating them.

**Where it sits relative to the observatories (descriptive, not a gate).** The
observatories are structurally *detect-only*: they observe, classify, and export
custody of observations, but never emit labels back into the governed ecosystem. RPP
is the family's *emit-side* member — it publishes governance records (claims,
attestations, actions, challenges) and renders them. The natural division of labor:

- Observatories **project into** RPP-shaped views (read-only rendering of their
  declared facts).
- RPP **publishes** governance records on its own footing (operator attestations,
  challenges, etc.).

This is a description of the existing division of labor, not a boundary anyone is
policing — it's recorded so the co-location reads as deliberate rather than
incidental.
