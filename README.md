# Agent Consensus Engine

ACE aggregates exact answers from independent agents using deterministic local majority voting. It runs on CPU, makes no model or network calls, and uses no database. Independence is supplied by the operator, not verified by the tool. Majority agreement is not proof of truth.

## Quickstart

Python 3.10 or newer, setuptools and pytest available locally:

```powershell
python -m pip install --no-index --no-deps --no-build-isolation -e .
ace fixtures --out demo
ace run --input demo
ace report --format md
python -m pytest -q
```

The chained demo is `ace fixtures --out demo && ace run --input demo && ace report --format md` in shells supporting `&&`. If the Python user Scripts directory is not on PATH, add the installation directory printed by pip to PATH or use module invocation: `python -m agent_consensus_engine.cli`.

## Input format

An input directory contains only JSON or JSONL data files. JSON accepts a record or an array. JSONL accepts one record per line, blank lines and header comments beginning with `#`. UTF-8 and UTF-8 with BOM are accepted. The reserved `expectations.json` file and dot files are metadata and excluded from input. Other file extensions produce a named schema error; CSV and YAML are not supported.

```json
{"id":"task-1","synthetic":false,"votes":[{"agent":"alpha","answer":"yes"},{"agent":"beta","answer":"yes"}],"ground_truth":"yes"}
```

Required fields: unique nonblank `id`, boolean `synthetic`, and `votes` list. Each vote has only nonblank `agent` and `answer` strings. Agents must be distinct within a record. Answers are exact, case-sensitive Unicode strings; whitespace is not normalised. Strings are limited to 10000 characters and votes to 1000 per record. Em dash characters are rejected. Unknown fields, including monetary amounts and negative amounts, are rejected, never silently discarded. An empty vote list is valid and unresolved. An optional `ground_truth` string permits evaluation. Optional ISO `date` must be on or before the fixed schema cutoff 2026-09-30; this fixed cutoff ensures validation does not change with the clock. Omit date for later trials until the schema is intentionally updated.

At least two votes and a strict majority (> half of all votes) are required for consensus. Ties and a single vote are unresolved. Dissent means more than one distinct answer, even when a majority exists. False positives are labelled records with a consensus answer unequal to ground truth. This metric covers incorrect accepted answers; it is not a binary-classification statistic. Unlabelled answers have no accuracy claim. Counts reconcile: consensus + unresolved = records, and correct + incorrect + labelled_unresolved = labelled. The JSON report includes each record's vote counts and evaluation for tracing figures.

For real trials, Henry enters his own data by hand and sets `synthetic: false`. This is an operator declaration, not an independently verified claim of authorship. Do not commit private trial data. A five-record hand-written synthetic input is in `examples/tiny`.

## Subcommands

| Command | Example | Purpose |
| --- | --- | --- |
| fixtures | `ace fixtures --out demo` | Generate the 200 labelled synthetic records and expectations |
| run | `ace run --input demo --state result.json` | Validate and compute saved results |
| report | `ace report --state result.json --format json --out report.json` | Render JSON or Markdown with provenance |
| disagreements | `ace disagreements --input demo` | Show dissent and unresolved decisions; totals cover the full input |
| audit | `ace audit --input demo` | Evaluate answers against explicit ground truth and show all decisions |

Every subcommand provides `--help` with an example. Default state is `.ace-result.json` in the current directory. `report` validates and recomputes votes from saved state, never trusts stored totals. Output file writes use a temporary file followed by atomic replacement; failures leave no partial output. Missing input, malformed JSON, invalid schema, invalid state, and write failures have named errors and nonzero status 2. Parse errors name file and line. JSON schema errors identify the record and file (line 1 for an array); JSONL errors identify the exact record line.

## Architecture

```text
local JSON / JSONL -> cli.load -> core.validate -> core.aggregate
                                           -> atomic saved state
saved state -> validated recomputation -> report -> Markdown / JSON
fixtures -> synthetic inputs + independent hand-computed expectations
```

Core functions perform no I/O. Ordering is stable by record id and answer. Identical inputs produce identical UTF-8 report and state bytes. Fixture generation uses hand-defined patterns; no randomness or seed is required.

## Honesty boundary and fixture policy

All reported counts are computed from explicit inputs. The tool does not discover, predict, or estimate facts. No time or money savings are presented: savings are explicitly unmeasured because no baseline is supplied. Any future illustrative or hypothetical figure must be labelled on every surface. Runtime evidence measures this machine's fixture execution only, not savings or real-world accuracy. Provenance banners enumerate synthetic and user-declared real record ids in JSON, and count each group in Markdown. Every generated data record carries `synthetic: true`; JSONL has a synthetic header comment. JSON expectations use an internal synthetic label because JSON does not support comments.

The fixture consists of 40 blocks of five cases: unanimous yes (3 votes), majority yes (3), tied yes/no (4), no votes (0), unanimous Unicode (4). Per block: 3 consensus, 2 unresolved, 14 votes, 2 dissent records. Across 200 records: 120 correct consensus, 80 labelled unresolved, 560 votes, 80 dissent records, zero incorrect consensus. Expectations are written independently of the engine. Corrupting one truth label produces 119 correct and 1 incorrect, proving evaluation follows data. This synthetic evidence does not validate real agent independence or factual reliability.

## Failure modes and limitations

Correlated agents can agree on a wrong answer. Equivalent natural-language answers may disagree literally. Label quality controls audit quality. Without labels, accuracy is unknown. Unresolved cases require human review. Input schema rejects unsupported monetary fields and extreme values. There is no weighting, answer semantic matching, automatic agent execution, or measured productivity baseline. Reports can be large because every decision is traceable.

## Two-week evidence hook and verdict

Status: evidence window not started. No real-use verdict is claimed. During the first 14 days of real use, record date, usage, total hand-checked consensus decisions, and incorrect decisions privately. Primary metric: incorrect consensus / hand-checked consensus, with numerator and denominator recorded. Zero hand-checked decisions means unmeasured, not zero error. After two weeks, if error exceeds 10 percent, fix the top observed cause or kill with the reason recorded. If unused, record that finding and kill. Record the final dated verdict and evidence: expand for daily use or revenue; integrate for heavy sibling overlap; commercialise for a demonstrated willing buyer; maintain as portfolio evidence otherwise; kill for non-use or inability to meet acceptance criteria. Do not invent future usage evidence to close the window.

See EVIDENCE.md for local acceptance results and LESSONS.md for operating lessons.
