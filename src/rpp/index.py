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


@dataclass
class Record:
    """A normalized RPP record."""

    kind: str
    raw: dict[str, Any]
    anchor_id: str = ""

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
    def status(self) -> str:
        return self.raw.get("status", "unknown")

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
