import json
from agent_consensus_engine.fixtures import generate, fixture_records, EXPECTED
from agent_consensus_engine.core import aggregate


def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    text=(tmp_path/"records.jsonl").read_text(encoding="utf-8")
    assert text.startswith("# SYNTHETIC")
    assert all(json.loads(line)["synthetic"] is True for line in text.splitlines()[1:])
    assert json.loads((tmp_path/"expectations.json").read_text())["synthetic"] is True


def test_fixture_ground_truth_matches_hand_computed():
    assert aggregate(fixture_records())["totals"] == EXPECTED
    assert EXPECTED["records"] == EXPECTED["consensus"] + EXPECTED["unresolved"]
    assert EXPECTED["labelled"] == EXPECTED["correct"] + EXPECTED["incorrect"] + EXPECTED["labelled_unresolved"]


def test_corrupted_ground_truth_changes_computed_figures():
    records=fixture_records()
    records[0]["ground_truth"]="no"
    result=aggregate(records)
    assert result["totals"]["correct"] == 119
    assert result["totals"]["incorrect"] == 1
    assert result["totals"]["false_positives"] == 1


def test_five_handwritten_records():
    from agent_consensus_engine.cli import load
    from pathlib import Path
    result=load(Path(__file__).parent.parent/"examples"/"tiny")
    assert result["totals"]["records"] == 5
    assert result["totals"]["consensus"] == 3
