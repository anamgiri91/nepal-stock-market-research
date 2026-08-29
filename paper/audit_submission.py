"""Mechanical pre-submission audit. Structure and consistency only — never science.

Run after `build.py` and before packaging. Everything here is a fact about the artifact: does
the compiled output match the source, do figures run in order, is every citation resolvable, is
the manuscript free of machine-specific paths. Nothing in this file inspects a result or asserts
an expected value, because a submission check that encodes today's numbers would fail the moment
the analysis legitimately changed.

    python paper/audit_submission.py         # exit 0 if clean, 1 otherwise
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"

_checks: list[tuple[bool, str, str]] = []


def check(passed: bool, label: str, detail: str = "") -> bool:
    _checks.append((bool(passed), label, detail))
    return bool(passed)


def main() -> int:
    md_path = PAPER / "main.md"
    build_path = PAPER / "build" / "main.html"

    if not md_path.exists():
        print("main.md not found", file=sys.stderr)
        return 1
    md = md_path.read_text()
    html = build_path.read_text() if build_path.exists() else ""

    check(bool(html), "build exists", "run paper/build.py first" if not html else "")

    # --- source and artifact agree -----------------------------------------------------
    title_m = re.search(r"^# (.+)$", md, re.M)
    title = title_m.group(1) if title_m else ""
    check(bool(title) and title in html, "compiled output carries the source title", title[:48])
    check(md.count(f"# {title}") == 1, "title appears exactly once in source")

    # --- front matter -------------------------------------------------------------------
    for field in ("Keywords:", "JEL classification:"):
        check(field in md, f"front matter has {field.rstrip(':')}")
    check("Affiliation" in md or "affiliation" in md,
          "affiliation is present or explicitly flagged as outstanding")

    # --- figures ------------------------------------------------------------------------
    caps = [int(x) for x in re.findall(r"\*\*Figure (\d+)\.\*\*", md)]
    imgs = [int(x) for x in re.findall(r"!\[Figure (\d+)\]", md)]
    check(caps == list(range(1, len(caps) + 1)), "figure captions numbered contiguously", str(caps))
    check(imgs == caps, "each figure image matches its caption number")
    if html:
        n_inline = html.count("data:image/png;base64")
        check(n_inline == len(caps), "every figure inlined in the build", f"{n_inline}/{len(caps)}")

    # --- tables -------------------------------------------------------------------------
    src_tables = len(re.findall(r"\n\|[^\n]*\|\n\|[-: |]+\|", md))
    if html:
        check(html.count("<table>") >= src_tables - 1,
              "tables survive compilation", f"{html.count('<table>')} rendered / {src_tables} in source")

    # --- mathematics survives compilation --------------------------------------------------
    n_display = md.count("$$") // 2
    if n_display:
        check("MathJax" in html, "display equations have a renderer in the build",
              f"{n_display} display equations")
        check(md.count("$$") % 2 == 0, "display-math delimiters balanced in source")
        check(md.count("$") % 2 == 0, "inline-math delimiters balanced in source")

    # --- cross-references ----------------------------------------------------------------
    have = {m.group(1) for m in re.finditer(r"^#{2,3} ([0-9]+(?:\.[0-9]+)?)\.? ", md, re.M)}
    want = {m.group(1) for m in re.finditer(r"§([0-9]+(?:\.[0-9]+)?)", md)}
    check(not (want - have), "no dangling section cross-references", str(sorted(want - have)))

    secs = [m.group(1) for m in re.finditer(r"^## (\d+)\. ", md, re.M)]
    check(secs == [str(i) for i in range(1, len(secs) + 1)],
          "top-level sections numbered contiguously", ",".join(secs))

    # --- citations resolve ---------------------------------------------------------------
    if "## References" in md:
        refs = md[md.index("## References"):]
        cited = set(re.findall(r"\b([A-Z][a-z]{2,})\s+(?:and|et al\.|,)?[^.]{0,40}?\(\d{4}[ab]?\)", md))
        orphan = sorted(n for n in cited if n not in refs)
        check(not orphan, "every cited surname appears in References", str(orphan[:4]))

    # --- nothing machine-specific --------------------------------------------------------
    leaks = [t for t in ("/Users/", "/private/tmp", "file:///", "C:\\\\") if t in md]
    check(not leaks, "manuscript contains no local paths", str(leaks))
    if html:
        check("/Users/" not in html and "/private/tmp" not in html,
              "compiled output contains no local paths")

    # --- reproducibility provenance ------------------------------------------------------
    check((ROOT / "data" / "processed" / "BUILD-MANIFEST.json").exists(),
          "build manifest present")
    check("BUILD-MANIFEST" in (ROOT / "README.md").read_text(),
          "README explains the manifest")
    check((PAPER / "submission.md").exists(), "submission materials present")

    # --- git identifies the version -------------------------------------------------------
    try:
        sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10).stdout.strip()
        check(bool(sha), "git HEAD identifies the manuscript version",
              sha + (" — WORKING TREE DIRTY" if dirty else " — clean"))
        check(not dirty, "working tree clean, so the artifact matches a commit")
    except Exception as exc:  # pragma: no cover
        check(False, "git version check", str(exc))

    # --- report ---------------------------------------------------------------------------
    print("PRE-SUBMISSION AUDIT — mechanical only")
    print("=" * 78)
    failed = 0
    for passed, label, detail in _checks:
        if not passed:
            failed += 1
        print(f"  {'PASS' if passed else 'FAIL'}  {label}" + (f"  — {detail}" if detail else ""))
    print("=" * 78)
    print(f"  {len(_checks) - failed}/{len(_checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
