# NORTH — what this project is for

Read this before starting any piece of work. It is the only document that says what "done"
means; everything else describes how.

---

## Destination

> **Understand USDM and ICH M11, and the AC/DC/BC framework, well enough to explain and
> demonstrate them — by structuring one protocol and taking one endpoint the whole way
> through.**

*Revised 2026-09-16.* The first version said "USDM v4 and the AC/DC/BC framework" and omitted
ICH M11 — the **M11** in what the field calls USDM11. The omission had already cost something:
work that would have advanced the M11 half was turned away by the test in §The test, because
the destination it was tested against was missing that half.

## Finish line

Done means all nine green, on at least one endpoint. Nothing else counts as finishing.

<!-- north:status -->

| # | Stage | Status |
|---|---|---|
| 0 | Protocol mapped to ICH M11 elements | ✓ |
| 0b | Protocol restructured to M11, USDM regenerated from it | ✗ |
| 1 | USDM fragments hand-authored | ✓ |
| 2 | BC linked on the chain's terminals | ✗ |
| 3 | DC — derivation authored | ✓ |
| 4 | AC — analysis bound | ✓ |
| 5 | eSAP generated | ✗ |
| 6 | Executed, a real result produced | ✗ |
| 7 | Compared against built ADaM | ✓ |

<!-- /north:status -->

This table is **verified against the filesystem** by `tools/check_consistency.py`, which the
pre-commit hook runs. It cannot quietly say ✓ for something that has not happened, and the
scoreboard prints on every commit.

## The route

All four remaining stages run on **one endpoint — laboratory change from baseline**, which is
the only tier that composes. Not on three endpoints. One, all the way.

**Stage 0b — protocol restructured to M11, USDM regenerated from it.** Added 2026-09-16 at
LG's direction. Stage 0 mapped the protocol and found the estimands in the wrong document;
0b moves them. Scoped to the same sections, and **done means both halves** — a restructured
protocol *and* `study/usdm/` regenerated from it, because a restructured section nothing
consumes leaves stage 1's fragment still transcribed from prose.

Progress: **§3 done** (`study/m11/protocol/section-03-objectives-endpoints.md`) — all thirty
previously-missing required estimand elements now present, transcribed from SAP §13, not
invented. Remaining: the six title-page elements, the §12.1 analyte list, and the USDM
regeneration.

**Stage 0 — protocol mapped to ICH M11 elements. Done 2026-09-16.**
[`study/m11/protocol-to-m11.md`](study/m11/protocol-to-m11.md). The headline: **M11 §3.1.1
requires the estimand in the protocol** — five of its seven required elements are ICH E9(R1)
estimand attributes — and TORIVA defers all five to the SAP, failing thirty required elements
across six objectives. That independently confirms, and makes countable, what stage 1 found
from the USDM side. Everything M11 wants exists somewhere in TORIVA's document set; none of it
is missing, all of it is misplaced.

The original scoping note follows. The
merged electronic M11 is 303 data elements, 216 of them Required, across 14 sections, each
carrying a CDISC code (`study/source-refs.md`). TORIVA's protocol is **not** M11-structured, so
this is a genuine mapping rather than a re-format, and it is the "M11" half of USDM11.

Scoped to the sections that feed the endpoint being carried — Title Page, §3 objectives and
endpoints, §8.4.4 clinical laboratory assessments — **not** all 216 required elements. A full
protocol digitisation remains a non-goal (`docs/specification.md` §13). First action: map
TORIVA's synopsis sections onto M11 element names, and record which required elements the
protocol does not supply, because that is the interesting half.

It sits before stage 1 logically: the USDM fragment should be a *product* of the M11 mapping
rather than transcribed from prose. Stage 1 was done first, in the other order, and that is
recorded rather than hidden — redoing it is not required, but stage 0 should say where the two
disagree.

**Stage 1 — USDM fragments hand-authored. Done 2026-09-16.**
`study/usdm/toriva-lung-301.usdm.json` — six objectives, six endpoints, seven laboratory BCs,
arms, population and one estimand. Loaded in the app and rendered. What was learned about USDM
v4's shape, and the one honest compromise in it, are in
[`study/usdm/README.md`](study/usdm/README.md).

**Stage 2 — BC linked.** Route is known. F04 established that BC linkage lives at *terminal*
level, not endpoint level, and the derivation pipeline has a BC picker on measure terminals.
First action — open the lab chain at step 6, link BCs on the measure terminals, confirm
`linkedBCIds` is no longer `[]`.

**Stage 5 — eSAP generated.** Step 7 of the builder, never opened. Unknown what it emits.
First action — open it with the lab chain loaded and see.

**Stage 6 — executed.** Step 8, via WebR. Unknown whether it needs real ADaM loaded into the
browser. First action — open it and find out. This is the stage that produces an actual number,
and nothing in this repository has ever produced one.

**Stage 7** is already green for this endpoint (`endpoints/01-simple-lab-cfb/comparison.md`).

Findings encountered on the way are recorded in two paragraphs and left alone. They are not
progress.

## The test

Applied to any proposed piece of work, **before starting it**:

> ### Which numbered stage does this advance?

**No number → it does not get done.** It goes in an appendix, or nowhere.

The test is deliberately harder to satisfy than "is this useful?" — nearly anything can be
argued useful. A stage number is a fact.

## This project is not

Naming these because the project drifted into all three once, and the drift was invisible while
it happened.

- **An audit of `cdisc-org/analysis-concepts`.** Their repository is the thing being learned,
  not the thing being assessed.
- **A governance or tooling product.** Part B of the specification is deferred and stays
  deferred until the finish line is green.
- **A critique.** Findings are a **by-product**: recorded when they block a stage, never
  pursued for their own sake, never the measure of progress.

## How this went wrong before, in one paragraph

`docs/specification.md` §2 set the objective as *"an artefact that answers: if we adopted this,
what would actually happen, and what would it cost?"* — an adoption-decision frame. That is not
the destination above, and no document in the repository said so. Twenty commits then executed
the written objective faithfully: thirteen findings, five issue drafts, a review plan, and
**1,985 lines of critique against 1,185 lines of framework work**, with stages 1, 2, 5 and 6
never started. Nothing was individually wrong. The compass was.

## Standing questions

Asked at the start of a session, and before any new artefact:

1. Which stage does this advance?
2. What did I learn about **the framework** — not about its gaps — from the last piece of work?
3. Is the findings count growing faster than the stage count?

If (2) is answered three times running with "that it cannot do X", the project has drifted
again.
