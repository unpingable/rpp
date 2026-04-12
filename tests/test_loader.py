"""Tests for the RPP file loaders."""

import json
import tempfile
from pathlib import Path

from rpp.loader import load_json_dir, load_ndjson


def _write_example(directory: Path, name: str, data: dict):
    (directory / name).write_text(json.dumps(data))


def test_load_json_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        _write_example(d, "claim.json", {
            "$type": "zone.neutral.rpp.claim",
            "issuer": "did:plc:test",
            "subject": {"subjectType": "did", "value": "did:plc:target"},
            "claimType": "test",
            "evidenceClass": "unknown",
            "createdAt": "2026-01-01T00:00:00Z",
        })
        _write_example(d, "not-rpp.json", {"foo": "bar"})
        _write_example(d, "readme.txt", {})  # not .json, ignored by glob

        index = load_json_dir(d)
        assert len(index.all_records) == 1
        assert index.all_records[0].kind == "claim"


def test_load_json_dir_skips_bad_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        (d / "bad.json").write_text("not json{{{")
        index = load_json_dir(d)
        assert len(index.all_records) == 0


def test_load_ndjson():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "events.ndjson"
        lines = [
            json.dumps({"$type": "zone.neutral.rpp.claim", "issuer": "did:plc:a",
                        "subject": {"subjectType": "did", "value": "did:plc:x"},
                        "claimType": "test", "evidenceClass": "unknown",
                        "createdAt": "2026-01-01T00:00:00Z"}),
            json.dumps({"$type": "zone.neutral.rpp.action", "issuer": "did:plc:b",
                        "subject": {"subjectType": "did", "value": "did:plc:x"},
                        "actionType": "content_hidden", "causeRefs": [],
                        "createdAt": "2026-01-01T00:01:00Z"}),
            "",  # blank line
            "not json",  # bad line
        ]
        path.write_text("\n".join(lines))

        index = load_ndjson(path)
        assert len(index.all_records) == 2
        kinds = {r.kind for r in index.all_records}
        assert kinds == {"claim", "action"}


def test_load_examples():
    """Smoke test: load the actual example files."""
    examples = Path(__file__).parent.parent / "examples"
    if not examples.exists():
        return  # skip if running from elsewhere
    index = load_json_dir(examples)
    assert len(index.all_records) == 4
    kinds = {r.kind for r in index.all_records}
    assert kinds == {"claim", "attestation", "action", "challenge"}
