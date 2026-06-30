"""RPP subject-state index.

This is the kernel boundary: normalized records and subject-centric
indexing. It knows nothing about where records come from (files, network,
operator API). Loaders feed records in; the index derives subject state.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from typing import Any


# Map $type to a friendlier kind name
TYPE_TO_KIND = {
    "zone.neutral.rpp.claim": "claim",
    "zone.neutral.rpp.attestation": "attestation",
    "zone.neutral.rpp.action": "action",
    "zone.neutral.rpp.challenge": "challenge",
}

VALID_KINDS = set(TYPE_TO_KIND.values())


# Self-authored `status` values look like two different things. Authorship and
# supersession are acts the producer is entitled to assert about its own object.
# The rest read like verdicts — computed (TTL), adjudicated (challenge outcome),
# or otherwise decided elsewhere. A producer asserting a verdict about itself is
# not authority; the reader must surface it as a *claimed* lifecycle state, never
# as checked admissibility. See docs/WDC-ADMISSIBILITY-BRIDGE.md.
VERDICT_LIKE_STATUS = frozenset(
    {"revoked", "expired", "upheld", "rejected", "inadmissible"}
)


@dataclass
class Validity:
    """A checked-admissibility result, attached out-of-band by a conforming
    validator (WLP / Governor / a witnessed-path checker).

    This NEVER comes from the record itself. A record may assert its lifecycle;
    only a checker may report check-state, and only by citing itself.
    """

    status: str  # checked_pass | checked_fail | not_supported
    source_ref: str  # citation to the checker receipt this verdict rests on


@dataclass
class Record:
    """A normalized RPP record."""

    kind: str
    raw: dict[str, Any]
    anchor_id: str = ""
    # Out-of-band check result. Populated only by a validator that consulted a
    # named checker receipt — never derived from `raw["status"]`. Absent means
    # unchecked, which is the honest default: RPP carries the path, does not judge it.
    checked_validity: Validity | None = None

    def __post_init__(self):
        if not self.anchor_id:
            # Stable anchor from kind + issuer/challenger + createdAt
            issuer = self.raw.get("issuer") or self.raw.get("challenger", "unknown")
            created = self.raw.get("createdAt", "")
            slug = f"{self.kind}:{issuer}:{created}"
            self.anchor_id = hashlib.sha256(slug.encode()).hexdigest()[:12]

    @property
    def subject_value(self) -> str | None:
        """Extract the subject value. All four record types carry an explicit subject."""
        if self.kind in VALID_KINDS:
            subj = self.raw.get("subject", {})
            return subj.get("value") if isinstance(subj, dict) else None
        return None

    @property
    def issuer(self) -> str:
        return self.raw.get("issuer") or self.raw.get("challenger", "unknown")

    @property
    def lifecycle(self) -> str:
        """Record-authored lifecycle state. This is the producer's claim about
        its own object (active/withdrawn/superseded/...), not a verdict about it.
        Never treat as admissibility — see `validity_status`."""
        return self.raw.get("status", "unknown")

    @property
    def lifecycle_is_verdict_like(self) -> bool:
        """True when the self-authored lifecycle reads like an external verdict
        (revoked/expired/upheld/...). Surfaced so a reader can mark it as a
        *claimed* state, not a checked one."""
        return self.lifecycle in VERDICT_LIKE_STATUS

    @property
    def status(self) -> str:
        """Back-compat alias for `lifecycle`. The honest name is `lifecycle`;
        this remains for the viewer template. It is NOT validity."""
        return self.lifecycle

    @property
    def validity_status(self) -> str:
        """Checked admissibility. The iron rule: `unchecked` unless a conforming
        validator receipt has been attached as `checked_validity`. RPP records
        may assert lifecycle; only a reader may report check-state, by citing a
        checker. Self-authored `status` can never promote this off `unchecked`."""
        return self.checked_validity.status if self.checked_validity else "unchecked"

    @property
    def validity_source_ref(self) -> str | None:
        """The checker receipt this validity rests on, or None if unchecked."""
        return self.checked_validity.source_ref if self.checked_validity else None

    @property
    def created_at(self) -> str:
        return self.raw.get("createdAt", "")


def normalize(data: dict[str, Any]) -> Record | None:
    """Normalize a raw JSON object into a Record, or None if not a valid RPP type."""
    rpp_type = data.get("$type", "")
    kind = TYPE_TO_KIND.get(rpp_type)
    if not kind:
        return None
    return Record(kind=kind, raw=data)


@dataclass
class SubjectIndex:
    """Subject-centric index of RPP records.

    This is the primary query surface. Feed it normalized Records;
    it builds subject-grouped views and cross-reference lookups.
    """

    subjects: dict[str, list[Record]] = field(default_factory=dict)
    all_records: list[Record] = field(default_factory=list)
    by_anchor: dict[str, Record] = field(default_factory=dict)

    def add(self, record: Record):
        """Add a record to the index."""
        self.all_records.append(record)
        self.by_anchor[record.anchor_id] = record

        subject = record.subject_value
        if subject:
            self.subjects.setdefault(subject, []).append(record)

    def get_subject(self, ref: str) -> list[Record]:
        """Get all records for a subject."""
        return self.subjects.get(ref, [])

    def subject_summary(self) -> list[dict[str, Any]]:
        """Summary of all subjects with object counts."""
        result = []
        for ref, records in sorted(self.subjects.items()):
            counts: dict[str, int] = {}
            for r in records:
                counts[r.kind] = counts.get(r.kind, 0) + 1
            result.append({"ref": ref, "counts": counts, "total": len(records)})
        return result

    def find_anchor_for_ref(self, ref: str) -> str | None:
        """Find an anchor_id for a causeRef/targetRef/relatedClaim.

        Scans all records — fine for current scale. When this becomes
        a bottleneck, build a ref->anchor lookup on ingest.
        """
        for record in self.all_records:
            if ref in json.dumps(record.raw):
                return record.anchor_id
        return None
