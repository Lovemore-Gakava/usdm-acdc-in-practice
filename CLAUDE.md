# CLAUDE.md

**Read [`NORTH.md`](NORTH.md) before doing anything else.** It states the destination, the
eight-stage finish line, and the test every piece of work must pass. This file says how to work;
`NORTH.md` says what for.

## The test

Before starting any piece of work, answer:

> **Which numbered stage of `NORTH.md`'s finish line does this advance?**

No number → do not do it. Say so and propose the work that does carry a number.

This applies to work you propose *and* to work you are asked for. If a request has no stage
number, say which stage it displaces before starting — the user may still want it, but the
trade should be visible rather than silent.

## Do not drift

The project drifted once, badly, and the mechanism is worth knowing because it will recur.

Findings about what the framework *cannot* do are cheap to produce, feel like progress, and
advance no stage. There are already thirteen. **Do not add another unless it blocks a stage you
are actively trying to complete**, and when one does, record it in two paragraphs and move on.

**The upstream issues and the review plan are parked** — `docs/findings/upstream-issues.md`,
`docs/review-plan.md`. Do not polish them, do not propose filing them, and do not treat the
review backlog as a blocker. Nothing is being filed.

Specific failures to avoid, each of which actually happened here:

- Noticing drift and continuing. Writing *"I should stop generating findings"* and then
  generating two more. **If you notice drift, stop and ask.**
- Treating a request for one more artefact as licence to skip the test.
- Producing rigour where it is not needed — three corrections to a finding nobody asked for,
  while stages 1, 2, 5 and 6 sat untouched.

## Verification discipline

This is the part of the old process worth keeping. Five findings have had a premise or fix
disproved, so:

- A claim about the **libraries** cites a path and `$defs` name at the pinned commit, or a count
  reproducible by a command in the file.
- A claim about **history** uses `git log -S` — it distinguishes *removed* from *never present*.
- A claim about the **application** is not established until the app has been **run**. Three
  findings went wrong by inferring behaviour from library JSON. Serve it:
  `python ac-dc-app/serve.py` from `upstream/analysis-concepts`, then
  `http://localhost:8080/ac-dc-app/index.html`.
- A claim about **TORIVA's data** needs the parquet read, not its markdown specification.

## Repository facts

- `upstream/analysis-concepts` is a **pinned, read-only submodule** at `739344c`. Never edit it;
  if a local change is unavoidable, `git -C upstream/analysis-concepts checkout <path>` after.
- TORIVA-LUNG 301 is **referenced, never vendored**. Sparse-checkout recipe in
  `study/source-refs.md`. On Git Bash for Windows, prefix `sparse-checkout set` with
  `MSYS_NO_PATHCONV=1` or it silently yields an empty tree.
- `tools/check_consistency.py` runs on every commit via `.githooks/pre-commit`. It verifies that
  documents match the filesystem **and** that `NORTH.md`'s status table is true. Enable the hook
  once per clone: `git config core.hooksPath .githooks`.
- `tools/check_baseline_ambiguity.py` needs `pyarrow`. Note `pyarrow.dataset` is blocked by
  Application Control on this machine — use `pq.ParquetFile(...).read()`, not `pq.read_table`.
- Python is `python`, not `python3`.

## Writing

Match the existing voice: direct, evidence-first, corrections left visible rather than deleted.
When something turns out wrong, amend it in place and say what changed — the repository's
record of its own errors is one of the few things in it worth keeping.

Do not restate a finding's full argument in the README, the finding file, `PROVENANCE.md` and a
commit message. Say it once, in the finding, and link.
