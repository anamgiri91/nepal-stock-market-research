"""Mechanical provenance check for every table in the manuscript.

Written 2026-08-29 after a table with no generating code was found to contain a 30% error
(A-053) and a second was found to splice two analytical vintages (A-056). Both survived
value-level checking, because a stale or hand-assembled artifact can match the manuscript
perfectly while no code produces it.

The rule this file enforces:

    A table is not reproducible because its output exists and matches. Its generating
    dependency must be identifiable and executable.

DELIBERATE DESIGN CONSTRAINT — do not "simplify" this away:

    Producers are resolved FROM THE REGISTRY ONLY. This file never globs `scripts/[0-9]*.py`.
    `run_pipeline.sh` discovers work by that glob, so an audit sharing it would be blind to
    exactly the unregistered producer the glob misses. The registry is the single declaration
    and this checker's job is to disagree with it loudly.

    python paper/audit_tables.py        # exit 0 if every table is accounted for, 1 otherwise
"""

from __future__ import annotations

import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "paper" / "TABLE-REGISTRY.toml"

VALID_STATUS = {"A", "B", "C", "D", "N"}
VALID_REMEDY = {"bad-number", "stale-artifact", "lost-producer",
                "assembly-error", "never-executable"}

_problems: list[tuple[str, str, str]] = []


def fail(tid: str, rule: str, detail: str) -> None:
    _problems.append((tid, rule, detail))


def manuscript_tables(md: str) -> list[tuple[int, str]]:
    """Every markdown table in document order, tagged with its section number."""
    lines = md.split("\n")
    sec, found = "?", []
    for i, line in enumerate(lines):
        if line.startswith(("## ", "### ")):
            m = re.match(r"#+\s*([0-9]+(?:\.[0-9]+)?)\.?\s", line)
            sec = m.group(1) if m else "?"
        if re.match(r"^\|[-: |]+\|$", line.strip()) and i > 0 and lines[i - 1].startswith("|"):
            found.append((len(found) + 1, sec))
    return found


def emits(producer: pathlib.Path, output: str) -> bool:
    """Static link: does the producer's source actually name this output file?

    Producers may build the name with an f-string (`f"table25_{i}_addrs_premise.csv"`), so a
    literal substring test is not enough: each digit run is also allowed to match a `{...}`
    interpolation. This stays a *static* check on purpose — running producers to find out what
    they write would make the audit as slow as the pipeline and as trusting as the thing it audits.
    """
    src = producer.read_text()
    name = pathlib.Path(output).name
    if name in src:
        return True
    pattern = "".join(r"(?:\d+|\{[^}]*\})" if part.isdigit() else re.escape(part)
                      for part in re.split(r"(\d+)", name) if part)
    return re.search(pattern, src) is not None


def check_output(tid: str, producer_path: str, output: str) -> None:
    """Rules 2-5, for one producer/output pair."""
    prod = ROOT / producer_path
    if not prod.exists():
        fail(tid, "producer missing", producer_path)
        return
    if output in ("none", "printed"):
        return
    out = ROOT / output
    if not out.exists():
        fail(tid, "output not generated", output)
        return
    if out.stat().st_mtime < prod.stat().st_mtime:
        fail(tid, "STALE: output older than its producer",
             f"{output} predates {producer_path}")
    if not emits(prod, output):
        fail(tid, "producer does not write this output",
             f"{pathlib.Path(output).name} not referenced in {producer_path}")


def validate(reg: dict, tables: list[tuple[int, str]]) -> list[tuple[str, str, str]]:
    """Apply every rule to a registry. Returns the problem list; callable from tests."""
    global _problems
    _problems = []
    entries = reg.get("table", [])

    # Rule 1 — the manuscript and the registry must describe the same set of tables.
    if len(tables) != len(entries):
        fail("-", "registry does not cover the manuscript",
             f"{len(tables)} tables in {reg['meta']['manuscript']}, {len(entries)} registered")
    for (n, sec), e in zip(tables, entries):
        tid = e.get("id", f"#{n}")
        if e.get("section") != sec:
            fail(tid, "section mismatch",
                 f"registry says {e.get('section')}, manuscript table {n} is in {sec}")

    for e in entries:
        tid = e.get("id", "?")
        status = e.get("status")
        if status not in VALID_STATUS:
            fail(tid, "invalid status", str(status))
            continue

        producer, output = e.get("producer", "none"), e.get("output", "none")

        # Rules 2-5.
        if producer != "none":
            check_output(tid, producer, output)
            if e.get("secondary_producer"):
                check_output(tid, e["secondary_producer"], e.get("secondary_output", "none"))
        elif status in {"A", "B"}:
            fail(tid, "status claims reproducible but declares no producer", status)

        # Rule 6 — a D-class table must say which kind of failure it is and where it is tracked.
        if status == "D":
            if e.get("remedy_class") not in VALID_REMEDY:
                fail(tid, "status D without a valid remedy class", str(e.get("remedy_class")))
            if not e.get("issue"):
                fail(tid, "status D without an issue id", "")

        # Rule 7 — B must document what the reader has to do to get from output to table.
        if status == "B" and not e.get("transformation"):
            fail(tid, "status B without a documented transformation", "")

        # Rule 8 — anything hand-assembled must say why that was legitimate.
        if e.get("assembled") and not e.get("justification"):
            fail(tid, "manually assembled without justification", "")

        # A claims values were checked; say when.
        if status == "A" and not e.get("verified"):
            fail(tid, "status A without a verification record", "")

        if not e.get("sample"):
            fail(tid, "no sample definition declared", "")

    # Non-table artifacts still need a producer: this is where a file with no generating code
    # at all (A-062) surfaces, which is a different failure from a table with no producer.
    for a in reg.get("artifact", []):
        check_output(f"art:{pathlib.Path(a['output']).stem[:18]}", a["producer"], a["output"])

    # Reverse check — every CSV shipped in the replication package must be claimed by something.
    claimed = {e.get("output") for e in entries} | {e.get("secondary_output") for e in entries}
    claimed |= {o["output"] for o in reg.get("orphan", [])}
    claimed |= {a["output"] for a in reg.get("artifact", [])}
    for csv in sorted((ROOT / "output" / "tables").glob("*.csv")):
        rel = str(csv.relative_to(ROOT))
        if rel not in claimed:
            fail("-", "artifact claimed by no registry entry", rel)

    return _problems


def main() -> int:
    if not REGISTRY.exists():
        print(f"registry not found: {REGISTRY}", file=sys.stderr)
        return 1
    reg = tomllib.loads(REGISTRY.read_text())
    entries = reg.get("table", [])
    tables = manuscript_tables((ROOT / reg["meta"]["manuscript"]).read_text())
    validate(reg, tables)

    # ---- report -------------------------------------------------------------------
    by_status: dict[str, list[str]] = {}
    for e in entries:
        by_status.setdefault(e.get("status", "?"), []).append(e.get("id", "?"))

    print("MANUSCRIPT TABLE PROVENANCE")
    print("=" * 78)
    for e in entries:
        s = e.get("status", "?")
        src = e.get("producer", "none")
        src = pathlib.Path(src).name if src != "none" else "— no producer —"
        extra = f"  [{e.get('remedy_class')}, {e.get('issue')}]" if s == "D" else ""
        print(f"  {s}  {e.get('id','?'):<4s} §{e.get('section',''):<5s} {src:<34s}{extra}")
    print("=" * 78)
    print("  " + " · ".join(f"{k}={len(v)}" for k, v in sorted(by_status.items())))
    print(f"  plus {len(reg.get('artifact', []))} non-table artifacts and "
          f"{len(reg.get('orphan', []))} declared orphans (no producer, tracked)")

    if _problems:
        print(f"\n  {len(_problems)} PROVENANCE FAILURE(S)")
        for tid, rule, detail in _problems:
            print(f"    {tid:<4s} {rule}" + (f" — {detail}" if detail else ""))
        return 1

    print("\n  every manuscript table is declared, and every declaration holds.")
    print("  NOTE: status D entries are declared failures, tracked by issue id. This check")
    print("        confirms they are *accounted for*, not that they are fixed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
