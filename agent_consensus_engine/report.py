"""Render measured counts with explicit data provenance."""
import json

def report_data(result):
    synthetic = [d["id"] for d in result["decisions"] if d["synthetic"]]
    real = [d["id"] for d in result["decisions"] if not d["synthetic"]]
    return dict(result, provenance=dict(banner=f"DATA PROVENANCE: {len(synthetic)} synthetic fixture records; {len(real)} user-declared real records. Real authorship is not independently verified.", synthetic_ids=synthetic, real_ids=real))

def render(result, format="md"):
    data = report_data(result)
    if format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    lines = ["# Agent Consensus Engine", "", data["provenance"]["banner"], "", "All counts are computed from input votes. Exact majority does not establish factual truth or agent independence.", "", "| Metric | Computed count |", "| --- | ---: |"]
    lines += [f"| {k} | {v} |" for k, v in data["totals"].items()]
    lines += ["", data["savings"]["note"], "", "## Traceable decisions", ""]
    lines += [json.dumps(d, ensure_ascii=False, sort_keys=True) for d in data["decisions"]]
    return "\n".join(lines) + "\n"
