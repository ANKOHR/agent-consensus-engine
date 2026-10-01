"""Pure exact voting. Hypothetical savings are never computed."""
from collections import Counter
from datetime import date

class SchemaError(ValueError):
    """An input field violates the explicit schema."""

def validate(records):
    seen = set()
    for index, record in enumerate(records, 1):
        prefix = f"record {index}"
        def fail(field, message):
            raise SchemaError(f"{prefix}: {field}: {message}")
        if not isinstance(record, dict):
            fail("record", "expected object")
        allowed = {"id", "synthetic", "votes", "ground_truth", "date"}
        extra = set(record) - allowed
        if extra:
            fail(sorted(extra)[0], "unknown field")
        for field in ("id", "synthetic", "votes"):
            if field not in record:
                fail(field, "required field missing")
        def string(field, value):
            if not isinstance(value, str) or not value.strip() or len(value) > 10000:
                fail(field, "expected nonblank string of at most 10000 characters")
            if "\u2014" in value:
                fail(field, "em dash forbidden; use a hyphen")
        string("id", record["id"])
        if record["id"] in seen:
            fail("id", "duplicate id")
        seen.add(record["id"])
        if type(record["synthetic"]) is not bool:
            fail("synthetic", "expected boolean")
        if "ground_truth" in record:
            string("ground_truth", record["ground_truth"])
        if "date" in record:
            try:
                parsed = date.fromisoformat(record["date"])
            except (ValueError, TypeError):
                fail("date", "expected ISO date")
            # Fixed schema ceiling keeps validation deterministic across runs.
            if parsed > date(2026, 9, 30):
                fail("date", "future date beyond fixed schema cutoff 2026-09-30")
        votes = record["votes"]
        if not isinstance(votes, list) or len(votes) > 1000:
            fail("votes", "expected list of at most 1000 votes")
        agents = set()
        for vote in votes:
            if not isinstance(vote, dict) or set(vote) != {"agent", "answer"}:
                fail("votes", "each vote requires only agent and answer")
            string("votes.agent", vote["agent"])
            string("votes.answer", vote["answer"])
            if vote["agent"] in agents:
                fail("votes.agent", "duplicate agent within record")
            agents.add(vote["agent"])
    return records

def aggregate(records):
    validate(records)
    decisions = []
    totals = dict(records=len(records), votes=0, consensus=0, unresolved=0,
                  dissent_records=0, labelled=0, correct=0, incorrect=0,
                  labelled_unresolved=0, false_positives=0)
    for record in sorted(records, key=lambda r: r["id"]):
        counts = Counter(v["answer"] for v in record["votes"])
        n = sum(counts.values())
        winner = next((a for a, c in sorted(counts.items()) if c > n / 2), None) if n >= 2 else None
        dissent = len(counts) > 1
        truth = record.get("ground_truth")
        status = "unresolved" if winner is None else "consensus"
        evaluation = "unlabelled" if truth is None else ("unresolved" if winner is None else "correct" if winner == truth else "incorrect")
        totals[status] += 1
        totals["votes"] += n
        totals["dissent_records"] += int(dissent)
        if truth is not None:
            totals["labelled"] += 1
            totals["labelled_unresolved" if winner is None else evaluation] += 1
            totals["false_positives"] += int(winner is not None and winner != truth)
        decisions.append(dict(id=record["id"], synthetic=record["synthetic"], status=status,
                              answer=winner, vote_counts=dict(sorted(counts.items())),
                              dissent=dissent, ground_truth=truth, evaluation=evaluation))
    return dict(schema_version=1, totals=totals, decisions=decisions,
                savings={"status": "unmeasured", "note": "Time and money savings are unmeasured; no baseline supplied."})
