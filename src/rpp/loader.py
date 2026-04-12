"""Load RPP records from JSON files and build a subject index."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Map $type to a friendlier kind name
TYPE_TO_KIND = {
    "zone.neutral.rpp.claim": "claim",
    "zone.neutral.rpp.attestation": "attestation",
    "zone.neutral.rpp.action": "action",
    "zone.neutral.rpp.challenge": "challenge",
}

KINDS_WITH_SUBJECT = {"claim", "attestation", "action"}


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
        """Extract the subject value, handling both subject-bearing and challenge records."""
        if self.kind in KINDS_WITH_SUBJECT:
            subj = self.raw.get("subject", {})
            return subj.get("value") if isinstance(subj, dict) else None
        if self.kind == "challenge":
            return self.raw.get("targetRef")
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


@dataclass
class SubjectIndex:
    """Subject-centric index of RPP records."""

    subjects: dict[str, list[Record]] = field(default_factory=dict)
    all_records: list[Record] = field(default_factory=list)
    # Map anchor_id -> record for linking
    by_anchor: dict[str, Record] = field(default_factory=dict)

    def add(self, record: Record):
        self.all_records.append(record)
        self.by_anchor[record.anchor_id] = record

        subject = record.subject_value
        if subject:
            self.subjects.setdefault(subject, []).append(record)

    def get_subject(self, ref: str) -> list[Record]:
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
        """Try to find an anchor_id for a causeRef/targetRef/relatedClaim."""
        # Check if any record's raw data could match this ref
        # For now, scan — this is fine for example-scale data
        for record in self.all_records:
            # Match on AT-URI-ish refs by checking if the ref appears in the record
            if ref in json.dumps(record.raw):
                return record.anchor_id
        return None


def load_records(directory: Path) -> SubjectIndex:
    """Load all JSON files from a directory and build a subject index."""
    index = SubjectIndex()

    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        rpp_type = data.get("$type", "")
        kind = TYPE_TO_KIND.get(rpp_type)
        if not kind:
            continue

        record = Record(kind=kind, raw=data)
        index.add(record)

    # Second pass: propagate challenges to the subjects of records that
    # reference them. A challenge targets a claim/action/attestation by
    # AT-URI. For the subject view to show the full chain, we also index
    # the challenge under every subject where the targeted ref appears
    # (as a causeRef, relatedClaim, or the challenge's own targetRef
    # matches a record that's already indexed under that subject).
    for record in list(index.all_records):
        if record.kind != "challenge":
            continue
        target_ref = record.raw.get("targetRef", "")
        if not target_ref:
            continue
        # Find any subject-bearing record whose causeRefs or own refs
        # mention the same target, or that IS the target
        for candidate in index.all_records:
            if candidate is record:
                continue
            candidate_refs = set()
            for ref_field in ("causeRefs", "relatedClaims", "evidenceRefs"):
                candidate_refs.update(candidate.raw.get(ref_field, []))
            # If the candidate references the same target, or IS referenced
            # by the same target pattern, propagate
            if target_ref in candidate_refs or target_ref == candidate.subject_value:
                subj = candidate.raw.get("subject", {})
                subj_val = subj.get("value") if isinstance(subj, dict) else None
                if subj_val and record not in index.subjects.get(subj_val, []):
                    index.subjects.setdefault(subj_val, []).append(record)

    return index
