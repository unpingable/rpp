# AGENTS.md — Working in this repo

This file is a **travel guide**, not a law.
If anything here conflicts with the user's explicit instructions, the user wins.

> Instruction files shape behavior; the user determines direction.

---

## Quick start

```bash
pip install -e ".[dev]"
pytest
```

## Tests

```bash
pytest
```

Always run tests before proposing commits. Never claim tests pass without running them.

---

## Safety and irreversibility

### Do not do these without explicit user confirmation
- Push to remote, create/close PRs or issues
- Delete or rewrite git history
- Modify dependency files in ways that change the lock file
- Publish ATProto records to any live PDS or service

### Preferred workflow
- Make changes in small, reviewable steps
- Run tests locally before proposing commits
- For any operation that affects external state, require explicit user confirmation

---

## Repository layout

```
lexicons/       ATProto lexicon definitions (zone.neutral.rpp.*)
examples/       Example records and subject-chain walkthrough
docs/           Architecture, operator API, gap specs, archived specs
src/            Rust kernel + Python service (TBD)
tests/          Test suites
```

---

## Coding conventions

- Rust for kernel invariants (receipt validation, normalization, supersession graph)
- Python 3.10+ for service layer, ATProto glue, API surface
- pytest for Python tests, cargo test for Rust
- ATProto lexicon namespace: zone.neutral.rpp.*

---

## Invariants

1. Claims and actions are always separate objects
2. Append-only: no silent mutation, superseded objects stay visible
3. Attestations are inputs, not truth — no portable caste markers

---

## What this is not

- Not a social protocol or ATProto replacement
- Not a moderation oracle or trust-score system
- Not a Governor dependency

---

## When you're unsure

Ask for clarification rather than guessing, especially around:
- Whether a new record type is needed (the answer is almost certainly no)
- Operator attestation semantics and trust boundaries
- Anything that changes a documented invariant

---

## Agent-specific instruction files

| Agent | File | Role |
|-------|------|------|
| Claude Code | `CLAUDE.md` | Full operational context, build details, conventions |
| Codex | `AGENTS.md` (this file) | Operating context + defaults |
| Any future agent | `AGENTS.md` (this file) | Start here |
