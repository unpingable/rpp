"""Load RPP records from files into a SubjectIndex.

This is an I/O adapter, not domain logic. The kernel boundary
lives in index.py (Record, normalize, SubjectIndex).
"""

from __future__ import annotations

import json
from pathlib import Path

from rpp.index import SubjectIndex, normalize


def load_json_dir(directory: Path) -> SubjectIndex:
    """Load all JSON files from a directory and build a subject index."""
    index = SubjectIndex()

    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        record = normalize(data)
        if record:
            index.add(record)

    return index


def load_ndjson(path: Path) -> SubjectIndex:
    """Load records from an NDJSON file and build a subject index."""
    index = SubjectIndex()

    try:
        text = path.read_text()
    except OSError:
        return index

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        record = normalize(data)
        if record:
            index.add(record)

    return index
