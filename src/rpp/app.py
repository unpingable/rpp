"""RPP subject-chain viewer."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote, unquote

from flask import Flask, render_template, request, jsonify, abort

from rpp.index import SubjectIndex
from rpp.loader import load_json_dir

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


def create_app(examples_dir: Path | None = None) -> Flask:
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
    index = load_json_dir(examples_dir or EXAMPLES_DIR)

    # Make helpers available in templates
    @app.context_processor
    def inject_helpers():
        return {
            "quote": quote,
            "unquote": unquote,
            "find_anchor": index.find_anchor_for_ref,
        }

    @app.route("/")
    def home():
        subjects = index.subject_summary()
        return render_template("index.html", subjects=subjects)

    @app.route("/subject")
    def subject_view():
        ref = request.args.get("ref", "")
        if not ref:
            abort(400, "Missing ?ref= parameter")
        records = index.get_subject(ref)
        if not records:
            abort(404, f"No records for subject: {ref}")

        # Group by kind
        groups = {
            "claims": [r for r in records if r.kind == "claim"],
            "attestations": [r for r in records if r.kind == "attestation"],
            "actions": [r for r in records if r.kind == "action"],
            "challenges": [r for r in records if r.kind == "challenge"],
        }
        return render_template("subject.html", ref=ref, groups=groups, records=records)

    # Debug/raw JSON endpoints
    @app.route("/api/subjects")
    def api_subjects():
        return jsonify(index.subject_summary())

    @app.route("/api/subject")
    def api_subject():
        ref = request.args.get("ref", "")
        if not ref:
            abort(400, "Missing ?ref= parameter")
        records = index.get_subject(ref)
        if not records:
            abort(404)
        return jsonify([{"kind": r.kind, "anchor_id": r.anchor_id, "raw": r.raw} for r in records])

    return app


def main():
    app = create_app()
    print(f"RPP viewer: http://localhost:8400")
    print(f"Loading records from: {EXAMPLES_DIR}")
    app.run(host="127.0.0.1", port=8400, debug=True)


if __name__ == "__main__":
    main()
