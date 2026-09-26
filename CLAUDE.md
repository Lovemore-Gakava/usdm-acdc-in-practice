# CLAUDE.md

**Read [`NORTH.md`](NORTH.md) first.** It states the destination, the finish lines and the test
every piece of work must pass. This file says how to work; `NORTH.md` says what for.

Where to look, so you load what the task needs and nothing else:

| Need | File |
|---|---|
| Destination, scoreboards, the test | [`NORTH.md`](NORTH.md) — kept short |
| Something is broken, or "how do I run it" | [`docs/troubleshooting.md`](docs/troubleshooting.md) |
| Why is it like this? | [`docs/decisions.md`](docs/decisions.md) |
| How claims are verified | [`docs/method.md`](docs/method.md) |
| Who wrote what, and what is unreviewed | [`PROVENANCE.md`](PROVENANCE.md) |
| Parked work — do not pick it up | [`docs/archive/`](docs/archive/README.md) |

## The test

Before starting any piece of work, answer:

> **Which numbered stage of `NORTH.md`'s finish line does this advance?**

No number → do not do it. Say so and propose the work that does carry a number.

This applies to work you propose *and* to work you are asked for. If a request has no stage
number, say which stage it displaces before starting — the user may still want it, but the
trade should be visible rather than silent.

## Do not drift

The project drifted once, badly, and the mechanism will recur.

Findings about what the framework *cannot* do are cheap to produce, feel like progress, and
advance no stage. There are already thirteen. **Do not add another unless it blocks a stage you
are actively trying to complete**, and when one does, record it in two paragraphs and move on.

**The parked work lives in [`docs/archive/`](docs/archive/README.md)** — the five drafted
upstream issues, the review plan and the two consumed review sheets. Do not polish them, do not
propose filing them, do not treat the review backlog as a blocker. Nothing is filed against `cdisc-org/analysis-concepts`, with one decided
exception: the `M.MMRM` implementation is *prepared* in `docs/contribution-mmrm.md` (LG,
2026-09-19) and only LG files it. Preparing it is not a licence to prepare anything else.

TORIVA is different — it is LG's own project, and issues #27 and #53 were filed there on LG's
explicit yes to a draft shown first. **That is the pattern for anything outward-facing: draft,
show, wait.**

**The SAP is an input, not a yardstick.** `study/usdm/README.md` fixes the layering: protocol +
CDISC Library → USDM, SAP → DC/AC. The SAP tells you *what derivation to author*. The moment it
is used the other way round — *here is what the SAP says, here is what the model cannot say* —
the work has become an assessment of `cdisc-org/analysis-concepts` again, whatever it is
called. This is the drift's second shape, harder to see because every individual step is
legitimate. It recurred inside an hour of the README being restructured to remove it, and LG
caught it, not the model.

The check: **what does this comparison decide?** If the answer is *whether the framework is
adequate*, stop. If it is *whether I authored the chain correctly*, continue.

Failures to avoid, each of which actually happened here:

- Noticing drift and continuing — writing *"I should stop generating findings"* and then
  generating two more. **If you notice drift, stop and ask.**
- Treating a request for one more artefact as licence to skip the test.
- Producing rigour where it is not needed: three corrections to a finding nobody asked for,
  while stages 1, 2, 5 and 6 sat untouched.

## Verification discipline

Five findings have had a premise or fix disproved, so:

- A claim about the **libraries** cites a path and `$defs` name at the pinned commit, or a count
  reproducible by a command in the file.
- A claim about **history** uses `git log -S` — it distinguishes *removed* from *never present*.
- A claim about the **application** is not established until the app has been **run**. Three
  findings went wrong inferring behaviour from library JSON.
- A claim about **TORIVA's data** needs the parquet read, not its markdown specification.

## Writing

Match the existing voice: direct, evidence-first, corrections left visible rather than deleted.
When something turns out wrong, amend it in place and say what changed — the repository's
record of its own errors is one of the few things in it worth keeping.

Say a thing once, in the place it belongs, and link. Do not restate a finding's argument in the
README, the finding file, `PROVENANCE.md` and a commit message.

**Prefer a guard to a sentence.** A rule that must be remembered will be forgotten; a rule the
tools enforce will not. Entry documents are budgeted and the budget is checked — see
`tools/check_consistency.py`.
