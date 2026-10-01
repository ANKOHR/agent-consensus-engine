import json
import time
import pytest
from agent_consensus_engine.cli import main, load, atomic_write, InputError
from agent_consensus_engine.fixtures import generate, EXPECTED


def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start=time.perf_counter()
    assert main(["fixtures","--out","demo"]) == 0
    assert main(["run","--input","demo"]) == 0
    assert main(["report","--format","json","--out","report.json"]) == 0
    assert json.loads((tmp_path/"report.json").read_text(encoding="utf-8"))["totals"] == EXPECTED
    assert time.perf_counter()-start < 5


def test_empty_input_renders_without_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path/"empty").mkdir()
    assert main(["run","--input","empty"]) == 0
    assert main(["report"]) == 0
    assert "| records | 0 |" in capsys.readouterr().out


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path/"bad.jsonl").write_text('# SYNTHETIC\n{bad\n')
    assert main(["run","--input",str(tmp_path)]) == 2
    err=capsys.readouterr().err
    assert "ParseError" in err and "bad.jsonl: line 2" in err
    assert "Traceback" not in err


@pytest.mark.parametrize("cmd",["fixtures","run","report","audit","disagreements"])
def test_cli_smoke_all_subcommands(cmd, capsys):
    with pytest.raises(SystemExit) as exc:
        main([cmd,"--help"])
    assert exc.value.code == 0
    assert "Example:" in capsys.readouterr().out


def test_domain_subcommands(tmp_path, capsys):
    generate(tmp_path)
    for cmd in ("audit","disagreements"):
        assert main([cmd,"--input",str(tmp_path)]) == 0
        assert "DATA PROVENANCE" in capsys.readouterr().out


def test_missing_input_named_error(tmp_path, capsys):
    assert main(["run","--input",str(tmp_path/"missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err


def test_schema_error_names_file_line_and_field(tmp_path, capsys):
    (tmp_path/"bad.jsonl").write_text('{"id":"one","synthetic":true,"votes":[],"amount":-1}\n')
    assert main(["run","--input",str(tmp_path)]) == 2
    err=capsys.readouterr().err
    assert "bad.jsonl: line 1" in err and "amount" in err and "SchemaError" in err


def test_report_write_failure_no_partial_files(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/"demo")
    assert main(["run","--input","demo"]) == 0
    before=set(tmp_path.iterdir())
    assert main(["report","--out",str(tmp_path)]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert set(tmp_path.iterdir()) == before


def test_cli_determinism(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/"demo")
    main(["run","--input","demo"])
    first=(tmp_path/".ace-result.json").read_bytes()
    main(["run","--input","demo"])
    assert first == (tmp_path/".ace-result.json").read_bytes()


def test_corrupt_state_named_error(tmp_path, capsys):
    state=tmp_path/"state.json"
    state.write_text('{"decisions":[{"vote_counts":{"yes":-1}}]}')
    assert main(["report","--state",str(state)]) == 2
    assert "StateError" in capsys.readouterr().err


def test_disagreement_provenance_covers_complete_input(tmp_path, capsys):
    generate(tmp_path)
    assert main(["disagreements","--input",str(tmp_path)]) == 0
    data=json.loads(capsys.readouterr().out)
    assert len(data["decisions"]) == 120
    assert len(data["provenance"]["synthetic_ids"]) == 200


@pytest.mark.parametrize("content", ['null', '{"decisions":null}', '{"decisions":[{"vote_counts":null}]}'])
def test_malformed_state_no_traceback(tmp_path, capsys, content):
    state=tmp_path/"state.json"
    state.write_text(content)
    assert main(["report","--state",str(state)]) == 2
    assert "StateError" in capsys.readouterr().err
