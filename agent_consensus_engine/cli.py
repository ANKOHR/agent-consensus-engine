"""Local CLI with named errors and atomic report writes."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import aggregate, SchemaError
from .fixtures import generate
from .report import render, report_data

class InputError(ValueError):
    pass

def load(directory):
    root = Path(directory)
    if not root.is_dir():
        raise InputError(f"MissingInput: {root}: use ace fixtures --out <dir> or provide an input directory")
    records = []
    sources = []
    for path in sorted(root.iterdir()):
        if path.name == "expectations.json" or path.name.startswith("."):
            continue
        if path.suffix not in {".jsonl", ".json"}:
            raise InputError(f"SchemaError: {path}: line 1: unsupported file type; use JSON or JSONL")
        try:
            content = path.read_text(encoding="utf-8-sig")
            if path.suffix == ".jsonl":
                for line, text in enumerate(content.splitlines(), 1):
                    if not text.strip() or text.lstrip().startswith("#"):
                        continue
                    try:
                        records.append(json.loads(text))
                        sources.append((path, line))
                    except json.JSONDecodeError as exc:
                        raise InputError(f"ParseError: {path}: line {line}: {exc.msg}") from exc
            else:
                obj = json.loads(content)
                batch = obj if isinstance(obj, list) else [obj]
                records.extend(batch)
                sources.extend((path, 1) for _ in batch)
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: {path}: line {exc.lineno}: {exc.msg}") from exc
        except (OSError, UnicodeError) as exc:
            raise InputError(f"ReadError: {path}: line 1: {exc}") from exc
    try:
        return aggregate(records)
    except SchemaError as exc:
        index = int(str(exc).split(":", 1)[0].split()[1]) - 1
        path, line = sources[index]
        raise InputError(f"SchemaError: {path}: line {line}: {exc}") from exc

def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            handle.write(content)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc}") from exc
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def parser():
    p = argparse.ArgumentParser(description="Exact local voting; no model calls. Example: ace fixtures --out demo")
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: ace fixtures --out demo")
    f.add_argument("--out", required=True)
    r = sub.add_parser("run", help="Compute and save consensus", epilog="Example: ace run --input demo")
    r.add_argument("--input", required=True)
    r.add_argument("--state", default=".ace-result.json")
    r = sub.add_parser("report", help="Render computed results with provenance", epilog="Example: ace report --format md")
    r.add_argument("--format", choices=["md", "json"], default="md")
    r.add_argument("--state", default=".ace-result.json")
    r.add_argument("--out")
    for name, help_text in [("disagreements", "List dissent and unresolved records"), ("audit", "Evaluate consensus against supplied ground truth")]:
        r = sub.add_parser(name, help=help_text, epilog=f"Example: ace {name} --input demo")
        r.add_argument("--input", required=True)
    return p

def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 SYNTHETIC records; expectations are hand-computed.")
        elif args.command == "run":
            result = load(args.input)
            atomic_write(args.state, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
            print(report_data(result)["provenance"]["banner"])
            print(f"Computed {result['totals']['records']} records. Use ace report for data provenance. Savings unmeasured.")
        elif args.command == "report":
            try:
                result = json.loads(Path(args.state).read_text(encoding="utf-8"))
                for decision in result["decisions"]:
                    counts = decision["vote_counts"]
                    if not isinstance(counts, dict) or any(type(n) is not int or n < 1 for n in counts.values()) or sum(counts.values()) > 1000:
                        raise ValueError("invalid vote_counts")
                # Reconstruct and recompute to validate saved state before rendering.
                records = [dict(id=d["id"], synthetic=d["synthetic"], votes=[dict(agent=str(i), answer=a) for i, a in enumerate([a for a, n in d["vote_counts"].items() for _ in range(n)])], **({"ground_truth": d["ground_truth"]} if d["ground_truth"] is not None else {})) for d in result["decisions"]]
                result = aggregate(records)
            except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
                raise InputError(f"StateError: {args.state}: {exc}; run ace run --input <dir> first") from exc
            output = render(result, args.format)
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
        else:
            result = load(args.input)
            if args.command == "disagreements":
                data = report_data(result)
                data["decisions"] = [d for d in data["decisions"] if d["dissent"] or d["status"] == "unresolved"]
                data["selection_note"] = "Filtered decisions; provenance and totals describe the complete input."
                print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2))
            else:
                print(render(result, "json"), end="")
        return 0
    except (InputError, OSError) as exc:
        print(str(exc).replace("\u2014", "-"), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
