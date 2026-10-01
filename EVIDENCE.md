# Local acceptance evidence

Measured on 2026-10-01, Windows, Python 3.12.10, CPU only.

- pytest: 40 passed.
- Installed ace console entry point: fixture generation, run, and Markdown report completed in 0.661800 seconds, below 5 seconds.
- Installed ace JSON report completed in 0.206113 seconds, below 5 seconds.
- JSON totals exactly match the independent hand-computed expectations: 200 records, 560 votes, 120 consensus, 80 unresolved, 80 dissent records, 200 labelled, 120 correct, 0 incorrect, 80 labelled unresolved, 0 false positives.
- Mutation test changes one label and observes 119 correct and 1 incorrect consensus.
- Empty input, malformed JSON, invalid schema, corrupt saved state, duplicate agents and ids, Unicode, long strings, deterministic bytes, and failed output writes are tested.
- Source, tests, example input and documentation scanned for forbidden em dash characters.

These measurements apply only to synthetic fixture execution on this machine. No real-use accuracy, time savings, money savings, buyer demand, or agent independence was measured. The two-week evidence window and final operating verdict remain pending real use as required by the brief. No network or model calls were made by the tool or demo. Installation used local packages with --no-index.
