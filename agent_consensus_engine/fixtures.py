"""Synthetic planted cases; no random numbers, seed not applicable."""
import json
from pathlib import Path

EXPECTED = dict(records=200, votes=560, consensus=120, unresolved=80,
                dissent_records=80, labelled=200, correct=120, incorrect=0,
                labelled_unresolved=80, false_positives=0)

def fixture_records():
    records = []
    # Five hand-defined cases repeated 40 times: unanimous, majority, tie,
    # no votes, and unanimous Unicode. Votes per block: 3 + 3 + 4 + 0 + 4.
    patterns = [["yes"] * 3, ["yes", "yes", "no"], ["yes", "no"] * 2, [], ["是"] * 4]
    for i in range(200):
        answers = patterns[i % 5]
        records.append(dict(id=f"case-{i:03d}", synthetic=True,
                            votes=[dict(agent=f"agent-{j}", answer=a) for j, a in enumerate(answers)],
                            ground_truth="是" if i % 5 == 4 else "yes"))
    return records

def generate(out):
    path = Path(out)
    path.mkdir(parents=True, exist_ok=True)
    (path / "records.jsonl").write_text("# SYNTHETIC fixture data\n" + "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in fixture_records()), encoding="utf-8")
    (path / "expectations.json").write_text(json.dumps(dict(synthetic=True, label="SYNTHETIC hand-computed expectations", totals=EXPECTED,
        arithmetic="40 blocks: 3 consensus, 2 unresolved, 14 votes, 2 dissent records per block"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
