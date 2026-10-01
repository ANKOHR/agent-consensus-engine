import pytest
from agent_consensus_engine.core import aggregate, SchemaError


def record(**kwargs):
    return dict(id="one", synthetic=False, votes=[dict(agent="a", answer="yes"), dict(agent="b", answer="yes")], **kwargs)


def test_majority_dissent_and_incorrect():
    r = record(ground_truth="no")
    r["votes"].append(dict(agent="c", answer="no"))
    result = aggregate([r])
    assert result["totals"]["incorrect"] == result["totals"]["false_positives"] == 1
    assert result["decisions"][0]["dissent"]


@pytest.mark.parametrize("change", [dict(amount=-1), dict(date="2099-01-01"), dict(id="x"*10001), dict(synthetic="true"), dict(votes=[dict(agent="a",answer="yes")]*2), dict(votes="bad"), dict(ground_truth=-1), dict(extra=1)])
def test_rejects_adversarial_values(change):
    r=record()
    r.update(change)
    with pytest.raises(SchemaError):
        aggregate([r])


def test_duplicate_ids():
    with pytest.raises(SchemaError, match="duplicate id"):
        aggregate([record(),record()])


def test_single_vote_is_insufficient():
    r=record()
    r["votes"]=r["votes"][:1]
    assert aggregate([r])["totals"]["unresolved"] == 1


def test_handles_unicode_and_long_inputs():
    r=record()
    r["id"]="C:\\Users\\亨利\\" + "界" * 9000
    r["votes"][0]["answer"]=r["votes"][1]["answer"]="是 café"
    assert aggregate([r])["decisions"][0]["answer"] == "是 café"
