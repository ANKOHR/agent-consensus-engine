import json
from agent_consensus_engine.core import aggregate
from agent_consensus_engine.fixtures import fixture_records, EXPECTED
from agent_consensus_engine.report import render


def test_report_matches_ground_truth_exact():
    assert json.loads(render(aggregate(fixture_records()),"json"))["totals"] == EXPECTED


def test_report_zero_false_positives():
    assert aggregate(fixture_records())["totals"]["false_positives"] == 0


def test_report_carries_provenance_banner():
    result=aggregate(fixture_records())
    for fmt in ("md","json"):
        assert "DATA PROVENANCE: 200 synthetic fixture records; 0 user-declared real records" in render(result,fmt)


def test_hypothetical_figures_labelled():
    for fmt in ("md","json"):
        output=render(aggregate([]),fmt)
        assert "unmeasured" in output
        assert "no baseline supplied" in output


def test_no_em_dashes_in_outputs():
    for fmt in ("md","json"):
        assert "\u2014" not in render(aggregate(fixture_records()),fmt)


def test_determinism_byte_identical():
    records=fixture_records()
    assert render(aggregate(records),"json").encode() == render(aggregate(list(reversed(records))),"json").encode()
