"""Tests for the RPP subject-state index."""

from rpp.index import Record, SubjectIndex, normalize


def test_normalize_claim():
    data = {
        "$type": "zone.neutral.rpp.claim",
        "issuer": "did:plc:test",
        "subject": {"subjectType": "did", "value": "did:plc:target"},
        "claimType": "classification",
        "evidenceClass": "direct_observation",
        "createdAt": "2026-04-12T00:00:00Z",
    }
    record = normalize(data)
    assert record is not None
    assert record.kind == "claim"
    assert record.subject_value == "did:plc:target"
    assert record.issuer == "did:plc:test"


def test_normalize_unknown_type():
    data = {"$type": "com.example.unrelated", "foo": "bar"}
    assert normalize(data) is None


def test_normalize_missing_type():
    assert normalize({"foo": "bar"}) is None


def test_challenge_has_subject():
    data = {
        "$type": "zone.neutral.rpp.challenge",
        "challenger": "did:plc:alice",
        "subject": {"subjectType": "at-uri", "value": "at://did:plc:alice/app.bsky.feed.post/123"},
        "targetRef": "at://did:plc:labeler/zone.neutral.rpp.claim/456",
        "grounds": ["insufficient_evidence"],
        "createdAt": "2026-04-12T00:00:00Z",
    }
    record = normalize(data)
    assert record is not None
    assert record.kind == "challenge"
    assert record.subject_value == "at://did:plc:alice/app.bsky.feed.post/123"
    assert record.issuer == "did:plc:alice"


def test_subject_index_groups_by_subject():
    index = SubjectIndex()
    claim = normalize({
        "$type": "zone.neutral.rpp.claim",
        "issuer": "did:plc:labeler",
        "subject": {"subjectType": "did", "value": "did:plc:target"},
        "claimType": "classification",
        "evidenceClass": "direct_observation",
        "createdAt": "2026-04-12T00:00:00Z",
    })
    action = normalize({
        "$type": "zone.neutral.rpp.action",
        "issuer": "did:plc:service",
        "subject": {"subjectType": "did", "value": "did:plc:target"},
        "actionType": "content_hidden",
        "causeRefs": [],
        "createdAt": "2026-04-12T00:01:00Z",
    })
    other = normalize({
        "$type": "zone.neutral.rpp.attestation",
        "issuer": "did:plc:operator",
        "subject": {"subjectType": "did", "value": "did:plc:other"},
        "attestationType": "batch_creation_pattern",
        "basis": "operator_telemetry",
        "scope": "test",
        "confidence": "low",
        "createdAt": "2026-04-12T00:02:00Z",
    })
    for r in [claim, action, other]:
        index.add(r)

    target_records = index.get_subject("did:plc:target")
    assert len(target_records) == 2
    assert {r.kind for r in target_records} == {"claim", "action"}

    other_records = index.get_subject("did:plc:other")
    assert len(other_records) == 1
    assert other_records[0].kind == "attestation"


def test_subject_summary():
    index = SubjectIndex()
    for data in [
        {"$type": "zone.neutral.rpp.claim", "issuer": "did:plc:a",
         "subject": {"subjectType": "did", "value": "did:plc:x"},
         "claimType": "test", "evidenceClass": "unknown", "createdAt": "2026-01-01T00:00:00Z"},
        {"$type": "zone.neutral.rpp.challenge", "challenger": "did:plc:b",
         "subject": {"subjectType": "did", "value": "did:plc:x"},
         "targetRef": "at://did:plc:a/zone.neutral.rpp.claim/1",
         "grounds": ["factual_error"], "createdAt": "2026-01-01T00:01:00Z"},
    ]:
        index.add(normalize(data))

    summary = index.subject_summary()
    assert len(summary) == 1
    assert summary[0]["ref"] == "did:plc:x"
    assert summary[0]["counts"] == {"claim": 1, "challenge": 1}
    assert summary[0]["total"] == 2


def test_anchor_ids_are_stable():
    data = {
        "$type": "zone.neutral.rpp.claim",
        "issuer": "did:plc:test",
        "subject": {"subjectType": "did", "value": "did:plc:target"},
        "claimType": "test",
        "evidenceClass": "unknown",
        "createdAt": "2026-04-12T00:00:00Z",
    }
    r1 = normalize(data)
    r2 = normalize(data)
    assert r1.anchor_id == r2.anchor_id
    assert len(r1.anchor_id) == 12
