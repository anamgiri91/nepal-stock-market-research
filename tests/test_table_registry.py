"""Negative tests for the manuscript table registry checker.

A provenance checker that only ever passes is worse than none: it converts an unexamined
assumption into a green tick. Every rule in `paper/audit_tables.py` is therefore exercised
here by constructing a registry that violates it and asserting the checker objects.

The live registry is also asserted to be internally consistent, but that assertion is the
least interesting one in the file.
"""

from __future__ import annotations

import pathlib
import sys
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))

import audit_tables as A  # noqa: E402

REAL_PRODUCER = "scripts/22_universe_composition.py"
REAL_OUTPUT = "output/tables/table27_universe_composition.csv"


def base_entry(**over):
    e = dict(id="T1", section="5.1", title="t", producer=REAL_PRODUCER,
             output=REAL_OUTPUT, sample="a sample", status="A",
             verified="2026-08-29")
    e.update(over)
    return e


def run(entries, tables=None, **reg_extra):
    reg = {"meta": {"manuscript": "paper/main.md"}, "table": entries}
    reg.update(reg_extra)
    return A.validate(reg, tables if tables is not None else [(1, "5.1")])


def rules(problems):
    return " | ".join(r for _, r, _ in problems)


def test_clean_entry_passes():
    """A well-formed entry raises no entry-level problem.

    The reverse check still fires here, because a synthetic registry naturally does not claim
    the repository's real CSVs. That is the check working, so it is scoped out of this one
    assertion and covered by `test_unclaimed_csv_fails` instead.
    """
    entry_level = [p for p in run([base_entry()])
                   if p[1] != "artifact claimed by no registry entry"]
    assert entry_level == []


def test_manuscript_table_absent_from_registry_fails():
    # two tables in the manuscript, one registered
    p = run([base_entry()], tables=[(1, "5.1"), (2, "6")])
    assert "registry does not cover the manuscript" in rules(p)


def test_section_mismatch_fails():
    p = run([base_entry(section="9")], tables=[(1, "5.1")])
    assert "section mismatch" in rules(p)


def test_missing_producer_file_fails():
    p = run([base_entry(producer="scripts/does_not_exist.py")])
    assert "producer missing" in rules(p)


def test_output_not_generated_fails():
    p = run([base_entry(output="output/tables/never_written.csv")])
    assert "output not generated" in rules(p)


def test_producer_that_does_not_write_the_output_fails():
    # a real script and a real CSV, but that script does not emit that CSV
    p = run([base_entry(producer="scripts/03_descriptive.py", output=REAL_OUTPUT)])
    assert "producer does not write this output" in rules(p)


def test_stale_output_fails(tmp_path, monkeypatch):
    """An output older than its producer is stale -- the table16/table17 failure (A-063)."""
    prod = tmp_path / "scripts" / "p.py"
    prod.parent.mkdir(parents=True)
    out = tmp_path / "output" / "tables" / "t.csv"
    out.parent.mkdir(parents=True)
    out.write_text("a,b\n1,2\n")
    out.touch()
    prod.write_text('df.to_csv("t.csv")\n')          # written after the output
    import os
    os.utime(out, (1, 1))                             # force the output to be older
    monkeypatch.setattr(A, "ROOT", tmp_path)
    p = run([base_entry(producer="scripts/p.py", output="output/tables/t.csv")])
    assert "STALE: output older than its producer" in rules(p)


def test_status_a_without_producer_fails():
    p = run([base_entry(producer="none", output="none")])
    assert "status claims reproducible but declares no producer" in rules(p)


def test_status_d_without_remedy_class_fails():
    p = run([base_entry(status="D", issue="A-001", producer="none", output="none")])
    assert "status D without a valid remedy class" in rules(p)


def test_status_d_with_bogus_remedy_class_fails():
    p = run([base_entry(status="D", remedy_class="gremlins", issue="A-001",
                        producer="none", output="none")])
    assert "status D without a valid remedy class" in rules(p)


def test_status_d_without_issue_fails():
    p = run([base_entry(status="D", remedy_class="bad-number",
                        producer="none", output="none")])
    assert "status D without an issue id" in rules(p)


def test_status_b_without_transformation_fails():
    p = run([base_entry(status="B", output="printed")])
    assert "status B without a documented transformation" in rules(p)


def test_assembled_without_justification_fails():
    p = run([base_entry(assembled=True)])
    assert "manually assembled without justification" in rules(p)


def test_status_a_without_verification_record_fails():
    e = base_entry()
    del e["verified"]
    assert "status A without a verification record" in rules(run([e]))


def test_missing_sample_definition_fails():
    e = base_entry()
    del e["sample"]
    assert "no sample definition declared" in rules(run([e]))


def test_invalid_status_fails():
    p = run([base_entry(status="Z")])
    assert "invalid status" in rules(p)


def test_unclaimed_csv_fails():
    """A CSV in the package that no entry claims -- how table13 (A-062) surfaces."""
    p = run([base_entry()])
    assert "artifact claimed by no registry entry" in rules(p)


def test_emits_resolves_fstring_filenames():
    """`f"table25_{i}_addrs_premise.csv"` must still link to table25_1_addrs_premise.csv."""
    prod = ROOT / "scripts" / "19_addrs_premise.py"
    assert A.emits(prod, "output/tables/table25_1_addrs_premise.csv")
    assert not A.emits(prod, "output/tables/table28_addrs_mass_decomposition.csv")


# ---------------------------------------------------------------- the live registry

def test_live_registry_is_consistent():
    reg = tomllib.loads((ROOT / "paper" / "TABLE-REGISTRY.toml").read_text())
    tables = A.manuscript_tables((ROOT / "paper" / "main.md").read_text())
    problems = A.validate(reg, tables)
    assert problems == [], "\n".join(f"{t}: {r} {d}" for t, r, d in problems)


def test_every_d_class_table_names_a_tracked_issue():
    reg = tomllib.loads((ROOT / "paper" / "TABLE-REGISTRY.toml").read_text())
    register = (ROOT.parent / "private" / "audit" / "ISSUE-REGISTER.md")
    if not register.exists():
        pytest.skip("issue register is private and not present")
    text = register.read_text()
    for e in reg["table"]:
        if e["status"] == "D":
            assert e["issue"] in text, f"{e['id']} cites {e['issue']}, absent from the register"
